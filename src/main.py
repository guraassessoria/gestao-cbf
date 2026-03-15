from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.db import Base, engine, SessionLocal
from src.routers import auth, competencias, dashboard, estruturas, health, processamentos, usuarios
from src.services.bootstrap import ensure_seed_data

settings = get_settings()


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

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(estruturas.router)
app.include_router(competencias.router)
app.include_router(processamentos.router)
app.include_router(dashboard.router)
