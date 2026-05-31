# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.briefing import build_interview_briefing
from app.dependencies import current_user, require_row, run_database_operation
from app.matching import score_job_match
from app.repositories import (
    candidate_from_row,
    create_interview_briefing,
    create_match_result,
    get_candidate,
    get_job,
    get_match_result,
    job_from_row,
    list_interview_briefings,
    list_match_results,
    match_from_row,
)
from app.routers.candidates import demo_candidate
from app.schemas import (
    BriefingRequest,
    JobDescription,
    MatchRequest,
    PersistBriefingRequest,
    PersistMatchRequest,
)

router = APIRouter()


@router.post("/match")
def match_job(request: MatchRequest) -> dict:
    result = score_job_match(request.candidate, request.job)
    return result.model_dump()


@router.post("/briefing")
def interview_briefing(request: BriefingRequest) -> dict:
    match = score_job_match(request.candidate, request.job)
    return build_interview_briefing(request.candidate, request.job, match)


@router.get("/demo/match")
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


@router.post("/matches/persist")
def persist_match(
    request: PersistMatchRequest,
    user: dict = Depends(current_user),
) -> dict:
    def operation(connection):
        candidate_row = require_row(
            get_candidate(connection, request.candidate_profile_id, user["id"]),
            "Candidate profile not found",
        )
        job_row = require_row(
            get_job(connection, request.job_description_id),
            "Job description not found",
        )
        match = score_job_match(candidate_from_row(candidate_row), job_from_row(job_row))
        return create_match_result(
            connection,
            request.candidate_profile_id,
            request.job_description_id,
            match,
            user["id"],
        )

    return run_database_operation(operation)


@router.get("/matches")
def get_matches(user: dict = Depends(current_user)) -> list[dict]:
    return run_database_operation(
        lambda connection: list_match_results(connection, user["id"])
    )


@router.post("/briefings/persist")
def persist_briefing(
    request: PersistBriefingRequest,
    user: dict = Depends(current_user),
) -> dict:
    def operation(connection):
        match_row = require_row(
            get_match_result(connection, request.match_result_id, user["id"]),
            "Match result not found",
        )
        candidate_row = require_row(
            get_candidate(connection, match_row["candidate_profile_id"], user["id"]),
            "Candidate profile not found",
        )
        job_row = require_row(
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
            user["id"],
        )

    return run_database_operation(operation)


@router.get("/briefings")
def get_briefings(user: dict = Depends(current_user)) -> list[dict]:
    return run_database_operation(
        lambda connection: list_interview_briefings(connection, user["id"])
    )
