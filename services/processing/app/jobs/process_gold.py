"""Silver -> Gold processing job for article metrics.

Reads the cleaned Parquet dataset from `silver/articles/`, computes
consumable aggregations (example: counts per journal and year) and
writes results to `gold/article_metrics/` in Parquet format. Registers
the run in the metadata schema analogous to the Silver job.
"""

import logging
from datetime import UTC, datetime

from pyspark.sql import SparkSession
from sqlalchemy.orm import Session

from shared.database.engine import engine
from shared.logging import get_logger, log_with_fields
from shared.models import finish_run, get_or_create_dataset, get_or_create_source, log_audit_event, start_run
from shared.schemas import IngestionRunResult

from .process_silver import build_spark_session

logger = get_logger(__name__)


def run_gold_job(
    spark: SparkSession | None = None,
    *,
    prefix: str = "pubmed",
    input_path: str = "s3a://silver/articles/",
    output_path: str = "s3a://gold/article_metrics/",
) -> IngestionRunResult:
    owns_session = spark is None
    spark = spark or build_spark_session(app_name="cholangiohub-gold")

    log_with_fields(logger, logging.INFO, "gold processing started", prefix=prefix)

    try:
        # Read the silver table written by the silver job (or provided path)
        df = spark.read.parquet(input_path)

        # Example aggregation: counts per journal and publication year
        metrics = (
            df.groupBy(df.journal, df.pub_year)
            .count()
            .withColumnRenamed("count", "article_count")
        )

        records_out = metrics.count()

        # write partitioned by year for easy consumption
        metrics.write.mode("overwrite").parquet(output_path)

        quality_summary = {
            "records_in_silver": df.count(),
            "records_out_gold": records_out,
        }

        with Session(bind=engine) as session:
            source = get_or_create_source(
                session,
                name="PubMed",
                source_type="scientific_database",
                description="PubMed articles",
                url="https://pubmed.ncbi.nlm.nih.gov",
            )
            dataset = get_or_create_dataset(session, source=source, dataset_name="pubmed", layer="gold")
            db_run = start_run(session, dataset=dataset)
            db_run = finish_run(session, run=db_run, status="completed", records_processed=records_out)
            log_audit_event(
                session,
                event_type="data_quality",
                message=f"Gold run {db_run.id} summary: {quality_summary}",
            )
            session.commit()
            run_id = str(db_run.id)

        log_with_fields(
            logger,
            logging.INFO,
            "gold processing finished",
            run_id=run_id,
            **quality_summary,
        )

        return IngestionRunResult(
            run_id=run_id,
            status="completed",
            records_in=quality_summary.get("records_in_silver"),
            records_out=records_out,
            details=str(quality_summary),
        )
    finally:
        if owns_session:
            spark.stop()


if __name__ == "__main__":
    print(run_gold_job())
