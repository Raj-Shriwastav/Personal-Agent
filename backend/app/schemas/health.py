"""Pydantic response schemas for the health endpoints."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app: str
    environment: str


class DatabaseHealthResponse(BaseModel):
    status: Literal["ok", "error"]
    database: Literal["connected", "unreachable"]
    detail: str
