import { useEffect, useRef, useState } from "react";
import { putAway, whenPutAway } from "./away";
import { t as tr, visitorLang } from "./l10n";
import { CONVERSATION_IDLE_MS, heardNothing, hush, listen, say,
         type Listener } from "./speech";
import { onWalk, stopWalking, walking, type Walking } from "./walk";

/**
 * The conversation you took with you.
 *
 * Mounted once, beside Help and the Guardian's lights, above the tab switch,
 * so it outlives the screen it started on. Every other ear in this console
 * is torn down when its screen unmounts — correctly, because a microphone
 * left open on a screen that no longer exists is a recording indicator
 * nobody can account for. This one is the exception, and it earns the
 * exception by being pressed for: nothing starts it but a button, it says on
 * screen which of listening, answering and stopped it is, and the way to end
 * it is the first control on the strip.
 *
 *     asked     is the microphone open
 *     mattered  does the person know, and can they close it
 *
 * ## The turn is `speech.ts`'s, not a second copy of one
 *
 * `listen` already decides between the service and the device recogniser,
 * asks the connected earbud for its microphone by name, ends a turn on two
 * and a half seconds of quiet, refuses to transcribe a recording the
 * analyser never heard a voice in, and reports being put away as its own
 * failure rather than as silence. A strip with its own recogniser would
 * have none of that and would drift from the two screens it was carrying.
 *
 * ## Being put away, and a correction
 *
 * This component shipped saying it could not survive being put away, and
 * that a minimised browser was a native shell's problem. That was half
 * right and the wrong half was load-bearing.
 *
 * `away.ts` is correct that a backgrounded page has its *recogniser* ended
 * by the browser. It is not correct about `getUserMedia`: on a desktop and
 * on Android an open capture keeps the tab alive, keeps recording while the
 * window is minimised, and makes the browser show its own recording
 * indicator the whole time. The two ways this console can hear behave
 * oppositely when the page goes away, and the first draft guarded them as
 * though they behaved the same.
 *
 *     asked     does a hidden page stop hearing
 *     mattered  which of the two ways of hearing was it using
 *
 * So the strip now asks `speech.ts` for the path that survives, by name,
 * and a deployment with no transcription service is told plainly that this
 * cannot be carried rather than being handed a microphone that will hear
 * nothing. Being put away is no longer a reason to stop — it is a fact the
 * strip states, because a person who minimised the window on purpose still
 * deserves to know the microphone is open.
 *
 * ## And the platform that correction did not cover
 *
 * The paragraph above once ended "the same bargain iOS makes with its
 * orange dot", which is true of a native iOS application and false of a
 * Safari page. iOS Safari suspends the whole page the moment you leave it,
 * capture included, and says nothing on the way out — a field report walked
 * on an iPhone, swiped up to the home screen, came back, and found the
 * conversation had stopped in silence.
 *
 *     asked     which of the two ways of hearing was it using
 *     mattered  does the platform let either of them run out there
 *
 * The sentence was not merely wrong; it named the platform that breaks the
 * rule as the example that proves it, which is why the belief felt settled.
 * Nothing on a page can prevent the suspension, so the strip does not try:
 * it asks its listener `live()` on the way back and says the microphone
 * stopped when it did. See the effect below.
 */
