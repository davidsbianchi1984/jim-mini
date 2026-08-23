import { useEffect, useRef, useState } from "react";
import { api, type CheckinResult, type Guidance } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { CONVERSATION_IDLE_MS, heardNothing, hush, hushAndReport, listen, primeVoice, say,
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
  // Deafened on purpose, and distinct from not listening: `listening` is
  // whether the ear is open right now, `muted` is whether it is allowed
  // to be. The same control the coach sphere carries, for the same
  // reason — these are one surface wearing two names.
  const [muted, setMuted] = useState(false);
  const [level, setLevel] = useState(0);
  const [who, setWho] = useState<string | null>(null);
  const [needsTap, setNeedsTap] = useState(false);
  const recorder = useRef<Listener | null>(null);
  const talking = useRef(false);
  const round = useRef(0);
  const lastHeard = useRef(0);
  // How much of the last reply reached the person before they spoke over
  // it, held from the moment of the interruption until the turn it belongs
  // to is sent. Empty whenever nothing was interrupted, which is most turns.
  const cutOff = useRef("");
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
    // Spent, not read: an interruption is a fact about ONE turn. Left in
    // place it would ride the next question too, and the Guardian would
    // account for a paragraph nobody had cut off.
    const cut = cutOff.current; cutOff.current = "";
    try {
      // Only the Guardian's own door carries it. A specialist answer is a
      // reply from a profile in QRME, reached over the tandem link, and
      // that door takes a question and nothing else — so the honest thing
      // is to send it where it is read and not where it would be dropped.
      const reply = area.current
        ? (await api.coachSpecialist(session.userId,
            { area: area.current, message: text }, session.userToken))
        : (await api.coach(session.userId,
            { area: "general", message: text,
              ...(cut ? { cut_off_heard: cut } : {}) },
            session.userToken));
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
    // Muted is a hard gate, not a filter: nothing opens the microphone
    // while it is on, including the re-open a silent stretch triggers.
    if (muted) { setListening(false); return; }
    const g = ++round.current;
    setListening(true);
    recorder.current = await listen(
      (text) => {
        if (g !== round.current) return;
        sayGen.current++;
        // Barging in is a turn, and it is also a FACT about the answer
        // being barged in on: the reply is played piece by piece, so this
        // is the one moment the console can say how much of it landed.
        // Read before the stop, because after it there is nothing to read.
        cutOff.current = hushAndReport();
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

  /** Deafen the ear without ending the conversation. Tapping the veil
   *  ends it, which is the wrong tool for "hold on, I'm talking to
   *  someone else." The sphere keeps speaking while muted: being unable
   *  to interrupt is a different complaint from being overheard. */
  function flipMuted() {
    if (muted) {
      setMuted(false);
      if (talking.current && !speaking) void hear();
      return;
    }
    setMuted(true);
    round.current++;            // orphan any in-flight recogniser callback
    recorder.current?.stop();
    recorder.current = null;
    setListening(false); setLevel(0);
  }

  function exitTalk() {
    talking.current = false;
    setMuted(false);
    round.current++;
    recorder.current?.stop();
    recorder.current = null;
    hush();
    setListening(false); setSpeaking(false); setLevel(0); setNeedsTap(false);
  }

  // Leaving the screen ends the conversation. There was no unmount
  // teardown at all: navigating away mid-reply left a headless loop —
  // the voice kept talking, and the standing conversation re-opened the
  // microphone under a screen that no longer exists.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => () => exitTalk(), []);

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
                      : muted ? tr("cch.muted", lang)
                      : speaking ? tr("cch.speaking.hush", lang)
                      : tr("cch.listening.stop", lang)}
          </div>
          {/* Not while the veil is still asking for the first tap: a mute
              offered before the microphone has ever opened is a control
              for a state that does not exist yet. `stopPropagation`, or
              the press that mutes also ends the conversation. */}
          {!needsTap && (
            <button className={"voice-orb-mute" + (muted ? " muted" : "")}
                    aria-pressed={muted}
                    aria-label={muted ? tr("cch.unmute", lang)
                                      : tr("cch.mute", lang)}
                    title={muted ? tr("cch.unmute", lang)
                                 : tr("cch.mute", lang)}
                    onClick={(e) => { e.stopPropagation(); flipMuted(); }}>
              {muted ? "🔇" : "🎙"}
            </button>
          )}
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
