from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies.database import database_session


router = APIRouter()


@router.get("/health/db")
def health_database(
    session: Session = Depends(database_session),
):
    result = session.execute(
        text("SELECT 1")
    )

    return {
        "status": "healthy",
        "database": result.scalar(),
    }