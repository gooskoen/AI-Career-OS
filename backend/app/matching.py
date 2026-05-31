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


class SkillStrength(BaseModel):
    skill: str
    contribution: int
    reason: str
    evidence: list[str] = Field(default_factory=list)


class GapAnalysis(BaseModel):
    critical: list[str] = Field(default_factory=list)
    moderate: list[str] = Field(default_factory=list)
    optional: list[str] = Field(default_factory=list)


class MatchExplanation(BaseModel):
    score_breakdown: dict[str, int]
    matched_skills: list[str]
    missing_skills: list[str]
    reasoning_summary: str
    penalties: list[str] = Field(default_factory=list)


class MatchResult(BaseModel):
    score: int = Field(ge=0, le=100)
    score_breakdown: dict[str, int] = Field(default_factory=dict)
    matched_keywords: list[str]
    missing_keywords: list[str]
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    strengths: list[SkillStrength] = Field(default_factory=list)
    gaps: GapAnalysis = Field(default_factory=GapAnalysis)
    recommended_actions: list[str] = Field(default_factory=list)
    explanation: MatchExplanation | None = None
    candidate_highlights: list[str]
    recommendation: str


def normalize_keywords(text: str) -> list[str]:
    """Extract stable lowercase keywords from free text."""

    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", text.lower())
    return sorted({word for word in words if word not in STOP_WORDS})


def score_job_match(candidate: CandidateProfile, job: JobDescription) -> MatchResult:
    candidate_terms = _candidate_terms(candidate)
    job_terms = _job_terms(job)
    required_skills = _normalized_skill_list(job.required_skills)
    nice_to_have_skills = _normalized_skill_list(job.nice_to_have_skills)

    matched = sorted(candidate_terms.intersection(job_terms))
    missing = sorted(job_terms.difference(candidate_terms))
    matched_required = _matched_skills(candidate_terms, required_skills)
    matched_nice_to_have = _matched_skills(candidate_terms, nice_to_have_skills)
    missing_required = _missing_skills(candidate_terms, required_skills)
    missing_nice_to_have = _missing_skills(candidate_terms, nice_to_have_skills)
    experience = _experience_signal(candidate, job)

    score_breakdown = _score_breakdown(
        candidate_terms,
        job_terms,
        required_skills,
        nice_to_have_skills,
        experience,
    )
    score = score_breakdown["overall"]
    recommendation = _recommendation(score)
    gaps = _gaps(missing_required, missing_nice_to_have, experience)
    matched_skills = sorted({*matched_required, *matched_nice_to_have})
    missing_skills = sorted({*missing_required, *missing_nice_to_have})
    penalties = _penalties(experience, missing_required, missing_nice_to_have)
    strengths = _strengths(candidate, matched_required, matched_nice_to_have)

    return MatchResult(
        score=score,
        score_breakdown=score_breakdown,
        matched_keywords=matched,
        missing_keywords=missing,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        strengths=strengths,
        gaps=gaps,
        recommended_actions=_recommended_actions(gaps, score),
        explanation=MatchExplanation(
            score_breakdown=score_breakdown,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            reasoning_summary=_reasoning_summary(score, strengths, gaps, penalties),
            penalties=penalties,
        ),
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
    required_skills: list[tuple[str, set[str]]],
    nice_to_have_skills: list[tuple[str, set[str]]],
    experience: dict[str, int | None],
) -> dict[str, int]:
    keyword_score = _coverage_score(candidate_terms, job_terms)
    required_score = _skill_coverage_score(candidate_terms, required_skills)
    nice_to_have_score = _skill_coverage_score(candidate_terms, nice_to_have_skills)
    experience_score = _experience_score(experience)
    weighted_scores = [
        (keyword_score, 15, bool(job_terms)),
        (required_score, 60, bool(required_skills)),
        (nice_to_have_score, 15, bool(nice_to_have_skills)),
        (experience_score, 10, experience["required_years"] is not None),
    ]
    active_weight = sum(weight for _, weight, active in weighted_scores if active)
    overall = 0
    if active_weight:
        overall = round(
            sum(score * weight for score, weight, active in weighted_scores if active)
            / active_weight
        )
    return {
        "overall": overall,
        "keyword": keyword_score,
        "required": required_score,
        "nice_to_have": nice_to_have_score,
        "experience": experience_score,
        "experience_penalty": max(0, 100 - experience_score),
        "required_years": experience["required_years"] or 0,
        "candidate_years": experience["candidate_years"] or 0,
    }


def _coverage_score(candidate_terms: set[str], target_terms: set[str]) -> int:
    if not target_terms:
        return 0
    return round(
        (len(candidate_terms.intersection(target_terms)) / len(target_terms)) * 100
    )


def _skill_coverage_score(
    candidate_terms: set[str],
    skills: list[tuple[str, set[str]]],
) -> int:
    if not skills:
        return 0
    matched = _matched_skills(candidate_terms, skills)
    return round((len(matched) / len(skills)) * 100)


def _normalized_skill_list(skills: list[str]) -> list[tuple[str, set[str]]]:
    normalized = []
    for skill in skills:
        terms = set(normalize_keywords(skill))
        if terms:
            normalized.append((skill, terms))
    return normalized


def _matched_skills(
    candidate_terms: set[str],
    skills: list[tuple[str, set[str]]],
) -> list[str]:
    return [
        skill
        for skill, skill_terms in skills
        if skill_terms and skill_terms.issubset(candidate_terms)
    ]


def _missing_skills(
    candidate_terms: set[str],
    skills: list[tuple[str, set[str]]],
) -> list[str]:
    return [
        skill
        for skill, skill_terms in skills
        if skill_terms and not skill_terms.issubset(candidate_terms)
    ]


