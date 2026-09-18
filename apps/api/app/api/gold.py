from __future__ import annotations

import ast
import os
from typing import Annotated, Any, cast

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies.database import database_session
from shared.models.metadata import AuditLog, Dataset, IngestionRun, Source

router = APIRouter()


@router.post("/process/gold")
def trigger_gold_processing() -> dict[str, Any]:
    """Trigger the processing service to run the Gold job.

    The processing service URL can be set with the `PROCESSING_SERVICE_URL`
    environment variable. Defaults to the compose service hostname.
    """
    processing_url = os.getenv("PROCESSING_SERVICE_URL", "http://cholangiohub-processing:8200")
    try:
        resp = requests.post(f"{processing_url}/process/gold", timeout=120)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return cast(dict[str, Any], resp.json())


@router.get("/runs", response_model=list[dict[str, Any]])
def list_gold_runs(session: Annotated[Session, Depends(database_session)]) -> list[dict[str, Any]]:
    """List recent Gold dataset runs from the metadata schema."""
    q = (
        session.query(IngestionRun, Dataset, Source)
        .join(Dataset, IngestionRun.dataset)
        .join(Source, Dataset.source)
        .filter(Dataset.layer == "gold")
        .order_by(IngestionRun.finished_at.desc())
        .limit(50)
    )

    results: list[dict[str, Any]] = []
    for run, dataset, source in q:
        results.append(
            {
                "run_id": str(run.id),
                "status": run.status,
                "records_processed": run.records_processed,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                "dataset": dataset.dataset_name,
                "source": source.name,
            }
        )

    return results


@router.get("/latest_summary")
def latest_gold_summary(session: Annotated[Session, Depends(database_session)]) -> dict[str, Any]:
    """Return the most recent Gold data quality summary extracted from the audit logs."""
    entry = (
        session.query(AuditLog)
        .filter(AuditLog.event_type == "data_quality")
        .order_by(AuditLog.created_at.desc())
        .first()
    )

    if entry is None or not entry.message:
        raise HTTPException(status_code=404, detail="No gold quality summary found")

    # message is written as: "Gold run <id> summary: { ... }"
    try:
        _, payload = entry.message.split("summary:", 1)
        summary = ast.literal_eval(payload.strip())
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse audit message") from None

    return cast(dict[str, Any], summary)



@router.get("/metrics")
def gold_metrics(
    journal: str | None = Query(None, description="Filter by journal"),
    year: int | None = Query(None, description="Filter by year"),
    limit: int = Query(100, description="Max results"),
    input_path: str | None = Query(None, description="Override gold parquet path"),
) -> list[dict[str, Any]]:
    """Proxy to the processing service `/gold/aggregations` endpoint and return aggregations."""
    processing_url = os.getenv("PROCESSING_SERVICE_URL", "http://cholangiohub-processing:8200")
    params = {"journal": journal, "year": year, "limit": limit}
    if input_path:
        params["input_path"] = input_path

    try:
        resp = requests.get(f"{processing_url}/gold/aggregations", params=params, timeout=120)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        data = resp.json()
    except Exception as exc:  # pragma: no cover - defensive
        detail = f"Invalid response from processing: {exc}"
        raise HTTPException(status_code=502, detail=detail) from exc

    if not isinstance(data, list):
        raise HTTPException(
            status_code=502, detail="Unexpected response shape from processing"
        )

    return cast(list[dict[str, Any]], data)
