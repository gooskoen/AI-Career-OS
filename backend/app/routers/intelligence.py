# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.company_intelligence import (
    CompanyIntelligenceRequest,
    build_company_intelligence,
)
from app.dependencies import current_user

router = APIRouter()


@router.post("/intelligence/company")
def company_intelligence(
    request: CompanyIntelligenceRequest,
    user: dict = Depends(current_user),
) -> dict:
    intelligence = build_company_intelligence(
        request.job,
        request.candidate,
        request.match_result,
        request.application_package,
        request.company_notes,
        request.recruiter_notes,
    )
    return intelligence.model_dump()
