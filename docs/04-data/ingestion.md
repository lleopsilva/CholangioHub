
---

# 4. `docs/04-data/ingestion.md`

```markdown
# Estratégia de Ingestão

---

# Objetivo

Definir como dados externos serão coletados.

---

# Arquitetura

```mermaid
flowchart LR

A[Source]

B[Collector]

C[Airflow]

D[Bronze]


A --> B
B --> C
C --> D

Tipos de ingestão
API

Preferencial.

Exemplo:

PubMed API.

Web Scraping

Usado quando não existir API.

Tecnologias:

BeautifulSoup
Selenium
Upload manual

Para documentos específicos:

guidelines;
PDFs institucionais.
Frequência

Exemplo:

Artigos:

Diário

Clinical Trials:

Diário

Guidelines:

Semanal/Mensal