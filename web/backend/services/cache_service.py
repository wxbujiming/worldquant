import json
import sqlite3
import datetime
import os
import threading

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
DB_PATH = os.path.join(DB_DIR, "wqb_cache.db")
BACKUP_PATH = DB_PATH + ".bak"
_local = threading.local()


def _get_conn() -> sqlite3.Connection:
    """每个线程一个独立的连接."""
    if not hasattr(_local, "conn") or _local.conn is None:
        os.makedirs(DB_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn
    return _local.conn


def _flatten(item: dict) -> dict:
    """将 JSON 第一层字段展平，嵌套 dict/list 转 JSON 字符串。"""
    out = {}
    for k, v in item.items():
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v)
        else:
            out[k] = v
    return out


def init_db():
    # 备份旧库
    if os.path.isfile(DB_PATH) and not os.path.isfile(BACKUP_PATH):
        try:
            os.rename(DB_PATH, BACKUP_PATH)
        except OSError:
            pass

    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sync_meta (
            data_type TEXT PRIMARY KEY,
            synced_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS operators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT,
            type TEXT,
            category TEXT,
            remarks TEXT DEFAULT '',
            raw_data TEXT
        );

        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wb_id TEXT,
            name TEXT,
            region TEXT,
            delay INTEGER,
            universe TEXT,
            category TEXT,
            coverage REAL,
            value_score REAL,
            themes TEXT,
            type TEXT,
            raw_data TEXT
        );

        CREATE TABLE IF NOT EXISTS fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wb_id TEXT,
            name TEXT,
            type TEXT,
            category TEXT,
            coverage REAL,
            dataset TEXT,
            dataset_id TEXT,
            raw_data TEXT
        );

        CREATE TABLE IF NOT EXISTS alphas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wb_id TEXT,
            name TEXT,
            grade TEXT,
            color TEXT,
            status TEXT,
            date_created TEXT,
            stage TEXT,
            tags TEXT,
            regular TEXT,
            settings TEXT,
            is_data TEXT,
            raw_data TEXT
        );
    """)
    conn.commit()


def get_synced_at(data_type: str) -> str | None:
    row = _get_conn().execute(
        "SELECT synced_at FROM sync_meta WHERE data_type = ?", (data_type,)
    ).fetchone()
    return row["synced_at"] if row else None


def set_synced_at(data_type: str):
    now = datetime.datetime.now().isoformat()
    _get_conn().execute(
        "INSERT OR REPLACE INTO sync_meta (data_type, synced_at) VALUES (?, ?)",
        (data_type, now),
    )
    _get_conn().commit()


# ── Operators ──────────────────────────────────────────────

def sync_operators(session) -> int:
    resp = session.search_operators()
    data = resp.json()
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("results") or data.get("operators") or data
    else:
        items = [data]
    if isinstance(items, dict):
        items = [items]
    conn = _get_conn()
    count = 0
    for item in items:
        op_name = item.get("name", "")
        if not op_name:
            continue
        flat = _flatten(item)
        raw = json.dumps(item)

        existing = conn.execute(
            "SELECT name, description, type, category FROM operators WHERE name = ?", (op_name,)
        ).fetchone()
        if existing:
            if (existing["name"] != flat.get("name")
                    or existing["description"] != flat.get("description")
                    or existing["type"] != flat.get("type")
                    or existing["category"] != flat.get("category")):
                conn.execute(
                    """UPDATE operators SET name=?, description=?, type=?, category=?, raw_data=?
                       WHERE name=?""",
                    (flat.get("name"), flat.get("description"), flat.get("type"),
                     flat.get("category"), raw, op_name),
                )
                count += 1
            continue

        conn.execute(
            """INSERT INTO operators (name, description, type, category, remarks, raw_data)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (flat.get("name"), flat.get("description"), flat.get("type"),
             flat.get("category"), "", raw),
        )
        count += 1
    set_synced_at("operators")
    conn.commit()
    return count


def get_cached_operators() -> list[dict]:
    rows = _get_conn().execute(
        "SELECT raw_data FROM operators ORDER BY name"
    ).fetchall()
    return [json.loads(r["raw_data"]) for r in rows]


def update_operator_remarks(op_id: str, remarks: str):
    _get_conn().execute(
        "UPDATE operators SET remarks = ? WHERE name = ?", (remarks, op_id)
    )
    _get_conn().commit()


def get_operator_remarks(op_id: str) -> str:
    row = _get_conn().execute(
        "SELECT remarks FROM operators WHERE name = ?", (op_id,)
    ).fetchone()
    return row["remarks"] if row else ""


