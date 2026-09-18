import os

import requests
from fastapi.testclient import TestClient

# Ensure settings can initialize during import in test environment
os.environ.setdefault("POSTGRES_DB", "testdb")
os.environ.setdefault("POSTGRES_USER", "user")
os.environ.setdefault("POSTGRES_PASSWORD", "pw")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("MINIO_ROOT_USER", "minio")
os.environ.setdefault("MINIO_ROOT_PASSWORD", "minio_pw")
os.environ.setdefault("MINIO_PORT", "9000")
os.environ.setdefault("MINIO_CONSOLE_PORT", "9001")
os.environ.setdefault("CLICKHOUSE_DB", "ch")
os.environ.setdefault("CLICKHOUSE_USER", "ch_user")
os.environ.setdefault("CLICKHOUSE_PASSWORD", "ch_pw")
os.environ.setdefault("CLICKHOUSE_HTTP_PORT", "8123")
os.environ.setdefault("CLICKHOUSE_NATIVE_PORT", "9000")

from apps.api.app import main as api_main
from apps.api.app.api import gold as gold_module


class FakeResp:
    def __init__(self, json_data, status_code: int = 200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.RequestException(f"status {self.status_code}")


def test_gold_metrics_proxies_success(monkeypatch):
    expected = [
        {"journal": "J1", "pub_year": 2020, "article_count": 42},
        {"journal": "J2", "pub_year": 2021, "article_count": 10},
    ]

    def fake_get(url, params=None, timeout=None):
        assert "/gold/aggregations" in url
        # params passed through from the API
        assert isinstance(params, dict)
        return FakeResp(expected, status_code=200)

    monkeypatch.setattr(gold_module.requests, "get", fake_get)

    client = TestClient(api_main.app)
    resp = client.get("/gold/metrics?journal=J1&year=2020&limit=10")

    assert resp.status_code == 200
    assert resp.json() == expected


def test_gold_metrics_processing_error(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise requests.RequestException("processing down")

    monkeypatch.setattr(gold_module.requests, "get", fake_get)

    client = TestClient(api_main.app)
    resp = client.get("/gold/metrics")

    assert resp.status_code == 502
    assert "processing" in resp.json()["detail"].lower()
