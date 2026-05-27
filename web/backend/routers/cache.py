from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from ..dependencies import require_session
from ..services.cache_service import (
    init_db,
    get_stats,
    sync_operators,
    sync_datasets,
    sync_fields,
    sync_alphas,
    get_cached_operators,
    get_cached_datasets,
    get_cached_fields,
    get_cached_alphas,
    get_synced_at,
    update_operator_remarks,
    get_operator_remarks,
)


class RemarksBody(BaseModel):
    remarks: str

router = APIRouter(prefix="/api/cache", tags=["cache"])


@router.get("/stats")
def cache_stats():
    init_db()
    return get_stats()


@router.post("/sync/operators")
def do_sync_operators(session=Depends(require_session)):
    init_db()
    count = sync_operators(session)
    return {"message": f"已同步 {count} 个算子"}


@router.post("/sync/datasets")
def do_sync_datasets(session=Depends(require_session)):
    init_db()
    count = sync_datasets(session)
    return {"message": f"已同步 {count} 个数据集"}


@router.post("/sync/fields")
def do_sync_fields(
    dataset_id: str | None = None,
    session=Depends(require_session),
):
    init_db()
    count = sync_fields(session, dataset_id)
    return {"message": f"已同步 {count} 个字段"}


@router.get("/operators")
def cached_operators():
    init_db()
    items = get_cached_operators()
    # 附加 remarks 字段
    for item in items:
        item["remarks"] = get_operator_remarks(item.get("name", ""))
    return {"results": items, "cached": True}


@router.patch("/operators/{op_id}/remarks")
def patch_operator_remarks(op_id: str, body: RemarksBody):
    init_db()
    update_operator_remarks(op_id, body.remarks)
    return {"message": "备注已更新"}


@router.get("/datasets")
def cached_datasets(
    region: str | None = None,
    delay: int | None = None,
    universe: str | None = None,
):
    init_db()
    items = get_cached_datasets(region, delay, universe)
    return {"results": items, "count": len(items), "cached": True}


@router.get("/fields")
def cached_fields(dataset_id: str | None = None):
    init_db()
    items = get_cached_fields(dataset_id)
    return {"results": items, "count": len(items), "cached": True}


@router.post("/sync/alphas")
def do_sync_alphas(session=Depends(require_session)):
    init_db()
    count = sync_alphas(session)
    return {"message": f"已同步 {count} 个 Alpha"}


@router.get("/alphas")
def cached_alphas():
    init_db()
    items = get_cached_alphas()
    return {"results": items, "count": len(items), "cached": True}
