# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from app.matching import MatchResult, normalize_keywords
from app.schemas import CandidateProfile, JobDescription


def build_interview_briefing(
    candidate: CandidateProfile,
    job: JobDescription,
    match: MatchResult,
) -> dict:
    """Create a deterministic interview briefing from candidate and job data."""

    candidate_strengths = [
        skill for skill in candidate.skills if skill.lower() in match.matched_keywords
    ]
    focus_areas = match.missing_keywords[:5]
    company_themes = normalize_keywords(job.description)[:6]

    return {
        "candidate_name": candidate.name,
        "target_role": job.title,
        "company": job.company,
        "match_score": match.score,
        "positioning_statement": (
            f"{candidate.name} should position their background in "
            f"{', '.join(candidate_strengths[:3]) or 'relevant delivery experience'} "
            f"against the needs of the {job.title} role."
        ),
        "strengths_to_emphasize": candidate_strengths[:6],
        "gaps_to_prepare": focus_areas,
        "likely_interview_topics": [
            f"How your experience maps to {keyword}" for keyword in company_themes[:4]
        ],
        "questions_to_ask": [
            "What outcomes would define success in the first 90 days?",
            "Which teams would this role partner with most often?",
            "Where are the biggest execution risks for this role today?",
        ],
        "notes": "Demo briefing generated from mock data only.",
    }
