from fastapi import APIRouter, Depends
from ..dependencies import require_session

router = APIRouter(prefix="/api/operators", tags=["operators"])


@router.get("")
def search_operators(session=Depends(require_session)):
    resp = session.search_operators()
    return resp.json()
