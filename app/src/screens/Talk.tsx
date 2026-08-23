import { useEffect, useRef, useState } from "react";
import { api, type Guidance } from "../api";
import { t as tr, visitorLang, word } from "../l10n";
import { CONVERSATION_IDLE_MS, hush, hushAndReport, heardNothing, listen, primeVoice,
         say, type Listener } from "../speech";
import { useSession } from "../store";

/**
 * Talking to JIM, and reaching everything else from the same place.
 *
 * The console had twenty-four tiles and no front door. Every capability was
 * behind one of them, which meant knowing which — and a field report said
 * what the shape should be instead: a **composer** at the bottom (the pill,
 * the mic, Speak) and a **horizontal scrolling rail** of features above it.
 * Nothing behind them; an empty screen stays empty.
 *
 *     asked     pull up JIM when I press the mark
 *     mattered  the mark opened a permissions panel, and the conversation
 *               was behind a different tile
 *
 * ## What the rail is, and what it is not
 *
 * It is a **launcher for screens that already exist**, not a second place to
 * implement them. Every chip calls `go` with a tab id, and the screen that
 * opens is the same one the tile opened — the same code, the same guards.
 * A rail that reimplemented a card would be two copies of one rule, which is
 * how the two drift apart.
 *
 * So this screen owns exactly one capability of its own: asking JIM
 * something. Everything else it does is navigation.
 *
 * ## Why the attachment menu is short
 *
 * The composer's `+` was asked for with four entries: Camera, Photos, Files
 * and Link. Two of those have a screen behind them today — clinical capture
 * takes a photo or a video of the body, and the channel screen is the
 * microphone. **Files and Link do not**, and this codebase does not ship a
 * control that does nothing: the ingest route they need is the next round's
 * work, and the menu grows when the route lands rather than before it.
 */
