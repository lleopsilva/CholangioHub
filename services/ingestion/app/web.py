from typing import Callable, Awaitable

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from shared.schemas import IngestionRunResult
from shared.utils.metrics import ServiceMetrics

from .collectors.pubmed import run as run_pubmed

app = FastAPI(title="CholangioHub Ingestion Runner")
metrics = ServiceMetrics("cholangiohub_ingestion")


class IngestRequest(BaseModel):
    term: str = "cholangiocarcinoma"
    limit: int = 5


@app.middleware("http")
async def track_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    metrics.record_http_request()
    response = await call_next(request)
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def metrics_endpoint() -> PlainTextResponse:
    return PlainTextResponse(metrics.render(), media_type="text/plain; version=0.0.4")


@app.post("/ingest/pubmed", response_model=IngestionRunResult)
def ingest_pubmed(req: IngestRequest | None = None) -> IngestionRunResult:
    payload = req or IngestRequest()
    return run_pubmed(term=payload.term, limit=payload.limit)
