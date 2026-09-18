from typing import Any

from fastapi import FastAPI

from app.api.gold import router as gold_router
from app.api.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title="CholangioHub API",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(gold_router, prefix="/gold")


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "project": "CholangioHub",
        "version": app.version,
        "database": settings.postgres_db,
    }
