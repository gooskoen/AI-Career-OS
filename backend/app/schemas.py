# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

SHORT_TEXT = 200
MEDIUM_TEXT = 2_000
LONG_TEXT = 20_000
MAX_LIST_ITEMS = 50


class CandidateProfile(BaseModel):
    name: str = Field(max_length=SHORT_TEXT, description="Demo candidate name only.")
    headline: str = Field(max_length=SHORT_TEXT)
    location: str = Field(max_length=SHORT_TEXT)
    summary: str = Field(max_length=MEDIUM_TEXT)
    target_roles: list[str] = Field(max_length=MAX_LIST_ITEMS)
    skills: list[str] = Field(max_length=MAX_LIST_ITEMS)
    experience_highlights: list[str] = Field(max_length=MAX_LIST_ITEMS)
    portfolio_links: list[str] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)


class JobDescription(BaseModel):
    title: str = Field(max_length=SHORT_TEXT)
    company: str = Field(max_length=SHORT_TEXT)
    location: str | None = Field(default=None, max_length=SHORT_TEXT)
    description: str = Field(max_length=LONG_TEXT)
    required_skills: list[str] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    nice_to_have_skills: list[str] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    source: str | None = Field(default=None, max_length=SHORT_TEXT)
    source_url: str | None = Field(default=None, max_length=MEDIUM_TEXT)
    external_id: str | None = Field(default=None, max_length=SHORT_TEXT)


class MatchRequest(BaseModel):
    candidate: CandidateProfile
    job: JobDescription


class BriefingRequest(BaseModel):
    candidate: CandidateProfile
    job: JobDescription


class PersistMatchRequest(BaseModel):
    candidate_profile_id: UUID
    job_description_id: UUID


class PersistBriefingRequest(BaseModel):
    match_result_id: UUID


class JobImportTextRequest(BaseModel):
    raw_text: str = Field(min_length=1, max_length=LONG_TEXT)
    source_url: str | None = Field(default=None, max_length=MEDIUM_TEXT)
    match_candidate_id: UUID | None = None


class JobImportUrlRequest(BaseModel):
    url: str = Field(min_length=1, max_length=MEDIUM_TEXT)
    match_candidate_id: UUID | None = None
