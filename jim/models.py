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
    "mental_health", "health_fitness", "nutrition", "career", "finance",
    "relationships", "personal_growth",
]

Source = Literal[
    "wearable", "health", "calendar", "spending", "bank", "messages", "location"
]


class CaptureTake(BaseModel):
    """A photograph, clip or sound of the body (jim/capture.py).

    `content` is base64. It is stripped of EXIF and sealed in the vault; no
    field here reaches JIM's own database with pixels in it.
    """
    kind: str = "photo"                 # photo | video | audio
    site: str                           # capture.SITES key
    content: str                        # base64
    provenance: str = "captured"        # captured | imported
    note: str | None = None
    condition: str | None = None
    # Required for an intimate site, and refused outright for a minor
    # whatever this says.
    intimate_consent: bool = False


class CaptureAttach(BaseModel):
    """Which captures a referral releases."""
    capture_ids: list[str] = []


class DockConfig(BaseModel):
    """Where the helper pane sits and what it carries (jim/dock.py)."""
    corner: str | None = None           # bottom_right | bottom_left
    state: str | None = None            # hidden | handle | open
    face: str | None = None
    faces: list[str] | None = None


class PlanChoice(BaseModel):
    """Joining a plan, or moving between them (jim/tiers.py)."""
    plan: str                               # basic | pro


class Enroll(BaseModel):
    display_name: str
    # Spec [0031] / FIG. 2 box 212, "choose name (anonymized)": enroll under a
    # pseudonym instead. The typed display_name is then discarded — the app
    # never learns the real one — and `legal_name`, if given, is used only in
    # an emergency briefing (see jim/identity.py).
    anonymous: bool = False
    legal_name: str | None = None
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
    # The plan this person joins on. Omitted means Basic — which includes
    # every emergency path, so the cheapest plan is never the unsafe one.
    plan: str | None = None
    resting_heart_rate: int | None = None
    # Deprecated: free-text goals from early enrollments. Use the
    # /goals endpoints for tracked goals instead.
    goals: str | None = None
    known_conditions: list[Condition] = Field(default_factory=list)
    devices: list[str] = Field(default_factory=list)   # e.g. ["smart_watch"]


class Signup(Enroll):
    """Creating an account: everything enrollment takes, plus the email that
    will be verified before any of it exists, and a password."""
    email: str
    password: str


class OAuthStart(BaseModel):
    """Opening the "Sign in with ..." door (jim/oauth.py). ``enroll`` is the
    Guardian's signup payload for a brand-new account — the provider vouches
    for the inbox, never for the consent questions."""
    redirect_uri: str | None = None
    enroll: dict | None = None


class SignIn(BaseModel):
    """Returning to an account (jim/accounts.py)."""
    email: str
    password: str


class VerifyEmail(BaseModel):
    """Presenting the emailed code proves the caller holds the inbox."""
    email: str
    code: str


class ResendCode(BaseModel):
    email: str


class BandSet(BaseModel):
    """Adjusting a personal drift band (jim/bands.py). Omitted fields keep
    whatever is in force."""
    margin: float | None = None       # half-width, in the metric's own unit
    watch_high: bool | None = None
    watch_low: bool | None = None


class VoiceSettings(BaseModel):
    """How this deployment speaks (jim/voice.py)."""
    provider: Literal["elevenlabs", "openai", "device"]
    api_key: str | None = None
    voice_id: str | None = None
    speak_replies: bool | None = None


class VoiceSpeak(BaseModel):
    text: str
    voice_id: str | None = None      # override, e.g. to sample a voice


class VoiceTranscribe(BaseModel):
    audio_base64: str
    filename: str | None = None


class MailSettings(BaseModel):
    """Where this deployment sends mail through (jim/mailer.py)."""
    host: str
    port: int = 587
    username: str | None = None
    password: str | None = None
    sender: str | None = None
    public_url: str | None = None    # what verification links point at


class MailTest(BaseModel):
    to: str


class ResetRequest(BaseModel):
    email: str


class ResetPassword(BaseModel):
    email: str
    code: str
    new_password: str


