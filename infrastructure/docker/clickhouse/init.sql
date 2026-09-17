CREATE DATABASE IF NOT EXISTS cholangiohub_raw;

CREATE DATABASE IF NOT EXISTS cholangiohub_analytics;



CREATE TABLE IF NOT EXISTS cholangiohub_raw.documents
(

    id UUID,

    source String,

    title String,

    content String,

    ingestion_date DateTime DEFAULT now()

)

ENGINE = MergeTree

ORDER BY ingestion_date;



CREATE TABLE IF NOT EXISTS cholangiohub_analytics.dataset_metrics
(

    dataset String,

    total_records UInt64,

    processed_at DateTime DEFAULT now()

)

ENGINE = MergeTree

ORDER BY processed_at;