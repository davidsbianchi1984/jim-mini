import { useState } from "react";
import { api } from "../api";
import { useSession } from "../store";

export function Onboarding() {
  const { setSession } = useSession();
  const [name, setName] = useState("David");
  const [birthdate, setBirthdate] = useState("1984-06-01");
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
        <label>Name<input value={name} onChange={(e) => setName(e.target.value)} /></label>
        <label>Birthdate<input type="date" value={birthdate} onChange={(e) => setBirthdate(e.target.value)} /></label>
        <label className="check">
          <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
          I consent to the terms of use
        </label>
        {error && <div className="error">⚠ {error}</div>}
        <button className="primary" disabled={busy || !consent} onClick={enroll}>
          {busy ? "Enrolling…" : "Get Started"}
        </button>
        <p className="hint">Start the backend: <code>JIM_CORS_ORIGINS=* uvicorn jim.api:app</code></p>
      </div>
    </div>
  );
}
