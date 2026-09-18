from shared.config.settings import Settings


def test_blank_env_values_fall_back_to_safe_defaults(monkeypatch):
    for key in [
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_PORT",
        "MINIO_ROOT_USER",
        "MINIO_ROOT_PASSWORD",
        "MINIO_PORT",
        "MINIO_CONSOLE_PORT",
    ]:
        monkeypatch.setenv(key, "")

    settings = Settings()

    assert settings.postgres_db == "postgres"
    assert settings.postgres_user == "postgres"
    assert settings.postgres_password == "postgres"
    assert settings.postgres_port == 5432

    assert settings.minio_root_user == "minioadmin"
    assert settings.minio_root_password == "minioadmin"
    assert settings.minio_port == 9000
    assert settings.minio_console_port == 9001
