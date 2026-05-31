# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from app.ingestion import (
    IngestionError,
    extract_job_from_text,
    import_job_from_text,
    normalize_job_text,
)


LINKEDIN_URL = "https://www.linkedin.com/jobs/view/4242424242/?currentJobId=5151515151"


def test_paste_import_from_linkedin_text_extracts_job_fields() -> None:
    raw_text = """
    Senior AI Product Manager
    ExampleTech
    Brussels, Belgium (Hybrid)
    Posted 2 days ago

    About the job
    Lead AI roadmap delivery, workflow automation, analytics, and stakeholder management.

    Required skills
    Python, SQL, Responsible AI
    """

    job = extract_job_from_text(raw_text, source_url=LINKEDIN_URL)

    assert job.source == "linkedin"
    assert job.title == "Senior AI Product Manager"
    assert job.company == "ExampleTech"
    assert job.location == "Brussels, Belgium (Hybrid)"
    assert job.source_url == LINKEDIN_URL
    assert job.external_id == "5151515151"
    assert "workflow automation" in job.required_skills
    assert "python" in job.required_skills
    assert "sql" in job.required_skills
    assert "responsible ai" in job.required_skills
    assert "Posted 2 days ago" in job.description


def test_linkedin_url_metadata_extraction_from_path_id() -> None:
    job = extract_job_from_text(
        "Data Platform Lead\nExampleCo\nRemote\nPython and SQL ownership.",
        source_url="https://linkedin.com/jobs/view/1234567890/",
    )

    assert job.source == "linkedin"
    assert job.external_id == "1234567890"


def test_duplicate_linkedin_import_returns_existing_job() -> None:
    existing = {
        "id": "existing-job",
        "title": "Senior AI Product Manager",
        "company": "ExampleTech",
        "location": "Brussels, Belgium (Hybrid)",
        "source_url": LINKEDIN_URL,
    }
    connection = FakeConnection(duplicate=existing)

    result = import_job_from_text(
        connection,
        "Senior AI Product Manager\nExampleTech\nBrussels, Belgium (Hybrid)",
        LINKEDIN_URL,
    )

    assert result == {"job": existing, "duplicate": True}
    assert connection.insert_count == 0


def test_rejected_private_and_local_urls() -> None:
    for url in [
        "ftp://www.linkedin.com/jobs/view/123",
        "http://localhost/jobs",
        "http://127.0.0.1/jobs",
        "http://10.0.0.1/jobs",
    ]:
        try:
            from app.ingestion import _validate_public_http_url

            _validate_public_http_url(url)
        except IngestionError:
            continue
        raise AssertionError(f"Expected URL to be rejected: {url}")


def test_normalize_job_text_collapses_empty_lines_and_spacing() -> None:
    assert normalize_job_text("Title\n\n   Company   \n\nRole   text") == (
        "Title\nCompany\nRole text"
    )


class FakeConnection:
    def __init__(self, duplicate: dict | None = None) -> None:
        self.duplicate = duplicate
        self.insert_count = 0

    def cursor(self):
        return FakeCursor(self)


class FakeCursor:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection
        self.last_sql = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def execute(self, sql: str, params=None) -> None:
        self.last_sql = sql
        if "INSERT INTO job_descriptions" in sql:
            self.connection.insert_count += 1

    def fetchone(self):
        if "SELECT" in self.last_sql and self.connection.duplicate:
            duplicate = self.connection.duplicate
            self.connection.duplicate = None
            return duplicate
        return {
            "id": "new-job",
            "title": "Senior AI Product Manager",
            "company": "ExampleTech",
            "location": "Brussels, Belgium (Hybrid)",
            "source_url": LINKEDIN_URL,
        }
