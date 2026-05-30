# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from app.schemas import CandidateProfile, JobDescription

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


class MatchResult(BaseModel):
    score: int = Field(ge=0, le=100)
    matched_keywords: list[str]
    missing_keywords: list[str]
    candidate_highlights: list[str]
    recommendation: str


def normalize_keywords(text: str) -> list[str]:
    """Extract stable lowercase keywords from free text."""

    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", text.lower())
    return sorted({word for word in words if word not in STOP_WORDS})


def score_job_match(candidate: CandidateProfile, job: JobDescription) -> MatchResult:
    candidate_terms = _candidate_terms(candidate)
    job_terms = _job_terms(job)

    matched = sorted(candidate_terms.intersection(job_terms))
    missing = sorted(job_terms.difference(candidate_terms))

    score = round((len(matched) / max(len(job_terms), 1)) * 100)
    recommendation = _recommendation(score)

    return MatchResult(
        score=score,
        matched_keywords=matched,
        missing_keywords=missing,
        candidate_highlights=_candidate_highlights(candidate, matched),
        recommendation=recommendation,
    )


def _candidate_terms(candidate: CandidateProfile) -> set[str]:
    joined = " ".join(
        [
            *candidate.skills,
            *candidate.target_roles,
            *candidate.summary.split(),
            *candidate.experience_highlights,
        ]
    )
    return set(normalize_keywords(joined))


def _job_terms(job: JobDescription) -> set[str]:
    joined = " ".join(
        [
            job.title,
            job.description,
            *job.required_skills,
            *job.nice_to_have_skills,
        ]
    )
    return set(normalize_keywords(joined))


def _candidate_highlights(candidate: CandidateProfile, matched: list[str]) -> list[str]:
    highlights = []
    for item in candidate.experience_highlights:
        item_terms = set(normalize_keywords(item))
        if item_terms.intersection(matched):
            highlights.append(item)
    return highlights[:5]


def _recommendation(score: int) -> str:
    if score >= 75:
        return "Strong match: tailor the application around the shared keywords."
    if score >= 50:
        return "Moderate match: address the missing keywords before applying."
    return "Early match: use this role for gap analysis or learning goals."
