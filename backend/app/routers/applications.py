# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from app.application_domain import (
    ApplicationCreateRequest,
    ApplicationNoteRequest,
    ApplicationStatus,
    ApplicationStatusUpdateRequest,
)
from app.application_package import (
    ApplicationPackageRequest,
    build_application_package,
)
from app.dependencies import require_row, run_database_operation
from app.repositories import (
    create_application,
    create_application_note,
    get_application,
    list_application_status_events,
    list_applications,
    update_application_status,
)
from app.responses import PaginatedResponse, paginated_response

router = APIRouter()


@router.post("/applications/package")
def application_package(request: ApplicationPackageRequest) -> dict:
    package = build_application_package(
        request.candidate,
        request.job,
        request.match_result,
    )
    return package.model_dump()


@router.post("/applications")
def persist_application(application: ApplicationCreateRequest) -> dict:
    return run_database_operation(
        lambda connection: create_application(connection, application)
    )


@router.get("/applications", response_model=PaginatedResponse[dict])
def get_applications(
    status: ApplicationStatus | None = None,
    candidate_id: UUID | None = None,
    job_id: UUID | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> dict:
    def operation(connection):
        rows, total = list_applications(
            connection,
            status=status,
            candidate_id=candidate_id,
            job_id=job_id,
            page=page,
            page_size=page_size,
        )
        return paginated_response(
            rows,
            page=page,
            page_size=page_size,
            total=total,
        )

    return run_database_operation(operation)


@router.get("/applications/{application_id}")
def read_application(application_id: UUID) -> dict:
    return run_database_operation(
        lambda connection: require_row(
            get_application(connection, application_id),
            "Application not found",
        )
    )


@router.patch("/applications/{application_id}/status")
def patch_application_status(
    application_id: UUID,
    status_update: ApplicationStatusUpdateRequest,
) -> dict:
    return run_database_operation(
        lambda connection: require_row(
            update_application_status(connection, application_id, status_update),
            "Application not found",
        )
    )


@router.get("/applications/{application_id}/status-events")
def get_application_status_events(application_id: UUID) -> list[dict]:
    return run_database_operation(
        lambda connection: list_application_status_events(connection, application_id)
    )


@router.post("/applications/{application_id}/notes")
def post_application_note(
    application_id: UUID,
    note: ApplicationNoteRequest,
) -> dict:
    return run_database_operation(
        lambda connection: create_application_note(connection, application_id, note)
    )
