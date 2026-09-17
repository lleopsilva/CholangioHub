from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from shared.schemas import IngestionRunResult
from shared.utils.metrics import ServiceMetrics

from .jobs.process_silver import run_silver_job
from .jobs.process_gold import run_gold_job

app = FastAPI(title="CholangioHub Processing Runner")
metrics = ServiceMetrics("cholangiohub_processing")


@app.middleware("http")
async def track_requests(request, call_next):
    metrics.record_http_request()
    response = await call_next(request)
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics_endpoint():
    return PlainTextResponse(metrics.render(), media_type="text/plain; version=0.0.4")


@app.post("/process/silver", response_model=IngestionRunResult)
def process_silver():
    return run_silver_job()


@app.post("/process/gold", response_model=IngestionRunResult)
def process_gold():
    return run_gold_job()
