from fastapi.testclient import TestClient

from services.ingestion.app import web as ingestion_web
from services.processing.app import web as processing_web


def test_ingestion_metrics_endpoint_exposes_basic_metrics():
    client = TestClient(ingestion_web.app)

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "cholangiohub_ingestion_http_requests_total" in response.text
    assert "# TYPE cholangiohub_ingestion_http_requests_total counter" in response.text


def test_processing_metrics_endpoint_exposes_basic_metrics():
    client = TestClient(processing_web.app)

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "cholangiohub_processing_http_requests_total" in response.text
    assert "# TYPE cholangiohub_processing_http_requests_total counter" in response.text


def test_ingestion_endpoint_accepts_empty_body_and_uses_defaults(monkeypatch):
    client = TestClient(ingestion_web.app)

    called = {}

    def fake_run_pubmed(term: str, limit: int):
        called["term"] = term
        called["limit"] = limit
        return {"run_id": "test-run", "status": "completed", "records_in": 0, "records_out": 0}

    monkeypatch.setattr(ingestion_web, "run_pubmed", fake_run_pubmed)

    response = client.post("/ingest/pubmed")

    assert response.status_code == 200
    assert called == {"term": "cholangiocarcinoma", "limit": 5}