class CareTeamLink(BaseModel):
    """Link the user's own QRME organization as their care team. The owner
    token is the user's own QRME credential, pasted knowingly — QRME's org
    routes are owner-only and JIM never sneaks around that."""

    org_id: str
    department_id: str                 # the desk that speaks for the Guardian
    owner_token: str


class CareTeamGoal(BaseModel):
    goal: str


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
    # The device's own report of how well it read (0..1). `signal.assess`
    # folds it in multiplicatively, so a wearable saying "poor contact" can
    # only ever lower trust — but this was the one input the model did not
    # declare, so pydantic stripped it at the door and the grader never saw
    # a device confess.
    signal_quality: float | None = Field(default=None, ge=0.0, le=1.0)
    source_device: str | None = None        # multimodal input: smart_watch |
                                            # stationary | neural_sensor |
                                            # gesture | robot | …
    note: str | None = None


class SessionStart(BaseModel):
    device: str | None = None               # the device this login is on


class DeviceRegister(BaseModel):
    name: str                               # e.g. smart_watch, kitchen_console
    # The first three are clause 16's embodiment classes. The rest are the
    # things people actually pair over Bluetooth: a speaker JIM speaks
    # through, the phone itself, smart glasses (Google, Meta), an AR/VR
    # headset, a spatial (3-D) display — a flat screen is "stationary" —
    # and the honest bucket for everything else. The console's picker
    # offered "phone" for a while before this row accepted it, which
    # meant a choice on screen the server refused.
    kind: Literal["wearable", "stationary", "autonomous",
                  "speaker", "phone", "glasses", "headset",
                  "spatial", "other"]
    transport: Literal["bluetooth", "wifi", "cellular", "wired"] | None = None
    has_llm: bool = False                   # embodiment carries its own LLM
    linked_to: str | None = None            # relays through this device
    paired: bool = False                    # the radio handshake happened


class JournalEntry(BaseModel):
    text: str


class GuidanceFeedback(BaseModel):
    rating: Literal["up", "down"]
    note: str | None = None


class MicAttach(BaseModel):
    """Nominate a registered device's microphone as channel 2 — the agent's
    own input, separate from the one carrying the user's voice."""
    device_name: str                   # e.g. smart_watch, earbuds, lapel_mic
    # What kind of microphone it is. Only ones pointed at a person qualify;
    # a room-facing one would lend everybody's voice. See jim/mic.py:MIC_TYPES.
    mic_type: Literal["watch", "earbuds", "headset", "lapel", "clip_on",
                      "bone_conduction", "glasses", "collar_tag", "handheld",
                      "speakerphone", "conference", "console", "laptop",
                      "room_array", "doorbell"]


class MicGain(BaseModel):
    """How wide channel 2 listens (see jim/mic.py:GAIN_LEVELS).

    Not an audio-quality preference: it is what makes "the agent hears you,
    not your call" true of the capture rather than true of a policy. Accepted
    at any level; the service caps what it actually runs at while somebody
    else's voice is in the air.
    """
    gain: Literal["near_field", "normal", "wide"]


class MicHandover(BaseModel):
    """Lend it, while the primary microphone is occupied (see jim/mic.py)."""
    reason: Literal["voice_call", "video_call", "recording", "dictation",
                    "live_room"]
    # How the occupying call is being heard. Required, not defaulted: on
    # speaker the wearable hears the other party too, and picking a default
    # would make that choice on the user's behalf.
    route: Literal["earpiece", "headset", "bluetooth_headset", "speaker"]
    others_present: bool = False       # anyone else in earshot
    # What is carrying the occupying call. If it is the same device as
    # channel 2, one microphone is being asked to be two channels.
    primary_device: str | None = None


class LocalitySet(BaseModel):
    """The town a referral searches near. Coarse and self-declared — not the
    consented live-location source. None clears it."""
    locality: str | None = None


class ReferralPrepare(BaseModel):
    condition: str                     # picks the specialist and the area
    provider_id: str                   # the clinician, from /referral/clinicians
    # Chosen deliberately, never swept in by a condition match. Intimate sites
    # are filtered out again on the way through — see capture.attach_to_referral.
    capture_ids: list[str] = []


