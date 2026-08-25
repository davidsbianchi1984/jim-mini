import { useEffect, useRef, useState } from "react";
import { api, type EngagedAct, type EngagedPermits, type EngagedReach,
         type EngagedSession, type EngagedStep,
         type StandingWatch } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { CONVERSATION_IDLE_MS, hush, heardNothing, listen, primeVoice,
         say, type Listener } from "../speech";
import { loadTheme } from "../theme";
import { useSession } from "../store";

/** The question the agent must ask before a topic leaves for a model —
 *  the reviewer's words, verbatim, the same sentence the system prompt
 *  carries (a test holds the two together). The screen watches for it so
 *  the choice can be two buttons and not just a typed word. */
const STUDY_ASK =
  "Shall I go online and research more into this topic and bring " +
  "back a copy for coach to hold and use while offline?";

/**
 * The Guardian you leave running.
 *
 * `Coach.tsx` is a turn: you ask, it answers, nothing is left holding. This
 * screen is a session — it stays open until you sign off, it can act on your
 * own records while it is open, and everything it did is a list you can take
 * back one row at a time.
 *
 * Three things this screen is responsible for that the backend cannot be:
 *
 * **Showing the reach before the session.** `engagedReach()` carries no token
 * because it is how somebody decides whether to open one at all. It renders
 * above the button, not behind a link — a list of what a thing may do to you
 * is not a detail view.
 *
 * **Never rendering an act as reversible when it is not.** `reversible` and
 * `irreversible_because` are two fields for a reason: an act that acted and
 * can no longer be taken back is a real third state, and `!reversible` alone
 * would tell somebody their journal entry had left the app.
 *
 * **Making sign-off a handover rather than a close.** The topics field is on
 * the sign-off card, filled in before the button, because the whole promise
 * is that leaving does not mean being unwatched.
 *
 * **Putting the switches next to the reach.** The permits card is the same
 * list as the reach card with toggles on it, and it sits in the same place —
 * because "what it may do" and "what I have let it do" are one question with
 * two answers, and a product that showed them on two screens would be the
 * menu problem this feature exists to answer.
 */
