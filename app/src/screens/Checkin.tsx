import { useState } from "react";
import { api, type CheckinResult } from "../api";
import { useSession } from "../store";

export function Checkin() {
  const { session } = useSession();
  const [mood, setMood] = useState(4);
  const [energy, setEnergy] = useState(3);
  const [note, setNote] = useState("");
  const [result, setResult] = useState<CheckinResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function save() {
    if (!session.userId || !session.userToken) return;
    setBusy(true); setError(null);
    try { setResult(await api.checkin(session.userId, { mood, energy, note }, session.userToken)); }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Check-in</h2>
        <span className="muted small">mood &amp; energy · a worrying note runs the crisis check</span>
      </header>
      <div className="card">
        <label>Mood: <b className="green">{mood}</b> / 5
          <input type="range" min="1" max="5" value={mood} onChange={(e) => setMood(+e.target.value)} /></label>
        <label>Energy: <b className="amber">{energy}</b> / 5
          <input type="range" min="1" max="5" value={energy} onChange={(e) => setEnergy(+e.target.value)} /></label>
        <label>Note (optional)<textarea rows={2} value={note} onChange={(e) => setNote(e.target.value)} /></label>
        <button className="primary" onClick={save} disabled={busy}>{busy ? "Saving…" : "Save check-in"}</button>
        {error && <div className="error">⚠ {error}</div>}
      </div>
      {result && (
        <div className="card">
          <h3>Logged</h3>
          <div className="muted small">mood {result.mood} · energy {result.energy}</div>
          {result.guardian?.detected ? (
            <div className="detect hit" style={{ marginTop: 10 }}>
              <div className="detect-head"><span className="tag warn">guardian</span> flagged</div>
              {result.guardian.guidance?.content && <p>{result.guardian.guidance.content}</p>}
            </div>
          ) : <div className="ok-note" style={{ marginTop: 10 }}>No concern detected — logged to your day.</div>}
        </div>
      )}
    </div>
  );
}
