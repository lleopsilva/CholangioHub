from sqlalchemy.orm import Session, sessionmaker

from shared.database.engine import engine


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=Session,
)


def get_session():
    with SessionLocal() as session:
        yield session