export function Engaged() {
  const { session } = useSession();
  const lang = visitorLang();
  const uid = session.userId;
  const token = session.userToken;

  const [reach, setReach] = useState<EngagedReach | null>(null);
  const [permits, setPermits] = useState<EngagedPermits | null>(null);
  const [live, setLive] = useState<EngagedSession | null>(null);
  const [acts, setActs] = useState<EngagedAct[]>([]);
  const [watching, setWatching] = useState<StandingWatch[]>([]);
  const [said, setSaid] = useState("");
  const [steps, setSteps] = useState<EngagedStep[]>([]);
  const [provenance, setProvenance] = useState<
    { generated_by: string; degraded: boolean; degraded_reason: string | null }
    | null>(null);
  const [topics, setTopics] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const foot = useRef<HTMLDivElement | null>(null);

  // The standing voice conversation — the same loop Coach and Talk carry,
  // on the screen where somebody asks for the look or sends the agent out
  // for knowledge. Field reality: this session gets talked to, and it was
  // the one conversational surface still requiring thumbs.
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [level, setLevel] = useState(0);
  const recorder = useRef<Listener | null>(null);
  const talking = useRef(false);
  const round = useRef(0);
  // Interrupting is a turn: the mic is open while the reply plays.
  // `sayGen` orphans a hushed reply's cleanup so the orb does not
  // flicker off under the interruption's own thinking; `saying` keeps
  // the idle exit from closing a reply still being said.
  const sayGen = useRef(0);
  const saying = useRef(false);
  const lastHeard = useRef(0);
  useEffect(() => { void primeVoice(); }, []);

  useEffect(() => {
    api.engagedReach().then(setReach).catch(() => { /* the card stands */ });
  }, []);

  async function refresh() {
    if (!uid || !token) return;
    try {
      const s = await api.engaged(uid, token);
      setLive(s);
      setActs(await api.engagedActs(uid, token));
      // Read from the watch list rather than the session's copy of it. The
      // card below shows what is being watched for whether or not anybody is
      // engaged — that is the whole point of a *standing* watch — and taking
      // it from the session would have left it stale the moment one closed.
      setWatching(await api.engagedWatches(uid, token));
      setPermits(await api.engagedPermits(uid, token));
      // "Make it black and white" lands as set_appearance server-side;
      // re-applying here is what makes the room change color in the same
      // breath as the reply that says it did.
      void loadTheme(uid, token);
    } catch (e) { setError((e as Error).message); }
  }

  async function flip(area: string, granted: boolean) {
    if (!uid || !token) return;
    setBusy(true); setError(null);
    try {
      await api.engagedSetPermit(uid, area, { granted }, token);
      // Re-read rather than patching the row in place: a grant is the sort of
      // thing a person double-checks, and a screen that showed its own guess
      // at the new state would be showing them their click, not the record.
      setPermits(await api.engagedPermits(uid, token));
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }
  useEffect(() => { refresh(); }, [uid]);

  // A session that says it stays open until you sign off has to still be
  // there when the transcript is long — scrolling to the newest turn is that
  // promise kept at the size where it stops being obvious.
  useEffect(() => { foot.current?.scrollIntoView({ block: "end" }); },
            [live?.turns?.length, steps.length]);

  async function engage() {
    if (!uid || !token) return;
    setBusy(true); setError(null);
    try {
      setLive(await api.engage(uid, { area: "personal_growth" }, token));
      await refresh();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function speak(text?: string) {
    const message = (text ?? said).trim();
    if (!uid || !token || !message) return;
    setBusy(true); setError(null); setNote(null);
    try {
      const turn = await api.engagedTurn(uid, { message }, token);
      setSteps(turn.did || []);
      setProvenance(turn.provenance);
      setSaid("");
      if (turn.stopped) setNote(turn.stopped);
      await refresh();
      // The same contract as Coach and Talk: a spoken question is answered
      // out loud, the purple orb holds for the whole reply, and then the
      // microphone opens again — with the idle clock restarted, so a long
      // answer never eats into the person's two minutes.
      if (turn.reply && (talking.current || speaking)) {
        setSpeaking(true);
        // The microphone opens WITH the voice: an interruption hushes
        // the reply and becomes the next turn.
        if (talking.current) { lastHeard.current = Date.now(); void hear(); }
        const s = ++sayGen.current;
        saying.current = true;
        say(turn.reply).finally(() => {
          saying.current = false;
          if (s === sayGen.current) setSpeaking(false);
          if (talking.current) lastHeard.current = Date.now();
        });
      } else {
        setSpeaking(false);
        if (talking.current) { lastHeard.current = Date.now(); void hear(); }
      }
    } catch (e) {
      talking.current = false;
      setError((e as Error).message); setSpeaking(false);
    }
    finally { setBusy(false); }
  }

  /** One turn of listening — Coach.tsx's loop, verbatim in shape: quiet
   *  re-opens the microphone, two quiet minutes bow out, a real refusal
   *  ends the conversation with its honest sentence. */
  async function hear() {
    const g = ++round.current;
    setListening(true);
    recorder.current = await listen(
      (text) => {
        if (g !== round.current) return; // the person already left
        sayGen.current++;
        hush();
        lastHeard.current = Date.now();
        setListening(false); setSpeaking(true);
        setSaid(text); void speak(text);
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

  async function undo(act: EngagedAct) {
    if (!uid || !token) return;
    setBusy(true); setError(null);
    try {
      await api.engagedUndo(uid, act.id, token);
      await refresh();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function signOff() {
    if (!uid || !token) return;
    setBusy(true); setError(null);
    try {
      const out = await api.engagedSignOff(uid, {
        topics: topics.split("\n").map((l) => l.trim()).filter(Boolean),
      }, token);
      setWatching(out.watches || []);
      setTopics(""); setSteps([]); setProvenance(null);
      await refresh();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function keepWatching(topic: string) {
    if (!uid || !token || !topic.trim()) return;
    try {
      await api.engagedWatch(uid, { topic: topic.trim() }, token);
      await refresh();
    } catch (e) { setError((e as Error).message); }
  }

  async function stopWatching(watch: StandingWatch) {
    if (!uid || !token) return;
    try {
      await api.engagedClearWatch(uid, watch.id, token);
      await refresh();
    } catch (e) { setError((e as Error).message); }
  }

  const open = !!live?.engaged;

  return (
    <section className="screen">
      {(listening || speaking) && (
        <div className="voice-orb-veil" role="status"
             aria-label={listening ? "Listening" : "Speaking"}
             onClick={exitTalk}>
          <div className={"voice-orb-holder" + (speaking ? " speaking" : "")}>
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
      <h2>{tr("engaged.title", lang)}</h2>
      <p className="muted">{tr("engaged.blurb", lang)}</p>

      {error && <div className="error">{error}</div>}

      {/* What it may do to you, before you let it near anything. */}
      {reach && (
        <div className="card">
          <h3>{tr("engaged.reach.title", lang)}</h3>
          <p className="muted small">{tr("engaged.reach.blurb", lang)}</p>
          <ul className="plain">
            {reach.can.map((c) => (
              <li key={c.name}>
                <span className={c.acts ? "chip warn" : "chip"}>
                  {/* Written as two literal lookups rather than one call on a
                      ternary: the console's dead-key guard reads literal
                      arguments, and a key reached only through an expression
                      reads to it as translated-and-never-used. */}
                  {c.acts ? tr("engaged.reach.acts", lang)
                          : tr("engaged.reach.reads", lang)}
                </span>{" "}
                {c.says}
                {c.irreversible_because && (
                  <em className="danger small">
                    {" — " + tr("engaged.reach.forever", lang)}
                  </em>
                )}
              </li>
            ))}
          </ul>
          <p className="muted small">
            {tr("engaged.reach.ceilings", lang)
               .replace("{steps}", String(reach.tools_per_turn))
               .replace("{acts}", String(reach.acts_per_session))}
          </p>
        </div>
      )}

      {/* The switches, beside the reach. Signed-in only, because a grant
          needs somebody to give it — the card above is the catalogue and
          this one is the answer to "and what have I let it do?". */}
      {permits && (
        <div className="card">
          <h3>{tr("permits.title", lang)}</h3>
          <p className="muted small">{tr("permits.blurb", lang)}</p>
          {permits.groups.map((a) => (
            <div key={a.area} className="row">
              <div style={{ flex: 1 }}>
                <strong>{tr(`permits.area.${a.area}`, lang)}</strong>
                <div className="muted small">{a.says}</div>
                {a.decided_at && (
                  <div className="muted small">
                    {(a.granted ? tr("permits.on.since", lang)
                                : tr("permits.off.since", lang))
                      .replace("{when}", a.decided_at.slice(0, 10))}
                  </div>
                )}
              </div>
              {/* The word beside the switch is what it is *now*, never what
                  pressing it would do. A button labelled with its own effect
                  and a button labelled with the current state look identical
                  and mean opposite things. */}
              <span className={a.granted ? "chip" : "chip warn"}>
                {a.granted ? tr("permits.on", lang) : tr("permits.off", lang)}
              </span>
              <button disabled={busy}
                      onClick={() => flip(a.area, !a.granted)}>
                {a.granted ? tr("permits.switch.off", lang)
                           : tr("permits.switch.on", lang)}
              </button>
            </div>
          ))}
          <p className="muted small">{permits.note}</p>
        </div>
      )}

      {/* The session itself. */}
      <div className="card">
        <h3>{open ? tr("engaged.open.title", lang)
                  : tr("engaged.closed.title", lang)}</h3>
        {!open && (
          <>
            <p className="muted small">{tr("engaged.closed.blurb", lang)}</p>
            <button className="primary" disabled={busy} onClick={engage}>
              {tr("engaged.engage", lang)}
            </button>
          </>
        )}

        {open && (
          <>
            <div className="transcript">
              {(live?.turns || []).map((turn, i) => (
                <p key={i} className={turn.role === "user" ? "said" : "heard"}>
                  <strong>
                    {turn.role === "user" ? tr("engaged.you", lang)
                                          : tr("engaged.jim", lang)}
                  </strong>{" "}
                  {turn.content}
                </p>
              ))}
              <div ref={foot} />
            </div>

            {/* What it did this turn, under the reply where it can be
                checked — an assistant that edits something and then
                describes the edit in prose is asking to be believed. */}
            {steps.length > 0 && (
              <ul className="steps">
                {steps.map((s, i) => (
                  <li key={i}>
                    {s.refused
                      ? <span className="danger">
                          {tr("engaged.step.refused", lang)} {s.tool}
                        </span>
                      : <>
                          <span className="chip">{s.status_code}</span>{" "}
                          {s.says || s.tool}
                          {s.acts && !s.reversible && (
                            <em className="danger small">
                              {" — " + tr("engaged.reach.forever", lang)}
                            </em>
                          )}
                        </>}
                  </li>
                ))}
              </ul>
            )}

            {note && <div className="warn">{tr(`refusal.${note}`, lang)}</div>}

            {/* Who actually answered. The same disclosure Coach carries: a
                canned fallback presented as the model somebody chose is the
                one lie this product cannot afford. */}
            {provenance?.degraded && (
              <div className="degraded">
                {tr("engaged.degraded", lang)
                   .replace("{who}", provenance.generated_by)}
                {provenance.degraded_reason
                  ? ` — ${provenance.degraded_reason}` : ""}
              </div>
            )}

            {/* The reviewer's yes/no, as buttons. The agent is held to the
                verbatim question by its prompt and the round's test, so the
                screen can recognize the moment and offer the choice — and
                in voice mode the person can simply say it instead. */}
            {(() => {
              const last = (live?.turns || []).slice(-1)[0];
              return last && last.role !== "user"
                && last.content.includes(STUDY_ASK);
            })() && (
              <div className="row">
                <button className="primary" disabled={busy}
                        onClick={() => speak("yes")}>
                  {tr("engaged.study.yes", lang)}
                </button>
                <button disabled={busy} onClick={() => speak("no")}>
                  {tr("engaged.study.no", lang)}
                </button>
              </div>
            )}

            <textarea rows={3} value={said}
                      placeholder={tr("engaged.say.hint", lang)}
                      onChange={(e) => setSaid(e.target.value)} />
            <button className="primary" disabled={busy || !said.trim()}
                    onClick={() => speak()}>
              {tr("engaged.say", lang)}
            </button>
            <button className={listening ? "mic listening" : "mic"}
                    onClick={toggleMic}
                    aria-pressed={listening}>
              {listening ? tr("cch.listening", lang) : tr("cch.talk", lang)}
            </button>
          </>
        )}
      </div>

      {/* The undo trail. Shown whether or not a session is open, because the
          thing somebody wants to take back is usually noticed later. */}
      <div className="card">
        <h3>{tr("engaged.trail.title", lang)}</h3>
        <p className="muted small">{tr("engaged.trail.blurb", lang)}</p>
        {acts.length === 0 && (
          <p className="muted">{tr("engaged.trail.none", lang)}</p>
        )}
        <ul className="plain">
          {acts.map((a) => (
            <li key={a.id}>
              {a.says}{" "}
              {a.undone_at ? (
                <span className="chip">{tr("engaged.trail.undone", lang)}</span>
              ) : a.reversible ? (
                <button disabled={busy} onClick={() => undo(a)}>
                  {tr("engaged.trail.undo", lang)}
                </button>
              ) : (
                <em className="danger small">
                  {tr("engaged.trail.forever", lang)}
                </em>
              )}
            </li>
          ))}
        </ul>
      </div>

      {/* Signing off, and what stays behind. */}
      {open && (
        <div className="card">
          <h3>{tr("engaged.off.title", lang)}</h3>
          <p className="muted small">{tr("engaged.off.blurb", lang)}</p>
          <textarea rows={3} value={topics}
                    placeholder={tr("engaged.off.hint", lang)}
                    onChange={(e) => setTopics(e.target.value)} />
          <button disabled={busy} onClick={signOff}>
            {tr("engaged.off", lang)}
          </button>
        </div>
      )}

      <div className="card">
        <h3>{tr("engaged.watch.title", lang)}</h3>
        <p className="muted small">{tr("engaged.watch.blurb", lang)}</p>
        {watching.length === 0 && (
          <p className="muted">{tr("engaged.watch.none", lang)}</p>
        )}
        <ul className="plain">
          {watching.map((w) => (
            <li key={w.id}>
              {w.topic}{" "}
              <button onClick={() => stopWatching(w)}>
                {tr("engaged.watch.stop", lang)}
              </button>
            </li>
          ))}
        </ul>
        <input placeholder={tr("engaged.watch.hint", lang)}
               onKeyDown={(e) => {
                 if (e.key === "Enter") {
                   keepWatching((e.target as HTMLInputElement).value);
                   (e.target as HTMLInputElement).value = "";
                 }
               }} />
      </div>
    </section>
  );
}
