from typing import Callable, Awaitable

from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import PlainTextResponse

from shared.schemas import IngestionRunResult
from shared.utils.metrics import ServiceMetrics

from .jobs.process_gold import run_gold_job
from .jobs.process_silver import run_silver_job, build_spark_session

app = FastAPI(title="CholangioHub Processing Runner")
metrics = ServiceMetrics("cholangiohub_processing")


@app.middleware("http")
async def track_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    metrics.record_http_request()
    response = await call_next(request)
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def metrics_endpoint() -> PlainTextResponse:
    return PlainTextResponse(metrics.render(), media_type="text/plain; version=0.0.4")


@app.post("/process/silver", response_model=IngestionRunResult)
def process_silver() -> IngestionRunResult:
    return run_silver_job()


@app.post("/process/gold", response_model=IngestionRunResult)
def process_gold() -> IngestionRunResult:
    return run_gold_job()

@app.get("/gold/aggregations")
def gold_aggregations(
    journal: str | None = Query(None, description="Filter by journal name"),
    year: int | None = Query(None, description="Filter by publication year"),
    limit: int = Query(100, description="Max number of rows to return"),
    input_path: str = Query("s3a://gold/article_metrics/", description="Path to gold parquet"),
) -> list[dict[str, object]]:
    """Compute simple aggregations from the Gold Parquet dataset using Spark.

    Returns top counts per journal and year, optionally filtered by `journal` or `year`.
    """
    spark = build_spark_session(app_name="cholangiohub-gold-api")
    try:
        df = spark.read.parquet(input_path)

        if journal:
            df = df.filter(df.journal == journal)
        if year:
            df = df.filter(df.pub_year == year)

        metrics_df = df.groupBy(df.journal, df.pub_year).count().withColumnRenamed("count", "article_count")
        ordered = metrics_df.orderBy(metrics_df.article_count.desc()).limit(limit)

        rows = ordered.collect()
        result: list[dict[str, object]] = []
        for r in rows:
            result.append({"journal": r["journal"], "pub_year": r["pub_year"], "article_count": int(r["article_count"])})
        return result
    finally:
        spark.stop()



@app.post("/gold/ingest_clickhouse")
def ingest_clickhouse(input_path: str | None = None) -> dict[str, int]:
    """Trigger ingestion of Gold metrics into ClickHouse.

    Reads Parquet from `input_path` or the default gold path and inserts aggregated
    metrics into ClickHouse using `CLICKHOUSE_HTTP_URL` and `CLICKHOUSE_DB` env vars.
    """
    from .jobs.clickhouse import ingest_article_metrics_to_clickhouse

    path = input_path or "s3a://gold/article_metrics/"
    inserted = ingest_article_metrics_to_clickhouse(input_path=path)
    return {"inserted_rows": inserted}
