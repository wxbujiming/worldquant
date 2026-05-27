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
            # 组合唯一 ID（同一基础 ID 可能有不同 region/delay/universe）
            composite_id = f"{ds_id}__{region}__{delay}__{universe}"
            exists = conn.execute(
                "SELECT 1 FROM datasets WHERE id = ?", (composite_id,)
            ).fetchone()
            if exists:
                continue
            conn.execute(
                """INSERT INTO datasets
                   (id, name, region, delay, universe, category,
                    coverage, value_score, theme, type, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    composite_id,
                    item.get("name", ""),
                    region,
                    delay,
                    universe,
                    category,
                    item.get("coverage"),
                    item.get("valueScore"),
                    1 if item.get("themes") else 0,
                    ds_type_str,
                    json.dumps(item),
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

def sync_fields(session, region: str, delay: int, universe: str,
                dataset_id: str | None = None) -> int:
    conn = _get_conn()
    count = 0
    kw = dict(region=region, delay=delay, universe=universe, limit=50)
    if dataset_id:
        kw["dataset_id"] = dataset_id
    for resp in session.search_fields(**kw):
        data = resp.json()
        items = data.get("results") or data.get("fields") or []
        for item in items:
            f_id = str(item.get("id", ""))
            if not f_id:
                continue
            exists = conn.execute(
                "SELECT 1 FROM fields WHERE id = ?", (f_id,)
            ).fetchone()
            if exists:
                continue
            conn.execute(
                """INSERT INTO fields
                   (id, name, dataset_id, type, category, coverage, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(item.get("id", "")),
                    item.get("name", ""),
                    item.get("dataset", {}).get("id", "") if isinstance(item.get("dataset"), dict) else "",
                    item.get("type", ""),
                    item.get("category", ""),
                    item.get("coverage"),
                    json.dumps(item),
                ),
            )
            count += 1
    tag = f"fields_{region}_{delay}_{universe}"
    if dataset_id:
        tag += f"_{dataset_id}"
    set_synced_at(tag)
    conn.commit()
    return count


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
