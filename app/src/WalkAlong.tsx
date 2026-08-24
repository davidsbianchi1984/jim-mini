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
 * ## What it does not survive
 *
 * Being put away. `away.ts` is explicit: a backgrounded page has its timers
 * throttled, its audio suspended and its recogniser ended by the browser,
 * and none of that arrives as an error. So the strip asks the same two
 * questions every other ear here asks — am I away, tell me when that changes
 * — and says it has stopped rather than going on claiming to listen. That is
 * the whole of the honesty available on the web: walking is inside this
 * application, and a minimised browser is a native shell's problem.
 */
export function WalkAlong() {
  const [who, setWho] = useState<Walking | null>(walking());
  const [heard, setHeard] = useState("");
  const [said, setSaid] = useState("");
  const [trouble, setTrouble] = useState("");
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [asleep, setAsleep] = useState(putAway());
  const rec = useRef<Listener | null>(null);
  const round = useRef(0);
  const lastHeard = useRef(Date.now());
  const lang = visitorLang();

  useEffect(() => onWalk(setWho), []);

  // The page going away closes the ear and says so. Coming back does not
  // reopen it: a microphone that restarts itself because a tab regained
  // focus is one nobody pressed for, which is the line this whole component
  // is on the right side of.
  useEffect(() => whenPutAway(
    () => { setAsleep(true); close(); },
    () => setAsleep(false)), []);

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
    );
  }

  async function turnTaken(w: Walking, g: number, message: string) {
    setSpeaking(true);
    try {
      const text = await w.take(message);
      if (g !== round.current) return;
      setSaid(text);
      setHeard("");
      if (text) await say(text);
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
        {asleep ? tr("walk.asleep", lang)
                : speaking ? tr("walk.speaking", lang)
                           : listening ? tr("walk.listening", lang)
                                       : tr("walk.quiet", lang)}
      </span>
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
