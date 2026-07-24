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
    provider_consent: bool = False          # allow a care provider's summary view
    cloud_contribution: bool = False        # opt-in: anonymized guidance outcomes
                                            # improve the shared cloud model
    guardian_consent: bool = False
    emergency_name: str | None = None
    emergency_phone: str | None = None
    contact_consent: bool = False
    language: str | None = None             # chosen at the setup gateway
    device_paired: bool = False
    resting_heart_rate: int | None = None
    # Deprecated: free-text goals from early enrollments. Use the
    # /goals endpoints for tracked goals instead.
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
    bp_systolic: int | None = None          # mmHg
    bp_diastolic: int | None = None         # mmHg
    hrv: float | None = None                # heart-rate variability, ms
    activity_level: int | None = None       # 0 (sedentary) .. 10 (intense)
    movement: str | None = None             # e.g. fall | collapse | immobile
    speech: str | None = None               # e.g. slurred | incoherent
    rhythm: str | None = None               # e.g. fibrillation (ECG-capable wearable)
    pulse: str | None = None                # e.g. absent (with a collapse)
    air_quality: str | None = None          # e.g. smoke | co | poor (env sensor)
    co_level: float | None = None           # carbon monoxide, ppm
    posture: str | None = None              # e.g. slouched | hunched (ergonomics)
    repetitive_motion_min: int | None = None  # minutes of repetitive motion
    source_device: str | None = None        # multimodal input: smart_watch |
                                            # stationary | neural_sensor |
                                            # gesture | robot | …
    note: str | None = None


class SessionStart(BaseModel):
    device: str | None = None               # the device this login is on


class DeviceRegister(BaseModel):
    name: str                               # e.g. smart_watch, kitchen_console
    kind: Literal["wearable", "stationary", "autonomous"]
    transport: Literal["bluetooth", "wifi", "cellular", "wired"] | None = None
    has_llm: bool = False                   # embodiment carries its own LLM
    linked_to: str | None = None            # relays through this device


class JournalEntry(BaseModel):
    text: str


class GuidanceFeedback(BaseModel):
    rating: Literal["up", "down"]
    note: str | None = None


class ConditionDeclare(BaseModel):
    condition: Condition
    note: str | None = None


class PersonalityUpdate(BaseModel):
    tone: str | None = None                 # e.g. "direct and brief"
    instructions: str | None = None         # free-text preference


class SensitivitySet(BaseModel):
    level: str                              # cautious | balanced | assertive


class ModelChoice(BaseModel):
    # A jim.llm registry name (anthropic | openai | grok | perplexity | gemini
    # | stub) or "auto" to defer to the platform default.
    provider: str


class RobotBind(BaseModel):
    model: str                      # jim.robotics catalog key, e.g. "neo"
    name: str | None = None         # household name; defaults to the label
    llm_provider: str | None = None  # jim.llm registry name; None → user's


class RobotCommand(BaseModel):
    command: str                    # from the body's kind/rating allowlist
    arg: str | None = None          # e.g. "confirmed" for perform_cpr,
                                    # "cpr" | "aed" for guide_first_aid


class ChildEnroll(BaseModel):
    display_name: str
    birthdate: date                  # required: the tier and the 18 cutoff
    relationship: str = "parent"     # parent | legal_guardian
    guardian_phone: str | None = None  # becomes the consented emergency line
    resting_heart_rate: int | None = None
    known_conditions: list[Condition] = Field(default_factory=list)
    language: str | None = None


class WaiverSign(BaseModel):
    signature: str                  # typed legal name
    accept: bool = False            # explicit acceptance of the terms


class LanguageChoice(BaseModel):
    language: str                   # jim.i18n.SUPPORTED code, e.g. "es"
    mode: str = "pre"               # pre (deliver translated) | on_demand


class TranslateRequest(BaseModel):
    text: str                       # anything the user ran across
    to: str | None = None           # target language; None -> user's choice


class SourceConsent(BaseModel):
    source: Source
    consented: bool


class ContextEvent(BaseModel):
    source: Source
    kind: str                      # e.g. transaction | sleep | event | message
    data: dict = Field(default_factory=dict)


SocialPlatform = Literal[
    "instagram", "x", "tiktok", "facebook", "linkedin", "youtube", "reddit",
    "threads", "whatsapp", "meta", "mastodon", "twitch", "snapchat", "roblox",
    "pinterest", "discord",
]


class SocialConnect(BaseModel):
    platform: SocialPlatform
    direction: Literal["collect", "publish"]
    handle: str | None = None
    scope: list[str] = Field(default_factory=list)


class SocialItem(BaseModel):
    content: str
    title: str | None = None


class SocialCollect(BaseModel):
    items: list[SocialItem] = Field(default_factory=list)


class SocialPublish(BaseModel):
    content: str
    topic: str | None = None


class AppConnect(BaseModel):
    provider: str
    app: str
    capabilities: list[str] = Field(default_factory=list)  # empty = grant all


class AppItem(BaseModel):
    content: str
    title: str | None = None


class AppCollect(BaseModel):
    items: list[AppItem] = Field(default_factory=list)


class AppInvoke(BaseModel):
    capability: str
    input: str | None = None


class ExcursionStart(BaseModel):
    topic: str
    question: str
    private: list[str] = Field(default_factory=list)


class CheckIn(BaseModel):
    mood: int = Field(ge=1, le=5)  # 1 low .. 5 great
    energy: int | None = Field(default=None, ge=1, le=5)
    note: str | None = None


class EmergencyRequest(BaseModel):
    """Trigger emergency mode. All fields optional — the coordinated response
    (services, location share, family contact, Medical ID, connected-device
    alerts) is assembled from what the user has on file; a ``situation`` or
    ``sample`` adds targeted first-aid guidance."""
    situation: str | None = None            # free-text description of what's wrong
    location: str | None = None             # to share with contacts/responders
    sample: BiometricSample | None = None   # live readings for AI guidance


class ActivityObserve(BaseModel):
    """An ambient signal from something the user is doing right now. Signals
    are open-ended (retries/errors, idle_seconds, duration_min, …); note is
    what they said out loud while doing it."""
    activity: str | None = None    # e.g. "editing video", "fixing the car"
    signals: dict = Field(default_factory=dict)
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
