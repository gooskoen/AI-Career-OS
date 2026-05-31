# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable, TypeVar
from uuid import UUID

from fastapi import FastAPI, HTTPException
from psycopg import Error as PsycopgError

from app.application_package import (
    ApplicationPackageRequest,
    build_application_package,
)
from app.briefing import build_interview_briefing
from app.company_intelligence import (
    CompanyIntelligenceRequest,
    build_company_intelligence,
)
from app.database import get_connection
from app.feedback import (
    OutcomeRequest,
    build_candidate_insights,
    build_outcome_history,
)
from app.ingestion import (
    IngestionError,
    UrlFetchError,
    import_job_from_text,
    import_job_from_url,
)
from app.matching import score_job_match
from app.repositories import (
    candidate_from_row,
    create_candidate,
    create_application_outcome,
    create_interview_briefing,
    create_job,
    create_match_result,
    get_candidate,
    get_job,
    get_match_result,
    job_from_row,
    list_candidates,
    list_application_outcomes,
    list_interview_briefings,
    list_jobs,
    list_match_results,
    match_from_row,
)
from app.schemas import (
    BriefingRequest,
    CandidateProfile,
    JobDescription,
    JobImportTextRequest,
    JobImportUrlRequest,
    MatchRequest,
    PersistBriefingRequest,
    PersistMatchRequest,
)

app = FastAPI(
    title="AI-Career-OS API",
    version="0.1.0",
    description="MVP backend for ATS matching and interview briefing demos.",
)

T = TypeVar("T")


def _example_profile_path() -> Path:
    configured_path = os.getenv("EXAMPLE_PROFILE_PATH")
    if configured_path:
        return Path(configured_path)

    candidates = [
        Path.cwd() / "examples" / "candidate_profile.example.json",
        Path(__file__).resolve().parents[1] / "examples" / "candidate_profile.example.json",
        Path(__file__).resolve().parents[2] / "examples" / "candidate_profile.example.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ai-career-os"}


@app.get("/demo/candidate", response_model=CandidateProfile)
def demo_candidate() -> CandidateProfile:
    """Load the checked-in mock candidate profile."""

    with _example_profile_path().open("r", encoding="utf-8") as profile_file:
        return CandidateProfile.model_validate(json.load(profile_file))


@app.post("/match")
def match_job(request: MatchRequest) -> dict:
    result = score_job_match(request.candidate, request.job)
    return result.model_dump()


@app.post("/briefing")
def interview_briefing(request: BriefingRequest) -> dict:
    match = score_job_match(request.candidate, request.job)
    return build_interview_briefing(request.candidate, request.job, match)


@app.post("/applications/package")
def application_package(request: ApplicationPackageRequest) -> dict:
    package = build_application_package(
        request.candidate,
        request.job,
        request.match_result,
    )
    return package.model_dump()


@app.post("/intelligence/company")
def company_intelligence(request: CompanyIntelligenceRequest) -> dict:
    intelligence = build_company_intelligence(
        request.job,
        request.candidate,
        request.match_result,
        request.application_package,
        request.company_notes,
        request.recruiter_notes,
    )
    return intelligence.model_dump()


@app.get("/demo/match")
def demo_match() -> dict:
    candidate = demo_candidate()
    job = JobDescription(
        title="AI Product Operations Lead",
        company="ExampleTech",
        description=(
            "Lead AI product operations, stakeholder communication, workflow "
            "automation, analytics, backlog prioritization, and responsible AI "
            "delivery for internal business teams."
        ),
        required_skills=[
            "AI strategy",
            "workflow automation",
            "stakeholder management",
            "analytics",
            "responsible AI",
        ],
        nice_to_have_skills=["FastAPI", "PostgreSQL", "prompt engineering"],
    )
    return score_job_match(candidate, job).model_dump()


@app.post("/candidates")
def persist_candidate(candidate: CandidateProfile) -> dict:
    return _run_database_operation(
        lambda connection: create_candidate(connection, candidate)
    )


@app.get("/candidates")
def get_candidates() -> list[dict]:
    return _run_database_operation(list_candidates)


