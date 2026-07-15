# Padrões de Desenvolvimento

## CholangioHub

---

# 1. Objetivo

Definir padrões técnicos para garantir qualidade, legibilidade e manutenção do código.

---

# 2. Linguagem Principal

A linguagem principal será:


Python 3.13


Motivos:

- ecossistema científico;
- integração com dados;
- NLP;
- APIs;
- Engenharia de Dados.

---

# 3. Estrutura de Código

Cada serviço deverá seguir:


service/

├── src/

│ ├── domain/

│ ├── application/

│ ├── infrastructure/

│ └── main.py

├── tests/

├── Dockerfile

├── requirements.txt

└── README.md


---

# 4. Padrões

## Formatação

Ferramenta:


Black


---

## Lint

Ferramenta:


Ruff


---

## Tipagem

Ferramenta:


MyPy


---

## Testes

Ferramenta:


Pytest


---

# 5. Princípios

- código simples;
- funções pequenas;
- baixo acoplamento;
- documentação obrigatória;
- testes antes de merge.