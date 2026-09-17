from collections.abc import Generator

from sqlalchemy.orm import Session

from shared.database import get_session


def database_session() -> Generator[Session, None, None]:
    yield from get_session()