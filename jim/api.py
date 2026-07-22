"""JIM-mini HTTP API — the standalone personal-guidance service."""

from __future__ import annotations

import io
import os
from datetime import date, datetime

from fastapi import FastAPI, HTTPException, Request, Response

from . import auth, coach, db, guardian, life, social
from .models import (
    ActivityObserve, BiometricSample, CheckIn, CoachMessage, ConditionDeclare,
    ContextEvent, DeviceRegister, EmergencyRequest, Enroll, GoalCreate,
    GoalUpdate, GuidanceFeedback, HabitCreate, HabitLog, JournalEntry,
    PersonalityUpdate, SensitivitySet, SessionStart, SocialCollect,
    SocialConnect, SocialPublish, SourceConsent, SpecialistRegister,
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

    # Optional CORS for a packaged guardian-console front-end (app/) calling the
    # API from another origin. Off by default; set JIM_CORS_ORIGINS to a
    # comma-separated allowlist, or "*" for any.
    _origins = os.environ.get("JIM_CORS_ORIGINS")
    if _origins:
        from fastapi.middleware.cors import CORSMiddleware
        _allow = ["*"] if _origins.strip() == "*" else [
            o.strip() for o in _origins.split(",") if o.strip()]
        app.add_middleware(
            CORSMiddleware, allow_origins=_allow, allow_credentials=False,
            allow_methods=["*"], allow_headers=["*"])

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

    def _user_or_404(user_id: str, request: Request) -> dict:
        """Load the user (404 if unknown) and authorize the caller: every
        per-user surface is PHI, so it requires that user's token."""
        user = guardian.get_user(user_id)
        if user is None:
            raise HTTPException(404, "user not found")
        auth.require(request, "user", user_id)
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
        user = guardian.enroll(body.model_dump())
        # The user token is shown exactly once, here.
        user["user_token"] = auth.issue("user", user["id"])
        return user

    @app.post("/specialists")
    def register_specialist(body: SpecialistRegister) -> dict:
        if body.mode == "tandem" and not body.qrme_profile_id:
            raise HTTPException(422, "tandem specialists require a qrme_profile_id")
        return guardian.register_specialist(body.model_dump())

    @app.post("/monitor/{user_id}")
    def monitor(user_id: str, body: BiometricSample, request: Request) -> dict:
        _user_or_404(user_id, request)
        sample = body.model_dump(exclude_none=True)
        note = sample.pop("note", None)
        return guardian.monitor(user_id, sample, note, qrme=app.state.qrme,
                                pdi=app.state.pdi)

    @app.get("/events/{user_id}")
    def events(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return guardian.events(user_id)

    def _public_base() -> str:
        return os.environ.get("JIM_PUBLIC_URL", "https://jim.app").rstrip("/")

    @app.post("/medical-id/qr/{user_id}", status_code=201)
    def issue_medical_card(user_id: str, request: Request) -> dict:
        """Mint (or rotate) the user's shareable Medical ID QR. The returned
        token is the credential a scanner uses; rotating invalidates the old
        code."""
        _user_or_404(user_id, request)
        token = guardian.issue_medical_card(user_id)
        return {"token": token,
                "view_url": f"/medical-id/{token}",
                "qr_svg_url": f"/medical-id/{token}/qr.svg"}

    @app.delete("/medical-id/qr/{user_id}", status_code=204)
    def revoke_medical_card(user_id: str, request: Request) -> Response:
        _user_or_404(user_id, request)
        if not guardian.revoke_medical_card(user_id):
            raise HTTPException(404, "no Medical ID card to revoke")
        return Response(status_code=204)

    @app.get("/medical-id/{token}")
    def view_medical_card(token: str) -> dict:
        """Public: a first responder scans the QR and reads the Medical ID —
        condition-level facts only, no auth token required (the phone is
        locked)."""
        med = guardian.resolve_medical_card(token)
        if med is None:
            raise HTTPException(404, "this Medical ID card is not valid")
        return med

    @app.get("/medical-id/{token}/qr.svg")
    def medical_card_qr(token: str) -> Response:
        """The printable / lock-screen QR image encoding the card's view URL."""
        if guardian.resolve_medical_card(token) is None:
            raise HTTPException(404, "this Medical ID card is not valid")
        import segno
        buf = io.BytesIO()
        segno.make(f"{_public_base()}/medical-id/{token}", error="q").save(
            buf, kind="svg", scale=8, border=2,
            dark="#b3261e", light="#ffffff")   # medical red on white
        return Response(content=buf.getvalue(), media_type="image/svg+xml")

    @app.post("/emergency/{user_id}", status_code=201)
    def emergency(user_id: str, body: EmergencyRequest,
                  request: Request) -> dict:
        """Emergency mode: one coordinated response — reach services, share
        location, contact family, surface the Medical ID, deliver step-by-step
        AI first aid, and alert every connected device."""
        _user_or_404(user_id, request)
        sample = body.sample.model_dump(exclude_none=True) if body.sample else None
        return guardian.emergency(user_id, body.situation, body.location,
                                  sample, qrme=app.state.qrme, pdi=app.state.pdi)

    @app.post("/activity/{user_id}", status_code=201)
    def observe_activity(user_id: str, body: ActivityObserve,
                         request: Request) -> dict:
        """Ambient background observation: JIM watches an ongoing activity and
        jumps in proactively when a struggle is building — before being asked."""
        _user_or_404(user_id, request)
        return guardian.observe_activity(
            user_id, body.activity, body.signals, body.note,
            qrme=app.state.qrme, pdi=app.state.pdi)

    # ---- physical embodiments (clause 16) ---------------------------------

    @app.post("/devices/{user_id}", status_code=201)
    def register_device(user_id: str, body: DeviceRegister,
                        request: Request) -> dict:
        _user_or_404(user_id, request)
        return guardian.register_device(user_id, body.model_dump())

    @app.get("/devices/{user_id}")
    def get_devices(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return guardian.devices_for(user_id)

    # ---- login sessions (cross-device continuity) -------------------------

    @app.post("/sessions/{user_id}", status_code=201)
    def start_session(user_id: str, body: SessionStart,
                      request: Request) -> dict:
        _user_or_404(user_id, request)
        return guardian.start_session(user_id, body.device,
                                      qrme=app.state.qrme)

    @app.post("/sessions/{user_id}/{session_id}/end")
    def end_session(user_id: str, session_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        ended = guardian.end_session(user_id, session_id)
        if ended is None:
            raise HTTPException(404, "session not found")
        return ended

    # ---- known conditions & counselor adaptation --------------------------

    @app.post("/conditions/{user_id}", status_code=201)
    def declare_condition(user_id: str, body: ConditionDeclare,
                          request: Request) -> dict:
        _user_or_404(user_id, request)
        return guardian.declare_condition(user_id, body.condition, body.note)

    @app.put("/personality/{user_id}")
    def set_personality(user_id: str, body: PersonalityUpdate,
                        request: Request) -> dict:
        _user_or_404(user_id, request)
        return guardian.set_personality(user_id, body.model_dump())

    @app.put("/sensitivity/{user_id}")
    def set_sensitivity(user_id: str, body: SensitivitySet,
                        request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return guardian.set_sensitivity(user_id, body.level)
        except ValueError as e:
            raise HTTPException(422, str(e))

    @app.get("/baseline/{user_id}")
    def get_baseline(user_id: str, request: Request) -> list[dict]:
        """The user's rolling per-metric baselines (provisional until enough
        resting samples have accrued)."""
        _user_or_404(user_id, request)
        return guardian.baseline_for(user_id)

    # ---- connected sources ("AI only sees what you allow") ----------------

    @app.get("/sources/{user_id}")
    def get_sources(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return life.sources(user_id)

    @app.put("/sources/{user_id}")
    def set_source(user_id: str, body: SourceConsent, request: Request) -> dict:
        _user_or_404(user_id, request)
        return life.set_source(user_id, body.source, body.consented)

    @app.post("/context/{user_id}", status_code=201)
    def add_context(user_id: str, body: ContextEvent, request: Request) -> dict:
        _user_or_404(user_id, request)
        if not life.source_allowed(user_id, body.source):
            raise HTTPException(
                403, f"source '{body.source}' is not consented for this user")
        return life.add_context(user_id, body.source, body.kind, body.data,
                                pdi=app.state.pdi)

    # ---- social-platform connections --------------------------------------
    # collect posts to inform guidance, or publish an update reachable by QR.

    @app.post("/social/{user_id}", status_code=201)
    def social_connect(user_id: str, body: SocialConnect, request: Request) -> dict:
        _user_or_404(user_id, request)
        return social.connect(user_id, body.platform, body.direction,
                              body.handle, body.scope)

    @app.get("/social/{user_id}")
    def social_list(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return social.for_user(user_id)

    def _social_or_404(cid: str, request: Request) -> dict:
        row = social.get(cid)
        if row is None:
            raise HTTPException(404, "social connection not found")
        _user_or_404(row["user_id"], request)   # enforce the owner's token
        return row

    @app.delete("/social/connection/{cid}")
    def social_revoke(cid: str, request: Request) -> dict:
        return social.revoke(_social_or_404(cid, request))

    @app.post("/social/connection/{cid}/collect", status_code=201)
    def social_collect(cid: str, body: SocialCollect, request: Request) -> dict:
        row = _social_or_404(cid, request)
        if row["direction"] != "collect":
            raise HTTPException(409, "this connection is for publishing, not collecting")
        if row["status"] != "active":
            raise HTTPException(409, "connection has been revoked")
        return social.collect(row, [i.model_dump() for i in body.items],
                              pdi=app.state.pdi)

    @app.post("/social/connection/{cid}/publish", status_code=201)
    def social_publish(cid: str, body: SocialPublish, request: Request) -> dict:
        row = _social_or_404(cid, request)
        if row["direction"] != "publish":
            raise HTTPException(409, "this connection is for collecting, not publishing")
        if row["status"] != "active":
            raise HTTPException(409, "connection has been revoked")
        return social.publish(row, body.content, body.topic)

    @app.get("/social/connection/{cid}/beacon")
    def social_beacon(cid: str, request: Request) -> dict:
        row = _social_or_404(cid, request)
        if row["direction"] != "publish":
            raise HTTPException(409, "beacons are for publish connections")
        return {"connection": cid, "platform": row["platform"],
                "handle": f"@{row['handle']}" if row["handle"] else None,
                "presence_url": social.presence_url(row, _public_base()),
                "qr_svg": f"/social/connection/{cid}/qr.svg"}

    @app.get("/social/connection/{cid}/qr.svg")
    def social_qr(cid: str, request: Request) -> Response:
        row = _social_or_404(cid, request)
        if row["direction"] != "publish":
            raise HTTPException(409, "beacons are for publish connections")
        import segno
        buf = io.BytesIO()
        segno.make(social.presence_url(row, _public_base()), error="q").save(
            buf, kind="svg", scale=8, border=2, dark="#161840", light="#F4E3C8")
        return Response(content=buf.getvalue(), media_type="image/svg+xml")

    # ---- mood & energy check-ins ------------------------------------------

    @app.post("/checkin/{user_id}", status_code=201)
    def check_in(user_id: str, body: CheckIn, request: Request) -> dict:
        _user_or_404(user_id, request)
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
    def get_goals(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return life.goals(user_id)

    @app.post("/goals/{user_id}", status_code=201)
    def add_goal(user_id: str, body: GoalCreate, request: Request) -> dict:
        _user_or_404(user_id, request)
        return life.add_goal(user_id, body.area, body.title, body.target)

    @app.patch("/goals/{user_id}/{goal_id}")
    def update_goal(user_id: str, goal_id: str, body: GoalUpdate,
                    request: Request) -> dict:
        _user_or_404(user_id, request)
        updated = life.update_goal(user_id, goal_id, body.progress, body.status)
        if updated is None:
            raise HTTPException(404, "goal not found")
        return updated

    # ---- habits & streaks -------------------------------------------------

    @app.get("/habits/{user_id}")
    def get_habits(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return life.habits(user_id)

    @app.post("/habits/{user_id}", status_code=201)
    def add_habit(user_id: str, body: HabitCreate, request: Request) -> dict:
        _user_or_404(user_id, request)
        return life.add_habit(user_id, body.name)

    @app.post("/habits/{user_id}/{habit_id}/log")
    def log_habit(user_id: str, habit_id: str, request: Request,
                  body: HabitLog | None = None) -> dict:
        _user_or_404(user_id, request)
        logged = life.log_habit(user_id, habit_id, body.day if body else None)
        if logged is None:
            raise HTTPException(404, "habit not found")
        return logged

    # ---- life coach & insights --------------------------------------------

    @app.post("/coach/{user_id}")
    def coach_reply(user_id: str, body: CoachMessage, request: Request) -> dict:
        _user_or_404(user_id, request)
        return coach.reply(user_id, body.area, body.message)

    @app.get("/coach/{user_id}")
    def coach_history(user_id: str, request: Request,
                      area: str | None = None) -> list[dict]:
        _user_or_404(user_id, request)
        return coach.history(user_id, area)

    @app.get("/insights/{user_id}")
    def get_insights(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return life.insights(user_id)

    @app.post("/companion/{user_id}")
    def companion_checkin(user_id: str, request: Request) -> dict:
        """An ambient, unprompted check-in from the coach — grounded in the
        user's latest mood, goals, and personality preferences."""
        _user_or_404(user_id, request)
        return coach.companion_checkin(user_id)

    # ---- journal, feedback, reports, provider portal ----------------------

    @app.post("/journal/{user_id}", status_code=201)
    def add_journal(user_id: str, body: JournalEntry, request: Request) -> dict:
        _user_or_404(user_id, request)
        result = life.add_journal(user_id, body.text, pdi=app.state.pdi)
        # Journal text runs the same crisis pipeline as check-in notes.
        result["guardian"] = guardian.monitor(
            user_id, {}, body.text, qrme=app.state.qrme, pdi=app.state.pdi)
        return result

    @app.get("/journal/{user_id}")
    def get_journal(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return life.journal_entries(user_id, pdi=app.state.pdi)

    @app.post("/feedback/{user_id}", status_code=201)
    def add_feedback(user_id: str, body: GuidanceFeedback,
                     request: Request) -> dict:
        user = _user_or_404(user_id, request)
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
    def progress_report(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return life.progress_report(user_id)

    @app.get("/access-log/{user_id}")
    def access_log(user_id: str, request: Request) -> dict:
        """See who accessed my data: every access to the user's sealed vault
        records, filtered to their own namespace and verifiable against PDI's
        tamper-evident audit chain."""
        _user_or_404(user_id, request)
        return life.access_log(user_id, pdi=app.state.pdi)

    @app.get("/provider/{user_id}")
    def provider_portal(user_id: str, request: Request) -> dict:
        user = _user_or_404(user_id, request)
        if not user.get("provider_consent"):
            raise HTTPException(
                403, "the user has not consented to provider access")
        return life.provider_summary(user)

    # ---- erasure ("delete anything, anytime") -----------------------------

    @app.delete("/data/{user_id}")
    def delete_data(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        result = life.delete_user_data(user_id, pdi=app.state.pdi)
        auth.revoke_subject(user_id)   # the user token dies with the data
        return result

    return app


app = create_app()
