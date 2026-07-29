import { useEffect, useState } from "react";
import { api } from "../api";
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

  function load() {
    if (!session.userId || !session.userToken) return;
    api.getBands(session.userId, session.userToken)
      .then((r) => setBands(r.bands))
      .catch((e) => setError((e as Error).message));
  }
  useEffect(load, [session.userId]);

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
          your Guardian checks in and asks how you are. It never calls
          anybody: that stays the emergency path's job, unchanged.
        </p>
        <p className="muted small">
          The widths below are yours to set. Narrow one to be told sooner;
          widen it if a metric of yours naturally wanders.
        </p>
      </div>

      {error && <div className="error">⚠ {error}</div>}

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
