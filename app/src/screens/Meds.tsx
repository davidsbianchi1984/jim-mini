import { useEffect, useState } from "react";
import { api, type MedBoard } from "../api";
import { useSession } from "../store";

// The medicine cabinet. Tracked in the user's own words — JIM is not a
// pharmacist and the board says so on its face. A missed dose is a
// question, never an alarm.
export function Meds() {
  const { session } = useSession();
  const [board, setBoard] = useState<MedBoard | null>(null);
  const [adherence, setAdherence] = useState<Awaited<ReturnType<typeof api.medsAdherence>> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // add form
  const [name, setName] = useState("");
  const [dose, setDose] = useState("");
  const [purpose, setPurpose] = useState("");
  const [times, setTimes] = useState("08:00");
  const [asNeeded, setAsNeeded] = useState(false);
  const [maxPerDay, setMaxPerDay] = useState<number | "">("");
  const [critical, setCritical] = useState(false);

  function load() {
    if (!session.userId || !session.userToken) return;
    api.medsBoard(session.userId, session.userToken).then(setBoard).catch((e) => setError((e as Error).message));
    api.medsAdherence(session.userId, session.userToken, 7).then(setAdherence).catch(() => setAdherence(null));
  }
  useEffect(load, [session.userId]);

  if (!session.userId || !session.userToken) return null;
  const uid = session.userId, token = session.userToken;

  async function run(fn: () => Promise<unknown>) {
    setBusy(true); setError(null);
    try { await fn(); load(); }
    catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function add() {
    const schedule = asNeeded
      ? { as_needed: true, ...(maxPerDay ? { max_per_day: Number(maxPerDay) } : {}) }
      : { times: times.split(",").map((t) => t.trim()).filter(Boolean) };
    await run(() => api.medsAdd(uid, token, {
      name, dose, schedule, purpose: purpose || undefined, critical }));
    setName(""); setDose(""); setPurpose(""); setCritical(false);
  }

  const statusLabel: Record<string, string> = {
    taken: "✓ taken", skipped: "— skipped", due: "due now",
    upcoming: "later today", missed: "missed",
  };

  return (
    <div className="screen">
      <header className="screen-head"><h2>Medications</h2></header>

      {board && board.missed_critical.length > 0 && (
        <div className="degraded">
          ⚠ {board.missed_critical.map((m) => `${m.name} (${m.slot})`).join(", ")} —
          marked critical and not logged today. If you took it, tap it below;
          if you didn't, that's worth a moment.
        </div>
      )}

      <div className="card">
        <h3>Today</h3>
        {board?.medications.length === 0 && (
          <p className="muted small">Nothing here yet — add what you take below, in your own words.</p>
        )}
        {board?.medications.map((m) => (
          <div key={m.id} className="med-row">
            <div className="med-head">
              <b>{m.name}</b> <span className="muted small">{m.dose}{m.purpose ? ` · ${m.purpose}` : ""}{m.critical ? " · critical" : ""}</span>
              <button className="med-archive" disabled={busy}
                      onClick={() => { if (confirm(`Stop tracking ${m.name}? The history is kept.`)) run(() => api.medsArchive(uid, m.id, token)); }}>
                stop
              </button>
            </div>
            {m.kind === "scheduled" && m.slots && (
              <div className="med-slots">
                {m.slots.map((s) => (
                  <div key={s.slot} className={`med-slot ${s.status}`}>
                    <span className="mono">{s.slot}</span>
                    <span className="med-status">{statusLabel[s.status] || s.status}</span>
                    {(s.status === "due" || s.status === "missed" || s.status === "upcoming") && (
                      <span className="actions">
                        <button className="primary" disabled={busy}
                                onClick={() => run(() => api.medsLog(uid, m.id, token, { action: "taken", slot: s.slot }))}>Take</button>
                        <button disabled={busy}
                                onClick={() => run(() => api.medsLog(uid, m.id, token, { action: "skipped", slot: s.slot }))}>Skip</button>
                      </span>
                    )}
                    {s.status === "skipped" && (
                      <button disabled={busy}
                              onClick={() => run(() => api.medsLog(uid, m.id, token, { action: "taken", slot: s.slot, note: "corrected" }))}>
                        Actually took it
                      </button>
                    )}
                    {s.note && <span className="muted small">“{s.note}”</span>}
                  </div>
                ))}
              </div>
            )}
            {m.kind === "as_needed" && (
              <div className="med-slots">
                <div className="med-slot">
                  <span className="med-status">as needed · {m.taken_today || 0} today{m.max_per_day ? ` of ${m.max_per_day} max` : ""}</span>
                  <button className="primary" disabled={busy}
                          onClick={() => run(() => api.medsLog(uid, m.id, token, { action: "taken" }))}>Took one</button>
                </div>
              </div>
            )}
          </div>
        ))}
        {board && <p className="muted small" style={{ marginTop: 10 }}>{board.disclaimer}</p>}
      </div>

      {adherence && adherence.medications.some((m) => m.rate !== null) && (
        <div className="card">
          <h3>Last {adherence.days} days</h3>
          {adherence.medications.filter((m) => m.rate !== null).map((m) => (
            <div key={m.id} className="med-adherence">
              <span>{m.name}</span>
              <div className="med-bar"><div className="med-bar-fill" style={{ width: `${Math.round((m.rate || 0) * 100)}%` }} /></div>
              <span className="muted small">{m.taken} of {m.expected}</span>
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h3>Add a medication</h3>
        <p className="muted small">Your words are fine — “the little white one, 10 mg” is a valid name and dose.</p>
        <div className="row">
          <label>Name<input value={name} placeholder="Lisinopril" onChange={(e) => setName(e.target.value)} /></label>
          <label>Dose<input value={dose} placeholder="10 mg" onChange={(e) => setDose(e.target.value)} /></label>
        </div>
        <label>What it's for <span className="muted small">(optional)</span>
          <input value={purpose} placeholder="blood pressure" onChange={(e) => setPurpose(e.target.value)} />
        </label>
        <label className="check">
          <input type="checkbox" checked={asNeeded} onChange={(e) => setAsNeeded(e.target.checked)} /> As needed, not on a schedule
        </label>
        {asNeeded ? (
          <label>Ceiling per day <span className="muted small">(optional — JIM will refuse to log past it)</span>
            <input type="number" min={1} value={maxPerDay} onChange={(e) => setMaxPerDay(e.target.value ? Number(e.target.value) : "")} />
          </label>
        ) : (
          <label>Times <span className="muted small">— comma-separated, 24h</span>
            <input value={times} placeholder="08:00, 20:00" onChange={(e) => setTimes(e.target.value)} />
          </label>
        )}
        <label className="check">
          <input type="checkbox" checked={critical} onChange={(e) => setCritical(e.target.checked)} /> Missing this one is worth a check-in
        </label>
        <button className="primary" disabled={busy || !name.trim() || !dose.trim()} onClick={add}>
          {busy ? "Saving…" : "Add to the cabinet"}
        </button>
      </div>

      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
