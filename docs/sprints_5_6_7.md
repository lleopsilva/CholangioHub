Sprint 5-7 Deliverables

Sprint 5 (stabilização & integração)
- Finish CI and merge `feat/gold-processing` PR (pending review).
- Add integration tests for the Gold end-to-end pipeline (ingest->silver->gold).
- Provide scripts to run local infra (MinIO, Postgres) for integration testing.

Sprint 6 (analytics & observability)
- Ingest Gold metrics into ClickHouse for analytics.
  - Implemented helper `services/processing/app/jobs/clickhouse.py` and endpoint
    `POST /gold/ingest_clickhouse` in the processing runner to trigger ingestion.
- Add Grafana dashboard placeholder at `infrastructure/grafana/dashboards/gold_metrics.json`.
- Expose metrics (Prometheus) already present on processing/ingestion services; wire to Grafana.

Sprint 7 (performance & scalability)
- Prepare Spark cluster configuration (YARN/Kubernetes) and make jobs cluster-ready.
- Investigate streaming ingestion options (Structured Streaming or Spark Streaming) for near-real-time updates to Gold.

Streaming prototype
- A local Structured Streaming prototype was added at `services/processing/app/jobs/streaming.py` and
  a CLI runner `services/processing/app/streaming_runner.py`.
- To run the prototype locally (reads Parquet files appended to Bronze and prints aggregations):

```bash
python -m services.processing.app.streaming_runner --input-path s3a://bronze/pubmed/ --output-path s3a://gold/article_metrics_stream/ --checkpoint /tmp/ckpt
```

Notes
- The prototype uses local[*] Spark session by default and writes aggregated results in `complete` output mode.
- For production, run the runner on a Spark cluster (YARN/K8s) and configure robust checkpointing and partitioning.

ClickHouse continuous ingestion
- The streaming job can now optionally ingest each micro-batch into ClickHouse via HTTP using `foreachBatch`.
- To run with ClickHouse ingestion enabled:

```bash
python -m services.processing.app.streaming_runner --input-path s3a://bronze/pubmed/ --enable-clickhouse --clickhouse-url http://clickhouse:8123 --clickhouse-db ch --checkpoint /tmp/ckpt
```

Security note: For production use, secure ClickHouse endpoint and consider batching/partitioning strategy and retries.

Run locally (quick start)

1. Start minimal infra (docker-compose with MinIO + Postgres).
2. Run migrations: `python scripts/apply_migrations.py`.
3. Seed Bronze data (fixtures) and run ingestion/processing endpoints.
4. Trigger ClickHouse ingestion (if ClickHouse available):

```bash
curl -X POST "http://localhost:8200/gold/ingest_clickhouse" -d "input_path=s3a://gold/article_metrics/"
```

Notes
- Integration tests requiring Docker/testcontainers are planned but not added yet — they will be implemented in `tests/integration/` once the team confirms testcontainer strategy and Python test environment in CI.
