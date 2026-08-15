import { useState } from "react";
import { api, type CheckinResult } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

export function Checkin() {
  const { session } = useSession();
  const lang = visitorLang();
  const [mood, setMood] = useState(4);
  const [energy, setEnergy] = useState(3);
  const [stress, setStress] = useState(2);
  const [note, setNote] = useState("");
  const [result, setResult] = useState<CheckinResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function save() {
    if (!session.userId || !session.userToken) return;
    setBusy(true); setError(null);
    try { setResult(await api.checkin(session.userId, { mood, energy, stress, note }, session.userToken)); }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("chk.title", lang)}</h2>
        <span className="muted small">{tr("chk.sub", lang)}</span>
      </header>
      <div className="card">
        <label>{tr("chk.mood", lang)} <b className="green">{mood}</b> / 5
          <input type="range" min="1" max="5" value={mood} onChange={(e) => setMood(+e.target.value)} /></label>
        <label>{tr("chk.energy", lang)} <b className="amber">{energy}</b> / 5
          <input type="range" min="1" max="5" value={energy} onChange={(e) => setEnergy(+e.target.value)} /></label>
        <label>{tr("chk.stress", lang)} <b className="red">{stress}</b> / 5
          <input type="range" min="1" max="5" value={stress} onChange={(e) => setStress(+e.target.value)} /></label>
        <label>{tr("chk.note", lang)}<textarea rows={2} value={note} onChange={(e) => setNote(e.target.value)} /></label>
        <button className="primary" onClick={save} disabled={busy}>{busy ? tr("set.saving", lang) : tr("chk.save", lang)}</button>
        {error && <div className="error">⚠ {error}</div>}
      </div>
      {/* role=status + aria-live: the check-in's verdict is announced to a
          screen reader instead of appearing silently below the sliders. */}
      {result && (
        <div className="card" role="status" aria-live="polite">
          <h3>{tr("chk.logged", lang)}</h3>
          <div className="muted small">{tr("chk.result", lang)
            .replace("{mood}", String(result.mood))
            .replace("{energy}", String(result.energy))
            .replace("{stress}", String(result.stress ?? stress))}</div>
          {result.guardian?.detected ? (
            <div className="detect hit" style={{ marginTop: 10 }}>
              <div className="detect-head"><span className="tag warn">{tr("chk.guardian", lang)}</span> {tr("chk.flagged", lang)}</div>
              {result.guardian.guidance?.content && <p>{result.guardian.guidance.content}</p>}
            </div>
          ) : <div className="ok-note" style={{ marginTop: 10 }}>{tr("chk.noconcern", lang)}</div>}
          {/* Until an engaged session needed a way to undo one, nothing in
              this product could delete a check-in: a person could say how
              they felt and had no way to unsay it. */}
          {result.id && (
            <button style={{ marginTop: 10 }} disabled={busy}
                    onClick={async () => {
                      if (!session.userId || !session.userToken) return;
                      setBusy(true);
                      try {
                        await api.removeCheckin(session.userId,
                          String(result.id), session.userToken);
                        setResult(null);
                      } catch (e) { setError((e as Error).message); }
                      finally { setBusy(false); }
                    }}>
              {tr("chk.remove", lang)}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
