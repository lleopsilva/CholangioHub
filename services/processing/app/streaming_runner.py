from __future__ import annotations

import argparse

from .jobs.streaming import run_streaming_job


def main() -> None:
    parser = argparse.ArgumentParser("Streaming runner for CholangioHub")
    parser.add_argument(
        "--input-path",
        default="s3a://bronze/pubmed/",
        help="Input path for streaming parquet",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Optional output Parquet path for aggregated results",
    )
    parser.add_argument(
        "--checkpoint",
        default="/tmp/cholangiohub_stream_ckpt",
        help="Checkpoint location for streaming",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=None,
        help="Timeout in ms to run the stream",
    )
    parser.add_argument(
        "--enable-clickhouse",
        action="store_true",
        help="Enable per-batch ingestion to ClickHouse",
    )
    parser.add_argument(
        "--clickhouse-url",
        default=None,
        help="ClickHouse HTTP URL (e.g. http://clickhouse:8123)",
    )
    parser.add_argument(
        "--clickhouse-db",
        default=None,
        help="ClickHouse database name",
    )
    parser.add_argument(
        "--clickhouse-table",
        default="article_metrics",
        help="ClickHouse target table name",
    )
    args = parser.parse_args()

    run_streaming_job(
        input_path=args.input_path,
        output_path=args.output_path,
        checkpoint_location=args.checkpoint,
        await_termination=True,
        timeout_ms=args.timeout_ms,
        enable_clickhouse=args.enable_clickhouse,
        clickhouse_url=args.clickhouse_url,
        clickhouse_db=args.clickhouse_db,
        clickhouse_table=args.clickhouse_table,
    )


if __name__ == "__main__":
    main()
