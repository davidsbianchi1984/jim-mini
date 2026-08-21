import { useEffect, useRef, useState } from "react";
import { api, type CheckinResult, type Guidance } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { CONVERSATION_IDLE_MS, heardNothing, hush, listen, primeVoice, say,
         type Listener } from "../speech";
import { useSession } from "../store";

// How you are, said back out loud when it matters.
//
// A worrying note here runs the same Guardian pipeline as the monitoring
// screen, and for a round the resemblance ended there: the monitor got the
// specialist's sphere — her name, her voice, the discussion at her own
// door — while the check-in printed the identical guidance as a paragraph
// under the sliders. The round that was picked before the interruptions
// ("carrying the specialist's sphere to the check-in screen") lands here:
// one pipeline, one sphere, whichever screen the worry arrived through.
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

  // The sphere — the same standing conversation the monitor carries, with
  // the same honesty rules: the mic opens WITH her voice (interrupting is
  // a turn), a reply that "finished" instantly is autoplay refused and
  // holds a tap-to-hear state, and the idle exit never fires mid-reply.
  const [speaking, setSpeaking] = useState(false);
  const [listening, setListening] = useState(false);
  const [level, setLevel] = useState(0);
  const [who, setWho] = useState<string | null>(null);
  const [needsTap, setNeedsTap] = useState(false);
  const recorder = useRef<Listener | null>(null);
  const talking = useRef(false);
  const round = useRef(0);
  const lastHeard = useRef(0);
  const area = useRef<string | null>(null);
  const sayGen = useRef(0);
  const saying = useRef(false);
  useEffect(() => { void primeVoice(); }, []);

  async function save() {
    if (!session.userId || !session.userToken) return;
    setBusy(true); setError(null);
    try {
      const r = await api.checkin(session.userId,
        { mood, energy, stress, note }, session.userToken);
      setResult(r);
      if (r.guardian?.detected && r.guardian.guidance?.content) {
        chime(r.guardian.guidance);
      }
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  function chime(g: Guidance) {
    setWho(g.specialist || g.source || null);
    area.current = g.specialist_area || null;
    talking.current = true;
    lastHeard.current = Date.now();
    setSpeaking(true);
    void hear();
    const t0 = Date.now();
    const sg = ++sayGen.current;
    saying.current = true;
    say(g.content).finally(() => {
      saying.current = false;
      if (Date.now() - t0 < 400 && g.content.length > 40) {
        setNeedsTap(true);
        return;
      }
      if (sg === sayGen.current) setSpeaking(false);
      if (talking.current) lastHeard.current = Date.now();
    });
  }

  function tapToHear() {
    const g = result?.guardian?.guidance;
    if (!g?.content) { exitTalk(); return; }
    setNeedsTap(false);
    const sg = ++sayGen.current;
    saying.current = true;
    say(g.content).finally(() => {
      saying.current = false;
      if (sg === sayGen.current) setSpeaking(false);
      if (talking.current) lastHeard.current = Date.now();
    });
  }

  async function discuss(text: string) {
    if (!session.userId || !session.userToken) return;
    try {
      const reply = area.current
        ? (await api.coachSpecialist(session.userId,
            { area: area.current, message: text }, session.userToken))
        : (await api.coach(session.userId,
            { area: "general", message: text }, session.userToken));
      const content = reply?.content
        || ("note" in (reply || {}) ? (reply as { note?: string }).note : "")
        || "";
      if (content && talking.current) {
        setSpeaking(true);
        if (talking.current) { lastHeard.current = Date.now(); void hear(); }
        const sg = ++sayGen.current;
        saying.current = true;
        say(content).finally(() => {
          saying.current = false;
          if (sg === sayGen.current) setSpeaking(false);
          if (talking.current) lastHeard.current = Date.now();
        });
      } else {
        setSpeaking(false);
        if (talking.current) { lastHeard.current = Date.now(); void hear(); }
      }
    } catch (e) {
      talking.current = false;
      setSpeaking(false); setError((e as Error).message);
    }
  }

  async function hear() {
    const g = ++round.current;
    setListening(true);
    recorder.current = await listen(
      (text) => {
        if (g !== round.current) return;
        sayGen.current++;
        hush();
        lastHeard.current = Date.now();
        setListening(false); setSpeaking(true);
        void discuss(text);
      },
      (msg) => {
        if (g !== round.current) return;
        if (talking.current && heardNothing(msg)) {
          if (!saying.current
              && Date.now() - lastHeard.current >= CONVERSATION_IDLE_MS) {
            exitTalk();
            return;
          }
          void hear();
          return;
        }
        talking.current = false;
        setListening(false); setError(msg);
      },
      setLevel,
    );
  }

  function exitTalk() {
    talking.current = false;
    round.current++;
    recorder.current?.stop();
    recorder.current = null;
    hush();
    setListening(false); setSpeaking(false); setLevel(0); setNeedsTap(false);
  }

  return (
    <div className="screen">
      {(listening || speaking || needsTap) && (
        <div className="voice-orb-veil" role="status"
             aria-label={listening ? "Listening" : "Speaking"}
             onClick={needsTap ? tapToHear : exitTalk}>
          <div className={"voice-orb-holder" + (speaking ? " speaking" : "")}>
            <div className="voice-orb-ring"
                 style={{ transform: `scale(${1 + level * 0.45})`,
                          opacity: 0.3 + level * 0.7 }} />
            <div className={"voice-orb " + (speaking ? "speaking" : "listening")} />
          </div>
          {who && <div className="voice-orb-who">{who}</div>}
          <div className="voice-orb-label">
            {needsTap ? tr("mon.taptohear", lang)
                      : speaking ? tr("cch.speaking.hush", lang)
                      : tr("cch.listening.stop", lang)}
          </div>
        </div>
      )}
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
              {/* The sphere speaks it; the card keeps it readable — the
                  voice is how the message stops being missable, never
                  the only copy of it. */}
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
