# CholangioHub


## Sobre

Plataforma open source de dados e conhecimento sobre colangiocarcinoma.


## Arquitetura

Ver:

docs/02-architecture


## Stack

- Python
- FastAPI
- Streamlit
- PostgreSQL
- MinIO
- ClickHouse
- Apache Spark
- Apache Airflow


## Ambiente local


### Pré-requisitos

- Docker Desktop
- Python
- uv


### Instalação


```bash
cp .env.example .env

make install

make infra-up

make migrate
```

Isso sobe toda a infraestrutura local (Postgres, MinIO, ClickHouse, Airflow, Spark, API, Dashboard e o serviço de ingestão) e aplica as migrations do banco (`database/migrations/`, via `scripts/apply_migrations.py`).


## Serviços locais

| Serviço | URL | Descrição |
|---|---|---|
| API | http://localhost:8000 | FastAPI pública (`/health/db` disponível) |
| Dashboard | http://localhost:8501 | Streamlit (MVP) |
| Ingestão | http://localhost:8100 | Serviço HTTP interno; expõe `POST /ingest/pubmed` |
| Processamento | http://localhost:8200 | Serviço HTTP interno; expõe `POST /process/silver` (Bronze → Silver) |
| Airflow | http://localhost:8080 | UI de orquestração das DAGs |
| MinIO Console | http://localhost:9001 | Buckets `bronze`/`silver`/`gold` |


## Ingestão de dados

O serviço de ingestão roda o coletor do PubMed via `POST /ingest/pubmed`:

```bash
curl -X POST http://localhost:8100/ingest/pubmed \
  -H "Content-Type: application/json" \
  -d '{"term": "cholangiocarcinoma", "limit": 5}'
```

Isso grava o JSON bruto em `bronze/pubmed/AAAA/MM/DD/` no MinIO e registra a execução em `metadata.ingestion_runs`.

A DAG `pubmed_ingest` (`pipelines/dags/pubmed_ingest_dag.py`) chama esse mesmo endpoint diariamente. Para rodar manualmente pela UI do Airflow (http://localhost:8080), ative a DAG `pubmed_ingest` e dispare um "Trigger DAG".


## Processamento Silver

Depois da ingestão, o serviço de processamento lê o Bronze (MinIO), limpa/deduplica os artigos e grava o resultado em Parquet no Silver:

```bash
curl -X POST http://localhost:8200/process/silver
```

A mesma DAG `pubmed_ingest` já encadeia esse passo automaticamente depois da ingestão (`trigger_ingest >> process_silver`).

The DAG `pubmed_ingest` already chains this step automatically after ingestion (`trigger_ingest >> process_silver`).

## Processamento Gold

Após a etapa Silver há uma etapa Gold de agregações e métricas pronta para consumo. O serviço de processamento agora expõe `POST /process/gold`.

Para validar end-to-end localmente, depois de subir a infraestrutura e aplicar migrations, você pode usar o script de validação que aciona ingest → process/silver → process/gold:

```bash
python scripts/validate_pipeline.py
```

Ou acionar manualmente os endpoints quando os serviços estiverem expostos:

```bash
# trigger ingest
curl -X POST http://localhost:8100/ingest/pubmed -H "Content-Type: application/json" -d '{"term":"cholangiocarcinoma","limit":5}'

# process silver
curl -X POST http://localhost:8200/process/silver

# process gold
curl -X POST http://localhost:8200/process/gold
```

Note que a primeira execução do Spark baixa dependências Java do Maven Central (requer internet uma vez).
Isso lê `bronze/pubmed/**/*.json`, valida completude (título obrigatório), remove duplicados por `(source, source_id)` mantendo o registro mais recente, grava `silver/articles/` no MinIO e registra a execução + métricas de qualidade em `metadata.ingestion_runs` / `metadata.audit_logs`.

A mesma DAG `pubmed_ingest` já encadeia esse passo automaticamente depois da ingestão (`trigger_ingest >> process_silver`).

> Na primeira execução, o Spark baixa os pacotes `hadoop-aws`/`aws-java-sdk-bundle` do Maven Central (necessário para o job falar com o MinIO via S3A) — exige internet na primeira vez; depois fica em cache.


## Migrations

As migrations SQL versionadas ficam em `database/migrations/` e são aplicadas com:

```bash
make migrate
```

O script (`scripts/apply_migrations.py`) aplica todos os arquivos `.sql` em ordem alfabética; são idempotentes (`IF NOT EXISTS`), então rodar de novo não duplica nada.


## Monitoramento

Métricas básicas de infraestrutura (Postgres, containers) ficam disponíveis via Prometheus + Grafana, definidos em `infrastructure/docker/compose/monitoring.yml` e já incluídos no `docker-compose.yml`:

| Serviço | URL |
|---|---|
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (login inicial `admin`/`admin`) |


## Testes

```bash
make test
```

Roda os testes unitários. Os testes de integração (que sobem containers reais via testcontainers) rodam separadamente no CI ou com:

```bash
uv run pytest tests/services/ingestion/test_pubmed_integration.py
```