"""HTTP API and web app for both modules.

    /                 Personal Cleaner (Module A) web app
    /console          Platform Purge Console (Module B)
    /appeal/{token}   Public appeals portal for affected users

Run: ``python -m botcleaner`` (or ``uvicorn --factory botcleaner.api:create_app``).
"""

import os
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, RedirectResponse
from pydantic import BaseModel, Field

from . import security as sec
from .connectors import x as xapi
from .db import DB
from .importers import EXPORT_HELP, ImportError_, import_export
from .instructions_store import InstructionStore
from .models import Platform
from .personal import NotFound, PersonalService
from .purge.console import PurgeService, Rule
from .purge.signals import SiteAccount
from .removal import RemovalService, modes_for

WEB = Path(__file__).parent / "web"


class Services:
    def __init__(self, db: DB, purge_enforcer=None, x_http=None):
        self.db = db
        self.personal = PersonalService(db)
        self.instructions = InstructionStore(db)
        self.x_http = x_http
        self.removal = RemovalService(db, self.personal, x_client_for=self.x_client_for)
        self.purge = PurgeService(db, enforcer=purge_enforcer)

    def x_client_for(self, user_id: str):
        tok = self.db.one("SELECT sealed FROM secrets WHERE user_id=? AND name='x_access_token'", (user_id,))
        me = self.db.one("SELECT sealed FROM secrets WHERE user_id=? AND name='x_user_id'", (user_id,))
        if not tok or not me:
            raise RuntimeError("X is not connected")
        return (xapi.XClient(sec.unseal(tok["sealed"], f"{user_id}:x_access_token"), http=self.x_http),
                sec.unseal(me["sealed"], f"{user_id}:x_user_id"))

    def save_secret(self, user_id: str, name: str, value: str) -> None:
        self.db.x("INSERT OR REPLACE INTO secrets VALUES (?,?,?)", (user_id, name, sec.seal(value, f"{user_id}:{name}")))

    def sync_x(self, user_id: str) -> dict:
        client, me = self.x_client_for(user_id)
        conns = client.connections(me)
        rec = self.personal.store_connections(user_id, Platform.x, conns)
        return {"imported": len(conns), "reconciled": rec, **self.personal.scan(user_id, "x")}

    # ---- background work ---------------------------------------------------------------

    def tick(self) -> dict:
        """One pass of the worker: one-click removals, purge batches, retention, rescans."""
        done = {"one_click": 0, "batches": 0, "purged_raw": 0, "rescans": 0}
        for j in self.db.q("SELECT id, user_id FROM removal_jobs WHERE state='running' AND mode='one_click'"):
            try:
                self.removal.run_one_click(j["user_id"], j["id"], max_items=10)
                done["one_click"] += 1
            except Exception:
                pass
        for b in self.db.q("SELECT tenant_id, id, actor FROM t_batches WHERE state='running'"):
            self.purge.step(b["tenant_id"], b["id"], b["actor"])
            done["batches"] += 1
        done["purged_raw"] = self.personal.purge_raw()
        for uid in self.personal.due_rescans():
            done["rescans"] += 1
            if self.db.one("SELECT 1 FROM secrets WHERE user_id=? AND name='x_access_token'", (uid,)):
                try:
                    self.sync_x(uid)
                except Exception:
                    pass
        return done


