from shared.config.settings import settings


def main() -> None:
    print("=" * 50)
    print("CholangioHub - Ingestion Service")
    print("=" * 50)

    print()
    print("Configuration loaded successfully")
    print()

    print(f"PostgreSQL Database : {settings.postgres_db}")
    print(f"PostgreSQL Port     : {settings.postgres_port}")

    print(f"ClickHouse Database : {settings.clickhouse_db}")
    print(f"ClickHouse HTTP     : {settings.clickhouse_http_port}")

    print(f"MinIO Port          : {settings.minio_port}")

    print()
    print("Service ready.")


if __name__ == "__main__":
    main()