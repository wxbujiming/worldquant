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
        conn.execute(
            """INSERT OR REPLACE INTO operators
               (id, name, description, type, category, raw_data)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                str(item.get("id", "")),
                item.get("name", ""),
                item.get("description", ""),
                item.get("type", ""),
                item.get("category", ""),
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


# ── Datasets ───────────────────────────────────────────────

def sync_datasets(session, region: str, delay: int, universe: str) -> int:
    conn = _get_conn()
    count = 0
    for resp in session.search_datasets(region=region, delay=delay, universe=universe, limit=50):
        data = resp.json()
        items = data.get("results") or data.get("datasets") or []
        for item in items:
            conn.execute(
                """INSERT OR REPLACE INTO datasets
                   (id, name, region, delay, universe, category,
                    coverage, value_score, theme, type, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(item.get("id", "")),
                    item.get("name", ""),
                    region,
                    delay,
                    universe,
                    item.get("category", ""),
                    item.get("coverage"),
                    item.get("valueScore"),
                    1 if item.get("theme") else 0,
                    item.get("type", ""),
                    json.dumps(item),
                ),
            )
            count += 1
    set_synced_at(f"datasets_{region}_{delay}_{universe}")
    conn.commit()
    return count


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
            conn.execute(
                """INSERT OR REPLACE INTO fields
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


# ── Statistics ─────────────────────────────────────────────

def get_stats() -> dict:
    conn = _get_conn()
    return {
        "operators": conn.execute("SELECT COUNT(*) FROM operators").fetchone()[0],
        "datasets": conn.execute("SELECT COUNT(*) FROM datasets").fetchone()[0],
        "fields": conn.execute("SELECT COUNT(*) FROM fields").fetchone()[0],
        "last_sync": {
            row["data_type"]: row["synced_at"]
            for row in conn.execute("SELECT * FROM sync_meta").fetchall()
        },
    }
