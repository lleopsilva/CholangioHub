from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title="CholangioHub API",
    version="0.1.0",
)

app.include_router(health_router)


@app.get("/")
def root():
    return {
        "project": "CholangioHub",
        "version": app.version,
        "database": settings.postgres_db,
    }