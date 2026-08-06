import { useCallback, useEffect, useState } from "react";
import {
  api, type PresenceBaseline, type PresenceBeat, type PresenceDay,
  type PresenceGrowth,
  type PresenceReach, type PresenceSurfaces, type PresenceWho,
} from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The presence — the coach that speaks first.
 *
 * Modelled on the operating system in *Her*, in the parts worth having: it
 * starts things, it notices without being asked, it is curious, it reports its
 * own change, and it keeps handing the reader people who are not it.
 *
 * Three things this screen renders and does not decide:
 *
 *   * **the boundaries** come from the server and are shown *first*, above any
 *     warm sentence. A guardian that is charming before it is honest has the
 *     order wrong;
 *   * **the line** is a key and a set of slots, filled from this table in the
 *     reader's own language — never an English sentence composed on a server;
 *   * **whether it speaks at all** is the backend's, decided from six areas of
 *     this person's own history. Silence renders as silence with its reason,
 *     because a guardian with something to say every single day is a
 *     notification and people turn notifications off.
 */
/** The ten line keys, spelled out.
 *
 *  `fill(b.line_key, …)` would be shorter and is what a first draft did — and
 *  a key looked up from a variable is invisible to the guard that checks every
 *  translated row is read by something, so ten rows in the table came back as
 *  "translated and looked up by nothing". The switch is the price of the guard
 *  keeping its teeth.
 */
function lineFor(b: PresenceBeat, lang: ReturnType<typeof visitorLang>): string {
  const s = b.slots;
  switch (b.line_key) {
    case "presence.notice.drift": return fill("presence.notice.drift", lang, s);
    case "presence.notice.mood": return fill("presence.notice.mood", lang, s);
    case "presence.nudge.goal": return fill("presence.nudge.goal", lang, s);
    case "presence.nudge.followup": return fill("presence.nudge.followup", lang, s);
    case "presence.celebrate.streak": return fill("presence.celebrate.streak", lang, s);
    case "presence.celebrate.goal": return fill("presence.celebrate.goal", lang, s);
    case "presence.curious.area": return fill("presence.curious.area", lang, s);
    case "presence.curious.open": return fill("presence.curious.open", lang, s);
    case "presence.quiet.held": return fill("presence.quiet.held", lang, s);
    case "presence.quiet.nothing": return fill("presence.quiet.nothing", lang, s);
    // A key this build has never heard of: show the server's English rather
    // than the key name at somebody.
    default: return b.english;
  }
}

