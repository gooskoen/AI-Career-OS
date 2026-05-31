# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from app.matching import score_job_match
from app.schemas import CandidateProfile, JobDescription


def test_strong_match_has_ranked_strengths_and_explanation() -> None:
    result = score_job_match(_strong_candidate(), _core_job())

    assert result.score >= 75
    assert result.score == result.score_breakdown["overall"]
    assert set(result.matched_skills).issuperset(
        {"Python", "SQL", "Kubernetes", "workflow automation"}
    )
    assert result.strengths[0].contribution >= result.strengths[-1].contribution
    assert result.strengths[0].reason == "Matches a required skill."
    assert result.strengths[0].evidence
    assert result.gaps.critical == []
    assert result.explanation is not None
    assert "Strong match" in result.explanation.reasoning_summary


def test_moderate_match_keeps_required_skills_weighted() -> None:
    result = score_job_match(_moderate_candidate(), _core_job())

    assert 50 <= result.score < 75
    assert "Kubernetes" in result.gaps.critical
    assert "Kubernetes" in result.missing_skills
    assert result.score_breakdown["required"] == 67
    assert any("Kubernetes" in action for action in result.recommended_actions)
    assert any("Missing required skills" in item for item in result.explanation.penalties)


def test_weak_match_has_low_score_and_stretch_action() -> None:
    result = score_job_match(_weak_candidate(), _core_job())

    assert result.score < 50
    assert set(result.gaps.critical).issuperset({"Python", "SQL", "Kubernetes"})
    assert result.recommended_actions[-1] == (
        "Treat this as a stretch role unless the gaps can be closed."
    )
    assert result.explanation is not None
    assert "Weak match" in result.explanation.reasoning_summary


def test_missing_critical_skill_has_actionable_recommendation() -> None:
    result = score_job_match(_moderate_candidate(), _core_job())

    assert result.gaps.critical[0] == "Kubernetes"
    assert result.recommended_actions[0] == (
        "Add a project or CV bullet that demonstrates Kubernetes."
    )
    assert any("Missing required skills" in item for item in result.explanation.penalties)


def test_excessive_nice_to_have_mismatch_does_not_dominate_score() -> None:
    job = JobDescription(
        title="AI Product Operations Lead",
        company="ExampleTech",
        description="Lead Python, SQL, workflow automation, and operations delivery.",
        required_skills=["Python", "SQL", "workflow automation"],
        nice_to_have_skills=[
            "GraphQL",
            "Terraform",
            "Snowflake",
            "dbt",
            "Kubernetes",
        ],
    )

    result = score_job_match(_strong_candidate(), job)

    assert result.score >= 75
    assert result.score_breakdown["nice_to_have"] < 50
    assert len(result.gaps.optional) >= 3
    assert any("Several nice-to-have skills" in item for item in result.explanation.penalties)


def test_experience_gap_is_penalized_and_explained() -> None:
    job = JobDescription(
        title="Senior Automation Lead",
        company="ExampleTech",
        description="Requires 8 years of automation delivery experience.",
        required_skills=["Python", "SQL", "workflow automation"],
        nice_to_have_skills=[],
    )

    result = score_job_match(_moderate_candidate(), job)

    assert result.score_breakdown["experience_penalty"] > 0
    assert any("experience gap" in item for item in result.gaps.critical)
    assert any("Experience penalty" in item for item in result.explanation.penalties)


def _strong_candidate() -> CandidateProfile:
    return CandidateProfile(
        name="Alex Demo",
        headline="Automation specialist",
        location="Remote",
        summary="Builds analytics and workflow automation systems with 6 years of experience.",
        target_roles=["AI Product Operations Lead"],
        skills=["Python", "SQL", "Kubernetes", "GraphQL", "workflow automation"],
        experience_highlights=[
            "Delivered Python analytics for operations teams.",
            "Built SQL reporting for product operations.",
            "Operated Kubernetes services for internal automation tools.",
            "Led workflow automation projects across support and sales teams.",
        ],
    )


def _moderate_candidate() -> CandidateProfile:
    return CandidateProfile(
        name="Blair Demo",
        headline="Operations analyst",
        location="Remote",
        summary="Builds workflow automation and reporting with 4 years of experience.",
        target_roles=["AI Product Operations Lead"],
        skills=["Python", "SQL", "workflow automation"],
        experience_highlights=[
            "Built Python automations for operations workflows.",
            "Created SQL dashboards for product teams.",
        ],
    )


def _weak_candidate() -> CandidateProfile:
    return CandidateProfile(
        name="Casey Demo",
        headline="Customer success coordinator",
        location="Remote",
        summary="Coordinates customer onboarding and support documentation.",
        target_roles=["Customer Success Manager"],
        skills=["customer onboarding", "documentation"],
        experience_highlights=[
            "Maintained onboarding documentation for support teams.",
        ],
    )


def _core_job() -> JobDescription:
    return JobDescription(
        title="AI Product Operations Lead",
        company="ExampleTech",
        description=(
            "Lead Python, SQL, workflow automation, Kubernetes, and GraphQL work. "
            "Requires 5 years of operations automation experience."
        ),
        required_skills=["Python", "SQL", "Kubernetes"],
        nice_to_have_skills=["GraphQL", "workflow automation"],
    )
