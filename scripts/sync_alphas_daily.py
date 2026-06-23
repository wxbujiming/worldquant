"""
Daily Alpha sync script.

Syncs Alpha data day-by-day from 2026-05-17 to today.
Skips existing wb_ids to avoid duplicates.

Usage:
    cd d:/Automation/github_wxbujiming/worldquant
    source .venv/Scripts/activate
    python scripts/sync_alphas_daily.py
"""

import os
import sys
import json
import time
import datetime
import sqlite3

# ── 路径配置 ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))     # <project>/scripts/
PROJECT_DIR = os.path.dirname(BASE_DIR)                   # <project>/
sys.path.insert(0, PROJECT_DIR)

DB_DIR = os.path.join(PROJECT_DIR, "web", "backend", "cache")
DB_PATH = os.path.join(DB_DIR, "wqb_cache.db")

# 从 .env 读取账号
from pydantic_settings import BaseSettings
from pathlib import Path


class _Settings(BaseSettings):
    wqb_email: str = ""
    wqb_password: str = ""

    model_config = {
        "env_file": str(Path(PROJECT_DIR) / "web" / ".env"),
        "env_file_encoding": "utf-8",
    }


settings = _Settings()

# ── 参数 ──────────────────────────────────────────────────
START_DATE = datetime.date(2026, 5, 17)
END_DATE = datetime.date.today()
_EASTERN = datetime.timezone(datetime.timedelta(hours=-4))


def main():
    email = settings.wqb_email.strip().strip("'\"")
    password = settings.wqb_password.strip().strip("'\"")

    if not email or not password:
        print("[ERROR] web/.env 中 WQB_EMAIL 或 WQB_PASSWORD 未设置")
        sys.exit(1)

    # ── 连接数据库 ──────────────────────────────────────────
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=DELETE")

    # 确保 alphas 表有 wb_id 唯一索引（支持 UPSERT）
    try:
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_alphas_wb_id ON alphas(wb_id)")
    except Exception:
        pass
    conn.commit()

    # ── 加载已有 wb_id ──────────────────────────────────────
    existing = {
        row[0]
        for row in conn.execute("SELECT wb_id FROM alphas WHERE wb_id IS NOT NULL").fetchall()
    }
    print(f"[INFO] 数据库已有 {len(existing)} 条 Alpha 记录")

    # ── 登录 WQB ────────────────────────────────────────────
    from wqb import WQBSession
    from wqb.filter_range import FilterRange

    print(f"[INFO] 登录 WQB: {email}")
    session = WQBSession((email, password))
    session.post_authentication()
    print("[INFO] 登录成功")

    # ── 逐天同步 ────────────────────────────────────────────
    cursor = START_DATE
    total_new = 0
    total_skipped = 0
    total_empty_days = 0
    day_count = (END_DATE - START_DATE).days + 1

    print(f"\n[INFO] 开始逐天同步 {START_DATE} ~ {END_DATE}，共 {day_count} 天")

    while cursor <= END_DATE:
        day_start = datetime.datetime.combine(cursor, datetime.time.min, tzinfo=_EASTERN)
        day_end = datetime.datetime.combine(cursor, datetime.time.max, tzinfo=_EASTERN)

        # API 过滤：date_created 在当天范围内
        fr = FilterRange(lo=day_start, hi=day_end, lo_eq=True, hi_eq=True)

        # 先获取 count
        resp = session.filter_alphas_limited(date_created=fr, limit=1, offset=0)
        data = resp.json()
        count = data.get("count", data.get("total", 0))

        if count == 0:
            total_empty_days += 1
            cursor += datetime.timedelta(days=1)
            continue

        # 翻页获取该天所有 Alpha
        limit = 100
        offset = 0
        day_new = 0
        day_skipped = 0

        while offset < count:
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
                if a_id in existing:
                    day_skipped += 1
                    continue

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
                conn.commit()
                for row in batch_rows:
                    existing.add(row[0])
                day_new += len(batch_rows)

            offset += limit
            time.sleep(0.3)

        total_new += day_new
        total_skipped += day_skipped

        if day_new > 0 or day_skipped > 0:
            print(f"  {cursor}  -> 新增 {day_new:4d}, 跳过 {day_skipped:4d}, 共 {count} 条")
        cursor += datetime.timedelta(days=1)

        time.sleep(0.5)

    # ── 记录同步时间 ────────────────────────────────────────
    now_str = datetime.datetime.now().isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO sync_meta (data_type, synced_at) VALUES (?, ?)",
        ("alphas", now_str),
    )
    conn.commit()
    conn.close()

    print(f"\n[INFO] 同步完成!")
    print(f"  新增: {total_new} 条")
    print(f"  跳过(已有): {total_skipped} 条")
    print(f"  空日期: {total_empty_days} 天")
    print(f"  总日期: {day_count} 天")


def _flatten(item: dict) -> dict:
    """将 JSON 第一层字段展平，嵌套 dict/list 转 JSON 字符串。"""
    out = {}
    for k, v in item.items():
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v)
        else:
            out[k] = v
    return out


if __name__ == "__main__":
    main()
