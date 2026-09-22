from __future__ import annotations

import os

import requests
from pyspark.sql import DataFrame

from .process_silver import build_spark_session


def ingest_article_metrics_to_clickhouse(
    input_path: str = "s3a://gold/article_metrics/",
    clickhouse_url: str | None = None,
    clickhouse_db: str | None = None,
    clickhouse_table: str = "article_metrics",
    clickhouse_user: str | None = None,
    clickhouse_password: str | None = None,
) -> int:
    """Read gold article metrics Parquet, aggregate, and insert into ClickHouse via HTTP.

    Returns number of rows inserted.
    """
    clickhouse_url = clickhouse_url or os.getenv("CLICKHOUSE_HTTP_URL")
    clickhouse_db = clickhouse_db or os.getenv("CLICKHOUSE_DB")
    clickhouse_user = clickhouse_user or os.getenv("CLICKHOUSE_USER")
    clickhouse_password = clickhouse_password or os.getenv("CLICKHOUSE_PASSWORD")

    if not clickhouse_url or not clickhouse_db:
        raise RuntimeError("CLICKHOUSE_HTTP_URL and CLICKHOUSE_DB must be set to ingest metrics")

    spark = build_spark_session(app_name="cholangiohub-clickhouse-ingest")
    try:
        df: DataFrame = spark.read.parquet(input_path)

        agg = df.groupBy(df.journal, df.pub_year).count()
        agg = agg.withColumnRenamed("count", "article_count")

        rows = agg.collect()

        if not rows:
            return 0

        payload_lines: list[str] = []
        for r in rows:
            journal = r["journal"] if r["journal"] is not None else ""
            pub_year = r["pub_year"] if r["pub_year"] is not None else 0
            article_count = int(r["article_count"]) if r["article_count"] is not None else 0
            payload_lines.append(f"{journal}\t{pub_year}\t{article_count}")

        payload = "\n".join(payload_lines)

        insert_query = (
            "INSERT%20INTO%20"
            f"{clickhouse_db}.{clickhouse_table}%20(journal,pub_year,article_count)%20"
            "FORMAT%20TabSeparated"
        )
        insert_url = f"{clickhouse_url}/?query={insert_query}"

        auth = (clickhouse_user, clickhouse_password) if clickhouse_user else None
        resp = requests.post(insert_url, data=payload.encode("utf-8"), auth=auth, timeout=60)
        resp.raise_for_status()

        return len(rows)
    finally:
        spark.stop()