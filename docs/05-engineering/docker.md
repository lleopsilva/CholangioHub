# 6. `docs/05-engineering/docker.md`

```markdown
# Estratégia Docker

---

# Objetivo

Garantir ambiente reproduzível.

---

# Princípios

Todos os serviços serão executados em containers.

---

# Serviços iniciais


airflow

spark

minio

postgres

clickhouse

api

dashboard


---

# Docker Compose

Ambiente local:


docker compose up


---

# Imagens

Cada serviço terá:


Dockerfile


próprio.

---

# Configuração

Utilizar:


.env


Nunca armazenar secrets no código.