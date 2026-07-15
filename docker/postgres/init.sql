CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS metadata;

CREATE TABLE IF NOT EXISTS metadata.system_info
(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO metadata.system_info(application)
VALUES ('CholangioHub');