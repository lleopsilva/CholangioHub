# Arquitetura Geral

## CholangioHub

Open Data & Knowledge Platform for Cholangiocarcinoma

---

# 1. Introdução

O CholangioHub utiliza uma arquitetura moderna baseada em:

- Data Engineering;
- Data Lake;
- processamento distribuído;
- APIs;
- aplicações analíticas;
- inteligência artificial.

A arquitetura foi projetada para permitir evolução incremental, mantendo separação entre ingestão, processamento, armazenamento e consumo.

---

# 2. Princípios Arquiteturais

## Separação de responsabilidades

Cada componente possui uma função específica.

---

## Data First

Todos os recursos são derivados de dados rastreáveis.

---

## Cloud Native

A plataforma utiliza containers e componentes independentes.

---

## Open Source

Toda arquitetura utiliza tecnologias abertas.

---

## Evolução incremental

A plataforma deve crescer sem necessidade de reescrever componentes existentes.

---

# 3. Visão Macro

```mermaid
flowchart LR

A[Fontes Externas]

A --> B[Ingestion Layer]

B --> C[Airflow]

C --> D[Spark Processing]

D --> E[Data Lake]

E --> F[Analytics Layer]

F --> G[API]

G --> H[Applications]

--- 
```
# 4. Camadas

Data Source Layer

Responsável pelas fontes externas.

Exemplos:

--> PubMed
--> ClinicalTrials.gov
--> WHO
--> INCA
--> Guidelines


Ingestion Layer

Responsável pela coleta.

Tecnologias:

--> Python
--> Requests
--> BeautifulSoup
--> APIs REST

Orchestration Layer

Responsável pelo controle dos pipelines.

Tecnologia:

--> Apache Airflow

Processing Layer

Responsável pelo tratamento dos dados.

Tecnologias:

--> Apache Spark
--> Python
--> dbt

Storage Layer

Responsável pelo armazenamento.

Componentes:

--> MinIO
--> PostgreSQL
--> ClickHouse

Application Layer

Responsável pelo consumo.

Componentes:

--> FastAPI
--> Streamlit

Intelligence Layer

Responsável pela evolução com IA.

Componentes futuros:

--> NLP
--> Embeddings
--> Knowledge Graph
--> RAG