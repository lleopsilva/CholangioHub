import os
import uuid

import pytest
from sqlalchemy import create_engine, text

try:
    from testcontainers.postgres import PostgresContainer
except Exception:  # pragma: no cover - skip when testcontainers not installed
    PostgresContainer = None


pytestmark = pytest.mark.integration


@pytest.mark.skipif(PostgresContainer is None, reason="testcontainers not installed")
def test_apps_api_reads_ingestion_runs_from_postgres():
    """Start a Postgres container, apply metadata migrations, insert a run, and
    verify the `apps/api` `/gold/runs` endpoint returns it.
    """
    with PostgresContainer("postgres:15") as pg:
        pg.start()
        db_url = pg.get_connection_url()  # e.g. postgresql://user:pass@host:port/db

        engine = create_engine(db_url)
        # apply SQL migrations
        base_dir = os.path.dirname(__file__)
        migrations_dir = os.path.abspath(
            os.path.join(base_dir, "..", "..", "database", "migrations")
        )

        # Execute migrations in order
        sql_files = [
            "001_create_metadata_schema.sql",
            "002_create_ingestion_control.sql",
            "003_create_audit_layer.sql",
        ]

        with engine.connect() as conn:
            for fname in sql_files:
                path = os.path.join(migrations_dir, fname)
                with open(path, encoding="utf-8") as fh:
                    sql = fh.read()
                conn.execute(text(sql))
                conn.commit()

            # insert source, dataset, ingestion_run
            source_id = str(uuid.uuid4())
            dataset_id = str(uuid.uuid4())
            run_id = str(uuid.uuid4())

            conn.execute(
                text(
                    "INSERT INTO metadata.sources (id, name, source_type) "
                    "VALUES (:id, :name, :stype)"
                ),
                {"id": source_id, "name": "pubmed", "stype": "api"},
            )
            conn.execute(
                text(
                    "INSERT INTO metadata.datasets (id, source_id, dataset_name, layer) "
                    "VALUES (:id, :source_id, :name, :layer)"
                ),
                {
                    "id": dataset_id,
                    "source_id": source_id,
                    "name": "pubmed_articles",
                    "layer": "gold",
                },
            )
            conn.execute(
                text(
                    "INSERT INTO metadata.ingestion_runs (id, dataset_id, status, "
                    "records_processed) VALUES (:id, :dataset_id, :status, :records)"
                ),
                {"id": run_id, "dataset_id": dataset_id, "status": "completed", "records": 123},
            )
            conn.commit()

        # Set env vars expected by shared.settings before importing the API app
        db_url = pg.get_connection_url()  # postgresql://user:pass@host:port/dbname
        from sqlalchemy.engine import make_url

        parsed = make_url(db_url)
        os.environ.setdefault("POSTGRES_HOST", parsed.host)
        os.environ.setdefault("POSTGRES_PORT", str(parsed.port))
        os.environ.setdefault("POSTGRES_DB", parsed.database)
        os.environ.setdefault("POSTGRES_USER", parsed.username)
        os.environ.setdefault("POSTGRES_PASSWORD", parsed.password)

        # Import app after env is configured
        # Provide remaining env defaults required by apps/api Settings
        os.environ.setdefault("MINIO_ROOT_USER", "minioadmin")
        os.environ.setdefault("MINIO_ROOT_PASSWORD", "minioadmin")
        os.environ.setdefault("MINIO_PORT", "9000")
        os.environ.setdefault("MINIO_CONSOLE_PORT", "9001")
        os.environ.setdefault("CLICKHOUSE_DB", "cholangiohub")
        os.environ.setdefault("CLICKHOUSE_USER", "admin")
        os.environ.setdefault("CLICKHOUSE_PASSWORD", "admin")
        os.environ.setdefault("CLICKHOUSE_HTTP_PORT", "8123")
        os.environ.setdefault("CLICKHOUSE_NATIVE_PORT", "9000")

        from fastapi.testclient import TestClient

        from apps.api.app import main as api_main

        client = TestClient(api_main.app)

        resp = client.get("/gold/runs")
        assert resp.status_code == 200
        data = resp.json()
        # Find our run
        ids = [r.get("run_id") for r in data]
        assert run_id in ids
