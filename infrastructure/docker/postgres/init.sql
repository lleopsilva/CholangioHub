-- Minimal init script: create extensions and schemas only.
-- Table creation and data insertion are managed via versioned SQL migrations
-- located in database/migrations/ and applied by scripts/apply_migrations.py.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS metadata;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;