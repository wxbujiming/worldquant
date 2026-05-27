from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import settings
from .services.wqb_service import create_session, get_session, destroy_session
from .routers import auth, datasets, fields, operators, alphas, simulations


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.wqb_email and settings.wqb_password:
        try:
            create_session(settings.wqb_email, settings.wqb_password)
            print(f"已自动登录: {settings.wqb_email}")
        except Exception as e:
            print(f"自动登录失败（可在页面上手动登录）: {e}")
    yield
    destroy_session()


app = FastAPI(title="WorldQuant Brain Web", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(fields.router)
app.include_router(operators.router)
app.include_router(alphas.router)
app.include_router(simulations.router)

STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")
