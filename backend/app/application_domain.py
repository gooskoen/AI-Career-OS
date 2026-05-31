# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import re
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

APPLICATION_STATUSES = (
    "drafted",
    "applied",
    "recruiter_replied",
    "interview_scheduled",
    "interview_completed",
    "rejected",
    "offer_received",
    "hired",
    "withdrawn",
)

ApplicationStatus = Literal[
    "drafted",
    "applied",
    "recruiter_replied",
    "interview_scheduled",
    "interview_completed",
    "rejected",
    "offer_received",
    "hired",
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


class ApplicationNoteRequest(BaseModel):
    note: str = Field(min_length=1, max_length=5_000)


def sanitize_note(note: str) -> str:
    redacted = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[redacted]", note)
    redacted = re.sub(r"https?://\S+", "[redacted]", redacted)
    redacted = re.sub(r"\+?\d[\d\s().-]{7,}\d", "[redacted]", redacted)
    return " ".join(redacted.split())
