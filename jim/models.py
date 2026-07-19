"""Pydantic schemas for the JIM-mini API."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Condition = Literal[
    "anxiety", "depression", "financial_stress", "relationship", "physical_distress"
]

LifeArea = Literal[
    "mental_health", "health_fitness", "career", "finance",
    "relationships", "personal_growth",
]

Source = Literal[
    "wearable", "health", "calendar", "spending", "bank", "messages", "location"
]


class Enroll(BaseModel):
    display_name: str
    birthdate: date | None = None
    terms_consent: bool
    guardian_consent: bool = False
    emergency_name: str | None = None
    emergency_phone: str | None = None
    contact_consent: bool = False
    device_paired: bool = False
    resting_heart_rate: int | None = None
    goals: str | None = None


class SpecialistRegister(BaseModel):
    condition: Condition
    mode: Literal["local", "tandem"] = "local"
    label: str | None = None
    qrme_profile_id: str | None = None   # required when mode == "tandem"


class BiometricSample(BaseModel):
    heart_rate: int | None = None
    resting_heart_rate: int | None = None
    respiratory_rate: int | None = None
    blood_oxygen: float | None = None
    note: str | None = None


class SourceConsent(BaseModel):
    source: Source
    consented: bool


class ContextEvent(BaseModel):
    source: Source
    kind: str                      # e.g. transaction | sleep | event | message
    data: dict = Field(default_factory=dict)


class CheckIn(BaseModel):
    mood: int = Field(ge=1, le=5)  # 1 low .. 5 great
    energy: int | None = Field(default=None, ge=1, le=5)
    note: str | None = None


class GoalCreate(BaseModel):
    area: LifeArea
    title: str
    target: str | None = None


class GoalUpdate(BaseModel):
    progress: float | None = Field(default=None, ge=0, le=1)
    status: Literal["active", "completed", "abandoned"] | None = None


class HabitCreate(BaseModel):
    name: str


class HabitLog(BaseModel):
    day: date | None = None        # defaults to today


class CoachMessage(BaseModel):
    area: LifeArea
    message: str
