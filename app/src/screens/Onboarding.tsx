import { useEffect, useState } from "react";
import { api, getBase, setBase, getSignupKey, setSignupKey } from "../api";
import { useSession } from "../store";
import { t as tr, visitorLang } from "../l10n";

type Mode = "signup" | "code" | "signin" | "reset";

/** Under 18 on the day they sign up — the bar the backend applies. */
function isMinor(birthdate: string): boolean {
  if (!birthdate) return false;
  const b = new Date(birthdate + "T00:00:00");
  if (isNaN(b.getTime())) return false;
  const now = new Date();
  let age = now.getFullYear() - b.getFullYear();
  if (now.getMonth() < b.getMonth()
      || (now.getMonth() === b.getMonth() && now.getDate() < b.getDate())) age -= 1;
  return age < 18;
}

// A password input with the conventional show/hide toggle: hidden characters
// are the reason typos survive, and letting people look is the standard cure
// (alongside typing it twice on the signup form).
function PasswordField(props: {
  label: string; value: string; placeholder?: string;
  onChange: (v: string) => void;
}) {
  const [shown, setShown] = useState(false);
  return (
    <label>{props.label}
      <span className="pw-wrap">
        <input type={shown ? "text" : "password"} value={props.value}
               placeholder={props.placeholder}
               onChange={(e) => props.onChange(e.target.value)} />
        <button type="button" className="pw-toggle" tabIndex={-1}
                aria-label={shown ? "Hide password" : "Show password"}
                onClick={() => setShown(!shown)}>
          {shown ? "Hide" : "Show"}
        </button>
      </span>
    </label>
  );
}

