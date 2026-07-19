"""Pydantic schemas for the JIM-mini API."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Condition = Literal[
    "anxiety", "depression", "stress", "phobia", "financial_stress",
    "relationship", "physical_distress", "physical_injury",
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
    known_conditions: list[Condition] = Field(default_factory=list)
    devices: list[str] = Field(default_factory=list)   # e.g. ["smart_watch"]


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
    body_temperature: float | None = None   # °C
    movement: str | None = None             # e.g. fall | collapse | immobile
    speech: str | None = None               # e.g. slurred | incoherent
    source_device: str | None = None        # multimodal input: smart_watch |
                                            # stationary | neural_sensor |
                                            # gesture | robot | …
    note: str | None = None


class SessionStart(BaseModel):
    device: str | None = None               # the device this login is on


class ConditionDeclare(BaseModel):
    condition: Condition
    note: str | None = None


class PersonalityUpdate(BaseModel):
    tone: str | None = None                 # e.g. "direct and brief"
    instructions: str | None = None         # free-text preference


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
