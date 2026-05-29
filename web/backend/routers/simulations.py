import asyncio
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..dependencies import require_session
from ..log_config import get_logger

logger = get_logger("simulations")
router = APIRouter(prefix="/api/simulate", tags=["simulations"])


class SimulateRequest(BaseModel):
    alpha: dict


@router.post("")
async def simulate(req: SimulateRequest, session=Depends(require_session)):
    alpha_id = req.alpha.get("id", "unknown")
    logger.info(f"开始模拟: alpha_id={alpha_id}")
    try:
        resp = await session.simulate(req.alpha, max_tries=range(600))
        if resp is None:
            logger.warning(f"模拟失败: alpha_id={alpha_id}")
            raise HTTPException(status_code=500, detail="Simulation failed")
        logger.info(f"模拟完成: alpha_id={alpha_id}")
        return resp.json()
    except Exception as e:
        logger.error(f"模拟异常: alpha_id={alpha_id} error={e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_simulate(
    reqs: list[SimulateRequest],
    concurrency: int = 3,
    session=Depends(require_session),
):
    alpha_ids = [r.alpha.get("id", "unknown") for r in reqs]
    logger.info(f"批量模拟: count={len(reqs)} concurrency={concurrency} alpha_ids={alpha_ids}")
    try:
        results = await session.concurrent_simulate(
            [r.alpha for r in reqs],
            concurrency=concurrency,
        )
        logger.info(f"批量模拟完成: count={len(results)}")
        return [r.json() if hasattr(r, "json") else r for r in results]
    except Exception as e:
        logger.error(f"批量模拟异常: error={e}")
        raise HTTPException(status_code=500, detail=str(e))
