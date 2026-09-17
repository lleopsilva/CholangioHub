CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS metadata.audit_logs
(

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    event_type VARCHAR(100),

    message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);