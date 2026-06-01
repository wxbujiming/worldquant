import json
import sqlite3
import datetime
import os
import threading
from ..log_config import get_logger

logger = get_logger("cache_service")
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
            wb_id TEXT UNIQUE,
            name TEXT,
            region TEXT,
            delay INTEGER,
            universe TEXT,
            category TEXT,
            coverage REAL,
            value_score REAL,
            themes TEXT,
            type TEXT,
            description TEXT            COMMENT '描述',
            subcategory TEXT            COMMENT '子分类（JSON）',
            date_coverage REAL          COMMENT '数据覆盖日期范围',
            user_count INTEGER          COMMENT '用户数',
            alpha_count INTEGER         COMMENT 'Alpha 数',
            field_count INTEGER         COMMENT '字段数',
            research_papers TEXT        COMMENT '研究论文（JSON）',
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
            date_created TEXT       COMMENT '创建时间',
            stage TEXT,
            tags TEXT,
            regular TEXT,
            settings TEXT,
            is_data TEXT,
            type TEXT                COMMENT '类型（如 REGULAR）',
            author TEXT              COMMENT '作者/用户',
            date_submitted TEXT      COMMENT '提交时间',
            train TEXT               COMMENT '训练集数据（JSON）',
            test TEXT                COMMENT '测试集数据（JSON）',
            raw_data TEXT
        );
    """)
    conn.commit()
    _migrate_datasets_schema(conn)
    _migrate_alphas_schema(conn)
    logger.info(f"数据库初始化完成: {DB_PATH}")


def _migrate_datasets_schema(conn):
    """为 datasets 表补充新增列，并从 raw_data 回填已有数据。"""
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(datasets)").fetchall()}
    additions = []
    for col, col_type in [("description", "TEXT"), ("subcategory", "TEXT"),
                          ("date_coverage", "REAL"), ("user_count", "INTEGER"),
                          ("alpha_count", "INTEGER"), ("field_count", "INTEGER"),
                          ("research_papers", "TEXT")]:
        if col not in existing:
            additions.append(f"ALTER TABLE datasets ADD COLUMN {col} {col_type}")
    for stmt in additions:
        conn.execute(stmt)

    # 回填新增字段
    conn.execute(
        """UPDATE datasets SET
            description = json_extract(raw_data, '$.description'),
            subcategory = json_extract(raw_data, '$.subcategory'),
            date_coverage = json_extract(raw_data, '$.dateCoverage'),
            user_count = json_extract(raw_data, '$.userCount'),
            alpha_count = json_extract(raw_data, '$.alphaCount'),
            field_count = json_extract(raw_data, '$.fieldCount'),
            research_papers = json_extract(raw_data, '$.researchPapers')
           WHERE description IS NULL"""
    )
    conn.commit()


def _migrate_alphas_schema(conn):
    """为 alphas 表添加 wb_id 唯一索引，支持 UPSERT。"""
    try:
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_alphas_wb_id ON alphas(wb_id)")
        conn.commit()
    except Exception as e:
        logger.warning(f"创建 alphas 索引失败: {e}")


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
    logger.info("开始同步算子数据...")
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
    logger.info(f"算子同步完成: 新增/更新 {count} 条, 总数 {len(items)}")
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
    logger.info("开始同步数据集数据...")
    conn = _get_conn()
    _migrate_datasets_schema(conn)
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
                "SELECT 1 FROM datasets WHERE wb_id = ?",
                (composite_id,),
            ).fetchone()
            if existing:
                conn.execute(
                    """UPDATE datasets SET name=?, region=?, delay=?, universe=?, category=?,
                       coverage=?, value_score=?, themes=?, type=?,
                       description=?, subcategory=?, date_coverage=?,
                       user_count=?, alpha_count=?, field_count=?, research_papers=?, raw_data=?
                       WHERE wb_id=?""",
                    (flat.get("name"), flat.get("region"), flat.get("delay"),
                     flat.get("universe"), flat.get("category"),
                     flat.get("coverage"), flat.get("valueScore"),
                     flat.get("themes"), flat.get("type"),
                     flat.get("description"), flat.get("subcategory"),
                     flat.get("dateCoverage"), flat.get("userCount"),
                     flat.get("alphaCount"), flat.get("fieldCount"),
                     flat.get("researchPapers"), raw, composite_id),
                )
                total += 1
                continue

            conn.execute(
                """INSERT INTO datasets
                   (wb_id, name, region, delay, universe, category,
                    coverage, value_score, themes, type,
                    description, subcategory, date_coverage,
                    user_count, alpha_count, field_count, research_papers, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (composite_id, flat.get("name"), flat.get("region"), flat.get("delay"),
                 flat.get("universe"), flat.get("category"),
                 flat.get("coverage"), flat.get("valueScore"),
                 flat.get("themes"), flat.get("type"),
                 flat.get("description"), flat.get("subcategory"),
                 flat.get("dateCoverage"), flat.get("userCount"),
                 flat.get("alphaCount"), flat.get("fieldCount"),
                 flat.get("researchPapers"), raw),
            )
            total += 1
        if len(items) < limit:
            break
        offset += limit
    set_synced_at("datasets")
    conn.commit()
    logger.info(f"数据集同步完成: 同步 {total} 条")
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
    conn = _get_conn()
    total = 0
    datasets = get_cached_datasets()
    seen = set()
    logger.info(f"开始同步字段数据... datasets_count={len(datasets)} dataset_id={dataset_id}")
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
    logger.info(f"字段同步完成: 同步 {total} 条")
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
    import datetime
    conn = _get_conn()

    # 增量同步：按创建时间排序，取近 3 天数据
    # 用 date_created 而非 date_submitted，确保未提交的新 Alpha 也能被同步
    _EASTERN = datetime.timezone(datetime.timedelta(hours=-4))
    SYNC_DAYS = 3
    last_sync = get_synced_at("alphas")
    if last_sync:
        sync_since = datetime.datetime.now(_EASTERN) - datetime.timedelta(days=SYNC_DAYS)
        logger.info(f"增量同步 Alpha (since {sync_since})...")
    else:
        sync_since = None
        logger.info("全量同步 Alpha...")

    count = 0
    offset = 0
    limit = 100

    # 加载本地缓存 ID 索引，用于快速判重
    local_ids: set[str] = set()
    local_status: dict[str, tuple[str | None, str | None]] = {}
    if sync_since is not None:
        rows = conn.execute(
            "SELECT wb_id, status, date_submitted FROM alphas WHERE date_created >= ?",
            (sync_since.isoformat(),),
        ).fetchall()
        for r in rows:
            local_ids.add(r["wb_id"])
            local_status[r["wb_id"]] = (r["status"], r["date_submitted"])
    else:
        rows = conn.execute(
            "SELECT wb_id, status, date_submitted FROM alphas"
        ).fetchall()
        for r in rows:
            local_ids.add(r["wb_id"])
            local_status[r["wb_id"]] = (r["status"], r["date_submitted"])
    logger.info(f"已加载 {len(local_ids)} 条本地缓存索引")

    def _parse_dt_aware(s: str) -> datetime.datetime | None:
        """解析 ISO 时间字符串，保持时区信息。"""
        try:
            return datetime.datetime.fromisoformat(s)
        except (ValueError, TypeError):
            return None

    while True:
        kwargs = dict(limit=limit, offset=offset)
        if sync_since is not None:
            kwargs["order"] = "-dateCreated"

        resp = session.filter_alphas_limited(**kwargs)
        data = resp.json()
        if isinstance(data, list):
            items = [item for item in data if isinstance(item, dict)]
        elif isinstance(data, dict):
            items = data.get("results") or data.get("alphas") or []
        else:
            items = []
        if not items:
            break

        # 本地按创建时间过滤
        if sync_since is not None:
            filtered = []
            for item in items:
                dc = item.get("dateCreated") or item.get("date_created")
                if dc:
                    dc_dt = _parse_dt_aware(dc)
                    if dc_dt and dc_dt >= sync_since:
                        filtered.append(item)
                else:
                    filtered.append(item)
            if not filtered:
                logger.info(f"增量同步结束：后续创建时间均早于 {sync_since} (offset={offset})")
                break
            items = filtered

        # 对比本地缓存，只处理新增和状态变化的
        batch_rows = []
        batch_new_ids = []
        all_existing = True
        for item in items:
            a_id = str(item.get("id", ""))
            if not a_id:
                continue
            if a_id in local_ids:
                old_status, old_ds = local_status.get(a_id, (None, None))
                new_status = item.get("status")
                new_ds = item.get("dateSubmitted") or item.get("date_submitted")
                if old_status != new_status or old_ds != new_ds:
                    all_existing = False
                    flat = _flatten(item)
                    batch_rows.append((
                        a_id,
                        flat.get("name"), flat.get("grade"), flat.get("color"),
                        flat.get("status"), flat.get("dateCreated"), flat.get("stage"),
                        flat.get("tags"), flat.get("regular"), flat.get("settings"),
                        flat.get("is"),
                        flat.get("type"), flat.get("author"), flat.get("dateSubmitted"),
                        flat.get("train"), flat.get("test"), json.dumps(item),
                    ))
                    batch_new_ids.append(a_id)
                    local_status[a_id] = (new_status, new_ds)
            else:
                all_existing = False
                flat = _flatten(item)
                batch_rows.append((
                    a_id,
                    flat.get("name"), flat.get("grade"), flat.get("color"),
                    flat.get("status"), flat.get("dateCreated"), flat.get("stage"),
                    flat.get("tags"), flat.get("regular"), flat.get("settings"),
                    flat.get("is"),
                    flat.get("type"), flat.get("author"), flat.get("dateSubmitted"),
                    flat.get("train"), flat.get("test"), json.dumps(item),
                ))
                batch_new_ids.append(a_id)
                local_ids.add(a_id)
                local_status[a_id] = (item.get("status"),
                                      item.get("dateSubmitted") or item.get("date_submitted"))

        # 整页都是已缓存无变化数据 → 结束
        if all_existing:
            logger.info(f"增量同步结束：后续数据均已缓存 (offset={offset})")
            break

        if not batch_rows:
            if len(items) < limit:
                break
            offset += limit
            time.sleep(0.5 if sync_since is not None else 1.1)
            continue

        conn.executemany("""
            INSERT INTO alphas
                (wb_id, name, grade, color, status, date_created, stage, tags,
                 regular, settings, is_data, type, author, date_submitted, train, test, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(wb_id) DO UPDATE SET
                name=excluded.name, grade=excluded.grade, color=excluded.color,
                status=excluded.status, date_created=excluded.date_created,
                stage=excluded.stage, tags=excluded.tags, regular=excluded.regular,
                settings=excluded.settings, is_data=excluded.is_data,
                type=excluded.type, author=excluded.author,
                date_submitted=excluded.date_submitted, train=excluded.train,
                test=excluded.test, raw_data=excluded.raw_data
        """, batch_rows)

        count += len(batch_rows)
        conn.commit()

        if len(items) < limit:
            break
        offset += limit
        time.sleep(0.5 if sync_since is not None else 1.1)

    # 用 conn 直接写入 sync_meta，确保和循环使用同一连接
    now = datetime.datetime.now().isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO sync_meta (data_type, synced_at) VALUES (?, ?)",
        ("alphas", now),
    )
    conn.commit()
    logger.info(f"Alpha 同步完成: {count} 条 (synced_at={now})")
    return count


def get_cached_alphas() -> list[dict]:
    rows = _get_conn().execute(
        "SELECT raw_data FROM alphas ORDER BY wb_id"
    ).fetchall()
    return [json.loads(r["raw_data"]) for r in rows]


# ── Statistics ─────────────────────────────────────────────

def get_stats() -> dict:
    conn = _get_conn()
    op_count = conn.execute("SELECT COUNT(*) FROM operators").fetchone()[0]
    ds_count = conn.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
    f_count = conn.execute("SELECT COUNT(*) FROM fields").fetchone()[0]
    a_count = conn.execute("SELECT COUNT(*) FROM alphas").fetchone()[0]
    sync_rows = conn.execute("SELECT * FROM sync_meta").fetchall()
    last_sync = {row["data_type"]: row["synced_at"] for row in sync_rows}
    logger.info(f"查询缓存统计: operators={op_count} datasets={ds_count} fields={f_count} alphas={a_count} last_sync={last_sync}")
    return {
        "operators": op_count,
        "datasets": ds_count,
        "fields": f_count,
        "alphas": a_count,
        "last_sync": last_sync,
    }
