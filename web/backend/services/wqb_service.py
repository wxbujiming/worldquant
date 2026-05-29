from wqb import WQBSession
from ..log_config import get_logger

logger = get_logger("wqb_service")

_session: WQBSession | None = None


def get_session() -> WQBSession | None:
    return _session


def create_session(email: str, password: str) -> WQBSession:
    global _session
    logger.info(f"创建 WQB 会话: email={email}")
    _session = WQBSession((email, password), logger=logger)
    _session.post_authentication()
    logger.info("WQB 会话创建成功")
    return _session


def destroy_session():
    global _session
    if _session is not None:
        try:
            _session.delete_authentication()
            logger.info("WQB 会话已销毁")
        except Exception:
            pass
    _session = None
