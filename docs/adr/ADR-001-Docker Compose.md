# ADR-001 — Docker Compose

## Status

Accepted

---

# Contexto

O projeto precisa possuir ambiente reproduzível para desenvolvimento.

---

# Decisão

Utilizar Docker Compose como mecanismo inicial de execução.

---

# Justificativa

Permite:

- ambiente local completo;
- isolamento de serviços;
- fácil onboarding;
- documentação simples.

---

# Serviços iniciais

- PostgreSQL
- MinIO
- Airflow
- Spark
- ClickHouse
- API
- Dashboard

---

# Consequência futura

Caso necessário poderá evoluir para Kubernetes.