export function Talk({ go }: {
  /** Open one of the console's existing screens. Ids are `App.tsx`'s tabs;
   *  typed as a string here so this screen does not need the union — the
   *  rail is a list of destinations, not a second definition of them. */
  go: (id: string) => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [said, setSaid] = useState("");
  const [reply, setReply] = useState<Guidance | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [plus, setPlus] = useState(false);
  // The microphone, for real — a field report pressed the mic on this
  // composer and was navigated to the channel screen: a mic that opens a
  // different room is a label, not a microphone. This one listens (five
  // seconds of silence sends, same as the coach's), and the orb stays up
  // from the end of the question through the whole spoken reply.
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [level, setLevel] = useState(0);
  const recorder = useRef<Listener | null>(null);
  // The conversation stands until the person leaves it (see Coach.tsx —
  // same loop, same reason): `talking` holds it open across the
  // listen/say callbacks, `round` stamps each listen so the exit tap
  // orphans a transcription still in flight.
  const talking = useRef(false);
  const round = useRef(0);
  // Interrupting is a turn: the mic is open while the reply plays.
  // `sayGen` orphans a hushed reply's cleanup so the orb does not
  // flicker off under the interruption's own thinking; `saying` keeps
  // the idle exit from closing a reply still being said.
  const sayGen = useRef(0);
  const saying = useRef(false);
  // When something was last actually heard — see Coach.tsx: a conversation
  // nobody has spoken into for two minutes ends on its own, quietly.
  const lastHeard = useRef(0);
  // How much of the last reply reached the person before they spoke over
  // it, held from the moment of the interruption until the turn it belongs
  // to is sent. Empty whenever nothing was interrupted, which is most turns.
  const cutOff = useRef("");
  useEffect(() => { void primeVoice(); }, []);

  const uid = session.userId;
  const token = session.userToken;

  /** The rail, in the order somebody reaches for them: the two that act in
   *  an emergency first, then the daily ones, then the record.
   *
   *  Each chip is a tab id and an icon, and its label is `talk.rail.<id>` —
   *  the destination named once. A separate `key` field beside the id would
   *  be a second list to keep in step with the first, and the way a chip
   *  ends up labelled for one screen and opening another. */
  const rail: { id: string; icon: string }[] = [
    { id: "safety", icon: "🆘" },
    { id: "channel", icon: "🎙" },
    { id: "attending", icon: "📷" },
    { id: "checkin", icon: "🌿" },
    { id: "meds", icon: "💊" },
    { id: "monitor", icon: "❤" },
    { id: "careteam", icon: "👥" },
    { id: "permits", icon: "🛡" },
    { id: "journal", icon: "📖" },
    { id: "held", icon: "🗄" },
    { id: "studio", icon: "🛠" },
  ];

  async function ask(text?: string) {
    const q = (text ?? said).trim();
    if (!uid || !token || !q) return;
    setBusy(true); setError(null);
    // A typed question interrupts too — see Coach.tsx for the same line and
    // the same reason.
    const cut = cutOff.current || hushAndReport(); cutOff.current = "";
    try {
      // `general` rather than a picked area: this is the front door, and
      // making somebody choose a category before they can type is the
      // menu problem this screen exists to answer. Coach's own screen
      // still offers the picker for somebody who wants it.
      const r = await api.coach(
        uid, { area: "general", message: q,
               ...(cut ? { cut_off_heard: cut } : {}) }, token);
      setReply(r);
      setSaid("");
      // A spoken question is answered out loud, the purple orb holds for
      // the whole reply — `say` resolves when the speaking ends — and
      // then the microphone opens again: a conversation is not over
      // until the person leaves it.
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
    } catch (e) {
      talking.current = false;
      setError(e instanceof Error ? e.message : String(e));
      setSpeaking(false);
    } finally {
      setBusy(false);
    }
  }

  /** One turn of listening. Quiet with nothing said is not a failure in
   *  a standing conversation: the microphone simply opens again. */
  async function hear() {
    const g = ++round.current;
    setListening(true);
    recorder.current = await listen(
      (text) => {
        if (g !== round.current) return; // the person already left
        sayGen.current++;
        // Barging in is a turn, and it is also a FACT about the answer
        // being barged in on: the reply is played piece by piece, so this
        // is the one moment the console can say how much of it landed.
        // Read before the stop, because after it there is nothing to read.
        cutOff.current = hushAndReport();
        lastHeard.current = Date.now();
        setListening(false); setSpeaking(true);
        setSaid(text); ask(text);
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

  if (!uid || !token) return <p>{tr("self.signin", lang)}</p>;

  return (
    <div className="talk">
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
      <div className="talk-body">
        {/* No empty state. Before the first answer this is blank space above
            the composer, which is what the composer is for. */}
        {reply && (
          <div className="card talk-reply">
            <p>{reply.content}</p>
            {reply.source && (
              <p className="muted small">{reply.source}</p>
            )}
          </div>
        )}
        {error && <div className="error">⚠ {error}</div>}
      </div>

      {/* The rail. `overflow-x: auto` with no wrap, so it scrolls sideways
          rather than becoming four rows of chips on a phone. */}
      <div className="talk-rail">
        {rail.map((c) => (
          <button key={c.id} className="talk-chip" onClick={() => go(c.id)}>
            <span aria-hidden="true">{c.icon}</span> {word("talk.rail", c.id, lang)}
          </button>
        ))}
      </div>

      <div className="talk-bar">
        {plus && (
          <div className="talk-plus" role="menu">
            {/* Field report: Camera and Photos pointed at the specialists
                screen — a menu that promises the camera roll and delivers
                a directory of clinicians. Both land on the camera card
                now (`#cam` scrolls the channel screen to it), which is
                where taking and importing a picture actually live, site
                vocabulary and consent included. */}
            <button role="menuitem" onClick={() => {
              setPlus(false); window.location.hash = "cam"; go("channel");
            }}>
              📷 {tr("talk.plus.camera", lang)}
            </button>
            <button role="menuitem" onClick={() => {
              setPlus(false); window.location.hash = "cam"; go("channel");
            }}>
              🖼 {tr("talk.plus.photos", lang)}
            </button>
            <button role="menuitem" onClick={() => { setPlus(false); go("channel"); }}>
              🎙 {tr("talk.plus.voice", lang)}
            </button>
          </div>
        )}
        <div className="talk-pill">
          <button className="talk-plusbtn" aria-label={tr("talk.plus", lang)}
                  aria-expanded={plus} onClick={() => setPlus(!plus)}>+</button>
          <input value={said} placeholder={tr("talk.ph", lang)}
                 onChange={(e) => setSaid(e.target.value)}
                 onKeyDown={(e) => { if (e.key === "Enter") ask(); }} />
          {/* A microphone, not a door: this used to navigate to the channel
              screen, which is a label wearing a mic's icon. The channel
              stays one tap away in the + menu and on the rail. */}
          <button className={"talk-mic" + (listening ? " listening" : "")}
                  aria-label={tr("cch.talk", lang)}
                  onClick={toggleMic}>🎤</button>
          <button className="talk-speak" disabled={busy || !said.trim()}
                  onClick={() => ask()}>{tr("talk.send", lang)}</button>
        </div>
      </div>
    </div>
  );
}
