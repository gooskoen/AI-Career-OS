# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import re
from typing import Literal
from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

APPLICATION_STATUSES = (
    "drafted",
    "applied",
    "recruiter_replied",
    "interview_scheduled",
    "interview_completed",
    "offer_received",
    "hired",
    "rejected",
    "withdrawn",
)

PIPELINE_STAGES = APPLICATION_STATUSES

ApplicationStatus = Literal[
    "drafted",
    "applied",
    "recruiter_replied",
    "interview_scheduled",
    "interview_completed",
    "offer_received",
    "hired",
    "rejected",
    "withdrawn",
]


class ApplicationCreateRequest(BaseModel):
    candidate_id: UUID
    job_id: UUID
    status: ApplicationStatus = "drafted"
    source: str | None = Field(default=None, max_length=200)
    match_result_id: UUID | None = None
    application_package_id: UUID | None = None
    company_intelligence_id: UUID | None = None


class ApplicationStatusUpdateRequest(BaseModel):
    status: ApplicationStatus


class ApplicationTransitionRequest(BaseModel):
    status: ApplicationStatus


class ApplicationNextActionRequest(BaseModel):
    next_action: str | None = Field(default=None, max_length=500)
    due_date: date | None = None


class ApplicationNoteRequest(BaseModel):
    note: str = Field(min_length=1, max_length=5_000)


def sanitize_note(note: str) -> str:
    redacted = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[redacted]", note)
    redacted = re.sub(r"https?://\S+", "[redacted]", redacted)
    redacted = re.sub(r"\+?\d[\d\s().-]{7,}\d", "[redacted]", redacted)
    return " ".join(redacted.split())
