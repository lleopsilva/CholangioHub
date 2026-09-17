import io
import json
import logging
from datetime import UTC, datetime

import requests
from sqlalchemy.orm import Session

from shared.database.engine import engine
from shared.logging import get_logger, log_with_fields
from shared.models import (
    finish_run,
    get_or_create_dataset,
    get_or_create_source,
    log_audit_event,
    start_run,
)
from shared.schemas import IngestionRunResult

from ..storage.minio_client import ensure_bucket, get_minio_client

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

logger = get_logger(__name__)


def search_pubmed(term: str, retmax: int = 5) -> list[str]:
    params = {
        "db": "pubmed",
        "term": term,
        "retmax": str(retmax),
        "retmode": "json",
    }
    resp = requests.get(ESEARCH_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    ids = data.get("esearchresult", {}).get("idlist", [])
    return ids


def fetch_summaries(ids: list[str]) -> dict:
    if not ids:
        return {}
    params = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
    resp = requests.get(ESUMMARY_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def store_raw_in_minio(data: dict, prefix: str = "pubmed") -> str:
    client = get_minio_client()
    bucket = "bronze"
    ensure_bucket(client, bucket)
    now = datetime.now(UTC)
    key = f"{prefix}/{now.strftime('%Y/%m/%d')}/{int(now.timestamp())}.json"
    raw = json.dumps(data).encode("utf-8")
    client.put_object(
        bucket, key, data=io.BytesIO(raw), length=len(raw), part_size=10 * 1024 * 1024
    )
    return key


def run(term: str = "cholangiocarcinoma", limit: int = 5) -> IngestionRunResult:
    """Fetch article summaries from PubMed and land them raw in the Bronze layer.

    Uses the shared ORM models/repository helpers (instead of hand-written SQL)
    so this collector and any future one share the same source/dataset/run
    bookkeeping logic.
    """
    log_with_fields(logger, logging.INFO, "pubmed ingestion started", term=term, limit=limit)

    ids = search_pubmed(term, retmax=limit)
    summaries = fetch_summaries(ids)

    object_key = store_raw_in_minio({"ids": ids, "summaries": summaries}, prefix="pubmed")

    with Session(bind=engine) as session:
        source = get_or_create_source(
            session,
            name="PubMed",
            source_type="scientific_database",
            description="PubMed articles",
            url="https://pubmed.ncbi.nlm.nih.gov",
        )
        dataset = get_or_create_dataset(
            session, source=source, dataset_name="pubmed", layer="bronze"
        )
        db_run = start_run(session, dataset=dataset)
        db_run = finish_run(session, run=db_run, status="completed", records_processed=len(ids))
        log_audit_event(
            session,
            event_type="ingestion",
            message=f"PubMed ingestion run {db_run.id}: {len(ids)} records -> {object_key}",
        )
        session.commit()
        run_id = str(db_run.id)

    log_with_fields(
        logger,
        logging.INFO,
        "pubmed ingestion finished",
        run_id=run_id,
        records=len(ids),
        object_key=object_key,
    )

    return IngestionRunResult(
        run_id=run_id,
        status="completed",
        records_in=len(ids),
        records_out=len(ids),
        object_key=object_key,
    )


if __name__ == "__main__":
    print(run())
