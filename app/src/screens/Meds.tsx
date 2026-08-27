import { useEffect, useState } from "react";
import { api, type MedBoard } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

// The medicine cabinet. Tracked in the user's own words — JIM is not a
// pharmacist and the board says so on its face. A missed dose is a
// question, never an alarm.
export function Meds() {
  const { session } = useSession();
  const lang = visitorLang();
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
      <header className="screen-head"><h2>{tr("med.title", lang)}</h2></header>

      {board && board.missed_critical.length > 0 && (
        <div className="degraded">
          {tr("med.missed", lang).replace("{list}", board.missed_critical
            .map((m) => `${m.name} (${m.slot})`).join(", "))}
        </div>
      )}

      <div className="card">
        <h3>{tr("med.today", lang)}</h3>
        {board?.medications.length === 0 && (
          <p className="muted small">{tr("med.none", lang)}</p>
        )}
        {board?.medications.map((m) => (
          <div key={m.id} className="med-row">
            <div className="med-head">
              <b>{m.name}</b> <span className="muted small">{m.dose}{m.purpose ? ` · ${m.purpose}` : ""}{m.critical ? tr("med.critical.mark", lang) : ""}</span>
              <button className="med-archive" disabled={busy}
                      onClick={() => { if (confirm(`Stop tracking ${m.name}? The history is kept.`)) run(() => api.medsArchive(uid, m.id, token)); }}>
                {tr("med.stop", lang)}
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
                                onClick={() => run(() => api.medsLog(uid, m.id, token, { action: "taken", slot: s.slot }))}>{tr("med.take", lang)}</button>
                        <button disabled={busy}
                                onClick={() => run(() => api.medsLog(uid, m.id, token, { action: "skipped", slot: s.slot }))}>{tr("med.skip", lang)}</button>
                      </span>
                    )}
                    {s.status === "skipped" && (
                      <button disabled={busy}
                              onClick={() => run(() => api.medsLog(uid, m.id, token, { action: "taken", slot: s.slot, note: "corrected" }))}>
                        {tr("med.actually", lang)}
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
                  <span className="med-status">{tr("med.asneeded.line", lang)
                    .replace("{n}", String(m.taken_today || 0))
                    .replace("{max}", m.max_per_day
                      ? tr("med.asneeded.max", lang)
                          .replace("{max}", String(m.max_per_day))
                      : "")}</span>
                  <button className="primary" disabled={busy}
                          onClick={() => run(() => api.medsLog(uid, m.id, token, { action: "taken" }))}>{tr("med.tookone", lang)}</button>
                </div>
              </div>
            )}
          </div>
        ))}
        {board && <p className="muted small" style={{ marginTop: 10 }}>{board.disclaimer}</p>}
      </div>

      {adherence && adherence.adherence_rows.some((m) => m.rate !== null) && (
        <div className="card">
          <h3>{tr("med.last", lang).replace("{n}", String(adherence.window_days))}</h3>
          {adherence.adherence_rows.filter((m) => m.rate !== null).map((m) => (
            <div key={m.id} className="med-adherence">
              <span>{m.name}</span>
              <div className="med-bar"><div className="med-bar-fill" style={{ width: `${Math.round((m.rate || 0) * 100)}%` }} /></div>
              <span className="muted small">{tr("med.of", lang)
                .replace("{taken}", String(m.taken))
                .replace("{expected}", String(m.expected))}</span>
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h3>{tr("med.add", lang)}</h3>
        <p className="muted small">{tr("med.add.pitch", lang)}</p>
        <div className="row">
          <label>{tr("med.name", lang)}<input value={name} placeholder={tr("med.name.ph", lang)} onChange={(e) => setName(e.target.value)} /></label>
          <label>{tr("med.dose", lang)}<input value={dose} placeholder={tr("med.dose.ph", lang)} onChange={(e) => setDose(e.target.value)} /></label>
        </div>
        <label>{tr("med.purpose", lang)} <span className="muted small">{tr("med.optional", lang)}</span>
          <input value={purpose} placeholder={tr("med.purpose.ph", lang)} onChange={(e) => setPurpose(e.target.value)} />
        </label>
        <label className="check">
          <input type="checkbox" checked={asNeeded} onChange={(e) => setAsNeeded(e.target.checked)} /> {tr("med.asneeded", lang)}
        </label>
        {asNeeded ? (
          <label>{tr("med.ceiling", lang)} <span className="muted small">{tr("med.ceiling.note", lang)}</span>
            <input type="number" min={1} value={maxPerDay} onChange={(e) => setMaxPerDay(e.target.value ? Number(e.target.value) : "")} />
          </label>
        ) : (
          <label>{tr("med.times", lang)} <span className="muted small">{tr("med.times.note", lang)}</span>
            <input value={times} placeholder="08:00, 20:00" onChange={(e) => setTimes(e.target.value)} />
          </label>
        )}
        <label className="check">
          <input type="checkbox" checked={critical} onChange={(e) => setCritical(e.target.checked)} /> {tr("med.critical", lang)}
        </label>
        <button className="primary" disabled={busy || !name.trim() || !dose.trim()} onClick={add}>
          {busy ? tr("set.saving", lang) : tr("med.add.button", lang)}
        </button>
      </div>

      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
