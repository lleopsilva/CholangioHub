# Data Lineage

---

# Objetivo

Rastrear a origem e transformação dos dados.

---

# Exemplo

```text
PubMed API

↓

collector.py

↓

bronze/articles.json

↓

spark_transform.py

↓

silver/articles.parquet

↓

dbt

↓

gold/article_metrics

↓

dashboard

```

# Metadados mantidos

Cada registro deverá possuir:

source

ingestion_date

pipeline_version

processing_timestamp