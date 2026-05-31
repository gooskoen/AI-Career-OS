# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import json

from app.application_package import build_application_package
from app.matching import score_job_match
from app.schemas import CandidateProfile, JobDescription


def test_strong_match_package() -> None:
    candidate = _candidate()
    job = _job()
    match = score_job_match(candidate, job)

    package = build_application_package(candidate, job, match)

    assert job.title in package.tailored_summary
    assert package.key_strengths
    assert package.talking_points
    assert "stretch application" not in package.cover_letter


def test_moderate_match_with_gaps() -> None:
    candidate = _candidate(
        skills=["Python", "SQL", "workflow automation"],
        experience_highlights=[
            "Delivered Python analytics for operations teams.",
            "Built SQL reporting for product operations.",
        ],
    )
    job = _job(required_skills=["Python", "SQL", "Kubernetes"])
    match = score_job_match(candidate, job)

    package = build_application_package(candidate, job, match)

    assert "Kubernetes" in package.risk_gaps
    assert any("Kubernetes" in edit for edit in package.recommended_cv_edits)


def test_weak_match_warning() -> None:
    candidate = _candidate(
        headline="Customer success coordinator",
        summary="Coordinates onboarding documentation.",
        target_roles=["Customer Success Manager"],
        skills=["documentation"],
        experience_highlights=["Maintained onboarding documentation."],
    )
    job = _job()
    match = score_job_match(candidate, job)

    package = build_application_package(candidate, job, match)

    assert "stretch application" in package.cover_letter
    assert any("stretch role" in point for point in package.talking_points)


def test_no_private_data_leakage() -> None:
    candidate = _candidate(
        summary=(
            "Builds automation. Contact alex@example.com or +32 499 12 34 56. "
            "Portfolio https://example.com/private"
        ),
        experience_highlights=[
            "Delivered Python analytics. Email alex@example.com for details.",
            "Built SQL reporting. Phone +32 499 12 34 56.",
        ],
    )
    job = _job()
    match = score_job_match(candidate, job)

    package = build_application_package(candidate, job, match)

    serialized = json.dumps(package.model_dump())
    assert "alex@example.com" not in serialized
    assert "+32 499 12 34 56" not in serialized
    assert "https://example.com/private" not in serialized


def _candidate(
    headline: str = "Automation specialist",
    summary: str = "Builds automation and analytics systems with 6 years of experience.",
    target_roles: list[str] | None = None,
    skills: list[str] | None = None,
    experience_highlights: list[str] | None = None,
) -> CandidateProfile:
    return CandidateProfile(
        name="Alex Demo",
        headline=headline,
        location="Remote",
        summary=summary,
        target_roles=target_roles or ["AI Product Operations Lead"],
        skills=skills or ["Python", "SQL", "Kubernetes", "workflow automation"],
        experience_highlights=experience_highlights
        or [
            "Delivered Python analytics for operations teams.",
            "Built SQL reporting for product operations.",
            "Operated Kubernetes services for internal automation tools.",
        ],
    )


def _job(required_skills: list[str] | None = None) -> JobDescription:
    return JobDescription(
        title="AI Product Operations Lead",
        company="ExampleTech",
        description=(
            "Lead Python, SQL, workflow automation, and Kubernetes delivery. "
            "Requires 5 years of operations automation experience."
        ),
        required_skills=required_skills or ["Python", "SQL", "Kubernetes"],
        nice_to_have_skills=["GraphQL", "workflow automation"],
    )
