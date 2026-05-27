from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from wqb import FilterRange
from ..dependencies import require_session

router = APIRouter(prefix="/api/alphas", tags=["alphas"])


@router.get("")
def filter_alphas(
    name: str | None = None,
    status: str | None = None,
    region: str | None = None,
    delay: int | None = None,
    universe: str | None = None,
    instrument_type: str | None = None,
    type: str | None = None,
    language: str | None = None,
    category: str | None = None,
    color: str | None = None,
    tag: str | None = None,
    favorite: bool | None = None,
    hidden: bool | None = None,
    sharpe_min: float | None = None,
    sharpe_max: float | None = None,
    returns_min: float | None = None,
    returns_max: float | None = None,
    fitness_min: float | None = None,
    fitness_max: float | None = None,
    drawdown_min: float | None = None,
    drawdown_max: float | None = None,
    turnover_min: float | None = None,
    turnover_max: float | None = None,
    order: str | None = None,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session=Depends(require_session),
):
    sharpe = (
        FilterRange(sharpe_min, sharpe_max)
        if sharpe_min is not None or sharpe_max is not None
        else None
    )
    returns = (
        FilterRange(returns_min, returns_max)
        if returns_min is not None or returns_max is not None
        else None
    )
    fitness = (
        FilterRange(fitness_min, fitness_max)
        if fitness_min is not None or fitness_max is not None
        else None
    )
    drawdown = (
        FilterRange(drawdown_min, drawdown_max)
        if drawdown_min is not None or drawdown_max is not None
        else None
    )
    turnover = (
        FilterRange(turnover_min, turnover_max)
        if turnover_min is not None or turnover_max is not None
        else None
    )
    resp = session.filter_alphas_limited(
        name=name,
        status=status,
        region=region,
        delay=delay,
        universe=universe,
        instrument_type=instrument_type,
        type=type,
        language=language,
        category=category,
        color=color,
        tag=tag,
        favorite=favorite,
        hidden=hidden,
        sharpe=sharpe,
        returns=returns,
        fitness=fitness,
        drawdown=drawdown,
        turnover=turnover,
        order=order,
        limit=limit,
        offset=offset,
    )
    return resp.json()


@router.get("/{alpha_id}")
def get_alpha(alpha_id: str, session=Depends(require_session)):
    resp = session.locate_alpha(alpha_id)
    return resp.json()


class PatchPropertiesRequest(BaseModel):
    name: str | None = None
    category: str | None = None
    color: str | None = None
    tags: list[str] | None = None
    favorite: bool | None = None
    hidden: bool | None = None
    regular_description: str | None = None


@router.patch("/{alpha_id}")
def patch_alpha(
    alpha_id: str,
    body: PatchPropertiesRequest,
    session=Depends(require_session),
):
    kwargs = body.model_dump(exclude_none=True)
    resp = session.patch_properties(alpha_id, **kwargs)
    return resp.json()


@router.post("/{alpha_id}/simulate")
async def simulate_alpha(alpha_id: str, session=Depends(require_session)):
    try:
        alpha = session.locate_alpha(alpha_id).json()
        resp = await session.simulate(alpha, max_tries=range(600))
        if resp is None:
            raise HTTPException(status_code=500, detail="Simulation failed")
        return resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alpha_id}/check")
async def check_alpha(alpha_id: str, session=Depends(require_session)):
    try:
        resp = await session.check(alpha_id, max_tries=range(600))
        if resp is None:
            raise HTTPException(status_code=500, detail="Check failed")
        return resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alpha_id}/submit")
async def submit_alpha(alpha_id: str, session=Depends(require_session)):
    try:
        resp = await session.submit(alpha_id, max_tries=range(600))
        if resp is None:
            raise HTTPException(status_code=500, detail="Submit failed")
        return resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