class SpecialistTaskStart(BaseModel):
    """Hand a QRME specialist multi-step work (see jim/handoff.py)."""
    condition: str                     # which specialist to ask
    goal: str
    # Omit for handoff.DEFAULT_PLAN. Whatever is asked for is intersected with
    # what the specialist's owner permits — the narrower set wins.
    plan: list[str] | None = None


class ImprovementSubmit(BaseModel):
    """"Help us improve": product feedback on the app itself."""
    category: str = "idea"             # idea | improvement | bug | praise | other
    message: str
    rating: int | None = None          # optional 1..5 satisfaction


class ConditionDeclare(BaseModel):
    condition: Condition
    note: str | None = None


class PersonalityUpdate(BaseModel):
    tone: str | None = None                 # e.g. "direct and brief"
    instructions: str | None = None         # free-text preference
    # Spec [0019]: guidance "may be structured to be neutral to a person's
    # background or beliefs, such as religion, politics, sexual orientation,
    # or the like, and in other examples may be derived with sensitivity to
    # the user's beliefs taken into account." The user picks which; neutral
    # is the default, because assuming someone's beliefs is worse than
    # leaving them out of it.
    beliefs_posture: Literal["neutral", "sensitive"] | None = None
    beliefs: str | None = None              # only consulted when "sensitive"
    # Spec [0019], same sentence: "as may a user's general intelligence or
    # ability to quickly grasp and apply guidance."
    explain_level: Literal["plain", "standard", "technical"] | None = None
    # Clause 11: user-specific models "that adapt to professional roles,
    # workflows, or collaborative environments" — the user's own words for
    # what they do, so stress guidance can land in the life they actually
    # live (a night-shift nurse and a long-haul driver need different advice
    # about sleep). Optional, like everything else here.
    occupation: str | None = None


class CommunityVisit(BaseModel):
    """FIG. 2 boxes 222–226: a community door was opened. Only the fact is
    kept — the conversation itself stays in QRME (jim/community.py)."""

    room_id: str


class PresenceSurface(BaseModel):
    """Where the presence speaks (jim/presence.py). One word, because the
    consequence — whether health is read out loud or shown — follows from
    the place rather than from a second setting somebody has to find.

    Named `speaks_on` and not `surface`: `surface` already means a *display*
    surface in QRME and PDI, and the shared-vocabulary guard across the three
    products is right that one field name should not mean two things.
    """

    speaks_on: str


class FollowupAnswer(BaseModel):
    """Spec [0039]: whether the counseling that was delivered actually
    worked. ``helped=False`` escalates toward a live person."""

    helped: bool
    note: str | None = None                 # the user's own words, optional


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


class FamilyControls(BaseModel):
    paused: bool | None = None       # holds everyday guidance only
    quiet_start: str | None = None   # HH:MM; window may wrap midnight
    quiet_end: str | None = None


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


class MoneyAccountAdd(BaseModel):
    """Register a money account (jim/money.py). The numbers are sealed in
    the PDI vault or refused — they never land in JIM's own database."""
    kind: str                               # checking | savings | brokerage | crypto
    institution: str
    label: str | None = None
    account_number: str | None = None
    routing_number: str | None = None
    api_key: str | None = None              # brokerage / exchange access


class AppointmentIn(BaseModel):
    title: str
    when: str
    where: str | None = None
    email_reminder: bool = False
    shop_id: str | None = None
    offering_id: str | None = None


class ShopOrderIn(BaseModel):
    shop_id: str
    offering_id: str
    quantity: int = 1


class ShopCancelIn(BaseModel):
    qrme_order_id: str


class FeatureFlip(BaseModel):
    feature: str
    enabled: bool


class CircleInviteIn(BaseModel):
    other_id: str


class CircleMessageIn(BaseModel):
    to: str
    body: str


class HomepageIn(BaseModel):
    """The homepage document, whole. The walls live in `jim/circle.py`
    where the refusal sentences are — this shape only carries it."""
    headline: str | None = None
    about: str | None = None
    theme: dict | None = None
    links: list[dict] | None = None
    top_friends: list[str] | None = None


class MoneyObserve(BaseModel):
    """A balance reading against a registered account."""
    account_id: str
    balance: float | None = None
    note: str | None = None


