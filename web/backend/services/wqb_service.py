import logging
from wqb import WQBSession, wqb_logger

logger = wqb_logger(name="wqb_web")

_session: WQBSession | None = None


def get_session() -> WQBSession | None:
    return _session


def create_session(email: str, password: str) -> WQBSession:
    global _session
    _session = WQBSession((email, password), logger=logger)
    _session.post_authentication()
    return _session


def destroy_session():
    global _session
    if _session is not None:
        try:
            _session.delete_authentication()
        except Exception:
            pass
    _session = None