def create_app(db_path: Optional[str] = None, purge_enforcer=None, x_http=None, worker: Optional[bool] = None) -> FastAPI:
    svc = Services(DB(db_path), purge_enforcer=purge_enforcer, x_http=x_http)
    admin_token = os.environ.get("BOTCLEANER_ADMIN_TOKEN")
    run_worker = worker if worker is not None else os.environ.get("BOTCLEANER_WORKER", "1") == "1"

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if run_worker:  # pragma: no cover - background thread
            def loop():
                while True:
                    try:
                        svc.tick()
                    except Exception:
                        pass
                    time.sleep(float(os.environ.get("BOTCLEANER_TICK_SECONDS", "20")))

            threading.Thread(target=loop, daemon=True).start()
        yield

    app = FastAPI(title="Bot Account Cleaner", version="0.1.0", lifespan=lifespan)
    app.state.svc = svc

    # ---- errors ---------------------------------------------------------------------

    @app.exception_handler(NotFound)
    @app.exception_handler(LookupError)
    async def _nf(_: Request, exc: Exception):
        return JSONResponse({"detail": str(exc) or "not found"}, status_code=404)

    @app.exception_handler(ValueError)
    async def _bad(_: Request, exc: Exception):
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @app.exception_handler(PermissionError)
    async def _forbidden(_: Request, exc: Exception):
        return JSONResponse({"detail": str(exc)}, status_code=403)

    # ---- auth -------------------------------------------------------------------------

    def user(authorization: str = Header(default="")) -> str:
        token = authorization.removeprefix("Bearer ").strip()
        uid = svc.personal.auth(token) if token else None
        if not uid:
            raise HTTPException(401, "Sign in first")
        return uid

    def admin(x_admin_token: str = Header(default="")) -> None:
        if not admin_token or not sec.token_matches(x_admin_token, sec.hash_token(admin_token)):
            raise HTTPException(401, "Admin token required")

    def tenant(x_api_key: str = Header(default="")) -> tuple[str, str, str]:
        found = svc.purge.auth(x_api_key) if x_api_key else None
        if not found:
            raise HTTPException(401, "API key required")
        return found

    def owner(t: tuple = Depends(tenant)) -> tuple[str, str, str]:
        if t[1] != "owner":
            raise HTTPException(403, "Owner key required")
        return t

    # ---- pages ----------------------------------------------------------------------------

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(WEB / "index.html")

    @app.get("/console", include_in_schema=False)
    def console_page():
        return FileResponse(WEB / "console.html")

    @app.get("/appeal/{token}", include_in_schema=False)
    def appeal_page(token: str):
        return FileResponse(WEB / "appeal.html")

    @app.get("/static/{name}", include_in_schema=False)
    def static(name: str):
        p = (WEB / name).resolve()
        if p.parent != WEB.resolve() or not p.exists():
            raise HTTPException(404)
        return FileResponse(p)

    @app.get("/api/health")
    def health():
        return {"ok": True}

    # =========================== Module A ===========================

    class SignupIn(BaseModel):
        email: str
        guardian_of: Optional[str] = None
        teen_consent: bool = False

    @app.post("/api/signup")
    def signup(body: SignupIn):
        uid, token = svc.personal.register(body.email, body.guardian_of, body.teen_consent)
        return {"user_id": uid, "token": token}

    @app.get("/api/me/dashboard")
    def dashboard(uid: str = Depends(user)):
        d = svc.personal.dashboard(uid)
        d["x_connected"] = bool(svc.db.one("SELECT 1 FROM secrets WHERE user_id=? AND name='x_access_token'", (uid,)))
        return d

    @app.delete("/api/me")
    def delete_me(uid: str = Depends(user)):
        svc.personal.delete_everything(uid)
        return {"deleted": True}

    @app.get("/api/import/help")
    def import_help():
        return EXPORT_HELP

    @app.post("/api/import/{platform}")
    async def import_file(platform: Platform, file: UploadFile = File(...), uid: str = Depends(user)):
        data = await file.read()
        try:
            conns = import_export(platform, file.filename or "upload", data)
        except ImportError_ as exc:
            raise HTTPException(400, str(exc))
        finally:
            del data  # raw export is never persisted
        rec = svc.personal.store_connections(uid, platform, conns)
        result = svc.personal.scan(uid, platform.value)
        return {"imported": len(conns), "reconciled": rec, **result}

    # X OAuth (PKCE)
    @app.get("/api/x/connect")
    def x_connect(request: Request, uid: str = Depends(user)):
        client_id = os.environ.get("X_CLIENT_ID")
        if not client_id:
            raise HTTPException(503, "X integration isn't configured on this server (set X_CLIENT_ID)")
        pkce = xapi.PKCE.new()
        svc.db.x("INSERT INTO oauth_pending VALUES (?,?,?,?)", (pkce.state, uid, pkce.verifier, sec.iso()))
        redirect = os.environ.get("X_REDIRECT_URI", str(request.url_for("x_callback")))
        return {"authorize_url": xapi.authorize_url(client_id, redirect, pkce)}

    @app.get("/api/x/callback", name="x_callback")
    def x_callback(request: Request, code: str, state: str):
        row = svc.db.one("SELECT * FROM oauth_pending WHERE state=?", (state,))
        if not row:
            raise HTTPException(400, "Unknown or expired sign-in attempt")
        svc.db.x("DELETE FROM oauth_pending WHERE state=?", (state,))
        redirect = os.environ.get("X_REDIRECT_URI", str(request.url_for("x_callback")))
        tok = xapi.XClient.exchange_code(os.environ["X_CLIENT_ID"], code, redirect, row["verifier"], http=svc.x_http)
        client = xapi.XClient(tok["access_token"], http=svc.x_http)
        me = client.me()
        svc.save_secret(row["user_id"], "x_access_token", tok["access_token"])
        if tok.get("refresh_token"):
            svc.save_secret(row["user_id"], "x_refresh_token", tok["refresh_token"])
        svc.save_secret(row["user_id"], "x_user_id", str(me["id"]))
        svc.sync_x(row["user_id"])
        return RedirectResponse("/?connected=x")

    @app.post("/api/x/sync")
    def x_sync(uid: str = Depends(user)):
        try:
            return svc.sync_x(uid)
        except RuntimeError as exc:
            raise HTTPException(400, str(exc))

    @app.delete("/api/x")
    def x_disconnect(uid: str = Depends(user)):
        svc.db.x("DELETE FROM secrets WHERE user_id=? AND name LIKE 'x_%'", (uid,))
        return {"disconnected": True}

    class ScanIn(BaseModel):
        platform: Optional[Platform] = None

    @app.post("/api/scan")
    def scan(body: ScanIn, uid: str = Depends(user)):
        return svc.personal.scan(uid, body.platform.value if body.platform else None)

    @app.get("/api/flags")
    def flags(platform: Optional[Platform] = None, direction: Optional[str] = None, tab: str = "likely_bot",
              sort: str = "score", reason: Optional[str] = None, limit: int = Query(500, le=2000), offset: int = 0,
              uid: str = Depends(user)):
        return svc.personal.list_flags(uid, platform.value if platform else None, direction, tab, sort, reason, limit, offset)

    @app.get("/api/flags/{platform}/{direction}/{account_id}")
    def flag(platform: Platform, direction: str, account_id: str, uid: str = Depends(user)):
        return svc.personal.get_flag(uid, platform.value, account_id, direction)

    class FeedbackIn(BaseModel):
        platform: Platform
        account_id: str
        is_bot: bool

    @app.post("/api/feedback")
    def feedback(body: FeedbackIn, uid: str = Depends(user)):
        return svc.personal.feedback(uid, body.platform.value, body.account_id, body.is_bot)

    class AccountRef(BaseModel):
        platform: Platform
        account_id: str
        direction: str = "follower"

    @app.post("/api/whitelist/remove")
    def unwhitelist(body: AccountRef, uid: str = Depends(user)):
        svc.personal.unwhitelist(uid, body.platform.value, body.account_id)
        return {"ok": True}

    class RemovalIn(BaseModel):
        platform: Platform
        accounts: list[dict]
        mode: Optional[str] = None

    @app.get("/api/removals/modes/{platform}")
    def removal_modes(platform: Platform):
        return {"modes": modes_for(platform.value)}

    @app.post("/api/removals")
    def create_removal(body: RemovalIn, uid: str = Depends(user)):
        return svc.removal.create_job(uid, body.platform.value, body.accounts, body.mode)

    @app.get("/api/removals")
    def list_removals(uid: str = Depends(user)):
        return svc.removal.jobs(uid)

    @app.get("/api/removals/{job_id}")
    def get_removal(job_id: str, uid: str = Depends(user)):
        return svc.removal.job(uid, job_id)

    class StateIn(BaseModel):
        state: str

    @app.post("/api/removals/{job_id}/state")
    def removal_state(job_id: str, body: StateIn, uid: str = Depends(user)):
        return svc.removal.set_state(uid, job_id, body.state)

    @app.post("/api/removals/{job_id}/run")
    def removal_run(job_id: str, uid: str = Depends(user)):
        try:
            job = svc.removal.run_one_click(uid, job_id, max_items=10)
        except RuntimeError as exc:
            raise HTTPException(400, str(exc))
        if job["state"] == "done":
            try:
                job = svc.removal.recheck_x(uid, job_id)
            except Exception:
                pass
        return job

    @app.get("/api/removals/{job_id}/next")
    def removal_next(job_id: str, device: str = "web", uid: str = Depends(user)):
        return svc.removal.next_assisted(uid, job_id, device)

    class ConfirmIn(BaseModel):
        outcome: str

    @app.post("/api/removals/{job_id}/items/{idx}/confirm")
    def removal_confirm(job_id: str, idx: int, body: ConfirmIn, uid: str = Depends(user)):
        return svc.removal.confirm(uid, job_id, idx, body.outcome)

    @app.get("/api/removals/{job_id}/guided")
    def removal_guided(job_id: str, device: str = "web", uid: str = Depends(user)):
        return svc.removal.guided(uid, job_id, device)

    # Instructions (A6/A7)
    @app.get("/api/instructions")
    def instructions(platform: Optional[str] = None, device: Optional[str] = None, action: Optional[str] = None,
                     authorization: str = Header(default="")):
        uid = svc.personal.auth(authorization.removeprefix("Bearer ").strip()) if authorization else None
        return svc.instructions.list(platform, device, action, uid)

    @app.get("/api/instructions/best")
    def best_instructions(platform: str, device: str, action: str, uid: str = Depends(user)):
        return svc.instructions.best(platform, device, action, uid)

    class InstructionIn(BaseModel):
        platform: str
        device: str
        action: str
        steps: list[str]
        app_version: str = ""
        screenshots: list[str] = Field(default_factory=list)
        share: bool = False
        replaces: Optional[str] = None

    @app.post("/api/instructions")
    def submit_instructions(body: InstructionIn, uid: str = Depends(user)):
        return svc.instructions.submit(uid, **body.model_dump())

    @app.post("/api/instructions/{iid}/outdated")
    def flag_instructions(iid: str, uid: str = Depends(user)):
        return svc.instructions.flag_outdated(iid, uid)

    @app.get("/api/admin/instructions/pending", dependencies=[Depends(admin)])
    def pending_instructions():
        return svc.instructions.pending()

    class ModerateIn(BaseModel):
        approve: bool

    @app.post("/api/admin/instructions/{iid}/moderate", dependencies=[Depends(admin)])
    def moderate_instructions(iid: str, body: ModerateIn):
        return svc.instructions.moderate(iid, body.approve)

    # Alerts, schedule, export, undo
    @app.get("/api/alerts")
    def alerts(uid: str = Depends(user)):
        return svc.personal.alerts(uid)

    @app.post("/api/alerts/read")
    def alerts_read(uid: str = Depends(user)):
        svc.personal.mark_alerts_read(uid)
        return {"ok": True}

    class RescanIn(BaseModel):
        cadence: str

    @app.post("/api/rescan")
    def rescan(body: RescanIn, uid: str = Depends(user)):
        return svc.personal.set_rescan(uid, body.cadence)

    @app.get("/api/export.csv")
    def export_csv(uid: str = Depends(user)):
        return PlainTextResponse(svc.personal.export_csv(uid), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=bot-cleaner-log.csv"})

    @app.get("/api/undo-log")
    def undo_log(event: Optional[str] = None, uid: str = Depends(user)):
        return svc.personal.undo_log(uid, event)

    @app.post("/api/undo/readded")
    def readded(body: AccountRef, uid: str = Depends(user)):
        svc.personal.mark_readded(uid, body.platform.value, body.account_id, body.direction)
        return {"ok": True}

    # =========================== Module B ===========================

    class TenantIn(BaseModel):
        name: str
        config: dict = Field(default_factory=dict)

    @app.post("/api/purge/tenants")
    def create_tenant(body: TenantIn, x_admin_token: str = Header(default="")):
        if admin_token and not sec.token_matches(x_admin_token, sec.hash_token(admin_token)):
            raise HTTPException(401, "Admin token required to create a tenant")
        tid, key = svc.purge.create_tenant(body.name, body.config)
        return {"tenant_id": tid, "api_key": key}

    @app.get("/api/purge/me")
    def purge_me(t=Depends(tenant)):
        name = svc.db.one("SELECT name FROM tenants WHERE id=?", (t[0],))["name"]
        return {"tenant_id": t[0], "name": name, "role": t[1], "actor": t[2]}

    @app.get("/api/purge/config")
    def get_config(t=Depends(tenant)):
        return svc.purge.config(t[0])

    @app.patch("/api/purge/config")
    def patch_config(patch: dict[str, Any], t=Depends(owner)):
        return svc.purge.set_config(t[0], patch)

    class ReviewerIn(BaseModel):
        name: str

    @app.post("/api/purge/reviewers")
    def add_reviewer(body: ReviewerIn, t=Depends(owner)):
        return svc.purge.add_reviewer(t[0], body.name)

    @app.post("/api/purge/accounts")
    def ingest(accounts: list[SiteAccount], t=Depends(owner)):
        return svc.purge.ingest(t[0], accounts)

    @app.post("/api/purge/accounts/csv")
    async def ingest_csv(file: UploadFile = File(...), t=Depends(owner)):
        text = (await file.read()).decode("utf-8-sig")
        return svc.purge.ingest(t[0], svc.purge.parse_csv(text))

    @app.post("/api/purge/scan")
    def purge_scan(t=Depends(owner)):
        return svc.purge.scan(t[0])

    @app.get("/api/purge/accounts")
    def explore(min_score: float = 0, max_score: float = 100, reason: Optional[str] = None, ring_id: Optional[str] = None,
                state: Optional[str] = None, signup_after: Optional[str] = None, signup_before: Optional[str] = None,
                limit: int = Query(200, le=2000), offset: int = 0, t=Depends(tenant)):
        return svc.purge.explore(t[0], min_score, max_score, reason, ring_id, state, signup_after, signup_before, limit, offset)

    @app.get("/api/purge/rings")
    def rings(t=Depends(tenant)):
        return svc.purge.rings(t[0])

    @app.get("/api/purge/sample")
    def sample(per_label: int = 10, t=Depends(tenant)):
        return svc.purge.sample(t[0], per_label)

    class ReviewIn(BaseModel):
        is_bot: bool
        note: str = ""

    @app.post("/api/purge/accounts/{account_id}/review")
    def review(account_id: str, body: ReviewIn, t=Depends(tenant)):
        return svc.purge.mark_reviewed(t[0], account_id, t[2], body.is_bot, body.note)

    @app.post("/api/purge/accounts/{account_id}/verified")
    def verified(account_id: str, t=Depends(owner)):
        return svc.purge.report_verified(t[0], account_id)

    @app.get("/api/purge/accounts/{account_id}/notice")
    def account_notice(account_id: str, t=Depends(tenant)):
        return svc.purge.notice_for_account(t[0], account_id)

    @app.get("/api/purge/rules")
    def list_rules(t=Depends(tenant)):
        return svc.purge.rules(t[0])

    @app.post("/api/purge/rules")
    def put_rule(rule: Rule, t=Depends(owner)):
        return svc.purge.put_rule(t[0], rule)

    @app.delete("/api/purge/rules/{rule_id}")
    def delete_rule(rule_id: str, t=Depends(owner)):
        svc.purge.delete_rule(t[0], rule_id)
        return {"ok": True}

    class DryRunIn(BaseModel):
        rules: list[Rule] = Field(default_factory=list)
        only_tiers: Optional[list[int]] = None

    @app.post("/api/purge/dry-run")
    def dry_run(body: DryRunIn, t=Depends(owner)):
        return svc.purge.dry_run(t[0], t[2], body.rules, body.only_tiers)

    @app.get("/api/purge/batches")
    def batches(t=Depends(tenant)):
        return svc.purge.batches(t[0])

    @app.get("/api/purge/batches/{bid}")
    def get_batch(bid: str, t=Depends(tenant)):
        return {**svc.purge.batch(t[0], bid), **svc.purge.batch_status(t[0], bid)}

    @app.post("/api/purge/batches/{bid}/execute")
    def execute(bid: str, t=Depends(owner)):
        return svc.purge.execute(t[0], bid, t[2])

    @app.post("/api/purge/batches/{bid}/step")
    def step(bid: str, t=Depends(owner)):
        return svc.purge.step(t[0], bid, t[2])

    @app.post("/api/purge/batches/{bid}/pause")
    def pause(bid: str, t=Depends(owner)):
        return svc.purge.pause(t[0], bid, t[2])

    @app.post("/api/purge/batches/{bid}/rollback")
    def rollback(bid: str, t=Depends(owner)):
        return svc.purge.rollback(t[0], bid, t[2])

    @app.get("/api/purge/feed")
    def feed(since: int = 0, t=Depends(owner)):
        return svc.purge.enforcement_feed(t[0], since)

    @app.get("/api/purge/appeals")
    def appeals(status: str = "open", t=Depends(tenant)):
        return svc.purge.appeal_queue(t[0], status)

    class DecideIn(BaseModel):
        approve: bool
        note: str = ""

    @app.post("/api/purge/appeals/{appeal_id}/decide")
    def decide(appeal_id: str, body: DecideIn, t=Depends(tenant)):
        return svc.purge.decide(t[0], appeal_id, t[2], body.approve, body.note)

    @app.get("/api/purge/removal-candidates")
    def removal_candidates(t=Depends(tenant)):
        return svc.purge.removal_candidates(t[0])

    class RemoveIn(BaseModel):
        account_ids: list[str]

    @app.post("/api/purge/remove-permanently")
    def remove_permanently(body: RemoveIn, t=Depends(tenant)):
        return svc.purge.remove_permanently(t[0], body.account_ids, t[2])

    @app.post("/api/purge/gate")
    def gate(signup: SiteAccount, t=Depends(owner)):
        return svc.purge.gate_signup(t[0], signup)

    @app.get("/api/purge/report")
    def report(days: int = 30, t=Depends(tenant)):
        return svc.purge.report(t[0], days)

    @app.get("/api/purge/audit")
    def audit(since: int = 0, account_id: Optional[str] = None, t=Depends(tenant)):
        return svc.purge.audit_log(t[0], since, account_id=account_id)

    @app.get("/api/purge/audit/verify")
    def audit_verify(t=Depends(tenant)):
        return svc.purge.verify_audit(t[0])

    # Public appeals portal
    @app.get("/api/appeal/{token}")
    def view_appeal(token: str):
        return svc.purge.view_notice(token)

    class AppealIn(BaseModel):
        statement: str
        contact: str = ""

    @app.post("/api/appeal/{token}")
    def submit_appeal(token: str, body: AppealIn):
        return svc.purge.submit_appeal(token, body.statement, body.contact)

    return app
