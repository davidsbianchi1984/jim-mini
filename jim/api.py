"""JIM-mini HTTP API — the standalone personal-guidance service."""

from __future__ import annotations

import os
from datetime import date, datetime

from fastapi import FastAPI, HTTPException

from . import coach, db, guardian, life
from .models import (
    BiometricSample, CheckIn, CoachMessage, ConditionDeclare, ContextEvent,
    DeviceRegister, Enroll, GoalCreate, GoalUpdate, GuidanceFeedback,
    HabitCreate, HabitLog, JournalEntry, PersonalityUpdate, SessionStart,
    SourceConsent, SpecialistRegister,
)
from .cloud import CloudModelClient
from .pdi_client import PDIClient
from .qrme_client import QRMEClient


def _age(birthdate: date) -> int:
    today = datetime.now().date()
    return today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )


def create_app(qrme_client: QRMEClient | None = None,
               pdi_client: PDIClient | None = None,
               cloud_client: CloudModelClient | None = None) -> FastAPI:
    app = FastAPI(title="JIM-mini / Guardian", version="0.1.0")

    # Tandem is optional: injected client (tests) > JIM_QRME_URL env > none.
    if qrme_client is None and os.environ.get("JIM_QRME_URL"):
        qrme_client = QRMEClient(base_url=os.environ["JIM_QRME_URL"])
    app.state.qrme = qrme_client

    # PDI tandem: sensitive payloads (medical first) go to the encrypted
    # vault instead of JIM's own database when configured.
    if pdi_client is None and os.environ.get("JIM_PDI_URL"):
        pdi_client = PDIClient(token=os.environ.get("JIM_PDI_TOKEN", ""),
                               base_url=os.environ["JIM_PDI_URL"])
    app.state.pdi = pdi_client

    # Cloud Model Gateway: greater-model guidance with local fallback, and
    # the opt-in contribution intake (JIM_CLOUD_URL + JIM_CLOUD_TOKEN).
    if cloud_client is None and os.environ.get("JIM_CLOUD_URL"):
        cloud_client = CloudModelClient(
            token=os.environ.get("JIM_CLOUD_TOKEN", ""),
            base_url=os.environ["JIM_CLOUD_URL"])
    app.state.cloud = cloud_client

    def _user_or_404(user_id: str) -> dict:
        user = guardian.get_user(user_id)
        if user is None:
            raise HTTPException(404, "user not found")
        return user

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "tandem": app.state.qrme is not None,
                "pdi": app.state.pdi is not None,
                "cloud": app.state.cloud is not None}

    @app.get("/cloud/status")
    def cloud_status() -> dict:
        """Whether a Cloud Model Gateway is configured, and what it serves."""
        cloud = app.state.cloud
        return {
            "cloud": cloud is not None,
            "model": cloud.model_info() if cloud is not None else None,
            "fallback": "local provider (Anthropic SDK or offline stub)",
            "contribution": "opt-in per user via cloud_contribution; "
                            "anonymized guidance outcomes only; revocable",
        }

    @app.post("/enroll", status_code=201)
    def enroll(body: Enroll) -> dict:
        if not body.terms_consent:
            raise HTTPException(403, "consent to terms of use is required to enroll")
        if body.birthdate and _age(body.birthdate) < 18 and not body.guardian_consent:
            raise HTTPException(403, "minors require parent/guardian consent")
        return guardian.enroll(body.model_dump())

    @app.post("/specialists")
    def register_specialist(body: SpecialistRegister) -> dict:
        if body.mode == "tandem" and not body.qrme_profile_id:
            raise HTTPException(422, "tandem specialists require a qrme_profile_id")
        return guardian.register_specialist(body.model_dump())

    @app.post("/monitor/{user_id}")
    def monitor(user_id: str, body: BiometricSample) -> dict:
        _user_or_404(user_id)
        sample = body.model_dump(exclude_none=True)
        note = sample.pop("note", None)
        return guardian.monitor(user_id, sample, note, qrme=app.state.qrme,
                                pdi=app.state.pdi)

    @app.get("/events/{user_id}")
    def events(user_id: str) -> list[dict]:
        _user_or_404(user_id)
        return guardian.events(user_id)

    # ---- physical embodiments (clause 16) ---------------------------------

    @app.post("/devices/{user_id}", status_code=201)
    def register_device(user_id: str, body: DeviceRegister) -> dict:
        _user_or_404(user_id)
        return guardian.register_device(user_id, body.model_dump())

    @app.get("/devices/{user_id}")
    def get_devices(user_id: str) -> list[dict]:
        _user_or_404(user_id)
        return guardian.devices_for(user_id)

    # ---- login sessions (cross-device continuity) -------------------------

    @app.post("/sessions/{user_id}", status_code=201)
    def start_session(user_id: str, body: SessionStart) -> dict:
        _user_or_404(user_id)
        return guardian.start_session(user_id, body.device)

    @app.post("/sessions/{user_id}/{session_id}/end")
    def end_session(user_id: str, session_id: str) -> dict:
        _user_or_404(user_id)
        ended = guardian.end_session(user_id, session_id)
        if ended is None:
            raise HTTPException(404, "session not found")
        return ended

    # ---- known conditions & counselor adaptation --------------------------

    @app.post("/conditions/{user_id}", status_code=201)
    def declare_condition(user_id: str, body: ConditionDeclare) -> dict:
        _user_or_404(user_id)
        return guardian.declare_condition(user_id, body.condition, body.note)

    @app.put("/personality/{user_id}")
    def set_personality(user_id: str, body: PersonalityUpdate) -> dict:
        _user_or_404(user_id)
        return guardian.set_personality(user_id, body.model_dump())

    # ---- connected sources ("AI only sees what you allow") ----------------

    @app.get("/sources/{user_id}")
    def get_sources(user_id: str) -> list[dict]:
        _user_or_404(user_id)
        return life.sources(user_id)

    @app.put("/sources/{user_id}")
    def set_source(user_id: str, body: SourceConsent) -> dict:
        _user_or_404(user_id)
        return life.set_source(user_id, body.source, body.consented)

    @app.post("/context/{user_id}", status_code=201)
    def add_context(user_id: str, body: ContextEvent) -> dict:
        _user_or_404(user_id)
        if not life.source_allowed(user_id, body.source):
            raise HTTPException(
                403, f"source '{body.source}' is not consented for this user")
        return life.add_context(user_id, body.source, body.kind, body.data,
                                pdi=app.state.pdi)

    # ---- mood & energy check-ins ------------------------------------------

    @app.post("/checkin/{user_id}", status_code=201)
    def check_in(user_id: str, body: CheckIn) -> dict:
        _user_or_404(user_id)
        result = life.check_in(user_id, body.mood, body.energy, body.note,
                               pdi=app.state.pdi)
        # A worrying note still goes through the Guardian pipeline so crisis
        # language escalates exactly as it does from /monitor.
        if body.note:
            result["guardian"] = guardian.monitor(
                user_id, {}, body.note, qrme=app.state.qrme, pdi=app.state.pdi)
        return result

    # ---- smart goals ------------------------------------------------------

    @app.get("/goals/{user_id}")
    def get_goals(user_id: str) -> list[dict]:
        _user_or_404(user_id)
        return life.goals(user_id)

    @app.post("/goals/{user_id}", status_code=201)
    def add_goal(user_id: str, body: GoalCreate) -> dict:
        _user_or_404(user_id)
        return life.add_goal(user_id, body.area, body.title, body.target)

    @app.patch("/goals/{user_id}/{goal_id}")
    def update_goal(user_id: str, goal_id: str, body: GoalUpdate) -> dict:
        _user_or_404(user_id)
        updated = life.update_goal(user_id, goal_id, body.progress, body.status)
        if updated is None:
            raise HTTPException(404, "goal not found")
        return updated

    # ---- habits & streaks -------------------------------------------------

    @app.get("/habits/{user_id}")
    def get_habits(user_id: str) -> list[dict]:
        _user_or_404(user_id)
        return life.habits(user_id)

    @app.post("/habits/{user_id}", status_code=201)
    def add_habit(user_id: str, body: HabitCreate) -> dict:
        _user_or_404(user_id)
        return life.add_habit(user_id, body.name)

    @app.post("/habits/{user_id}/{habit_id}/log")
    def log_habit(user_id: str, habit_id: str, body: HabitLog | None = None) -> dict:
        _user_or_404(user_id)
        logged = life.log_habit(user_id, habit_id, body.day if body else None)
        if logged is None:
            raise HTTPException(404, "habit not found")
        return logged

    # ---- life coach & insights --------------------------------------------

    @app.post("/coach/{user_id}")
    def coach_reply(user_id: str, body: CoachMessage) -> dict:
        _user_or_404(user_id)
        return coach.reply(user_id, body.area, body.message)

    @app.get("/coach/{user_id}")
    def coach_history(user_id: str, area: str | None = None) -> list[dict]:
        _user_or_404(user_id)
        return coach.history(user_id, area)

    @app.get("/insights/{user_id}")
    def get_insights(user_id: str) -> list[dict]:
        _user_or_404(user_id)
        return life.insights(user_id)

    @app.post("/companion/{user_id}")
    def companion_checkin(user_id: str) -> dict:
        """An ambient, unprompted check-in from the coach — grounded in the
        user's latest mood, goals, and personality preferences."""
        _user_or_404(user_id)
        return coach.companion_checkin(user_id)

    # ---- journal, feedback, reports, provider portal ----------------------

    @app.post("/journal/{user_id}", status_code=201)
    def add_journal(user_id: str, body: JournalEntry) -> dict:
        _user_or_404(user_id)
        result = life.add_journal(user_id, body.text, pdi=app.state.pdi)
        # Journal text runs the same crisis pipeline as check-in notes.
        result["guardian"] = guardian.monitor(
            user_id, {}, body.text, qrme=app.state.qrme, pdi=app.state.pdi)
        return result

    @app.get("/journal/{user_id}")
    def get_journal(user_id: str) -> list[dict]:
        _user_or_404(user_id)
        return life.journal_entries(user_id, pdi=app.state.pdi)

    @app.post("/feedback/{user_id}", status_code=201)
    def add_feedback(user_id: str, body: GuidanceFeedback) -> dict:
        user = _user_or_404(user_id)
        result = life.add_feedback(user_id, body.rating, body.note)
        # Opt-in cloud contribution: anonymized guidance outcomes only —
        # condition domain, severity, and the rating. Never ids or notes.
        result["contributed"] = False
        if user.get("cloud_contribution") and app.state.cloud is not None:
            last = db.connect().execute(
                "SELECT condition, severity FROM events"
                " WHERE user_id=? AND type='guidance'"
                " ORDER BY created_at DESC, rowid DESC LIMIT 1",
                (user_id,)).fetchone()
            if last:
                result["contributed"] = app.state.cloud.contribute({
                    "source": "jim-mini",
                    "kind": "guidance_outcome",
                    "condition": last["condition"],
                    "severity": last["severity"],
                    "rating": body.rating,
                })
        return result

    @app.get("/report/{user_id}")
    def progress_report(user_id: str) -> dict:
        _user_or_404(user_id)
        return life.progress_report(user_id)

    @app.get("/provider/{user_id}")
    def provider_portal(user_id: str) -> dict:
        user = _user_or_404(user_id)
        if not user.get("provider_consent"):
            raise HTTPException(
                403, "the user has not consented to provider access")
        return life.provider_summary(user)

    # ---- erasure ("delete anything, anytime") -----------------------------

    @app.delete("/data/{user_id}")
    def delete_data(user_id: str) -> dict:
        _user_or_404(user_id)
        return life.delete_user_data(user_id, pdi=app.state.pdi)

    return app


app = create_app()
