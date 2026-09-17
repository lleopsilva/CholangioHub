from pydantic import BaseModel


class IngestionRunResult(BaseModel):
    """Summary returned by an ingestion or processing run.

    Used as the response body for the ingestion and processing HTTP
    services, so callers (the Airflow DAG, tests, humans hitting the API
    by hand) get a consistent, typed shape instead of an ad-hoc dict.
    """

    run_id: str
    status: str
    records_in: int = 0
    records_out: int = 0
    object_key: str | None = None
    details: str | None = None
