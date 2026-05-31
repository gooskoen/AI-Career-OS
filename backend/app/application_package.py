# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from app.matching import MatchResult
from app.schemas import CandidateProfile, JobDescription


class ApplicationPackageRequest(BaseModel):
    candidate: CandidateProfile
    job: JobDescription
    match_result: MatchResult


class ApplicationPackage(BaseModel):
    tailored_summary: str
    cover_letter: str
    talking_points: list[str] = Field(default_factory=list)
    key_strengths: list[str] = Field(default_factory=list)
    risk_gaps: list[str] = Field(default_factory=list)
    recommended_cv_edits: list[str] = Field(default_factory=list)


def build_application_package(
    candidate: CandidateProfile,
    job: JobDescription,
    match: MatchResult,
) -> ApplicationPackage:
    """Create deterministic application materials from existing match analysis."""

    strengths = _key_strengths(match)
    gaps = _risk_gaps(match)
    warning = _weak_match_warning(match.score)

    tailored_summary = _clean(
        (
            f"{candidate.name} is positioned for the {job.title} role at "
            f"{job.company} through {', '.join(strengths[:3]) or 'relevant delivery experience'}. "
            f"Focus the CV summary on {', '.join(match.matched_skills[:4]) or 'the closest role requirements'}."
        )
    )

    cover_letter = _clean(
        (
            f"Dear {job.company} hiring team,\n\n"
            f"I am interested in the {job.title} role because it aligns with "
            f"{', '.join(strengths[:3]) or 'my relevant operating experience'}. "
            f"My strongest evidence is { _evidence_sentence(match) }. "
            f"{_gap_sentence(gaps)}\n\n"
            f"{warning}"
            f"Thank you for considering my application."
        )
    )

    return ApplicationPackage(
        tailored_summary=tailored_summary,
        cover_letter=cover_letter,
        talking_points=_talking_points(job, match, warning),
        key_strengths=strengths,
        risk_gaps=gaps,
        recommended_cv_edits=_recommended_cv_edits(match, gaps),
    )


def _key_strengths(match: MatchResult) -> list[str]:
    if match.strengths:
        return [_clean(strength.skill) for strength in match.strengths[:5]]
    return [_clean(skill) for skill in match.matched_skills[:5]]


def _risk_gaps(match: MatchResult) -> list[str]:
    return [
        _clean(gap)
        for gap in [
            *match.gaps.critical,
            *match.gaps.moderate,
            *match.gaps.optional,
        ][:6]
    ]


def _evidence_sentence(match: MatchResult) -> str:
    evidence = []
    for strength in match.strengths:
        evidence.extend(strength.evidence)
    if evidence:
        return _clean(evidence[0])
    if match.candidate_highlights:
        return _clean(match.candidate_highlights[0])
    return "the overlap between my background and the role requirements"


def _gap_sentence(gaps: list[str]) -> str:
    if not gaps:
        return "The current match profile shows no critical gaps to lead with."
    return f"I would proactively address {', '.join(gaps[:2])} with concrete examples."


def _weak_match_warning(score: int) -> str:
    if score >= 50:
        return ""
    return (
        "This is currently a stretch application, so the package should clearly "
        "explain transferable evidence and the plan to close gaps. "
    )


def _talking_points(
    job: JobDescription,
    match: MatchResult,
    warning: str,
) -> list[str]:
    points = [
        _clean(f"Connect prior work to {skill}.")
        for skill in match.matched_skills[:4]
    ]
    points.extend(
        _clean(f"Prepare a specific story for the gap: {gap}.")
        for gap in [*match.gaps.critical, *match.gaps.moderate][:3]
    )
    if warning:
        points.append("Frame this as a stretch role with a concrete learning plan.")
    if not points:
        points.append(_clean(f"Explain motivation for the {job.title} role."))
    return points[:7]


def _recommended_cv_edits(match: MatchResult, gaps: list[str]) -> list[str]:
    edits = [
        _clean(f"Add a CV bullet with measurable evidence for {skill}.")
        for skill in match.matched_skills[:3]
    ]
    edits.extend(
        _clean(f"Add a project or learning note that demonstrates {gap}.")
        for gap in gaps[:3]
    )
    if not edits:
        edits.append("Add one concise role-specific achievement to the CV summary.")
    return edits[:6]


def _clean(value: str) -> str:
    """Remove contact-style/private fragments from generated application text."""

    redacted = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[redacted]", value)
    redacted = re.sub(r"https?://\S+", "[redacted]", redacted)
    redacted = re.sub(r"\+?\d[\d\s().-]{7,}\d", "[redacted]", redacted)
    return " ".join(redacted.split())