class SavingsSet(BaseModel):
    goal: float
    note: str | None = None


class MandateSet(BaseModel):
    """The written handover: what JIM may do with the money, in caps and in
    words. Disabling needs nothing but `enabled: false`."""
    enabled: bool
    cap_per_order: float = 0
    monthly_cap: float = 0
    asset_classes: list[str] = Field(default_factory=list)
    scope: str = ""


class BudgetSet(BaseModel):
    """A budgeting plan (jim/life.py): this much per month for this
    category — '*' is the whole month's plan."""
    category: str = "*"
    monthly_limit: float = Field(gt=0)


class CheckIn(BaseModel):
    mood: int = Field(ge=1, le=5)  # 1 low .. 5 great
    energy: int | None = Field(default=None, ge=1, le=5)
    stress: int | None = Field(default=None, ge=1, le=5)  # 1 calm .. 5 overwhelmed
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


class BeaconPlace(BaseModel):
    """Print a watched person's beacon onto something.

    ``label`` and ``placement`` are the owner's own filing notes — several
    codes, several doors — and are never shown to whoever scans one.
    """

    label: str
    placement: str | None = None
    kind: Literal["personal", "site"] = "personal"


class BeaconAlarm(BaseModel):
    """A passer-by raising the people who are watching. No account, by design."""

    message: str | None = None


class RelayAccept(BaseModel):
    """A named human taking a site incident. Anonymous acceptance is refused —
    'someone accepted it' is the thing the relay exists to stop being enough."""

    responder: str


class RelayQuestion(BaseModel):
    question: str


class TutorialMark(BaseModel):
    """Where a learner is in the Guardian's walkthrough.

    `lesson` is optional because `/tutorial/start` needs only who is asking —
    requiring a step id to begin at the beginning would be a field somebody
    has to invent a value for.
    """

    learner_id: str
    lesson: str = ""
    mode: str = "text"


class VigilArm(BaseModel):
    """Naming the steward, and the words they will read — written now,
    while the person is fine."""

    steward_name: str
    steward_channel: str
    quiet_days: float = 3.0
    note: str | None = None


class WorkoutAsk(BaseModel):
    """The three adaptation inputs the field named: your minutes, your
    level, your focus."""

    minutes: int = 15
    level: str = "beginner"
    focus: str = "full_body"


class MealPlanAsk(BaseModel):
    goal: str
    preferences: list[str] = []
    days: int = 1


class HelpAsk(BaseModel):
    question: str = ""


class CrashWatchArm(BaseModel):
    """Programming the crash watch in advance: who is contacted when the
    person cannot answer, after how many unanswered attempts, and whether
    emergency services may be asked for — consent given while fine."""

    trusted_name: str
    trusted_channel: str
    attempts: int = 3
    window_minutes: float = 5.0
    contact_emergency_services: bool = False


class MedCreate(BaseModel):
    """A medication in the user's own words — 'the little white one, 10 mg'
    is a valid name and dose. schedule: {"times": ["08:00","20:00"]} or
    {"as_needed": true, "max_per_day": 3}."""

    name: str
    dose: str
    schedule: dict
    purpose: str | None = None
    critical: bool = False
    notes: str | None = None


class MedUpdate(BaseModel):
    name: str | None = None
    dose: str | None = None
    schedule: dict | None = None
    purpose: str | None = None
    critical: bool | None = None
    notes: str | None = None


class MedLog(BaseModel):
    action: str                 # taken | skipped
    slot: str | None = None     # required for scheduled meds
    note: str | None = None

class SelfProfileLink(BaseModel):
    """Binding a user to their own QRME `self` profile.

    An **owner** token. Not the interactor token `tandem_links` holds — the
    whole point of a self-profile is that it is not a stranger to them.
    """

    profile_id: str
    owner_token: str


class SelfProfileConsent(BaseModel):
    """Which categories the Guardian may tell that profile about.

    A list, replaced wholesale, empty by default and empty as a valid answer.
    Names are checked against `synthetic_self.CATEGORIES` in the module rather
    than typed here, so the allowlist has one home.
    """

    categories: list[str] = Field(default_factory=list)
