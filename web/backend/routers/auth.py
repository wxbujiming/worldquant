from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..config import settings
from ..services.wqb_service import create_session, destroy_session, get_session

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(req: LoginRequest):
    if get_session() is not None:
        destroy_session()
    try:
        session = create_session(req.email, req.password)
        return {
            "message": "Login successful",
            "email": session.wqb_auth.username,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login/env")
def login_with_env():
    if not settings.wqb_email or not settings.wqb_password:
        raise HTTPException(status_code=400, detail="未配置环境变量账号")
    if get_session() is not None:
        destroy_session()
    try:
        session = create_session(settings.wqb_email, settings.wqb_password)
        return {
            "message": "Login successful",
            "email": session.wqb_auth.username,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.delete("/logout")
def logout():
    destroy_session()
    return {"message": "Logged out"}


@router.get("/status")
def status():
    session = get_session()
    if session is not None:
        return {
            "authenticated": True,
            "email": session.wqb_auth.username,
        }
    return {
        "authenticated": False,
        "has_credentials": bool(settings.wqb_email and settings.wqb_password),
    }
