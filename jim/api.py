"""JIM-mini HTTP API — the standalone personal-guidance service."""

from __future__ import annotations

import io
import json
import os
from datetime import date, datetime

from fastapi import FastAPI, HTTPException, Request, Response

from . import (app_connectors, auth, catalog, coach, db, escalation, guardian,
               life, llm, research, robotics, social)
from .models import (
    ActivityObserve, AppCollect, AppConnect, AppInvoke, BiometricSample, CheckIn,
    CoachMessage, ConditionDeclare, ContextEvent, DeviceRegister, EmergencyRequest,
    Enroll, ExcursionStart, GoalCreate, GoalUpdate, GuidanceFeedback, HabitCreate,
    HabitLog, JournalEntry, ModelChoice, PersonalityUpdate, RobotBind,
    RobotCommand, WaiverSign,
    SensitivitySet, SessionStart, SocialCollect, SocialConnect, SocialPublish,
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

    @app.get("/connectors/catalog")
    def connector_catalog() -> dict:
        """The connected-apps catalog: the AI-integrated apps (Apple, Google,
        Microsoft, Canva) the Guardian and its agents can connect to."""
        return catalog.catalog()

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

    @app.get("/models")
    def list_models() -> dict:
        """Every LLM provider JIM knows about, with whether it is configured in
        this deployment, so a settings screen can enable/disable choices."""
        return {"providers": llm.available(), "default": llm.default_name()}

    @app.get("/model/{user_id}")
    def get_user_model(user_id: str, request: Request) -> dict:
        """The user's stored provider preference and what it resolves to now."""
        _user_or_404(user_id, request)
        choice = llm.get_choice(user_id)
        return {"user_id": user_id, "provider": choice,
                "effective": llm.resolve_choice(choice)}

    @app.put("/model/{user_id}")
    def set_user_model(user_id: str, body: ModelChoice,
                       request: Request) -> dict:
        """Choose which LLM powers this user's coaching and guidance."""
        _user_or_404(user_id, request)
        if body.provider not in llm.CHOICES:
            raise HTTPException(
                422, f"provider must be one of {', '.join(llm.CHOICES)}")
        llm.set_choice(user_id, body.provider)
        return {"user_id": user_id, "provider": body.provider,
                "effective": llm.resolve_choice(body.provider)}

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

    # ---- robot helpers (guardian responders) ------------------------------

    @app.get("/robotics/catalog")
    def robotics_catalog() -> dict:
        """Every supported robot platform, with per-kind command allowlists and
        the directive each kind receives on an escalation. Public registry."""
        return robotics.catalog()

    @app.post("/robots/{user_id}", status_code=201)
    def bind_robot(user_id: str, body: RobotBind, request: Request) -> dict:
        """Bind a catalog robot as a guardian responder: it registers as a
        device (escalation alerts dispatch to it) and receives a role-specific
        directive when the Guardian escalates."""
        _user_or_404(user_id, request)
        try:
            return guardian.bind_robot(user_id, body.model, body.name,
                                       body.llm_provider)
        except ValueError as e:
            raise HTTPException(422 if "llm" in str(e).lower() else 404, str(e))

    @app.get("/robots/{user_id}")
    def list_robots(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return guardian.robots_for(user_id)

    @app.delete("/robots/{user_id}/{robot_id}")
    def unbind_robot(user_id: str, robot_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        result = guardian.unbind_robot(user_id, robot_id)
        if result is None:
            raise HTTPException(404, "robot not found")
        return result

    @app.get("/waivers/{user_id}")
    def get_waiver(user_id: str, request: Request) -> dict:
        """The autonomous-resuscitation waiver: its terms, and whether this
        user has one signed. Automatic CPR starts and fully-automatic AED
        operation stay locked until it is signed."""
        _user_or_404(user_id, request)
        waiver = guardian.waiver_for(user_id)
        return {"kind": guardian.WAIVER_KIND, "terms": guardian.WAIVER_TERMS,
                "signed": waiver is not None,
                "signature": waiver["signature"] if waiver else None,
                "signed_at": waiver["signed_at"] if waiver else None}

    @app.post("/waivers/{user_id}", status_code=201)
    def sign_waiver(user_id: str, body: WaiverSign, request: Request) -> dict:
        user = _user_or_404(user_id, request)
        if not body.accept:
            raise HTTPException(403, "the waiver terms must be explicitly "
                                     "accepted")
        signature = body.signature.strip()
        if not signature:
            raise HTTPException(422, "a typed legal-name signature is "
                                     "required")
        expected = (user.get("display_name") or "").strip().lower()
        if expected and signature.lower() != expected:
            raise HTTPException(
                422, f"signature must match the enrolled name "
                     f"({user['display_name']})")
        return guardian.sign_waiver(user_id, signature)

    @app.delete("/waivers/{user_id}")
    def revoke_waiver(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        if not guardian.revoke_waiver(user_id):
            raise HTTPException(404, "no signed waiver on file")
        return {"kind": guardian.WAIVER_KIND, "signed": False,
                "note": "confirm-gated operation restored"}

    @app.post("/robots/{user_id}/{robot_id}/command", status_code=201)
    def command_robot(user_id: str, robot_id: str, body: RobotCommand,
                      request: Request) -> dict:
        """Send one allowlisted command to a bound robot. First-aid commands
        follow the body's rating: assist-rated platforms fetch the AED, coach
        the playbook aloud, and meet responders; perform-rated platforms may
        additionally deliver chest compressions — but only after a person on
        scene confirms (perform_cpr is a two-step), and never a shock: the
        AED analyzes the rhythm and a human presses the button."""
        _user_or_404(user_id, request)
        try:
            result = guardian.robot_command(user_id, robot_id,
                                            body.command, body.arg)
        except ValueError as exc:
            raise HTTPException(422, str(exc))
        if result is None:
            raise HTTPException(404, "robot not found")
        return result

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

    @app.get("/escalation-policy/{user_id}")
    def escalation_policy(user_id: str, request: Request) -> dict:
        """Transparency: how this user's sensitivity resolves each severity to
        an escalation tier, and the safety floors no dial can lower — shown
        before anything happens, so the behavior is never a surprise."""
        user = _user_or_404(user_id, request)
        level = (user or {}).get("sensitivity") or "balanced"
        return escalation.policy(level)

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

    # ---- connected-app connectors -----------------------------------------
    # connect a catalog app; agents collect context, act, or produce with it.

    @app.post("/apps/{user_id}", status_code=201)
    def app_connect(user_id: str, body: AppConnect, request: Request) -> dict:
        _user_or_404(user_id, request)
        e = app_connectors.entry(body.provider, body.app)
        if e is None:
            raise HTTPException(404, f"unknown connector: {body.provider}/{body.app}")
        unknown = set(body.capabilities) - set(e["capabilities"])
        if unknown:
            raise HTTPException(422, f"{body.app} does not offer: {sorted(unknown)}")
        return app_connectors.connect(user_id, e, body.capabilities)

    @app.get("/apps/{user_id}")
    def app_list(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return app_connectors.for_user(user_id)

    def _app_or_404(cid: str, request: Request) -> dict:
        row = app_connectors.get(cid)
        if row is None:
            raise HTTPException(404, "app connector not found")
        _user_or_404(row["user_id"], request)
        return row

    @app.delete("/apps/connector/{cid}")
    def app_revoke(cid: str, request: Request) -> dict:
        return app_connectors.revoke(_app_or_404(cid, request))

    @app.post("/apps/connector/{cid}/collect", status_code=201)
    def app_collect(cid: str, body: AppCollect, request: Request) -> dict:
        row = _app_or_404(cid, request)
        if "collect" not in json.loads(row["directions"]):
            raise HTTPException(409, f"{row['app']} does not support collecting context")
        if row["status"] != "active":
            raise HTTPException(409, "connector has been revoked")
        return app_connectors.collect(row, [i.model_dump() for i in body.items],
                                      pdi=app.state.pdi)

    @app.post("/apps/connector/{cid}/invoke", status_code=201)
    def app_invoke(cid: str, body: AppInvoke, request: Request) -> dict:
        row = _app_or_404(cid, request)
        if row["status"] != "active":
            raise HTTPException(409, "connector has been revoked")
        if body.capability not in json.loads(row["capabilities"]):
            raise HTTPException(422, f"this {row['app']} connector was not granted "
                                     f"'{body.capability}'")
        return app_connectors.invoke(row, body.capability, body.input)

    # ---- safe knowledge excursions ----------------------------------------
    # study an unfamiliar topic without carrying the user's PHI out.

    def _excursion_row(cid: str) -> dict:
        row = db.connect().execute(
            "SELECT * FROM excursions WHERE id=?", (cid,)).fetchone()
        if row is None:
            raise HTTPException(404, "excursion not found")
        return dict(row)

    def _excursion_out(row: dict) -> dict:
        return {"id": row["id"], "user_id": row["user_id"], "topic": row["topic"],
                "brief": row["brief"], "redactions": row["redactions"],
                "left_host": bool(row["left_host"]), "findings": row["findings"],
                "learned": bool(row["learned"])}

    @app.post("/excursions/{user_id}", status_code=201)
    def start_excursion(user_id: str, body: ExcursionStart, request: Request) -> dict:
        _user_or_404(user_id, request)
        cloud = app.state.cloud
        brief, redactions = research.sanitize(
            user_id, f"{body.topic}\n{body.question}", body.private)
        left_host = research.would_leave(cloud)
        findings = research.gather(brief, cloud)
        cid = db.new_id("exc")
        db.connect().execute(
            "INSERT INTO excursions (id, user_id, topic, brief, redactions,"
            " left_host, findings, learned, created_at) VALUES (?,?,?,?,?,?,?,0,?)",
            (cid, user_id, body.topic, brief, redactions, int(left_host),
             findings, db.utcnow()))
        db.connect().commit()
        return _excursion_out(_excursion_row(cid))

    @app.get("/excursions/{user_id}")
    def list_excursions(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        rows = db.connect().execute(
            "SELECT * FROM excursions WHERE user_id=? ORDER BY created_at, rowid",
            (user_id,)).fetchall()
        return [_excursion_out(dict(r)) for r in rows]

    @app.get("/excursions/entry/{cid}")
    def get_excursion(cid: str, request: Request) -> dict:
        row = _excursion_row(cid)
        _user_or_404(row["user_id"], request)
        return _excursion_out(row)

    @app.post("/excursions/entry/{cid}/learn", status_code=201)
    def learn_excursion(cid: str, request: Request) -> dict:
        row = _excursion_row(cid)
        _user_or_404(row["user_id"], request)
        if not row["findings"]:
            raise HTTPException(409, "this excursion has no findings to learn")
        if row["learned"]:
            return {"learned": True, "already_learned": True}
        life.add_context(row["user_id"], "research", "knowledge",
                         {"topic": row["topic"], "content": row["findings"]},
                         pdi=app.state.pdi)
        db.connect().execute("UPDATE excursions SET learned=1 WHERE id=?", (cid,))
        db.connect().commit()
        return {"learned": True, "already_learned": False,
                "note": "findings folded into guidance context; the local model now uses them"}

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
