
---

# 5. `docs/02-architecture/infrastructure.md`

```markdown
# Arquitetura Física

---

# Ambiente Docker

Todos os serviços serão executados em containers independentes.

---

# Rede

Serão utilizadas redes separadas:

## frontend

Comunicação:

- Nginx
- API
- Dashboard

---

## backend

Comunicação:

- Airflow
- Spark
- APIs internas

---

## storage

Comunicação:

- MinIO
- PostgreSQL
- ClickHouse

---

# Volumes

Persistência:

- minio-data
- postgres-data
- clickhouse-data
- airflow-logs
- spark-events

---

# Configuração

Todas as configurações sensíveis estarão em: .env 
Nunca serão armazenadas no código.