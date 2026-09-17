"""Simple end-to-end validator that triggers ingestion -> process/silver -> process/gold
by calling the local HTTP endpoints and reporting statuses.

Usage: python scripts/validate_pipeline.py

Requires the services to be reachable at the host/ports documented in the README.
This script does not bring up Docker; run `make infra-up` beforehand.
"""
from __future__ import annotations

import time
import sys
import json
from typing import Optional

import requests

INGEST_URL = "http://localhost:8100/ingest/pubmed"
PROCESSING_URL = "http://localhost:8102"


def post_ingest(term: str = "cholangiocarcinoma", limit: int = 5) -> Optional[dict]:
    payload = {"term": term, "limit": limit}
    try:
        r = requests.post(INGEST_URL, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("ingest call failed:", e)
        return None


def post_processing(path: str) -> Optional[dict]:
    try:
        r = requests.post(f"{PROCESSING_URL}/{path}", json={}, timeout=600)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"processing {path} failed:", e)
        return None


def main():
    print("Triggering ingest/pubmed...")
    ingest_res = post_ingest()
    if not ingest_res:
        print("Ingest failed; aborting")
        sys.exit(1)
    print("Ingest result:", json.dumps(ingest_res, indent=2))

    # wait a little for objects to land in MinIO and services to be ready
    print("Waiting 5s before triggering silver processing...")
    time.sleep(5)

    print("Triggering /process/silver")
    silver_res = post_processing("process/silver")
    if not silver_res:
        print("Silver processing failed; aborting")
        sys.exit(1)
    print("Silver result:", json.dumps(silver_res, indent=2))

    print("Waiting 3s before triggering gold processing...")
    time.sleep(3)

    print("Triggering /process/gold")
    gold_res = post_processing("process/gold")
    if not gold_res:
        print("Gold processing failed; aborting")
        sys.exit(1)
    print("Gold result:", json.dumps(gold_res, indent=2))

    print("Pipeline validation complete")


if __name__ == "__main__":
    main()
