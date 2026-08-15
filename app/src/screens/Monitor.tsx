import { useState } from "react";
import { api, type FollowupResult, type MonitorResult } from "../api";
import { PaceCue } from "../PaceCue";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

export function Monitor() {
  const { session } = useSession();
  const lang = visitorLang();
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
      setResult(await api.monitor(session.userId, { heart_rate: hr, respiratory_rate: resp, stress_level: stress }, session.userToken));
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
        <h2>{tr("mon.title", lang)}</h2>
        <span className="muted small">{tr("mon.sub", lang)}</span>
      </header>

      <div className="card">
        <h3>{tr("mon.submit", lang)}</h3>
        <div className="row">
          <label>{tr("mon.hr", lang)}<input type="number" value={hr} onChange={(e) => setHr(+e.target.value)} /></label>
          <label>{tr("mon.resp", lang)}<input type="number" value={resp} onChange={(e) => setResp(+e.target.value)} /></label>
        </div>
        <label>{tr("mon.stress", lang)}<input type="number" step="0.1" min="0" max="1" value={stress} onChange={(e) => setStress(+e.target.value)} /></label>
        <button className="primary" onClick={submit} disabled={busy}>{busy ? tr("mon.analyzing", lang) : tr("mon.send", lang)}</button>
        {error && <div className="error">⚠ {error}</div>}
      </div>

      {result && (
        <div className={"card detect " + (result.detected ? "hit" : "calm")}>
          <div className="detect-head">
            {result.detected
              ? <><span className="tag warn">{result.severity}</span> {result.condition}</>
              : <span className="tag ok">{tr("mon.calm", lang)}</span>}
          </div>
          {result.reason && <div className="muted small">{result.reason}</div>}
          {result.drift?.crossings?.length ? (
            <div className="guidance">
              <div className="guidance-src">{tr("mon.drift", lang)}</div>
              <p>{result.drift.question}</p>
              <ul className="refs">
                {result.drift.crossings.map((c) => (
                  <li key={c.metric}>
                    {tr("mon.reading", lang)
                      .replace("{label}", String(c.label))
                      .replace("{value}{unit}", `${c.value}${c.unit}`)
                      .replace("{direction}", String(c.direction))
                      .replace("{baseline}{unit}", `${c.baseline}${c.unit}`)
                      .replace("{edge}{unit}", `${c.edge}${c.unit}`)}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {result.guidance?.content && (
            <div className="guidance">
              <div className="guidance-src">{tr("mon.guidance", lang)
                .replace("{source}", String(result.guidance.source))}</div>
              <p>{result.guidance.content}</p>
              {result.guidance.first_aid && (
                <div className="first-aid">
                  <b>{result.guidance.first_aid.title || tr("mon.firstaid", lang)}</b>
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
                    <button onClick={() => say(true)} disabled={asking}>{tr("mon.helped", lang)}</button>
                    <button className="warn" onClick={() => say(false)} disabled={asking}>
                      {tr("mon.nothelped", lang)}
                    </button>
                  </div>
                </div>
              )}
              {answer?.helped && (
                <div className="followup"><span className="muted small">
                  {tr("mon.noted", lang)}
                </span></div>
              )}
              {answer && answer.helped === false && answer.live_assistance && (
                <div className="followup">
                  <b>{tr("mon.reaching", lang)}</b>
                  <div className="muted small">
                    {tr("mon.escalated", lang).replace("{tier}",
                      String(answer.escalation_decision?.tier.replace(/_/g, " ")))}
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
              <div className="guidance-src">{tr("mon.companion", lang)}</div>
              <p>
                {tr("mon.relaying", lang)}{" "}
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