export function Onboarding({ onAccess }: { onAccess?: () => void } = {}) {
  const { setSession } = useSession();
  const [mode, setMode] = useState<Mode>("signup");
  // No pre-filled identity. A name sitting in the box is the one most people
  // never change, and a wrong birthdate in an age-verification field is worse
  // than an empty one — the user is the only source for either.
  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [email, setEmail] = useState("");
  const [guardianEmail, setGuardianEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [consent, setConsent] = useState(false);
  // Spec [0031] box 212: enroll under a pseudonym instead of a name.
  const [anonymous, setAnonymous] = useState(false);
  const [legalName, setLegalName] = useState("");
  const [code, setCode] = useState("");
  const [delivery, setDelivery] = useState<string | null>(null);
  // Whether this deployment requires an invite key to create an account —
  // read from /health, so the field appears only where the gate exists. A
  // laptop install never sees it; the beta host always does.
  const [needsInvite, setNeedsInvite] = useState(false);
  const [inviteKey, setInviteKey] = useState(getSignupKey());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [oauthDoors, setOauthDoors] = useState<
    { provider: string; name: string; configured: boolean; setup?: string }[]>([]);
  const [oauthWaiting, setOauthWaiting] = useState(false);

  useEffect(() => {
    api.oauthProviders().then((r) => setOauthDoors(r.providers)).catch(() => {});
  }, []);

  async function signInWith(provider: string) {
    setError(null); setNotice(null); setOauthWaiting(true);
    try {
      // On the signup tab the enrollment rides along: the provider vouches
      // for the inbox, never for the consent questions.
      const enroll = mode === "signup"
        ? { display_name: name.trim(), birthdate, terms_consent: consent, anonymous,
            legal_name: anonymous && legalName.trim() ? legalName.trim() : undefined }
        : undefined;
      if (mode === "signup" && (!name.trim() || !consent)) {
        setError("Fill in your name and consent first — Google or Apple can vouch for your email, not your answers.");
        setOauthWaiting(false);
        return;
      }
      const started = await api.oauthStart(provider, enroll);
      window.open(started.url, "_blank");
      setNotice("Finish signing in with the browser window that just opened…");
      const until = Date.now() + 120000;
      while (Date.now() < until) {
        await new Promise((r) => setTimeout(r, 2000));
        const got = await api.oauthClaim(started.state).catch(() => null);
        if (got === null) { setError("Sign-in was not completed — try again."); break; }
        if (got.ready && got.user_token) {
          setSession({ userId: (got.id || got.user_id)!, userToken: got.user_token,
                       displayName: got.display_name || "" });
          return;
        }
      }
    } catch (e) { setError((e as Error).message); }
    finally { setOauthWaiting(false); }
  }

  // The desktop shell is only the console; the Guardian itself is the local
  // backend. Check for it up front so the form never turns a missing backend
  // into a cryptic fetch error after it has been filled in.
  const [backendUp, setBackendUp] = useState<boolean | null>(null);
  const [base, setBaseInput] = useState(getBase());

  async function checkBackend() {
    setBackendUp(null);
    try { await api.health(); setBackendUp(true); }
    catch { setBackendUp(false); }
  }
  useEffect(() => { checkBackend(); }, []);
  function saveBase() { setBase(base); checkBackend(); }

  // On the code screen, the person may verify by clicking the emailed link
  // in their browser instead of typing the code. The app holds the email and
  // password, so it notices on its own: poll sign-in until the address is
  // proven, then continue without another keystroke.
  useEffect(() => {
    if (mode !== "code" || !password) return;
    const timer = setInterval(async () => {
      try {
        const u = await api.signin({ email: email.trim(), password });
        setSession({ userId: u.user_id, userToken: u.user_token, displayName: u.display_name || "" });
      } catch { /* not verified yet — keep waiting */ }
    }, 3000);
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, email, password]);

  function switchMode(m: Mode) {
    setMode(m); setError(null); setNotice(null); setCode("");
    setPassword(""); setConfirm("");
  }

  async function run<T>(fn: () => Promise<T>, then: (r: T) => void) {
    setBusy(true); setError(null); setNotice(null);
    try { then(await fn()); }
    catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  const passwordsMatch = password === confirm;

  useEffect(() => {
    api.health().then((h) => setNeedsInvite(!!h.signup_key)).catch(() => {});
  }, []);

  const signup = async () => {
    setBusy(true); setError(null); setNotice(null);
    try {
      const r = await api.signup({ email: email.trim(), password, display_name: name.trim(),
                                   birthdate, terms_consent: consent, anonymous,
                                   guardian_consent: isMinor(birthdate) || undefined,
                                   guardian_email: isMinor(birthdate) && guardianEmail.trim()
                                     ? guardianEmail.trim() : undefined,
                                   legal_name: anonymous && legalName.trim() ? legalName.trim() : undefined });
      if (r.verification === "local" && r.user_token) {
        // No mail transport on this deployment (the desktop install): the
        // machine owner is trusted, the account is already active.
        setSession({ userId: r.id!, userToken: r.user_token, displayName: r.display_name });
        return;
      }
      setDelivery(r.code_delivery || null); setMode("code");
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already pending")) {
        // A signup that crashed mid-flight (0.4.3 did exactly this) leaves a
        // pending account. Never strand the person on the form for that —
        // go to the code screen and issue a fresh code.
        setMode("code");
        try {
          const r = await api.resendCode(email.trim());
          setDelivery(r.code_delivery);
          setNotice("This address already had a signup in progress — we've sent a fresh code.");
        } catch (e2) { setError((e2 as Error).message); }
      } else if (msg.includes("already exists")) {
        setMode("signin");
        setNotice("This address already has an account — sign in (or use Forgot password).");
      } else {
        setError(msg);
      }
    } finally { setBusy(false); }
  };
  const verify = () => run(
    () => api.verifyEmail({ email: email.trim(), code: code.trim() }),
    (u) => setSession({ userId: u.id, userToken: u.user_token, displayName: u.display_name }),
  );
  const resend = () => run(
    () => api.resendCode(email.trim()),
    (r) => { setDelivery(r.code_delivery); setNotice("A new code is on its way — the old one no longer works."); },
  );
  const signin = () => run(
    () => api.signin({ email: email.trim(), password }),
    (u) => setSession({ userId: u.user_id, userToken: u.user_token, displayName: u.display_name || "" }),
  );
  const startReset = () => run(
    () => api.requestReset(email.trim()),
    (r) => { setDelivery(r.code_delivery); setNotice("If that address has an account, a reset code is on its way."); },
  );
  const finishReset = () => run(
    () => api.resetPassword({ email: email.trim(), code: code.trim(), new_password: password }),
    () => { switchMode("signin"); setNotice("Password changed — sign in with the new one."); },
  );

  const isDesktop = Boolean((window as unknown as { jimDesktop?: unknown }).jimDesktop);
  const whereIsTheCode = delivery === "console"
    ? (isDesktop
        ? <> {tr("onb.nomail", visitorLang())} <b>{tr("onb.nomail.log", visitorLang())}</b> {tr("onb.nomail.open", visitorLang())}</>
        : <> {tr("onb.nomail", visitorLang())} <b>{tr("onb.nomail.terminal", visitorLang())}</b></>)
    : null;

  return (
    <div className="onboarding">
      <div className="onboard-card">
        <div className="orb big" />
        <h1>{tr("onb.tagline", visitorLang())}</h1>
        <p className="muted">{tr("onb.pitch", visitorLang())}</p>

        {(mode === "signup" || mode === "signin") && (
          <div className="tabs">
            <button className={mode === "signup" ? "tab active" : "tab"}
                    onClick={() => switchMode("signup")}>{tr("onb.create", visitorLang())}</button>
            <button className={mode === "signin" ? "tab active" : "tab"}
                    onClick={() => switchMode("signin")}>{tr("onb.signin", visitorLang())}</button>
          </div>
        )}

        {(mode === "signup" || mode === "signin") && oauthDoors.length > 0 && (
          <div className="oauth-doors">
            {oauthDoors.map((d) => (
              <button key={d.provider} disabled={!d.configured || oauthWaiting}
                      title={d.configured ? undefined : d.setup}
                      onClick={() => signInWith(d.provider)}>
                {tr("onb.signwith", visitorLang())
                  .replace("{mode}", mode === "signup"
                    ? tr("onb.mode.up", visitorLang())
                    : tr("onb.mode.in", visitorLang()))
                  .replace("{provider}", d.name)}
                {!d.configured && <span className="muted small"> {tr("onb.oauth.absent", visitorLang())}</span>}
              </button>
            ))}
          </div>
        )}

        {mode === "signup" && (<>
          <label>{tr("onb.name", visitorLang())}<input value={name} placeholder={tr("onb.yourname", visitorLang())} onChange={(e) => setName(e.target.value)} /></label>
          {/* Spec [0031] box 212: an anonymous user name is a first-class
              choice, and the tradeoff is stated where the choice is made. */}
          <label className="check">
            <input type="checkbox" checked={anonymous}
                   onChange={(e) => setAnonymous(e.target.checked)} />
            {tr("onb.anon", visitorLang())}
          </label>
          {anonymous && (<>
            <p className="field-hint">
              {tr("onb.legalname.why", visitorLang())}
            </p>
            <label>{tr("onb.legalname", visitorLang())}
              <input value={legalName} placeholder={tr("onb.legalname.blank", visitorLang())}
                     onChange={(e) => setLegalName(e.target.value)} /></label>
          </>)}
          <label>{tr("onb.birthdate", visitorLang())}<input type="date" value={birthdate} onChange={(e) => setBirthdate(e.target.value)} /></label>
          {isMinor(birthdate) && (
            /* Verified parental consent: the activation code goes to this
               address, so the click that opens the account is the
               guardian's own. */
            <label>{tr("onb.guardian", visitorLang())}<input type="email" value={guardianEmail}
                   onChange={(e) => setGuardianEmail(e.target.value)} /></label>
          )}
          <label>{tr("onb.email", visitorLang())}<input type="email" value={email} placeholder={tr("onb.email.ph", visitorLang())} onChange={(e) => setEmail(e.target.value)} /></label>
          <PasswordField label="Password" value={password} placeholder={tr("onb.password.min", visitorLang())} onChange={setPassword} />
          <p className="field-hint">{tr("onb.password.min", visitorLang())}</p>
          {/* Typed twice on purpose: hidden characters are how a typo gets
              remembered wrong with total confidence. The match check is
              instant, before anything is submitted. */}
          <PasswordField label="Re-enter password" value={confirm} placeholder={tr("onb.password.same", visitorLang())} onChange={setConfirm} />
          {confirm && !passwordsMatch && (
            <div className="error">{tr("onb.password.mismatch", visitorLang())}</div>
          )}
          <label className="check">
            <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
            {tr("onb.consent", visitorLang())}
          </label>
          {needsInvite && (<>
            <label>{tr("onb.invite", visitorLang())}
              <input value={inviteKey}
                     placeholder={tr("onb.invite", visitorLang())}
                     onChange={(e) => { setInviteKey(e.target.value); setSignupKey(e.target.value); }} />
            </label>
            <p className="field-hint">{tr("onb.invite.hint", visitorLang())}</p>
          </>)}
        </>)}

        {mode === "code" && (<>
          <p className="muted">
            {tr("onb.verify.sent", visitorLang())} <b>{email}</b>{whereIsTheCode}.
            <b> {tr("onb.verify.click", visitorLang())}</b> {tr("onb.verify.type", visitorLang())}
          </p>
          {delivery === "console" && (window as unknown as { jimDesktop?: { openBackendLog?: () => void } }).jimDesktop?.openBackendLog && (
            <button className="linkish" onClick={() =>
              (window as unknown as { jimDesktop: { openBackendLog: () => void } }).jimDesktop.openBackendLog()
            }>{tr("onb.openlog", visitorLang())}</button>
          )}
          <label>{tr("onb.code", visitorLang())}
            <input value={code} inputMode="numeric" placeholder="123456" onChange={(e) => setCode(e.target.value)} />
          </label>
        </>)}

        {mode === "signin" && (<>
          <label>{tr("onb.email", visitorLang())}<input type="email" value={email} placeholder={tr("onb.email.ph", visitorLang())} onChange={(e) => setEmail(e.target.value)} /></label>
          <PasswordField label="Password" value={password} onChange={setPassword} />
        </>)}

        {mode === "reset" && (<>
          <p className="muted">{tr("onb.reset.hint", visitorLang())}{whereIsTheCode}.</p>
          <label>{tr("onb.email", visitorLang())}<input type="email" value={email} placeholder={tr("onb.email.ph", visitorLang())} onChange={(e) => setEmail(e.target.value)} /></label>
          <div className="actions" style={{ justifyContent: "center" }}>
            <button disabled={busy || !email.trim()} onClick={startReset}>{tr("onb.reset.send", visitorLang())}</button>
          </div>
          <label>{tr("onb.reset.code", visitorLang())}
            <input value={code} inputMode="numeric" placeholder="123456" onChange={(e) => setCode(e.target.value)} />
          </label>
          <PasswordField label="New password" value={password} placeholder={tr("onb.password.min", visitorLang())} onChange={setPassword} />
          <PasswordField label="Re-enter new password" value={confirm} placeholder={tr("onb.password.same", visitorLang())} onChange={setConfirm} />
          {confirm && !passwordsMatch && (
            <div className="error">{tr("onb.password.mismatch", visitorLang())}</div>
          )}
        </>)}

        {backendUp === false && (
          <div className="error">
            {tr("onb.unreachable", visitorLang())} <code>{getBase()}</code>.
            <p className="muted small" style={{ margin: "8px 0" }}>
              {tr("onb.localservice", visitorLang())} <code>{tr("onb.serve", visitorLang())}</code>{tr("onb.orpoint", visitorLang())}
            </p>
            <label>{tr("onb.backend", visitorLang())}<input value={base} onChange={(e) => setBaseInput(e.target.value)} /></label>
            <button onClick={saveBase}>{tr("onb.retry", visitorLang())}</button>
          </div>
        )}
        {error && <div className="error">⚠ {error}</div>}
        {notice && <div className="muted small">{notice}</div>}

        {mode === "signup" && (<>
          <button className="primary"
                  disabled={busy || !consent || !name.trim() || !birthdate || !email.trim()
                            || !password || !passwordsMatch || backendUp === false}
                  onClick={signup}>
            {busy ? "Creating…" : "Create account"}
          </button>
          {/* Starting without an email address.

              The backend has carried `POST /enroll` since the beginning — a
              name, a birthdate, a consent, and you are in. Every screen in
              front of it asked for an email and a password anyway, so the
              only way to reach it was a phone or a curl command.

              That is not a cosmetic gap. An email address is a thing a
              person might not have, might not control, or might share with
              somebody they are trying not to be watched by. A guardian
              product that makes one mandatory to begin has quietly decided
              who gets a guardian. This deployment's own backend never
              decided that; the console did, by omission.

              The trade is real and is stated rather than buried: no address
              means no way to recover the account, and the token below is
              the only key to it. */}
          <div className="muted small" style={{ marginTop: 12 }}>
            {tr("onb.noemail.why", visitorLang())}
          </div>
          <button disabled={busy || !consent || !name.trim() || !birthdate
                            || backendUp === false}
                  onClick={() => run(
                    () => api.enroll({ display_name: name.trim(), birthdate,
                                       terms_consent: consent }),
                    (u) => setSession({ userId: u.id, userToken: u.user_token,
                                        displayName: u.display_name }))}>
            {tr("onb.noemail", visitorLang())}
          </button>
        </>)}
        {mode === "code" && (<>
          <button className="primary" disabled={busy || code.trim().length !== 6} onClick={verify}>
            {busy ? "Checking…" : "Verify & get started"}
          </button>
          <button className="linkish" disabled={busy} onClick={resend}>{tr("onb.code.resend", visitorLang())}</button>
        </>)}
        {mode === "signin" && (<>
          <button className="primary"
                  disabled={busy || !email.trim() || !password || backendUp === false}
                  onClick={signin}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
          <button className="linkish" onClick={() => switchMode("reset")}>{tr("onb.forgot", visitorLang())}</button>
        </>)}
        {mode === "reset" && (<>
          <button className="primary"
                  disabled={busy || !email.trim() || code.trim().length !== 6
                            || !password || !passwordsMatch}
                  onClick={finishReset}>
            {busy ? "Resetting…" : "Set new password"}
          </button>
          <button className="linkish" onClick={() => switchMode("signin")}>{tr("onb.back", visitorLang())}</button>
        </>)}
        {/* The accessibility statement and its report door, before the
            account — the person it exists for may be the person this
            enrollment shut out. */}
        {onAccess && (
          <button className="linkish" onClick={onAccess}>
            {tr("acc.title", visitorLang())}
          </button>
        )}
      </div>
    </div>
  );
}
