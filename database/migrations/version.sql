CREATE TABLE IF NOT EXISTS metadata.schema_version
(

    version INTEGER PRIMARY KEY,

    description VARCHAR(255),

    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);