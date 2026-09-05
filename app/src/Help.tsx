import { useState } from "react";
import { api } from "./api";
import { t as tr, visitorLang } from "./l10n";

/**
 * The help box, on every screen.
 *
 * Mounted from the edge dock rather than by any screen, because "available
 * on all screens" is a property of the shell rather than something each
 * screen can be trusted to remember — and the one screen that forgets is
 * the one somebody is stuck on.
 *
 * It was a "?" bubble fixed to a corner. It is a tab on the dock now: the
 * same panel, opened beside the tab instead of over the corner of whatever
 * screen was underneath.
 *
 * Deliberately faceless and unnamed, matching QRME's: the Guardian is the
 * character in this product, and the help box is just the map. Anything
 * beyond the app's own doors it hands to the Coach — which is JIM.
 */
export function Help({ open, onToggle }:
                     { open: boolean; onToggle: () => void }) {
  const lang = visitorLang();
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function ask() {
    const question = q.trim();
    if (!question) return;
    setBusy(true);
    setAnswer(null);
    try {
      const r = await api.help(question);
      setAnswer(r.answer);
      // Marked when a model wrote it. On a page full of disclosed synthetic
      // profiles, a generated sentence should not be the one unlabelled thing.
      setNote(r.ai ? "AI-generated · " + r.disclosure : r.disclosure);
    } catch {
      setAnswer("Help isn't reachable right now.");
      setNote(null);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <button className={"edge-tab help-fab" + (open ? " on" : "")}
              type="button" aria-expanded={open} onClick={onToggle}
              aria-label={tr("dock.help", lang)} title={tr("dock.help", lang)}>
        <span className="help-mark" aria-hidden="true">?</span>
        <span className="edge-tab-word">{tr("dock.help", lang)}</span>
      </button>
      {open && (
    <div className="edge-panel help-panel" role="dialog"
         aria-label={tr("dock.help", lang)}>
      <header>
        <strong>{tr("dock.help", lang)}</strong>
        <button className="help-close" onClick={onToggle}
                aria-label="Close help">×</button>
      </header>
      <div className="help-body">
        {answer && <p className="help-answer">{answer}</p>}
        {answer && note && <p className="help-note">{note}</p>}
        {!answer && (
          <p className="help-note">
            Ask about profiles, beacons, memory, desks, reviews or the age
            gate. This isn't one of the synthetic profiles — it has no persona
            and no memory of you.
          </p>
        )}
      </div>
      <div className="help-ask">
        <input value={q} placeholder="What would you like to know?"
               onChange={(e) => setQ(e.target.value)}
               onKeyDown={(e) => e.key === "Enter" && ask()} />
        <button className="primary" onClick={ask} disabled={busy}>
          {busy ? "…" : "Ask"}
        </button>
      </div>
    </div>
      )}
    </>
  );
}
