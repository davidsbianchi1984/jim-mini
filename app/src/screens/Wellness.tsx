import { useEffect, useRef, useState } from "react";
import { api, type CalmSession, type MealPlan, type WorkoutPlan } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { hush, say } from "../speech";
import { useSession } from "../store";

/**
 * Guided wellness — the on-purpose half of guidance. Three generators, all
 * deterministic on the backend (a breathing count, a rep dose, and a menu
 * are protocols, not generations): calm sessions the app paces and can
 * speak, workout plans shaped to minutes/level/focus, and meal plans
 * shaped to goal and preferences. The Coach stays the place to talk about
 * any of it.
 */
export function Wellness() {
  const { session } = useSession();
  const lang = visitorLang();
  const [catalog, setCatalog] = useState<{ kind: string; title: string; minutes: number; what: string }[]>([]);
  const [calm, setCalm] = useState<CalmSession | null>(null);
  const [stepIx, setStepIx] = useState(-1);          // -1 = not running
  const [spoken, setSpoken] = useState(true);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [minutes, setMinutes] = useState(15);
  const [level, setLevel] = useState("beginner");
  const [focus, setFocus] = useState("full_body");
  const [workout, setWorkout] = useState<WorkoutPlan | null>(null);

  const [goal, setGoal] = useState("eat_healthier");
  const [prefs, setPrefs] = useState<string[]>([]);
  const [days, setDays] = useState(1);
  const [meals, setMeals] = useState<MealPlan | null>(null);

  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.calmCatalog().then((r) => setCatalog(r.sessions)).catch(() => {});
    return () => { if (timer.current) clearTimeout(timer.current); hush(); };
  }, []);

  function runStep(s: CalmSession, ix: number) {
    if (ix >= s.steps.length) { setStepIx(-1); return; }
    setStepIx(ix);
    if (spoken) say(s.steps[ix].say);
    timer.current = setTimeout(() => runStep(s, ix + 1),
                               s.steps[ix].seconds * 1000);
  }

  async function startCalm(kind: string) {
    if (!session.userId || !session.userToken) return;
    setBusy(kind); setError(null);
    try {
      const s = await api.startCalm(session.userId, kind, session.userToken);
      setCalm(s);
      runStep(s, 0);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(null); }
  }

  function stopCalm() {
    if (timer.current) clearTimeout(timer.current);
    hush();
    setStepIx(-1);
  }

  async function makeWorkout() {
    if (!session.userId || !session.userToken) return;
    setBusy("workout"); setError(null);
    try {
      setWorkout(await api.workoutPlan(session.userId,
        { minutes, level, focus }, session.userToken));
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(null); }
  }

  async function makeMeals() {
    if (!session.userId || !session.userToken) return;
    setBusy("meals"); setError(null);
    try {
      setMeals(await api.mealPlan(session.userId,
        { goal, preferences: prefs, days }, session.userToken));
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(null); }
  }

  const togglePref = (p: string) =>
    setPrefs((cur) => cur.includes(p) ? cur.filter((x) => x !== p) : [...cur, p]);

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("wel.title", lang)}</h2>
        <span className="muted small">{tr("wel.sub", lang)}</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>{tr("wel.calm", lang)}</h3>
        <p className="muted small">
          {tr("wel.calm.pitch", lang).replace("{spoken}",
            spoken ? tr("wel.calm.spoken", lang) : "")}
        </p>
        <label className="check">
          <input type="checkbox" checked={spoken}
                 onChange={(e) => setSpoken(e.target.checked)} />
          {tr("wel.calm.speak", lang)}
        </label>
        <div className="voice-row" style={{ flexWrap: "wrap" }}>
          {catalog.map((s) => (
            <button key={s.kind} disabled={busy === s.kind || stepIx >= 0}
                    onClick={() => startCalm(s.kind)} title={s.what}>
              {tr("wel.calm.tile", lang)
                .replace("{title}", s.title)
                .replace("{n}", String(s.minutes))}
            </button>
          ))}
        </div>
        {calm && stepIx >= 0 && (
          <div className="calm-run">
            <div className="calm-say">{calm.steps[stepIx].say}</div>
            <div className="muted small">
              {tr("wel.calm.step", lang)
                .replace("{i}", String(stepIx + 1))
                .replace("{n}", String(calm.steps.length))
                .replace("{sec}", String(calm.steps[stepIx].seconds))}
            </div>
            <button onClick={stopCalm}>{tr("wel.calm.end", lang)}</button>
          </div>
        )}
        {calm && stepIx === -1 && (
          <p className="muted small">{tr("wel.calm.done", lang)}</p>
        )}
      </div>

      <div className="card">
        <h3>{tr("wel.work", lang)}</h3>
        <div className="voice-row">
          <label>{tr("wel.work.minutes", lang)}
            <input type="number" min={5} max={90} value={minutes}
                   onChange={(e) => setMinutes(Number(e.target.value))} /></label>
          <label>{tr("wel.work.level", lang)}
            <select value={level} onChange={(e) => setLevel(e.target.value)}>
              {["beginner", "intermediate", "advanced"].map((l) =>
                <option key={l} value={l}>{l}</option>)}
            </select></label>
          <label>{tr("wel.work.focus", lang)}
            <select value={focus} onChange={(e) => setFocus(e.target.value)}>
              {["full_body", "cardio", "strength", "yoga", "mobility"].map((f) =>
                <option key={f} value={f}>{f.replace("_", " ")}</option>)}
            </select></label>
          <button className="primary" disabled={busy === "workout"}
                  onClick={makeWorkout}>{tr("wel.work.build", lang)}</button>
        </div>
        {workout && (
          <div>
            {workout.blocks.map((b, i) => (
              <div key={i} style={{ padding: "8px 0", borderBottom: "1px solid var(--line)" }}>
                <b>{b.name}</b>
                <span className="muted small">{tr("wel.work.block", lang)
                  .replace("{sec}", String(b.seconds))
                  .replace("{cue}", b.cue)}</span>
              </div>
            ))}
            <p className="muted small">{workout.note}</p>
          </div>
        )}
      </div>

      <div className="card">
        <h3>{tr("wel.meals", lang)}</h3>
        <div className="voice-row">
          <label>{tr("wel.meals.goal", lang)}
            <select value={goal} onChange={(e) => setGoal(e.target.value)}>
              <option value="eat_healthier">{tr("wel.meals.healthier", lang)}</option>
              <option value="lose_weight">{tr("wel.meals.lose", lang)}</option>
              <option value="gain_muscle">{tr("wel.meals.gain", lang)}</option>
            </select></label>
          <label>{tr("wel.meals.days", lang)}
            <input type="number" min={1} max={7} value={days}
                   onChange={(e) => setDays(Number(e.target.value))} /></label>
          <button className="primary" disabled={busy === "meals"}
                  onClick={makeMeals}>{tr("wel.meals.plan", lang)}</button>
        </div>
        <div className="voice-row" style={{ flexWrap: "wrap" }}>
          {["vegetarian", "vegan", "dairy_free", "gluten_free"].map((p) => (
            <label key={p} className="check">
              <input type="checkbox" checked={prefs.includes(p)}
                     onChange={() => togglePref(p)} />
              {p.replace("_", "-")}
            </label>
          ))}
        </div>
        {meals && (
          <div>
            <p className="muted small">{tr("wel.meals.shape", lang)
              .replace("{why}", meals.shape.why)
              .replace("{kcal}",
                String(meals.shape.orientation_calories))}</p>
            {meals.days.map((d) => (
              <div key={d.day_number} style={{ padding: "8px 0", borderBottom: "1px solid var(--line)" }}>
                <b>{tr("wel.meals.day", lang)
                  .replace("{n}", String(d.day_number))}</b>
                {d.meals.map((m) => (
                  <div key={m.slot} className="muted small">
                    {m.slot}: {m.name}
                  </div>
                ))}
              </div>
            ))}
            <p className="muted small">{meals.disclaimer}</p>
          </div>
        )}
      </div>
    </div>
  );
}