def _strengths(
    candidate: CandidateProfile,
    matched_required: list[str],
    matched_nice_to_have: list[str],
) -> list[SkillStrength]:
    ranked = [
        SkillStrength(
            skill=skill,
            contribution=60,
            reason="Matches a required skill.",
            evidence=_evidence_for_skill(candidate, skill),
        )
        for skill in matched_required
    ]
    ranked.extend(
        SkillStrength(
            skill=skill,
            contribution=15,
            reason="Matches a nice-to-have skill.",
            evidence=_evidence_for_skill(candidate, skill),
        )
        for skill in matched_nice_to_have
        if skill not in matched_required
    )
    return sorted(ranked, key=lambda item: (-item.contribution, item.skill.lower()))[:5]


def _evidence_for_skill(candidate: CandidateProfile, skill: str) -> list[str]:
    skill_terms = set(normalize_keywords(skill))
    evidence = [
        item
        for item in candidate.experience_highlights
        if skill_terms.issubset(set(normalize_keywords(item)))
    ]
    if not evidence and skill in candidate.skills:
        evidence.append(f"Listed skill: {skill}")
    return evidence[:2]


def _gaps(
    missing_required: list[str],
    missing_nice_to_have: list[str],
    experience: dict[str, int | None],
) -> GapAnalysis:
    critical = list(missing_required)
    if _experience_gap(experience) >= 3:
        critical.append(_experience_gap_label(experience))

    moderate = []
    if 1 <= _experience_gap(experience) < 3:
        moderate.append(_experience_gap_label(experience))

    return GapAnalysis(
        critical=critical[:6],
        moderate=moderate[:4],
        optional=missing_nice_to_have[:6],
    )


def _recommended_actions(gaps: GapAnalysis, score: int) -> list[str]:
    actions = []
    for skill in gaps.critical[:3]:
        actions.append(_action_for_gap(skill, "CV bullet"))
    for skill in gaps.moderate[:2]:
        actions.append(_action_for_gap(skill, "interview example"))
    for skill in gaps.optional[:2]:
        actions.append(f"Add a concise side project or learning note for {skill}.")
    if score < 75:
        actions.append("Tailor the profile summary to the highest-weight job skills.")
    if score < 50:
        actions.append("Treat this as a stretch role unless the gaps can be closed.")
    if not actions:
        actions.append("Apply with a concise, role-specific summary.")
    return actions


def _action_for_gap(gap: str, artifact: str) -> str:
    if "experience gap" in gap:
        return (
            f"Prepare a {artifact} that shows ownership, scope, and outcomes "
            f"to reduce the {gap}."
        )
    return f"Add a project or {artifact} that demonstrates {gap}."


def _experience_signal(
    candidate: CandidateProfile,
    job: JobDescription,
) -> dict[str, int | None]:
    candidate_years = _max_years(
        " ".join([candidate.summary, *candidate.experience_highlights])
    )
    required_years = _max_years(" ".join([job.description, *job.required_skills]))
    return {
        "candidate_years": candidate_years,
        "required_years": required_years,
    }


def _max_years(text: str) -> int | None:
    matches = re.findall(r"(\d{1,2})\+?\s*(?:years?|yrs?)", text.lower())
    if not matches:
        return None
    return max(int(match) for match in matches)


def _experience_score(experience: dict[str, int | None]) -> int:
    gap = _experience_gap(experience)
    if experience["required_years"] is None:
        return 0
    if gap <= 0:
        return 100
    if gap == 1:
        return 75
    if gap == 2:
        return 55
    return max(10, 55 - ((gap - 2) * 15))


def _experience_gap(experience: dict[str, int | None]) -> int:
    required_years = experience["required_years"]
    candidate_years = experience["candidate_years"]
    if required_years is None:
        return 0
    return max(0, required_years - (candidate_years or 0))


def _experience_gap_label(experience: dict[str, int | None]) -> str:
    return (
        f"{_experience_gap(experience)} year experience gap "
        f"against {experience['required_years']} required years"
    )


def _penalties(
    experience: dict[str, int | None],
    missing_required: list[str],
    missing_nice_to_have: list[str],
) -> list[str]:
    penalties = []
    gap = _experience_gap(experience)
    if gap:
        penalties.append(
            f"Experience penalty: candidate shows "
            f"{experience['candidate_years'] or 0} years against "
            f"{experience['required_years']} requested years."
        )
    if missing_required:
        penalties.append(
            f"Missing required skills carry high weight: {', '.join(missing_required)}."
        )
    if len(missing_nice_to_have) >= 3:
        penalties.append(
            f"Several nice-to-have skills are missing: {', '.join(missing_nice_to_have[:5])}."
        )
    return penalties


def _reasoning_summary(
    score: int,
    strengths: list[SkillStrength],
    gaps: GapAnalysis,
    penalties: list[str],
) -> str:
    if score >= 75:
        fit = "Strong match"
    elif score >= 50:
        fit = "Moderate match"
    else:
        fit = "Weak match"

    strength_text = ", ".join(strength.skill for strength in strengths[:3]) or "limited direct matches"
    gap_count = len(gaps.critical) + len(gaps.moderate) + len(gaps.optional)
    penalty_text = " Penalties applied." if penalties else ""
    return f"{fit}: strongest evidence is {strength_text}; {gap_count} gaps found.{penalty_text}"


def _recommendation(score: int) -> str:
    if score >= 75:
        return "Strong match: tailor the application around the shared keywords."
    if score >= 50:
        return "Moderate match: address the missing keywords before applying."
    return "Early match: use this role for gap analysis or learning goals."
