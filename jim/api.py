"""JIM-mini HTTP API — the standalone personal-guidance service."""

from __future__ import annotations

import html
import io
import json
import logging
import os
from datetime import date, datetime

from fastapi.exceptions import RequestValidationError
from fastapi import (Depends, FastAPI, Header, HTTPException, Request,
                     Response)
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse

from . import pagehead
from . import (accounts, adaptation, app_connectors, auth, bands, beacons,
               finetune as finetune_mod,
               careteam, community,
               catalog,
               coach,
               mailer,
               circle, contribution, db, money, schedule, shopping,
               escalation, family, followup, guardian, handoff, i18n, identity,
               landing, life, llm,
               meds, mic, mobile, notify, oauth, offline, presence,
               problems as problems_mod,
               referral, relay,
               research,
               robotics,
               rota, social, storage, synthetic_self, terms as terms_mod, tiers, tutorial,
               vigil, voice, watch)
from . import continuity
from . import crashwatch
from . import help as help_mod
from . import calm as calm_mod
from . import fitness as fitness_mod
from . import nutrition as nutrition_mod
from . import capture as capture_mod
from . import dock as dock_mod
from .models import (
    ActivityObserve, AppCollect, AppConnect, AppInvoke, BeaconAlarm,
    BeaconPlace, BiometricSample, CheckIn,
    ChildEnroll,
    CareTeamGoal, CareTeamLink,
    CoachMessage, ConditionDeclare, ContextEvent, DeviceRegister, EmergencyRequest,
    CoachStudy, Enroll, ExcursionStart, FamilyControls, GoalCreate, GoalUpdate,
    CommunityVisit, FollowupAnswer, GuidanceFeedback, HabitCreate,
    BudgetSet, CrashWatchArm, HelpAsk, MealPlanAsk, OAuthStart, WorkoutAsk,
    MandateSet, MoneyAccountAdd, MoneyObserve, AppointmentIn, ShopOrderIn, ShopCancelIn, SavingsSet,
    FeatureFlip, CircleInviteIn, CircleMessageIn, HomepageIn,
    AccessReportSubmit,
    HabitLog, ImprovementSubmit, JournalEntry, ModelChoice, PersonalityUpdate,
    FinetuneSwitch, PresenceBearing, PresenceSurface,
    RobotBind, RelayAccept, RelayQuestion,
    SelfProfileConsent, SelfProfileLink,
    BandSet,
    LanguageChoice, LocalitySet, MailSettings, MailTest,
    MedCreate, MedLog, MedUpdate,
    MicAttach, MicGain, MicHandover,
    ReferralPrepare, ResendCode, ResetPassword, ResetRequest, RobotCommand,
    SignIn, Signup,
    TranslateRequest, VerifyEmail,
    VigilArm,
    VoiceSettings, VoiceSpeak, VoiceTranscribe, WaiverSign,
    SensitivitySet, SessionStart, SocialCollect, SocialConnect, SocialPublish,
    SourceConsent, SpecialistRegister, SpecialistTaskStart,
    CaptureAttach, CaptureTake, DockConfig, PlanChoice, TutorialMark, MealLog,
    DrillStart, DrillAnswer, StatementDrop, BankLink,
)
from .cloud import CloudModelClient
from .pdi_client import PDIClient
from .qrme_client import QRMEClient


#: The unhandled-error path logs here and nowhere else: the traceback
#: stays on this machine, and what leaves is a status and a sentence.
_log = logging.getLogger(__name__)

def _age(birthdate: date) -> int:
    today = datetime.now().date()
    return today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )


