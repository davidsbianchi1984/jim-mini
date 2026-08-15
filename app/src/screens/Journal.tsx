import { useEffect, useRef, useState } from "react";
import { api, type JournalRow, type LetterRow, type MealRow } from "../api";
import { listen, primeVoice, type Listener } from "../speech";
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
  const [meals, setMeals] = useState<MealRow[]>([]);
  const [mealNote, setMealNote] = useState("");
  const [mealPhoto, setMealPhoto] = useState<string | null>(null);
  const [letters, setLetters] = useState<LetterRow[]>([]);

  function load() {
    if (!session.userId || !session.userToken) return;
    api.journal(session.userId, session.userToken)
      .then(setEntries)
      .catch((e) => setError((e as Error).message));
    api.meals(session.userId, session.userToken)
      .then(setMeals)
      .catch(() => setMeals([]));
    api.letters(session.userId, session.userToken)
      .then(setLetters)
      .catch(() => setLetters([]));
  }

  async function writeLetter() {
    if (!session.userId || !session.userToken) return;
    setBusy(true); setError(null);
    try {
      await api.writeLetter(session.userId, session.userToken);
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function logMeal() {
    if (!session.userId || !session.userToken || !mealNote.trim()) return;
    setBusy(true); setError(null);
    try {
      await api.logMeal(session.userId, mealNote.trim(), session.userToken,
                        mealPhoto ?? undefined);
      setMealNote(""); setMealPhoto(null); load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  function pickMealPhoto(file: File | null) {
    if (!file) { setMealPhoto(null); return; }
    const reader = new FileReader();
    reader.onload = () => {
      const url = String(reader.result || "");
      setMealPhoto(url.slice(url.indexOf(",") + 1) || null);
    };
    reader.readAsDataURL(file);
  }
  useEffect(load, [session.userId]);
  // Same reason as Coach: the microphone's path is settled on mount, so
  // the tap itself never awaits. See `listen` in ../speech.
  useEffect(() => { void primeVoice(); }, []);

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
            {listening ? tr("jrn.listening", lang) : tr("jrn.speak", lang)}
          </button>
          <button className="primary" disabled={busy || !text.trim()}
                  onClick={() => add()}>
            {busy ? tr("set.saving", lang) : tr("jrn.add", lang)}
          </button>
        </div>
        <p className="muted small">{tr("jrn.sealed", lang)}</p>
      </div>

      {/* Meals: the photo is the receipt, the note is the log. No pretended
          vision — the log comes from the person's words, tidied by the
          online model when one is standing. */}
      <div className="card">
        <h3>{tr("mea.title", lang)}</h3>
        <div className="row">
          <input value={mealNote} placeholder={tr("mea.ph", lang)}
                 onChange={(e) => setMealNote(e.target.value)} style={{ flex: 1 }} />
          <input type="file" accept="image/*"
                 onChange={(e) => pickMealPhoto(e.target.files?.[0] ?? null)} />
          <button className="primary" disabled={busy || !mealNote.trim()}
                  onClick={logMeal}>{tr("mea.log", lang)}</button>
        </div>
        <p className="muted small">{tr("mea.receipt", lang)}</p>
        {meals.length === 0 && (
          <div className="muted small">{tr("mea.none", lang)}</div>
        )}
        {meals.map((m) => (
          <div key={m.id}
               style={{ padding: "8px 0", borderBottom: "1px solid var(--line)" }}>
            <div className="muted small">
              {m.created_at ? new Date(m.created_at).toLocaleString() : ""}
              {m.photo_sealed ? " · " + tr("mea.sealed", lang) : ""}
            </div>
            <div>{m.logged}</div>
          </div>
        ))}
      </div>

      {/* The weekly letter: composed only from what was logged — no
          invented feelings, no homework. A week with nothing logged gets
          no letter, and the refusal says so. */}
      <div className="card">
        <h3>{tr("let.title", lang)}</h3>
        <p className="muted small">{tr("let.pitch", lang)}</p>
        <button className="primary" disabled={busy} onClick={writeLetter}>
          {tr("let.write", lang)}
        </button>
        {letters.length === 0 && (
          <div className="muted small">{tr("let.none", lang)}</div>
        )}
        {letters.map((l) => (
          <div key={l.id}
               style={{ padding: "8px 0", borderBottom: "1px solid var(--line)" }}>
            <div className="muted small">{l.week_start}</div>
            <div style={{ whiteSpace: "pre-wrap" }}>{l.body}</div>
          </div>
        ))}
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
              {e.vaulted ? tr("jrn.vaulted", lang) : ""}
            </div>
            <div>{e.text}</div>
            {/* Somebody writing their own diary should always have had this,
                and it is the way back from an engaged session that wrote an
                entry for them. */}
            <button disabled={busy}
                    onClick={async () => {
                      if (!session.userId || !session.userToken) return;
                      await api.removeJournal(session.userId, String(e.id),
                                              session.userToken);
                      setEntries(await api.journal(session.userId,
                                                   session.userToken));
                    }}>
              {tr("jrn.remove", lang)}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
