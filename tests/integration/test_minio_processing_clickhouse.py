import json
import os
import time

import pytest

try:
    from testcontainers.core.generic import DockerContainer
    from testcontainers.postgres import PostgresContainer
except Exception:  # pragma: no cover - skip when testcontainers not installed
    PostgresContainer = None
    DockerContainer = None

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    PostgresContainer is None or DockerContainer is None,
    reason="testcontainers not installed",
)
def test_minio_processing_clickhouse_pipeline(tmp_path):
    # Start Postgres
    with PostgresContainer("postgres:15") as pg, \
        DockerContainer("minio/minio:latest") as minio, \
        DockerContainer("clickhouse/clickhouse-server:latest") as ch:
        pg.start()

        # Start MinIO with required env and command
        minio.with_exposed_ports(9000, 9001)
        minio.with_env("MINIO_ROOT_USER", "minioadmin")
        minio.with_env("MINIO_ROOT_PASSWORD", "minioadmin")
        minio.with_command("server /data --console-address :9001")
        minio.start()

        # Start ClickHouse
        ch.with_exposed_ports(8123)
        ch.start()

        # Compose endpoints/credentials
        minio_host = minio.get_container_host_ip()
        minio_port = minio.get_exposed_port(9000)
        minio_endpoint = f"http://{minio_host}:{minio_port}"

        ch_host = ch.get_container_host_ip()
        ch_port = ch.get_exposed_port(8123)
        clickhouse_url = f"http://{ch_host}:{ch_port}"

        # Apply Postgres migrations
        db_url = pg.get_connection_url()
        from sqlalchemy import create_engine, text

        engine = create_engine(db_url)
        base_dir = os.path.dirname(__file__)
        migrations_dir = os.path.abspath(
            os.path.join(base_dir, "..", "..", "database", "migrations")
        )
        with engine.connect() as conn:
            for fname in [
                "001_create_metadata_schema.sql",
                "002_create_ingestion_control.sql",
                "003_create_audit_layer.sql",
            ]:
                path = os.path.join(migrations_dir, fname)
                with open(path, encoding="utf-8") as fh:
                    sql = fh.read()
                conn.execute(text(sql))
                conn.commit()

        # Set env vars for services to pick up
        from sqlalchemy.engine import make_url

        parsed = make_url(db_url)
        os.environ.setdefault("POSTGRES_HOST", parsed.host)
        os.environ.setdefault("POSTGRES_PORT", str(parsed.port))
        os.environ.setdefault("POSTGRES_DB", parsed.database)
        os.environ.setdefault("POSTGRES_USER", parsed.username)
        os.environ.setdefault("POSTGRES_PASSWORD", parsed.password)

        os.environ.setdefault("MINIO_ROOT_USER", "minioadmin")
        os.environ.setdefault("MINIO_ROOT_PASSWORD", "minioadmin")
        os.environ.setdefault("MINIO_HOST", minio_host)
        os.environ.setdefault("MINIO_PORT", str(minio_port))

        os.environ.setdefault("CLICKHOUSE_HTTP_URL", clickhouse_url)
        os.environ.setdefault("CLICKHOUSE_DB", "cholangiohub")

        # Wait a little for services to become available
        time.sleep(5)

        # Upload a bronze JSON file to MinIO
        import boto3
        from botocore.client import Config

        s3 = boto3.resource(
            "s3",
            endpoint_url=minio_endpoint,
            aws_access_key_id=os.environ["MINIO_ROOT_USER"],
            aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

        bucket_name = "bronze"
        try:
            s3.create_bucket(Bucket=bucket_name)
        except Exception:
            pass

        # create sample bronze json
        sample = {
            "source": "pubmed",
            "source_id": "1",
            "title": "T1",
            "journal": "J1",
            "pub_year": 2020,
            "authors": ["A"],
            "ingested_at": "2026-09-17T00:00:00",
        }
        key = "pubmed/0000/0001/article1.json"
        s3.Object(bucket_name, key).put(Body=json.dumps(sample).encode("utf-8"))

        # Import processing app after env configured
        from fastapi.testclient import TestClient

        from services.processing.app import web as processing_web

        client = TestClient(processing_web.app)

        # Run silver job (reads from s3a://bronze/pubmed/... using MinIO)
        resp = client.post("/process/silver")
        assert resp.status_code == 200

        # Run gold job
        resp = client.post("/process/gold")
        assert resp.status_code == 200

        # Prepare ClickHouse DB/table
        import requests

        ddl = (
            "CREATE DATABASE IF NOT EXISTS cholangiohub; "
            "CREATE TABLE IF NOT EXISTS cholangiohub.article_metrics "
            "(journal String, pub_year Int32, article_count Int32) "
            "ENGINE = MergeTree() ORDER BY (journal, pub_year)"
        )
        r = requests.post(f"{clickhouse_url}/?query={ddl}")
        r.raise_for_status()

        # Ingest into ClickHouse
        resp = client.post("/gold/ingest_clickhouse")
        assert resp.status_code == 200

        # Query ClickHouse count
        query = "SELECT%20count()%20FROM%20cholangiohub.article_metrics"
        r = requests.post(f"{clickhouse_url}/?query={query}")
        r.raise_for_status()
        assert r.text.strip() != "0"
