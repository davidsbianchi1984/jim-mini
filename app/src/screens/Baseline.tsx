import { useEffect, useState } from "react";
import { api, type CrashWatchStatus, type MoneyView,
         type VigilStatus } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

type Band = Awaited<ReturnType<typeof api.getBands>>["bands"][number];

// Your own normal, and how far from it counts — and, since the round-up,
// every other line the Guardian draws around this person: how readily it
// speaks up, how long a silence trips the vigil, where the money guardian
// calls cash low. The reviewer's call: limits live in one place, not
// scattered a screen each across the menus.
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
  const [sens, setSens] = useState<string>("balanced");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cw, setCw] = useState<CrashWatchStatus | null>(null);
  const [cwName, setCwName] = useState("");
  const [cwChannel, setCwChannel] = useState("");
  const [cwAttempts, setCwAttempts] = useState(3);
  const [cwWindow, setCwWindow] = useState(5);
  const [cwEms, setCwEms] = useState(false);
  const [money, setMoney] = useState<MoneyView | null>(null);

  function load() {
    if (!session.userId || !session.userToken) return;
    api.getBands(session.userId, session.userToken)
      .then((r) => { setBands(r.bands); setSens(r.sensitivity); })
      .catch((e) => setError((e as Error).message));
    api.moneyView(session.userId, session.userToken)
      .then(setMoney)
      .catch(() => setMoney(null));
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

  async function pickSensitivity(level: string) {
    if (!session.userId || !session.userToken) return;
    setBusy("sensitivity"); setError(null);
    try {
      await api.setSensitivity(session.userId, { level }, session.userToken);
      setSens(level);
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(null); }
  }

  async function setFloor(floor: number | null) {
    if (!session.userId || !session.userToken) return;
    setBusy("floor"); setError(null);
    try {
      await api.moneySetFloor(session.userId, { floor }, session.userToken);
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(null); }
  }

  async function setGoal(goal: number) {
    if (!session.userId || !session.userToken) return;
    setBusy("goal"); setError(null);
    try {
      await api.moneySetSavings(session.userId, { goal }, session.userToken);
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(null); }
  }

  async function setCap(field: "cap_per_order" | "monthly_cap", value: number) {
    // A cap slider edits the standing mandate in place; everything else
    // about the handover — scope, asset classes, the enable itself — is
    // resent exactly as it stands, because a limit change is not a new
    // grant of permission.
    if (!session.userId || !session.userToken || !money?.mandate) return;
    setBusy(field); setError(null);
    try {
      await api.moneySetMandate(session.userId, {
        enabled: money.mandate.enabled,
        cap_per_order: field === "cap_per_order"
          ? value : money.mandate.cap_per_order,
        monthly_cap: field === "monthly_cap"
          ? value : money.mandate.monthly_cap,
        asset_classes: money.mandate.asset_classes,
        scope: money.mandate.scope,
      }, session.userToken);
      load();
    } catch (e) { setError((e as Error).message); }
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
            : tr("bas.learning", lang)}
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
            {cw?.armed ? tr("bas.watch.update", lang)
                       : tr("bas.watch.arm", lang)}
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

      <VigilPanel />

      <div className="card">
        <h3>{tr("bas.sens.title", lang)}</h3>
        <p className="muted small">{tr("bas.sens.lead", lang)}</p>
        <div className="voice-row">
          {(["cautious", "balanced", "assertive"] as const).map((s) => (
            <button key={s} disabled={busy === "sensitivity"}
                    className={sens === s ? "primary" : ""}
                    onClick={() => pickSensitivity(s)}>
              {tr(`w.sens.${s}`, lang)}
            </button>
          ))}
        </div>
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
                ±{b.margin}{b.unit}{b.source === "user" ? tr("bas.band.yours", lang) : ""}
              </div>
            </div>

            {!b.provisional && (
              <div className="band-scale">
                <div className="band-inner" style={{ left: "25%", right: "25%" }} />
              </div>
            )}

            <div className="voice-row">
              {/* Bounds come with the band — the metric knows its own
                  scale, and the screen stopped guessing it from the unit. */}
              <input type="range" min={b.slider_min} max={b.slider_max}
                     step={b.slider_step}
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

      {money && (
        <div className="card">
          <h3>{tr("bas.money.title", lang)}</h3>
          <p className="muted small">{tr("bas.money.lead", lang)}</p>

          <div className="band-row">
            <div>
              <div className="band-name">{tr("bas.money.floor", lang)}</div>
              <div className="band-figures">{tr("bas.money.floor.note", lang)}</div>
            </div>
            <div className="muted small">
              {money.floor.floor}
              {money.floor.source === "user" ? tr("bas.band.yours", lang) : ""}
            </div>
          </div>
          <div className="voice-row">
            <input type="range" min={25} max={2000} step={25}
                   value={money.floor.floor} disabled={busy === "floor"}
                   onChange={(e) => setFloor(Number(e.target.value))} />
            {money.floor.source === "user" && (
              <button onClick={() => setFloor(null)} disabled={busy === "floor"}>
                {tr("bas.metrics.reset", lang)}
              </button>
            )}
          </div>

          <div className="band-row">
            <div>
              <div className="band-name">{tr("bas.money.goal", lang)}</div>
              <div className="band-figures">{tr("bas.money.goal.note", lang)}</div>
            </div>
            <div className="muted small">
              {money.savings ? money.savings.goal_amount : "—"}
            </div>
          </div>
          <div className="voice-row">
            <input type="range" min={250} max={50000} step={250}
                   value={money.savings?.goal_amount ?? 250} disabled={busy === "goal"}
                   onChange={(e) => setGoal(Number(e.target.value))} />
          </div>

          {money.mandate?.enabled ? (
            <>
              <div className="band-row">
                <div>
                  <div className="band-name">{tr("bas.money.caps", lang)}</div>
                  <div className="band-figures">
                    {money.mandate.cap_per_order} {tr("bas.money.cap.order", lang)}
                    {" · "}
                    {money.mandate.monthly_cap} {tr("bas.money.cap.month", lang)}
                  </div>
                </div>
              </div>
              <div className="voice-row">
                <input type="range" min={10} max={1000} step={10}
                       value={money.mandate.cap_per_order}
                       disabled={busy === "cap_per_order"}
                       onChange={(e) => setCap("cap_per_order", Number(e.target.value))} />
                <input type="range" min={50} max={5000} step={50}
                       value={money.mandate.monthly_cap}
                       disabled={busy === "monthly_cap"}
                       onChange={(e) => setCap("monthly_cap", Number(e.target.value))} />
              </div>
            </>
          ) : (
            <p className="muted small">{tr("bas.money.caps.none", lang)}</p>
          )}
        </div>
      )}
    </div>
  );
}

