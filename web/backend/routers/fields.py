from fastapi import APIRouter, Depends, Query
from wqb import FilterRange
from ..dependencies import require_session

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
    return resp.json()


@router.get("/{field_id}")
def get_field(field_id: str, session=Depends(require_session)):
    resp = session.locate_field(field_id)
    return resp.json()
