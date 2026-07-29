import { useEffect, useState } from "react";
import { api, type CrashWatchStatus } from "../api";
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
        <h2>Your baseline</h2>
        <span className="muted small">
          {established
            ? `${established} of ${bands.length} learned`
            : "learning — wear the watch and sleep in it"}
        </span>
      </header>

      <div className="card">
        <h3>What this is</h3>
        <p className="muted small">
          Every resting reading nudges your own average for each metric. Once
          a metric has enough of them, a <b>band</b> is drawn around it — and
          when a reading lands outside that band, in <b>either direction</b>,
          your Guardian checks in and asks how you are. A drift check-in on
          its own never calls anybody — but the <b>crash watch</b> below is
          exactly the "call somebody" you can program: if a reading turns
          critical and you stop answering, help gets sent.
        </p>
        <p className="muted small">
          The widths below are yours to set. Narrow one to be told sooner;
          widen it if a metric of yours naturally wanders.
        </p>
      </div>

      {error && <div className="error">⚠ {error}</div>}

      {cw?.asking && (
        <div className="card" style={{ borderColor: "#ffb84d" }}>
          <h3>JIM is asking: are you okay?</h3>
          <p className="muted small">
            A concerning reading came in ({cw.concern}). This is attempt{" "}
            {cw.attempt} of {cw.attempts} — after that, your crash watch
            contacts {cw.trusted_name}
            {cw.contact_emergency_services ? " and requests emergency services" : ""}.
          </p>
          <button className="primary" onClick={imOkay}>I'm okay</button>
        </div>
      )}
      {cw?.tripped && (
        <div className="error">
          ⚠ The crash watch tripped: {cw.trusted_name} was contacted
          {cw.contact_emergency_services ? " and an emergency-services dispatch was requested" : ""}.
          Any normal reading — or the button above — stands it down.
        </div>
      )}

      <div className="card">
        <h3>Crash watch — if you stop answering, help gets sent</h3>
        <p className="muted small">
          Off by default, programmed by you: when a reading turns{" "}
          <b>critical</b> (a collapsing pulse, oxygen falling) JIM asks{" "}
          "are you okay?" — and if {cwAttempts} attempts over{" "}
          {(cwAttempts * cwWindow).toFixed(0)} minutes all go unanswered, it
          contacts your trusted person{cwEms ? " and requests emergency services" : ""}.
          Any sign of you — the button, a normal reading — calls it off.
          Drift check-ins stay calm and never trigger this.
        </p>
        <label>Trusted person
          <input value={cwName} onChange={(e) => setCwName(e.target.value)}
                 placeholder="Rosa" /></label>
        <label>How to reach them (email or phone)
          <input value={cwChannel} onChange={(e) => setCwChannel(e.target.value)}
                 placeholder="rosa@example.com" /></label>
        <div className="voice-row">
          <label>Attempts
            <input type="number" min={1} max={10} value={cwAttempts}
                   onChange={(e) => setCwAttempts(Number(e.target.value))} /></label>
          <label>Minutes per attempt
            <input type="number" min={1} max={60} value={cwWindow}
                   onChange={(e) => setCwWindow(Number(e.target.value))} /></label>
        </div>
        <label className="check">
          <input type="checkbox" checked={cwEms}
                 onChange={(e) => setCwEms(e.target.checked)} />
          May request emergency services (this app relays the request to
          every connected system — it cannot itself place a call)
        </label>
        <div className="voice-row">
          <button className="primary" disabled={busy === "crashwatch"}
                  onClick={armCrashWatch}>
            {cw?.armed ? "Update the crash watch" : "Arm the crash watch"}
          </button>
          {cw?.armed && (
            <button disabled={busy === "crashwatch"} onClick={disarmCrashWatch}>
              Disarm
            </button>
          )}
        </div>
        {cw?.armed && !cw.asking && !cw.tripped && (
          <p className="muted small">
            Armed — {cw.trusted_name} will be contacted after{" "}
            {cw.attempts} unanswered attempts.
          </p>
        )}
      </div>

      <div className="card">
        <h3>Your metrics</h3>
        {bands.length === 0 && <div className="muted small">Nothing yet.</div>}
        {bands.map((b) => (
          <div key={b.metric} style={{ padding: "12px 0", borderBottom: "1px solid var(--line)" }}>
            <div className="band-row">
              <div>
                <div className="band-name">{b.label}</div>
                <div className="band-figures">
                  {b.provisional ? (
                    <>learning — {b.samples} resting reading{b.samples === 1 ? "" : "s"} so far</>
                  ) : (
                    <>your usual <b>{b.baseline}{b.unit}</b>, checked in below{" "}
                      <b>{b.low_edge}{b.unit}</b> or above <b>{b.high_edge}{b.unit}</b></>
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
                tell me when it drops
              </label>
              <label className="check">
                <input type="checkbox" checked={b.watch_high} disabled={busy === b.metric}
                       onChange={(e) => change(b.metric, { watch_high: e.target.checked })} />
                tell me when it climbs
              </label>
              {b.source === "user" && (
                <button onClick={() => reset(b.metric)} disabled={busy === b.metric}>
                  Reset
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