@app.post("/jobs")
def persist_job(job: JobDescription) -> dict:
    return _run_database_operation(lambda connection: create_job(connection, job))


@app.get("/jobs")
def get_jobs() -> list[dict]:
    return _run_database_operation(list_jobs)


@app.post("/jobs/import-text")
def import_text_job(request: JobImportTextRequest) -> dict:
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
        )
        return {
            "job": job_row,
            "duplicate": import_result["duplicate"],
            "match": match_row,
        }

    return _run_database_operation(operation)


@app.post("/jobs/import-url")
def import_url_job(request: JobImportUrlRequest) -> dict:
    def operation(connection):
        import_result = import_job_from_url(connection, request.url)
        job_row = import_result["job"]
        match_row = _create_optional_match(
            connection,
            job_row,
            request.match_candidate_id,
        )
        return {
            "job": job_row,
            "duplicate": import_result["duplicate"],
            "match": match_row,
        }

    return _run_database_operation(operation)


@app.post("/matches/persist")
def persist_match(request: PersistMatchRequest) -> dict:
    def operation(connection):
        candidate_row = _require_row(
            get_candidate(connection, request.candidate_profile_id),
            "Candidate profile not found",
        )
        job_row = _require_row(
            get_job(connection, request.job_description_id),
            "Job description not found",
        )
        match = score_job_match(candidate_from_row(candidate_row), job_from_row(job_row))
        return create_match_result(
            connection,
            request.candidate_profile_id,
            request.job_description_id,
            match,
        )

    return _run_database_operation(operation)


@app.get("/matches")
def get_matches() -> list[dict]:
    return _run_database_operation(list_match_results)


@app.post("/briefings/persist")
def persist_briefing(request: PersistBriefingRequest) -> dict:
    def operation(connection):
        match_row = _require_row(
            get_match_result(connection, request.match_result_id),
            "Match result not found",
        )
        candidate_row = _require_row(
            get_candidate(connection, match_row["candidate_profile_id"]),
            "Candidate profile not found",
        )
        job_row = _require_row(
            get_job(connection, match_row["job_description_id"]),
            "Job description not found",
        )
        briefing = build_interview_briefing(
            candidate_from_row(candidate_row),
            job_from_row(job_row),
            match_from_row(match_row),
        )
        return create_interview_briefing(
            connection,
            request.match_result_id,
            briefing,
        )

    return _run_database_operation(operation)


@app.get("/briefings")
def get_briefings() -> list[dict]:
    return _run_database_operation(list_interview_briefings)


@app.post("/outcomes")
def create_outcome(outcome: OutcomeRequest) -> dict:
    return _run_database_operation(
        lambda connection: create_application_outcome(connection, outcome)
    )


@app.get("/outcomes/{candidate_id}")
def get_outcomes(candidate_id: UUID) -> dict:
    return _run_database_operation(
        lambda connection: build_outcome_history(
            list_application_outcomes(connection, candidate_id)
        )
    )


@app.get("/insights/candidate/{candidate_id}")
def get_candidate_insights(candidate_id: UUID) -> dict:
    return _run_database_operation(
        lambda connection: build_candidate_insights(
            list_application_outcomes(connection, candidate_id)
        )
    )


def _run_database_operation(operation: Callable[..., T]) -> T:
    try:
        with get_connection() as connection:
            return operation(connection)
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UrlFetchError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except PsycopgError as exc:
        raise HTTPException(status_code=503, detail="Database operation failed") from exc


def _require_row(row: dict | None, message: str) -> dict:
    if row is None:
        raise HTTPException(status_code=404, detail=message)
    return row


def _create_optional_match(connection, job_row: dict, candidate_id) -> dict | None:
    if candidate_id is None:
        return None

    candidate_row = _require_row(
        get_candidate(connection, candidate_id),
        "Candidate profile not found",
    )
    match = score_job_match(candidate_from_row(candidate_row), job_from_row(job_row))
    return create_match_result(connection, candidate_id, job_row["id"], match)
