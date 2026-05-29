from fastapi import APIRouter, Depends, Query
from wqb import FilterRange
from ..dependencies import require_session
from ..log_config import get_logger

logger = get_logger("fields")
router = APIRouter(prefix="/api/fields", tags=["fields"])


@router.get("")
def search_fields(
    region: str = Query(..., description="e.g. usa, eur, asia"),
    delay: int = Query(..., description="1, 2, 3, 4"),
    universe: str = Query(..., description="e.g. top3000, top2000"),
    instrument_type: str = Query("EQUITY"),
    dataset_id: str | None = None,
    search: str | None = None,
    category: str | None = None,
    type: str | None = None,
    coverage_min: float | None = None,
    coverage_max: float | None = None,
    order: str | None = None,
    limit: int = Query(50, ge=1, le=50),
    offset: int = Query(0, ge=0),
    session=Depends(require_session),
):
    coverage = (
        FilterRange(coverage_min, coverage_max)
        if coverage_min is not None or coverage_max is not None
        else None
    )
    logger.info(f"搜索字段: region={region} delay={delay} universe={universe} "
                f"dataset_id={dataset_id} search={search} category={category} limit={limit} offset={offset}")
    resp = session.search_fields_limited(
        region=region,
        delay=delay,
        universe=universe,
        instrument_type=instrument_type,
        dataset_id=dataset_id,
        search=search,
        category=category,
        type=type,
        coverage=coverage,
        order=order,
        limit=limit,
        offset=offset,
    )
    data = resp.json()
    results = data.get("results", [])
    logger.info(f"字段搜索完成: 返回 {len(results)} 条")
    return data


@router.get("/{field_id}")
def get_field(field_id: str, session=Depends(require_session)):
    logger.info(f"获取字段详情: field_id={field_id}")
    resp = session.locate_field(field_id)
    return resp.json()
