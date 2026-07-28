import { useEffect, useState } from "react";
import { api, getBase, setBase } from "../api";
import { useSession } from "../store";

type Mode = "signup" | "code" | "signin" | "reset";

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

export function Onboarding() {
  const { setSession } = useSession();
  const [mode, setMode] = useState<Mode>("signup");
  // No pre-filled identity. A name sitting in the box is the one most people
  // never change, and a wrong birthdate in an age-verification field is worse
  // than an empty one — the user is the only source for either.
  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [consent, setConsent] = useState(false);
  const [code, setCode] = useState("");
  const [delivery, setDelivery] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

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

  const signup = () => run(
    () => api.signup({ email: email.trim(), password, display_name: name.trim(), birthdate, terms_consent: consent }),
    (r) => { setDelivery(r.code_delivery); setMode("code"); },
  );
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

  const whereIsTheCode = delivery === "console"
    ? <> — this deployment has no mail service configured, so the code was <b>printed in the terminal running the backend</b></>
    : null;

  return (
    <div className="onboarding">
      <div className="onboard-card">
        <div className="orb big" />
        <h1>Your Guardian, always here</h1>
        <p className="muted">Monitor, predict, guide, escalate — grounded in your baseline, on your device.</p>

        {(mode === "signup" || mode === "signin") && (
          <div className="tabs">
            <button className={mode === "signup" ? "tab active" : "tab"}
                    onClick={() => switchMode("signup")}>Create account</button>
            <button className={mode === "signin" ? "tab active" : "tab"}
                    onClick={() => switchMode("signin")}>Sign in</button>
          </div>
        )}

        {mode === "signup" && (<>
          <label>Name<input value={name} placeholder="Your name" onChange={(e) => setName(e.target.value)} /></label>
          <label>Birthdate<input type="date" value={birthdate} onChange={(e) => setBirthdate(e.target.value)} /></label>
          <label>Email<input type="email" value={email} placeholder="you@example.com" onChange={(e) => setEmail(e.target.value)} /></label>
          <PasswordField label="Password" value={password} placeholder="At least 8 characters" onChange={setPassword} />
          <p className="field-hint">At least 8 characters.</p>
          {/* Typed twice on purpose: hidden characters are how a typo gets
              remembered wrong with total confidence. The match check is
              instant, before anything is submitted. */}
          <PasswordField label="Re-enter password" value={confirm} placeholder="Same password again" onChange={setConfirm} />
          {confirm && !passwordsMatch && (
            <div className="error">⚠ The passwords don't match yet.</div>
          )}
          <label className="check">
            <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
            I consent to the terms of use
          </label>
        </>)}

        {mode === "code" && (<>
          <p className="muted">
            We sent a 6-digit code to <b>{email}</b>{whereIsTheCode}.
            Enter it to prove the address is yours; your account exists only after that.
          </p>
          <label>Verification code
            <input value={code} inputMode="numeric" placeholder="123456" onChange={(e) => setCode(e.target.value)} />
          </label>
        </>)}

        {mode === "signin" && (<>
          <label>Email<input type="email" value={email} placeholder="you@example.com" onChange={(e) => setEmail(e.target.value)} /></label>
          <PasswordField label="Password" value={password} onChange={setPassword} />
        </>)}

        {mode === "reset" && (<>
          <p className="muted">Enter your account's email; we'll send a 6-digit reset code{whereIsTheCode}.</p>
          <label>Email<input type="email" value={email} placeholder="you@example.com" onChange={(e) => setEmail(e.target.value)} /></label>
          <div className="actions" style={{ justifyContent: "center" }}>
            <button disabled={busy || !email.trim()} onClick={startReset}>Send reset code</button>
          </div>
          <label>Reset code
            <input value={code} inputMode="numeric" placeholder="123456" onChange={(e) => setCode(e.target.value)} />
          </label>
          <PasswordField label="New password" value={password} placeholder="At least 8 characters" onChange={setPassword} />
          <PasswordField label="Re-enter new password" value={confirm} placeholder="Same password again" onChange={setConfirm} />
          {confirm && !passwordsMatch && (
            <div className="error">⚠ The passwords don't match yet.</div>
          )}
        </>)}

        {backendUp === false && (
          <div className="error">
            ⚠ The Guardian backend isn't reachable at <code>{getBase()}</code>.
            <p className="muted small" style={{ margin: "8px 0" }}>
              This window is only the console — the Guardian runs as a local
              service. Start it with <code>python -m jim serve</code>, or point
              this console at a machine already running one:
            </p>
            <label>Backend URL<input value={base} onChange={(e) => setBaseInput(e.target.value)} /></label>
            <button onClick={saveBase}>Save &amp; retry</button>
          </div>
        )}
        {error && <div className="error">⚠ {error}</div>}
        {notice && <div className="muted small">{notice}</div>}

        {mode === "signup" && (
          <button className="primary"
                  disabled={busy || !consent || !name.trim() || !birthdate || !email.trim()
                            || !password || !passwordsMatch || backendUp === false}
                  onClick={signup}>
            {busy ? "Creating…" : "Create account"}
          </button>
        )}
        {mode === "code" && (<>
          <button className="primary" disabled={busy || code.trim().length !== 6} onClick={verify}>
            {busy ? "Checking…" : "Verify & get started"}
          </button>
          <button className="linkish" disabled={busy} onClick={resend}>Resend code</button>
        </>)}
        {mode === "signin" && (<>
          <button className="primary"
                  disabled={busy || !email.trim() || !password || backendUp === false}
                  onClick={signin}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
          <button className="linkish" onClick={() => switchMode("reset")}>Forgot password?</button>
        </>)}
        {mode === "reset" && (<>
          <button className="primary"
                  disabled={busy || !email.trim() || code.trim().length !== 6
                            || !password || !passwordsMatch}
                  onClick={finishReset}>
            {busy ? "Resetting…" : "Set new password"}
          </button>
          <button className="linkish" onClick={() => switchMode("signin")}>Back to sign in</button>
        </>)}
      </div>
    </div>
  );
}
