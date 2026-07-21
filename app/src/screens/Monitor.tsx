import { useState } from "react";
import { api, type MonitorResult } from "../api";
import { useSession } from "../store";

export function Monitor() {
  const { session } = useSession();
  const [hr, setHr] = useState(110);
  const [resp, setResp] = useState(22);
  const [stress, setStress] = useState(0.8);
  const [result, setResult] = useState<MonitorResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    if (!session.userId || !session.userToken) return;
    setBusy(true); setError(null);
    try {
      setResult(await api.monitor(session.userId, { heart_rate: hr, respiration: resp, stress_level: stress }, session.userToken));
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Live Monitoring</h2>
        <span className="muted small">detect → guide → escalate</span>
      </header>

      <div className="card">
        <h3>Submit a biometric sample</h3>
        <div className="row">
          <label>Heart rate (bpm)<input type="number" value={hr} onChange={(e) => setHr(+e.target.value)} /></label>
          <label>Respiration (/min)<input type="number" value={resp} onChange={(e) => setResp(+e.target.value)} /></label>
        </div>
        <label>Stress (0–1)<input type="number" step="0.1" min="0" max="1" value={stress} onChange={(e) => setStress(+e.target.value)} /></label>
        <button className="primary" onClick={submit} disabled={busy}>{busy ? "Analyzing…" : "Send to Guardian"}</button>
        {error && <div className="error">⚠ {error}</div>}
      </div>

      {result && (
        <div className={"card detect " + (result.detected ? "hit" : "calm")}>
          <div className="detect-head">
            {result.detected
              ? <><span className="tag warn">{result.severity}</span> {result.condition}</>
              : <span className="tag ok">all calm</span>}
          </div>
          {result.reason && <div className="muted small">{result.reason}</div>}
          {result.guidance?.content && (
            <div className="guidance">
              <div className="guidance-src">{result.guidance.source} guidance</div>
              <p>{result.guidance.content}</p>
              {result.guidance.references?.length ? (
                <ul className="refs">{result.guidance.references.map((r, i) => <li key={i}>{r}</li>)}</ul>
              ) : null}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
