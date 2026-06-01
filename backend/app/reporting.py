# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, Field

from app.application_domain import APPLICATION_STATUSES
from app.feedback import POSITIVE_OUTCOMES, build_candidate_insights

TimeWindow = Literal["last_30_days", "last_90_days", "last_year", "all_time"]

TERMINAL_STATUSES = {"hired", "rejected", "withdrawn"}
FUNNEL_STAGES = (
    "applied",
    "recruiter_replied",
    "interview_scheduled",
    "interview_completed",
    "offer_received",
    "hired",
)
SUCCESS_OUTCOMES = {"offer_received", "hired"}


class DashboardReportResponse(BaseModel):
    active_applications: int = Field(ge=0)
    interviews_scheduled: int = Field(ge=0)
    offers_received: int = Field(ge=0)
    hires: int = Field(ge=0)
    rejections: int = Field(ge=0)
    pipeline_totals: dict[str, int]


class FunnelReportResponse(BaseModel):
    applications: int = Field(ge=0)
    recruiter_replies: int = Field(ge=0)
    interviews: int = Field(ge=0)
    offers: int = Field(ge=0)
    hires: int = Field(ge=0)
    application_to_reply_rate: float
    reply_to_interview_rate: float
    interview_to_offer_rate: float
    offer_to_hire_rate: float


class ApplicationReportResponse(BaseModel):
    applications_by_status: dict[str, int]
    applications_by_source: dict[str, int]
    applications_by_month: dict[str, int]
    applications_by_job_family: dict[str, int]


class OutcomeReportResponse(BaseModel):
    rejection_rate: float
    offer_rate: float
    hire_rate: float
    outcome_trends: dict[str, dict[str, int]]


class SkillReportResponse(BaseModel):
    strongest_performing_skills: list[str]
    weakest_performing_skills: list[str]
    most_successful_skills: list[str]
    rejection_linked_skills: list[str]


class RecommendationReportResponse(BaseModel):
    recommendations_followed: dict[str, int]
    recommendations_ignored: dict[str, int]
    recommendation_usage_rates: dict[str, float]


def cutoff_for_time_window(time_window: TimeWindow) -> datetime | None:
    now = datetime.now(UTC)
    if time_window == "last_30_days":
        return now - timedelta(days=30)
    if time_window == "last_90_days":
        return now - timedelta(days=90)
    if time_window == "last_year":
        return now - timedelta(days=365)
    return None


def dashboard_report(applications: list[dict]) -> dict:
    status_counts = _status_counts(applications)
    return DashboardReportResponse(
        active_applications=sum(
            count
            for status, count in status_counts.items()
            if status not in TERMINAL_STATUSES
        ),
        interviews_scheduled=status_counts["interview_scheduled"],
        offers_received=status_counts["offer_received"],
        hires=status_counts["hired"],
        rejections=status_counts["rejected"],
        pipeline_totals=status_counts,
    ).model_dump()


def funnel_report(applications: list[dict], outcomes: list[dict]) -> dict:
    achieved = _achieved_stages_by_application(applications, outcomes)
    applications_count = len({row["id"] for row in applications})
    recruiter_replies = _count_stage(achieved, "recruiter_replied")
    interviews = sum(
        1
        for stages in achieved.values()
        if "interview_scheduled" in stages or "interview_completed" in stages
    )
    offers = _count_stage(achieved, "offer_received")
    hires = _count_stage(achieved, "hired")

    return FunnelReportResponse(
        applications=applications_count,
        recruiter_replies=recruiter_replies,
        interviews=interviews,
        offers=offers,
        hires=hires,
        application_to_reply_rate=_rate(recruiter_replies, applications_count),
        reply_to_interview_rate=_rate(interviews, recruiter_replies),
        interview_to_offer_rate=_rate(offers, interviews),
        offer_to_hire_rate=_rate(hires, offers),
    ).model_dump()


def application_report(applications: list[dict], outcomes: list[dict]) -> dict:
    latest_family_by_application = _latest_job_family_by_application(outcomes)
    return ApplicationReportResponse(
        applications_by_status=_status_counts(applications),
        applications_by_source=_count_values(
            _source_label(row.get("source") or row.get("job_source"))
            for row in applications
        ),
        applications_by_month=_count_values(
            _month_label(row.get("created_at")) for row in applications
        ),
        applications_by_job_family=_count_values(
            latest_family_by_application.get(row["id"])
            or _infer_job_family(row.get("job_title") or "")
            for row in applications
        ),
    ).model_dump()


def outcome_report(applications: list[dict], outcomes: list[dict]) -> dict:
    total_applications = len({row["id"] for row in applications})
    counts = Counter(row["outcome"] for row in outcomes)
    return OutcomeReportResponse(
        rejection_rate=_rate(counts["rejected"], total_applications),
        offer_rate=_rate(counts["offer_received"], total_applications),
        hire_rate=_rate(counts["hired"], total_applications),
        outcome_trends=_outcome_trends(outcomes),
    ).model_dump()


