import { useEffect, useState } from "react";
import {
  api, type DockState, type EngagedSession, type HandGrant,
  type MicState, type MonitorRow, type Row, type VoiceQuota,
} from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "./../store";

/**
 * The capability register: every faculty this Guardian can be given, what
 * it stands on, and where it is taken back.
 *
 * ## Why this screen exists when nothing here is new
 *
 * Every capability below already had a door — `console_doorless.txt` has
 * been at zero for many rounds. What none of them had was a single place
 * that names them as a set. Seeing was a card inside Channel & camera;
 * a bound body was one of twenty-four rows on What reaches out; the look
 * permit was a checkbox on Hands. A reader who wanted to answer *what can
 * this thing actually do* had to already know where to look, which means
 * the only people who could answer it were the people who built it.
 *
 *     asked     can each capability be reached
 *     mattered  can the whole set be read at once
 *
 * ## The four columns, and why they are these four
 *
 * A faculty is not described by what it is. It is described by what it is
 * allowed to do, what it is doing right now, and how it is stopped. So
 * every row carries the same four things and no row is allowed fewer:
 *
 *   * **what it is** — the function, in a sentence, in the reader's
 *     language;
 *   * **where it stands** — read live from the same route the owning
 *     screen reads, so this register cannot drift into a brochure;
 *   * **what it rests on** — the permission that had to exist first,
 *     named rather than implied;
 *   * **where it is withdrawn** — the screen that owns it, one press away.
 *
 * The third column is the one this screen is for. A register that listed
 * capabilities without naming the consent under each would be a feature
 * list; a feature list is what a product writes about itself, and a
 * register is what somebody else can hold it to.
 *
 * ## The naming
 *
 * These are named for what they do, not for the body part they resemble.
 * The engineering shorthand behind them is anatomical — the eyes, the
 * ears, the hands — and that shorthand is exactly wrong on a screen a
 * regulator, a clinician or an attorney may read: "eyes" claims a faculty,
 * where "visual perception, described in words and not retained" states a
 * behaviour that can be checked. Each row therefore carries the function
 * as its title and names the product surface it opens underneath, so the
 * two vocabularies stay joined instead of competing.
 *
 * ## Nothing here acts
 *
 * No control on this screen grants, commands, or revokes. It reads, and
 * it routes. The same reasoning `jim/dock.py` gives for the helper dock:
 * the surfaces being summarised include a live escalation and a running
 * grant, and a revoke button in a summary card is a mis-tap against the
 * one thing the summary exists to make legible.
 */

type Tab = "channel" | "bearing" | "reach" | "hands" | "permits";

/** One row of the register: what it is, and which screen withdraws it. */
type Faculty = {
  /** `cap.<key>.title` / `.what` / `.rests` in `l10n.ts`. */
  key: string;
  /** The screen that owns the capability — the only place it changes. */
  opens: Tab;
  /** The product's own name for the surface, shown under the function. */
  surface: string;
};

//: The register, in the order a capability is acquired rather than
//: alphabetically: what it takes in, how it presents, what it can move,
//: and last what it may do unattended. An attorney reading down this list
//: should meet the passive faculties before the active ones, because the
//: active ones are the ones that need the earlier answers.
const FACULTIES: Faculty[] = [
  { key: "sight", opens: "channel", surface: "nav.channel" },
  { key: "hearing", opens: "channel", surface: "nav.channel" },
  { key: "speech", opens: "bearing", surface: "nav.bearing" },
  { key: "appearance", opens: "bearing", surface: "nav.bearing" },
  { key: "body", opens: "reach", surface: "nav.reach" },
  { key: "movement", opens: "reach", surface: "nav.reach" },
  { key: "observation", opens: "hands", surface: "nav.hands" },
  { key: "operation", opens: "hands", surface: "nav.hands" },
  { key: "unattended", opens: "permits", surface: "nav.permits" },
];

/** Everything the register reads, each allowed to fail on its own. */
type Held = {
  monitors: MonitorRow[] | null;
  mic: MicState | null;
  voice: VoiceQuota | null;
  dock: DockState | null;
  robots: Row[] | null;
  grants: HandGrant[] | null;
  engaged: EngagedSession | null;
};

const NOTHING: Held = {
  monitors: null, mic: null, voice: null, dock: null,
  robots: null, grants: null, engaged: null,
};

