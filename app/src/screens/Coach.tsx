import { useEffect, useRef, useState } from "react";
import { api, type CoachCurriculum, type CoachStore, type ErrandLedger,
         type Guidance, type LookoutList, type LookoutPage,
         type NoticeLedger, type SpecialistAnswer } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { CONVERSATION_IDLE_MS, hush, heardNothing, listen, primeVoice,
         say, type Listener } from "../speech";
import { useSession } from "../store";

const AREAS: import("../api").GoalArea[] =
  ["mental_health", "health_fitness", "career", "relationships"];

export function Coach() {
  const { session } = useSession();
  const [area, setArea] = useState<import("../api").GoalArea>("mental_health");
  const [message, setMessage] = useState("I've been feeling stressed about work.");
  const [reply, setReply] = useState<Guidance | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fromSpecialist, setFromSpecialist] = useState<SpecialistAnswer | null>(null);
  const lang = visitorLang();

  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [level, setLevel] = useState(0);
  const recorder = useRef<Listener | null>(null);
  // The conversation stands until the person leaves it. A field report:
  // the exchange worked perfectly once, then the spoken reply ended and
  // the veil dropped them back to the screen — a conversation that hangs
  // up after every answer. `talking` holds the loop open (refs, because
  // the listen/say callbacks outlive their render); `round` stamps each
  // listen so an exit tap orphans any transcription still in flight.
  const talking = useRef(false);
  const round = useRef(0);
  // When something was last actually heard. Quiet re-opens the microphone,
  // but a conversation nobody has spoken into for two minutes ends on its
  // own — quietly, because leaving a room empty is not an error.
  const lastHeard = useRef(0);
  // The microphone is open while the reply plays now — interrupting is a
  // turn. `sayGen` orphans a hushed reply's cleanup so the purple orb
  // does not flicker off under the interruption's own thinking, and
  // `saying` keeps the idle exit from closing a reply still being said.
  const sayGen = useRef(0);
  const saying = useRef(false);

  // The store the offline stack predicts from, and JIM's syllabus for it.
  const [knows, setKnows] = useState<CoachStore | null>(null);
  const [syllabus, setSyllabus] = useState<CoachCurriculum | null>(null);
  const [studied, setStudied] = useState<string | null>(null);
  const [studying, setStudying] = useState(false);
  // The unattended pass — what it went and learned without being asked, and
  // what is left to spend today.
  const [ledger, setLedger] = useState<ErrandLedger | null>(null);
  const [running, setRunning] = useState(false);
  // The situational half of the same ladder: what the coach noticed during
  // the day, and which half of it settled each one.
  const [noticed, setNoticed] = useState<NoticeLedger | null>(null);
  const [handling, setHandling] = useState(false);
  // The lookout: pages the vault re-reads on their own schedule.
  const [watches, setWatches] = useState<LookoutList | null>(null);
  const [watchUrl, setWatchUrl] = useState("");
  const [watchHours, setWatchHours] = useState("24");
  const [capture, setCapture] = useState<LookoutPage | null>(null);

  async function loadKnows() {
    if (!session.userId || !session.userToken) return;
    try {
      setKnows(await api.coachStore(session.userId, session.userToken));
      setSyllabus(await api.coachCurriculum(session.userId, session.userToken));
      setLedger(await api.errands(session.userId, session.userToken));
      setNoticed(await api.noticed(session.userId, session.userToken));
      setWatches(await api.lookouts(session.userId, session.userToken));
    } catch { /* the ask card stands on its own */ }
  }
  useEffect(() => { loadKnows(); }, [session.userId]);
  // Learn which path the microphone should take before anybody taps it.
  // Asking at tap time is what used to spend the user gesture Safari
  // requires for the device recogniser. See `listen` in ../speech.
  useEffect(() => { void primeVoice(); }, []);

  async function study(topic?: string, sArea?: string) {
    if (!session.userId || !session.userToken) return;
    setStudying(true); setError(null);
    try {
      const r = await api.coachStudy(session.userId,
        { topic, area: sArea }, session.userToken);
      setStudied(r.studied);
      await loadKnows();
    } catch (e) { setError((e as Error).message); }
    finally { setStudying(false); }
  }

  /** Let it go and study, unattended, whatever the coach could not answer.
   *  Refused without the permit and again once the day is spent — two
   *  different sentences, shown as they arrive rather than flattened. */
  async function runErrands() {
    if (!session.userId || !session.userToken) return;
    setRunning(true); setError(null);
    try {
      await api.runErrands(session.userId, session.userToken);
      await loadKnows();
    } catch (e) { setError((e as Error).message); }
    finally { setRunning(false); }
  }

  /** Deal with what the coach noticed during the day.
   *
   * No budget guard on the button, unlike the errands one beside it: this
   * pass is worth running on a spent day, because the offline coach settles
   * what it can for nothing and the backend reports what waits for tomorrow
   * rather than refusing the lot.
   */
  async function runNoticed() {
    if (!session.userId || !session.userToken) return;
    setHandling(true); setError(null);
    try {
      await api.runNoticed(session.userId, session.userToken);
      await loadKnows();
    } catch (e) { setError((e as Error).message); }
    finally { setHandling(false); }
  }

  async function ask(text?: string) {
    const said = (text ?? message).trim();
    if (!session.userId || !session.userToken || !said) return;
    setBusy(true); setError(null);
    try {
      const r = await api.coach(session.userId, { area, message: said },
                                session.userToken);
      setReply(r); setFromSpecialist(null);
      // Talking to it should mean being answered out loud — a spoken
      // question answered only in text is half a conversation. `say`
      // resolves when the speaking ends, so the purple orb stays for the
      // whole answer — and then the microphone opens again, because a
      // conversation is not over until the person leaves it.
      if (r?.content && (talking.current || speaking)) {
        setSpeaking(true);
        // The microphone opens WITH the voice, not after it: a long or
        // off-target answer should be stoppable with words, so an
        // interruption hushes the reply and becomes the next turn.
        if (talking.current) { lastHeard.current = Date.now(); void hear(); }
        const s = ++sayGen.current;
        saying.current = true;
        say(r.content).finally(() => {
          saying.current = false;
          if (s === sayGen.current) setSpeaking(false);
          if (talking.current) lastHeard.current = Date.now();
        });
      } else {
        setSpeaking(false);
        if (talking.current) { lastHeard.current = Date.now(); void hear(); }
      }
    }
    catch (e) {
      talking.current = false;
      setError((e as Error).message); setSpeaking(false);
    }
    finally { setBusy(false); }
  }

  /** One turn of listening. The orb goes green→purple in one motion and
   *  stays up through the thinking and the whole spoken answer — a veil
   *  that blinks away between hearing and answering reads as the
   *  conversation dropping. Quiet with nothing said is not a failure in
   *  a standing conversation: the microphone simply opens again. */
  async function hear() {
    const g = ++round.current;
    setListening(true);
    recorder.current = await listen(
      (text) => {
        if (g !== round.current) return; // the person already left
        // Barging in is a turn: whatever is still being said stops the
        // moment something real was heard, and the orphaned cleanup must
        // not drop the orb under the new turn's thinking.
        sayGen.current++;
        hush();
        lastHeard.current = Date.now();
        setListening(false); setSpeaking(true);
        setMessage(text); ask(text);
      },
      (msg) => {
        if (g !== round.current) return;
        if (talking.current && heardNothing(msg)) {
          // Never bow out mid-reply: the idle clock only closes a room
          // where nobody — the person or the profile — is speaking.
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

  /** Leave the conversation: nothing in flight answers, nothing re-opens. */
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
  // microphone under a screen that no longer exists.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => () => exitTalk(), []);

  async function toggleMic() {
    if (listening) { exitTalk(); return; }
    setError(null);
    talking.current = true;
    lastHeard.current = Date.now();
    await hear();
  }

  return (
    <div className="screen">
      {(listening || speaking) && (
        <div className="voice-orb-veil" role="status"
             aria-label={listening ? "Listening" : "Speaking"}
             onClick={exitTalk}>
          <div className={"voice-orb-holder" + (speaking ? " speaking" : "")}>
            {/* The audio-wave ring: the person's own voice level, drawn
                around the sphere while it listens — a still ring is a mic
                hearing silence, which is also worth seeing. */}
            <div className="voice-orb-ring"
                 style={{ transform: `scale(${1 + level * 0.45})`,
                          opacity: 0.3 + level * 0.7 }} />
            <div className={"voice-orb " + (speaking ? "speaking" : "listening")} />
          </div>
          <div className="voice-orb-label">
            {speaking ? tr("cch.speaking.hush", lang)
                      : tr("cch.listening.stop", lang)}
          </div>
        </div>
      )}
      <header className="screen-head">
        <h2>{tr("cch.title", lang)}</h2>
        <span className="muted small">{tr("cch.sub", lang)}</span>
      </header>
      <div className="card">
        <label>{tr("cch.area", lang)}
          <select value={area} onChange={(e) => setArea(e.target.value as import("../api").GoalArea)}>
            {AREAS.map((a) => <option key={a}>{a}</option>)}
          </select>
        </label>
        <label>{tr("cch.mind", lang)}
          <textarea rows={3} value={message} onChange={(e) => setMessage(e.target.value)} />
        </label>
        <div className="voice-row">
          <button className="primary" onClick={() => ask()} disabled={busy || listening}>
            {busy ? tr("cch.thinking", lang) : tr("cch.ask", lang)}
          </button>
          <button className={listening ? "mic listening" : "mic"} onClick={toggleMic}
                  disabled={busy}>
            {listening ? tr("cch.listening", lang) : tr("cch.talk", lang)}
          </button>
          {reply?.content && (
            <button onClick={() => { if (speaking) { hush(); setSpeaking(false); }
                                     else { setSpeaking(true); say(reply.content).finally(() => setSpeaking(false)); } }}>
              {speaking ? tr("cch.stop", lang) : tr("cch.readaloud", lang)}
            </button>
          )}
        </div>
        {error && <div className="error">⚠ {error}</div>}
      </div>
      {/* role=status + aria-live: a screen reader is told the coach's
          answer arrived, instead of the card appearing silently. */}
      {reply?.content && (
        <div className="card guidance" role="status" aria-live="polite">
          <div className="guidance-src">{tr("cch.guidance", lang)
            .replace("{area}", area.replace("_", " "))}</div>
          <p>{reply.content}</p>
          {/* Who actually answered. When the model layer degraded, say so in
              amber — canned fallback text presented as the chosen model is a
              lie the user has no way to detect from the words alone. */}
          {reply.provenance?.degraded ? (
            <div className="degraded">
              {tr("cch.fallback", lang)}{" "}
              {reply.provenance.generated_by === "stub"
                ? tr("cch.prov.online", lang)
                : reply.provenance.generated_by} —{" "}
              {reply.provenance.degraded_reason
                || tr("cch.prov.unreached", lang)}.
            </div>
          ) : reply.provenance?.generated_by && reply.provenance.generated_by !== "stub" && (
            <div className="muted small">{tr("cch.answered", lang)
              .replace("{who}", String(reply.provenance.generated_by))}</div>
          )}

          {/* A specialist covers this area. An offer, not a send — what would
              cross is what the person just wrote, so the button is theirs to
              press and the note says so before they press it. */}
          {reply.specialist_offer?.available && !fromSpecialist && (
            <div className="spec-row">
              <div>
                <b>{reply.specialist_offer.label}</b>
                <div className="muted small">{reply.specialist_offer.note}</div>
              </div>
              <button disabled={busy} onClick={async () => {
                if (!session.userId || !session.userToken) return;
                setBusy(true); setError(null);
                try {
                  setFromSpecialist(await api.coachSpecialist(
                    session.userId, { area, message }, session.userToken));
                } catch (e) { setError((e as Error).message); }
                finally { setBusy(false); }
              }}>{tr("spec.ask", lang)}</button>
            </div>
          )}
        </div>
      )}

      {knows && (
        <div className="card">
          <b>{tr("cch.knows", lang)}</b>
          <div className="muted small">
            {tr("cch.knows.counts", lang)
              .replace("{pack}", String(knows.pack))
              .replace("{learned}", String(knows.excursions.length))
              .replace("{deposits}", String(knows.deposits.length))}
          </div>
          {syllabus && syllabus.suggested.length > 0 && (
            <>
              <div className="muted small" style={{ marginTop: 8 }}>
                <b>{tr("cch.study.head", lang)}</b>
              </div>
              {syllabus.suggested.map((s) => (
                <div key={s.topic} className="spec-row">
                  <div>
                    {s.topic}
                    <div className="muted small">{s.why}</div>
                  </div>
                  <button disabled={studying}
                          onClick={() => study(s.topic, s.area)}>
                    {tr("cch.study.go", lang)}
                  </button>
                </div>
              ))}
            </>
          )}
          {studied && (
            <div className="muted small">✓ {studied} — {tr("cch.study.done", lang)}</div>
          )}

          {/* The pass that runs without being pressed once it is allowed.
              The coach answers all day for nothing; this is what it calls
              when it could not, and calling costs — so the budget is shown
              beside the button rather than discovered in a refusal. */}
          {ledger && (
            <div style={{ marginTop: 10 }}>
              <div className="muted small">
                <b>{tr("err.head", lang)}</b>
              </div>
              <div className="muted small">
                {ledger.permitted
                  ? `${ledger.spent_today}/${ledger.daily} · ${tr("err.today", lang)}`
                  : tr("err.notallowed", lang)}
              </div>
              {ledger.permitted && (
                <button disabled={running || ledger.spent_today >= ledger.daily}
                        onClick={runErrands}>
                  {tr("err.go", lang)}
                </button>
              )}
              {ledger.errands.map((e) => (
                <div key={e.id} className="spec-row">
                  <div>
                    {e.topic}
                    <div className="muted small">{e.why}</div>
                    <div className="muted small">
                      {e.left_host ? tr("err.left", lang) : tr("err.stayed", lang)}
                      {e.redactions > 0 && ` · ${e.redactions} ${tr("err.redacted", lang)}`}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* The lookout: a page the vault re-reads on its schedule and
              re-seals in place — JIM never does the watching, and the
              capture stays in the tandem. Behind the same study permit
              as the errands above it. */}
          {watches && ledger?.permitted && (
            <div style={{ marginTop: 10 }}>
              <div className="muted small">
                <b>{tr("lkt.title", lang)}</b>
              </div>
              <div className="muted small">{tr("lkt.lead", lang)}</div>
              {!watches.readable && (
                <div className="muted small">{tr("lkt.unreadable", lang)}</div>
              )}
              <div className="row">
                <input value={watchUrl} placeholder={tr("lkt.url", lang)}
                       onChange={(e) => setWatchUrl(e.target.value)}
                       style={{ flex: 1 }} />
                <input value={watchHours} type="number" min={0.25} max={744}
                       aria-label={tr("lkt.hours", lang)}
                       onChange={(e) => setWatchHours(e.target.value)}
                       style={{ width: 72 }} />
                <button disabled={!watchUrl.trim() || !watchHours}
                        onClick={async () => {
                          if (!session.userId || !session.userToken) return;
                          try {
                            await api.plantLookout(session.userId,
                              watchUrl.trim(), Number(watchHours),
                              session.userToken);
                            setWatchUrl("");
                            setWatches(await api.lookouts(
                              session.userId, session.userToken));
                          } catch (e) { setError(String(e)); }
                        }}>
                  {tr("lkt.plant", lang)}
                </button>
              </div>
              {watches.lookouts.map((w) => (
                <div key={w.id} className="spec-row">
                  <div style={{ flex: 1 }}>
                    {w.url}
                    <div className="muted small">
                      {w.every_hours}
                      {w.status && ` · ${w.status}`}
                      {w.next_run_at && ` · ${w.next_run_at.slice(0, 16)}`}
                      {w.changed_at &&
                        ` · ${fill("lkt.changed", lang,
                                   { when: w.changed_at.slice(0, 10) })}`}
                      {w.trouble && (
                        <span className="error"> · {w.trouble}</span>
                      )}
                    </div>
                  </div>
                  <button onClick={async () => {
                    if (!session.userId || !session.userToken) return;
                    try {
                      setCapture(await api.lookoutPage(
                        session.userId, w.id, session.userToken));
                    } catch (e) { setError(String(e)); }
                  }}>
                    {tr("lkt.read", lang)}
                  </button>
                  <button className="danger" onClick={async () => {
                    if (!session.userId || !session.userToken) return;
                    try {
                      await api.dropLookout(session.userId, w.id,
                                            session.userToken);
                      setWatches(await api.lookouts(
                        session.userId, session.userToken));
                    } catch (e) { setError(String(e)); }
                  }}>
                    {tr("lkt.drop", lang)}
                  </button>
                </div>
              ))}
              {capture && (
                <div className="muted small">
                  <b>{capture.url}</b>
                  {capture.readable
                    ? ` · ${capture.fetched_at?.slice(0, 16)} · ${capture.chars}`
                    : ` · ${tr("lkt.nocapture", lang)}`}
                  {capture.changed_at &&
                    ` · ${fill("lkt.changed", lang,
                               { when: capture.changed_at.slice(0, 10) })}`}
                  {capture.text && (
                    <div style={{ whiteSpace: "pre-wrap", maxHeight: 160,
                                  overflow: "auto" }}>
                      {capture.text.slice(0, 2000)}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* The other half of the same ladder. That one is what the coach
              could not *answer*; this is what it could not *settle* — a
              situation rather than a question. Each row says which half
              dealt with it, because that difference is the whole product
              claim and it is invisible unless it is written down. */}
          {noticed && (
            <div style={{ marginTop: 10 }}>
              <div className="muted small">
                <b>{tr("ntc.head", lang)}</b>
              </div>
              {!noticed.settlement.permitted && (
                <div className="muted small">{tr("ntc.notallowed", lang)}</div>
              )}
              {noticed.settlement.permitted && (
                <>
                  {/* The number this whole ladder exists to move. Only once
                      something has actually been handled — `free_share` is
                      null before that, and a bare 0% would say the coach
                      settled none of them. */}
                  {noticed.settlement.free_share !== null && (
                    <div className="muted small">
                      {tr("ntc.free", lang)
                        .replace("{n}", String(noticed.settlement.settled_free))
                        .replace("{total}", String(
                          noticed.settlement.settled_free + noticed.settlement.settled_paid))}
                    </div>
                  )}
                  <button disabled={handling} onClick={runNoticed}>
                    {tr("ntc.go", lang)}
                  </button>
                  {/* Still there, and why: the day's turns are gone and the
                      coach could not settle these on its own. */}
                  {noticed.waiting.length > 0
                    && noticed.settlement.spent_today >= noticed.settlement.daily && (
                    <div className="muted small">{tr("ntc.waiting", lang)}</div>
                  )}
                </>
              )}
              {noticed.handled.map((n) => (
                <div key={n.id} className="spec-row">
                  <div>
                    {n.condition}
                    <div className="muted small">
                      {n.settled_by === "coach" ? tr("ntc.by.coach", lang)
                                                : tr("ntc.by.jim", lang)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {fromSpecialist && (
        <div className="card guidance" role="status" aria-live="polite">
          <div className="guidance-src">
            {fromSpecialist.specialist?.label || tr("spec.fallback", lang)} · {tr("spec.via", lang)}
          </div>
          {fromSpecialist.delivered ? (
            <p>{fromSpecialist.content}</p>
          ) : fromSpecialist.held_for_owner_approval ? (
            <div className="degraded">
              {tr("spec.held", lang)}
            </div>
          ) : (
            <div className="degraded">
              {fromSpecialist.reason}
              {fromSpecialist.note ? ` — ${fromSpecialist.note}` : ""}
            </div>
          )}
          {fromSpecialist.provenance && (
            <>
              <div className="muted small">{fromSpecialist.provenance.method}</div>
              <div className="muted small">
                {tr("spec.shared", lang)}: {fromSpecialist.provenance.shared}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
