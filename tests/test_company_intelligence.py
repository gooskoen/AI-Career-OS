# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import json

from app.application_package import build_application_package
from app.company_intelligence import build_company_intelligence
from app.matching import score_job_match
from app.schemas import CandidateProfile, JobDescription


def test_company_intelligence_from_job_description() -> None:
    candidate, job, match, package = _context()

    intelligence = build_company_intelligence(job, candidate, match, package)

    assert job.company in intelligence.company_summary
    assert job.title in intelligence.company_summary
    assert intelligence.likely_business_needs
    assert any("automation" in need.lower() for need in intelligence.likely_business_needs)


def test_recruiter_message_generation() -> None:
    candidate, job, match, package = _context()

    intelligence = build_company_intelligence(
        job,
        candidate,
        match,
        package,
        recruiter_notes="Recruiter prefers concise context.",
    )

    assert job.title in intelligence.recruiter_message_draft
    assert job.company in intelligence.recruiter_message_draft
    assert str(match.score) in intelligence.recruiter_message_draft
    assert "concise context" in intelligence.recruiter_message_draft


def test_interview_questions_generation() -> None:
    candidate, job, match, package = _context()

    intelligence = build_company_intelligence(job, candidate, match, package)

    assert len(intelligence.questions_to_ask) >= 3
    assert any("first 90 days" in question for question in intelligence.questions_to_ask)
    assert intelligence.interview_focus_areas


def test_risk_flags_for_weak_match() -> None:
    candidate, job, match, package = _context(candidate=_weak_candidate())

    intelligence = build_company_intelligence(job, candidate, match, package)

    assert any("Weak match score" in flag for flag in intelligence.risk_flags)
    assert any("stretch role" in action for action in intelligence.next_best_actions)


def test_no_private_data_leakage() -> None:
    candidate, job, match, package = _context()

    intelligence = build_company_intelligence(
        job,
        candidate,
        match,
        package,
        company_notes="Contact hr@example.com or see https://example.com/private.",
        recruiter_notes="Call +32 499 12 34 56 after review.",
    )

    serialized = json.dumps(intelligence.model_dump())
    assert "hr@example.com" not in serialized
    assert "https://example.com/private" not in serialized
    assert "+32 499 12 34 56" not in serialized


def _context(candidate: CandidateProfile | None = None):
    resolved_candidate = candidate or _candidate()
    job = _job()
    match = score_job_match(resolved_candidate, job)
    package = build_application_package(resolved_candidate, job, match)
    return resolved_candidate, job, match, package


def _candidate() -> CandidateProfile:
    return CandidateProfile(
        name="Alex Demo",
        headline="Automation specialist",
        location="Remote",
        summary="Builds automation and analytics systems with 6 years of experience.",
        target_roles=["AI Product Operations Lead"],
        skills=["Python", "SQL", "Kubernetes", "workflow automation"],
        experience_highlights=[
            "Delivered Python analytics for operations teams.",
            "Built SQL reporting for product operations.",
            "Operated Kubernetes services for internal automation tools.",
        ],
    )


def _weak_candidate() -> CandidateProfile:
    return CandidateProfile(
        name="Casey Demo",
        headline="Customer success coordinator",
        location="Remote",
        summary="Coordinates onboarding documentation.",
        target_roles=["Customer Success Manager"],
        skills=["documentation"],
        experience_highlights=["Maintained onboarding documentation."],
    )


def _job() -> JobDescription:
    return JobDescription(
        title="AI Product Operations Lead",
        company="ExampleTech",
        description=(
            "Lead Python, SQL, workflow automation, and Kubernetes delivery "
            "for internal business teams."
        ),
        required_skills=["Python", "SQL", "Kubernetes"],
        nice_to_have_skills=["GraphQL", "workflow automation"],
    )
