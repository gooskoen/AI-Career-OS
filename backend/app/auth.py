# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from pydantic import BaseModel, Field

ACCESS_TOKEN_MINUTES = 30
REFRESH_TOKEN_DAYS = 14
PASSWORD_ITERATIONS = 120_000


class UserRegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    display_name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=12, max_length=200)


class UserLoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=1, max_length=200)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=500)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return (
        f"pbkdf2_sha256${PASSWORD_ITERATIONS}$"
        f"{base64.urlsafe_b64encode(salt).decode()}$"
        f"{base64.urlsafe_b64encode(digest).decode()}"
    )


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            base64.urlsafe_b64decode(salt.encode()),
            int(iterations),
        )
        actual = base64.urlsafe_b64encode(digest).decode()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_MINUTES)).timestamp()),
    }
    return _encode_jwt(payload)


def decode_access_token(token: str) -> UUID | None:
    payload = _decode_jwt(token)
    if not payload or payload.get("type") != "access":
        return None
    subject = payload.get("sub")
    try:
        return UUID(str(subject))
    except (TypeError, ValueError):
        return None


def create_refresh_token() -> tuple[str, str, datetime]:
    token = secrets.token_urlsafe(48)
    token_hash = hash_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DAYS)
    return token, token_hash, expires_at


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def auth_secret() -> bytes:
    configured = os.getenv("AUTH_SECRET")
    if configured:
        return configured.encode("utf-8")
    return b"ai-career-os-demo-auth-secret"


def _encode_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_segment = _base64url_json(header)
    payload_segment = _base64url_json(payload)
    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    signature = hmac.new(auth_secret(), signing_input, hashlib.sha256).digest()
    return f"{header_segment}.{payload_segment}.{_base64url(signature)}"


def _decode_jwt(token: str) -> dict | None:
    try:
        header_segment, payload_segment, signature_segment = token.split(".", 2)
        signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
        expected = _base64url(
            hmac.new(auth_secret(), signing_input, hashlib.sha256).digest()
        )
        if not hmac.compare_digest(signature_segment, expected):
            return None
        payload = json.loads(_base64url_decode(payload_segment))
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            return None
        return payload
    except (ValueError, json.JSONDecodeError, TypeError):
        return None


def _base64url_json(value: dict) -> str:
    return _base64url(json.dumps(value, separators=(",", ":")).encode("utf-8"))


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii")).decode("utf-8")
