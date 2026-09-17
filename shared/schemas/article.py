from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class Article(BaseModel):
    """Canonical, cleaned representation of a scientific article.

    This is the contract produced by the Silver processing job and consumed
    by anything downstream (Gold aggregations, the API, the dashboard). It
    is intentionally source-agnostic: a PubMed record and a future
    ClinicalTrials.gov record should both be able to map onto this shape.
    """

    source: str = Field(..., description="Origin system, e.g. 'pubmed'")
    source_id: str = Field(..., description="Unique identifier within the source system")
    title: str
    journal: str | None = None
    pub_year: int | None = Field(default=None, description="Publication year, when parseable")
    authors: list[str] = Field(default_factory=list)
    ingested_at: datetime

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title must not be blank")
        return cleaned

    @field_validator("source_id")
    @classmethod
    def source_id_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("source_id must not be blank")
        return cleaned

    def dedup_key(self) -> str:
        """Key used to deduplicate records within and across ingestion runs."""
        return f"{self.source}:{self.source_id}"
