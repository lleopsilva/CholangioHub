import os

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    postgres_db: str = Field(default="postgres")
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    postgres_host: str = Field(default="localhost")

    minio_root_user: str = Field(default="minioadmin")
    minio_root_password: str = Field(default="minioadmin")
    minio_host: str = Field(default="minio")
    minio_port: int = Field(default=9000)
    minio_console_port: int = Field(default=9001)

    clickhouse_db: str = Field(default="cholangiohub")
    clickhouse_user: str = Field(default="admin")
    clickhouse_password: str = Field(default="admin")
    clickhouse_http_port: int = Field(default=8123)
    clickhouse_native_port: int = Field(default=9000)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("postgres_port", "minio_port", "minio_console_port", "clickhouse_http_port", "clickhouse_native_port", mode="before")
    @classmethod
    def parse_optional_int(cls, value, info: ValidationInfo):
        if value is None:
            return cls.model_fields[info.field_name].default
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return cls.model_fields[info.field_name].default
        return int(value)

    @field_validator(
        "postgres_db",
        "postgres_user",
        "postgres_password",
        "postgres_host",
        "minio_root_user",
        "minio_root_password",
        "minio_host",
        "clickhouse_db",
        "clickhouse_user",
        "clickhouse_password",
        mode="before",
    )
    @classmethod
    def parse_optional_str(cls, value, info: ValidationInfo):
        if value is None:
            return cls.model_fields[info.field_name].default
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return cls.model_fields[info.field_name].default
        return value


settings = Settings()