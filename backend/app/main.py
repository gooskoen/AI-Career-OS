# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI

from app.briefing import build_interview_briefing
from app.matching import score_job_match
from app.schemas import (
    BriefingRequest,
    CandidateProfile,
    JobDescription,
    MatchRequest,
)

app = FastAPI(
    title="AI-Career-OS API",
    version="0.1.0",
    description="MVP backend for ATS matching and interview briefing demos.",
)


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
