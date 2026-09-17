from sqlalchemy import create_engine, text

eng = create_engine(
    'postgresql+psycopg2://postgres:postgres@127.0.0.1:55942/postgres'
)
with eng.connect() as conn:
    row = conn.execute(
        text(
            'SELECT id, status, records_processed, started_at, finished_at '
            'FROM metadata.ingestion_runs ORDER BY started_at DESC LIMIT 1'
        )
    ).fetchone()
    print(row)
