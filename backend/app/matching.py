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
    score_breakdown: dict[str, int] = Field(default_factory=dict)
    matched_keywords: list[str]
    missing_keywords: list[str]
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    candidate_highlights: list[str]
    recommendation: str


def normalize_keywords(text: str) -> list[str]:
    """Extract stable lowercase keywords from free text."""

    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", text.lower())
    return sorted({word for word in words if word not in STOP_WORDS})


def score_job_match(candidate: CandidateProfile, job: JobDescription) -> MatchResult:
    candidate_terms = _candidate_terms(candidate)
    job_terms = _job_terms(job)
    required_terms = set(normalize_keywords(" ".join(job.required_skills)))
    nice_to_have_terms = set(normalize_keywords(" ".join(job.nice_to_have_skills)))

    matched = sorted(candidate_terms.intersection(job_terms))
    missing = sorted(job_terms.difference(candidate_terms))

    score_breakdown = _score_breakdown(
        candidate_terms,
        job_terms,
        required_terms,
        nice_to_have_terms,
    )
    score = score_breakdown["overall"]
    recommendation = _recommendation(score)
    gaps = _gaps(missing, required_terms)

    return MatchResult(
        score=score,
        score_breakdown=score_breakdown,
        matched_keywords=matched,
        missing_keywords=missing,
        strengths=_strengths(candidate, matched),
        gaps=gaps,
        recommended_actions=_recommended_actions(gaps, score),
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


def _score_breakdown(
    candidate_terms: set[str],
    job_terms: set[str],
    required_terms: set[str],
    nice_to_have_terms: set[str],
) -> dict[str, int]:
    keyword_score = _coverage_score(candidate_terms, job_terms)
    required_score = _coverage_score(candidate_terms, required_terms)
    nice_to_have_score = _coverage_score(candidate_terms, nice_to_have_terms)
    overall = round(
        (keyword_score * 0.45)
        + (required_score * 0.45)
        + (nice_to_have_score * 0.10)
    )
    return {
        "overall": overall,
        "keyword": keyword_score,
        "required": required_score,
        "nice_to_have": nice_to_have_score,
    }


def _coverage_score(candidate_terms: set[str], target_terms: set[str]) -> int:
    if not target_terms:
        return 100
    return round(
        (len(candidate_terms.intersection(target_terms)) / len(target_terms)) * 100
    )


def _strengths(candidate: CandidateProfile, matched: list[str]) -> list[str]:
    matched_terms = set(matched)
    skill_strengths = []
    for skill in candidate.skills:
        skill_terms = set(normalize_keywords(skill))
        if skill_terms.intersection(matched_terms):
            skill_strengths.append(skill)
    if skill_strengths:
        return skill_strengths[:5]
    return matched[:5]


def _gaps(missing: list[str], required_terms: set[str]) -> list[str]:
    priority_gaps = [term for term in missing if term in required_terms]
    secondary_gaps = [term for term in missing if term not in required_terms]
    return [*priority_gaps, *secondary_gaps][:8]


def _recommended_actions(gaps: list[str], score: int) -> list[str]:
    actions = []
    if gaps:
        actions.append(f"Address top missing keywords: {', '.join(gaps[:5])}.")
    if score < 75:
        actions.append("Tailor the profile summary and recent highlights to the role.")
    if score < 50:
        actions.append("Treat this as a stretch role unless the gaps can be closed.")
    if not actions:
        actions.append("Apply with a concise, role-specific summary.")
    return actions


def _recommendation(score: int) -> str:
    if score >= 75:
        return "Strong match: tailor the application around the shared keywords."
    if score >= 50:
        return "Moderate match: address the missing keywords before applying."
    return "Early match: use this role for gap analysis or learning goals."
