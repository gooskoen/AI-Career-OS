# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.dependencies import current_user, run_database_operation
from app.reporting import (
    ApplicationReportResponse,
    DashboardReportResponse,
    FunnelReportResponse,
    OutcomeReportResponse,
    RecommendationReportResponse,
    SkillReportResponse,
    TimeWindow,
    application_report,
    cutoff_for_time_window,
    dashboard_report,
    funnel_report,
    outcome_report,
    recommendation_report,
    skill_report,
)
from app.repositories import list_reporting_applications, list_reporting_outcomes

router = APIRouter(prefix="/reporting")


@router.get("/dashboard", response_model=DashboardReportResponse)
def get_dashboard_report(
    time_window: TimeWindow = Query(default="all_time"),
    user: dict = Depends(current_user),
) -> dict:
    return _reporting_operation(
        user["id"],
        time_window,
        lambda applications, outcomes: dashboard_report(applications),
    )


@router.get("/funnel", response_model=FunnelReportResponse)
def get_funnel_report(
    time_window: TimeWindow = Query(default="all_time"),
    user: dict = Depends(current_user),
) -> dict:
    return _reporting_operation(user["id"], time_window, funnel_report)


@router.get("/applications", response_model=ApplicationReportResponse)
def get_application_report(
    time_window: TimeWindow = Query(default="all_time"),
    user: dict = Depends(current_user),
) -> dict:
    return _reporting_operation(user["id"], time_window, application_report)


@router.get("/outcomes", response_model=OutcomeReportResponse)
def get_outcome_report(
    time_window: TimeWindow = Query(default="all_time"),
    user: dict = Depends(current_user),
) -> dict:
    return _reporting_operation(user["id"], time_window, outcome_report)


@router.get("/skills", response_model=SkillReportResponse)
def get_skill_report(
    time_window: TimeWindow = Query(default="all_time"),
    user: dict = Depends(current_user),
) -> dict:
    return _reporting_operation(
        user["id"],
        time_window,
        lambda applications, outcomes: skill_report(outcomes),
    )


@router.get("/recommendations", response_model=RecommendationReportResponse)
def get_recommendation_report(
    time_window: TimeWindow = Query(default="all_time"),
    user: dict = Depends(current_user),
) -> dict:
    return _reporting_operation(
        user["id"],
        time_window,
        lambda applications, outcomes: recommendation_report(outcomes),
    )


def _reporting_operation(user_id, time_window: TimeWindow, builder):
    since = cutoff_for_time_window(time_window)

    def operation(connection):
        applications = list_reporting_applications(
            connection,
            user_id=user_id,
            since=since,
        )
        outcomes = list_reporting_outcomes(
            connection,
            user_id=user_id,
            since=since,
        )
        return builder(applications, outcomes)

    return run_database_operation(operation)
