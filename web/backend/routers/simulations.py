import asyncio
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..dependencies import require_session

router = APIRouter(prefix="/api/simulate", tags=["simulations"])


class SimulateRequest(BaseModel):
    alpha: dict


@router.post("")
async def simulate(req: SimulateRequest, session=Depends(require_session)):
    try:
        resp = await session.simulate(req.alpha, max_tries=range(600))
        if resp is None:
            raise HTTPException(status_code=500, detail="Simulation failed")
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_simulate(
    reqs: list[SimulateRequest],
    concurrency: int = 3,
    session=Depends(require_session),
):
    try:
        results = await session.concurrent_simulate(
            [r.alpha for r in reqs],
            concurrency=concurrency,
        )
        return [r.json() if hasattr(r, "json") else r for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