export function WalkAlong() {
  const [who, setWho] = useState<Walking | null>(walking());
  const [heard, setHeard] = useState("");
  const [said, setSaid] = useState("");
  // Who answered the last turn. Not an error state — an answer
  // from what is stored here is an answer — but a person hearing
  // it should know it was not the model they picked.
  const [offline, setOffline] = useState(false);
  const [trouble, setTrouble] = useState("");
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [asleep, setAsleep] = useState(putAway());
  const rec = useRef<Listener | null>(null);
  const round = useRef(0);
  const lastHeard = useRef(Date.now());
  const lang = visitorLang();

  useEffect(() => onWalk(setWho), []);

  // The page going away is noted and not acted on. The recording path
  // survives it on a desktop and on Android, so closing the ear here would
  // be this component inventing a failure the browser did not have — and
  // coming back does not reopen anything either, because nothing was
  // closed.
  //
  // ## And what a phone did to that
  //
  // A field report, from an iPhone: walk, swipe up to the home screen, come
  // back to Safari, and the conversation had stopped without a word. iOS
  // Safari suspends the whole page the moment you leave it, capture and
  // all — the survival above is a desktop fact and an Android fact, and on
  // iOS it is simply false. Nothing here could have known that in advance
  // and it does not try to; what it must do is notice on the way back.
  //
  //     asked     did the capture survive being put away
  //     mattered  does the strip find out when it did not
  //
  // So returning asks the listener whether it is really still open, and
  // says it stopped when it is not. Stopping without a word is the failure
  // this whole component is written against, and a platform doing the
  // stopping is no excuse for going on drawing a microphone that is shut.
  // The ear is not reopened: a microphone that restarts itself because a
  // tab regained focus is one nobody pressed for.
  useEffect(() => whenPutAway(
    () => setAsleep(true),
    () => {
      setAsleep(false);
      // After the browser has finished waking the page, not during: on
      // iOS the recorder's own state settles as the tab resumes, and
      // reading it in the same tick as the visibility event catches it
      // mid-answer.
      window.setTimeout(() => {
        if (!walking() || !rec.current) return;
        if (rec.current.live()) return;
        close();
        setTrouble(tr("walk.away.stopped", lang));
      }, 0);
    }), []);

  useEffect(() => {
    if (!who) { close(); return; }
    setTrouble("");
    lastHeard.current = Date.now();
    void hear(who);
    return close;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [who?.shownName]);

  /** Leave: nothing in flight answers, nothing re-opens, the voice stops. */
  function close() {
    round.current += 1;
    rec.current?.stop();
    rec.current = null;
    hush();
    setListening(false);
    setSpeaking(false);
  }

  /** One turn of listening. Quiet with nothing said is not a failure in a
   *  standing conversation — the microphone simply opens again — until the
   *  idle window closes a conversation nobody is in. The same rule and the
   *  same number as Talk and Coach, from the same constant, because a strip
   *  that bowed out on its own schedule would be a third answer to a
   *  question the console has already answered twice. */
  async function hear(w: Walking) {
    const g = ++round.current;
    setListening(true);
    rec.current = await listen(
      (text) => {
        if (g !== round.current) return;
        lastHeard.current = Date.now();
        setListening(false);
        setHeard(text);
        void turnTaken(w, g, text);
      },
      (msg) => {
        if (g !== round.current) return;
        if (heardNothing(msg)) {
          if (Date.now() - lastHeard.current >= CONVERSATION_IDLE_MS) {
            close();
            return;
          }
          void hear(w);
          return;
        }
        // Everything else is a real failure, and the strip says which one
        // in the sentence `speech.ts` wrote for it. A strip that reported
        // a refused microphone as "not listening" would be the silence-and
        // -deafness confusion `away.ts` exists about, one component along.
        setListening(false);
        setTrouble(msg);
      },
      undefined,
      // By name, not by hope. This asks for the recording path — the one
      // that survives a minimised window — and refuses rather than falling
      // back to the recogniser that would die out there without saying so.
      { carryWhenAway: true },
    );
  }

  async function turnTaken(w: Walking, g: number, message: string) {
    setSpeaking(true);
    try {
      const answer = await w.take(message);
      if (g !== round.current) return;
      setSaid(answer.text);
      setOffline(Boolean(answer.offline));
      setHeard("");
      if (answer.text) await say(answer.text);
    } catch {
      if (g !== round.current) return;
      setSaid(tr("walk.lost", lang));
    } finally {
      if (g === round.current) {
        setSpeaking(false);
        lastHeard.current = Date.now();
        void hear(w);
      }
    }
  }

  if (!who) return null;
  return (
    <div className="walk-strip" role="status" aria-live="polite">
      <button className="walk-end" onClick={() => { close(); stopWalking(); }}>
        {tr("walk.end", lang)}
      </button>
      <span className="walk-who">{who.shownName}</span>
      <span className="muted small walk-state">
        {speaking ? tr("walk.speaking", lang)
                  : listening ? (asleep ? tr("walk.aloft", lang)
                                        : tr("walk.listening", lang))
                              : tr("walk.quiet", lang)}
      </span>
      {/* Who answered, when it was not the model. Between the state and
          the words, because it qualifies the words rather than the ear. */}
      {offline && !trouble && (
        <span className="muted small walk-offline">
          {tr("walk.offline", lang)}
        </span>
      )}
      {trouble && <span className="walk-trouble">{trouble}</span>}
      {(heard || said) && !trouble && (
        <span className="walk-words">{heard || said}</span>
      )}
      {!listening && !speaking && !asleep && (
        <button className="walk-again"
                onClick={() => { setTrouble(""); void hear(who); }}>
          {tr("walk.again", lang)}
        </button>
      )}
    </div>
  );
}
