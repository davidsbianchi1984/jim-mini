import { useEffect, useState } from "react";
import { api, getBase, setBase } from "../api";
import { useSession } from "../store";

export function Onboarding() {
  const { setSession } = useSession();
  // No pre-filled identity. A name sitting in the box is the one most people
  // never change, and a wrong birthdate in an age-verification field is worse
  // than an empty one — the user is the only source for either.
  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // The desktop shell is only the console; the Guardian itself is the local
  // backend. Check for it up front so "Get Started" never turns a missing
  // backend into a cryptic fetch error after the form is filled in.
  const [backendUp, setBackendUp] = useState<boolean | null>(null);
  const [base, setBaseInput] = useState(getBase());

  async function checkBackend() {
    setBackendUp(null);
    try {
      await api.health();
      setBackendUp(true);
    } catch {
      setBackendUp(false);
    }
  }
  useEffect(() => { checkBackend(); }, []);

  function saveBase() {
    setBase(base);
    checkBackend();
  }

  async function enroll() {
    setBusy(true); setError(null);
    try {
      const u = await api.enroll({ display_name: name.trim(), birthdate, terms_consent: consent });
      setSession({ userId: u.id, userToken: u.user_token, displayName: u.display_name });
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  return (
    <div className="onboarding">
      <div className="onboard-card">
        <div className="orb big" />
        <h1>Your Guardian, always here</h1>
        <p className="muted">Monitor, predict, guide, escalate — grounded in your baseline, on your device.</p>
        <label>Name<input value={name} placeholder="Your name" onChange={(e) => setName(e.target.value)} /></label>
        <label>Birthdate<input type="date" value={birthdate} onChange={(e) => setBirthdate(e.target.value)} /></label>
        <label className="check">
          <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
          I consent to the terms of use
        </label>
        {backendUp === false && (
          <div className="error">
            ⚠ The Guardian backend isn't reachable at <code>{getBase()}</code>.
            <p className="muted small" style={{ margin: "8px 0" }}>
              This window is only the console — the Guardian runs as a local
              service. Start it with <code>python -m jim</code> (or{" "}
              <code>JIM_CORS_ORIGINS=* uvicorn jim.api:app</code>), or point
              this console at a machine already running one:
            </p>
            <label>Backend URL<input value={base} onChange={(e) => setBaseInput(e.target.value)} /></label>
            <button onClick={saveBase}>Save &amp; retry</button>
          </div>
        )}
        {error && <div className="error">⚠ {error}</div>}
        <button
          className="primary"
          disabled={busy || !consent || !name.trim() || !birthdate || backendUp === false}
          onClick={enroll}
        >
          {busy ? "Enrolling…" : "Get Started"}
        </button>
      </div>
    </div>
  );
}
