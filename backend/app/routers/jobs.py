# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import current_user, require_row, run_database_operation
from app.ingestion import import_job_from_text, import_job_from_url
from app.matching import score_job_match
from app.repositories import (
    candidate_from_row,
    create_job,
    create_match_result,
    get_candidate,
    job_from_row,
    list_jobs,
)
from app.schemas import JobDescription, JobImportTextRequest, JobImportUrlRequest

router = APIRouter()


@router.post("/jobs")
def persist_job(job: JobDescription) -> dict:
    return run_database_operation(lambda connection: create_job(connection, job))


@router.get("/jobs")
def get_jobs() -> list[dict]:
    return run_database_operation(list_jobs)


@router.post("/jobs/import-text")
def import_text_job(
    request: JobImportTextRequest,
    user: dict = Depends(current_user),
) -> dict:
    def operation(connection):
        import_result = import_job_from_text(
            connection,
            request.raw_text,
            request.source_url,
        )
        job_row = import_result["job"]
        match_row = _create_optional_match(
            connection,
            job_row,
            request.match_candidate_id,
            user["id"],
        )
        return {
            "job": job_row,
            "duplicate": import_result["duplicate"],
            "match": match_row,
        }

    return run_database_operation(operation)


@router.post("/jobs/import-url")
def import_url_job(
    request: JobImportUrlRequest,
    user: dict = Depends(current_user),
) -> dict:
    def operation(connection):
        import_result = import_job_from_url(connection, request.url)
        job_row = import_result["job"]
        match_row = _create_optional_match(
            connection,
            job_row,
            request.match_candidate_id,
            user["id"],
        )
        return {
            "job": job_row,
            "duplicate": import_result["duplicate"],
            "match": match_row,
        }

    return run_database_operation(operation)


def _create_optional_match(
    connection,
    job_row: dict,
    candidate_id,
    user_id,
) -> dict | None:
    if candidate_id is None:
        return None

    candidate_row = require_row(
        get_candidate(connection, candidate_id, user_id),
        "Candidate profile not found",
    )
    match = score_job_match(candidate_from_row(candidate_row), job_from_row(job_row))
    return create_match_result(connection, candidate_id, job_row["id"], match, user_id)
