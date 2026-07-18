"""JIM-mini HTTP API — the standalone personal-guidance service."""

from __future__ import annotations

import os
from datetime import date, datetime

from fastapi import FastAPI, HTTPException

from . import db, guardian
from .models import BiometricSample, Enroll, SpecialistRegister
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

    return app


app = create_app()
