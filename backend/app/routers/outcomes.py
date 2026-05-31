# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from app.application_domain import ApplicationStatusUpdateRequest
from app.dependencies import run_database_operation
from app.feedback import (
    OutcomeRequest,
    build_candidate_insights,
    build_outcome_history,
)
from app.repositories import (
    create_application_outcome,
    list_application_outcomes,
    update_application_status,
)

router = APIRouter()


@router.post("/outcomes")
def create_outcome(outcome: OutcomeRequest) -> dict:
    def operation(connection):
        created = create_application_outcome(connection, outcome)
        update_application_status(
            connection,
            outcome.application_id,
            ApplicationStatusUpdateRequest(status=outcome.outcome),
        )
        return created

    return run_database_operation(operation)


@router.get("/outcomes/{candidate_id}")
def get_outcomes(candidate_id: UUID) -> dict:
    return run_database_operation(
        lambda connection: build_outcome_history(
            list_application_outcomes(connection, candidate_id)
        )
    )


@router.get("/insights/candidate/{candidate_id}")
def get_candidate_insights(candidate_id: UUID) -> dict:
    return run_database_operation(
        lambda connection: build_candidate_insights(
            list_application_outcomes(connection, candidate_id)
        )
    )
