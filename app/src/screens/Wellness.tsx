import { useEffect, useRef, useState } from "react";
import { api, type CalmSession, type MealPlan, type WorkoutPlan } from "../api";
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
        <h2>Wellness</h2>
        <span className="muted small">calm · movement · meals — on purpose, any hour</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>Guided calm</h3>
        <p className="muted small">
          Protocols, not generations — the counts never vary. Pick one; the
          app paces it{spoken ? " and speaks each step" : ""}.
        </p>
        <label className="check">
          <input type="checkbox" checked={spoken}
                 onChange={(e) => setSpoken(e.target.checked)} />
          Speak the steps out loud
        </label>
        <div className="voice-row" style={{ flexWrap: "wrap" }}>
          {catalog.map((s) => (
            <button key={s.kind} disabled={busy === s.kind || stepIx >= 0}
                    onClick={() => startCalm(s.kind)} title={s.what}>
              {s.title} · {s.minutes} min
            </button>
          ))}
        </div>
        {calm && stepIx >= 0 && (
          <div className="calm-run">
            <div className="calm-say">{calm.steps[stepIx].say}</div>
            <div className="muted small">
              step {stepIx + 1} of {calm.steps.length} ·{" "}
              {calm.steps[stepIx].seconds}s
            </div>
            <button onClick={stopCalm}>End early</button>
          </div>
        )}
        {calm && stepIx === -1 && (
          <p className="muted small">Session complete. Carry the pace with you.</p>
        )}
      </div>

      <div className="card">
        <h3>A workout for the time you have</h3>
        <div className="voice-row">
          <label>Minutes
            <input type="number" min={5} max={90} value={minutes}
                   onChange={(e) => setMinutes(Number(e.target.value))} /></label>
          <label>Level
            <select value={level} onChange={(e) => setLevel(e.target.value)}>
              {["beginner", "intermediate", "advanced"].map((l) =>
                <option key={l} value={l}>{l}</option>)}
            </select></label>
          <label>Focus
            <select value={focus} onChange={(e) => setFocus(e.target.value)}>
              {["full_body", "cardio", "strength", "yoga", "mobility"].map((f) =>
                <option key={f} value={f}>{f.replace("_", " ")}</option>)}
            </select></label>
          <button className="primary" disabled={busy === "workout"}
                  onClick={makeWorkout}>Build it</button>
        </div>
        {workout && (
          <div>
            {workout.blocks.map((b, i) => (
              <div key={i} style={{ padding: "8px 0", borderBottom: "1px solid var(--line)" }}>
                <b>{b.name}</b>
                <span className="muted small"> · {b.seconds}s — {b.cue}</span>
              </div>
            ))}
            <p className="muted small">{workout.note}</p>
          </div>
        )}
      </div>

      <div className="card">
        <h3>A day of meals that fits you</h3>
        <div className="voice-row">
          <label>Goal
            <select value={goal} onChange={(e) => setGoal(e.target.value)}>
              <option value="eat_healthier">eat healthier</option>
              <option value="lose_weight">lose weight</option>
              <option value="gain_muscle">gain muscle</option>
            </select></label>
          <label>Days
            <input type="number" min={1} max={7} value={days}
                   onChange={(e) => setDays(Number(e.target.value))} /></label>
          <button className="primary" disabled={busy === "meals"}
                  onClick={makeMeals}>Plan it</button>
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
            <p className="muted small">{meals.shape.why} · about{" "}
              {meals.shape.orientation_calories} kcal/day for orientation</p>
            {meals.days.map((d) => (
              <div key={d.day} style={{ padding: "8px 0", borderBottom: "1px solid var(--line)" }}>
                <b>Day {d.day}</b>
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