def skill_report(outcomes: list[dict]) -> dict:
    positive_rows = [row for row in outcomes if row["outcome"] in POSITIVE_OUTCOMES]
    rejected_rows = [row for row in outcomes if row["outcome"] == "rejected"]
    success_rows = [row for row in outcomes if row["outcome"] in SUCCESS_OUTCOMES]

    return SkillReportResponse(
        strongest_performing_skills=_top_values(
            skill for row in positive_rows for skill in row.get("skills") or []
        ),
        weakest_performing_skills=_top_values(
            skill for row in rejected_rows for skill in row.get("skills") or []
        ),
        most_successful_skills=_top_values(
            skill for row in success_rows for skill in row.get("skills") or []
        ),
        rejection_linked_skills=_top_values(
            skill for row in rejected_rows for skill in row.get("skills") or []
        ),
    ).model_dump()


def recommendation_report(outcomes: list[dict]) -> dict:
    recommendations = {
        "cv_edits_applied": "cv_edits_applied",
        "cover_letter_used": "cover_letter_used",
        "interview_prep_used": "interview_prep_used",
    }
    followed = {}
    ignored = {}
    usage_rates = {}
    total = len(outcomes)

    for label, field in recommendations.items():
        followed[label] = sum(1 for row in outcomes if row.get(field))
        ignored[label] = sum(1 for row in outcomes if not row.get(field))
        usage_rates[label] = _rate(followed[label], total)

    return RecommendationReportResponse(
        recommendations_followed=followed,
        recommendations_ignored=ignored,
        recommendation_usage_rates=usage_rates,
    ).model_dump()


def candidate_insights_v2(outcomes: list[dict]) -> dict:
    base = build_candidate_insights(outcomes)
    rejected_rows = [row for row in outcomes if row["outcome"] == "rejected"]
    positive_rows = [row for row in outcomes if row["outcome"] in POSITIVE_OUTCOMES]

    base.update(
        {
            "top_job_families": _top_values(
                row.get("job_family") for row in positive_rows
            ),
            "recurring_rejection_patterns": base["most_common_rejection_reasons"],
            "strongest_skill_clusters": _skill_clusters(positive_rows),
            "focus_recommendations": base["recommended_focus_areas"],
            "rejection_count": len(rejected_rows),
        }
    )
    return base


def _status_counts(applications: list[dict]) -> dict[str, int]:
    counts = {status: 0 for status in APPLICATION_STATUSES}
    for row in applications:
        status = row.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def _achieved_stages_by_application(
    applications: list[dict],
    outcomes: list[dict],
) -> dict[object, set[str]]:
    achieved = {row["id"]: set() for row in applications}
    for row in applications:
        status = row.get("status")
        achieved[row["id"]].update(_stages_reached(status))
    for row in outcomes:
        application_id = row["application_id"]
        if application_id not in achieved:
            achieved[application_id] = set()
        outcome = row.get("outcome")
        achieved[application_id].update(_stages_reached(outcome))
    return achieved


def _count_stage(achieved: dict[object, set[str]], stage: str) -> int:
    return sum(1 for stages in achieved.values() if stage in stages)


def _stages_reached(status: str | None) -> set[str]:
    if status not in FUNNEL_STAGES:
        return set()
    stage_index = FUNNEL_STAGES.index(status)
    return set(FUNNEL_STAGES[: stage_index + 1])


def _latest_job_family_by_application(outcomes: list[dict]) -> dict[object, str]:
    latest = {}
    for row in outcomes:
        if row.get("job_family"):
            latest[row["application_id"]] = row["job_family"]
    return latest


def _outcome_trends(outcomes: list[dict]) -> dict[str, dict[str, int]]:
    trends: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in outcomes:
        trends[_month_label(row.get("created_at"))][row["outcome"]] += 1
    return {
        month: dict(sorted(counts.items()))
        for month, counts in sorted(trends.items())
    }


def _count_values(values) -> dict[str, int]:
    counts = Counter(value or "unknown" for value in values)
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _top_values(values) -> list[str]:
    return list(_count_values(value for value in values if value).keys())[:5]


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 2)


def _month_label(value) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m")
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m")
    return "unknown"


def _source_label(source: str | None) -> str:
    return source or "unknown"


def _infer_job_family(title: str) -> str:
    lowered = title.lower()
    families = {
        "data": "Data",
        "analytics": "Data",
        "engineer": "Engineering",
        "developer": "Engineering",
        "product": "Product",
        "marketing": "Marketing",
        "sales": "Sales",
        "operations": "Operations",
        "ai": "AI",
    }
    for keyword, family in families.items():
        if keyword in lowered:
            return family
    return "unknown"


def _skill_clusters(rows: list[dict]) -> list[str]:
    clusters = []
    skill_counts = _count_values(
        skill for row in rows for skill in row.get("skills") or []
    )
    if any(skill.lower() in {"python", "sql", "analytics"} for skill in skill_counts):
        clusters.append("data and automation")
    if any(
        skill.lower() in {"stakeholder management", "communication"}
        for skill in skill_counts
    ):
        clusters.append("stakeholder communication")
    if any(skill.lower() in {"ai", "machine learning", "llm"} for skill in skill_counts):
        clusters.append("ai delivery")
    return clusters[:5] or list(skill_counts.keys())[:3]