# ── Datasets ───────────────────────────────────────────────

def sync_datasets(session) -> int:
    conn = _get_conn()
    total = 0
    offset = 0
    limit = 50
    while True:
        resp = session.get(
            f"https://api.worldquantbrain.com/data-sets?limit={limit}&offset={offset}"
        )
        data = resp.json()
        items = data.get("results") or []
        if not items:
            break
        for item in items:
            ds_id = str(item.get("id", ""))
            if not ds_id:
                continue
            region = (item.get("region") or "").lower()
            delay = item.get("delay", 0)
            universe = (item.get("universe") or "").lower()
            composite_id = f"{ds_id}__{region}__{delay}__{universe}"
            raw = json.dumps(item)
            flat = _flatten(item)

            existing = conn.execute(
                "SELECT wb_id, name, region, delay, universe FROM datasets WHERE wb_id = ?",
                (composite_id,),
            ).fetchone()
            if existing:
                if (existing["name"] != flat.get("name")
                        or existing["region"] != flat.get("region")
                        or existing["delay"] != flat.get("delay")
                        or existing["universe"] != flat.get("universe")):
                    conn.execute(
                        """UPDATE datasets SET name=?, region=?, delay=?, universe=?, category=?,
                           coverage=?, value_score=?, themes=?, type=?, raw_data=?
                           WHERE wb_id=?""",
                        (flat.get("name"), flat.get("region"), flat.get("delay"),
                         flat.get("universe"), flat.get("category"),
                         flat.get("coverage"), flat.get("valueScore"),
                         flat.get("themes"), flat.get("type"), raw, composite_id),
                    )
                    total += 1
                continue

            conn.execute(
                """INSERT INTO datasets
                   (wb_id, name, region, delay, universe, category,
                    coverage, value_score, themes, type, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (composite_id, flat.get("name"), flat.get("region"), flat.get("delay"),
                 flat.get("universe"), flat.get("category"),
                 flat.get("coverage"), flat.get("valueScore"),
                 flat.get("themes"), flat.get("type"), raw),
            )
            total += 1
        if len(items) < limit:
            break
        offset += limit
    set_synced_at("datasets")
    conn.commit()
    return total


def get_cached_datasets(region: str | None = None,
                        delay: int | None = None,
                        universe: str | None = None) -> list[dict]:
    where = []
    params = []
    if region:
        where.append("region = ?")
        params.append(region)
    if delay is not None:
        where.append("delay = ?")
        params.append(delay)
    if universe:
        where.append("universe = ?")
        params.append(universe)
    sql = "SELECT raw_data FROM datasets"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY name"
    rows = _get_conn().execute(sql, params).fetchall()
    return [json.loads(r["raw_data"]) for r in rows]


# ── Fields ─────────────────────────────────────────────────

def sync_fields(session, dataset_id: str | None = None) -> int:
    import time
    from .wqb_service import logger
    conn = _get_conn()
    total = 0
    datasets = get_cached_datasets()
    seen = set()
    for ds in datasets:
        d_id = ds.get("id", "")
        if not d_id:
            continue
        if dataset_id and d_id != dataset_id:
            continue
        region = ds.get("region")
        delay = ds.get("delay")
        universe = ds.get("universe")
        combo_key = f"{d_id}|{region}|{delay}|{universe}"
        if combo_key in seen:
            continue
        seen.add(combo_key)
        if not region or delay is None or not universe:
            continue

        if not dataset_id:
            existing = conn.execute(
                "SELECT COUNT(*) FROM fields WHERE wb_id LIKE ?", (f"{d_id}%",)
            ).fetchone()[0]
            if existing > 0:
                continue

        offset = 0
        limit = 50
        while True:
            time.sleep(1.1)
            resp = session.search_fields_limited(
                region=region, delay=delay, universe=universe,
                dataset_id=d_id, limit=limit, offset=offset,
            )
            if not resp.ok:
                logger.warning(f"fields API error: {resp.status_code} {resp.text[:200]} for {combo_key}")
                break
            data = resp.json()
            if isinstance(data, list):
                logger.warning(f"fields API returned list (likely error): {data} for {combo_key}")
                break
            items = data.get("results") or []
            if not items:
                break
            for item in items:
                f_id = str(item.get("id", ""))
                if not f_id:
                    continue
                raw = json.dumps(item)
                flat = _flatten(item)

                ds_id = ""
                ds_val = item.get("dataset")
                if isinstance(ds_val, dict):
                    ds_id = ds_val.get("id", "")

                existing = conn.execute(
                    "SELECT name, type, category, coverage FROM fields WHERE wb_id = ?", (f_id,)
                ).fetchone()
                if existing:
                    if (existing["name"] != flat.get("name")
                            or existing["type"] != flat.get("type")
                            or existing["category"] != flat.get("category")
                            or existing["coverage"] != flat.get("coverage")):
                        conn.execute(
                            """UPDATE fields SET name=?, type=?, category=?, coverage=?, dataset=?, dataset_id=?, raw_data=?
                               WHERE wb_id=?""",
                            (flat.get("name"), flat.get("type"), flat.get("category"),
                             flat.get("coverage"), flat.get("dataset"), ds_id, raw, f_id),
                        )
                        total += 1
                    continue
                conn.execute(
                    """INSERT INTO fields (wb_id, name, type, category, coverage, dataset, dataset_id, raw_data)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (f_id, flat.get("name"), flat.get("type"), flat.get("category"),
                     flat.get("coverage"), flat.get("dataset"), ds_id, raw),
                )
                total += 1
            if len(items) < limit:
                break
            offset += limit
    set_synced_at("fields")
    conn.commit()
    return total


