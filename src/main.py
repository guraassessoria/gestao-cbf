from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src.core.config import get_settings
from src.core.db import Base, engine, SessionLocal
from src.routers import auth, competencias, dashboard, estruturas, health, processamentos, usuarios
from src.services.bootstrap import ensure_seed_data

settings = get_settings()

STATIC_DIR = Path(__file__).resolve().parent.parent / "public"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_seed_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API do MVP de processamento de balancetes mensais",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(usuarios.router, prefix="/api")
app.include_router(estruturas.router, prefix="/api")
app.include_router(competencias.router, prefix="/api")
app.include_router(processamentos.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


# Serve frontend SPA (static files built into public/)
if STATIC_DIR.is_dir():
    _static_root = STATIC_DIR.resolve()

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        file = (STATIC_DIR / path).resolve()
        if file.is_file() and str(file).startswith(str(_static_root)):
            return FileResponse(str(file))
        index = STATIC_DIR / "index.html"
        if index.is_file():
            return FileResponse(str(index), media_type="text/html")
        return {"detail": "Not Found"}
