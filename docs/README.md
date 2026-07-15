# CholangioHub

> **Open Data & Knowledge Platform for Cholangiocarcinoma**

![Status](https://img.shields.io/badge/status-under%20development-orange)
![Python](https://img.shields.io/badge/python-3.13-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📖 Sobre o projeto

O **CholangioHub** é uma plataforma open source desenvolvida para centralizar, organizar e disponibilizar informações confiáveis sobre **colangiocarcinoma**, integrando literatura científica, diretrizes clínicas, ensaios clínicos e dados públicos em um único ambiente.

O projeto possui dois objetivos complementares:

- democratizar o acesso à informação para pacientes, familiares e profissionais da saúde;
- servir como uma plataforma moderna de Engenharia de Dados e Analytics.

---

## 🎯 Missão

Construir a maior plataforma aberta em língua portuguesa dedicada ao conhecimento sobre colangiocarcinoma, baseada em evidências científicas e atualizada automaticamente.

---

## 👥 Público-alvo

- Pacientes
- Familiares
- Profissionais de saúde
- Pesquisadores
- Engenheiros de Dados
- Desenvolvedores Open Source

---

# 🏗 Arquitetura

```text
               Fontes de Dados

 PubMed
 ClinicalTrials
 WHO
 NIH
 INCA
 FDA
 ANVISA
 ESMO
 NCCN
 ASCO

             │

             ▼

      Data Ingestion

             ▼

        Apache Airflow

             ▼

       Apache Spark

             ▼

     Medallion Data Lake

 Bronze → Silver → Gold

      │             │

      ▼             ▼

 ClickHouse    PostgreSQL

        │

        ▼

      FastAPI

        │

 ┌──────┴────────┐

 ▼               ▼

Portal       Dashboard
```

---

# 🚀 Tecnologias

## Engenharia de Dados

- Apache Airflow
- Apache Spark
- dbt
- ClickHouse
- PostgreSQL
- MinIO

## Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic

## Frontend

- Streamlit

## Infraestrutura

- Docker
- Docker Compose
- GitHub Actions

---

# 📂 Estrutura do Projeto

```text
cholangiohub/

docs/
docker/
ingestion/
processing/
api/
dashboard/
ai/
tests/
scripts/
data/

docker-compose.yml
README.md
LICENSE
```

---

# 📚 Documentação

Toda documentação encontra-se em:

```
docs/
```

Incluindo:

- Arquitetura
- Modelo de Dados
- ADRs
- Roadmap
- Infraestrutura
- Engenharia
- Deployment

---

# 🧬 Fontes de Dados

A plataforma será alimentada automaticamente por fontes públicas como:

- PubMed
- ClinicalTrials.gov
- Europe PMC
- CrossRef
- WHO
- NIH
- NCI
- INCA
- ANVISA

---

# ⚠ Aviso Importante

O CholangioHub **não substitui orientação médica**.

Todo conteúdo disponibilizado possui finalidade educacional e informativa.

Sempre consulte profissionais de saúde para decisões relacionadas ao diagnóstico e tratamento.

---

# 🤝 Como contribuir

Contribuições serão muito bem-vindas.

Você poderá contribuir com:

- código
- documentação
- correções
- tradução
- novas integrações
- revisão científica

---

# 📅 Roadmap

- [x] Planejamento
- [ ] Arquitetura
- [ ] Infraestrutura
- [ ] Data Lake
- [ ] Airflow
- [ ] Spark
- [ ] Primeira ingestão
- [ ] API
- [ ] Dashboard
- [ ] IA
- [ ] Deploy

---

# 📄 Licença

MIT License.

---

# ❤️ Motivação

Este projeto nasceu da necessidade de reunir conhecimento confiável sobre uma doença rara para facilitar o acesso à informação por pacientes, familiares, profissionais de saúde e pesquisadores.

Acreditamos que informação organizada e baseada em evidências pode reduzir barreiras ao conhecimento e apoiar melhores decisões, sempre em conjunto com o acompanhamento médico.