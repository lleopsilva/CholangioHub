CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS metadata.ingestion_runs
(

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    dataset_id UUID,

    status VARCHAR(30) NOT NULL,

    records_processed INTEGER DEFAULT 0,

    started_at TIMESTAMP,

    finished_at TIMESTAMP,


    CONSTRAINT fk_ingestion_dataset

        FOREIGN KEY(dataset_id)

        REFERENCES metadata.datasets(id)

);