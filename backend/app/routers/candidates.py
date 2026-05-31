# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import json

from fastapi import APIRouter

from app.dependencies import example_profile_path, run_database_operation
from app.repositories import create_candidate, list_candidates
from app.schemas import CandidateProfile

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ai-career-os"}


@router.get("/demo/candidate", response_model=CandidateProfile)
def demo_candidate() -> CandidateProfile:
    """Load the checked-in mock candidate profile."""

    with example_profile_path().open("r", encoding="utf-8") as profile_file:
        return CandidateProfile.model_validate(json.load(profile_file))


@router.post("/candidates")
def persist_candidate(candidate: CandidateProfile) -> dict:
    return run_database_operation(
        lambda connection: create_candidate(connection, candidate)
    )


@router.get("/candidates")
def get_candidates() -> list[dict]:
    return run_database_operation(list_candidates)
