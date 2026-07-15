
---

# 2. `docs/03-domain/entities.md`

```markdown
# Entidades do Domínio

---

# Disease

Representa a doença.

## Atributos
id

name

description

classification

created_at


Exemplo:

---

# Subtype

Tipos anatômicos.

Exemplos:

- Intrahepatic Cholangiocarcinoma
- Perihilar Cholangiocarcinoma
- Distal Cholangiocarcinoma

---

# Article

Representa uma publicação científica.

Atributos:
id

title

abstract

journal

publication_date

doi

source

---

# ClinicalTrial

Representa estudos clínicos.

Atributos:
id

title

phase

status

intervention

location

---

# Treatment

Representa modalidades terapêuticas.

Exemplos:

- cirurgia;
- quimioterapia;
- radioterapia;
- imunoterapia;
- terapia alvo.

---

# Drug

Medicamentos.

Exemplos:

- Durvalumab
- Pembrolizumab
- FGFR inhibitors

---

# Biomarker

Marcadores associados.

Exemplos:

- IDH1
- FGFR2 fusion
- HER2
- MSI

---

# Gene

Informações genéticas.

---

# Guideline

Diretrizes clínicas.

Exemplos:

- NCCN
- ESMO
- ASCO

---

# Organization

Instituições.

Exemplos:

- WHO
- NIH
- FDA
- INCA

---

# Author

Autores científicos.

---

# PatientEducation

Conteúdo educacional.

Exemplos:

- explicações;
- perguntas frequentes;
- cuidados.