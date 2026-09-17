"""Bronze -> Silver processing job for PubMed articles.

Reads the raw JSON payloads landed by services/ingestion in the MinIO
`bronze` bucket, parses and deduplicates them, and writes a clean Parquet
dataset to the `silver` bucket. Run locally with Spark in `local[*]` mode
(no dependency on a separate Spark cluster) so it can be triggered by a
single HTTP call from Airflow, the same way services/ingestion works.
"""

import logging
from datetime import UTC, datetime

from pyspark.sql import Row, SparkSession
from pyspark.sql.types import ArrayType, IntegerType, StringType, StructField, StructType
from sqlalchemy.orm import Session

from shared.database.engine import engine
from shared.logging import get_logger, log_with_fields
from shared.models import finish_run, get_or_create_dataset, get_or_create_source, log_audit_event, start_run
from shared.schemas import IngestionRunResult

from .parsing import parse_bronze_pubmed_payload

logger = get_logger(__name__)

ARTICLE_SCHEMA = StructType(
    [
        StructField("source", StringType(), nullable=False),
        StructField("source_id", StringType(), nullable=False),
        StructField("title", StringType(), nullable=False),
        StructField("journal", StringType(), nullable=True),
        StructField("pub_year", IntegerType(), nullable=True),
        StructField("authors", ArrayType(StringType()), nullable=True),
        StructField("ingested_at", StringType(), nullable=False),
    ]
)


def build_spark_session(app_name: str = "cholangiohub-silver") -> SparkSession:
    """Build a local Spark session wired up to talk to the MinIO S3A endpoint.

    Uses local[*] rather than the standalone cluster (spark-master/worker)
    so this job stays a simple, independently-triggerable HTTP service,
    consistent with how services/ingestion is triggered. Submitting to the
    standalone cluster is a reasonable follow-up once there are heavier
    workloads that actually benefit from distributing across the worker.
    """
    from shared.config.settings import settings

    minio_endpoint = f"http://{getattr(settings, 'minio_host', 'minio')}:9000"

    spark = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262",
        )
        .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", settings.minio_root_user)
        .config("spark.hadoop.fs.s3a.secret.key", settings.minio_root_password)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.connection.timeout", "60000")
        .config("spark.hadoop.fs.s3a.socket.timeout", "60000")
        .getOrCreate()
    )

    hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()
    for key, value in {
        "fs.s3a.endpoint": minio_endpoint,
        "fs.s3a.access.key": settings.minio_root_user,
        "fs.s3a.secret.key": settings.minio_root_password,
        "fs.s3a.path.style.access": "true",
        "fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        "fs.s3a.connection.ssl.enabled": "false",
        "fs.s3a.connection.timeout": "60000",
        "fs.s3a.socket.timeout": "60000",
    }.items():
        hadoop_conf.set(key, value)

    logger.info("s3a config applied: %s", {key: hadoop_conf.get(key) for key in ["fs.s3a.endpoint", "fs.s3a.connection.timeout", "fs.s3a.socket.timeout", "fs.s3a.path.style.access"]})

    return spark


def run_silver_job(spark: SparkSession | None = None, *, prefix: str = "pubmed") -> IngestionRunResult:
    owns_session = spark is None
    spark = spark or build_spark_session()

    log_with_fields(logger, logging.INFO, "silver processing started", prefix=prefix)

    try:
        # One JSON object per bronze file; wholeTextFiles gives us (path, content)
        # pairs so each file is parsed independently and in parallel.
        raw = spark.sparkContext.wholeTextFiles(f"s3a://bronze/{prefix}/*/*/*/*.json")
        records_in = raw.count()

        import json

        def parse_file(pair):
            _, content = pair
            try:
                payload = json.loads(content)
            except json.JSONDecodeError:
                return []
            return parse_bronze_pubmed_payload(payload)

        parsed = raw.flatMap(parse_file)
        rows = parsed.map(
            lambda r: Row(
                source=r["source"],
                source_id=r["source_id"],
                title=r["title"],
                journal=r.get("journal"),
                pub_year=r.get("pub_year"),
                authors=r.get("authors") or [],
                ingested_at=r["ingested_at"],
            )
        )

        df = spark.createDataFrame(rows, schema=ARTICLE_SCHEMA)
        records_parsed = df.count()

        # Uniqueness: keep the most recently ingested row per (source, source_id)
        deduped = (
            df.orderBy(df.ingested_at.desc())
            .dropDuplicates(["source", "source_id"])
        )
        records_out = deduped.count()
        duplicates_removed = records_parsed - records_out

        deduped.write.mode("overwrite").parquet("s3a://silver/articles/")

        quality_summary = {
            "records_in_bronze_files": records_in,
            "records_parsed": records_parsed,
            "records_after_dedup": records_out,
            "duplicates_removed": duplicates_removed,
        }

        with Session(bind=engine) as session:
            source = get_or_create_source(
                session,
                name="PubMed",
                source_type="scientific_database",
                description="PubMed articles",
                url="https://pubmed.ncbi.nlm.nih.gov",
            )
            dataset = get_or_create_dataset(session, source=source, dataset_name="pubmed", layer="silver")
            db_run = start_run(session, dataset=dataset)
            db_run = finish_run(session, run=db_run, status="completed", records_processed=records_out)
            log_audit_event(
                session,
                event_type="data_quality",
                message=f"Silver run {db_run.id} quality summary: {quality_summary}",
            )
            session.commit()
            run_id = str(db_run.id)

        log_with_fields(
            logger,
            logging.INFO,
            "silver processing finished",
            run_id=run_id,
            **quality_summary,
        )

        return IngestionRunResult(
            run_id=run_id,
            status="completed",
            records_in=records_parsed,
            records_out=records_out,
            details=str(quality_summary),
        )
    finally:
        if owns_session:
            spark.stop()


if __name__ == "__main__":
    print(run_silver_job())
