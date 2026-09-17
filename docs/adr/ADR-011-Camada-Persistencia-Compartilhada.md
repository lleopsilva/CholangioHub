# ADR-011 — Camada de Persistência Compartilhada

## Status

Accepted

## Data

2026-07-16

## Contexto

O CholangioHub é uma plataforma composta por múltiplos componentes:

- API FastAPI
- Serviços de Ingestão
- Serviços de Processamento
- Dashboard
- Serviços de IA

Esses componentes precisam acessar o banco de metadados PostgreSQL.

A arquitetura inicial definiu a existência de componentes compartilhados em `shared/`, porém não havia uma definição explícita sobre a localização da infraestrutura de persistência.

Sem essa definição, cada aplicação poderia implementar sua própria conexão com banco, causando duplicação, inconsistência e maior custo de manutenção.

## Decisão

A infraestrutura de persistência compartilhada será localizada em:

shared/
└── database/


Essa camada será responsável pelos componentes técnicos de acesso ao banco:

- configuração do engine;
- gerenciamento de sessões;
- classe base ORM;
- utilitários comuns de persistência.

A camada não conterá regras de negócio.

As regras de negócio permanecem nos respectivos serviços:

- `services/ingestion`
- `services/processing`
- `services/ai`

## Consequências

### Positivas

- Reutilização da infraestrutura de banco por todos os componentes.
- Padronização do acesso ao PostgreSQL.
- Redução de código duplicado.
- Melhor isolamento entre infraestrutura e domínio.
- Facilita testes automatizados.

### Negativas

- Introdução de uma nova responsabilidade dentro de `shared`.
- Necessidade de manter disciplina para não transformar essa camada em depósito de regras de negócio.

## Estrutura resultante

shared/
├── config/
├── database/
├── logging/
├── models/
├── schemas/
└── utils/

