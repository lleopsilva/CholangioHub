from __future__ import annotations

from typing import Optional
import os
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql import Row
import requests


def build_streaming_spark(app_name: str = "cholangiohub-streaming") -> SparkSession:
    builder = (
        SparkSession.builder.master("local[*]")
        .appName(app_name)
        .config("spark.sql.shuffle.partitions", "1")
    )

    # Allow passing extra Spark config via env var `SPARK_EXTRA_CONF` as key=val;comma-separated
    extra = os.getenv("SPARK_EXTRA_CONF")
    if extra:
        for pair in extra.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                builder = builder.config(k.strip(), v.strip())

    return builder.getOrCreate()


def run_streaming_job(
    input_path: str = "s3a://bronze/pubmed/",
    output_path: Optional[str] = None,
    checkpoint_location: str | None = None,
    app_name: str = "cholangiohub-streaming",
    await_termination: bool = True,
    timeout_ms: int | None = None,
    enable_clickhouse: bool = False,
    clickhouse_url: str | None = None,
    clickhouse_db: str | None = None,
    clickhouse_table: str = "article_metrics",
) -> None:
    """A minimal Structured Streaming prototype.

    - Reads appended Parquet files from `input_path` (assumes Bronze writes Parquet)
    - Aggregates counts by `journal` and `pub_year`
    - Writes results to console and optionally to `output_path` in Parquet (complete mode)

    This function is intended as a local prototype. For production, run on a Spark cluster
    and tune checkpointing and output modes appropriately.
    """
    spark = build_streaming_spark(app_name=app_name)

    try:
        df: DataFrame = spark.readStream.format("parquet").load(input_path)


        # Basic aggregation
        agg = df.groupBy("journal", "pub_year").count().withColumnRenamed("count", "article_count")

        # helper to push batch DataFrame to ClickHouse via HTTP (TabSeparated)
        def _batch_to_clickhouse(batch_df: DataFrame, batch_id: int) -> None:
            if not clickhouse_url or not clickhouse_db:
                raise RuntimeError("ClickHouse URL/DB not configured for ingestion")

            rows = batch_df.collect()
            if not rows:
                return

            lines: list[str] = []
            for r in rows:
                journal = r["journal"] if r["journal"] is not None else ""
                pub_year = r["pub_year"] if r["pub_year"] is not None else 0
                article_count = int(r["article_count"]) if r["article_count"] is not None else 0
                # Escape tabs/newlines in journal
                safe_journal = str(journal).replace("\t", " ").replace("\n", " ")
                lines.append(f"{safe_journal}\t{pub_year}\t{article_count}")

            payload = "\n".join(lines)
            insert_url = f"{clickhouse_url}/?query=INSERT%20INTO%20{clickhouse_db}.{clickhouse_table}%20(journal,pub_year,article_count)%20FORMAT%20TabSeparated"
            resp = requests.post(insert_url, data=payload.encode("utf-8"), timeout=60)
            resp.raise_for_status()

        # Always write to console for quick visibility
        write_stream = agg.writeStream.outputMode("complete").format("console").option("truncate", False)

        if enable_clickhouse:
            # Use foreachBatch to push each micro-batch to ClickHouse
            write_stream = write_stream.foreachBatch(_batch_to_clickhouse)

        console_q = write_stream.start()

        if output_path:
            if not checkpoint_location:
                raise RuntimeError("checkpoint_location is required when writing to output_path")

            file_q = (
                agg.writeStream
                .outputMode("complete")
                .format("parquet")
                .option("path", output_path)
                .option("checkpointLocation", checkpoint_location)
                .start()
            )
        else:
            file_q = None

        if await_termination:
            if timeout_ms:
                console_q.awaitTermination(timeout_ms)
                if file_q:
                    file_q.stop()
            else:
                console_q.awaitTermination()
        else:
            # return immediately with queries running in background
            return
    finally:
        # Do not stop spark here when running streaming in long-lived mode
        if not await_termination:
            return
        spark.stop()
