"""Alpha 公式生成器 — API 路由"""

from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import require_session
from ..log_config import get_logger
from ..services.alpha_generator import (
    generate_stage1,
    generate_stage2,
    generate_stage3,
    Stage1Request,
    Stage2Request,
    Stage3Request,
    Stage1Response,
    Stage2Response,
    Stage3Response,
)

logger = get_logger("generator")
router = APIRouter(prefix="/api/generator", tags=["generator"])


@router.post("/stage1", response_model=Stage1Response)
def post_stage1(req: Stage1Request, session=Depends(require_session)):
    logger.info(f"Stage 1: dataset_ids={req.dataset_ids} count={req.count}")
    try:
        return generate_stage1(req)
    except Exception as e:
        logger.error(f"Stage 1 失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stage2", response_model=Stage2Response)
def post_stage2(req: Stage2Request, session=Depends(require_session)):
    logger.info(f"Stage 2: count={req.count} inputs={len(req.input_expressions)}")
    try:
        return generate_stage2(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Stage 2 失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stage3", response_model=Stage3Response)
def post_stage3(req: Stage3Request, session=Depends(require_session)):
    logger.info(f"Stage 3: count={req.count} inputs={len(req.input_expressions)}")
    try:
        return generate_stage3(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Stage 3 失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))