export function Presence() {
  const { session } = useSession();
  const lang = visitorLang();
  const uid = session.userId;
  const token = session.userToken;

  const [who, setWho] = useState<PresenceWho | null>(null);
  const [day, setDay] = useState<PresenceDay | null>(null);
  const [base, setBase] = useState<PresenceBaseline | null>(null);
  const [surf, setSurf] = useState<PresenceSurfaces | null>(null);
  const [reach, setReach] = useState<PresenceReach | null>(null);
  const [grew, setGrew] = useState<PresenceGrowth | null>(null);
  const [spoken, setSpoken] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!uid || !token) return;
    setError(null);
    try {
      setWho(await api.presenceWho());
      setDay(await api.presenceDay(uid, token));
      setBase(await api.presenceBaseline(uid, token));
      setSurf(await api.presenceSurfaces(uid, token));
      setGrew(await api.presenceGrowth(uid, token));
    } catch (e) {
      setError((e as Error).message);
    }
    // The tandem is optional and a missing one is not an error here: 409 is
    // the shape "the people live in QRME", and an empty shelf says it better
    // than a red banner would.
    try {
      if (uid && token) setReach(await api.presenceReach(uid, token));
    } catch { setReach(null); }
  }, [uid, token]);

  useEffect(() => { load(); }, [load]);

  /** `/day` is the plan; `/beat` is the utterance.
   *
   *  Asking for a slot's beat is what *counts as having said it* — the
   *  backend records it so the same line does not come back tomorrow. Reading
   *  the day ahead deliberately does not, because a plan somebody never heard
   *  must not be filed as something they were told.
   */
  async function hear(slot: string) {
    if (!uid || !token) return;
    try {
      const got = await api.presenceBeat(uid, token, slot);
      setSpoken((p) => ({ ...p, [slot]: got.spoken ?? got.english }));
    } catch (e) { setError((e as Error).message); }
  }

  async function deepen(slot: string) {
    if (!uid || !token) return;
    try {
      const got = await api.presenceDeepen(uid, token, slot);
      setSpoken((p) => ({ ...p, [slot]: got.spoken ?? got.english }));
    } catch (e) { setError((e as Error).message); }
  }

  async function choose(surface: string) {
    if (!uid || !token) return;
    try { setSurf(await api.presenceChooseSurface(uid, token, surface)); }
    catch (e) { setError((e as Error).message); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("presence.tab", lang)}</h2>
        <span className="muted small">{tr("presence.sub", lang)}</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      {/* Honest before warm, deliberately in that order. */}
      {who && (
        <div className="card">
          <p><strong>{tr("presence.what", lang)}</strong></p>
          <p>{who.says}</p>
          <p className="muted small">{tr("presence.will.not", lang)}</p>
          <ul>
            {Object.entries(who.boundaries).map(([key, b]) => (
              <li key={key} className="muted small">{b.says}</li>
            ))}
          </ul>
          <p className="muted small">{who.note}</p>
        </div>
      )}

      {day && (
        <div className="card">
          <p><strong>{tr("presence.today", lang)}</strong></p>
          <p className="muted small">{tr("presence.offline", lang)}</p>
          {day.beats.map((b) => (
            <div key={b.slot} className="row" style={{ alignItems: "flex-start" }}>
              <span className="pill">{b.slot}</span>
              <div style={{ flex: 1 }}>
                <p>{spoken[b.slot] ?? lineFor(b, lang)}</p>
                {/* Why it said this. A presence that cannot show its reason
                    is one nobody can argue with. */}
                {b.because.map((why) => (
                  <p key={why} className="muted small">{why}</p>
                ))}
              </div>
              {b.speak && (
                <>
                  <button onClick={() => hear(b.slot)}>
                    {tr("presence.tab", lang)}
                  </button>
                  <button onClick={() => deepen(b.slot)}>
                    {tr("presence.deepen", lang)}
                  </button>
                </>
              )}
            </div>
          ))}
        </div>
      )}

      {base && (
        <div className="card">
          <p><strong>{tr("presence.baseline", lang)}</strong>{" "}
            <span className="muted small">
              {base.known_areas} / {base.of}
            </span>
          </p>
          {Object.values(base.areas).map((a) => (
            <div key={a.area} className="row">
              <span style={{ flex: 1 }}>{a.area.replace(/_/g, " ")}</span>
              <span className="muted small">{a.standing}</span>
            </div>
          ))}
        </div>
      )}

      {surf && (
        <div className="card">
          <p><strong>{tr("presence.surfaces", lang)}</strong></p>
          <p className="muted small">{surf.rule}</p>
          {surf.surfaces.map((s) => (
            <div key={s.surface} className="row">
              <button className={s.chosen ? "primary" : ""}
                      onClick={() => choose(s.surface)}>
                {s.surface}
              </button>
              <span className="muted small" style={{ flex: 1 }}>{s.note}</span>
              <span className="muted small">
                {s.reads_health_aloud
                  ? tr("presence.aloud", lang)
                  : tr("presence.shown", lang)}
              </span>
            </div>
          ))}
          <p className="muted small">{surf.glasses_makes.join(" · ")}</p>
        </div>
      )}

      {reach && (
        <div className="card">
          <p><strong>{tr("presence.reach", lang)}</strong></p>
          <p className="muted small">{reach.note}</p>
          {reach.offers.map((o) => (
            <div key={`${o.kind}-${o.id}`} className="row">
              <span className="pill">{o.kind}</span>
              <span style={{ flex: 1 }}>{o.who ?? o.topic ?? o.id}</span>
              <span className="muted small">{o.trade ?? o.about ?? ""}</span>
            </div>
          ))}
        </div>
      )}

      {grew && (
        <div className="card">
          <p><strong>{tr("presence.growth", lang)}</strong></p>
          <div className="row">
            <span style={{ flex: 1 }}>{grew.beats_spoken}</span>
            <span className="muted small">
              {grew.areas_i_can_see} / {grew.of}
            </span>
          </div>
          {grew.what_i_changed.map((line) => (
            <p key={line} className="muted small">{line}</p>
          ))}
          {/* The honest half, in its own words, on the screen rather than in
              a docstring nobody reads. */}
          <p className="muted small">{grew.about_myself}</p>
        </div>
      )}
    </div>
  );
}
