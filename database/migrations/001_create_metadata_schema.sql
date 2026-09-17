CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS metadata;


CREATE TABLE IF NOT EXISTS metadata.sources
(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    name VARCHAR(150) NOT NULL,

    source_type VARCHAR(50) NOT NULL,

    description TEXT,

    url TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS metadata.datasets
(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    source_id UUID,

    dataset_name VARCHAR(150) NOT NULL,

    layer VARCHAR(30) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_dataset_source
        FOREIGN KEY(source_id)
        REFERENCES metadata.sources(id)
);