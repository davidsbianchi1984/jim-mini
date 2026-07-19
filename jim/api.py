"""JIM-mini HTTP API — the standalone personal-guidance service."""

from __future__ import annotations

import os
from datetime import date, datetime

from fastapi import FastAPI, HTTPException

from . import coach, db, guardian, life
from .models import (
    BiometricSample, CheckIn, CoachMessage, ContextEvent, Enroll, GoalCreate,
    GoalUpdate, HabitCreate, HabitLog, SourceConsent, SpecialistRegister,
)
from .qrme_client import QRMEClient


def _age(birthdate: date) -> int:
    today = datetime.now().date()
    return today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )


def create_app(qrme_client: QRMEClient | None = None) -> FastAPI:
    app = FastAPI(title="JIM-mini / Guardian", version="0.1.0")

    # Tandem is optional: injected client (tests) > JIM_QRME_URL env > none.
    if qrme_client is None and os.environ.get("JIM_QRME_URL"):
        qrme_client = QRMEClient(base_url=os.environ["JIM_QRME_URL"])
    app.state.qrme = qrme_client

    def _user_or_404(user_id: str) -> dict:
        user = guardian.get_user(user_id)
        if user is None:
            raise HTTPException(404, "user not found")
        return user

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "tandem": app.state.qrme is not None}

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
        return guardian.monitor(user_id, sample, note, qrme=app.state.qrme)

    @app.get("/events/{user_id}")
    def events(user_id: str) -> list[dict]:
        _user_or_404(user_id)
        return guardian.events(user_id)

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
        return life.add_context(user_id, body.source, body.kind, body.data)

    # ---- mood & energy check-ins ------------------------------------------

    @app.post("/checkin/{user_id}", status_code=201)
    def check_in(user_id: str, body: CheckIn) -> dict:
        _user_or_404(user_id)
        result = life.check_in(user_id, body.mood, body.energy, body.note)
        # A worrying note still goes through the Guardian pipeline so crisis
        # language escalates exactly as it does from /monitor.
        if body.note:
            result["guardian"] = guardian.monitor(
                user_id, {}, body.note, qrme=app.state.qrme)
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

    # ---- erasure ("delete anything, anytime") -----------------------------

    @app.delete("/data/{user_id}")
    def delete_data(user_id: str) -> dict:
        _user_or_404(user_id)
        return life.delete_user_data(user_id)

    return app


app = create_app()
