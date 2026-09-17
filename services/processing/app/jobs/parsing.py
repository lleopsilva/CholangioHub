import re
from datetime import UTC, datetime
from typing import Any

_YEAR_RE = re.compile(r"(19|20)\d{2}")


def _parse_pub_year(pubdate: str | None) -> int | None:
    if not pubdate:
        return None
    match = _YEAR_RE.search(pubdate)
    return int(match.group(0)) if match else None


def _extract_authors(raw_authors: list[dict[str, Any]] | None) -> list[str]:
    if not raw_authors:
        return []
    names: list[str] = []
    for a in raw_authors:
        if isinstance(a, dict):
            name = a.get("name")
            if isinstance(name, str):
                names.append(name)
    return names


def parse_bronze_pubmed_payload(
    payload: dict[str, Any], *, ingested_at: str | None = None
) -> list[dict[str, Any]]:
    """Turn one raw bronze PubMed JSON payload into a list of flat article dicts.

    `payload` is the object stored by services/ingestion (shape:
    ``{"ids": [...], "summaries": {"result": {"uids": [...], "<uid>": {...}}}}``).
    Kept free of Spark/DB dependencies so it can be unit tested in isolation
    and reused by the Spark job as a `flatMap` function.
    """
    ingested_at = ingested_at or datetime.now(UTC).isoformat()

    result = (payload or {}).get("summaries", {}).get("result", {})
    uids = result.get("uids", [])

    records: list[dict[str, Any]] = []
    for uid in uids:
        entry = result.get(uid)
        if not isinstance(entry, dict):
            continue

        title = (entry.get("title") or "").strip()
        if not title:
            # Completeness check: skip records missing a required field
            continue

        records.append(
            {
                "source": "pubmed",
                "source_id": str(uid),
                "title": title,
                "journal": entry.get("fulljournalname"),
                "pub_year": _parse_pub_year(entry.get("pubdate")),
                "authors": _extract_authors(entry.get("authors")),
                "ingested_at": ingested_at,
            }
        )

    return records
