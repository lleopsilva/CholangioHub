"""Simple SQL migrations runner.

Applies all .sql files in database/migrations in alphabetical order
using the project's SQLAlchemy engine. Designed for local/dev usage
until a full Alembic integration is added.
"""
import logging
import os
import sys
from pathlib import Path

# Make the repo root importable even when this file is run directly
# (`python scripts/apply_migrations.py`), since Python only adds the
# script's own directory to sys.path in that case, not the repo root.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.database.engine import engine


MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "database" / "migrations"


def apply_migration_file(conn, path: Path):
    logging.info("Applying %s", path.name)
    sql = path.read_text(encoding="utf-8")
    # Execute raw SQL; migrations are idempotent (use IF NOT EXISTS)
    conn.exec_driver_sql(sql)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not MIGRATIONS_DIR.exists():
        logging.error("Migrations directory not found: %s", MIGRATIONS_DIR)
        return 1

    sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not sql_files:
        logging.info("No SQL migration files found in %s", MIGRATIONS_DIR)
        return 0

    with engine.begin() as conn:
        for f in sql_files:
            apply_migration_file(conn, f)

    logging.info("Migrations applied: %d files", len(sql_files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
