from fastapi import Depends, HTTPException, status
from .services.wqb_service import get_session


def require_session(session=Depends(get_session)):
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login first.",
        )
    return session
