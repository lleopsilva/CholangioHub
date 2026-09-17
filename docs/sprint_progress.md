---
- **Timestamp**: 2026-09-17T12:00:00.000000-03:00
- **Sprint**: Sprint 4
- **Activity**: Silver -> Gold processing (aggregation)
- **Status**: completed
- **Summary**: Added Gold aggregation job, endpoint and DAG step
- **Details**:
    Implemented `services/processing/app/jobs/process_gold.py` which reads `silver/articles/`, computes aggregations (example: counts per `journal` and `pub_year`) and writes results to `gold/article_metrics/`. Exposed `POST /process/gold` in the processing runner and updated the `pubmed_ingest` DAG to chain `process_silver >> process_gold`. Added unit test `tests/services/processing/test_process_gold.py` and a validation script `scripts/validate_pipeline.py` to run ingest → silver → gold locally.
---
# Sprint Progress Log

This file records concise summaries of sprint activities, appended by a small helper script after each completed activity.

Format for each entry:

- **Timestamp**: 2026-07-17T12:00:00Z
- **Sprint**: Sprint 2
- **Activity**: Implement PubMed collector
- **Status**: completed
- **Summary**: One-line summary of what was done
- **Details**: Optional multiline details

---
---
- **Timestamp**: 2026-07-17T11:21:53.805250-03:00
- **Sprint**: Sprint 1
- **Activity**: Infra, migrations, CI
- **Status**: completed
- **Summary**: Created Docker Compose, applied migrations, added CI workflow
- **Details**:
    Applied SQL migrations; fixed shared DB engine host; added .github/workflows/ci.yml (ruff, mypy, pytest, bandit, pip-audit).

---
- **Timestamp**: 2026-07-17T11:22:07.298656-03:00
- **Sprint**: Sprint 2
- **Activity**: Apply DB migrations to Postgres
- **Status**: completed
- **Summary**: Applied database migrations
- **Details**:
    Executed scripts/apply_migrations.py to apply SQL in database/migrations to Postgres metadata schema.

---
- **Timestamp**: 2026-07-17T11:22:13.617364-03:00
- **Sprint**: Sprint 2
- **Activity**: Bring up Docker Compose stack
- **Status**: completed
- **Summary**: Started storage, processing and application services via Docker Compose
- **Details**:
    Brought up Postgres, MinIO, ClickHouse, Airflow, Spark, API, Dashboard, and ingestion services for local development.

---
- **Timestamp**: 2026-07-17T11:22:18.596890-03:00
- **Sprint**: Sprint 2
- **Activity**: Implement PubMed collector + ingestion endpoint
- **Status**: completed
- **Summary**: Added PubMed collector and FastAPI ingestion endpoint
- **Details**:
    Collector uses Entrez e-utilities to fetch summaries; stores raw JSON in MinIO bronze bucket; registers runs in metadata.ingestion_runs; endpoint POST /ingest/pubmed added.

---
- **Timestamp**: 2026-07-17T11:22:23.372691-03:00
- **Sprint**: Sprint 2
- **Activity**: Add Airflow DAG to trigger ingestion
- **Status**: completed
- **Summary**: Added pubmed_ingest DAG
- **Details**:
    Created pipelines/dags/pubmed_ingest_dag.py using SimpleHttpOperator to POST to /ingest/pubmed (requires Airflow connection ingestion_service).

---
- **Timestamp**: 2026-07-17T11:42:29.915972-03:00
- **Sprint**: Sprint 2
- **Activity**: Configure Airflow ingestion_service connection
- **Status**: completed
- **Summary**: Added AIRFLOW_CONN_INGESTION_SERVICE env var
- **Details**:
    Set to http://cholangiohub-ingestion:8100 on airflow-webserver and airflow-scheduler in processing compose.

---
- **Timestamp**: 2026-07-17T19:30:00.000000-03:00
- **Sprint**: Sprint 3
- **Activity**: Plan next sprint and complete integration
- **Status**: in-progress
- **Summary**: Defined Sprint 3 objectives for compose finalization, end-to-end validation, and documentation
- **Details**:
    - Finalizar `infrastructure/docker/compose/processing.yml` e `application.yml`
    - Verificar execução end-to-end do DAG `pubmed_ingest`
    - Ajustar integração entre Airflow, ingestion service e API
    - Consolidar documentação e roadmap do projeto

