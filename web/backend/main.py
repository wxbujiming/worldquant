from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import settings
from .services.wqb_service import create_session, get_session, destroy_session
from .services.cache_service import init_db, sync_operators, sync_datasets, sync_fields, get_synced_at
from .routers import auth, datasets, fields, operators, alphas, simulations, cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if settings.wqb_email and settings.wqb_password:
        try:
            create_session(settings.wqb_email, settings.wqb_password)
            session = get_session()
            print(f"已自动登录: {settings.wqb_email}")

            # 启动后后台同步静态数据
            ops_synced = get_synced_at("operators")
            if not ops_synced:
                try:
                    c = sync_operators(session)
                    print(f"已缓存 {c} 个算子")
                except Exception as e:
                    print(f"算子缓存失败: {e}")

            ds_synced = get_synced_at("datasets_usa_1_top3000")
            if not ds_synced:
                try:
                    c = sync_datasets(session, "usa", 1, "top3000")
                    print(f"已缓存 {c} 个数据集")
                except Exception as e:
                    print(f"数据集缓存失败: {e}")
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
app.include_router(cache.router)

STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")
