import { useRef, useState } from "react";
import { api, type FollowupResult, type Guidance,
         type MonitorResult } from "../api";
import { PaceCue } from "../PaceCue";
import { t as tr, visitorLang } from "../l10n";
import { CONVERSATION_IDLE_MS, hush, heardNothing, listen, primeVoice,
         say, type Listener } from "../speech";
import { useSession } from "../store";
import { useEffect } from "react";

export function Monitor() {
  const { session } = useSession();
  const lang = visitorLang();
  const [hr, setHr] = useState(110);
  const [resp, setResp] = useState(22);
  const [stress, setStress] = useState(0.8);
  const [result, setResult] = useState<MonitorResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<FollowupResult | null>(null);
  const [asking, setAsking] = useState(false);

  // The specialist's own sphere. A field report: blood oxygen dropped, the
  // attached doctor profile chimed in — with text, easy to scroll past.
  // When guidance lands on a detection now, she pops up and says it, and
  // the microphone opens for a discussion at her own door. The sphere
  // never replaces the emergency card and its call door — one tap on the
  // veil and they are in front of you; the voice is how the message stops
  // being missable, not a gate in front of the help.
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [level, setLevel] = useState(0);
  const [who, setWho] = useState<string | null>(null);
  // The browser held the audio. Autoplay rules can refuse a sphere that
  // opens without a fresh gesture — the say() resolves in milliseconds
  // having played nothing. A sphere that then carried on to listening
  // would have skipped the message it exists to deliver; instead it
  // stands, says the truth, and one tap (a gesture the browser accepts)
  // plays it and starts the conversation.
  const [needsTap, setNeedsTap] = useState(false);
  const recorder = useRef<Listener | null>(null);
  const talking = useRef(false);
  const round = useRef(0);
  const lastHeard = useRef(0);
  const area = useRef<string | null>(null);
  // Interrupting is a turn: the mic is open while she speaks. `sayGen`
  // orphans a hushed reply's cleanup; `saying` keeps the idle exit from
  // closing a reply still being said.
  const sayGen = useRef(0);
  const saying = useRef(false);
  useEffect(() => { void primeVoice(); }, []);

  async function submit() {
    if (!session.userId || !session.userToken) return;
    setBusy(true); setError(null); setAnswer(null);
    try {
      const r = await api.monitor(session.userId, { heart_rate: hr, respiratory_rate: resp, stress_level: stress }, session.userToken);
      setResult(r);
      if (r.detected && r.guidance?.content) chime(r.guidance);
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  /** The chime-in: her sphere opens, the guidance is spoken so it cannot
   *  be missed, and then the mic opens for the discussion — the standing
   *  loop every other conversational surface carries. */
  function chime(g: Guidance) {
    setWho(g.specialist || g.source || null);
    area.current = g.specialist_area || null;
    talking.current = true;
    lastHeard.current = Date.now();
    setSpeaking(true);
    // The microphone opens WITH her voice: interrupting mid-guidance is
    // a turn, and there is no fragile "re-open after" step to fail.
    void hear();
    const t0 = Date.now();
    const sg = ++sayGen.current;
    saying.current = true;
    say(g.content).finally(() => {
      saying.current = false;
      // A guidance paragraph that "finished speaking" in under half a
      // second played nothing — the browser refused autoplay. Hold the
      // sphere in its honest tap-to-hear state rather than sailing on
      // to a conversation about a message nobody heard.
      if (Date.now() - t0 < 400 && g.content.length > 40) {
        setNeedsTap(true);
        return;
      }
      if (sg === sayGen.current) setSpeaking(false);
      if (talking.current) lastHeard.current = Date.now();
    });
  }

  /** The tap the browser was waiting for: play the held message, then
   *  the standing conversation takes over as if autoplay had worked. */
  function tapToHear() {
    const g = result?.guidance;
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

  /** One discussion turn. Her area when the server named one — the same
   *  door the monitoring path just delivered through — the coach's front
   *  door otherwise, so a local-guidance detection still talks back. */
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
          // Never bow out mid-reply: the idle clock only closes a room
          // where nobody is speaking.
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
    setListening(false); setSpeaking(false); setLevel(0);
  }

  // Leaving the screen ends the conversation. There was no unmount
  // teardown at all: navigating away mid-reply left a headless loop —
  // the voice kept talking, and the standing conversation re-opened the
  // microphone under a screen that no longer exists. Cleanup touches
  // refs, the shared voice module, and stable setters only, so the
  // first render's closure is the right one to keep.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => () => exitTalk(), []);

  // Spec [0039]: "did that help?" — and if it didn't, a live person.
  async function saidHelped(helped: boolean) {
    if (!session.userId || !session.userToken) return;
    setAsking(true); setError(null);
    try {
      setAnswer(await api.answerFollowup(session.userId, { helped }, session.userToken));
    } catch (e) { setError((e as Error).message); } finally { setAsking(false); }
  }

  return (
    <div className="screen">
      {(listening || speaking) && (
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
        <h2>{tr("mon.title", lang)}</h2>
        <span className="muted small">{tr("mon.sub", lang)}</span>
      </header>

      <div className="card">
        <h3>{tr("mon.submit", lang)}</h3>
        <div className="row">
          <label>{tr("mon.hr", lang)}<input type="number" value={hr} onChange={(e) => setHr(+e.target.value)} /></label>
          <label>{tr("mon.resp", lang)}<input type="number" value={resp} onChange={(e) => setResp(+e.target.value)} /></label>
        </div>
        <label>{tr("mon.stress", lang)}<input type="number" step="0.1" min="0" max="1" value={stress} onChange={(e) => setStress(+e.target.value)} /></label>
        <button className="primary" onClick={submit} disabled={busy}>{busy ? tr("mon.analyzing", lang) : tr("mon.send", lang)}</button>
        {error && <div className="error">⚠ {error}</div>}
      </div>

      {result && (
        <div className={"card detect " + (result.detected ? "hit" : "calm")}>
          <div className="detect-head">
            {result.detected
              ? <><span className="tag warn">{result.severity}</span> {result.condition}</>
              : <span className="tag ok">{tr("mon.calm", lang)}</span>}
          </div>
          {result.reason && <div className="muted small">{result.reason}</div>}
          {result.drift?.crossings?.length ? (
            <div className="guidance">
              <div className="guidance-src">{tr("mon.drift", lang)}</div>
              <p>{result.drift.question}</p>
              <ul className="refs">
                {result.drift.crossings.map((c) => (
                  <li key={c.metric}>
                    {tr("mon.reading", lang)
                      .replace("{label}", String(c.label))
                      .replace("{value}{unit}", `${c.value}${c.unit}`)
                      .replace("{direction}", String(c.direction))
                      .replace("{baseline}{unit}", `${c.baseline}${c.unit}`)
                      .replace("{edge}{unit}", `${c.edge}${c.unit}`)}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {result.guidance?.content && (
            <div className="guidance">
              <div className="guidance-src">{tr("mon.guidance", lang)
                .replace("{source}", String(result.guidance.source))}</div>
              <p>{result.guidance.content}</p>
              {result.guidance.first_aid && (
                <div className="first-aid">
                  <b>{result.guidance.first_aid.title || tr("mon.firstaid", lang)}</b>
                  <ol className="refs">
                    {result.guidance.first_aid.steps.map((s, i) => <li key={i}>{s}</li>)}
                  </ol>
                  <PaceCue aid={result.guidance.first_aid} />
                </div>
              )}
              {result.guidance.references?.length ? (
                <ul className="refs">{result.guidance.references.map((r, i) => <li key={i}>{r}</li>)}</ul>
              ) : null}
              {/* Spec [0039]: the loop's closing edge. Guidance that didn't
                  land reaches a person instead of repeating itself. */}
              {result.followup && !answer && (
                <div className="followup">
                  <b>{result.followup.question}</b>
                  <div className="followup-buttons">
                    <button onClick={() => saidHelped(true)} disabled={asking}>{tr("mon.helped", lang)}</button>
                    <button className="warn" onClick={() => saidHelped(false)} disabled={asking}>
                      {tr("mon.nothelped", lang)}
                    </button>
                  </div>
                </div>
              )}
              {answer?.helped && (
                <div className="followup"><span className="muted small">
                  {tr("mon.noted", lang)}
                </span></div>
              )}
              {answer && answer.helped === false && answer.live_assistance && (
                <div className="followup">
                  <b>{tr("mon.reaching", lang)}</b>
                  <div className="muted small">
                    {tr("mon.escalated", lang).replace("{tier}",
                      String(answer.escalation_decision?.tier.replace(/_/g, " ")))}
                  </div>
                  <ul className="refs">
                    {answer.live_assistance.options.map((o, i) => (
                      <li key={i}>
                        {o.name}{o.channel ? ` — ${o.channel}` : ""}
                        {o.note ? <span className="muted small"> ({o.note})</span> : null}
                      </li>
                    ))}
                  </ul>
                  <div className="muted small">{answer.live_assistance.note}</div>
                </div>
              )}
            </div>
          )}
          {(result.escalation as { companion?: { relaying?: { note?: string } } } | null)?.companion && (
            <div className="guidance">
              <div className="guidance-src">{tr("mon.companion", lang)}</div>
              <p>
                {tr("mon.relaying", lang)}{" "}
                <span className="muted small">
                  {(result.escalation as { companion: { relaying: { note: string } } }).companion.relaying.note}
                </span>
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
