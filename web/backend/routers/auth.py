from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..config import settings
from ..services.wqb_service import create_session, destroy_session, get_session
from ..log_config import get_logger

logger = get_logger("auth")
router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(req: LoginRequest):
    logger.info(f"用户登录: email={req.email}")
    if get_session() is not None:
        destroy_session()
    try:
        session = create_session(req.email, req.password)
        logger.info(f"登录成功: email={req.email}")
        return {
            "message": "Login successful",
            "email": session.wqb_auth.username,
        }
    except Exception as e:
        logger.warning(f"登录失败: email={req.email} error={e}")
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login/env")
def login_with_env():
    logger.info("环境变量登录")
    if not settings.wqb_email or not settings.wqb_password:
        raise HTTPException(status_code=400, detail="未配置环境变量账号")
    if get_session() is not None:
        destroy_session()
    try:
        session = create_session(settings.wqb_email, settings.wqb_password)
        logger.info(f"环境变量登录成功: email={settings.wqb_email}")
        return {
            "message": "Login successful",
            "email": session.wqb_auth.username,
        }
    except Exception as e:
        logger.warning(f"环境变量登录失败: error={e}")
        raise HTTPException(status_code=401, detail=str(e))


@router.delete("/logout")
def logout():
    logger.info("用户登出")
    destroy_session()
    return {"message": "Logged out"}


@router.get("/status")
def status():
    session = get_session()
    authenticated = session is not None
    logger.info(f"查询登录状态: authenticated={authenticated}")
    if authenticated:
        return {
            "authenticated": True,
            "email": session.wqb_auth.username,
        }
    return {
        "authenticated": False,
        "has_credentials": bool(settings.wqb_email and settings.wqb_password),
    }
