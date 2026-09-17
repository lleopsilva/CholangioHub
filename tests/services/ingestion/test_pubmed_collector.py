from services.ingestion.app.collectors import pubmed
from shared.schemas import IngestionRunResult


def test_run_publishes_and_registers(monkeypatch):
    # Arrange: mock search and fetch
    ids = ["1", "2", "3"]
    summaries = {"uids": ids}
    monkeypatch.setattr(pubmed, "search_pubmed", lambda term, retmax=5: ids)
    monkeypatch.setattr(pubmed, "fetch_summaries", lambda ids: summaries)

    # Fake MinIO client
    class FakeMinioClient:
        def __init__(self):
            self.calls = []

        def put_object(self, bucket, key, data, length, part_size=None):
            content = data.read() if hasattr(data, "read") else data
            self.calls.append({"bucket": bucket, "key": key, "content": content, "length": length})

    fake_client = FakeMinioClient()
    monkeypatch.setattr(pubmed, "get_minio_client", lambda: fake_client)
    monkeypatch.setattr(pubmed, "ensure_bucket", lambda client, bucket: None)

    # Fake ORM session standing in for shared.models repository calls
    class FakeSource:
        id = "source-1"

    class FakeDataset:
        id = "dataset-1"

    class FakeRun:
        id = "456"
        status = None
        records_processed = None

    class FakeSession:
        def __init__(self):
            self.committed = False

        def add(self, obj):
            pass

        def flush(self):
            pass

        def commit(self):
            self.committed = True

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(pubmed, "Session", lambda bind=None: FakeSession())
    monkeypatch.setattr(pubmed, "get_or_create_source", lambda session, **kwargs: FakeSource())
    monkeypatch.setattr(pubmed, "get_or_create_dataset", lambda session, **kwargs: FakeDataset())
    monkeypatch.setattr(pubmed, "start_run", lambda session, **kwargs: FakeRun())
    monkeypatch.setattr(pubmed, "finish_run", lambda session, **kwargs: FakeRun())
    monkeypatch.setattr(pubmed, "log_audit_event", lambda session, **kwargs: None)

    # Act
    result = pubmed.run(term="cholangiocarcinoma", limit=3)

    # Assert
    assert isinstance(result, IngestionRunResult)
    assert result.run_id == "456"
    assert result.records_in == 3
    assert result.status == "completed"
    assert result.object_key.startswith("pubmed/")
    assert fake_client.calls, "Expected MinIO put_object to be called"
    call = fake_client.calls[0]
    assert call["bucket"] == "bronze"
    assert call["length"] == len(call["content"])
