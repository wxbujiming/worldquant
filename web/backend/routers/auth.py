from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..config import settings
from ..dependencies import require_session
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


@router.get("/profile")
def user_profile(session=Depends(require_session)):
    logger.info("查询用户信息")
    # 基本信息
    user_resp = session.get("https://api.worldquantbrain.com/users/self")
    user_data = user_resp.json()
    # 竞赛/分数信息
    comp_resp = session.get("https://api.worldquantbrain.com/competitions")
    comp_data = comp_resp.json()
    score = None
    level = None
    rank = None
    alphas = None
    if isinstance(comp_data, dict):
        results = comp_data.get("results") or []
        for c in results:
            lb = c.get("leaderboard")
            if lb and lb.get("score") is not None:
                score = lb.get("score")
                level = lb.get("level")
                rank = lb.get("rank")
                alphas = lb.get("alphas")
                break
    return {**user_data, "score": score, "level": level, "rank": rank, "submittedAlphas": alphas}


@router.get("/simulation-quota")
def simulation_quota(session=Depends(require_session)):
    """查询剩余模拟测试次数（通过一次轻量模拟并立即取消来获取）"""
    logger.info("查询模拟配额")
    alpha = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY", "region": "USA",
            "universe": "TOP3000", "delay": 1, "decay": 5,
            "neutralization": "SUBINDUSTRY", "truncation": 0.08,
            "pasteurization": "ON", "unitHandling": "VERIFY",
            "nanHandling": "ON", "language": "FASTEXPR",
            "visualization": False,
        },
        "regular": "rank(close)",
    }
    resp = session.post("https://api.worldquantbrain.com/simulations", json=alpha)
    remaining = resp.headers.get("X-Ratelimit-Remaining")
    limit = resp.headers.get("X-Ratelimit-Limit")
    # 立即取消模拟，不浪费配额
    location = resp.headers.get("Location")
    if location and resp.status_code == 201:
        try:
            session.delete(location)
        except Exception:
            pass
    return {
        "remaining": int(remaining) if remaining else None,
        "limit": int(limit) if limit else None,
    }
