from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from ..dependencies import require_session
from ..log_config import get_logger
from ..services.cache_service import (
    init_db,
    get_stats,
    sync_operators,
    sync_datasets,
    sync_fields,
    sync_alphas,
    get_cached_operators,
    get_cached_datasets,
    get_cached_dataset_kinds,
    get_cached_fields,
    get_cached_alphas,
    get_synced_at,
    update_operator_remarks,
    get_operator_remarks,
)


class RemarksBody(BaseModel):
    remarks: str

logger = get_logger("cache")
router = APIRouter(prefix="/api/cache", tags=["cache"])


@router.get("/stats")
def cache_stats():
    init_db()
    stats = get_stats()
    logger.info(f"查询缓存统计: {stats}")
    return stats


@router.post("/sync/operators")
def do_sync_operators(session=Depends(require_session)):
    init_db()
    logger.info("开始同步算子...")
    count = sync_operators(session)
    logger.info(f"算子同步完成: {count} 条")
    return {"message": f"已同步 {count} 个算子"}


@router.post("/sync/datasets")
def do_sync_datasets(session=Depends(require_session)):
    init_db()
    logger.info("开始同步数据集...")
    count = sync_datasets(session)
    logger.info(f"数据集同步完成: {count} 条")
    return {"message": f"已同步 {count} 个数据集"}


@router.post("/sync/fields")
def do_sync_fields(
    dataset_id: str | None = None,
    session=Depends(require_session),
):
    init_db()
    logger.info(f"开始同步字段... dataset_id={dataset_id}")
    count = sync_fields(session, dataset_id)
    logger.info(f"字段同步完成: {count} 条")
    return {"message": f"已同步 {count} 个字段"}


@router.get("/operators")
def cached_operators():
    init_db()
    items = get_cached_operators()
    # 附加 remarks 字段
    for item in items:
        item["remarks"] = get_operator_remarks(item.get("name", ""))
    logger.info(f"查询缓存算子: {len(items)} 条")
    return {"results": items, "cached": True}


@router.patch("/operators/{op_id}/remarks")
def patch_operator_remarks(op_id: str, body: RemarksBody):
    init_db()
    logger.info(f"更新算子备注: op_id={op_id}")
    update_operator_remarks(op_id, body.remarks)
    return {"message": "备注已更新"}


@router.get("/datasets")
def cached_datasets(
    region: str | None = None,
    delay: int | None = None,
    universe: str | None = None,
):
    init_db()
    # 统一转大写匹配数据库存储格式
    if region:
        region = region.upper()
    if universe:
        universe = universe.upper()
    items = get_cached_datasets(region, delay, universe)
    logger.info(f"查询缓存数据集: {len(items)} 条 (region={region} delay={delay} universe={universe})")
    return {"results": items, "count": len(items), "cached": True}


@router.get("/dataset-kinds")
def cached_dataset_kinds():
    init_db()
    items = get_cached_dataset_kinds()
    logger.info(f"查询缓存数据集种类: {len(items)} 条")
    return {"results": items, "count": len(items), "cached": True}


@router.get("/fields")
def cached_fields(dataset_id: str | None = None):
    init_db()
    items = get_cached_fields(dataset_id)
    logger.info(f"查询缓存字段: {len(items)} 条 (dataset_id={dataset_id})")
    return {"results": items, "count": len(items), "cached": True}


@router.post("/sync/alphas")
def do_sync_alphas(
    sync_date_from: str | None = Query(None, description="同步起始日期 (ISO 格式，如 2026-06-01)"),
    sync_date_to: str | None = Query(None, description="同步截止日期 (ISO 格式，如 2026-06-22)"),
    session=Depends(require_session),
):
    init_db()
    logger.info(f"开始同步 Alpha... sync_date_from={sync_date_from} sync_date_to={sync_date_to}")
    count = sync_alphas(session, sync_date_from, sync_date_to)
    logger.info(f"Alpha 同步完成: {count} 条")
    return {"message": f"已同步 {count} 个 Alpha"}


@router.get("/alphas")
def cached_alphas():
    init_db()
    items = get_cached_alphas()
    logger.info(f"查询缓存 Alpha: {len(items)} 条")
    return {"results": items, "count": len(items), "cached": True}
