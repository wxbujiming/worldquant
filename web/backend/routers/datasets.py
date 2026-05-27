from fastapi import APIRouter, Depends, Query
from wqb import FilterRange
from ..dependencies import require_session

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("")
def search_datasets(
    region: str = Query(..., description="e.g. usa, eur, asia"),
    delay: int = Query(..., description="1, 2, 3, 4"),
    universe: str = Query(..., description="e.g. top3000, top2000"),
    instrument_type: str = Query("EQUITY"),
    search: str | None = None,
    category: str | None = None,
    theme: bool | None = None,
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
    resp = session.search_datasets_limited(
        region=region,
        delay=delay,
        universe=universe,
        instrument_type=instrument_type,
        search=search,
        category=category,
        theme=theme,
        coverage=coverage,
        order=order,
        limit=limit,
        offset=offset,
    )
    return resp.json()


@router.get("/{dataset_id}")
def get_dataset(dataset_id: str, session=Depends(require_session)):
    resp = session.locate_dataset(dataset_id)
    return resp.json()
