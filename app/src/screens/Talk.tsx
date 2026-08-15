import { useState } from "react";
import { api, type Guidance } from "../api";
import { t as tr, visitorLang, word } from "../l10n";
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
  ];

  async function ask() {
    if (!uid || !token || !said.trim()) return;
    setBusy(true); setError(null);
    try {
      // `general` rather than a picked area: this is the front door, and
      // making somebody choose a category before they can type is the
      // menu problem this screen exists to answer. Coach's own screen
      // still offers the picker for somebody who wants it.
      setReply(await api.coach(uid, { area: "general", message: said.trim() },
                               token));
      setSaid("");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  if (!uid || !token) return <p>{tr("self.signin", lang)}</p>;

  return (
    <div className="talk">
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
            <button role="menuitem" onClick={() => { setPlus(false); go("attending"); }}>
              📷 {tr("talk.plus.camera", lang)}
            </button>
            <button role="menuitem" onClick={() => { setPlus(false); go("attending"); }}>
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
          <button className="talk-mic" aria-label={tr("talk.rail.channel", lang)}
                  onClick={() => go("channel")}>🎙</button>
          <button className="talk-speak" disabled={busy || !said.trim()}
                  onClick={ask}>{tr("talk.send", lang)}</button>
        </div>
      </div>
    </div>
  );
}
