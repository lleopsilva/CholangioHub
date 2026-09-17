"""Append a concise sprint activity entry to docs/sprint_progress.md.

Short usage example:
    python scripts/log_sprint_activity.py --sprint "Sprint 2" --activity "PubMed collector" \
        --status completed --summary "Added collector and endpoint"
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parents[1] / "docs" / "sprint_progress.md"


def append_entry(sprint: str, activity: str, status: str, summary: str, details: str | None):
    ts = datetime.now(UTC).astimezone().isoformat()
    entry_lines = [
        "---\n",
        f"- **Timestamp**: {ts}\n",
        f"- **Sprint**: {sprint}\n",
        f"- **Activity**: {activity}\n",
        f"- **Status**: {status}\n",
        f"- **Summary**: {summary}\n",
    ]
    if details:
        entry_lines.append("- **Details**:\n")
        # indent details block
        for line in details.splitlines():
            entry_lines.append(f"    {line}\n")
    entry_lines.append("\n")

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.writelines(entry_lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sprint", required=True)
    parser.add_argument("--activity", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--details", default="")

    args = parser.parse_args()
    append_entry(args.sprint, args.activity, args.status, args.summary, args.details)
    print(f"Appended activity to {LOG_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
