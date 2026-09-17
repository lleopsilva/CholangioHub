import shutil
from pathlib import Path

from pyspark.sql import SparkSession

from services.processing.app.jobs.process_gold import run_gold_job


def test_run_gold_job_local(tmp_path):
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

    df.write.parquet(str(silver_dir))

    result = run_gold_job(spark=spark, prefix="pubmed_test", input_path=str(silver_dir), output_path=str(gold_dir))

    assert result.status == "completed"
    # gold output parquet should exist
    files = list(Path(gold_dir).rglob("*.parquet"))
    assert len(files) > 0

    # cleanup spark
    spark.stop()
