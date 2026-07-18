"""Pydantic schemas for the JIM-mini API."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel

Condition = Literal[
    "anxiety", "depression", "financial_stress", "relationship", "physical_distress"
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
