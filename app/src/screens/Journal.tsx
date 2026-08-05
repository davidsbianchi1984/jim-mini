import { useEffect, useRef, useState } from "react";
import { api, type JournalRow } from "../api";
import { listen, type Listener } from "../speech";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The journal — typed or spoken, the user's own words to JIM.
 *
 * The backend has carried this for a long time (POST/GET /journal); this
 * screen finally gives it a door. Two honest notes are part of the
 * design: entries are sealed in the vault on private plans (the row says
 * which happened), and crisis language in an entry reaches the Guardian
 * exactly as it does from monitoring — a journal is often where someone
 * says the thing they wouldn't say out loud.
 */
export function Journal() {
  const { session } = useSession();
  const lang = visitorLang();
  const [entries, setEntries] = useState<JournalRow[]>([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [listening, setListening] = useState(false);
  const recorder = useRef<Listener | null>(null);

  function load() {
    if (!session.userId || !session.userToken) return;
    api.journal(session.userId, session.userToken)
      .then(setEntries)
      .catch((e) => setError((e as Error).message));
  }
  useEffect(load, [session.userId]);

  async function add(spoken?: string) {
    const entry = (spoken ?? text).trim();
    if (!session.userId || !session.userToken || !entry) return;
    setBusy(true); setError(null);
    try {
      await api.addJournal(session.userId, entry, session.userToken);
      setText("");
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function toggleMic() {
    if (listening) {
      recorder.current?.stop();
      recorder.current = null;
      setListening(false);
      return;
    }
    setError(null);
    setListening(true);
    recorder.current = await listen(
      // Spoken words land in the box first, not straight into the record —
      // a transcription error should be the user's to fix, not to discover
      // in next week's entry.
      (said) => { setListening(false); setText((t) => (t ? t + " " : "") + said); },
      (msg) => { setListening(false); setError(msg); },
    );
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("jrn.title", lang)}</h2>
        <span className="muted small">{tr("jrn.sub", lang)}</span>
      </header>

      <div className="card">
        <h3>{tr("jrn.new", lang)}</h3>
        <textarea rows={4} value={text}
                  placeholder={tr("jrn.ph", lang)}
                  onChange={(e) => setText(e.target.value)} />
        <div className="voice-row">
          <button className={listening ? "mic listening" : "mic"}
                  onClick={toggleMic}
                  title={listening ? "Stop listening" : "Speak your entry"}>
            {listening ? "◼ listening…" : "🎙 speak"}
          </button>
          <button className="primary" disabled={busy || !text.trim()}
                  onClick={() => add()}>
            {busy ? "Saving…" : "Add to the journal"}
          </button>
        </div>
        <p className="muted small">{tr("jrn.sealed", lang)}</p>
      </div>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>{tr("jrn.entries", lang)}</h3>
        {entries.length === 0 && (
          <div className="muted small">{tr("jrn.none", lang)}</div>
        )}
        {entries.slice().reverse().map((e) => (
          <div key={e.id}
               style={{ padding: "10px 0", borderBottom: "1px solid var(--line)" }}>
            <div className="muted small">
              {new Date(e.created_at).toLocaleString()}
              {e.vaulted ? " · sealed in the vault" : ""}
            </div>
            <div>{e.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