export function Capabilities({ go }: { go: (tab: string) => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const L = (key: string) => tr(key, lang);
  const [held, setHeld] = useState<Held>(NOTHING);
  const [read, setRead] = useState(false);

  useEffect(() => {
    const { userId: uid, userToken: token } = session;
    if (!uid || !token) return;
    // `allSettled`, not `all`. A deployment with no speaking provider
    // answers 503 on the quota route by design — the refusal is the
    // information — and one rejected promise must not blank the other
    // eight rows. Each faculty renders from what came back for it alone.
    Promise.allSettled([
      api.monitors(uid, token),
      api.micState(uid, token),
      api.voiceQuota(),
      api.dock(uid, token),
      api.robots(uid, token),
      api.handGrants(uid, token, true),
      api.engaged(uid, token),
    ]).then(([mon, mic, voice, dock, robots, grants, engaged]) => {
      const got = <T,>(r: PromiseSettledResult<T>): T | null =>
        r.status === "fulfilled" ? r.value : null;
      setHeld({
        monitors: got(mon),
        mic: got(mic),
        voice: got(voice),
        dock: got(dock),
        robots: got(robots),
        grants: got(grants)?.grants ?? null,
        engaged: got(engaged),
      });
      setRead(true);
    });
  }, [session.userId, session.userToken]);

  /** What each faculty is doing right now, in the reader's language.
   *
   *  `null` is not "off" and is never rendered as off: it is this console
   *  not having been able to ask. The two are different facts and the
   *  register refuses to let them look the same — the same refusal the
   *  Held screen makes about an empty access list. */
  function standing(key: string): string | null {
    const lensed = (held.monitors ?? []).filter(
      (m) => m.on && m.senses.includes("sight"));
    const heard = (held.monitors ?? []).filter(
      (m) => m.on && m.senses.includes("sound"));
    const live = held.grants ?? [];
    switch (key) {
      case "sight":
        if (held.monitors === null) return null;
        return lensed.length === 0 ? L("cap.sight.none")
          : L("cap.sight.some").replace("{n}", String(lensed.length))
                               .replace("{names}", lensed.map(
                                 (m) => m.name).join(", "));
      case "hearing": {
        if (held.monitors === null && held.mic === null) return null;
        if (held.mic?.listening) {
          return L("cap.hearing.live").replace(
            "{device}", String(held.mic.device ?? held.mic.mic_type ?? ""));
        }
        return heard.length === 0 ? L("cap.hearing.none")
          : L("cap.hearing.idle").replace("{n}", String(heard.length));
      }
      case "speech":
        if (held.voice === null) return L("cap.speech.none");
        return L("cap.speech.some").replace(
          "{provider}", held.voice.provider);
      case "appearance":
        if (held.dock === null) return null;
        return held.dock.set
          ? L("cap.appearance.some").replace("{face}", held.dock.face)
          : L("cap.appearance.none");
      case "body":
        if (held.robots === null) return null;
        return (held.robots.length === 0) ? L("cap.body.none")
          : L("cap.body.some").replace("{n}", String(held.robots.length))
              .replace("{names}", held.robots.map(
                (r) => String(r.name ?? r.model)).join(", "));
      case "movement":
        if (held.robots === null) return null;
        // Movement is not its own binding. It is what a bound body is
        // permitted to be told, so with no body there is nothing to
        // report — and saying "off" would imply a switch that exists.
        return held.robots.length === 0 ? L("cap.movement.none")
          : L("cap.movement.some");
      case "observation": {
        if (held.grants === null) return null;
        const looking = live.filter((g) => g.verbs.includes("look"));
        return looking.length === 0 ? L("cap.observation.none")
          : L("cap.observation.some").replace(
              "{n}", String(looking.length));
      }
      case "operation": {
        if (held.grants === null) return null;
        const acting = live.filter(
          (g) => g.verbs.some((v) => v !== "look"));
        return acting.length === 0 ? L("cap.operation.none")
          : L("cap.operation.some").replace("{n}", String(acting.length));
      }
      case "unattended":
        if (held.engaged === null) return null;
        return held.engaged.engaged
          ? L("cap.unattended.some").replace(
              "{area}", String(held.engaged.area ?? ""))
              .replace("{n}", String(held.engaged.acted.length))
          : L("cap.unattended.none");
      default:
        return null;
    }
  }

  return (
    <>
      <div className="screen-head">
        <h2>{L("cap.title")}</h2>
        <p className="muted small">{L("cap.lead")}</p>
      </div>
      <div className="card">
        <p className="small">{L("cap.standing")}</p>
      </div>
      {FACULTIES.map((f) => {
        const now = standing(f.key);
        return (
          <div className="card" key={f.key}>
            <h3>{L(`cap.${f.key}.title`)}</h3>
            <p className="muted small">{L(`cap.${f.key}.what`)}</p>
            <p className="small">
              <strong>{L("cap.now")}</strong>{" "}
              {now === null
                ? <span className="muted">
                    {read ? L("cap.unreadable") : L("cap.reading")}
                  </span>
                : <span>{now}</span>}
            </p>
            <p className="small">
              <strong>{L("cap.rests")}</strong>{" "}
              <span className="muted">{L(`cap.${f.key}.rests`)}</span>
            </p>
            <button onClick={() => go(f.opens)}>
              {L("cap.open").replace("{screen}", L(f.surface))}
            </button>
          </div>
        );
      })}
    </>
  );
}
