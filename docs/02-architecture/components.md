
---

# 2. `docs/02-architecture/components.md`

```markdown
# Componentes da Plataforma

---

# Visão Geral

O CholangioHub é composto por componentes independentes.

---

# 1. Ingestion Service

Responsabilidade:

Coletar informações externas.

Exemplos:

- artigos;
- estudos;
- documentos.

Tecnologia:

Python.

---

# 2. Airflow

Responsabilidade:

Orquestrar pipelines.

Executa:

- agendamento;
- dependências;
- retries;
- monitoramento.

---

# 3. Spark

Responsabilidade:

Processamento distribuído.

Executa:

- limpeza;
- transformação;
- enriquecimento;
- agregações.

---

# 4. MinIO

Responsabilidade:

Data Lake.

Estrutura:
bronze/

silver/

gold/


---

# 5. PostgreSQL

Responsabilidade:

Dados transacionais.

Armazena:

- usuários;
- configurações;
- metadados.

---

# 6. ClickHouse

Responsabilidade:

Analytics.

Armazena:

- métricas;
- indicadores;
- consultas analíticas.

---

# 7. FastAPI

Responsabilidade:

Camada de serviço.

Exposição:

- artigos;
- estudos;
- tratamentos;
- indicadores.

---

# 8. Streamlit

Responsabilidade:

Interface analítica.

Exibe:

- dashboards;
- gráficos;
- pesquisas.

---

# 9. AI Layer

Responsabilidade:

Transformar dados em conhecimento.

Futuro:

- classificação;
- resumo;
- busca inteligente.