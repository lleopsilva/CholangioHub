# Arquitetura Medallion

---

# Objetivo

Organizar os dados em camadas com diferentes níveis de tratamento.

---

# Bronze Layer

## Objetivo

Preservar dados originais.

---

Características:

- sem transformação;
- histórico completo;
- somente append.

---

Exemplo:

bronze/

pubmed/

2026/

article.json


---

# Silver Layer

## Objetivo

Dados tratados e normalizados.

---

Processos:

- limpeza;
- padronização;
- deduplicação;
- enriquecimento.

---

Exemplo:


silver/

articles/

clinical_trials/

drugs/


---

# Gold Layer

## Objetivo

Dados prontos para consumo.

---

Exemplos:


gold/

treatment_statistics

clinical_trial_dashboard

publication_metrics


---

# Fluxo

```text
Raw

↓

Bronze

↓

Silver

↓

Gold

↓

Users