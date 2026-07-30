import { useState } from "react";
import { api, type FollowupResult, type MonitorResult } from "../api";
import { PaceCue } from "../PaceCue";
import { useSession } from "../store";

export function Monitor() {
  const { session } = useSession();
  const [hr, setHr] = useState(110);
  const [resp, setResp] = useState(22);
  const [stress, setStress] = useState(0.8);
  const [result, setResult] = useState<MonitorResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<FollowupResult | null>(null);
  const [asking, setAsking] = useState(false);

  async function submit() {
    if (!session.userId || !session.userToken) return;
    setBusy(true); setError(null); setAnswer(null);
    try {
      setResult(await api.monitor(session.userId, { heart_rate: hr, respiration: resp, stress_level: stress }, session.userToken));
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  // Spec [0039]: "did that help?" — and if it didn't, a live person.
  async function say(helped: boolean) {
    if (!session.userId || !session.userToken) return;
    setAsking(true); setError(null);
    try {
      setAnswer(await api.answerFollowup(session.userId, { helped }, session.userToken));
    } catch (e) { setError((e as Error).message); } finally { setAsking(false); }
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
          {result.drift?.crossings?.length ? (
            <div className="guidance">
              <div className="guidance-src">drift from your baseline — a check-in, not an alarm</div>
              <p>{result.drift.question}</p>
              <ul className="refs">
                {result.drift.crossings.map((c) => (
                  <li key={c.metric}>
                    {c.label}: <b>{c.value}{c.unit}</b> — {c.direction} your usual{" "}
                    {c.baseline}{c.unit} (edge {c.edge}{c.unit})
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {result.guidance?.content && (
            <div className="guidance">
              <div className="guidance-src">{result.guidance.source} guidance</div>
              <p>{result.guidance.content}</p>
              {result.guidance.first_aid && (
                <div className="first-aid">
                  <b>{result.guidance.first_aid.title || "First aid, step by step"}</b>
                  <ol className="refs">
                    {result.guidance.first_aid.steps.map((s, i) => <li key={i}>{s}</li>)}
                  </ol>
                  <PaceCue aid={result.guidance.first_aid} />
                </div>
              )}
              {result.guidance.references?.length ? (
                <ul className="refs">{result.guidance.references.map((r, i) => <li key={i}>{r}</li>)}</ul>
              ) : null}
              {/* Spec [0039]: the loop's closing edge. Guidance that didn't
                  land reaches a person instead of repeating itself. */}
              {result.followup && !answer && (
                <div className="followup">
                  <b>{result.followup.question}</b>
                  <div className="followup-buttons">
                    <button onClick={() => say(true)} disabled={asking}>Yes, that helped</button>
                    <button className="warn" onClick={() => say(false)} disabled={asking}>
                      No, it didn't
                    </button>
                  </div>
                </div>
              )}
              {answer?.helped && (
                <div className="followup"><span className="muted small">
                  Noted — monitoring resumes, and the Guardian remembers that
                  this worked for you.
                </span></div>
              )}
              {answer && answer.helped === false && answer.live_assistance && (
                <div className="followup">
                  <b>Reaching a person</b>
                  <div className="muted small">
                    escalated to {answer.escalation_decision?.tier.replace(/_/g, " ")}
                  </div>
                  <ul className="refs">
                    {answer.live_assistance.options.map((o, i) => (
                      <li key={i}>
                        {o.name}{o.channel ? ` — ${o.channel}` : ""}
                        {o.note ? <span className="muted small"> ({o.note})</span> : null}
                      </li>
                    ))}
                  </ul>
                  <div className="muted small">{answer.live_assistance.note}</div>
                </div>
              )}
            </div>
          )}
          {(result.escalation as { companion?: { relaying?: { note?: string } } } | null)?.companion && (
            <div className="guidance">
              <div className="guidance-src">companion, in the background</div>
              <p>
                Relaying a dispatcher briefing — who you are, your known
                conditions and critical medications, the latest readings, and
                what's being done — through every configured channel, updated
                with each new reading.{" "}
                <span className="muted small">
                  {(result.escalation as { companion: { relaying: { note: string } } }).companion.relaying.note}
                </span>
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
