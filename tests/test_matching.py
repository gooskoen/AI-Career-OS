# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from app.matching import score_job_match
from app.schemas import CandidateProfile, JobDescription


def test_match_score_has_structured_breakdown() -> None:
    result = score_job_match(_candidate(), _job())

    assert 0 <= result.score <= 100
    assert result.score == result.score_breakdown["overall"]
    assert set(result.score_breakdown) == {
        "overall",
        "keyword",
        "required",
        "nice_to_have",
    }


def test_match_strengths_include_candidate_skills() -> None:
    result = score_job_match(_candidate(), _job())

    assert "Python" in result.strengths
    assert "SQL" in result.strengths
    assert "workflow automation" in result.strengths


def test_match_gaps_prioritize_required_terms() -> None:
    result = score_job_match(_candidate(), _job())

    assert "kubernetes" in result.gaps
    assert result.gaps.index("kubernetes") < result.gaps.index("graphql")


def test_match_recommendations_are_deterministic() -> None:
    result = score_job_match(_candidate(), _job())

    assert result.recommended_actions
    assert result.recommended_actions[0].startswith("Address top missing keywords:")


def _candidate() -> CandidateProfile:
    return CandidateProfile(
        name="Alex Demo",
        headline="Automation specialist",
        location="Remote",
        summary="Builds analytics and workflow automation systems.",
        target_roles=["AI Product Operations Lead"],
        skills=["Python", "SQL", "workflow automation", "analytics"],
        experience_highlights=[
            "Delivered Python and SQL analytics for operations teams.",
            "Built workflow automation for product operations.",
        ],
    )


def _job() -> JobDescription:
    return JobDescription(
        title="AI Product Operations Lead",
        company="ExampleTech",
        description=(
            "Lead Python, SQL, workflow automation, Kubernetes, and GraphQL work."
        ),
        required_skills=["Python", "SQL", "Kubernetes"],
        nice_to_have_skills=["GraphQL", "workflow automation"],
    )
