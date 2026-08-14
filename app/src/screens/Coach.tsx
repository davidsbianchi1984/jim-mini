import { useEffect, useRef, useState } from "react";
import { api, type CoachCurriculum, type CoachStore, type Guidance,
         type SpecialistAnswer } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { hush, listen, primeVoice, say, type Listener } from "../speech";
import { useSession } from "../store";

const AREAS = ["mental_health", "health_fitness", "career", "relationships"];

export function Coach() {
  const { session } = useSession();
  const [area, setArea] = useState("mental_health");
  const [message, setMessage] = useState("I've been feeling stressed about work.");
  const [reply, setReply] = useState<Guidance | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fromSpecialist, setFromSpecialist] = useState<SpecialistAnswer | null>(null);
  const lang = visitorLang();

  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const recorder = useRef<Listener | null>(null);

  // The store the offline stack predicts from, and JIM's syllabus for it.
  const [knows, setKnows] = useState<CoachStore | null>(null);
  const [syllabus, setSyllabus] = useState<CoachCurriculum | null>(null);
  const [studied, setStudied] = useState<string | null>(null);
  const [studying, setStudying] = useState(false);

  async function loadKnows() {
    if (!session.userId || !session.userToken) return;
    try {
      setKnows(await api.coachStore(session.userId, session.userToken));
      setSyllabus(await api.coachCurriculum(session.userId, session.userToken));
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

  async function ask(text?: string) {
    const said = (text ?? message).trim();
    if (!session.userId || !session.userToken || !said) return;
    setBusy(true); setError(null);
    try {
      const r = await api.coach(session.userId, { area, message: said },
                                session.userToken);
      setReply(r); setFromSpecialist(null);
      // Talking to it should mean being answered out loud — a spoken
      // question answered only in text is half a conversation.
      if (r?.content && (text !== undefined || speaking)) {
        setSpeaking(true);
        say(r.content).finally(() => setSpeaking(false));
      }
    }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
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
      (text) => { setListening(false); setMessage(text); ask(text); },
      (msg) => { setListening(false); setError(msg); },
    );
  }

  return (
    <div className="screen">
      {(listening || speaking) && (
        <div className="voice-orb-veil" role="status"
             aria-label={listening ? "Listening" : "Speaking"}
             onClick={() => { if (listening) toggleMic(); else { hush(); setSpeaking(false); } }}>
          <div className={"voice-orb " + (listening ? "listening" : "speaking")} />
          <div className="voice-orb-label">
            {listening ? "listening — tap to stop" : "speaking — tap to hush"}
          </div>
        </div>
      )}
      <header className="screen-head">
        <h2>{tr("cch.title", lang)}</h2>
        <span className="muted small">{tr("cch.sub", lang)}</span>
      </header>
      <div className="card">
        <label>{tr("cch.area", lang)}
          <select value={area} onChange={(e) => setArea(e.target.value)}>
            {AREAS.map((a) => <option key={a}>{a}</option>)}
          </select>
        </label>
        <label>{tr("cch.mind", lang)}
          <textarea rows={3} value={message} onChange={(e) => setMessage(e.target.value)} />
        </label>
        <div className="voice-row">
          <button className="primary" onClick={() => ask()} disabled={busy || listening}>
            {busy ? "Thinking…" : "Ask the coach"}
          </button>
          <button className={listening ? "mic listening" : "mic"} onClick={toggleMic}
                  disabled={busy}>
            {listening ? "◉ Listening — tap to send" : "🎙 Talk to it"}
          </button>
          {reply?.content && (
            <button onClick={() => { if (speaking) { hush(); setSpeaking(false); }
                                     else { setSpeaking(true); say(reply.content).finally(() => setSpeaking(false)); } }}>
              {speaking ? "■ Stop" : "🔊 Read it aloud"}
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
              {reply.provenance.generated_by === "stub" ? "an online model" : reply.provenance.generated_by} —{" "}
              {reply.provenance.degraded_reason || "the model could not be reached"}.
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
