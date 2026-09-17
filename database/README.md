# CholangioHub Database

Camada responsável pela evolução controlada dos bancos relacionais.

## Estratégia

As alterações estruturais são realizadas através de migrations versionadas.

## Ordem de execução

001_create_metadata_schema.sql

002_create_ingestion_control.sql

003_create_audit_layer.sql


## Regras

- Nunca alterar migrations aplicadas.
- Novas alterações geram novos arquivos.
- Toda alteração precisa possuir versão.