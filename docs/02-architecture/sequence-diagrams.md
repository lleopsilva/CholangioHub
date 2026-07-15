# Diagramas de Sequência

---

# Pipeline de ingestão

```mermaid
sequenceDiagram

participant Source
participant Collector
participant Airflow
participant Storage
participant Spark
participant Warehouse


Airflow->>Collector: Executa coleta

Collector->>Source: Solicita dados

Source-->>Collector: Retorna documentos

Collector->>Storage: Salva Bronze

Airflow->>Spark: Executa processamento

Spark->>Storage: Atualiza Silver

Spark->>Warehouse: Publica Gold

sequenceDiagram

participant User
participant Dashboard
participant API
participant ClickHouse


User->>Dashboard: Pesquisa informação

Dashboard->>API: Solicita dados

API->>ClickHouse: Consulta

ClickHouse-->>API: Resultado

API-->>Dashboard: Resposta

Dashboard-->>User: Visualização