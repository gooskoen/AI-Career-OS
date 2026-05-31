# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import uuid4

from app.feedback import (
    OutcomeRequest,
    build_candidate_insights,
    build_outcome_history,
    conversion_metrics,
    sanitize_notes,
)


def test_outcome_creation_model_sanitizes_notes() -> None:
    outcome = OutcomeRequest(
        candidate_id=uuid4(),
        job_id=uuid4(),
        application_id=uuid4(),
        outcome="applied",
        notes="Applied via portal. Contact alex@example.com or +32 499 12 34 56.",
        cv_edits_applied=True,
        cover_letter_used=True,
        skills=["Python", "SQL"],
        job_family="AI Operations",
    )

    assert outcome.outcome == "applied"
    sanitized = sanitize_notes(outcome.notes)
    assert "alex@example.com" not in sanitized
    assert "+32 499 12 34 56" not in sanitized


def test_outcome_transitions_timeline_and_counts() -> None:
    candidate_id = uuid4()
    application_id = uuid4()
    rows = [
        _row(candidate_id, application_id, "applied"),
        _row(candidate_id, application_id, "recruiter_replied"),
        _row(candidate_id, application_id, "interview_scheduled"),
    ]

    history = build_outcome_history(rows)

    assert [item["outcome"] for item in history["timeline"]] == [
        "applied",
        "recruiter_replied",
        "interview_scheduled",
    ]
    assert history["counts"]["applied"] == 1
    assert history["counts"]["recruiter_replied"] == 1
    assert history["counts"]["interview_scheduled"] == 1


def test_analytics_calculations() -> None:
    candidate_id = uuid4()
    rows = [
        _row(candidate_id, uuid4(), "applied"),
        _row(candidate_id, uuid4(), "applied"),
        _row(candidate_id, uuid4(), "recruiter_replied"),
        _row(candidate_id, uuid4(), "interview_scheduled"),
        _row(candidate_id, uuid4(), "interview_completed"),
        _row(candidate_id, uuid4(), "offer_received"),
        _row(candidate_id, uuid4(), "hired"),
    ]

    metrics = conversion_metrics(rows)

    assert metrics["application_to_reply_rate"] == 0.5
    assert metrics["reply_to_interview_rate"] == 1.0
    assert metrics["interview_to_offer_rate"] == 1.0
    assert metrics["offer_to_hire_rate"] == 1.0


def test_insight_generation() -> None:
    candidate_id = uuid4()
    rows = [
        _row(
            candidate_id,
            uuid4(),
            "interview_scheduled",
            skills=["Python", "workflow automation"],
            job_family="AI Operations",
            interview_prep_used=True,
        ),
        _row(
            candidate_id,
            uuid4(),
            "offer_received",
            skills=["Python", "SQL"],
            job_family="AI Operations",
            cv_edits_applied=True,
            cover_letter_used=True,
        ),
        _row(
            candidate_id,
            uuid4(),
            "rejected",
            notes="Rejected for seniority and missing skill depth.",
        ),
    ]

    insights = build_candidate_insights(rows)

    assert insights["strongest_performing_skills"][0] == "Python"
    assert insights["most_successful_job_families"] == ["AI Operations"]
    assert "seniority mismatch" in insights["most_common_rejection_reasons"]
    assert insights["recommended_focus_areas"]
    assert insights["improvement_opportunities"]


def test_privacy_protections_in_history() -> None:
    candidate_id = uuid4()
    rows = [
        _row(
            candidate_id,
            uuid4(),
            "recruiter_replied",
            notes="Recruiter emailed alex@example.com and shared https://example.com/private.",
        )
    ]

    history = build_outcome_history(rows)
    notes = history["timeline"][0]["notes"]

    assert "alex@example.com" not in notes
    assert "https://example.com/private" not in notes


def _row(
    candidate_id,
    application_id,
    outcome: str,
    notes: str = "",
    skills: list[str] | None = None,
    job_family: str | None = None,
    cv_edits_applied: bool = False,
    cover_letter_used: bool = False,
    interview_prep_used: bool = False,
) -> dict:
    return {
        "id": uuid4(),
        "candidate_id": candidate_id,
        "job_id": uuid4(),
        "application_id": application_id,
        "outcome": outcome,
        "notes": notes,
        "cv_edits_applied": cv_edits_applied,
        "cover_letter_used": cover_letter_used,
        "interview_prep_used": interview_prep_used,
        "skills": skills or [],
        "job_family": job_family,
        "created_at": None,
    }
