# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.auth import require_auth_secret
from app.errors import (
    http_exception_handler,
    internal_exception_handler,
    validation_exception_handler,
)
from app.routers import (
    applications,
    auth,
    candidates,
    intelligence,
    jobs,
    matching,
    outcomes,
    reporting,
)

require_auth_secret()


def parse_cors_origins(raw_origins: str | None = None) -> list[str]:
    configured_origins = (
        raw_origins
        if raw_origins is not None
        else os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        )
    )
    return [
        origin.strip().strip("[]").strip().strip("\"'")
        for origin in configured_origins.split(",")
        if origin.strip()
    ]


app = FastAPI(
    title="AI-Career-OS API",
    version="0.9.0",
    description="MVP backend for career application workflow demos.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)

app.include_router(candidates.router)
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(applications.router)
app.include_router(intelligence.router)
app.include_router(outcomes.router)
app.include_router(reporting.router)
