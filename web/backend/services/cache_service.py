import json
import sqlite3
import datetime
import os
import threading
from ..log_config import get_logger

logger = get_logger("cache_service")
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

        CREATE TABLE IF NOT EXISTS dataset_kinds (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            subcategory TEXT,
            type TEXT,
            raw_data TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS dataset_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind_id TEXT NOT NULL REFERENCES dataset_kinds(id),
            wb_id TEXT UNIQUE,
            region TEXT NOT NULL,
            delay INTEGER NOT NULL,
            universe TEXT NOT NULL,
            coverage REAL,
            value_score REAL,
            themes TEXT,
            date_coverage REAL,
            user_count INTEGER,
            alpha_count INTEGER,
            field_count INTEGER,
            research_papers TEXT,
            raw_data TEXT
        );

        -- 旧表保留用于迁移，后续可删除
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
    _migrate_to_kind_variant(conn)
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


def _migrate_to_kind_variant(conn):
    """将旧 datasets 表的数据迁移到 dataset_kinds + dataset_variants。"""
    try:
        # 检查旧表是否有数据且新表为空
        old_count = conn.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
        if old_count == 0:
            return
        new_count = conn.execute("SELECT COUNT(*) FROM dataset_kinds").fetchone()[0]
        if new_count > 0:
            return

        logger.info(f"开始迁移 {old_count} 条数据集到新表结构...")

        # 查出所有唯一 kind
        rows = conn.execute("""
            SELECT DISTINCT
                substr(wb_id, 1, instr(wb_id, '__') - 1) as kind_id,
                name, description, category, subcategory, type, raw_data
            FROM datasets
            WHERE wb_id LIKE '%__%'
        """).fetchall()

        for row in rows:
            kind_id = row["kind_id"]
            if not kind_id:
                continue
            # 取第一个变体的 raw_data 作为 kind 的 raw_data
            conn.execute(
                """INSERT OR IGNORE INTO dataset_kinds (id, name, description, category, subcategory, type, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (kind_id, row["name"], row["description"],
                 row["category"], row["subcategory"], row["type"], row["raw_data"]),
            )

        # 迁移所有 variant 到 dataset_variants
        conn.execute("""
            INSERT OR IGNORE INTO dataset_variants
                (kind_id, wb_id, region, delay, universe,
                 coverage, value_score, themes, date_coverage,
                 user_count, alpha_count, field_count, research_papers, raw_data)
            SELECT
                substr(wb_id, 1, instr(wb_id, '__') - 1),
                wb_id, region, delay, universe,
                coverage, value_score, themes, date_coverage,
                user_count, alpha_count, field_count, research_papers, raw_data
            FROM datasets
            WHERE wb_id LIKE '%__%'
        """)

        conn.commit()
        migrated = conn.execute("SELECT COUNT(*) FROM dataset_variants").fetchone()[0]
        logger.info(f"数据迁移完成: {len(rows)} 种数据集种类, {migrated} 个变体")
    except Exception as e:
        logger.warning(f"迁移数据集结构失败: {e}")


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

            # 1) 写入 dataset_kinds（唯一种类）
            conn.execute(
                """INSERT OR IGNORE INTO dataset_kinds
                   (id, name, description, category, subcategory, type, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (ds_id, flat.get("name"), flat.get("description"),
                 flat.get("category"), flat.get("subcategory"), flat.get("type"), raw),
            )

            # 2) 写入 dataset_variants（具体变体）
            conn.execute(
                """INSERT OR REPLACE INTO dataset_variants
                   (kind_id, wb_id, region, delay, universe,
                    coverage, value_score, themes, date_coverage,
                    user_count, alpha_count, field_count, research_papers, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (ds_id, composite_id, flat.get("region"), flat.get("delay"),
                 flat.get("universe"),
                 flat.get("coverage"), flat.get("valueScore"),
                 flat.get("themes"), flat.get("dateCoverage"),
                 flat.get("userCount"), flat.get("alphaCount"),
                 flat.get("fieldCount"), flat.get("researchPapers"), raw),
            )

            # 3) 写入旧表保持向后兼容
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
    """
    从 dataset_variants 查询已缓存的数据集变体。
    返回 raw_data 列表（与旧格式兼容）。
    """
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
    sql = "SELECT raw_data FROM dataset_variants"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY wb_id"
    rows = _get_conn().execute(sql, params).fetchall()
    if not rows:
        # fallback: 旧表
        sql = "SELECT raw_data FROM datasets"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY wb_id"
        rows = _get_conn().execute(sql, params).fetchall()
    return [json.loads(r["raw_data"]) for r in rows]


def get_cached_dataset_kinds() -> list[dict]:
    """返回所有已缓存的 dataset_kinds 列表（含变体数）。"""
    rows = _get_conn().execute("""
        SELECT k.id, k.name, k.description, k.category, k.subcategory, k.type,
               (SELECT COUNT(*) FROM dataset_variants v WHERE v.kind_id = k.id) as variant_count,
               (SELECT COUNT(*) FROM fields f WHERE f.dataset_id = k.id) as field_count
        FROM dataset_kinds k
        ORDER BY k.name
    """).fetchall()
    if not rows:
        return []
    results = []
    for r in rows:
        d = dict(r)
        # 反序列化 JSON 字段便于前端直接使用
        for field in ("category", "subcategory"):
            val = d.get(field)
            if val and isinstance(val, str):
                try:
                    d[field] = json.loads(val)
                except (json.JSONDecodeError, TypeError):
                    pass
        results.append(d)
    return results


# ── Fields ─────────────────────────────────────────────────

def sync_fields(session, dataset_id: str | None = None) -> int:
    import time
    conn = _get_conn()
    total = 0
    # 按种类去重，每种只需同步一次（字段按 kind_id 存储）
    rows = conn.execute("""
        SELECT kind_id, region, delay, universe
        FROM dataset_variants
        GROUP BY kind_id
        ORDER BY kind_id
    """).fetchall()
    if not rows:
        # fallback: 旧表（向后兼容）
        fallback_rows = _get_conn().execute("""
            SELECT
                substr(wb_id, 1, instr(wb_id, '__') - 1) as kind_id,
                region, delay, universe
            FROM datasets WHERE wb_id LIKE '%__%'
            GROUP BY kind_id
        """).fetchall()
        if not fallback_rows:
            return 0
        rows = fallback_rows

    logger.info(f"开始同步字段数据... datasets_count={len(rows)} dataset_id={dataset_id}")
    for row in rows:
        d_id = row["kind_id"]
        if not d_id:
            continue
        if dataset_id and d_id != dataset_id:
            continue
        region = row["region"]
        delay = row["delay"]
        universe = row["universe"]
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
        max_pages = 200  # 最多 200 页（10000 条），防止死循环
        for page in range(1, max_pages + 1):
            time.sleep(1.1)
            resp = session.search_fields_limited(
                region=region, delay=delay, universe=universe,
                dataset_id=d_id, limit=limit, offset=offset,
            )
            if not resp.ok:
                logger.warning(f"fields API error: {resp.status_code} {resp.text[:200]} for {d_id}/{region}/{delay}/{universe}")
                break
            data = resp.json()
            if isinstance(data, list):
                logger.warning(f"fields API returned list (likely error): {data} for {d_id}/{region}/{delay}/{universe}")
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

            # 判断是否最后一页：API 返回总数 或 返回数不足 limit
            total_count = data.get("count", data.get("total", 0))
            if total_count and offset + len(items) >= total_count:
                logger.info(f"字段分页结束（总数）: {d_id}/{region}/{delay}/{universe} offset={offset} total={total_count}")
                break
            if len(items) < limit:
                break
            offset += limit
        else:
            logger.warning(f"字段同步超过最大页数限制 ({max_pages})，强制终止: {d_id}/{region}/{delay}/{universe}")


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

def _parse_dt_aware(s: str) -> datetime.datetime | None:
    """解析 ISO 时间字符串，保持时区信息。"""
    try:
        return datetime.datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def sync_alphas(session,
                sync_date_from: str | None = None,
                sync_date_to: str | None = None) -> int:
    """
    按时间窗口分块同步 Alpha。

    WQB API 的 offset 上限为 10000（filter_alphas_limited 硬编码限制），
    当 Alpha 条数超过时纯 offset 翻页会死循环。
    此函数将时间范围拆分为 180 天窗口，每个窗口内用 API 返回的 count 控制翻页，
    若某窗口超过 9500 条则递归拆分为子窗口，确保永不触及 10000 限制。

    参数:
        sync_date_from: 起始日期 (ISO 格式 YYYY-MM-DD)，None 则按增量/全量决定
        sync_date_to:   截止日期 (ISO 格式 YYYY-MM-DD)，None 则到"现在"
    """
    import time
    import datetime
    conn = _get_conn()
    _EASTERN = datetime.timezone(datetime.timedelta(hours=-4))
    SYNC_DAYS = 5
    WINDOW_DAYS = 180
    MAX_ITEMS_PER_WINDOW = 9500

    # ── 确定时间范围 ────────────────────────────────────────
    now_et = datetime.datetime.now(_EASTERN)
    has_from = sync_date_from is not None
    has_to = sync_date_to is not None

    if has_from:
        from_dt = datetime.datetime.fromisoformat(sync_date_from)
        if from_dt.tzinfo is None:
            from_dt = from_dt.replace(tzinfo=_EASTERN)
    else:
        last_sync = get_synced_at("alphas")
        if last_sync:
            from_dt = now_et - datetime.timedelta(days=SYNC_DAYS)
        else:
            from_dt = datetime.datetime(2018, 1, 1, tzinfo=_EASTERN)

    if has_to:
        to_dt = datetime.datetime.fromisoformat(sync_date_to)
        if to_dt.tzinfo is None:
            to_dt = to_dt.replace(tzinfo=_EASTERN)
    else:
        to_dt = now_et

    # 空范围 → 直接返回
    if from_dt >= to_dt:
        logger.info("同步范围为空，跳过")
        return 0

    if has_from or has_to:
        logger.info(f"指定日期同步 Alpha (from={from_dt.isoformat()} to={to_dt.isoformat()})...")
    else:
        last_sync = get_synced_at("alphas")
        if last_sync:
            logger.info(f"增量同步 Alpha (since {from_dt.date()})...")
        else:
            logger.info("全量同步 Alpha...")

    # ── 拆分 180 天时间窗口 ─────────────────────────────────
    raw_windows: list[tuple[datetime.datetime, datetime.datetime]] = []
    cursor = from_dt
    while cursor < to_dt:
        end = min(cursor + datetime.timedelta(days=WINDOW_DAYS), to_dt)
        raw_windows.append((cursor, end))
        cursor = end

    # ── 加载本地缓存索引 ────────────────────────────────────
    local_ids: set[str] = set()
    local_status: dict[str, tuple[str | None, str | None]] = {}
    rows = conn.execute(
        "SELECT wb_id, status, date_submitted FROM alphas"
    ).fetchall()
    for r in rows:
        local_ids.add(r["wb_id"])
        local_status[r["wb_id"]] = (r["status"], r["date_submitted"])
    logger.info(f"已加载 {len(local_ids)} 条本地缓存索引")

    from wqb.filter_range import FilterRange

    total_count = 0

    def _window_count(win_start: datetime.datetime,
                      win_end: datetime.datetime) -> int:
        """获取一个时间窗口内的 Alpha 总数（一次轻量 API 调用）。"""
        fr = FilterRange(lo=win_start, hi=win_end, lo_eq=True, hi_eq=False)
        resp = session.filter_alphas_limited(date_created=fr, limit=1, offset=0)
        data = resp.json()
        return data.get("count", data.get("total", 0))

    def _sync_window(win_start: datetime.datetime,
                     win_end: datetime.datetime,
                     expected: int) -> int:
        """同步单个时间窗口内的所有 Alpha。"""
        fr = FilterRange(lo=win_start, hi=win_end, lo_eq=True, hi_eq=False)
        offset = 0
        limit = 100
        win_count = 0

        while offset < expected:
            resp = session.filter_alphas_limited(
                date_created=fr, limit=limit, offset=offset,
                order="-dateCreated",
            )
            data = resp.json()
            items = data.get("results") or data.get("alphas") or []
            if not items:
                break

            batch_rows = []
            for item in items:
                a_id = str(item.get("id", ""))
                if not a_id:
                    continue
                if a_id in local_ids:
                    old_status, old_ds = local_status.get(a_id, (None, None))
                    new_status = item.get("status")
                    new_ds = item.get("dateSubmitted") or item.get("date_submitted")
                    if old_status != new_status or old_ds != new_ds:
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
                        local_status[a_id] = (new_status, new_ds)
                else:
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
                    local_ids.add(a_id)
                    local_status[a_id] = (
                        item.get("status"),
                        item.get("dateSubmitted") or item.get("date_submitted"),
                    )

            if batch_rows:
                conn.executemany("""
                    INSERT INTO alphas
                        (wb_id, name, grade, color, status, date_created, stage, tags,
                         regular, settings, is_data, type, author, date_submitted,
                         train, test, raw_data)
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
                win_count += len(batch_rows)
                conn.commit()

            offset += limit
            time.sleep(0.5)

        return win_count

    def _sync_window_range(win_start: datetime.datetime,
                           win_end: datetime.datetime) -> int:
        """
        递归处理时间窗口：检查数据量，若超过上限则拆分。
        返回该范围内同步的条数。
        """
        count = _window_count(win_start, win_end)
        if count == 0:
            return 0
        if count >= MAX_ITEMS_PER_WINDOW:
            mid = win_start + (win_end - win_start) / 2
            logger.info(
                f"窗口 {win_start.date()}~{win_end.date()} 含 {count} 条"
                f"，超过上限 {MAX_ITEMS_PER_WINDOW}，拆分为子窗口"
            )
            sub1 = _sync_window_range(win_start, mid)
            sub2 = _sync_window_range(mid, win_end)
            return sub1 + sub2
        logger.info(
            f"同步窗口 {win_start.date()}~{win_end.date()} ({count} 条)..."
        )
        return _sync_window(win_start, win_end, count)

    # ── 执行同步 ────────────────────────────────────────────
    for ws, we in raw_windows:
        if has_from or has_to:
            # 用户指定日期 → 检查并拆分大窗口
            sub_count = _sync_window_range(ws, we)
            total_count += sub_count
        else:
            # 增量同步（5 天），不可能超过 9500 → 直接同步
            win_count = _window_count(ws, we)
            if win_count > 0:
                n = _sync_window(ws, we, win_count)
                total_count += n
                logger.info(f"增量窗口 {ws.date()}~{we.date()} 完成 ({n} 条)")
            else:
                logger.info(f"增量窗口 {ws.date()}~{we.date()} 无数据")

    # ── 记录同步时间 ────────────────────────────────────────
    now_str = datetime.datetime.now().isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO sync_meta (data_type, synced_at) VALUES (?, ?)",
        ("alphas", now_str),
    )
    conn.commit()
    logger.info(f"Alpha 同步完成: 共 {total_count} 条 (synced_at={now_str})")
    return total_count


def get_cached_alphas() -> list[dict]:
    rows = _get_conn().execute(
        "SELECT raw_data FROM alphas ORDER BY wb_id"
    ).fetchall()
    return [json.loads(r["raw_data"]) for r in rows]


# ── Statistics ─────────────────────────────────────────────

def get_stats() -> dict:
    conn = _get_conn()
    op_count = conn.execute("SELECT COUNT(*) FROM operators").fetchone()[0]
    ds_variants = conn.execute("SELECT COUNT(*) FROM dataset_variants").fetchone()[0]
    ds_kinds = conn.execute("SELECT COUNT(*) FROM dataset_kinds").fetchone()[0]
    f_count = conn.execute("SELECT COUNT(*) FROM fields").fetchone()[0]
    a_count = conn.execute("SELECT COUNT(*) FROM alphas").fetchone()[0]
    sync_rows = conn.execute("SELECT * FROM sync_meta").fetchall()
    last_sync = {row["data_type"]: row["synced_at"] for row in sync_rows}
    logger.info(f"查询缓存统计: operators={op_count} dataset_kinds={ds_kinds} dataset_variants={ds_variants} fields={f_count} alphas={a_count} last_sync={last_sync}")
    return {
        "operators": op_count,
        "dataset_kinds": ds_kinds,
        "dataset_variants": ds_variants,
        "datasets": ds_variants,  # 向后兼容
        "fields": f_count,
        "alphas": a_count,
        "last_sync": last_sync,
    }
