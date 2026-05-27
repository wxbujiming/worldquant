from fastapi import APIRouter, Depends, Query
from ..dependencies import require_session
from ..services.cache_service import (
    init_db,
    get_stats,
    sync_operators,
    sync_datasets,
    sync_fields,
    get_cached_operators,
    get_cached_datasets,
    get_cached_fields,
    get_synced_at,
)

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
def do_sync_datasets(
    region: str = Query("usa"),
    delay: int = Query(1),
    universe: str = Query("top3000"),
    session=Depends(require_session),
):
    init_db()
    count = sync_datasets(session, region, delay, universe)
    return {"message": f"已同步 {count} 个数据集"}


@router.post("/sync/fields")
def do_sync_fields(
    region: str = Query("usa"),
    delay: int = Query(1),
    universe: str = Query("top3000"),
    dataset_id: str | None = None,
    session=Depends(require_session),
):
    init_db()
    count = sync_fields(session, region, delay, universe, dataset_id)
    return {"message": f"已同步 {count} 个字段"}


@router.get("/operators")
def cached_operators():
    init_db()
    return {"results": get_cached_operators(), "cached": True}


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
