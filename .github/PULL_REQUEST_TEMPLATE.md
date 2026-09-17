<!-- Title: short, imperative-style summary -->

## Summary

Describe the change and why it was made.

## Changes
- Added `process_gold` job, `/process/gold` endpoint and DAG step
- Added `scripts/validate_pipeline.py` to run a local e2e smoke test
- Added unit test `tests/services/processing/test_process_gold.py`

## How to test
1. Start local infra: `make infra-up`
2. Apply migrations: `make migrate`
3. Run validator: `python scripts/validate_pipeline.py`

## Checklist
- [ ] CI passes (unit + integration)
- [ ] Manual validation complete (see `scripts/validate_pipeline.py`)
- [ ] Documentation updated (`README.md`, `docs/sprint_progress.md`)

## Notes
If local Spark downloads are required, the first run may take longer due to Maven artifact fetching.
