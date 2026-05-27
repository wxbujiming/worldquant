import json
import sqlite3
import datetime
import os
import threading

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
DB_PATH = os.path.join(DB_DIR, "wqb_cache.db")
_local = threading.local()


def _get_conn() -> sqlite3.Connection:
    """每个线程一个独立的连接."""
    if not hasattr(_local, "conn") or _local.conn is None:
        os.makedirs(DB_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=DELETE")
        _local.conn = conn
    return _local.conn


def init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sync_meta (
            data_type TEXT PRIMARY KEY,
            synced_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS operators (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            type TEXT,
            category TEXT,
            remarks TEXT DEFAULT '',
            raw_data TEXT
        );

        CREATE TABLE IF NOT EXISTS datasets (
            id TEXT PRIMARY KEY,
            name TEXT,
            region TEXT,
            delay INTEGER,
            universe TEXT,
            category TEXT,
            coverage REAL,
            value_score REAL,
            theme INTEGER,
            type TEXT,
            raw_data TEXT
        );

        CREATE TABLE IF NOT EXISTS fields (
            id TEXT PRIMARY KEY,
            name TEXT,
            dataset_id TEXT,
            type TEXT,
            category TEXT,
            coverage REAL,
            raw_data TEXT
        );

        CREATE TABLE IF NOT EXISTS alphas (
            id TEXT PRIMARY KEY,
            raw_data TEXT
        );
    """)
    # 兼容旧表：添加缺失的列
    for col in ("remarks",):
        try:
            conn.execute(f"ALTER TABLE operators ADD COLUMN {col} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
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
        exists = conn.execute(
            "SELECT 1 FROM operators WHERE id = ?", (op_name,)
        ).fetchone()
        if exists:
            continue
        conn.execute(
            """INSERT INTO operators
               (id, name, description, type, category, remarks, raw_data)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                op_name,
                op_name,
                item.get("description", ""),
                item.get("type", ""),
                item.get("category", ""),
                "",
                json.dumps(item),
            ),
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
        "UPDATE operators SET remarks = ? WHERE id = ?", (remarks, op_id)
    )
    _get_conn().commit()


def get_operator_remarks(op_id: str) -> str:
    row = _get_conn().execute(
        "SELECT remarks FROM operators WHERE id = ?", (op_id,)
    ).fetchone()
    return row["remarks"] if row else ""


# ── Datasets ───────────────────────────────────────────────

def sync_datasets(session) -> int:
    """同步所有数据集，不再按 region/delay/universe 过滤（API 已变更）。"""
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
            cat = item.get("category")
            category = cat.get("id") if isinstance(cat, dict) else (cat or "")
            ds_type = item.get("type")
            ds_type_str = ds_type.get("id") if isinstance(ds_type, dict) else (ds_type or "")
            composite_id = f"{ds_id}__{region}__{delay}__{universe}"
            new_name = item.get("name", "")
            new_coverage = item.get("coverage")
            new_value_score = item.get("valueScore")
            new_theme = 1 if item.get("themes") else 0
            new_raw = json.dumps(item)

            existing = conn.execute(
                """SELECT name, coverage, value_score, theme, category, type
                   FROM datasets WHERE id = ?""",
                (composite_id,),
            ).fetchone()
            if existing:
                if (existing["name"] != new_name or existing["coverage"] != new_coverage
                        or existing["value_score"] != new_value_score
                        or existing["theme"] != new_theme or existing["category"] != category
                        or existing["type"] != ds_type_str):
                    conn.execute(
                        """UPDATE datasets SET name=?, category=?, coverage=?, value_score=?, theme=?, type=?, raw_data=?
                           WHERE id=?""",
                        (new_name, category, new_coverage, new_value_score, new_theme, ds_type_str, new_raw, composite_id),
                    )
                    total += 1
                continue
            conn.execute(
                """INSERT INTO datasets
                   (id, name, region, delay, universe, category,
                    coverage, value_score, theme, type, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    composite_id,
                    new_name,
                    region,
                    delay,
                    universe,
                    category,
                    new_coverage,
                    new_value_score,
                    new_theme,
                    ds_type_str,
                    new_raw,
                ),
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
    """同步字段。

    遍历缓存数据集列表，每个条目自带 region/delay/universe。
    指定 dataset_id 时只同步该数据集的所有组合。
    dataset_id 为 None 时只同步当前字段数为 0 的数据集。
    """
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

        # 全量同步时跳过已有字段的数据集（节省时间 + 避免限流）
        if not dataset_id:
            existing = conn.execute(
                "SELECT COUNT(*) FROM fields WHERE dataset_id = ?", (d_id,)
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
            # 检测 API 错误（限流、session 过期等），避免静默失败
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
                cat = item.get("category")
                category_str = json.dumps(cat) if isinstance(cat, dict) else (cat or "")
                new_name = item.get("name", "")
                new_type = item.get("type", "")
                new_coverage = item.get("coverage")
                new_ds_id = item.get("dataset", {}).get("id", "") if isinstance(item.get("dataset"), dict) else ""

                existing = conn.execute(
                    "SELECT name, type, category, coverage, raw_data FROM fields WHERE id = ?", (f_id,)
                ).fetchone()
                if existing:
                    # 对比关键字段，有变更则更新
                    old_name = existing["name"]
                    old_type = existing["type"]
                    old_cat = existing["category"]
                    old_coverage = existing["coverage"]
                    if (old_name != new_name or old_type != new_type
                            or old_cat != category_str
                            or old_coverage != new_coverage):
                        conn.execute(
                            """UPDATE fields SET name=?, dataset_id=?, type=?, category=?, coverage=?, raw_data=?
                               WHERE id=?""",
                            (new_name, new_ds_id, new_type, category_str, new_coverage, json.dumps(item), f_id),
                        )
                        total += 1
                    continue
                conn.execute(
                    """INSERT INTO fields
                       (id, name, dataset_id, type, category, coverage, raw_data)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        f_id,
                        new_name,
                        new_ds_id,
                        new_type,
                        category_str,
                        new_coverage,
                        json.dumps(item),
                    ),
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
            exists = conn.execute(
                "SELECT 1 FROM alphas WHERE id = ?", (a_id,)
            ).fetchone()
            if exists:
                continue
            conn.execute(
                "INSERT INTO alphas (id, raw_data) VALUES (?, ?)",
                (a_id, json.dumps(item)),
            )
            count += 1
        if len(items) < limit:
            break
        offset += limit
    set_synced_at("alphas")
    conn.commit()
    return count


def get_cached_alphas() -> list[dict]:
    rows = _get_conn().execute(
        "SELECT raw_data FROM alphas ORDER BY id"
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