---
- **Timestamp**: 2026-07-20T00:00:00.000000-03:00
- **Sprint**: Sprint 3
- **Activity**: Register ingestion_service connection explicitly + add health check
- **Status**: completed
- **Summary**: Airflow now registers the ingestion_service HTTP connection via CLI in the webserver entrypoint (metastore), in addition to the existing env var fallback
- **Details**:
    Added `airflow connections add ingestion_service --conn-type http --conn-host cholangiohub-ingestion --conn-port 8100` to airflow-webserver entrypoint. Added GET /health to services/ingestion. DAG now has an HttpSensor (wait_for_ingestion_service) before the trigger task.

---
- **Timestamp**: 2026-07-20T00:00:00.000000-03:00
- **Sprint**: Sprint 3
- **Activity**: Complete monitoring.yml (Prometheus + Grafana + cAdvisor)
- **Status**: completed
- **Summary**: Added monitoring stack and included it in docker-compose.yml
- **Details**:
    Prometheus scrapes cholangiohub-api, cholangiohub-ingestion (both need /metrics instrumentation as a follow-up — endpoints not yet exposed) and cadvisor. Grafana pre-provisioned with the Prometheus datasource. Ports: Prometheus 9090, Grafana 3000, cAdvisor 8081.

---
- **Timestamp**: 2026-07-20T00:00:00.000000-03:00
- **Sprint**: Sprint 3
- **Activity**: Add make migrate and finish README
- **Status**: completed
- **Summary**: Makefile now has a migrate target; README documents all local services, ingestion endpoint, migrations and monitoring
- **Details**:
    README.md was previously unfinished (unclosed code block, no docs for ingestion/migrate/monitoring). Completed with service table, curl example for POST /ingest/pubmed, and testing instructions.

---
- **Timestamp**: 2026-07-20T00:00:00.000000-03:00
- **Sprint**: Sprint 3
- **Activity**: End-to-end DAG validation
- **Status**: pending (manual step)
- **Summary**: Requires a local Docker environment to execute — not runnable in this environment
- **Details**:
    Next local step: `make infra-up && make migrate`, then trigger the `pubmed_ingest` DAG from the Airflow UI (or `airflow dags backfill pubmed_ingest -s 2026-07-18 -e 2026-07-19` for a backfill test) and confirm data lands in MinIO `bronze/pubmed/` and a row appears in `metadata.ingestion_runs`.
---
- **Timestamp**: 2026-07-20T00:00:00.000000-03:00
- **Sprint**: Sprint 4
- **Activity**: Add shared/schemas, shared/models, shared/logging
- **Status**: completed
- **Summary**: Added the shared contracts/persistence/logging layer that was pending since the first analysis, and refactored the PubMed collector to use it
- **Details**:
    shared/schemas: Article (canonical article contract) and IngestionRunResult (HTTP response contract). shared/models: SQLAlchemy ORM (Source, Dataset, IngestionRun, AuditLog) mapping the existing metadata schema, plus a repository module (get_or_create_source/dataset, start_run/finish_run, log_audit_event). shared/logging: JSON structured logger (get_logger, log_with_fields). services/ingestion/app/collectors/pubmed.py refactored to use these instead of raw SQL text() queries; unit and integration tests updated accordingly (integration test now builds its schema from the real database/migrations/*.sql files instead of a hand-rolled copy).

---
- **Timestamp**: 2026-07-20T00:00:00.000000-03:00
- **Sprint**: Sprint 4
- **Activity**: Bronze -> Silver processing service (PySpark)
- **Status**: completed
- **Summary**: New services/processing microservice, mirroring the ingestion service's HTTP-triggered pattern
- **Details**:
    app/jobs/parsing.py: pure-Python, Spark-free parser from raw PubMed bronze payloads to flat article dicts, with completeness checks (skips blank titles) - unit tested in tests/services/processing/test_parsing.py. app/jobs/process_silver.py: PySpark job (local[*] mode, s3a config for MinIO) that reads bronze/pubmed/**/*.json, parses, deduplicates by (source, source_id) keeping the most recent ingested_at, writes Parquet to silver/articles/, and registers the run + quality metrics via shared.models. app/web.py exposes POST /process/silver and GET /health. Added to infrastructure/docker/compose/processing.yml; DAG pubmed_ingest now chains trigger_ingest >> wait_for_processing_service >> process_silver.
- **Note**: Not runnable in this environment (no Docker/Java). First local run needs internet once (Spark downloads hadoop-aws/aws-java-sdk-bundle from Maven). Next manual step: `make infra-up`, trigger the pubmed_ingest DAG, and confirm silver/articles/ appears in MinIO with the expected row count.
