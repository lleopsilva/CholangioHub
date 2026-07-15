
---

# 4. `docs/02-architecture/deployment-view.md`

```markdown
# Deployment View

---

# Ambiente inicial

O CholangioHub será executado inicialmente utilizando Docker Compose.

---

# Containers

```mermaid
graph TD

N[Nginx]

N --> API[FastAPI]

N --> UI[Streamlit]

API --> CH[ClickHouse]

API --> PG[PostgreSQL]

AIR[Airflow]

AIR --> SP[Spark]

SP --> MINIO[MinIO]