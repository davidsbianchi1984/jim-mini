import { useEffect, useState, type ReactNode } from "react";
import { api, getBase, type HandAction, type HandGrant,
         type HandsVocabulary, type HandReach,
         type HandRoutine } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The hands.
 *
 * The coach could see, hear and speak; this is the screen where it is
 * given
 * permission to press a button on somebody's machine. Which means the
 * design problem is not *how do I start it* — that is one button — it is
 * **how does a person see, at a glance, exactly what they just handed
 * over, and take it back in one press**.
 *
 * So the screen is built around the grant rather than around the errand:
 *
 * - the bounds are shown as bounds. Places, moves, minutes and steps are
 *   four fields on one card because they are four halves of one sentence,
 *   and a screen that buried the step budget under "advanced" would be
 *   drawing the dangerous part as the boring part;
 * - **both doors are on the same card.** The owner picks the permission
 *   from the list, or types what they would have said out loud, and the
 *   row that comes back is rendered identically either way. A spoken
 *   grant that reads differently from a picked one invites the belief
 *   that it *is* different;
 * - the told box echoes what the words were understood to mean. Somebody
 *   who says "you can click and type in my calendar for the next hour"
 *   should see `calendar · press, type · 60 minutes` come back, and the
 *   moment that echo is wrong they know before anything moves;
 * - **the ledger shows refusals.** A hand that declined to type a
 *   password is the most reassuring row on the screen and the easiest one
 *   to hide, so refused steps are drawn in line with the rest and carry
 *   their reason;
 * - `never` is rendered from the server, verbatim, above everything. It
 *   names the iPhone case out loud — Apple provides no way for anything
 *   to drive another app's interface — because a person whose phone did
 *   nothing deserves the reason and not a spinner.
 *
 * `Take back` is the loudest control here and never refuses: a reach
 * already running stops at its next step, because the check lives in the
 * backend's `act`, not in this button.
 */
/** Which machine is reading this screen. The picker used to open on
 *  macOS for everybody, so the first Windows reader opened a reach that
 *  told the deciding half it was working a Mac — the errand was right and
 *  the menus it reasoned about were somebody else's. A guess the reader
 *  can correct beats a constant nobody notices. */
function _thisMachine(): string {
  const said = (navigator.userAgent || "").toLowerCase();
  if (said.includes("android")) return "android";
  if (/iphone|ipad|ipod/.test(said)) return "ios";
  if (said.includes("win")) return "windows";
  if (said.includes("mac")) return "macos";
  if (said.includes("linux")) return "linux";
  return "macos";
}

/** The one line that puts the motor on somebody's machine. A constant
 *  rather than a translated string: what the reader types has to match
 *  what pip expects, in every language. */
const INSTALL = "pip install pyautogui mss pillow";