def get_cached_fields(dataset_id: str | None = None) -> list[dict]:
    if dataset_id:
        rows = _get_conn().execute(
            "SELECT raw_data FROM fields WHERE dataset_id = ? ORDER BY name",
            (dataset_id,),
        ).fetchall()
    else:
        rows = _get_conn().execute(
            "SELECT raw_data FROM fields ORDER BY name"
        ).fetchall()
    return [json.loads(r["raw_data"]) for r in rows]


# ── Alphas ───────────────────────────────────────────────

def sync_alphas(session) -> int:
    import time
    conn = _get_conn()
    count = 0
    offset = 0
    limit = 100
    while True:
        resp = session.filter_alphas_limited(limit=limit, offset=offset)
        data = resp.json()
        items = data.get("results") or data.get("alphas") or []
        if not items:
            break
        for item in items:
            a_id = str(item.get("id", ""))
            if not a_id:
                continue
            raw = json.dumps(item)
            flat = _flatten(item)

            existing = conn.execute(
                "SELECT name, grade, color, status, stage FROM alphas WHERE wb_id = ?", (a_id,)
            ).fetchone()
            if existing:
                if (existing["name"] != flat.get("name")
                        or existing["grade"] != flat.get("grade")
                        or existing["color"] != flat.get("color")
                        or existing["status"] != flat.get("status")
                        or existing["stage"] != flat.get("stage")):
                    conn.execute(
                        """UPDATE alphas SET name=?, grade=?, color=?, status=?, date_created=?,
                           stage=?, tags=?, regular=?, settings=?, is_data=?, raw_data=?
                           WHERE wb_id=?""",
                        (flat.get("name"), flat.get("grade"), flat.get("color"),
                         flat.get("status"), flat.get("dateCreated"), flat.get("stage"),
                         flat.get("tags"), flat.get("regular"), flat.get("settings"),
                         flat.get("is"), raw, a_id),
                    )
                    count += 1
                continue

            conn.execute(
                """INSERT INTO alphas
                   (wb_id, name, grade, color, status, date_created, stage, tags,
                    regular, settings, is_data, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (a_id, flat.get("name"), flat.get("grade"), flat.get("color"),
                 flat.get("status"), flat.get("dateCreated"), flat.get("stage"),
                 flat.get("tags"), flat.get("regular"), flat.get("settings"),
                 flat.get("is"), raw),
            )
            count += 1
        conn.commit()
        if len(items) < limit:
            break
        offset += limit
        time.sleep(1.1)
    set_synced_at("alphas")
    conn.commit()
    return count


def get_cached_alphas() -> list[dict]:
    rows = _get_conn().execute(
        "SELECT raw_data FROM alphas ORDER BY wb_id"
    ).fetchall()
    return [json.loads(r["raw_data"]) for r in rows]


# ── Statistics ─────────────────────────────────────────────

def get_stats() -> dict:
    conn = _get_conn()
    return {
        "operators": conn.execute("SELECT COUNT(*) FROM operators").fetchone()[0],
        "datasets": conn.execute("SELECT COUNT(*) FROM datasets").fetchone()[0],
        "fields": conn.execute("SELECT COUNT(*) FROM fields").fetchone()[0],
        "alphas": conn.execute("SELECT COUNT(*) FROM alphas").fetchone()[0],
        "last_sync": {
            row["data_type"]: row["synced_at"]
            for row in conn.execute("SELECT * FROM sync_meta").fetchall()
        },
    }