def create_app(qrme_client: QRMEClient | None = None,
               pdi_client: PDIClient | None = None,
               cloud_client: CloudModelClient | None = None) -> FastAPI:
    # The membership gate is an application-wide dependency rather than a
    # call at the top of each paid handler: one table, one chokepoint, and no
    # route opts in. See jim/tiers.py — including NEVER_GATED, the paths no
    # plan may ever stand in front of.
    app = FastAPI(title="JIM-mini / Guardian", version="0.68.0",
                  dependencies=[Depends(tiers.gate)])

    # A storage-posture refusal is 402 wherever it is raised, not 422 or 500.
    # Registered application-wide rather than wrapped at each write, because
    # the payloads it guards are reached from several routes and the failure
    # of a missed one is silent: the write succeeds and lands in the clear.
    # Starlette matches handlers along the exception's MRO, so this catches
    # StorageError and nothing else — plain ValueError is unaffected.
    # Every refusal in this product, in the language of whoever is reading it.
    #
    # `i18n.refuse` is the one place a refusal becomes a response. There are
    # nine handlers here and eight of them were built one per health domain,
    # each with its own JSONResponse — so a single HTTPException handler,
    # ported from QRME where one is enough, would have localized the
    # framework's refusals and left the medication cabinet, the vigil and the
    # crash watch in English. In this product those are the wrong eight to
    # miss.
    #
    #     asked     are the refusals localized
    #     mattered  are all of them
    #
    # test_the_guardian_refuses_in_one_language.py fails the next handler
    # added that does not return through here.
    @app.exception_handler(HTTPException)
    async def _refusal_in_the_readers_language(request: Request,
                                               exc: HTTPException):
        return i18n.refuse(request, exc.status_code,
                           {"detail": exc.detail}, exc.headers)

    # The refusal FastAPI renders itself, which is the one a person meets most
    # often: a mistyped form is a 422. `RequestValidationError` is neither an
    # `HTTPException` nor one of the eight domain errors, so it went out past
    # all nine handlers above — in English, and carrying pydantic's `input`
    # key, which on a missing field is the entire submitted body handed
    # straight back. A journal entry, for instance. See `jim/i18n.py`.
    #
    # Routed through `i18n.refuse` like everything else, so the structural
    # guard covers it. The rows are already translated by `validation_detail`;
    # `localize_detail` leaves a list alone, so nothing is done twice.
    @app.exception_handler(RequestValidationError)
    async def _rejected_input_stays_with_its_sender(
            request: Request, invalid: RequestValidationError):
        # `message` rides alongside because `detail` is a list, and a list is
        # not something any of this product's clients could show a person: the
        # console printed it as JSON, Android did the same by coercion, and
        # iOS and Windows asked for a string, got an array, and fell back to
        # "HTTP 422".
        #
        #     asked     is the refusal translated
        #     mattered  is the refusal a sentence
        #
        # `detail` keeps its shape — it is the FastAPI contract and what the
        # driven tests read. The sentence carries nothing the rows do not.
        language = i18n.refusal_language(request)
        rows = i18n.validation_detail(invalid.errors(), language)
        return i18n.refuse(request, 422, {
            "detail": rows, "message": i18n.validation_message(rows, language)})

    @app.exception_handler(storage.StorageError)
    def _storage_refusal(request: Request, exc: storage.StorageError):
        return i18n.refuse(request, 402, {
            "detail": str(exc),
            "reason": "storage_posture",
            "have": tiers.plan_of(tiers.account_of(request) or ""),
            "needs": "basic",
            "price_usd": tiers.PLANS["basic"]["price_usd"],
            "period": tiers.PLANS["basic"]["period"],
            "billing": "simulated — no real funds move",
            "emergency_unaffected": True,
        })

    # The watch bridge speaks in refusals a Shortcut author can act on —
    # carry the status it chose (404 wrong channel, 422 unusable payload).
    @app.exception_handler(watch.WatchError)
    def _watch_refusal(request: Request, exc: watch.WatchError):
        return i18n.refuse(request, exc.status, {"detail": exc.message})

    @app.exception_handler(crashwatch.CrashWatchError)
    def _crashwatch_refusal(request: Request, exc: crashwatch.CrashWatchError):
        return i18n.refuse(request, exc.status, {"detail": exc.message})

    @app.exception_handler(calm_mod.CalmError)
    def _calm_refusal(request: Request, exc: calm_mod.CalmError):
        return i18n.refuse(request, exc.status, {"detail": exc.message})

    @app.exception_handler(fitness_mod.FitnessError)
    def _fitness_refusal(request: Request, exc: fitness_mod.FitnessError):
        return i18n.refuse(request, exc.status, {"detail": exc.message})

    @app.exception_handler(nutrition_mod.NutritionError)
    def _nutrition_refusal(request: Request,
                           exc: nutrition_mod.NutritionError):
        return i18n.refuse(request, exc.status, {"detail": exc.message})

    @app.exception_handler(synthetic_self.SelfLinkError)
    def _self_link_refusal(request: Request,
                           exc: synthetic_self.SelfLinkError):
        return i18n.refuse(request, exc.status, {"detail": exc.message})

    @app.exception_handler(vigil.VigilError)
    def _vigil_refusal(request: Request, exc: vigil.VigilError):
        return i18n.refuse(request, exc.status, {"detail": exc.message})

    @app.exception_handler(meds.MedError)
    def _med_refusal(request: Request, exc: meds.MedError):
        return i18n.refuse(request, exc.status, {"detail": exc.message})


    # -- the synthetic self: the one QRME profile that is this person ---------
    #
    # Everything else in this file that touches QRME reaches somebody else's
    # profile. See jim/synthetic_self.py and docs/tandem.md for the boundary
    # these five routes exist to hold.

    @app.get("/self-profile/{user_id}")
    def self_profile(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return synthetic_self.status(user_id)

    @app.post("/self-profile/{user_id}", status_code=201)
    def link_self_profile(user_id: str, body: SelfProfileLink,
                          request: Request) -> dict:
        """Bind this user to their own QRME `self` profile.

        The owner token is theirs and stays here. QRME is asked what kind of
        profile it is and the link is refused unless the answer is `self`.
        """
        _user_or_404(user_id, request)
        return synthetic_self.link(user_id, body.profile_id,
                                   body.owner_token, app.state.qrme)

    @app.delete("/self-profile/{user_id}")
    def unlink_self_profile(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return synthetic_self.unlink(user_id)

    @app.put("/self-profile/{user_id}/consent")
    def consent_self_profile(user_id: str, body: SelfProfileConsent,
                             request: Request) -> dict:
        """Replace the consented categories. Empty is a valid answer and the
        default; it is how somebody says *not this any more*."""
        _user_or_404(user_id, request)
        return synthetic_self.consent(user_id, body.categories)

    @app.get("/self-profile/{user_id}/preview")
    def preview_self_profile(user_id: str, request: Request) -> dict:
        """Exactly what would be sent, composed by the code that sends it."""
        _user_or_404(user_id, request)
        return synthetic_self.preview(user_id)

    @app.post("/self-profile/{user_id}/brief")
    def brief_self_profile(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return synthetic_self.send(user_id, app.state.qrme)

    # Optional CORS for a packaged guardian-console front-end (app/) calling the
    # API from another origin. Off by default; set JIM_CORS_ORIGINS to a
    # comma-separated allowlist, or "*" for any.

    # Bring-your-own model key: ``x-llm-api-key`` rides the request into a
    # context variable the provider layer reads — the caller's generations run
    # on their credential, which is never persisted and never logged. Requests
    # without one use the deployment's env key (the operator lending theirs).
    @app.middleware("http")
    async def _llm_request_key(request: Request, call_next):
        token = llm.set_request_key(request.headers.get("x-llm-api-key"))
        try:
            return await call_next(request)
        finally:
            llm.reset_request_key(token)

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

    def _vault(user_id: str):
        """The vault this user's **writes** go to, or None on an open plan.

        Every seal point used to receive `app.state.pdi` directly, which asks
        whether the *deployment* has a vault rather than whether the *account*
        is on a plan that uses one — so a free account on a PDI-backed
        deployment had its journal, check-in notes and detection detail sealed
        into a vault it was not paying for and could not hold a key to. Free is
        platform custody over plain HTTPS; see `jim/storage.py`.

        **Writes only.** Reads (`journal_entries`, `content_for_care`,
        `access_log`, the audit surfaces) and deletions (`delete_user_data`,
        `capture.delete`) keep `app.state.pdi` unchanged, because somebody who
        was on Basic for a year and moved to Free still has a year of sealed
        records to read back and, if they ask, to have purged. A plan-gated
        vault on a read strands somebody's history behind a billing change; on
        a delete it leaves records nobody can reach and calls that erasure.
        """
        return storage.vault_for(tiers.governing_plan(user_id), app.state.pdi)

    @app.get("/terms")
    def terms() -> dict:
        """The Terms of Service every client displays at the gateway:
        version, key points, and where the full text lives. Acceptance is
        required to enroll and recorded (version + timestamp) on the
        account."""
        return {"version": terms_mod.TERMS_VERSION,
                "key_points": terms_mod.KEY_POINTS,
                "document": terms_mod.DOCUMENT}

    @app.get("/offline/status")
    def offline_status() -> dict:
        """What this deployment can and cannot reach.

        A guarantee nobody can read is a guarantee nobody can check. The flag
        was settable before this and there was nowhere to see the answer — the
        sibling has had `GET /offline/status` since offline mode was written,
        and this product had the mode without the proof.

        Open, like `/health`: an operator standing up an on-prem deployment
        needs to confirm the posture before there is an account to sign in
        with, and the answer names no person and no data.
        """
        return offline.status(app)

    @app.post("/v1/problems", status_code=202)
    async def report_problems(request: Request) -> dict:
        """The error reports come home — see `jim/problems.py`.

        Same contract as the Cloud Model Gateway's intake, on the product's
        own backend, so a deployment with no gateway still collects its own
        failures. Accepted or refused whole: a partial accept would leave
        the sender believing its redaction is fine while the half that
        proved otherwise was silently binned.
        """
        try:
            payload = problems_mod.screen(await request.json())
        except problems_mod.Rejected as exc:
            raise HTTPException(422, str(exc)) from exc
        folded = problems_mod.add(payload)
        return {"accepted": True, "problems": len(payload["problems"]),
                "failures": folded}

    @app.get("/v1/problems")
    def list_problems(request: Request) -> dict:
        """The aggregate, worst first — for whoever is fixing the bugs.

        Narrower than the intake: anyone may post (a wrong write costs a
        wrong counter), but the aggregate is a live map of what fails on
        every version, so reading needs ``JIM_PROBLEMS_KEY`` — or a caller
        on the backend's own machine, the self-hosted case where operator
        and user are one person. Behind a reverse proxy every caller looks
        local, so a published deployment must set the key.
        """
        key = os.environ.get("JIM_PROBLEMS_KEY", "")
        if key:
            presented = request.headers.get("authorization") or ""
            if not presented.startswith("Bearer "):
                raise HTTPException(
                    401, "reading the failure map requires the "
                         "JIM_PROBLEMS_KEY bearer token")
            import secrets as _secrets
            if not _secrets.compare_digest(presented[len("Bearer "):], key):
                raise HTTPException(403, "wrong problems key")
        else:
            host = request.client.host if request.client else ""
            if host not in ("127.0.0.1", "::1", "localhost", "testclient"):
                raise HTTPException(
                    403, "the failure aggregate is readable from this "
                         "machine only until JIM_PROBLEMS_KEY is set — "
                         "behind a proxy, set it")
        return {"rows": problems_mod.rows()}

    @app.get("/health")
    def health() -> dict:
        # The version is here so a desktop shell can tell whether the backend
        # answering the port is its own. A stale backend from an older
        # install answers /health perfectly well and then serves an older
        # API — which is how a user who installed three upgrades kept
        # meeting the first version's signup.
        # The footsteps: how many people are enrolled here. An aggregate,
        # not a roster — no name, pseudonym or id rides with the number.
        # It lives on /health rather than a route of its own because every
        # client already reads /health at launch for the version check, so
        # the count arrives through a door that already exists. A user row
        # only exists once enrollment finished (an email account creates
        # its user at verification), so the count is people, not attempts.
        footsteps = db.connect().execute(
            "SELECT COUNT(*) FROM users").fetchone()[0]
        return {"status": "ok", "version": app.version,
                "tandem": app.state.qrme is not None,
                "pdi": app.state.pdi is not None,
                "cloud": app.state.cloud is not None,
                "console": mobile.console_dir() is not None,
                # Whether account creation here needs an invite key, so the
                # signup screen can ask for one instead of collecting a form
                # that ends in a 403 the person cannot answer. Only the fact
                # that a key is required — never the key.
                "signup_key": bool(os.environ.get("JIM_SIGNUP_KEY")),
                "footsteps": footsteps}

    # -- run it from your phone ---------------------------------------------

    @app.get("/pair")
    def pair(request: Request) -> dict:
        """How to open the Guardian on a phone: the console's URL on this
        local network, ready to type or scan. Same Wi-Fi, no app store."""
        return mobile.pairing(port=request.url.port or 8000)

    @app.get("/pair/qr.svg")
    def pair_qr(request: Request) -> Response:
        """The console URL as a QR code — point the phone's camera at it."""
        import segno
        buf = io.BytesIO()
        url = mobile.pairing(port=request.url.port or 8000)["console_url"]
        segno.make(url, error="q").save(
            buf, kind="svg", scale=8, border=2,
            dark="#0b1120", light="#ffffff")
        return Response(content=buf.getvalue(), media_type="image/svg+xml")

    # -- the Guardian's walkthrough -----------------------------------------
    #
    # Reads only, apart from the learner's own progress. Nothing here triggers
    # an escalation, reaches an emergency contact or files a condition "to show
    # you how" — in a product whose actions reach a real person's phone at
    # three in the morning, a demonstration that fires for real is not one.

    # -- guided wellness: calm sessions, workout plans, meal plans --------
    # The on-purpose half of guidance: nobody has to be in trouble to use
    # any of these. All three are deterministic protocols and tables — the
    # Coach is where the conversation about them happens.

    @app.get("/calm")
    def calm_catalog() -> dict:
        """The guided sessions on offer. Public like /help: a breathing
        exercise should not require an account to browse."""
        return {"sessions": calm_mod.catalog()}

    @app.post("/calm/{user_id}/{kind}", status_code=201)
    def calm_start(user_id: str, kind: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return calm_mod.start(user_id, kind)

    @app.get("/calm/{user_id}/history")
    def calm_history(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return calm_mod.history(user_id)

    @app.post("/fitness/{user_id}/plan", status_code=201)
    def workout_plan(user_id: str, body: WorkoutAsk,
                     request: Request) -> dict:
        _user_or_404(user_id, request)
        return fitness_mod.plan(user_id, body.minutes, body.level,
                                body.focus)

    @app.post("/nutrition/{user_id}/plan", status_code=201)
    def meal_plan(user_id: str, body: MealPlanAsk,
                  request: Request) -> dict:
        _user_or_404(user_id, request)
        return nutrition_mod.plan(user_id, body.goal, body.preferences,
                                  body.days)

    @app.get("/help/topics")
    def help_topics() -> dict:
        """What the help box can answer, so a UI can offer them."""
        return {"topics": help_mod.topics(),
                "disclosure": help_mod.DISCLOSURE}

    @app.post("/help")
    def ask_help(body: HelpAsk) -> dict:
        """The help box on every screen. Public on purpose — "where is
        the thing?" arrives before a sign-in does. It writes nothing."""
        return help_mod.ask(body.question)

    @app.get("/tutorial")
    def tutorial_outline(mode: str = "text") -> dict:
        """The whole walkthrough, chaptered. `?mode=voice` to be spoken."""
        try:
            return tutorial.outline(mode)
        except tutorial.TutorialError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.get("/tutorial/steps/{key}")
    def tutorial_step(key: str, mode: str = "text") -> dict:
        try:
            return tutorial.step(key, mode)
        except tutorial.TutorialError as exc:
            raise HTTPException(404, str(exc)) from None

    @app.get("/tutorial/for-screen/{number}")
    def tutorial_for_screen(number: int, mode: str = "text") -> dict:
        """The lesson covering a given screen, so a screen can explain
        itself instead of opening the tour at the beginning."""
        found = tutorial.for_screen(number, mode)
        if found is None:
            raise HTTPException(404, "no lesson covers that screen")
        return found

    @app.post("/tutorial/start")
    def tutorial_start(body: TutorialMark) -> dict:
        return tutorial.start(body.learner_id, body.mode)

    @app.get("/tutorial/progress/{learner_id}")
    def tutorial_progress(learner_id: str, mode: str = "text") -> dict:
        return tutorial.where(learner_id, mode)

    @app.post("/tutorial/done")
    def tutorial_done(body: TutorialMark) -> dict:
        try:
            return tutorial.mark(body.learner_id, body.lesson, body.mode)
        except tutorial.TutorialError as exc:
            raise HTTPException(404, str(exc)) from None

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
                422, i18n.fill(i18n.MUST_BE_ONE_OF, field="provider",
                              choices=", ".join(llm.CHOICES)))
        llm.set_choice(user_id, body.provider)
        return {"user_id": user_id, "provider": body.provider,
                "effective": llm.resolve_choice(body.provider)}

    @app.get("/languages")
    def list_languages() -> dict:
        """Supported languages: model-generated text is produced in-language;
        the marked subset also has hand-translated safety content (playbooks,
        waiver terms)."""
        return {"languages": [{"code": code, "label": label,
                               "safety_content_translated":
                                   code == i18n.DEFAULT
                                   or code in i18n.HAND_TRANSLATED}
                              for code, label in i18n.SUPPORTED.items()],
                "default": i18n.DEFAULT}

    @app.get("/language/{user_id}")
    def get_user_language(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        code, mode = i18n.get_pref(user_id)
        return {"user_id": user_id, "language": code,
                "label": i18n.SUPPORTED[code], "mode": mode}

    @app.put("/language/{user_id}")
    def set_user_language(user_id: str, body: LanguageChoice,
                          request: Request) -> dict:
        """Everything drafted for or delivered to this user — guidance,
        coaching, playbooks, waiver terms — localizes to this language.
        mode "pre" (default) delivers everything already translated;
        "on_demand" keeps originals for use with POST /translate."""
        _user_or_404(user_id, request)
        if body.language not in i18n.SUPPORTED:
            raise HTTPException(
                422, i18n.fill(i18n.MUST_BE_ONE_OF, field="language",
                              choices=", ".join(i18n.SUPPORTED)))
        if body.mode not in i18n.MODES:
            raise HTTPException(
                422, i18n.fill(i18n.MUST_BE_ONE_OF, field="mode",
                              choices=", ".join(i18n.MODES)))
        i18n.set_language(user_id, body.language, body.mode)
        return {"user_id": user_id, "language": body.language,
                "label": i18n.SUPPORTED[body.language], "mode": body.mode}

    @app.post("/translate/{user_id}")
    def translate_text(user_id: str, body: TranslateRequest,
                       request: Request) -> dict:
        """Translate anything the user runs across — a note, a message, a
        document snippet — into their language (or an explicit target).
        Known safety strings use the hand translations; free text uses the
        user's own model; the offline stub says so instead of pretending."""
        _user_or_404(user_id, request)
        try:
            return i18n.translate(user_id, body.text, body.to)
        except ValueError as exc:
            raise HTTPException(422, str(exc))

    @app.post("/enroll", status_code=201,
              dependencies=[Depends(auth.require_signup_key)])
    def enroll(body: Enroll) -> dict:
        if not body.terms_consent:
            raise HTTPException(403, "consent to terms of use is required to enroll")
        if body.birthdate and _age(body.birthdate) < 18 and not body.guardian_consent:
            raise HTTPException(403, "minors require parent/guardian consent")
        user = guardian.enroll(body.model_dump(exclude={"language"}))
        # Language chosen at the setup gateway applies from the first
        # response onward.
        if body.language:
            if body.language not in i18n.SUPPORTED:
                raise HTTPException(
                    422,
                    i18n.fill(i18n.MUST_BE_ONE_OF, field="language",
                              choices=", ".join(i18n.SUPPORTED)))
            i18n.set_language(user["id"], body.language)
            user["language"] = body.language
        # Signing up is where a membership starts. Basic unless a plan is
        # named — the cheaper of two prices is the honest default for somebody
        # who has not chosen, and every emergency path is in Basic.
        tiers.subscribe(user["id"], body.plan or tiers.DEFAULT_PLAN)
        user["membership"] = tiers.membership(user["id"])
        # The user token is shown exactly once, here.
        user["user_token"] = auth.issue("user", user["id"])
        return user

    # ---- accounts: email + password, address verified first ---------------

    @app.post("/signup", status_code=201,
              dependencies=[Depends(auth.require_signup_key)])
    def signup(body: Signup) -> dict:
        """Create an account. The enrollment is validated now but held
        pending: nothing exists — no user, no token, no membership — until
        the emailed code proves the caller holds the address. The response
        says how the code travelled (``smtp``, or ``console`` — printed to
        the server terminal when no mail is configured), never the code."""
        if not body.terms_consent:
            raise HTTPException(403, "consent to terms of use is required to enroll")
        if body.birthdate and _age(body.birthdate) < 18:
            if not body.guardian_consent:
                raise HTTPException(403, "minors require parent/guardian consent")
            # Spec [0024]/[0030]: on the account path the consent is
            # *verified*, not asserted — the activation code is delivered to
            # the guardian's own inbox, so it must exist and be theirs.
            if not (body.guardian_email or "").strip():
                raise HTTPException(
                    403, "a minor's verification code goes to their parent "
                         "or guardian — provide guardian_email")
            if body.guardian_email.strip().lower() == body.email.strip().lower():
                raise HTTPException(
                    422, "the guardian's address must be different from "
                         "the minor's own")
        if body.language and body.language not in i18n.SUPPORTED:
            raise HTTPException(
                422, i18n.fill(i18n.MUST_BE_ONE_OF, field="language",
                              choices=", ".join(i18n.SUPPORTED)))
        try:
            return accounts.signup(
                body.email, body.password,
                body.model_dump(mode="json", exclude={"email", "password"}))
        except accounts.AccountError as exc:
            raise HTTPException(exc.status, exc.detail)

    @app.post("/verify-email")
    def verify_email(body: VerifyEmail) -> dict:
        """Trade the emailed code for the account's first session: the user
        is enrolled here (not at signup), and the token is shown once."""
        try:
            return accounts.verify(body.email, body.code)
        except accounts.AccountError as exc:
            raise HTTPException(exc.status, exc.detail)

    @app.get("/verify-email/click", response_class=HTMLResponse)
    def verify_email_click(token: str = "") -> HTMLResponse:
        """The emailed link lands here, in a browser. The app finishes on
        its own: it holds the email and password, so it signs in the moment
        the address is proven."""
        page = ("<html><body style='font-family:sans-serif;background:#0d0a20;"
                "color:#e6edf3;display:grid;place-items:center;height:95vh'>"
                "<div style='text-align:center'><h1>{title}</h1><p>{body}</p>"
                "</div></body></html>")
        try:
            result = accounts.verify_link(token)
        except accounts.AccountError as exc:
            return HTMLResponse(page.format(
                title="That link didn't work", body=exc.detail), 403)
        if result["already"]:
            return HTMLResponse(page.format(
                title="Already verified",
                body="This address was verified earlier — just sign in."))
        return HTMLResponse(page.format(
            title="✓ Verified",
            body="Your account is active. Go back to JIM Guardian — "
                 "it will continue on its own."))

    # ---- speaking and listening -------------------------------------------

    @app.get("/settings/voice")
    def get_voice_settings() -> dict:
        """Which voice this deployment speaks in, and what it can offer."""
        return voice.describe_settings()

    @app.put("/settings/voice",
             dependencies=[Depends(auth.require_signup_key)])
    def put_voice_settings(body: VoiceSettings) -> dict:
        try:
            return voice.save_settings(
                provider=body.provider, api_key=body.api_key or "",
                voice_id=body.voice_id or "", speak_replies=body.speak_replies)
        except ValueError as exc:
            raise HTTPException(422, str(exc))

    @app.delete("/settings/voice",
                dependencies=[Depends(auth.require_signup_key)])
    def delete_voice_settings() -> dict:
        return voice.clear_settings()

    @app.post("/voice/speak")
    def voice_speak(body: VoiceSpeak) -> Response:
        """Say something aloud: text in, audio out. A deployment with no
        speaking service answers 503 and the app reads the text with the
        device's own voice — silence would be the wrong failure."""
        if not body.text.strip():
            raise HTTPException(422, "nothing to say")
        try:
            audio, media_type = voice.speak(body.text, body.voice_id)
        except voice.VoiceUnavailable as exc:
            raise HTTPException(503, str(exc))
        except voice.VoiceError as exc:
            raise HTTPException(502, str(exc))
        return Response(content=audio, media_type=media_type)

    @app.post("/voice/transcribe")
    def voice_transcribe(body: VoiceTranscribe) -> dict:
        """Recorded speech in, words out. The audio is not stored."""
        import base64 as _b64

        try:
            raw = _b64.b64decode(body.audio_base64, validate=True)
        except Exception:
            raise HTTPException(422, "audio_base64 is not valid base64")
        if not raw:
            raise HTTPException(422, "no audio")
        try:
            return {"text": voice.transcribe(raw, body.filename or "speech.webm")}
        except voice.VoiceUnavailable as exc:
            raise HTTPException(503, str(exc))
        except voice.VoiceError as exc:
            raise HTTPException(502, str(exc))

    # ---- your own normal, and how far from it counts ----------------------

    @app.get("/bands/{user_id}")
    def get_bands(user_id: str, request: Request) -> dict:
        """Every metric's band, the learned baseline, and where the two edges
        sit — so a screen can show *your normal* rather than a bare number.
        Edges appear only once the baseline is established."""
        user = _user_or_404(user_id, request)
        return {"user_id": user_id,
                "sensitivity": user.get("sensitivity") or "balanced",
                "bands": bands.overview(
                    user_id, user.get("sensitivity") or "balanced")}

    @app.put("/bands/{user_id}/{metric}")
    def put_band(user_id: str, metric: str, body: BandSet,
                 request: Request) -> dict:
        """Widen, narrow, or switch off a direction. Crossing a band is a
        check-in, never an escalation."""
        _user_or_404(user_id, request)
        try:
            return bands.set_band(user_id, metric, margin=body.margin,
                                  watch_high=body.watch_high,
                                  watch_low=body.watch_low)
        except ValueError as exc:
            raise HTTPException(422, str(exc))

    @app.delete("/bands/{user_id}/{metric}")
    def delete_band(user_id: str, metric: str, request: Request) -> dict:
        """Back to the default width for this metric."""
        _user_or_404(user_id, request)
        if metric not in bands.DEFAULTS:
            raise HTTPException(422, f"unknown metric {metric!r}")
        return bands.reset_band(user_id, metric)

    # ---- where this deployment sends mail through -------------------------

    @app.get("/settings/mail")
    def get_mail_settings() -> dict:
        """The mail configuration, never its password. Until a host is set,
        no verification email can be sent to anybody — which is why local
        signup does not wait for one."""
        return mailer.describe_settings()

    @app.put("/settings/mail",
             dependencies=[Depends(auth.require_signup_key)])
    def put_mail_settings(body: MailSettings) -> dict:
        """Point this deployment at a mail server, from the app itself.
        Environment variables still win when set."""
        try:
            return mailer.save_settings(
                host=body.host, port=body.port, username=body.username or "",
                password=body.password or "", sender=body.sender or "",
                public_url=body.public_url or "")
        except ValueError as exc:
            raise HTTPException(422, str(exc))

    @app.delete("/settings/mail",
                dependencies=[Depends(auth.require_signup_key)])
    def delete_mail_settings() -> dict:
        """Forget the mail server; delivery falls back to the console."""
        return mailer.clear_settings()

    @app.post("/settings/mail/test",
              dependencies=[Depends(auth.require_signup_key)])
    def test_mail_settings(body: MailTest) -> dict:
        """Send a real message now, and say plainly what the server said.
        A settings screen that saves without ever proving it can deliver is
        how an app ends up insisting it emailed somebody."""
        if mailer.configured_transport() != "smtp":
            raise HTTPException(
                422, "no mail server is configured — save one first")
        try:
            mailer.deliver(
                body.to,
                "JIM Guardian test message",
                "This is a test from JIM Guardian.\n\nIf you are reading it "
                "in your inbox, verification emails will reach your users "
                "too.")
        except Exception as exc:  # noqa: BLE001 — smtplib raises many kinds
            raise HTTPException(502, f"the mail server refused it: {exc}")
        return {"sent": True, "to": body.to}

    @app.post("/verify-email/resend")
    def resend_code(body: ResendCode) -> dict:
        """Send a fresh code, retiring the previous ones. Answers the same
        whether or not the address has an account — this endpoint is not an
        address oracle."""
        try:
            return accounts.resend(body.email)
        except accounts.AccountError as exc:
            raise HTTPException(exc.status, exc.detail)

    @app.post("/password/reset/request")
    def request_password_reset(body: ResetRequest) -> dict:
        """Email a reset code. Same answer whether or not the address has an
        account — not an address oracle."""
        try:
            return accounts.request_reset(body.email)
        except accounts.AccountError as exc:
            raise HTTPException(exc.status, exc.detail)

    @app.post("/password/reset")
    def reset_password(body: ResetPassword) -> dict:
        """Trade the emailed code for a new password. Every existing session
        dies with the old password; sign in again with the new one."""
        try:
            return accounts.reset_password(body.email, body.code,
                                           body.new_password)
        except accounts.AccountError as exc:
            raise HTTPException(exc.status, exc.detail)

    # ---- Sign in with Google / Apple (jim/oauth.py) -----------------------

    @app.get("/auth/oauth/providers")
    def oauth_providers() -> dict:
        """Which sign-in doors are live here, and how to open the rest."""
        return oauth.providers()

    @app.post("/auth/oauth/{provider}/start",
              dependencies=[Depends(auth.require_signup_key)])
    def oauth_start(provider: str, body: OAuthStart,
                    request: Request) -> dict:
        redirect = body.redirect_uri or str(
            request.url_for("oauth_callback", provider=provider))
        try:
            return oauth.start(provider, redirect, enroll=body.enroll)
        except oauth.OAuthError as exc:
            raise HTTPException(exc.status, exc.message) from None

    @app.get("/auth/oauth/{provider}/callback", response_class=HTMLResponse)
    def oauth_callback(provider: str, code: str = "", state: str = "",
                       error: str = "") -> HTMLResponse:
        if error or not code:
            return HTMLResponse(
                f"<h2>Sign-in was not completed</h2>"
                f"<p>{html.escape(error) or 'no code came back'} — you can close "
                "this window and try again.</p>", status_code=400)
        try:
            done = oauth.callback(provider, code, state)
        except oauth.OAuthError as exc:
            return HTMLResponse(
                f"<h2>Sign-in failed</h2><p>{html.escape(exc.message)}</p>",
                status_code=exc.status)
        return HTMLResponse(
            f"<h2>Signed in as {html.escape(done['email'])}</h2>"
            "<p>You can close this window and return to the app.</p>")

    @app.post("/auth/oauth/{provider}/callback", response_class=HTMLResponse)
    async def oauth_callback_post(provider: str,
                                  request: Request) -> HTMLResponse:
        """Apple's half of the door.

        Apple's rule is that requesting any scope forces
        ``response_mode=form_post``, so the browser comes back as a POST with
        the code in a urlencoded body rather than the query string. Parsed
        from the raw body on purpose — the same trick the media upload uses,
        so no python-multipart dependency is added for one form.
        """
        import urllib.parse as _up
        form = _up.parse_qs((await request.body()).decode("utf-8", "replace"))
        return oauth_callback(provider,
                              code=(form.get("code") or [""])[0],
                              state=(form.get("state") or [""])[0],
                              error=(form.get("error") or [""])[0])

    @app.get("/auth/oauth/claim")
    def oauth_claim(state: str) -> dict:
        try:
            return oauth.claim(state)
        except oauth.OAuthError as exc:
            raise HTTPException(exc.status, exc.message) from None

    @app.post("/signin")
    def signin(body: SignIn) -> dict:
        """Email + password for a fresh session token. Unknown address and
        wrong password get the same answer; an unverified address cannot
        sign in at all."""
        try:
            return accounts.signin(body.email, body.password)
        except accounts.AccountError as exc:
            raise HTTPException(exc.status, exc.detail)

    # ---- showing it, rather than describing it ----------------------------

    @app.post("/users/{user_id}/meals", status_code=201)
    def log_meal(user_id: str, body: MealLog, request: Request) -> dict:
        """Point the camera at the plate: the note is the log (tidied by the
        online model when one is standing), the photo is sealed like any
        capture, and the log line reaches the offline coach's nutrition
        area."""
        user = _user_or_404(user_id, request)
        from . import meals as meals_mod
        try:
            return meals_mod.log(user, body.note, body.content,
                                 pdi=app.state.pdi, cloud=app.state.cloud)
        except capture_mod.VaultRequired as exc:
            raise HTTPException(503, str(exc)) from None
        except storage.StorageError:
            raise
        except (meals_mod.MealError, capture_mod.CaptureError) as exc:
            raise HTTPException(422, str(exc)) from None

    @app.get("/users/{user_id}/meals")
    def meal_board(user_id: str, request: Request) -> list[dict]:
        """Recent meals, newest first — log lines and whether a sealed
        receipt stands behind each. The photos themselves need the capture
        image door; a board is not a gallery."""
        _user_or_404(user_id, request)
        from . import meals as meals_mod
        return meals_mod.board(user_id)

    @app.post("/users/{user_id}/drills", status_code=201)
    def start_drill(user_id: str, body: DrillStart, request: Request) -> dict:
        """Deal one interview question from the local bank, with what it
        probes stated up front — practice works with the network cut."""
        user = _user_or_404(user_id, request)
        from . import drills as drills_mod
        try:
            return drills_mod.start(user, body.kind)
        except drills_mod.DrillError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.post("/users/{user_id}/drills/{drill_id}/answer")
    def answer_drill(user_id: str, drill_id: str, body: DrillAnswer,
                     request: Request) -> dict:
        """Read one practice answer against what the question probes — by
        the online coach when one is standing, by the checklist itself when
        not, and the reading says which it was."""
        user = _user_or_404(user_id, request)
        from . import drills as drills_mod
        try:
            return drills_mod.answer(user, drill_id, body.answer,
                                     cloud=app.state.cloud)
        except drills_mod.DrillError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.get("/users/{user_id}/drills")
    def drill_history(user_id: str, request: Request) -> list[dict]:
        """Recent drills, newest first."""
        _user_or_404(user_id, request)
        from . import drills as drills_mod
        return drills_mod.history(user_id)

    @app.post("/users/{user_id}/letters", status_code=201)
    def write_letter(user_id: str, request: Request) -> dict:
        """The weekly letter: what the last seven days actually held, in
        words — composed only from what was logged. A week with nothing
        logged gets no letter."""
        user = _user_or_404(user_id, request)
        from . import letter as letter_mod
        try:
            return letter_mod.compose(user, cloud=app.state.cloud)
        except letter_mod.LetterError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.get("/users/{user_id}/letters")
    def letter_shelf(user_id: str, request: Request) -> list[dict]:
        """Past weekly letters, newest first, each carrying the digest the
        words were written from."""
        _user_or_404(user_id, request)
        from . import letter as letter_mod
        return letter_mod.shelf(user_id)

    @app.get("/captures/vocabulary")
    def capture_vocabulary() -> dict:
        """Kinds, body sites, which are intimate, and what an agent may see.
        Public — a client has to draw the picker, and the limits are worth
        reading before you take the photograph rather than after."""
        return capture_mod.vocabulary()

    @app.post("/users/{user_id}/captures", status_code=201)
    def take_capture(user_id: str, body: CaptureTake, request: Request) -> dict:
        """Seal a photograph, clip or sound of the body.

        The bytes go to the vault; this returns the record, never the image.
        Refused outright if no vault is configured — see jim/capture.py — and
        refused on the free plan, whose store is in the clear.
        """
        user = _user_or_404(user_id, request)
        try:
            # `app.state.pdi`, not `_vault(...)`, and deliberately: on an open
            # plan a capture is refused outright (402), and handing this the
            # plan-gated None would surface "this deployment has no vault"
            # (503) instead — a true statement about the wrong thing.
            return capture_mod.take(
                user, body.kind, body.site, body.content,
                body.provenance, body.note, body.condition,
                body.intimate_consent, pdi=app.state.pdi)
        except capture_mod.VaultRequired as exc:
            # 503, not 422: the request was fine and the deployment is not.
            raise HTTPException(503, str(exc)) from None
        except storage.StorageError:
            # Answered 402 by the application-wide handler. Named here only so
            # it is not swallowed by the CaptureError arm below, and distinct
            # from the 503 above, which no amount of money fixes.
            raise
        except capture_mod.CaptureError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.get("/users/{user_id}/captures")
    def list_captures(user_id: str, request: Request,
                      condition: str | None = None) -> list[dict]:
        """The records. Metadata only — the image needs its own call."""
        _user_or_404(user_id, request)
        return capture_mod.for_user(user_id, condition)

    @app.get("/users/{user_id}/captures/{capture_id}/image")
    def capture_image(user_id: str, capture_id: str,
                      request: Request) -> dict:
        """The sealed bytes, for the person they belong to.

        Separate from the listing on purpose: reading *that* a photograph
        exists and reading the photograph are different acts, and only the
        second should need the vault to answer.
        """
        _user_or_404(user_id, request)
        cap = capture_mod.read(capture_id)
        if cap["user_id"] != user_id:
            raise HTTPException(403, "that capture belongs to somebody else")
        try:
            content = capture_mod.content_for_care(capture_id, app.state.pdi)
        except capture_mod.VaultRequired as exc:
            raise HTTPException(503, str(exc)) from None
        except capture_mod.CaptureError as exc:
            raise HTTPException(404, str(exc)) from None
        return {"id": capture_id, "kind": cap["kind"], "content": content}

    @app.post("/users/{user_id}/captures/attach")
    def attach_captures(user_id: str, body: CaptureAttach,
                        request: Request) -> dict:
        """Choose which captures a referral releases.

        Intimate-site captures are never swept in by a match; they come back
        under `explicit` and have to be named one at a time.
        """
        _user_or_404(user_id, request)
        try:
            return capture_mod.attach_to_referral(body.capture_ids, user_id)
        except capture_mod.CaptureError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.delete("/users/{user_id}/captures/{capture_id}")
    def delete_capture(user_id: str, capture_id: str,
                       request: Request) -> dict:
        """Withdraw it. The vault record is destroyed; a tombstone remains so
        a clinician who was shown it sees it was withdrawn."""
        _user_or_404(user_id, request)
        try:
            return capture_mod.delete(capture_id, user_id, app.state.pdi)
        except capture_mod.CaptureError as exc:
            raise HTTPException(422, str(exc)) from None

    # ---- the pane in the corner -------------------------------------------

    @app.get("/dock/faces")
    def dock_vocabulary() -> dict:
        """Everything needed to draw the pane. Public — the product's shape,
        not anybody's data."""
        return dock_mod.vocabulary()

    @app.get("/dock/where/{face}")
    def dock_where(face: str) -> dict:
        """The screen that can actually do this face's job."""
        try:
            return dock_mod.route(face)
        except dock_mod.DockError as exc:
            raise HTTPException(404, str(exc)) from None

    @app.get("/dock/{user_id}")
    def dock_settings(user_id: str, request: Request,
                      alarm_active: bool = False) -> dict:
        auth.require(request, "user", user_id)
        return dock_mod.opens_as(user_id, alarm_active)

    @app.put("/dock/{user_id}")
    def dock_configure(user_id: str, body: DockConfig,
                       request: Request) -> dict:
        auth.require(request, "user", user_id)
        try:
            return dock_mod.configure(user_id, body.corner, body.state,
                                      body.face, body.faces)
        except dock_mod.DockError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.get("/dock/{user_id}/face/{name}")
    def dock_face(user_id: str, name: str, request: Request,
                  surface_id: str | None = None) -> dict:
        auth.require(request, "user", user_id)
        try:
            return dock_mod.face(user_id, name, surface_id)
        except dock_mod.DockError as exc:
            raise HTTPException(422, str(exc)) from None

    # ---- membership -------------------------------------------------------

    @app.get("/plans")
    def plans() -> dict:
        """The price list. Public — a paywall whose terms nobody can read
        before signing in is one people bounce off.

        Generated from the same table the gate reads, and it carries the
        never-gated list by name, because "will this stop my alarm working"
        is the first question worth answering here.
        """
        return tiers.catalogue()

    @app.get("/memberships/{account_id}")
    def membership(account_id: str, request: Request) -> dict:
        auth.require(request, "user", account_id)
        return tiers.membership(account_id)

    @app.post("/memberships/{account_id}")
    def subscribe(account_id: str, body: PlanChoice, request: Request) -> dict:
        """Join a plan or move between them. Billing is simulated and the
        response says so."""
        auth.require(request, "user", account_id)
        try:
            return tiers.subscribe(account_id, body.plan)
        except tiers.TierError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.delete("/memberships/{account_id}")
    def cancel_membership(account_id: str, request: Request) -> dict:
        """End it. The person keeps their record, their conditions and every
        emergency path."""
        auth.require(request, "user", account_id)
        return tiers.cancel(account_id)

    # ---- family: a parent sets up and watches over a child's account ------

    @app.post("/guardians/{guardian_id}/children", status_code=201)
    def enroll_child(guardian_id: str, body: ChildEnroll,
                     request: Request) -> dict:
        """Parent-led setup: a verified-adult guardian enrolls their child.
        The consent is recorded as a relationship (who, as what, when), the
        account starts with protective defaults, and the guardian gets an
        age-sized oversight window."""
        guardian_user = _user_or_404(guardian_id, request)
        try:
            child = family.enroll_child(
                guardian_user, body.model_dump(exclude={"language"}),
                pdi=_vault(guardian_id))
        except storage.StorageError:
            # Ahead of the ValueError arm below, which it subclasses, so the
            # setup is not reported as malformed. Answered 402 by the
            # application-wide handler.
            raise
        except ValueError as e:
            raise HTTPException(
                403 if "verified-adult" in str(e) else 422, str(e))
        if body.language:
            if body.language not in i18n.SUPPORTED:
                raise HTTPException(
                    422,
                    i18n.fill(i18n.MUST_BE_ONE_OF, field="language",
                              choices=", ".join(i18n.SUPPORTED)))
            i18n.set_language(child["id"], body.language)
            child["language"] = body.language
        # The child's device token is shown exactly once, here — the
        # guardian puts it on the child's watch or phone.
        child["child_token"] = auth.issue("user", child["id"])
        return child

    @app.get("/guardians/{guardian_id}/children")
    def list_children(guardian_id: str, request: Request) -> list[dict]:
        """The guardian's family list, each child with their current
        oversight tier (which ends by itself at 18)."""
        _user_or_404(guardian_id, request)
        return family.children_of(guardian_id)

    @app.get("/guardians/{guardian_id}/children/{child_id}")
    def child_overview(guardian_id: str, child_id: str,
                       request: Request) -> dict:
        """The oversight window: full timeline under 13, alerts-only for
        teenagers, closed at 18. Condition-level facts only — never raw
        notes or payloads."""
        _user_or_404(guardian_id, request)
        overview = family.child_overview(guardian_id, child_id)
        if overview is None:
            raise HTTPException(404, "no such child on this guardian")
        return overview

    @app.put("/guardians/{guardian_id}/children/{child_id}/controls")
    def set_family_controls(guardian_id: str, child_id: str,
                            body: FamilyControls, request: Request) -> dict:
        """Pause and quiet hours for the child's device. Holds everyday
        guidance only — monitoring, crisis escalation, and the emergency
        path never pause."""
        _user_or_404(guardian_id, request)
        result = family.set_controls(
            guardian_id, child_id, paused=body.paused,
            quiet_start=body.quiet_start, quiet_end=body.quiet_end)
        if result is None:
            raise HTTPException(404, "no such child on this guardian")
        return result

    @app.get("/guardians/{guardian_id}/watch")
    def guardian_watch(guardian_id: str, request: Request) -> dict:
        """The parent's wrist: one light per child from the last 24 hours
        of alert-level events (green quiet, orange escalated, red critical)
        — the wrist taps the parent when a child needs someone. Alert-level
        only, so the teen tier's privacy holds by construction."""
        _user_or_404(guardian_id, request)
        return family.watch_face(guardian_id)

    @app.delete("/guardians/{guardian_id}/children/{child_id}")
    def unlink_child(guardian_id: str, child_id: str,
                     request: Request) -> dict:
        """The guardian steps back: the oversight window closes; the child
        account and the recorded consent event remain."""
        _user_or_404(guardian_id, request)
        if not family.unlink(guardian_id, child_id):
            raise HTTPException(404, "no such child on this guardian")
        return {"guardian_id": guardian_id, "child_id": child_id,
                "linked": False}

    @app.get("/specialists")
    def list_specialists() -> list[dict]:
        """The specialist registry: which named expert stands behind each
        condition domain, and whether guidance routes locally or in tandem
        with a QRME profile."""
        rows = db.connect().execute(
            "SELECT condition, mode, label, qrme_profile_id FROM specialists"
            " ORDER BY condition").fetchall()
        return [dict(r) for r in rows]

    @app.post("/specialists/seed", status_code=201)
    def seed_specialists() -> dict:
        """Populate the starter specialists: one named domain expert per
        condition, so guidance carries a specialist attribution from the
        first deploy. Idempotent — covered conditions are skipped."""
        from . import seed
        return seed.seed()

    @app.post("/specialists/seed/tandem", status_code=201)
    def seed_tandem_specialists() -> dict:
        """Wire starter specialists to their QRME Starter Collection
        counterparts (tandem mode), resolving each @handle against the
        connected QRME deployment. Conditions without a genuine QRME
        counterpart stay local; existing tandem links are kept."""
        if app.state.qrme is None:
            raise HTTPException(
                409, "no QRME endpoint configured (set JIM_QRME_URL)")
        from . import seed
        return seed.seed_tandem(app.state.qrme)

    @app.get("/specialists/catalog")
    def specialists_catalog() -> dict:
        """The attach bracket's stock: the QRME Starter Collection — 33
        industry experts plus the mental-health trio, each already carrying
        its industry's knowledge pack profile-side — beside what is attached
        today, so the console can offer click-to-attach per condition."""
        if app.state.qrme is None:
            raise HTTPException(
                409, "no QRME endpoint configured (set JIM_QRME_URL)")
        attached = {r["condition"]: dict(r) for r in db.connect().execute(
            "SELECT condition, mode, label, qrme_profile_id FROM specialists"
        ).fetchall()}
        from .models import Condition as _Condition
        import typing as _typing
        return {
            "qrme_url": getattr(app.state.qrme, "base_url", None),
            "conditions": [
                {"condition": c, "attached": attached.get(c)}
                for c in _typing.get_args(_Condition)],
            "starters": app.state.qrme.marketplace(),
            "note": "each starter carries its industry's knowledge pack on "
                    "the QRME side; attaching one routes that condition's "
                    "guidance through it in tandem",
        }

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
        # The calendar's bottom rung rides this sense — see jim/schedule.py.
        schedule.remind_pass(user_id, _money_lang(user_id))
        return guardian.monitor(user_id, sample, note, qrme=app.state.qrme,
                                pdi=_vault(user_id))

    @app.get("/events/{user_id}")
    def events(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return guardian.events(user_id)

    # -- the care team is an organization (jim/careteam.py) -----------------
    # The user links their own QRME org; when concerns stack (drift while
    # adherence slips) the Guardian takes the situation to the whole team
    # as one coordination goal, and the joint plan lands back here.

    @app.put("/users/{user_id}/care-team")
    def link_care_team(user_id: str, body: CareTeamLink,
                       request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return careteam.link(user_id, body.org_id, body.department_id,
                                 body.owner_token, app.state.qrme)
        except careteam.CareTeamError as e:
            raise HTTPException(422, str(e))

    @app.get("/users/{user_id}/care-team")
    def care_team_status(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return careteam.status(user_id)

    @app.delete("/users/{user_id}/care-team", status_code=204)
    def unlink_care_team(user_id: str, request: Request) -> None:
        _user_or_404(user_id, request)
        careteam.unlink(user_id)

    @app.post("/users/{user_id}/care-team/coordinate", status_code=201)
    def coordinate_care_team(user_id: str, body: CareTeamGoal,
                             request: Request) -> dict:
        """Take a goal to the care team by hand — the same path the
        stacking rule uses, minus the rule."""
        _user_or_404(user_id, request)
        try:
            return careteam.run(user_id, body.goal, {"manual": True},
                                app.state.qrme)
        except careteam.CareTeamError as e:
            raise HTTPException(422, str(e))

    @app.get("/users/{user_id}/care-team/plans")
    def care_team_plans(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return careteam.plans(user_id)

    # -- the watch bridge (jim/watch.py) ------------------------------------
    # Readings reach JIM from any wrist with no app to install: an
    # automation drips live samples at a tokened URL, and the wearable's
    # own export seeds the baseline from history it already recorded. The
    # ?device= picker chooses which wearable family the recipe teaches —
    # Apple Watch, Wear OS, Fitbit or Garmin.

    @app.get("/watch/channel/{user_id}")
    def watch_channel(user_id: str, request: Request,
                      device: str = "apple_watch") -> dict:
        """The setup card: drip URL, this device's recipe, arrivals so
        far — and the device list itself, so the picker renders from the
        API rather than being hardcoded four times."""
        _user_or_404(user_id, request)
        base = mobile.pairing(port=request.url.port or 8000)["api_url"]
        return watch.setup(user_id, base, device=device)

    @app.post("/watch/channel/{user_id}/rotate")
    def watch_rotate(user_id: str, request: Request,
                     device: str = "apple_watch") -> dict:
        _user_or_404(user_id, request)
        watch.rotate(user_id)
        base = mobile.pairing(port=request.url.port or 8000)["api_url"]
        return watch.setup(user_id, base, device=device)

    @app.post("/watch/drip/{token}")
    def watch_drip(token: str, payload: dict) -> dict:
        """The Shortcut's POST. The token in the path is the whole
        credential — see jim/watch.py for why the reply carries counts and
        nothing else."""
        return watch.drip(token, payload, qrme=app.state.qrme,
                          vault_for=_vault)

    @app.post("/watch/seed/{user_id}")
    async def watch_seed(user_id: str, request: Request) -> dict:
        """Upload the Health app's export.zip (or bare export.xml) as the
        request body. History folds into baselines only — no events, no
        check-ins; enrollment day should be quiet."""
        _user_or_404(user_id, request)
        return watch.seed(user_id, await request.body())

    # -- the vigil (jim/vigil.py) -------------------------------------------
    # The alarm that fires on the ABSENCE of readings: a steward, chosen and
    # worded in advance, is told when the signals stop.

    @app.get("/vigil/{user_id}")
    def vigil_status(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return vigil.status(user_id)

    @app.put("/vigil/{user_id}")
    def vigil_arm(user_id: str, body: VigilArm, request: Request) -> dict:
        _user_or_404(user_id, request)
        return vigil.arm(user_id, body.steward_name, body.steward_channel,
                         quiet_days=body.quiet_days, note=body.note)

    @app.delete("/vigil/{user_id}")
    def vigil_disarm(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return vigil.disarm(user_id)

    @app.post("/vigil/{user_id}/sweep")
    def vigil_sweep(user_id: str, request: Request) -> dict:
        """Idempotent silence check — the console calls it on open; anything
        else may too. Trips at most once per silence."""
        _user_or_404(user_id, request)
        return vigil.sweep(user_id)

    @app.post("/vigil/{user_id}/resolve")
    def vigil_resolve(user_id: str, request: Request) -> dict:
        """The "I'm okay" button."""
        _user_or_404(user_id, request)
        return vigil.resolve(user_id)

    # -- the crash watch (jim/crashwatch.py) --------------------------------
    # The vigil's acute sibling: a critical reading opens "are you okay?",
    # and N unanswered attempts summon the help the user programmed in
    # advance — a trusted person, and (only if the box was ticked) an
    # emergency-services dispatch request.

    @app.get("/crash-watch/{user_id}")
    def crash_watch_status(user_id: str, request: Request) -> dict:
        """Status — and the clock: a status read advances expired
        attempts, so the console polling is what re-asks the question."""
        _user_or_404(user_id, request)
        crashwatch.sweep(user_id)
        return crashwatch.status(user_id)

    @app.put("/crash-watch/{user_id}")
    def crash_watch_arm(user_id: str, body: CrashWatchArm,
                        request: Request) -> dict:
        _user_or_404(user_id, request)
        return crashwatch.arm(
            user_id, body.trusted_name, body.trusted_channel,
            attempts=body.attempts, window_minutes=body.window_minutes,
            contact_emergency_services=body.contact_emergency_services)

    @app.delete("/crash-watch/{user_id}")
    def crash_watch_disarm(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return crashwatch.disarm(user_id)

    @app.post("/crash-watch/{user_id}/respond")
    def crash_watch_respond(user_id: str, request: Request) -> dict:
        """The "I'm okay" button — the all-clear, from the only voice
        that can give it."""
        _user_or_404(user_id, request)
        return crashwatch.respond(user_id)

    # -- the medicine cabinet (jim/meds.py) ---------------------------------
    # What the user takes, in their words. JIM is not a pharmacist: it
    # tracks what it is told, and a missed dose is a check-in, never an
    # alarm.

    @app.get("/meds/{user_id}")
    def meds_board(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return meds.board(user_id)

    @app.post("/meds/{user_id}", status_code=201)
    def meds_add(user_id: str, body: MedCreate, request: Request) -> dict:
        _user_or_404(user_id, request)
        return meds.add(user_id, body.name, body.dose, body.schedule,
                        purpose=body.purpose, critical=body.critical,
                        notes=body.notes)

    @app.put("/meds/{user_id}/{med_id}")
    def meds_update(user_id: str, med_id: str, body: MedUpdate,
                    request: Request) -> dict:
        _user_or_404(user_id, request)
        return meds.update(user_id, med_id,
                           **body.model_dump(exclude_none=True))

    @app.delete("/meds/{user_id}/{med_id}")
    def meds_archive(user_id: str, med_id: str, request: Request) -> dict:
        """Stopped, not deleted — the history stays honest."""
        _user_or_404(user_id, request)
        return meds.archive(user_id, med_id)

    @app.post("/meds/{user_id}/{med_id}/log")
    def meds_log(user_id: str, med_id: str, body: MedLog,
                 request: Request) -> dict:
        _user_or_404(user_id, request)
        return meds.log(user_id, med_id, body.action, slot=body.slot,
                        note=body.note)

    @app.get("/meds/{user_id}/adherence")
    def meds_adherence(user_id: str, request: Request,
                       days: int = 7) -> dict:
        _user_or_404(user_id, request)
        return meds.adherence(user_id, days=days)

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

    # -- care beacons: a printed code on the things around a watched person --
    # Distinct from the Medical ID above: that card travels with the person and
    # is *read*; this one stays with a place and is *rung*. The alarm comes
    # before the disclosure, and its ceiling is notify_contact. docs/beacons.md

    def _beacon_or_404(bid: str, request: Request) -> dict:
        row = beacons.get(bid)
        if row is None:
            raise HTTPException(404, "beacon not found")
        auth.require(request, "user", row["user_id"])
        return row

    @app.post("/users/{user_id}/beacons", status_code=201)
    def place_beacon(user_id: str, body: BeaconPlace, request: Request) -> dict:
        """Place a beacon. A minor's is guardian-issued only, so the placer is
        taken from the caller's own token rather than the path."""
        user = guardian.get_user(user_id)
        if user is None:
            raise HTTPException(404, "user not found")
        who = auth.principal(request)
        if who is None:
            raise HTTPException(401, "authentication required")
        try:
            return beacons.place(user, body.label, body.placement, body.kind,
                                 placed_by=who["subject_id"])
        except beacons.BeaconError as exc:
            raise HTTPException(422, str(exc))

    @app.get("/users/{user_id}/beacons")
    def list_beacons(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return beacons.for_user(user_id)

    @app.delete("/beacons/{bid}")
    def retire_beacon(bid: str, request: Request) -> dict:
        return beacons.retire(_beacon_or_404(bid, request))

    @app.get("/users/{user_id}/alarms")
    def list_alarms(user_id: str, request: Request,
                    open_only: bool = False) -> list[dict]:
        """Who rang while they were away — their token only. Who called on
        somebody is theirs, not a visitor's to browse.

        Every way help gets summoned lands here: beacon alarms, and — first,
        because it is the acute one — the crash watch's trip, shaped as an
        alarm so one queue answers everything. The sweep runs so a deadline
        that passed since the last look trips before the list is read."""
        _user_or_404(user_id, request)
        crashwatch.sweep(user_id)
        crash = crashwatch.as_alarm(user_id)
        rows = beacons.alarms_for(user_id, open_only)
        return [crash] + rows if crash else rows

    @app.post("/users/{user_id}/alarms/{alarm_id}/clear")
    def clear_alarm(user_id: str, alarm_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        out = (crashwatch.clear_alarm(user_id)
               if alarm_id == crashwatch.ALARM_ID
               else beacons.clear(user_id, alarm_id))
        if out is None:
            raise HTTPException(404, "no open alarm with that id")
        return out

    # The public surface. No token — a stranger holding a phone at a sticker is
    # exactly the caller this exists for.

    @app.get("/c/{bid}", response_class=HTMLResponse)
    def beacon_page(bid: str, request: Request) -> HTMLResponse:
        """What a phone's camera app opens when somebody scans the sticker.

        HTML, because a QR is pointed at by a person holding a phone — this
        used to answer JSON and show a neighbour a wall of braces. The JSON is
        still served at ``/c/{id}/card`` for anything reading it
        programmatically.

        The language is **the finder's**, negotiated from their own
        ``Accept-Language``. Every other localization path in this product
        takes a ``user_id``, and the reader of this page is the one person in
        it who has no account — so until this line existed they were told in
        English, wherever they were standing, that somebody was being watched
        over and what to do about it.
        """
        card = beacons.card(bid)
        language = i18n.negotiate(request.headers.get("accept-language"))
        if card is None:
            return HTMLResponse(landing.gone(language), status_code=404)
        return HTMLResponse(landing.care_page(card, language))

    @app.get("/c/{bid}/card")
    def beacon_card(bid: str) -> dict:
        """Stage one as JSON — for an app rather than a phone browser. Nothing
        clinical, no location, and no word about how the person is."""
        card = beacons.card(bid)
        if card is None:
            raise HTTPException(404, "this code does not resolve to anything")
        return card

    @app.get("/c/{bid}/qr.svg")
    def beacon_qr(bid: str) -> Response:
        """The printable code, in the same medical red as the Medical ID — a
        printed code on a person's things should look like the other one."""
        row = beacons.get(bid)
        if row is None or not row["active"]:
            raise HTTPException(404, "this code does not resolve to anything")
        import segno
        buf = io.BytesIO()
        segno.make(f"{_public_base()}/c/{bid}", error="q").save(
            buf, kind="svg", scale=8, border=2,
            dark="#b3261e", light="#ffffff")
        return Response(content=buf.getvalue(), media_type="image/svg+xml")

    @app.post("/c/{bid}/alarm", status_code=201)
    def raise_alarm(bid: str, body: BeaconAlarm,
                    accept_language: str = Header(default="")) -> dict:
        """Stage two. Raising the alarm is what turns a passer-by into a
        responder, and what earns them the Medical ID — never for a minor.

        **In the finder's language.** The page they pressed the button on has
        been negotiating `Accept-Language` since the round that localized it;
        this route was not, so the two sentences it answers with arrived in
        English on a Spanish page — the badge saying the alarm is raised and
        this is not an emergency service, and the note telling them to call an
        ambulance themselves because this page cannot. Those are the two
        sentences on the whole surface that most need to be understood, and
        they land at the moment somebody is kneeling over a person deciding
        what to do next.

        Two keys by name rather than a walk over the response. The Medical ID
        rides in the same object, and a person's conditions, their contact's
        name and their resting heart rate are facts rather than copy —
        translating a clinical value is how a responder gets misled. `note`
        and `badge` are the only sentences here that this product wrote.
        """
        language = i18n.negotiate(accept_language)
        out = beacons.alarm(bid, body.message, qrme=app.state.qrme)
        if out is None:
            raise HTTPException(404, i18n.tr(
                "this code does not resolve to anything", language))
        for key in ("note", "badge"):
            if isinstance(out.get(key), str):
                out[key] = i18n.tr(out[key], language)
        return out

    # -- the workplace relay: the agent that answers when nobody does -------

    @app.get("/relay/roster")
    def relay_roster() -> dict:
        """Who the relay works through, and whether one is configured here."""
        out = {"configured": relay.available(), "roster": relay.roster(),
               "ceiling": beacons.ALARM_TIER,
               "note": ("the relay escalates people, not sirens — it cannot "
                        "reach emergency services on anyone's behalf")}
        warning = rota.problem()
        if warning:
            out["warning"] = warning
        return out

    @app.get("/relay/rota")
    def relay_rota() -> dict:
        """The rota, and who it would page **right now**.

        Answerable in the afternoon rather than discovered at 3am: an operator
        should be able to see that their night shift resolves to the night
        person before the night they need it to.
        """
        try:
            return rota.describe()
        except rota.RotaError as exc:
            raise HTTPException(422, str(exc))

    @app.get("/relay/channel")
    def relay_channel() -> dict:
        """Whether an escalation can actually reach anybody. URL-free."""
        return notify.channel()

    @app.get("/users/{user_id}/pages")
    def list_pages(user_id: str, request: Request,
                   undelivered_only: bool = False) -> list[dict]:
        """Escalations and whether each reached anyone."""
        _user_or_404(user_id, request)
        return notify.for_user(user_id, undelivered_only)

    @app.get("/users/{user_id}/incidents")
    def list_incidents(user_id: str, request: Request) -> list[dict]:
        """Open, unaccepted alarms on this account's site beacons — at
        incident scope, never person scope."""
        _user_or_404(user_id, request)
        return relay.open_incidents(user_id)

    @app.post("/users/{user_id}/alarms/{alarm_id}/escalate")
    def relay_escalate(user_id: str, alarm_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        out = (crashwatch.escalate_alarm(user_id)
               if alarm_id == crashwatch.ALARM_ID
               else relay.escalate(user_id, alarm_id))
        if out is None:
            raise HTTPException(404, "no alarm with that id")
        return out

    @app.post("/users/{user_id}/alarms/{alarm_id}/accept")
    def relay_accept(user_id: str, alarm_id: str, body: RelayAccept,
                     request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            out = (crashwatch.accept_alarm(user_id, body.responder)
                   if alarm_id == crashwatch.ALARM_ID
                   else relay.accept(user_id, alarm_id, body.responder))
        except ValueError as exc:
            raise HTTPException(422, str(exc))
        if out is None:
            raise HTTPException(404, "no open alarm with that id")
        return out

    @app.post("/alarms/{alarm_id}/guidance")
    def relay_guidance(alarm_id: str, body: RelayQuestion,
                       request: Request) -> dict:
        """What to tell whoever is waiting. Public: the person standing over a
        colleague has no account and needs an answer in ninety seconds.

        And in their own language, from their own Accept-Language — the one
        localization path in this product that cannot key off a user id,
        because this caller has none.
        """
        return relay.guidance(
            alarm_id, body.question, qrme=app.state.qrme,
            language=i18n.negotiate(request.headers.get("accept-language")))

    @app.post("/emergency/{user_id}", status_code=201)
    def emergency(user_id: str, body: EmergencyRequest,
                  request: Request) -> dict:
        """Emergency mode: one coordinated response — reach services, share
        location, contact family, surface the Medical ID, deliver step-by-step
        AI first aid, and alert every connected device."""
        _user_or_404(user_id, request)
        sample = body.sample.model_dump(exclude_none=True) if body.sample else None
        return guardian.emergency(user_id, body.situation, body.location,
                                  sample, qrme=app.state.qrme,
                                  pdi=_vault(user_id))

    @app.post("/activity/{user_id}", status_code=201)
    def observe_activity(user_id: str, body: ActivityObserve,
                         request: Request) -> dict:
        """Ambient background observation: JIM watches an ongoing activity and
        jumps in proactively when a struggle is building — before being asked."""
        _user_or_404(user_id, request)
        # The calendar's bottom rung rides this sense too.
        schedule.remind_pass(user_id, _money_lang(user_id))
        return guardian.observe_activity(
            user_id, body.activity, body.signals, body.note,
            qrme=app.state.qrme, pdi=_vault(user_id))

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
        language = i18n.effective_language(user_id)
        return {"kind": guardian.WAIVER_KIND,
                "terms": i18n.localize_strings(guardian.WAIVER_TERMS,
                                               language),
                "language": language,
                "signed": waiver is not None,
                "signature": waiver["signature"] if waiver else None,
                "signed_at": waiver["signed_at"] if waiver else None}

    @app.post("/waivers/{user_id}", status_code=201)
    def sign_waiver(user_id: str, body: WaiverSign, request: Request) -> dict:
        user = _user_or_404(user_id, request)
        if user.get("birthdate") and _age(
                date.fromisoformat(user["birthdate"])) < 18:
            # Hard line: the autonomous-resuscitation waiver can never be
            # signed for a minor — not by the minor, not by a guardian.
            # Confirm-gated (human-in-the-loop) operation is the ceiling.
            raise HTTPException(
                403, "the autonomous-resuscitation waiver can never be "
                     "signed for a minor — not by the minor and not by a "
                     "guardian; confirm-gated operation is the ceiling")
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

    # ---- the community door (FIG. 2 boxes 222–226) -------------------------

    @app.get("/community/{user_id}")
    def community_view(user_id: str, request: Request,
                       locality: str | None = None) -> dict:
        """QRME's rooms, forums and places, shown through the tandem — the
        community P001's spec text promises, kept where its moderation and
        its languages already live. 409 without a QRME endpoint."""
        _user_or_404(user_id, request)
        if app.state.qrme is None:
            raise HTTPException(
                409, "no QRME endpoint configured (set JIM_QRME_URL) — the "
                     "community lives in QRME and JIM shows the door")
        return community.view(user_id, app.state.qrme, locality=locality)

    @app.get("/community/{user_id}/feed")
    def community_feed(user_id: str, request: Request,
                       cursor: str | None = None) -> dict:
        """QRME's public feed, through the tandem. Read-only by construction:
        there is no route here that posts to it, because publishing belongs
        in QRME under the user's own QRME identity. 409 without an endpoint,
        the same as the rooms above."""
        _user_or_404(user_id, request)
        if app.state.qrme is None:
            raise HTTPException(
                409, "no QRME endpoint configured (set JIM_QRME_URL) — the "
                     "feed lives in QRME and JIM shows the door")
        return community.feed(user_id, app.state.qrme, cursor=cursor)

    @app.post("/community/{user_id}/visits", status_code=201)
    def community_visit(user_id: str, body: CommunityVisit,
                        request: Request) -> dict:
        """Note that a door was opened: the fact, on your own timeline, and
        never anything from inside the room."""
        _user_or_404(user_id, request)
        return community.note_visit(user_id, body.room_id)

    @app.get("/community/{user_id}/visits")
    def community_visits(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return community.history(user_id)

    @app.get("/anonymity/{user_id}")
    def anonymity(user_id: str, request: Request) -> dict:
        """What anonymity keeps and what it costs, said out loud — spec
        [0031]'s "anonymous user name" as an informed choice rather than a
        checkbox with hidden consequences."""
        _user_or_404(user_id, request)
        return identity.posture(guardian.get_user(user_id))

    # ---- the presence (jim/presence.py) -----------------------------------
    #
    # The coach that speaks first. Every read below is answered from rows this
    # deployment already holds — no model, no network — because a guardian
    # that goes quiet when the signal drops is not a guardian.

    @app.get("/presence")
    def presence_who() -> dict:
        """What this thing is, answerable without an account so the answer is
        the same to a child, a guardian, a clinician and a regulator."""
        return presence.who_am_i()

    @app.get("/presence/{user_id}/baseline")
    def presence_baseline(user_id: str, request: Request) -> dict:
        """The six areas, and the evidence behind each standing."""
        _user_or_404(user_id, request)
        return presence.baseline(user_id)

    @app.get("/presence/{user_id}/beat")
    def presence_beat(user_id: str, request: Request,
                      slot: str = "morning") -> dict:
        """The next unprompted thing it would say — or nothing, with the
        reason. Silence is an outcome here, not a failure to produce one."""
        _user_or_404(user_id, request)
        return presence.beat(user_id, slot=slot)

    @app.get("/presence/{user_id}/day")
    def presence_day(user_id: str, request: Request) -> dict:
        """The day's three beats at once, so a client can schedule them and
        then lose its connection without losing the day."""
        _user_or_404(user_id, request)
        return presence.day(user_id)

    @app.post("/presence/{user_id}/deepen")
    def presence_deepen(user_id: str, request: Request,
                        slot: str = "morning") -> dict:
        """The same beat with a model's wording on it. The model may not
        change whether it speaks, which area, or the evidence."""
        _user_or_404(user_id, request)
        return presence.deepen(user_id, slot=slot)

    @app.get("/presence/{user_id}/reach")
    def presence_reach(user_id: str, request: Request,
                       area: str | None = None) -> dict:
        """Other minds — QRME's rooms, desks and profiles, offered. 409
        without a tandem, the same as every other door onto QRME."""
        _user_or_404(user_id, request)
        if app.state.qrme is None:
            raise HTTPException(
                409, "no QRME endpoint configured (set JIM_QRME_URL) — the "
                     "people live in QRME and JIM shows the door")
        return presence.reach_out(user_id, app.state.qrme, area=area)

    @app.get("/presence/{user_id}/surfaces")
    def presence_surfaces(user_id: str, request: Request) -> dict:
        """Where it can speak, and what each surface makes it hold back."""
        _user_or_404(user_id, request)
        return presence.surfaces(user_id)

    @app.put("/presence/{user_id}/surface")
    def presence_choose_surface(user_id: str, body: PresenceSurface,
                                request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return presence.choose_surface(user_id, body.speaks_on)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/presence/{user_id}/bearing")
    def presence_bearing(user_id: str, request: Request) -> dict:
        """How it is carrying itself, and what that does and does not
        change. Companion is the default; the dial is a register, never a
        capability."""
        _user_or_404(user_id, request)
        return presence.posture(user_id)

    @app.put("/presence/{user_id}/bearing")
    def presence_set_bearing(user_id: str, body: PresenceBearing,
                             request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return presence.set_bearing(user_id, body.bearing)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/presence/{user_id}/say")
    def presence_say(user_id: str, request: Request,
                     slot: str = "morning") -> dict:
        """The beat, and whether this surface may speak it.

        The surface rule stops being a label here. `surfaces()` has reported
        `reads_health_aloud` since the picker shipped and nothing read it —
        every consumer was a screen rendering the word next to a button. The
        decision now happens before anything is synthesised.
        """
        _user_or_404(user_id, request)
        return presence.say(user_id, slot=slot)

    @app.get("/presence/{user_id}/due")
    def presence_due(user_id: str, request: Request,
                     hour: int | None = None) -> dict:
        """The hands-free question: is there something to say right now.

        One question a device on a timer has to know how to ask. The slot is
        taken from the hour rather than the caller, so a watch, a pair of
        earbuds and a speaker cannot disagree about what time of day it is
        for the same person.
        """
        _user_or_404(user_id, request)
        return presence.due(user_id, hour=hour)

    @app.get("/presence/{user_id}/growth")
    def presence_growth(user_id: str, request: Request) -> dict:
        """What it has become, with the counts under it — reported change
        held to evidence rather than asserted."""
        _user_or_404(user_id, request)
        return presence.growth(user_id)

    # ---- the user-specific model (clause 11) ------------------------------

    @app.post("/adaptation/{user_id}")
    def rebuild_adaptation(user_id: str, request: Request) -> dict:
        """Run the offline pass: recompute this user's adaptation profile from
        their own stored history and seal it in the vault when configured.
        Nothing is transmitted to any model vendor."""
        _user_or_404(user_id, request)
        return adaptation.rebuild(user_id, pdi=app.state.pdi)

    @app.get("/adaptation/{user_id}")
    def read_adaptation(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return adaptation.get(user_id)

    # ---- the offline fine-tune --------------------------------------------
    #
    # Beside `/adaptation` and not folded into it. That one recomputes a
    # profile that conditions a prompt; this one trains weights. A reader who
    # cannot tell which happened has been told nothing useful, and one route
    # doing both is how that reader is created.

    @app.post("/finetune/{user_id}")
    def run_finetune(user_id: str, request: Request,
                     backend: str | None = None) -> dict:
        """Train a user-specific model offline, from this user's own answered
        follow-ups. Nothing is transmitted: the pass runs with the network
        blocked, so a backend that reached for a model hub raises."""
        _user_or_404(user_id, request)
        return finetune_mod.train(user_id, pdi=app.state.pdi, backend=backend)

    @app.get("/finetune/{user_id}")
    def read_finetune(user_id: str, request: Request) -> dict:
        """The artifact, weights and all. Readable by the person whose history
        trained it — a model somebody cannot inspect is one they cannot
        meaningfully decline."""
        _user_or_404(user_id, request)
        out = finetune_mod.latest(user_id)
        if out is None:
            raise HTTPException(status_code=404,
                                detail="nothing has been trained yet")
        return out

    @app.put("/finetune/{user_id}/active")
    def switch_finetune(user_id: str, body: FinetuneSwitch,
                        request: Request) -> dict:
        """Training and using are two decisions. Off takes effect on the next
        reply and the base behaviour is never more than this switch away."""
        _user_or_404(user_id, request)
        return finetune_mod.activate(user_id, body.active)

    # ---- the state that survives between sessions -------------------------

    @app.get("/continuity/{user_id}")
    def read_continuity(user_id: str, request: Request) -> dict:
        """What the Guardian carries across sessions about this person, in
        named dimensions with their meanings — counts and timings only, never
        anything they wrote."""
        _user_or_404(user_id, request)
        return continuity.state(user_id)

    @app.delete("/continuity/{user_id}")
    def forget_continuity(user_id: str, request: Request) -> dict:
        """Drop it. Every derived thing here has to be droppable by the person
        it was derived from."""
        _user_or_404(user_id, request)
        return {"forgotten": continuity.forget(user_id)}

    # ---- did the counseling work? (spec [0039]) ---------------------------

    @app.get("/followup/{user_id}")
    def open_followups(user_id: str, request: Request) -> dict:
        """What the app should be asking: guidance delivered and not yet
        reported on, plus the recent record of what worked."""
        _user_or_404(user_id, request)
        return {"open": followup.open_for(user_id),
                "history": followup.history(user_id)}

    @app.post("/followup/{user_id}")
    def answer_followup(user_id: str, body: FollowupAnswer,
                        request: Request) -> dict:
        """"It helped" resumes monitoring; "it did not" runs the escalation
        ladder again with the ineffective-guidance rung, and names the humans
        who can help right now."""
        _user_or_404(user_id, request)
        return followup.answer(user_id, body.helped, body.note)

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
                                pdi=_vault(user_id))

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
                              pdi=_vault(row["user_id"]))

    @app.post("/social/connection/{cid}/scrape", status_code=201)
    def social_scrape(cid: str, request: Request) -> dict:
        row = _social_or_404(cid, request)
        if row["direction"] != "collect":
            raise HTTPException(409, "this connection is for publishing, not collecting")
        if row["status"] != "active":
            raise HTTPException(409, "connection has been revoked")
        try:
            return social.fetch_page(row, _public_base(), pdi=_vault(row["user_id"]))
        except ValueError as e:
            raise HTTPException(409, str(e))
        except LookupError as e:
            raise HTTPException(400, str(e))
        except Exception as e:                                # noqa: BLE001
            raise HTTPException(502, f"could not fetch — {e.__class__.__name__}: {e}")

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
                                      pdi=_vault(row["user_id"]))

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
                         pdi=_vault(row["user_id"]))
        db.connect().execute("UPDATE excursions SET learned=1 WHERE id=?", (cid,))
        db.connect().commit()
        return {"learned": True, "already_learned": False,
                "note": "findings folded into the coach's store; the offline "
                        "pipeline reads them on the next question"}

    # ---- the money guardian (jim/money.py) --------------------------------
    # Credentials vault-or-refused; warnings ride the proactive ladder at
    # `checkin` severity and carry their doors; the mandate is a written,
    # revocable handover and its orders are logged proposals. The overview
    # carries its own labels in the reader's language, because the desktop
    # console has no translation table and its English backlog is a ratchet.

    def _money_lang(user_id: str) -> str:
        code, _mode = i18n.get_pref(user_id)
        return code

    @app.get("/money/{user_id}")
    def money_view(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return money.view(user_id, _money_lang(user_id), qrme=app.state.qrme)

    @app.post("/money/{user_id}/accounts", status_code=201)
    def money_add_account(user_id: str, body: MoneyAccountAdd,
                          request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return money.add_account(
                user_id, body.kind, body.institution, body.label or "",
                body.account_number, body.routing_number, body.api_key,
                pdi=_vault(user_id))
        except money.MoneyError as exc:
            raise HTTPException(422, str(exc))

    @app.post("/money/{user_id}/observe")
    def money_observe(user_id: str, body: MoneyObserve,
                      request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return money.observe(user_id, body.account_id, body.balance,
                                 body.note, _money_lang(user_id),
                                 pdi=_vault(user_id), qrme=app.state.qrme)
        except money.MoneyError as exc:
            raise HTTPException(422, str(exc))

    @app.post("/money/{user_id}/statements", status_code=201)
    def money_drop_statement(user_id: str, body: StatementDrop,
                             request: Request) -> dict:
        """Drop a statement file: sealed in the vault, read locally by
        deterministic arithmetic, and — when it closes with a balance —
        walked through the same observe path a hand-typed reading takes."""
        _user_or_404(user_id, request)
        try:
            return money.drop_statement(
                user_id, body.account_id, body.filename or "", body.content,
                _money_lang(user_id), pdi=_vault(user_id),
                qrme=app.state.qrme)
        except money.MoneyError as exc:
            raise HTTPException(422, str(exc))

    @app.get("/money/{user_id}/statements")
    def money_statements(user_id: str, request: Request) -> list[dict]:
        """Dropped statements, newest first — the readings, never the
        files; those stay sealed."""
        _user_or_404(user_id, request)
        return money.statements_for(user_id)

    @app.post("/money/{user_id}/links", status_code=201)
    def money_link_bank(user_id: str, body: BankLink,
                        request: Request) -> dict:
        """Write down a bank-link consent through an aggregator. Status
        stays `consented` until the deployment can actually sync — the
        record never claims data that was not pulled."""
        _user_or_404(user_id, request)
        try:
            return money.link_bank(user_id, body.institution,
                                   body.aggregator, body.kind,
                                   pdi=_vault(user_id))
        except money.MoneyError as exc:
            raise HTTPException(422, str(exc))

    @app.get("/money/{user_id}/links")
    def money_links(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return money.links_for(user_id)

    @app.post("/money/{user_id}/links/{link_id}/sync")
    def money_sync_bank(user_id: str, link_id: str,
                        request: Request) -> dict:
        """Pull balances through the link — or hear exactly why not."""
        _user_or_404(user_id, request)
        try:
            return money.sync_bank(user_id, link_id)
        except money.MoneyError as exc:
            raise HTTPException(422, str(exc))

    @app.delete("/money/{user_id}/links/{link_id}")
    def money_revoke_link(user_id: str, link_id: str,
                          request: Request) -> dict:
        """Taking your hands back is never gated."""
        _user_or_404(user_id, request)
        try:
            return money.revoke_link(user_id, link_id)
        except money.MoneyError as exc:
            raise HTTPException(422, str(exc))

    @app.put("/money/{user_id}/savings")
    def money_set_savings(user_id: str, body: SavingsSet,
                          request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return money.set_savings(user_id, body.goal, body.note)
        except money.MoneyError as exc:
            raise HTTPException(422, str(exc))

    @app.put("/money/{user_id}/mandate")
    def money_set_mandate(user_id: str, body: MandateSet,
                          request: Request) -> dict:
        """The handover. Enabling is Pro-gated through the same capability
        as every other piece of delegated work; revoking is never gated —
        taking your hands back must not have a price."""
        _user_or_404(user_id, request)
        if body.enabled:
            plan = tiers.plan_of(user_id)
            if not tiers.entitles(plan, "synthetic_agents"):
                raise HTTPException(402, {
                    "reason": "plan", "capability": "synthetic_agents",
                    "needs": tiers.CAPABILITIES["synthetic_agents"]["from"],
                    "have": plan,
                    "message": tiers.refusal(plan, "synthetic_agents"),
                    "billing": "simulated — no real funds move",
                    "emergency_unaffected": True,
                })
        try:
            return money.set_mandate(user_id, body.enabled,
                                     body.cap_per_order, body.monthly_cap,
                                     body.asset_classes, body.scope)
        except money.MoneyError as exc:
            raise HTTPException(422, str(exc))

    # ---- booking and scheduling (jim/schedule.py) --------------------------
    # A booking is a row, not a hostage; reminders ride the ladder's bottom
    # rung off the monitor/observe senses; email goes to the user or nowhere.

    @app.get("/schedule/{user_id}")
    def schedule_view(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return schedule.view(user_id, _money_lang(user_id))

    @app.post("/schedule/{user_id}", status_code=201)
    def schedule_book(user_id: str, body: AppointmentIn,
                      request: Request) -> dict:
        user = _user_or_404(user_id, request)
        try:
            return schedule.book(user_id, dict(user), body.title, body.when,
                                 body.where, body.email_reminder,
                                 body.shop_id, body.offering_id,
                                 qrme=app.state.qrme)
        except (schedule.ScheduleError, shopping.ShoppingError) as exc:
            raise HTTPException(422, str(exc))

    @app.delete("/schedule/{user_id}/{appointment_id}")
    def schedule_cancel(user_id: str, appointment_id: str,
                        request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return schedule.cancel(user_id, appointment_id,
                                   qrme=app.state.qrme)
        except schedule.ScheduleError as exc:
            raise HTTPException(422, str(exc))

    # ---- shopping through the tandem (jim/shopping.py) --------------------
    # Browsing is anonymous; ordering is the interactor's act; the history
    # is held HERE. Labels ride the view in the reader's language.

    @app.get("/shopping/{user_id}")
    def shopping_view(user_id: str, request: Request,
                      tag: str | None = None) -> dict:
        _user_or_404(user_id, request)
        return shopping.view(user_id, _money_lang(user_id),
                             qrme=app.state.qrme, tag=tag)

    @app.post("/shopping/{user_id}/order", status_code=201)
    def shopping_order(user_id: str, body: ShopOrderIn,
                       request: Request) -> dict:
        user = _user_or_404(user_id, request)
        try:
            return shopping.order(user_id, dict(user), body.shop_id,
                                  body.offering_id, body.quantity,
                                  qrme=app.state.qrme)
        except shopping.ShoppingError as exc:
            raise HTTPException(422, str(exc))

    @app.post("/shopping/{user_id}/cancel")
    def shopping_cancel(user_id: str, body: ShopCancelIn,
                        request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return shopping.cancel(user_id, body.qrme_order_id,
                                   qrme=app.state.qrme)
        except shopping.ShoppingError as exc:
            raise HTTPException(422, str(exc))

    # ---- your circle (jim/circle.py) --------------------------------------
    # Contacts by mutual invitation, messages that never leave this
    # deployment, per-user switches, and the homepage sandbox. Labels ride
    # the view in the reader's language.

    @app.get("/circle/{user_id}")
    def circle_view(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return circle.view(user_id, _money_lang(user_id))

    @app.put("/circle/{user_id}/features")
    def circle_feature(user_id: str, body: FeatureFlip,
                       request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return circle.set_feature(user_id, body.feature, body.enabled)
        except circle.CircleError as exc:
            raise HTTPException(422, str(exc))

    @app.post("/circle/{user_id}/contacts", status_code=201)
    def circle_invite(user_id: str, body: CircleInviteIn,
                      request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return circle.invite(user_id, body.other_id)
        except circle.CircleError as exc:
            raise HTTPException(422, str(exc))

    @app.delete("/circle/{user_id}/contacts/{other_id}")
    def circle_leave(user_id: str, other_id: str,
                     request: Request) -> dict:
        _user_or_404(user_id, request)
        return circle.leave(user_id, other_id)

    @app.post("/circle/{user_id}/messages", status_code=201)
    def circle_send(user_id: str, body: CircleMessageIn,
                    request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return circle.send_message(user_id, body.to, body.body)
        except circle.CircleError as exc:
            raise HTTPException(422, str(exc))

    @app.get("/circle/{user_id}/messages")
    def circle_messages(user_id: str, request: Request,
                        with_id: str | None = None) -> dict:
        """The thread list, or — `?with_id=` — one conversation."""
        _user_or_404(user_id, request)
        if with_id:
            return {"with": with_id,
                    "messages": circle.thread(user_id, with_id)}
        return {"threads": circle.threads(user_id)}

    @app.get("/circle/{user_id}/homepage/{other_id}")
    def circle_homepage(user_id: str, other_id: str,
                        request: Request) -> dict:
        """A neighbour's page, seen as yourself: the viewer is the
        credential, the owner's switch is the gate."""
        _user_or_404(user_id, request)
        try:
            return circle.homepage(other_id,
                                   viewer_is_owner=other_id == user_id)
        except circle.CircleError:
            raise HTTPException(404, "this homepage is not shared")

    @app.put("/circle/{user_id}/homepage")
    def circle_edit_homepage(user_id: str, body: HomepageIn,
                             request: Request) -> dict:
        _user_or_404(user_id, request)
        try:
            return circle.set_homepage(user_id, body.model_dump(
                exclude_none=True))
        except circle.CircleError as exc:
            raise HTTPException(422, str(exc))

    # ---- budgeting plans ----------------------------------------------------


    @app.put("/budgets/{user_id}")
    def set_budget(user_id: str, body: BudgetSet, request: Request) -> dict:
        """The financial card's promise: guidance that keeps spending aligned
        with a *plan*, not just a hardcoded alarm. Consented spending events
        consume the plan; crossing 80% or the plan itself speaks up."""
        _user_or_404(user_id, request)
        return life.set_budget(user_id, body.category, body.monthly_limit)

    @app.get("/budgets/{user_id}")
    def budgets(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return life.budgets_view(user_id)

    @app.delete("/budgets/{user_id}/{category}")
    def remove_budget(user_id: str, category: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        return life.remove_budget(user_id, category)

    # ---- mood & energy check-ins ------------------------------------------

    @app.post("/checkin/{user_id}", status_code=201)
    def check_in(user_id: str, body: CheckIn, request: Request) -> dict:
        _user_or_404(user_id, request)
        result = life.check_in(user_id, body.mood, body.energy, body.note,
                               pdi=_vault(user_id), stress=body.stress)
        # A worrying note still goes through the Guardian pipeline so crisis
        # language escalates exactly as it does from /monitor.
        if body.note:
            result["guardian"] = guardian.monitor(
                user_id, {}, body.note, qrme=app.state.qrme,
                pdi=_vault(user_id))
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

    @app.post("/coach/{user_id}/specialist")
    def coach_ask_specialist(user_id: str, body: CoachMessage,
                             request: Request) -> dict:
        """Send this question to the QRME specialist covering the area.

        Explicit, because it shares what the person wrote with a profile
        outside JIM. `POST /coach/{id}` only *offers*; this is the door they
        choose. Never reachable from escalation.
        """
        _user_or_404(user_id, request)
        return coach.ask_specialist(user_id, body.area, body.message,
                                    app.state.qrme, pdi=app.state.pdi)

    @app.get("/coach/{user_id}")
    def coach_history(user_id: str, request: Request,
                      area: str | None = None) -> list[dict]:
        _user_or_404(user_id, request)
        return coach.history(user_id, area)

    @app.get("/coach/{user_id}/store")
    def coach_store(user_id: str, request: Request) -> dict:
        """What the offline coach can draw on for this user, provenance and
        all: the curated pack's size, JIM's learned excursions, and the
        deposits paid model turns left behind. This store is the user's own
        asset — readable in full, grown by use."""
        _user_or_404(user_id, request)
        from . import pipeline
        return pipeline.store(user_id)

    @app.get("/coach/{user_id}/curriculum")
    def coach_curriculum(user_id: str, request: Request) -> dict:
        """What JIM should study next for this coach — the coach's own
        recorded misses first, then where the user actually put the AI in
        their life (bands with a learned baseline, active goals, the dose
        board), minus what the store already covers. Each suggestion feeds
        an excursion topic."""
        _user_or_404(user_id, request)
        from . import pipeline
        return pipeline.curriculum(user_id)

    @app.post("/coach/{user_id}/study", status_code=201)
    def coach_study(user_id: str, body: CoachStudy, request: Request) -> dict:
        """JIM imports knowledge for coach, in one press: an excursion on
        the named topic — or the curriculum's top suggestion — with the
        findings learned straight into the store. Online when a model can
        be reached, honestly local when not; either way the store deepens
        and any matching recorded miss closes."""
        _user_or_404(user_id, request)
        from . import pipeline
        topic, area = body.topic, body.area
        if not topic:
            head = pipeline.curriculum(user_id)["suggested"][:1]
            if not head:
                raise HTTPException(409, "nothing to study — the curriculum "
                                         "is empty and no topic was named")
            topic, area = head[0]["topic"], head[0]["area"]
        cloud = app.state.cloud
        brief, redactions = research.sanitize(user_id, topic, [])
        left_host = research.would_leave(cloud)
        findings = research.gather(brief, cloud)
        cid = db.new_id("exc")
        conn = db.connect()
        conn.execute(
            "INSERT INTO excursions (id, user_id, topic, brief, redactions,"
            " left_host, findings, learned, created_at) VALUES (?,?,?,?,?,?,?,1,?)",
            (cid, user_id, topic, brief, redactions, int(left_host),
             findings, db.utcnow()))
        conn.execute(
            "UPDATE gaps SET filled=1 WHERE user_id=? AND lower(question)=lower(?)",
            (user_id, topic))
        conn.commit()
        # `folded`, not `learned`: the store route's `learned` is a list of
        # entries, and one wire name carries one type.
        return {"studied": topic, "area": area, "folded": True,
                "left_host": left_host, "excursion_id": cid,
                "note": "findings folded into the coach's store; the offline "
                        "pipeline reads them on the next question"}

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
        result = life.add_journal(user_id, body.text, pdi=_vault(user_id))
        # Journal text runs the same crisis pipeline as check-in notes.
        result["guardian"] = guardian.monitor(
            user_id, {}, body.text, qrme=app.state.qrme, pdi=_vault(user_id))
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
        # `contribution.send` logs exactly what left, which is what makes the
        # preview and revoke surfaces below able to tell the truth.
        result["contributed"] = False
        if user.get("cloud_contribution") and app.state.cloud is not None:
            result["contributed"] = contribution.send(
                user_id, body.rating, app.state.cloud)
        return result

    @app.get("/users/{user_id}/cloud-contribution")
    def cloud_contribution(user_id: str, request: Request) -> dict:
        """What would leave if you contribute, and everything that already has.

        The settings screen offers "preview before it leaves"; this is the
        thing that lets it. `preview_next` is built by the same function that
        builds the real payload, so it cannot drift into describing something
        the send does not do.
        """
        user = _user_or_404(user_id, request)
        return contribution.view(user_id, bool(user.get("cloud_contribution")))

    @app.post("/users/{user_id}/cloud-contribution/revoke")
    def revoke_cloud_contribution(user_id: str, request: Request) -> dict:
        """Turn contribution off **and** delete what has already gone.

        Consent the screen calls revocable used to mean only "stoppable" —
        nothing identified what had already been sent, so nothing could be
        withdrawn. Each item's opaque ref is asked to be deleted at the
        gateway.
        """
        _user_or_404(user_id, request)
        return contribution.revoke(user_id, app.state.cloud)

    # ---- a second ear: borrowing a wearable's microphone -------------------
    # Permission and state only; capture is on the device. See jim/mic.py.

    @app.get("/mic/types")
    def mic_types() -> dict:
        """Which microphones can be channel 2, and which cannot.

        Published so a client can offer the right list rather than guessing,
        and so the reason a room microphone is excluded is discoverable
        instead of arriving as a refusal.
        """
        return {
            "personal": sorted(mic.PERSONAL_TYPES),
            "ambient": sorted(t for t, ok in mic.MIC_TYPES.items() if not ok),
            "rule": "a microphone pointed at you can be channel 2; one "
                    "pointed at a room cannot, because everyone it picks up "
                    "would be lending their voice without being asked",
        }

    @app.get("/mic/gains")
    def mic_gains() -> dict:
        """How wide channel 2 can be told to listen.

        Published alongside `/mic/types` so a client can build the dial from
        the service's own words — including which levels reach past the
        wearer, which is the property the cap is judged on.
        """
        return {
            "levels": [{"gain": name, **spec}
                       for name, spec in mic.GAIN_LEVELS.items()],
            "default": mic.DEFAULT_GAIN,
            "capped_during": list(mic.OTHERS_AUDIBLE),
            "voice_focus": mic.VOICE_FOCUS,
            "rule": "every level is you at a different distance, never more "
                    "people — the channel keys on your voice and drops the "
                    "chatter at all of them. You can set it however you like; "
                    "while somebody else's voice is in the air the agent stays "
                    "narrow anyway, and your setting comes back afterwards",
        }

    @app.put("/users/{user_id}/mic")
    def attach_mic(user_id: str, body: MicAttach, request: Request) -> dict:
        """Nominate a microphone the agent may borrow as channel 2.

        Attaching is **not** listening — it says which one may be lent.
        """
        _user_or_404(user_id, request)
        try:
            return mic.attach(user_id, body.device_name, body.mic_type)
        except mic.MicError as exc:
            raise HTTPException(422, str(exc))

    @app.delete("/users/{user_id}/mic")
    def detach_mic(user_id: str, request: Request) -> dict:
        """Remove the wearable, ending any live handover with it."""
        _user_or_404(user_id, request)
        return mic.detach(user_id)

    @app.get("/users/{user_id}/mic")
    def mic_state(user_id: str, request: Request) -> dict:
        """What the agent can hear right now, in words you can check."""
        _user_or_404(user_id, request)
        return mic.state(user_id)

    @app.put("/users/{user_id}/mic/gain")
    def set_mic_gain(user_id: str, body: MicGain, request: Request) -> dict:
        """Turn channel 2 up or down.

        Accepted at any level, including mid-call — a control that refuses
        teaches people it is broken. What a call changes is the *effective*
        gain, which is reported back here alongside the setting.
        """
        _user_or_404(user_id, request)
        try:
            return mic.set_gain(user_id, body.gain)
        except mic.MicError as exc:
            raise HTTPException(422, str(exc))

    @app.post("/users/{user_id}/mic/handover", status_code=201)
    def hand_over_mic(user_id: str, body: MicHandover,
                      request: Request) -> dict:
        """Lend the agent the wearable while your main microphone is busy.

        Refused on speaker, or with others in earshot: the wearable would be
        picking up somebody who is not a user here and was never asked.
        """
        _user_or_404(user_id, request)
        try:
            return mic.handover(user_id, body.reason, body.route,
                                body.others_present, body.primary_device)
        except mic.MicError as exc:
            raise HTTPException(403, str(exc))

    @app.post("/users/{user_id}/mic/release")
    def release_mic(user_id: str, request: Request) -> dict:
        """Take the microphone back."""
        _user_or_404(user_id, request)
        return mic.release(user_id)

    @app.get("/users/{user_id}/mic/history")
    def mic_history(user_id: str, request: Request) -> list[dict]:
        """Every time the agent held it, and for how long."""
        _user_or_404(user_id, request)
        return mic.history(user_id)

    # ---- reaching a real clinician ----------------------------------------
    # JIM matches and prepares; it never holds the credential or relays the
    # assertion. See jim/referral.py.

    @app.put("/users/{user_id}/locality")
    def set_locality(user_id: str, body: LocalitySet,
                     request: Request) -> dict:
        """The town a referral should search near — a place name, not a
        position, and clearable by sending null."""
        _user_or_404(user_id, request)
        return referral.set_locality(user_id, body.locality)

    @app.get("/users/{user_id}/referral/clinicians")
    def referral_clinicians(user_id: str, condition: str,
                            request: Request) -> dict:
        """Real clinicians for this condition, near this user if known."""
        _user_or_404(user_id, request)
        return referral.clinicians(user_id, condition, app.state.qrme)

    @app.post("/users/{user_id}/referral/prepare", status_code=201)
    def prepare_referral(user_id: str, body: ReferralPrepare,
                         request: Request) -> dict:
        """Assemble the summary and raise the signature that would release it.

        **Nothing is released.** The response carries the package so the user
        can read what would go, and a challenge their device signs against
        QRME — the Face ID prompt belongs to QRME, not to the Guardian.
        """
        _user_or_404(user_id, request)
        spec = guardian._specialist(body.condition)
        try:
            return referral.prepare(user_id, body.condition, body.provider_id,
                                    spec, app.state.qrme, body.capture_ids)
        except capture_mod.CaptureError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.post("/users/{user_id}/referral/requests/{request_id}/released")
    def confirm_referral_release(user_id: str, request_id: str,
                                 request: Request) -> dict:
        """The client reports that the QRME signing ceremony completed.

        JIM cannot observe it — the signature is raised against QRME's relying
        party — so this is a report, and `jim/referral.py` says so plainly.
        """
        _user_or_404(user_id, request)
        try:
            return referral.mark_released(user_id, request_id)
        except referral.ReferralError as exc:
            raise HTTPException(404, str(exc)) from None

    @app.get("/users/{user_id}/referral/requests")
    def referral_requests(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return referral.requests_for(user_id)

    # ---- handing a specialist a task, not a turn --------------------------
    # Deliberately not reachable from `monitor`: escalation decides in one
    # call and must keep doing so. See jim/handoff.py.

    @app.post("/users/{user_id}/specialist-tasks", status_code=201)
    def start_specialist_task(user_id: str, body: SpecialistTaskStart,
                              request: Request) -> dict:
        """Ask a QRME specialist to take on multi-step work.

        A refusal is a 200-shaped answer with `started: false` and a reason,
        not an error — the caller may still have somebody in front of them,
        and "this specialist doesn't accept delegated work" is information
        rather than a fault.
        """
        _user_or_404(user_id, request)
        spec = guardian._specialist(body.condition)
        return handoff.start(user_id, body.goal, spec, app.state.qrme,
                             body.plan)

    @app.get("/users/{user_id}/specialist-tasks")
    def list_specialist_tasks(user_id: str, request: Request) -> list[dict]:
        _user_or_404(user_id, request)
        return handoff.list_for(user_id)

    @app.get("/users/{user_id}/specialist-tasks/{task_id}")
    def get_specialist_task(user_id: str, task_id: str,
                            request: Request) -> dict:
        _user_or_404(user_id, request)
        out = handoff.status(user_id, task_id, app.state.qrme)
        if out is None:
            raise HTTPException(404, "no such task")
        return out

    @app.post("/users/{user_id}/specialist-tasks/{task_id}/advance")
    def advance_specialist_task(user_id: str, task_id: str,
                                request: Request) -> dict:
        """Run the specialist's next phase."""
        _user_or_404(user_id, request)
        out = handoff.advance(user_id, task_id, app.state.qrme)
        if out is None:
            raise HTTPException(404, "no such task")
        return out

    # ---- "help us improve": product feedback on the app itself ------------
    # Distinct from guidance feedback above: open to anyone, about the app.

    _IMPROVE_CATEGORIES = ("idea", "improvement", "bug", "praise", "other")

    def _submitter(request: Request) -> str:
        who = auth.principal(request)
        return f"{who['role']}:{who['subject_id']}" if who else "anonymous"

    @app.post("/improve", status_code=201)
    def submit_improvement(body: ImprovementSubmit, request: Request) -> dict:
        """Tell us how to make the app better — an idea, an improvement, a
        bug, or praise, with an optional 1–5 rating. Open to anyone."""
        if body.category not in _IMPROVE_CATEGORIES:
            raise HTTPException(
                422, i18n.fill(i18n.MUST_BE_ONE_OF, field="category",
                              choices=", ".join(_IMPROVE_CATEGORIES)))
        message = body.message.strip()
        if not message:
            raise HTTPException(422, "a message is required")
        if body.rating is not None and not (1 <= body.rating <= 5):
            raise HTTPException(422, "rating must be 1–5")
        conn = db.connect()
        iid = db.new_id("imp")
        conn.execute(
            "INSERT INTO improvements (id, submitter, category, message,"
            " rating, status, created_at) VALUES (?,?,?,?,?,'received',?)",
            (iid, _submitter(request), body.category, message, body.rating,
             db.utcnow()))
        conn.commit()
        return {"id": iid, "category": body.category, "status": "received",
                "note": "thank you — this goes straight to the team"}

    @app.get("/improve")
    def list_improvements(request: Request) -> dict:
        """The caller's own submissions (newest first) plus the public tally
        by category — never anyone else's words."""
        conn = db.connect()
        submitter = _submitter(request)
        mine = []
        if submitter != "anonymous":
            mine = [dict(r) for r in conn.execute(
                "SELECT id, category, message, rating, status, created_at"
                " FROM improvements WHERE submitter=?"
                " ORDER BY created_at DESC, rowid DESC", (submitter,)).fetchall()]
        tally = {c: 0 for c in _IMPROVE_CATEGORIES}
        for row in conn.execute(
                "SELECT category, COUNT(*) AS n FROM improvements"
                " GROUP BY category").fetchall():
            if row["category"] in tally:
                tally[row["category"]] = row["n"]
        return {"mine": mine, "tally": tally, "total": sum(tally.values()),
                "categories": list(_IMPROVE_CATEGORIES)}

    # ---- ability is not a gate: the accessibility door --------------------
    # Three questions and none is a diagnosis. Deliberately account-free and
    # unlinked: the table has no submitter column, because a report about
    # ability must not become a record about a body — and the person this
    # door exists for may be the person the enrollment shut out. The words
    # stay on this deployment (sealed to the PDI vault when configured) and
    # are never relayed to the shared problems collector, which is
    # content-free by design where this is nothing but content.

    @app.post("/access/reports", status_code=201)
    def submit_access_report(body: AccessReportSubmit,
                             request: Request) -> dict:
        """File an accessibility report — no account, no diagnosis."""
        doing = body.doing.strip()
        wall = body.wall.strip()
        if not doing or not wall:
            raise HTTPException(
                422, "say what you were trying to do and what stood in the way")
        lang = body.lang if body.lang in i18n.SUPPORTED else "en"

        rid = db.new_id("acc")
        at = db.utcnow()

        pdi_key = None
        pdi = app.state.pdi
        if pdi is not None:
            pdi_key = f"jim/access/reports/{rid}"
            payload = {"report_id": rid, "lang": lang, "doing": doing,
                       "wall": wall,
                       "help": (body.help or "").strip() or None, "at": at}
            try:
                pdi.put(pdi_key, json.dumps(payload))
            except Exception:
                pdi_key = None   # vault unreachable — the local row stands

        conn = db.connect()
        conn.execute(
            "INSERT INTO access_reports (id, lang, doing, wall, help,"
            " status, pdi_key, created_at) VALUES (?,?,?,?,?,'received',?,?)",
            (rid, lang, doing, wall, (body.help or "").strip() or None,
             pdi_key, at))
        conn.commit()
        return {"id": rid, "status": "received",
                "note": "thank you — this becomes tracked work, and it "
                        "stays on this deployment"}

    @app.get("/access/reports")
    def read_access_reports(request: Request) -> dict:
        """Every report, newest first — for the deployment's steward."""
        auth.require_reviewer(request)
        conn = db.connect()
        reports = [dict(r) for r in conn.execute(
            "SELECT id, lang, doing, wall, help, status, pdi_key, created_at"
            " FROM access_reports"
            " ORDER BY created_at DESC, rowid DESC").fetchall()]
        return {"reports": reports, "total": len(reports)}

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

    @app.get("/custody/{user_id}")
    def custody(user_id: str, request: Request) -> dict:
        """The user's sealed tandem exchanges: every QRME specialist chat
        this Guardian sealed into the PDI vault, plus whether PDI's
        tamper-evident audit chain is intact."""
        _user_or_404(user_id, request)
        if app.state.pdi is None:
            raise HTTPException(
                409, "no PDI vault configured (set JIM_PDI_URL / JIM_PDI_TOKEN)")
        keys = [r["key"] for r in db.connect().execute(
            "SELECT key FROM vault_keys WHERE user_id=? AND key LIKE ?"
            " ORDER BY key", (user_id, f"jim/{user_id}/tandem/%")).fetchall()]
        return {"records": keys, "count": len(keys),
                "chain_intact": app.state.pdi.audit_verify()}

    @app.get("/custody/{user_id}/provenance")
    def custody_provenance(user_id: str, key: str, request: Request) -> dict:
        """PDI's derivation trail for one sealed exchange — origin, seal
        details, audit history — readable only for the user's own custody
        records."""
        _user_or_404(user_id, request)
        if app.state.pdi is None:
            raise HTTPException(
                409, "no PDI vault configured (set JIM_PDI_URL / JIM_PDI_TOKEN)")
        owned = db.connect().execute(
            "SELECT 1 FROM vault_keys WHERE user_id=? AND key=?",
            (user_id, key)).fetchone()
        if owned is None or not key.startswith(f"jim/{user_id}/tandem/"):
            raise HTTPException(404, "no such custody record")
        result = app.state.pdi.provenance(key)
        if result is None:
            raise HTTPException(502, "PDI vault unreachable")
        return result

    @app.get("/provider/{user_id}")
    def provider_portal(user_id: str, request: Request) -> dict:
        user = _user_or_404(user_id, request)
        if not user.get("provider_consent"):
            raise HTTPException(
                403, "the user has not consented to provider access")
        return life.provider_summary(user)

    # ---- portability and erasure ("take it or delete it, anytime") --------

    @app.get("/data/{user_id}")
    def export_data(user_id: str, request: Request) -> dict:
        """Everything this deployment holds about you, by table.

        There was no route here. This product keeps a medicine cabinet, a
        money guardian's accounts and mandates, clinical captures, a journal
        and a continuity vector, and offered its owner a way to erase all of
        it and no way to take it — while the suite gateway's GDPR Article 20
        bundle listed this product's contribution as a progress report.

        Live credentials are dropped per column, not per table: what a watch
        channel was for is the person's own history and its token is not
        theirs to mail anywhere.
        """
        _user_or_404(user_id, request)
        return life.export_user_data(user_id)

    @app.delete("/data/{user_id}")
    def delete_data(user_id: str, request: Request) -> dict:
        _user_or_404(user_id, request)
        result = life.delete_user_data(user_id, pdi=app.state.pdi)
        auth.revoke_subject(user_id)   # the user token dies with the data
        return result

    # The console itself, served from this API so a phone loads the UI and
    # calls the API on one origin (no CORS, nothing to configure). Mounted
    # last so it can never shadow an API route; absent until app/ is built.
    _console = mobile.console_dir()
    if _console is not None:
        from fastapi.staticfiles import StaticFiles
        app.mount("/app", StaticFiles(directory=str(_console), html=True),
                  name="console")

        # The front door. Measured live at 0.60.9: the bare domain answered
        # {"detail": "Not Found"}, because the console lives under /app and
        # nothing said so. A tester types the domain, not the mount point.
        # Registered only when there is a console to land on — headless
        # deployments keep their honest 404.
        from fastapi.responses import RedirectResponse

        @app.get("/", include_in_schema=False)
        async def _the_front_door() -> RedirectResponse:
            return RedirectResponse("/app/")

    # What a page promises a browser before it says anything else.
    #
    # These products serve HTML a person reaches without an account, on a
    # device that is not theirs: the sticker a stranger kneels over, the
    # sealed-carrier card, the page a sign-in provider sends a browser back
    # to. Measured over HTTP at 0.59.3, every one of them went out with no
    # Content-Security-Policy, no X-Content-Type-Options, no X-Frame-Options
    # and no Referrer-Policy — and nothing in-process could see that, because
    # a TestClient reads none of those headers and a browser reads all of
    # them.
    #
    # The nonce is minted before the route runs so the page builders can
    # stamp it on their own inline script; the policy then names that nonce
    # and nothing else, which is the difference between a header that stops
    # an injected `<script>` and one that decorates the response.
    #
    #     asked     is the page correct
    #     mattered  what can a page do that is not
    # Android's HttpURLConnection refuses to speak PATCH — a
    # ProtocolException, not a preference — so that shell sends POST with
    # `x-http-method-override: PATCH`. Honoured for PATCH alone: the two
    # verbs the stack can already say need no override, and an override to
    # anything else is ignored rather than obeyed.
    @app.middleware("http")
    async def _the_verb_the_phone_cannot_say(request: Request, call_next):
        if (request.method == "POST"
                and request.headers.get("x-http-method-override", "")
                    .upper() == "PATCH"):
            request.scope["method"] = "PATCH"
        return await call_next(request)

    @app.middleware("http")
    async def _what_a_page_promises_a_browser(request: Request, call_next):
        value = pagehead.new_nonce()
        response = await call_next(request)
        if response.headers.get("content-type", "").startswith("text/html"):
            for key, header in pagehead.HEADERS.items():
                response.headers.setdefault(key, header)
            # Two kinds of HTML leave this app. The server-rendered pages
            # carry an inline script the nonce policy names; the console under
            # /app is a built bundle whose script is an external file no nonce
            # can reach. Stamping the console with the nonce policy blanks it
            # — the browser refuses its own bundle — which is what 0.60.9
            # first shipped to a real host. See pagehead.console_policy.
            path = request.url.path
            chosen = (pagehead.console_policy()
                      if path == "/app" or path.startswith("/app/")
                      else pagehead.policy(value))
            response.headers.setdefault("content-security-policy", chosen)
        return response

    # A failure the console can read.
    #
    # An unhandled exception is rendered by Starlette's `ServerErrorMiddleware`,
    # which sits *outside* every middleware this factory adds — including CORS.
    # So a 500 went back to a browser with no `access-control-allow-origin`, the
    # browser dropped the whole response, and the console reported a network
    # error. Measured over HTTP at 0.59.2, in all three products:
    #
    #     GET /health   200   access-control-allow-origin: *
    #     a 500         500   access-control-allow-origin: None
    #
    # No in-process test could see it: a `TestClient` never sends an `Origin`
    # and never runs the browser's rule. And the consequence is worse here than
    # the missing header suggests — this estate's consoles distinguish "the
    # backend is unreachable" from "the backend refused", and a 500 the browser
    # discards is indistinguishable from the first. The version-mismatch guard
    # and the problem reporter both read a failure that never arrives.
    #
    # Registering `@app.exception_handler(Exception)` does not fix it: Starlette
    # hands that handler to `ServerErrorMiddleware`, which is still outside the
    # CORS layer. It has to be a middleware, and it has to sit *inside* CORS —
    # which is why the CORS block below is the last one added.
    #
    #     asked     does the server answer when a route fails
    #     mattered  does the answer reach the reader
    #
    # The body says nothing about what broke. The traceback is logged here and
    # stays here; what leaves is a status and a sentence, which is the same
    # posture every other refusal in this product takes.
    @app.middleware("http")
    async def _a_failure_the_console_can_read(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            _log.exception("unhandled error on %s %s",
                           request.method, request.url.path)
            return JSONResponse(
                status_code=500,
                content={"detail": "server_error",
                         "message": "Something went wrong on our side. "
                                    "Nothing you sent was recorded."})

    # Last on purpose, and this is load-bearing. `add_middleware` inserts at
    # the front, so the middleware registered last is the outermost — and CORS
    # has to be outside the catch-all above, or the 500 it builds goes back
    # without the header again. The three products used to disagree about this
    # ordering: two added CORS before their request-scoped middleware and one
    # after, which nothing was comparing.
    _origins = os.environ.get("JIM_CORS_ORIGINS")
    if _origins:
        from fastapi.middleware.cors import CORSMiddleware
        _allow = ["*"] if _origins.strip() == "*" else [
            o.strip() for o in _origins.split(",") if o.strip()]
        app.add_middleware(
            CORSMiddleware, allow_origins=_allow, allow_credentials=False,
            allow_methods=["*"], allow_headers=["*"])

    return app


app = create_app()
