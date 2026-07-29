import { useState } from "react";
import { api } from "./api";

/**
 * The help box, on every screen.
 *
 * Mounted in App outside the tab switch, because "available on all screens" is
 * a property of the shell rather than something each screen can be trusted to
 * remember — and the one screen that forgets is the one somebody is stuck on.
 *
 * Deliberately faceless and unnamed, matching QRME's: the Guardian is the
 * character in this product, and the help box is just the map. Anything
 * beyond the app's own doors it hands to the Coach — which is JIM.
 */
export function Help() {
  const [open, setOpen] = useState(false);
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

  if (!open) {
    return (
      <button className="help-fab" onClick={() => setOpen(true)}
              aria-label="Help">?</button>
    );
  }

  return (
    <div className="help-panel" role="dialog" aria-label="Help">
      <header>
        <strong>Help</strong>
        <button className="help-close" onClick={() => setOpen(false)}
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
  );
}
