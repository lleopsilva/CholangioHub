from pathlib import Path

from pyspark.sql import SparkSession

from services.processing.app.jobs import process_gold


def test_run_gold_job_local(tmp_path, monkeypatch):
    spark = SparkSession.builder.master("local[1]").appName("test-gold").getOrCreate()

    # create a small silver DataFrame and write to local parquet
    data = [
        ("PubMed", "1", "Title A", "Journal X", 2020, ["A B"], "2026-07-20T00:00:00+00:00"),
        ("PubMed", "2", "Title B", "Journal X", 2021, ["C D"], "2026-07-20T00:00:01+00:00"),
    ]
    cols = ["source", "source_id", "title", "journal", "pub_year", "authors", "ingested_at"]
    df = spark.createDataFrame(data, schema=cols)

    silver_dir = tmp_path / "silver_articles"
    gold_dir = tmp_path / "gold_metrics"
    silver_dir.mkdir()
    gold_dir.mkdir()

    df.write.mode("overwrite").parquet(str(silver_dir))

    # Monkeypatch DB interactions to avoid requiring a running Postgres instance
    class FakeSource:
        id = "source-1"

    class FakeDataset:
        id = "dataset-1"

    class FakeRun:
        id = "run-1"

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

    monkeypatch.setattr(process_gold, "Session", lambda bind=None: FakeSession())
    monkeypatch.setattr(process_gold, "get_or_create_source", lambda session, **kwargs: FakeSource())
    monkeypatch.setattr(process_gold, "get_or_create_dataset", lambda session, **kwargs: FakeDataset())
    monkeypatch.setattr(process_gold, "start_run", lambda session, **kwargs: FakeRun())
    monkeypatch.setattr(process_gold, "finish_run", lambda session, **kwargs: FakeRun())
    monkeypatch.setattr(process_gold, "log_audit_event", lambda session, **kwargs: None)

    result = process_gold.run_gold_job(
        spark=spark, prefix="pubmed_test", input_path=str(silver_dir), output_path=str(gold_dir)
    )

    assert result.status == "completed"
    # gold output parquet should exist
    files = list(Path(gold_dir).rglob("*.parquet"))
    assert len(files) > 0

    # cleanup spark
    spark.stop()
