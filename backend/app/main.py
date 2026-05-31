# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.errors import (
    http_exception_handler,
    internal_exception_handler,
    validation_exception_handler,
)
from app.routers import (
    applications,
    candidates,
    intelligence,
    jobs,
    matching,
    outcomes,
)

app = FastAPI(
    title="AI-Career-OS API",
    version="0.9.0",
    description="MVP backend for career application workflow demos.",
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)

app.include_router(candidates.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(applications.router)
app.include_router(intelligence.router)
app.include_router(outcomes.router)
