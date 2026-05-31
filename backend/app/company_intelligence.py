# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from app.application_package import ApplicationPackage
from app.matching import MatchResult, normalize_keywords
from app.schemas import CandidateProfile, JobDescription


class CompanyIntelligenceRequest(BaseModel):
    job: JobDescription
    candidate: CandidateProfile
    match_result: MatchResult
    application_package: ApplicationPackage
    company_notes: str | None = Field(default=None, max_length=5_000)
    recruiter_notes: str | None = Field(default=None, max_length=5_000)


class CompanyIntelligence(BaseModel):
    company_summary: str
    likely_business_needs: list[str] = Field(default_factory=list)
    interview_focus_areas: list[str] = Field(default_factory=list)
    questions_to_ask: list[str] = Field(default_factory=list)
    recruiter_message_draft: str
    salary_positioning_notes: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    next_best_actions: list[str] = Field(default_factory=list)


def build_company_intelligence(
    job: JobDescription,
    candidate: CandidateProfile,
    match: MatchResult,
    package: ApplicationPackage,
    company_notes: str | None = None,
    recruiter_notes: str | None = None,
) -> CompanyIntelligence:
    """Create deterministic company and recruiter preparation from supplied data."""

    themes = _themes(job, company_notes)
    risks = _risk_flags(match, job, company_notes)
    focus_areas = _interview_focus_areas(match, package, themes)

    return CompanyIntelligence(
        company_summary=_company_summary(job, company_notes, themes),
        likely_business_needs=_business_needs(job, themes),
        interview_focus_areas=focus_areas,
        questions_to_ask=_questions_to_ask(job, focus_areas, risks),
        recruiter_message_draft=_recruiter_message(
            job,
            candidate,
            match,
            package,
            recruiter_notes,
        ),
        salary_positioning_notes=_salary_positioning_notes(job, match),
        risk_flags=risks,
        next_best_actions=_next_best_actions(match, package, risks),
    )


def _company_summary(
    job: JobDescription,
    company_notes: str | None,
    themes: list[str],
) -> str:
    note_text = f" Notes mention {company_notes}." if company_notes else ""
    summary = (
        f"{job.company} is hiring for {job.title}. The available role text points to "
        f"{', '.join(themes[:4]) or 'the responsibilities in the job description'}."
        f"{note_text}"
    )
    return _clean(summary)


def _themes(job: JobDescription, company_notes: str | None) -> list[str]:
    source = " ".join(
        [
            job.title,
            job.description,
            " ".join(job.required_skills),
            " ".join(job.nice_to_have_skills),
            _clean(company_notes or ""),
        ]
    )
    keywords = normalize_keywords(source)
    preferred = [
        keyword
        for keyword in keywords
        if keyword
        not in {
            "company",
            "candidate",
            "description",
            "experience",
            "hiring",
            "redacted",
            "role",
            "team",
            "work",
        }
    ]
    return preferred[:8]


def _business_needs(job: JobDescription, themes: list[str]) -> list[str]:
    needs = [f"Deliver outcomes for {job.title}."]
    needs.extend(f"Reduce execution risk around {theme}." for theme in themes[:3])
    if job.required_skills:
        needs.append(f"Find evidence for required skills: {', '.join(job.required_skills[:3])}.")
    return [_clean(need) for need in needs[:5]]


def _interview_focus_areas(
    match: MatchResult,
    package: ApplicationPackage,
    themes: list[str],
) -> list[str]:
    focus = [
        f"Proof of strength: {strength}."
        for strength in package.key_strengths[:3]
    ]
    focus.extend(f"Risk/gap discussion: {gap}." for gap in package.risk_gaps[:3])
    focus.extend(f"Company context: {theme}." for theme in themes[:2])
    if match.score < 50:
        focus.append("Transferable experience and gap-closing plan.")
    return [_clean(item) for item in focus[:7]]


def _questions_to_ask(
    job: JobDescription,
    focus_areas: list[str],
    risks: list[str],
) -> list[str]:
    questions = [
        f"What outcomes would define success for the {job.title} role in the first 90 days?",
        "Which business problem is most urgent for this hire to solve?",
        "How will this role partner with hiring managers and delivery teams?",
    ]
    if focus_areas:
        questions.append(f"Where would {focus_areas[0].rstrip('.').lower()} matter most?")
    if risks:
        questions.append(f"How should a candidate best address {risks[0].lower()}?")
    return [_clean(question) for question in questions[:5]]


def _recruiter_message(
    job: JobDescription,
    candidate: CandidateProfile,
    match: MatchResult,
    package: ApplicationPackage,
    recruiter_notes: str | None,
) -> str:
    note = f" I noticed: {recruiter_notes}." if recruiter_notes else ""
    message = (
        f"Hello, I am exploring the {job.title} role at {job.company}. "
        f"My strongest fit is {', '.join(package.key_strengths[:3]) or candidate.headline}, "
        f"with a current match score of {match.score}. "
        f"I would value a short conversation about the team priorities and hiring process."
        f"{note}"
    )
    return _clean(message)


def _salary_positioning_notes(job: JobDescription, match: MatchResult) -> list[str]:
    notes = [
        "Use market research outside this app before naming a compensation range.",
        f"Anchor salary discussion on scope, seniority, and impact for {job.title}.",
    ]
    if match.score >= 75:
        notes.append("Strong match: position near the upper side of a researched range.")
    elif match.score >= 50:
        notes.append("Moderate match: position around the middle of a researched range.")
    else:
        notes.append("Weak match: prioritize learning opportunity and role fit before range.")
    return [_clean(note) for note in notes]


def _risk_flags(
    match: MatchResult,
    job: JobDescription,
    company_notes: str | None,
) -> list[str]:
    risks = []
    if match.score < 50:
        risks.append("Weak match score; prepare transferable evidence before outreach.")
    if match.gaps.critical:
        risks.append(f"Critical match gaps: {', '.join(match.gaps.critical[:3])}.")
    if not job.location:
        risks.append("Job location is not specified.")
    if company_notes and any(
        term in company_notes.lower()
        for term in ["layoff", "hiring freeze", "restructure", "turnover"]
    ):
        risks.append("Company notes mention possible stability or hiring risk.")
    return [_clean(risk) for risk in risks[:5]]


def _next_best_actions(
    match: MatchResult,
    package: ApplicationPackage,
    risks: list[str],
) -> list[str]:
    actions = [
        "Review company website and public materials manually before interview.",
        "Prepare one story for each top interview focus area.",
    ]
    actions.extend(package.recommended_cv_edits[:2])
    if risks:
        actions.append("Prepare a concise answer for the highest-priority risk flag.")
    if match.score < 50:
        actions.append("Decide whether this is worth pursuing as a stretch role.")
    return [_clean(action) for action in actions[:6]]


def _clean(value: str) -> str:
    redacted = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[redacted]", value)
    redacted = re.sub(r"https?://\S+", "[redacted]", redacted)
    redacted = re.sub(r"\+?\d[\d\s().-]{7,}\d", "[redacted]", redacted)
    return " ".join(redacted.split())
