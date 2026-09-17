import os
import time
from pathlib import Path

os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "1")

from minio import Minio
from sqlalchemy import create_engine, text

from testcontainers.postgres import PostgresContainer
from testcontainers.core.container import DockerContainer

from services.ingestion.app.collectors import pubmed

MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "database" / "migrations"


def apply_real_migrations(engine):
    """Build the schema from the actual versioned migrations, not a hand-rolled
    copy, so this test stays honest about what production looks like."""
    with engine.begin() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS metadata"))
        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            conn.exec_driver_sql(sql_file.read_text(encoding="utf-8"))


def test_pubmed_integration(monkeypatch):
    # Start Postgres container
    with PostgresContainer("postgres:15-alpine") as pg:
        pg_url = pg.get_connection_url().replace("postgresql://", "postgresql+psycopg://")
        engine = create_engine(pg_url)

        apply_real_migrations(engine)

        # Start MinIO container
        with DockerContainer("minio/minio:latest") as mc:
            mc.with_exposed_ports(9000)
            mc.with_env("MINIO_ROOT_USER", "minioadmin")
            mc.with_env("MINIO_ROOT_PASSWORD", "minioadmin")
            mc.with_command("server /data")
            mc.start()
            host = mc.get_container_host_ip()
            port = mc.get_exposed_port(9000)
            endpoint = f"{host}:{port}"

            # Wait briefly for MinIO to be ready
            time.sleep(2)

            client = Minio(endpoint, access_key="minioadmin", secret_key="minioadmin", secure=False)
            if not client.bucket_exists("bronze"):
                client.make_bucket("bronze")

            # Point the collector at the containers we just started
            monkeypatch.setattr(pubmed, "get_minio_client", lambda: client)
            monkeypatch.setattr(pubmed, "ensure_bucket", lambda c, b: None)
            monkeypatch.setattr(pubmed, "engine", engine)

            # Mock the network calls to PubMed itself
            monkeypatch.setattr(pubmed, "search_pubmed", lambda term, retmax=2: ["1", "2"])
            monkeypatch.setattr(pubmed, "fetch_summaries", lambda ids: {"uids": ids})

            # Act
            result = pubmed.run(term="cholangiocarcinoma", limit=2)

            # Assert: object landed in MinIO
            obj = client.get_object("bronze", result.object_key)
            data = obj.read()
            assert b"summaries" in data

            # Assert: run + source + dataset rows exist via the real schema
            with engine.connect() as conn:
                count = conn.execute(text("SELECT COUNT(*) FROM metadata.ingestion_runs")).scalar_one()
                assert count >= 1

                source_name = conn.execute(
                    text("SELECT name FROM metadata.sources WHERE name = 'PubMed'")
                ).scalar_one_or_none()
                assert source_name == "PubMed"

            assert result.status == "completed"
            assert result.records_in == 2
