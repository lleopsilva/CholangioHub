from services.processing.app.jobs.parsing import parse_bronze_pubmed_payload


def make_payload(entries: dict) -> dict:
    return {
        "ids": list(entries.keys()),
        "summaries": {
            "header": {"type": "esummary"},
            "result": {"uids": list(entries.keys()), **entries},
        },
    }


def test_parses_valid_entries():
    payload = make_payload(
        {
            "111": {
                "title": "Cholangiocarcinoma review",
                "fulljournalname": "Journal of Hepatology",
                "pubdate": "2023 Jan 15",
                "authors": [{"name": "Silva L"}, {"name": "Souza M"}],
            }
        }
    )

    records = parse_bronze_pubmed_payload(payload, ingested_at="2026-07-20T00:00:00+00:00")

    assert len(records) == 1
    record = records[0]
    assert record["source"] == "pubmed"
    assert record["source_id"] == "111"
    assert record["title"] == "Cholangiocarcinoma review"
    assert record["journal"] == "Journal of Hepatology"
    assert record["pub_year"] == 2023
    assert record["authors"] == ["Silva L", "Souza M"]
    assert record["ingested_at"] == "2026-07-20T00:00:00+00:00"


def test_skips_entries_missing_title_completeness_check():
    payload = make_payload(
        {
            "111": {"title": "", "pubdate": "2023"},
            "222": {"title": "Has a title", "pubdate": "2022"},
        }
    )

    records = parse_bronze_pubmed_payload(payload)

    assert [r["source_id"] for r in records] == ["222"]


def test_handles_missing_pubdate_and_authors_gracefully():
    payload = make_payload({"111": {"title": "No extra fields"}})

    records = parse_bronze_pubmed_payload(payload)

    assert records[0]["pub_year"] is None
    assert records[0]["authors"] == []


def test_empty_payload_returns_no_records():
    assert parse_bronze_pubmed_payload({}) == []
    assert parse_bronze_pubmed_payload({"ids": [], "summaries": {}}) == []
