from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    session_id: UUID
    lang: Literal["en", "hi"] = "en"
    level: Literal["lok_sabha", "vidhan_sabha", "panchayat"] | None = None

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message must not be blank")
        return v


# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------

class PhaseSchema(BaseModel):
    id: str
    order: int
    name: str
    duration_days_typical: int | None = None
    description: str
    key_facts: list[str] = []


class TimelineResponse(BaseModel):
    level: str
    name: str
    description: str
    phases: list[PhaseSchema]


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------

class EligibilityRequest(BaseModel):
    age: int = Field(ge=0, le=120)
    citizenship: Literal["indian", "other"]
    state: str = Field(min_length=1, max_length=100)
    already_registered: bool

    @field_validator("state")
    @classmethod
    def state_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("state must not be blank")
        return v.strip()


class NextStep(BaseModel):
    label: str
    url: str


class EligibilityResponse(BaseModel):
    eligible: bool
    reasons: list[str]
    next_steps: list[NextStep]
