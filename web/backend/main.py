from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import auth, datasets, fields, operators, alphas, simulations


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


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
