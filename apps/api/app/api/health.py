from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

# Import ordering can vary across environments; silence ruff import-sorting
# warning for this small router file.
from app.dependencies.database import database_session  # noqa: I001

router = APIRouter()


@router.get("/health/db")
def health_database(
    session: Session = Depends(database_session),  # noqa: B008
):
    result = session.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": result.scalar(),
    }
