# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    name: str = Field(description="Demo candidate name only.")
    headline: str
    location: str
    summary: str
    target_roles: list[str]
    skills: list[str]
    experience_highlights: list[str]
    portfolio_links: list[str] = Field(default_factory=list)


class JobDescription(BaseModel):
    title: str
    company: str
    description: str
    required_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    source_url: str | None = None


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
    raw_text: str
    source_url: str | None = None
    match_candidate_id: UUID | None = None


class JobImportUrlRequest(BaseModel):
    url: str
    match_candidate_id: UUID | None = None
