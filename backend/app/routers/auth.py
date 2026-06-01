# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.auth import (
    RefreshTokenRequest,
    UserLoginRequest,
    UserRegisterRequest,
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.dependencies import run_database_operation
from app.repositories import (
    create_auth_audit_event,
    create_refresh_token_record,
    create_user,
    get_refresh_token_record,
    get_user,
    get_user_by_email,
)

router = APIRouter()


@router.post("/auth/register")
def register_user(request: UserRegisterRequest) -> dict:
    def operation(connection):
        if get_user_by_email(connection, request.email):
            raise HTTPException(status_code=409, detail="Email is already registered")

        user = create_user(
            connection,
            email=request.email,
            display_name=request.display_name,
            password_hash=hash_password(request.password),
        )
        refresh_token, refresh_hash, expires_at = create_refresh_token()
        create_refresh_token_record(
            connection,
            user_id=user["id"],
            token_hash=refresh_hash,
            expires_at=expires_at,
        )
        return _token_response(user, refresh_token)

    return run_database_operation(operation)


@router.post("/auth/login")
def login_user(request: UserLoginRequest) -> dict:
    def operation(connection):
        user = get_user_by_email(connection, request.email)
        if user is None or not verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        create_auth_audit_event(connection, user["id"], "login")
        refresh_token, refresh_hash, expires_at = create_refresh_token()
        create_refresh_token_record(
            connection,
            user_id=user["id"],
            token_hash=refresh_hash,
            expires_at=expires_at,
        )
        return _token_response(user, refresh_token)

    return run_database_operation(operation)


@router.post("/auth/refresh")
def refresh_access_token(request: RefreshTokenRequest) -> dict:
    def operation(connection):
        refresh_record = get_refresh_token_record(
            connection,
            hash_token(request.refresh_token),
        )
        if refresh_record is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = get_user(connection, refresh_record["user_id"])
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        create_auth_audit_event(connection, user["id"], "refresh")
        return {
            "access_token": create_access_token(user["id"]),
            "token_type": "bearer",
            "user": _safe_user(user),
        }

    return run_database_operation(operation)


def _token_response(user: dict, refresh_token: str) -> dict:
    return {
        "access_token": create_access_token(user["id"]),
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": _safe_user(user),
    }


def _safe_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "email": user["email"],
        "display_name": user["display_name"],
    }