// Moved here whole from Settings in the limits round-up: the vigil's
// quiet-days threshold is a line the Guardian draws around this person,
// and those live on this screen now.
function VigilPanel() {
  const { session } = useSession();
  const lang = visitorLang();
  const [st, setSt] = useState<VigilStatus | null>(null);
  const [name, setName] = useState("");
  const [channel, setChannel] = useState("");
  const [days, setDays] = useState(3);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function load() {
    if (!session.userId || !session.userToken) return;
    // sweep, not just read: opening the app is the natural moment to ask
    // "has anyone gone quiet?" — it is idempotent and trips at most once.
    api.sweepVigil(session.userId, session.userToken).then((s) => {
      setSt(s);
      if (s.armed) {
        setName(s.steward_name || ""); setChannel(s.steward_channel || "");
        setDays(s.quiet_days || 3); setNote(s.note || "");
      }
    }).catch(() => setSt(null));
  }
  useEffect(load, [session.userId]);

  if (!session.userId || !session.userToken) return null;

  async function run(fn: () => Promise<VigilStatus>) {
    setBusy(true); setError(null);
    try { setSt(await fn()); } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <div className="card">
      <h3>{tr("set.vigil", lang)}</h3>
      <p className="muted small">{tr("set.vigil.pitch", lang)}</p>
      {st?.tripped && (
        <div className="degraded">
          {tr("set.vigil.tripped", lang)
            .replace("{name}", String(st.steward_name))
            .replace("{after}", st.silent_hours != null
              ? tr("set.vigil.after", lang).replace("{n}",
                  String(Math.round((st.silent_hours) / 24 * 10) / 10))
              : "")}
          <div style={{ marginTop: 8 }}>
            <button className="primary" disabled={busy}
                    onClick={() => run(() => api.resolveVigil(session.userId!, session.userToken!))}>
              {tr("set.vigil.okay", lang)}
            </button>
          </div>
        </div>
      )}
      <div className="row">
        <label>{tr("set.vigil.name", lang)}<input value={name} placeholder={tr("set.vigil.name.ph", lang)} onChange={(e) => setName(e.target.value)} /></label>
        <label>{tr("set.vigil.reach", lang)}<input value={channel} placeholder={tr("set.vigil.reach.ph", lang)} onChange={(e) => setChannel(e.target.value)} /></label>
      </div>
      <label>{tr("set.vigil.days", lang)}
        <input type="number" min={1} max={60} value={days} onChange={(e) => setDays(Number(e.target.value))} />
      </label>
      <label>{tr("set.vigil.words", lang)} <span className="muted small">{tr("set.vigil.words.note", lang)}</span>
        <input value={note} placeholder={tr("set.vigil.words.ph", lang)} onChange={(e) => setNote(e.target.value)} />
      </label>
      <div className="actions">
        <button className="primary" disabled={busy || !name.trim() || !channel.trim()}
                onClick={() => run(() => api.armVigil(session.userId!, session.userToken!,
                  { steward_name: name, steward_channel: channel, quiet_days: days, note: note || undefined }))}>
          {st?.armed ? tr("set.vigil.update", lang)
                     : tr("set.vigil.arm", lang)}
        </button>
        {st?.armed && (
          <button disabled={busy}
                  onClick={() => run(() => api.disarmVigil(session.userId!, session.userToken!))}>
            {tr("set.vigil.disarm", lang)}
          </button>
        )}
        {/* A read, not a sweep. Opening this screen sweeps — which is the
            right default, because opening the app is the natural moment to
            ask whether anybody has gone quiet — but a sweep can *trip* the
            vigil and send a stranger to somebody's door. That makes it a
            write, and a write should not be the only way to look at a
            thing. This is the way to look without acting. */}
        <button disabled={busy}
                onClick={() => run(() => api.getVigil(session.userId!, session.userToken!))}>
          {tr("set.vigil.check", lang)}
        </button>
      </div>
      {st?.armed && st.last_heard_at && !st.tripped && (
        <div className="muted small">
          {tr("set.vigil.armed", lang)
            .replace("{when}", st.silent_hours != null
              ? `${st.silent_hours}h ago` : "recently")
            .replace("{name}", String(st.steward_name))}
        </div>
      )}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
