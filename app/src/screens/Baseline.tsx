import { useEffect, useState } from "react";
import { api, type CrashWatchStatus } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

type Band = Awaited<ReturnType<typeof api.getBands>>["bands"][number];

// Your own normal, and how far from it counts.
//
// This is not the alarm layer — that watches for episodes and can call
// somebody. This watches for *drift from your own baseline*, in either
// direction, and produces a question. The edges only appear once the
// Guardian has learned enough resting samples to have a baseline worth
// drawing a line around; until then the screen says so rather than showing
// a threshold built on two readings.
export function Baseline() {
  const { session } = useSession();
  const lang = visitorLang();
  const [bands, setBands] = useState<Band[]>([]);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cw, setCw] = useState<CrashWatchStatus | null>(null);
  const [cwName, setCwName] = useState("");
  const [cwChannel, setCwChannel] = useState("");
  const [cwAttempts, setCwAttempts] = useState(3);
  const [cwWindow, setCwWindow] = useState(5);
  const [cwEms, setCwEms] = useState(false);

  function load() {
    if (!session.userId || !session.userToken) return;
    api.getBands(session.userId, session.userToken)
      .then((r) => setBands(r.bands))
      .catch((e) => setError((e as Error).message));
    api.crashWatch(session.userId, session.userToken)
      .then((st) => {
        setCw(st);
        if (st.trusted_name) setCwName(st.trusted_name);
        if (st.trusted_channel) setCwChannel(st.trusted_channel);
        if (st.attempts) setCwAttempts(st.attempts);
        if (st.window_minutes) setCwWindow(st.window_minutes);
        setCwEms(Boolean(st.contact_emergency_services));
      })
      .catch(() => setCw(null));
  }
  useEffect(load, [session.userId]);
  // The status read is also the clock: polling is what re-asks the question
  // when a deadline passes, so an open question stays live on screen.
  useEffect(() => {
    if (!cw?.asking) return;
    const t = setInterval(load, 20000);
    return () => clearInterval(t);
  }, [cw?.asking]);

  async function armCrashWatch() {
    if (!session.userId || !session.userToken) return;
    setBusy("crashwatch"); setError(null);
    try {
      setCw(await api.armCrashWatch(session.userId, {
        trusted_name: cwName, trusted_channel: cwChannel,
        attempts: cwAttempts, window_minutes: cwWindow,
        contact_emergency_services: cwEms,
      }, session.userToken));
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(null); }
  }

  async function disarmCrashWatch() {
    if (!session.userId || !session.userToken) return;
    setBusy("crashwatch");
    try { setCw(await api.disarmCrashWatch(session.userId, session.userToken)); }
    finally { setBusy(null); }
  }

  async function imOkay() {
    if (!session.userId || !session.userToken) return;
    setCw(await api.imOkay(session.userId, session.userToken));
  }

  async function change(metric: string, body: Parameters<typeof api.setBand>[2]) {
    if (!session.userId || !session.userToken) return;
    setBusy(metric); setError(null);
    try {
      await api.setBand(session.userId, metric, body, session.userToken);
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(null); }
  }

  async function reset(metric: string) {
    if (!session.userId || !session.userToken) return;
    setBusy(metric);
    try { await api.resetBand(session.userId, metric, session.userToken); load(); }
    finally { setBusy(null); }
  }

  const established = bands.filter((b) => !b.provisional).length;

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("bas.title", lang)}</h2>
        <span className="muted small">
          {established
            ? `${established} of ${bands.length} learned`
            : "learning — wear the watch and sleep in it"}
        </span>
      </header>

      <div className="card">
        <h3>{tr("bas.what", lang)}</h3>
        <p className="muted small">{tr("bas.what.p1", lang)}</p>
        <p className="muted small">{tr("bas.what.p2", lang)}</p>
      </div>

      {error && <div className="error">⚠ {error}</div>}

      {cw?.asking && (
        <div className="card" style={{ borderColor: "#ffb84d" }}>
          <h3>{tr("bas.ask.title", lang)}</h3>
          <p className="muted small">
            {tr("bas.ask.body", lang)
              .replace("{concern}", String(cw.concern ?? ""))
              .replace("{attempt}", String(cw.attempt))
              .replace("{attempts}", String(cw.attempts))
              .replace("{name}", String(cw.trusted_name ?? ""))
              .replace("{ems}", cw.contact_emergency_services
                ? " and requests emergency services" : "")}
          </p>
          <button className="primary" onClick={imOkay}>{tr("bas.ask.ok", lang)}</button>
        </div>
      )}
      {cw?.tripped && (
        <div className="error">
          {tr("bas.trip", lang)
            .replace("{name}", String(cw.trusted_name ?? ""))
            .replace("{ems}", cw.contact_emergency_services
              ? " and an emergency-services dispatch was requested" : "")}
        </div>
      )}

      <div className="card">
        <h3>{tr("bas.cw.title", lang)}</h3>
        <p className="muted small">
          {tr("bas.cw.lead", lang)
            .replace("{n}", String(cwAttempts))
            .replace("{m}", (cwAttempts * cwWindow).toFixed(0))
            .replace("{ems}", cwEms ? " and requests emergency services" : "")}
        </p>
        <label>{tr("bas.cw.name", lang)}
          <input value={cwName} onChange={(e) => setCwName(e.target.value)}
                 placeholder={tr("bas.cw.name.ph", lang)} /></label>
        <label>{tr("bas.cw.channel", lang)}
          <input value={cwChannel} onChange={(e) => setCwChannel(e.target.value)}
                 placeholder={tr("bas.cw.channel.ph", lang)} /></label>
        <div className="voice-row">
          <label>{tr("bas.cw.attempts", lang)}
            <input type="number" min={1} max={10} value={cwAttempts}
                   onChange={(e) => setCwAttempts(Number(e.target.value))} /></label>
          <label>{tr("bas.cw.window", lang)}
            <input type="number" min={1} max={60} value={cwWindow}
                   onChange={(e) => setCwWindow(Number(e.target.value))} /></label>
        </div>
        <label className="check">
          <input type="checkbox" checked={cwEms}
                 onChange={(e) => setCwEms(e.target.checked)} />
          {tr("bas.cw.ems", lang)}
        </label>
        <div className="voice-row">
          <button className="primary" disabled={busy === "crashwatch"}
                  onClick={armCrashWatch}>
            {cw?.armed ? "Update the crash watch" : "Arm the crash watch"}
          </button>
          {cw?.armed && (
            <button disabled={busy === "crashwatch"} onClick={disarmCrashWatch}>
              {tr("bas.cw.disarm", lang)}
            </button>
          )}
        </div>
        {cw?.armed && !cw.asking && !cw.tripped && (
          <p className="muted small">
            {tr("bas.cw.armed", lang)
              .replace("{name}", String(cw.trusted_name ?? ""))
              .replace("{n}", String(cw.attempts))}
          </p>
        )}
      </div>

      <div className="card">
        <h3>{tr("bas.metrics", lang)}</h3>
        {bands.length === 0 && <div className="muted small">{tr("bas.metrics.none", lang)}</div>}
        {bands.map((b) => (
          <div key={b.metric} style={{ padding: "12px 0", borderBottom: "1px solid var(--line)" }}>
            <div className="band-row">
              <div>
                <div className="band-name">{b.label}</div>
                <div className="band-figures">
                  {b.provisional ? (
                    <>{tr("bas.metrics.learning", lang)
                      .replace("{n}", String(b.samples))
                      .replace("{s}", b.samples === 1 ? "" : "s")}</>
                  ) : (
                    <>{tr("bas.metrics.usual", lang)
                      .replace("{v}", `${b.baseline}${b.unit}`)
                      .replace("{lo}", `${b.low_edge}${b.unit}`)
                      .replace("{hi}", `${b.high_edge}${b.unit}`)}</>
                  )}
                </div>
              </div>
              <div className="muted small">
                ±{b.margin}{b.unit}{b.source === "user" ? " (yours)" : ""}
              </div>
            </div>

            {!b.provisional && (
              <div className="band-scale">
                <div className="band-inner" style={{ left: "25%", right: "25%" }} />
              </div>
            )}

            <div className="voice-row">
              <input type="range" min={0.1} max={b.unit === "°C" ? 2 : 30}
                     step={b.unit === "°C" ? 0.1 : 0.5}
                     value={b.margin} disabled={busy === b.metric}
                     onChange={(e) => change(b.metric, { margin: Number(e.target.value) })} />
              <label className="check">
                <input type="checkbox" checked={b.watch_low} disabled={busy === b.metric}
                       onChange={(e) => change(b.metric, { watch_low: e.target.checked })} />
                {tr("bas.metrics.drop", lang)}
              </label>
              <label className="check">
                <input type="checkbox" checked={b.watch_high} disabled={busy === b.metric}
                       onChange={(e) => change(b.metric, { watch_high: e.target.checked })} />
                {tr("bas.metrics.climb", lang)}
              </label>
              {b.source === "user" && (
                <button onClick={() => reset(b.metric)} disabled={busy === b.metric}>
                  {tr("bas.metrics.reset", lang)}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
