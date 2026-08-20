import { useEffect, useRef, useState } from "react";
import { api, type EngagedAct, type EngagedPermits, type EngagedReach,
         type EngagedSession, type EngagedStep,
         type StandingWatch } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { loadTheme } from "../theme";
import { useSession } from "../store";

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

  async function speak() {
    const message = said.trim();
    if (!uid || !token || !message) return;
    setBusy(true); setError(null); setNote(null);
    try {
      const turn = await api.engagedTurn(uid, { message }, token);
      setSteps(turn.did || []);
      setProvenance(turn.provenance);
      setSaid("");
      if (turn.stopped) setNote(turn.stopped);
      await refresh();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
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
                          <span className="chip">{s.answered}</span>{" "}
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

            <textarea rows={3} value={said}
                      placeholder={tr("engaged.say.hint", lang)}
                      onChange={(e) => setSaid(e.target.value)} />
            <button className="primary" disabled={busy || !said.trim()}
                    onClick={speak}>
              {tr("engaged.say", lang)}
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
