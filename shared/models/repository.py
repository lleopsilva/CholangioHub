from datetime import UTC, datetime

from sqlalchemy.orm import Session

from shared.models.metadata import AuditLog, Dataset, IngestionRun, Source


def get_or_create_source(
    session: Session,
    *,
    name: str,
    source_type: str,
    description: str | None = None,
    url: str | None = None,
) -> Source:
    source = session.query(Source).filter_by(name=name).one_or_none()
    if source is None:
        source = Source(name=name, source_type=source_type, description=description, url=url)
        session.add(source)
        session.flush()
    return source


def get_or_create_dataset(
    session: Session,
    *,
    source: Source,
    dataset_name: str,
    layer: str,
) -> Dataset:
    dataset = (
        session.query(Dataset)
        .filter_by(source_id=source.id, dataset_name=dataset_name, layer=layer)
        .one_or_none()
    )
    if dataset is None:
        dataset = Dataset(source_id=source.id, dataset_name=dataset_name, layer=layer)
        session.add(dataset)
        session.flush()
    return dataset


def start_run(session: Session, *, dataset: Dataset) -> IngestionRun:
    run = IngestionRun(
        dataset_id=dataset.id,
        status="running",
        records_processed=0,
        started_at=datetime.now(UTC),
    )
    session.add(run)
    session.flush()
    return run


def finish_run(session: Session, *, run: IngestionRun, status: str, records_processed: int) -> IngestionRun:
    run.status = status
    run.records_processed = records_processed
    run.finished_at = datetime.now(UTC)
    session.add(run)
    session.flush()
    return run


def log_audit_event(session: Session, *, event_type: str, message: str) -> AuditLog:
    entry = AuditLog(event_type=event_type, message=message)
    session.add(entry)
    session.flush()
    return entry
