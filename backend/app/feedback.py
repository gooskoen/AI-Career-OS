# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import re
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

OUTCOMES = (
    "applied",
    "recruiter_replied",
    "interview_scheduled",
    "interview_completed",
    "rejected",
    "offer_received",
    "hired",
    "withdrawn",
)

POSITIVE_OUTCOMES = {
    "recruiter_replied",
    "interview_scheduled",
    "interview_completed",
    "offer_received",
    "hired",
}

ApplicationOutcome = Literal[
    "applied",
    "recruiter_replied",
    "interview_scheduled",
    "interview_completed",
    "rejected",
    "offer_received",
    "hired",
    "withdrawn",
]


class OutcomeRequest(BaseModel):
    candidate_id: UUID
    job_id: UUID
    application_id: UUID
    outcome: ApplicationOutcome
    notes: str = Field(default="", max_length=5_000)
    cv_edits_applied: bool = False
    cover_letter_used: bool = False
    interview_prep_used: bool = False
    skills: list[str] = Field(default_factory=list, max_length=50)
    job_family: str | None = Field(default=None, max_length=200)


def sanitize_notes(notes: str) -> str:
    redacted = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[redacted]", notes)
    redacted = re.sub(r"https?://\S+", "[redacted]", redacted)
    redacted = re.sub(r"\+?\d[\d\s().-]{7,}\d", "[redacted]", redacted)
    return " ".join(redacted.split())


def outcome_timeline(rows: list[dict]) -> list[dict]:
    return [
        {
            "id": row.get("id"),
            "candidate_id": row["candidate_id"],
            "job_id": row["job_id"],
            "application_id": row["application_id"],
            "outcome": row["outcome"],
            "notes": sanitize_notes(row.get("notes") or ""),
            "cv_edits_applied": bool(row.get("cv_edits_applied")),
            "cover_letter_used": bool(row.get("cover_letter_used")),
            "interview_prep_used": bool(row.get("interview_prep_used")),
            "skills": row.get("skills") or [],
            "job_family": row.get("job_family"),
            "created_at": row.get("created_at"),
        }
        for row in rows
    ]


def outcome_counts(rows: list[dict]) -> dict[str, int]:
    counts = {outcome: 0 for outcome in OUTCOMES}
    for row in rows:
        outcome = row["outcome"]
        if outcome in counts:
            counts[outcome] += 1
    return counts


def conversion_metrics(rows: list[dict]) -> dict[str, float]:
    counts = outcome_counts(rows)
    return {
        "application_to_reply_rate": _rate(
            counts["recruiter_replied"],
            counts["applied"],
        ),
        "reply_to_interview_rate": _rate(
            counts["interview_scheduled"],
            counts["recruiter_replied"],
        ),
        "interview_to_offer_rate": _rate(
            counts["offer_received"],
            counts["interview_completed"],
        ),
        "offer_to_hire_rate": _rate(
            counts["hired"],
            counts["offer_received"],
        ),
    }


def build_outcome_history(rows: list[dict]) -> dict:
    timeline = outcome_timeline(rows)
    return {
        "timeline": timeline,
        "counts": outcome_counts(timeline),
        "conversion_metrics": conversion_metrics(timeline),
    }


def build_candidate_insights(rows: list[dict]) -> dict:
    timeline = outcome_timeline(rows)
    positive_rows = [row for row in timeline if row["outcome"] in POSITIVE_OUTCOMES]
    rejected_rows = [row for row in timeline if row["outcome"] == "rejected"]

    strongest_skills = _top_values(
        skill for row in positive_rows for skill in row["skills"]
    )
    successful_job_families = _top_values(
        row["job_family"] for row in positive_rows if row.get("job_family")
    )
    rejection_reasons = _rejection_reasons(rejected_rows)
    improvement_opportunities = _improvement_opportunities(timeline)

    return {
        "strongest_performing_skills": strongest_skills,
        "most_common_rejection_reasons": rejection_reasons,
        "most_successful_job_families": successful_job_families,
        "recommended_focus_areas": _recommended_focus_areas(
            strongest_skills,
            rejection_reasons,
            improvement_opportunities,
        ),
        "improvement_opportunities": improvement_opportunities,
    }


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 2)


def _top_values(values) -> list[str]:
    counts: dict[str, int] = {}
    for value in values:
        if not value:
            continue
        counts[str(value)] = counts.get(str(value), 0) + 1
    return [
        value
        for value, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ][:5]


def _rejection_reasons(rows: list[dict]) -> list[str]:
    reasons = []
    keywords = {
        "experience": "experience gap",
        "salary": "salary mismatch",
        "location": "location mismatch",
        "skill": "skill gap",
        "senior": "seniority mismatch",
        "culture": "culture fit",
    }
    for row in rows:
        notes = (row.get("notes") or "").lower()
        for keyword, reason in keywords.items():
            if keyword in notes:
                reasons.append(reason)
    return _top_values(reasons)


def _improvement_opportunities(rows: list[dict]) -> list[str]:
    opportunities = []
    if any(not row["cv_edits_applied"] for row in rows):
        opportunities.append("Apply recommended CV edits before more submissions.")
    if any(not row["cover_letter_used"] for row in rows):
        opportunities.append("Use the tailored cover letter for comparable roles.")
    if any(
        row["outcome"] in {"interview_scheduled", "interview_completed"}
        and not row["interview_prep_used"]
        for row in rows
    ):
        opportunities.append("Use interview preparation before scheduled interviews.")
    if any(row["outcome"] == "rejected" for row in rows):
        opportunities.append("Review rejection notes and address repeated gaps.")
    return opportunities[:5]


def _recommended_focus_areas(
    skills: list[str],
    rejection_reasons: list[str],
    opportunities: list[str],
) -> list[str]:
    focus = []
    if skills:
        focus.append(f"Double down on roles using {', '.join(skills[:3])}.")
    if rejection_reasons:
        focus.append(f"Reduce repeated rejection driver: {rejection_reasons[0]}.")
    focus.extend(opportunities[:2])
    if not focus:
        focus.append("Track more outcomes before changing strategy.")
    return focus[:5]
