from fastapi import APIRouter, Depends
from ..dependencies import require_session
from ..log_config import get_logger

logger = get_logger("operators")
router = APIRouter(prefix="/api/operators", tags=["operators"])


@router.get("")
def search_operators(session=Depends(require_session)):
    logger.info("搜索算子")
    resp = session.search_operators()
    data = resp.json()
    items = data if isinstance(data, list) else data.get("results", data.get("operators", []))
    logger.info(f"算子搜索完成: 返回 {len(items)} 条")
    return data
