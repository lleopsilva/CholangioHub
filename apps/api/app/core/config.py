from functools import lru_cache
from pathlib import Path

# Silence import-sorting warnings here; the file's imports are intentionally
# grouped for readability rather than strict alphabetical order.
from pydantic_settings import BaseSettings, SettingsConfigDict  # noqa: I001

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # PostgreSQL
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int

    # MinIO
    minio_root_user: str
    minio_root_password: str
    minio_port: int
    minio_console_port: int

    # ClickHouse
    clickhouse_db: str
    clickhouse_user: str
    clickhouse_password: str
    clickhouse_http_port: int
    clickhouse_native_port: int


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