export function Hands() {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.userId || "";
  const token = session.userToken || "";

  const [vocab, setVocab] = useState<HandsVocabulary | null>(null);
  const [grants, setGrants] = useState<HandGrant[]>([]);
  const [routines, setRoutines] = useState<HandRoutine[]>([]);

  const [surface, setSurface] = useState("computer");
  const [places, setPlaces] = useState("");
  const [verbs, setVerbs] = useState<string[]>(["press", "type"]);
  const [minutes, setMinutes] = useState(30);
  const [steps, setSteps] = useState(40);
  const [watched, setWatched] = useState(true);
  const [said, setSaid] = useState("");

  const [useGrant, setUseGrant] = useState("");
  const [errand, setErrand] = useState("");
  const [platform, setPlatform] = useState(_thisMachine());
  const [mode, setMode] = useState("acting");

  const [reach, setReach] = useState<HandReach | null>(null);
  const [ledger, setLedger] = useState<HandAction[]>([]);
  const [routineName, setRoutineName] = useState("");
  const [moveVerb, setMoveVerb] = useState("press");
  const [moveTarget, setMoveTarget] = useState("");
  const [moveText, setMoveText] = useState("");
  const [handTo, setHandTo] = useState("");
  const [dictated, setDictated] = useState("");
  const [onScreen, setOnScreen] = useState("");

  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<ReactNode>(null);
  const fail = (e: unknown) => setError(
    e instanceof Error ? e.message : String(e));

  useEffect(() => {
    api.handsVocabulary().then(setVocab).catch(() => setVocab(null));
  }, []);

  function load() {
    if (!me || !token) { setGrants([]); setRoutines([]); return; }
    api.handGrants(me, token).then((r) => setGrants(r.grants))
      .catch(() => setGrants([]));
    api.handRoutines(me, token).then((r) => setRoutines(r.routines))
      .catch(() => setRoutines([]));
  }
  useEffect(load, [me, token]);

  function refresh(id: string) {
    api.readReach(me, token, id).then((r) => {
      setReach(r.reach); setLedger(r.ledger);
    }).catch(fail);
  }

  const live = grants.filter((g) => g.live);
  // An iPhone is on the list of platforms and not on the list of drivable
  // ones. Saying so here, beside the picker, is the difference between a
  // decision and a bug — the backend refuses either way.
  const undrivable = !!vocab && mode === "acting"
    && !vocab.drivable.includes(platform);

  // `look`, `ask` and `done` are added to every grant by `_verbs()` on the
  // other side, ticked or not — a hand that cannot see, ask or stop is a
  // worse hand rather than a safer one. Drawing them empty and disabled
  // said "refused" when it meant "always", so they are drawn as what they
  // are: on, and not yours to turn off.
  const always = ["look", "ask", "done"];

  /** The motor's command line, on ONE line. It used to be printed the
   *  way a shell script reads — four lines ending in backslashes — and
   *  the first person to run it was on PowerShell, where a trailing
   *  backslash is an argument rather than a continuation. A line that
   *  only works on the machine the author happened to use is not a line
   *  to print on a screen anybody opens. */
  function motorCommand(reachId: string): string {
    // No token. It used to be here, and this screen said so plainly —
    // "the token below is yours, on your own machine". That was true and
    // still wrong: the motor photographs the screen it runs on, so a
    // token typed into that window is in the shell's history, the
    // process list, the scrollback and every frame the eyes send. The
    // deciding model refused an errand over exactly that, correctly. The
    // program asks for it instead, and nothing types it in public.
    return `python hands.py --base ${getBase()} --profile ${me}`
      + ` --reach ${reachId}`;
  }

  /** The token, onto the clipboard, without ever drawing it. Taking it
   *  out of the printed command was right and left nowhere to get it
   *  from — the first person to try typed something else and the stack
   *  answered "authentication required", which was true and unhelpful.
   *  Copied is not shown: the fold below is there for a browser that
   *  will not reach the clipboard, and it costs a deliberate press. */
  async function copyToken() {
    setNote(null);
    try {
      await navigator.clipboard.writeText(token);
      setNote(tr("hnd.motor.token.copied", lang));
    } catch {
      setNote(tr("hnd.motor.token.stuck", lang));
    }
  }

  async function copyInstall() {
    setNote(null);
    try {
      await navigator.clipboard.writeText(INSTALL);
      setNote(tr("hnd.motor.installed", lang));
    } catch { setNote(tr("hnd.motor.select", lang)); }
  }

  async function copyMotor(reachId: string) {
    setNote(null);
    try {
      await navigator.clipboard.writeText(motorCommand(reachId));
      setNote(tr("hnd.motor.copied", lang));
    } catch {
      // A browser that will not reach the clipboard is not a failure
      // worth a refusal — the line is on screen and can be selected.
      setNote(tr("hnd.motor.select", lang));
    }
  }

  function toggleVerb(v: string) {
    setVerbs((prev) => prev.includes(v)
      ? prev.filter((x) => x !== v) : [...prev, v]);
  }

  async function give() {
    setError(null); setNote(null);
    try {
      const written = await api.grantHands(me, token, {
        surface,
        places: places.split(",").map((p) => p.trim()).filter(Boolean),
        verbs, minutes, steps, watched,
      });
      setNote(fill("hnd.gave", lang, { places: written.places.join(", ") }));
      setUseGrant(written.id);
      load();
    } catch (e) { fail(e); }
  }

  async function tell() {
    setError(null); setNote(null);
    try {
      const written = await api.tellHands(me, token,
                                          { in_words: said, surface, watched });
      setNote(fill("hnd.heard", lang, {
        places: written.places.join(", "),
        verbs: written.verbs.join(", "),
      }));
      setSaid(""); setUseGrant(written.id); load();
    } catch (e) { fail(e); }
  }

  async function takeBack(id: string) {
    setError(null); setNote(null);
    try {
      await api.takeHandsBack(me, token, id);
      setNote(tr("hnd.tookback", lang));
      load();
    } catch (e) { fail(e); }
  }

  async function begin() {
    setError(null); setNote(null);
    try {
      const opened = await api.openReach(me, token, {
        grant_id: useGrant, errand, platform, mode,
      });
      setReach(opened); setLedger([]);
    } catch (e) { fail(e); }
  }

  async function stop() {
    if (!reach) return;
    setError(null);
    try {
      const ended = await api.stopReach(me, token, reach.id);
      setReach(ended);
    } catch (e) { fail(e); }
  }

  /** One move, by hand.
   *
   * With no companion driving a real cursor yet, this is the only way to
   * exercise a reach — and it stays useful after there is one, because
   * the person watching is the one who should be able to take a single
   * step themselves without handing over the whole errand.
   */
  async function makeMove() {
    if (!reach) return;
    setError(null); setNote(null);
    try {
      const detail: Record<string, unknown> = {};
      if (moveVerb === "type") { detail.text = moveText; detail.field = moveTarget; }
      if (moveVerb === "key") detail.key = moveText;
      const step = await api.handAct(me, token, reach.id, {
        verb: moveVerb, target: moveTarget || null, detail,
      });
      // A refusal comes back as a step, not as an error — the ledger is
      // where it belongs, and the ledger is what refreshes.
      if (step.outcome !== "done") setNote(step.note || step.outcome || null);
      setMoveText("");
      refresh(reach.id);
    } catch (e) { fail(e); }
  }

  /** Let it choose, rather than being told the move.
   *
   * The console cannot photograph another machine's screen — that is the
   * companion's job, and the companion posts a frame to this same door.
   * What this end can do is describe the screen in words, which is the
   * honest thing a person watching can offer, and is exactly what the
   * eyes would have produced from a picture.
   */
  async function letItChoose() {
    if (!reach) return;
    setError(null); setNote(null);
    try {
      const step = await api.nextMove(me, token, reach.id,
                                      { saw: onScreen.trim() || null });
      if (step.outcome !== "done") setNote(step.note || step.outcome || null);
      refresh(reach.id);
    } catch (e) { fail(e); }
  }

  async function passItOn() {
    if (!reach) return;
    setError(null); setNote(null);
    try {
      const passed = await api.handOver(me, token, reach.id,
                                        { to_user_id: handTo });
      setReach(passed); setHandTo("");
      refresh(passed.id);
    } catch (e) { fail(e); }
  }

  /** A routine somebody dictates rather than demonstrates. One line per
   *  step, `verb: what it aims at` — the same rows `learn_from_reach`
   *  writes, arriving through the other door. */
  async function dictate() {
    setError(null); setNote(null);
    const steps = dictated.split("\n").map((line) => {
      const [verb, ...rest] = line.split(":");
      return { verb: verb.trim().toLowerCase(),
               target: rest.join(":").trim() || null,
               detail: {} };
    }).filter((step) => step.verb);
    try {
      await api.writeRoutine(me, token, {
        name: routineName, surface, learned: "told", steps,
      });
      setNote(tr("hnd.wrotedown", lang));
      setDictated(""); setRoutineName(""); load();
    } catch (e) { fail(e); }
  }

  async function writeItDown() {
    if (!reach) return;
    setError(null); setNote(null);
    try {
      await api.routineFromReach(me, token,
                                 { reach_id: reach.id, name: routineName });
      setNote(tr("hnd.wrotedown", lang));
      setRoutineName(""); load();
    } catch (e) { fail(e); }
  }

  async function again(routineId: string) {
    setError(null); setNote(null);
    try {
      const run = await api.replayRoutine(me, token, routineId,
                                          { grant_id: useGrant, platform });
      setReach(run.reach);
      refresh(run.reach.id);
      load();
    } catch (e) { fail(e); }
  }

  return (
    <div className="screen" id="hands">
      <h2>{tr("hnd.title", lang)}</h2>
      <p className="muted">{tr("hnd.pitch", lang)}</p>

      {/* The refusals, from the server, above everything else. */}
      {vocab && (
        <div className="card">
          <h3>{tr("hnd.never", lang)}</h3>
          <ul className="small">
            {vocab.never.map((line) => <li key={line}>{line}</li>)}
          </ul>
        </div>
      )}

      {error && <div className="error">⚠ {error}</div>}
      {note && <p className="small">{note}</p>}

      <div className="card">
        <h3>{tr("hnd.give", lang)}</h3>
        <p className="muted small">{tr("hnd.give.pitch", lang)}</p>

        <div className="row">
          <label>{tr("hnd.surface", lang)}
            <select value={surface}
                    onChange={(e) => setSurface(e.target.value)}>
              {(vocab?.surfaces || ["computer"]).map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>
          <label>{tr("hnd.places", lang)}
            <input value={places} onChange={(e) => setPlaces(e.target.value)}
                   placeholder={tr("hnd.places.hint", lang)} />
          </label>
        </div>

        <p className="small">{tr("hnd.moves", lang)}</p>
        <div className="row">
          {(vocab?.verbs || []).map((v) => (
            <label key={v} className="small">
              <input type="checkbox"
                     checked={verbs.includes(v) || always.includes(v)}
                     disabled={always.includes(v)}
                     onChange={() => toggleVerb(v)} /> {v}
            </label>
          ))}
        </div>
        <p className="muted small">{tr("hnd.always", lang)}</p>

        <div className="row">
          <label>{tr("hnd.minutes", lang)}
            <input type="number" min={1} max={vocab?.caps.minutes || 240}
                   value={minutes}
                   onChange={(e) => setMinutes(Number(e.target.value))} />
          </label>
          <label>{tr("hnd.steps", lang)}
            <input type="number" min={1} max={vocab?.caps.steps || 200}
                   value={steps}
                   onChange={(e) => setSteps(Number(e.target.value))} />
          </label>
          <label className="small">
            <input type="checkbox" checked={watched}
                   onChange={(e) => setWatched(e.target.checked)} />
            {" "}{tr("hnd.watched", lang)}
          </label>
          <button disabled={!me || !token || !places.trim() || !verbs.length}
                  onClick={give}>{tr("hnd.give.go", lang)}</button>
        </div>

        <hr />
        <p className="small">{tr("hnd.told", lang)}</p>
        <p className="muted small">{tr("hnd.told.pitch", lang)}</p>
        <div className="row">
          <input value={said} onChange={(e) => setSaid(e.target.value)}
                 placeholder={tr("hnd.told.hint", lang)} />
          <button disabled={!me || !token || !said.trim()}
                  onClick={tell}>{tr("hnd.told.go", lang)}</button>
        </div>
      </div>

      <div className="card">
        <h3>{tr("hnd.now", lang)}</h3>
        {!live.length && <p className="muted small">{tr("hnd.none", lang)}</p>}
        {grants.map((g) => (
          <div key={g.id} className="row">
            <span className="small">
              <strong>{g.places.join(", ")}</strong> · {g.verbs.join(", ")}
              {" · "}{g.steps} {tr("hnd.stepsword", lang)}
              {" · "}{g.door}
              {!g.live && ` · ${tr("hnd.over", lang)}`}
            </span>
            {g.said && <span className="muted small">“{g.said}”</span>}
            {g.live && (
              <button onClick={() => takeBack(g.id)}>
                {tr("hnd.takeback", lang)}
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("hnd.put", lang)}</h3>
        <div className="row">
          <select value={useGrant} onChange={(e) => setUseGrant(e.target.value)}>
            <option value="">{tr("hnd.pickgrant", lang)}</option>
            {live.map((g) => (
              <option key={g.id} value={g.id}>{g.places.join(", ")}</option>
            ))}
          </select>
          <select value={platform}
                  onChange={(e) => setPlatform(e.target.value)}>
            {(vocab?.platforms || ["macos"]).map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="acting">{tr("hnd.mode.act", lang)}</option>
            <option value="watching">{tr("hnd.mode.watch", lang)}</option>
          </select>
        </div>
        <div className="row">
          <input value={errand} onChange={(e) => setErrand(e.target.value)}
                 placeholder={tr("hnd.errand", lang)} />
          <button disabled={!useGrant || !errand.trim() || undrivable}
                  onClick={begin}>{tr("hnd.put.go", lang)}</button>
        </div>
        {undrivable && (
          <p className="small">{tr("hnd.undrivable", lang)}</p>
        )}
      </div>

      {reach && (
        <div className="card">
          <h3>{reach.errand}</h3>
          <p className="muted small">
            {fill("hnd.reach.line", lang, {
              state: reach.state, left: reach.steps_left,
              where: reach.platform,
            })}
          </p>
          {reach.why && <p className="small">{reach.why}</p>}
          <div className="row">
            <button onClick={() => refresh(reach.id)}>
              {tr("hnd.refresh", lang)}
            </button>
            {reach.state === "open" && (
              <button onClick={stop}>{tr("hnd.stop", lang)}</button>
            )}
          </div>
          {ledger.map((step) => (
            <p key={step.n} className="small">
              <strong>{step.n}. {step.verb}</strong>
              {step.target ? ` — ${step.target}` : ""}
              {step.outcome !== "done" && ` · ${step.outcome}`}
              {/* Permitted and performed are two different facts, and a
                  step nobody reported on is a third. Saying nothing where
                  the report is missing would read as "it happened". */}
              {step.outcome === "done" && (
                <span className="muted">
                  {" · "}{tr(`hnd.landed.${step.landed || "unknown"}`, lang)}
                </span>
              )}
              {step.landed_note && (
                <span className="muted"> {step.landed_note}</span>
              )}
              {step.note && <span className="muted"> {step.note}</span>}
              {step.saw && <span className="muted small"> · {step.saw}</span>}
            </p>
          ))}
          {/* The motor's command line, already filled in.
           *
           * The stack cannot move a cursor — `companion/hands.py` does,
           * and it runs on the machine whose screen is being worked. It
           * needs four things this screen already knows, and the
           * alternative was telling somebody to dig an owner token out
           * of browser storage, which is not a thing to ask of anybody.
           *
           * The token is on screen because it is the reader's own, on
           * their own machine, and the line is useless without it. It is
           * said out loud rather than hidden, so nobody pastes it
           * somewhere it should not go by not knowing what it was. */}
          {reach.state === "open" && reach.surface !== "here" && (
            <div className="hnd-motor">
              <p className="small">{tr("hnd.motor", lang)}</p>
              <p className="muted small">{tr("hnd.motor.sub", lang)}</p>
              {/* A shell command is the same in every language, so it is
                  neither prose to translate nor prose to leave in English:
                  it is a line to copy, and it goes in a box like the other
                  one. Inside the caption it made two of the ten languages
                  read as half-finished English; drawn as loose text it was
                  an English string on a translated screen. Both readings
                  were right about the same mistake. */}
              <textarea readOnly rows={1} className="hnd-cmd"
                        value={INSTALL} />
              <div className="row">
                <button onClick={copyInstall}>
                  {tr("hnd.motor.install", lang)}
                </button>
              </div>
              <textarea readOnly rows={3} className="hnd-cmd"
                        value={motorCommand(reach.id)} />
              <div className="row">
                <button onClick={() => copyMotor(reach.id)}>
                  {tr("hnd.motor.copy", lang)}
                </button>
                <button onClick={copyToken}>
                  {tr("hnd.motor.token", lang)}
                </button>
              </div>
              <details className="hnd-token">
                <summary className="small">
                  {tr("hnd.motor.token.show", lang)}
                </summary>
                <p className="muted small">
                  {tr("hnd.motor.token.warn", lang)}
                </p>
                <code className="hnd-cmd">{token}</code>
              </details>
              <p className="muted small">{tr("hnd.motor.dry", lang)}</p>
            </div>
          )}
          {reach.state === "open" && (
            <>
              <p className="small">{tr("hnd.move", lang)}</p>
              <div className="row">
                <select value={moveVerb}
                        onChange={(e) => setMoveVerb(e.target.value)}>
                  {(vocab?.verbs || []).map((v) => (
                    <option key={v} value={v}>{v}</option>
                  ))}
                </select>
                <input value={moveTarget}
                       onChange={(e) => setMoveTarget(e.target.value)}
                       placeholder={tr("hnd.move.at", lang)} />
                {(moveVerb === "type" || moveVerb === "key") && (
                  <input value={moveText}
                         onChange={(e) => setMoveText(e.target.value)}
                         placeholder={moveVerb === "key"
                           ? tr("hnd.move.key", lang)
                           : tr("hnd.move.text", lang)} />
                )}
                <button onClick={makeMove}>{tr("hnd.move.go", lang)}</button>
              </div>
              <p className="small">{tr("hnd.choose", lang)}</p>
              <div className="row">
                <input value={onScreen}
                       onChange={(e) => setOnScreen(e.target.value)}
                       placeholder={tr("hnd.choose.ph", lang)} />
                <button onClick={letItChoose}>
                  {tr("hnd.choose.go", lang)}
                </button>
              </div>
              <div className="row">
                <input value={handTo}
                       onChange={(e) => setHandTo(e.target.value)}
                       placeholder={tr("hnd.pass.who", lang)} />
                <button disabled={!handTo.trim()} onClick={passItOn}>
                  {tr("hnd.pass.go", lang)}
                </button>
              </div>
              <p className="muted small">{tr("hnd.pass.note", lang)}</p>
            </>
          )}
          <div className="row">
            <input value={routineName}
                   onChange={(e) => setRoutineName(e.target.value)}
                   placeholder={tr("hnd.name", lang)} />
            <button disabled={!routineName.trim() || !ledger.length}
                    onClick={writeItDown}>{tr("hnd.write", lang)}</button>
          </div>
        </div>
      )}

      <div className="card">
        <h3>{tr("hnd.again", lang)}</h3>
        <p className="muted small">{tr("hnd.again.pitch", lang)}</p>
        <div className="row">
          <input value={routineName}
                 onChange={(e) => setRoutineName(e.target.value)}
                 placeholder={tr("hnd.name", lang)} />
        </div>
        <textarea value={dictated} rows={3}
                  onChange={(e) => setDictated(e.target.value)}
                  placeholder={tr("hnd.dictate.ph", lang)} />
        <div className="row">
          <button disabled={!routineName.trim() || !dictated.trim()}
                  onClick={dictate}>{tr("hnd.dictate.go", lang)}</button>
        </div>
        {!routines.length && <p className="muted small">{tr("hnd.noroutines", lang)}</p>}
        {routines.map((r) => (
          <div key={r.id} className="row">
            <span className="small">
              <strong>{r.name}</strong> · {r.steps.length} · {r.learned}
              {r.runs ? ` · ${r.runs}` : ""}
            </span>
            <button disabled={!useGrant} onClick={() => again(r.id)}>
              {tr("hnd.again.go", lang)}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
