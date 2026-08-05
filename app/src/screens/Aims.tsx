import { useEffect, useState } from "react";
import { api, type BudgetBoard, type GoalArea, type GoalRow,
         type HabitRow } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * What somebody is trying to do — goals, habits, a monthly budget, and the
 * ordinary activity that JIM watches around them.
 *
 * Ten routes have carried this since well before the console existed. Every
 * one of them was reachable from a phone and from none of the desktop app,
 * which is the gap the per-client audit opened: the union guard was asking
 * whether *some* client could reach a route, and a phone could, so the
 * number looked healthy while a desktop owner could not set a goal.
 *
 * Two things on this screen come from driving the routes rather than reading
 * their signatures, and neither was guessable:
 *
 *   * A goal's `area` is a closed set of seven. The server names them in its
 *     422 body; they are a union type in `api.ts` now, so a wrong one is a
 *     build error rather than a rejected save.
 *   * `GET /budgets` answers with a **board** — `{month, days_left, budgets}`
 *     — not the array of lines the name suggests.
 */

const AREAS: { id: GoalArea; label: string }[] = [
  { id: "health_fitness", label: "Health & fitness" },
  { id: "mental_health", label: "Mental health" },
  { id: "nutrition", label: "Nutrition" },
  { id: "career", label: "Career" },
  { id: "finance", label: "Finance" },
  { id: "relationships", label: "Relationships" },
  { id: "personal_growth", label: "Personal growth" },
];

export function Aims() {
  const { session } = useSession();
  const lang = visitorLang();
  const [goals, setGoals] = useState<GoalRow[]>([]);
  const [habits, setHabits] = useState<HabitRow[]>([]);
  const [board, setBoard] = useState<BudgetBoard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [title, setTitle] = useState("");
  const [area, setArea] = useState<GoalArea>("health_fitness");
  const [target, setTarget] = useState("");
  const [habit, setHabit] = useState("");
  const [category, setCategory] = useState("groceries");
  const [limit, setLimit] = useState("400");
  const [activity, setActivity] = useState("");

  const uid = session.userId;
  const token = session.userToken;

  function load() {
    if (!uid || !token) return;
    api.goals(uid, token).then(setGoals).catch(fail);
    api.habits(uid, token).then(setHabits).catch(fail);
    api.budgets(uid, token).then(setBoard).catch(fail);
  }
  function fail(e: unknown) { setError((e as Error).message); }
  useEffect(load, [uid]);

  async function run(work: () => Promise<unknown>) {
    if (!uid || !token) return;
    setBusy(true); setError(null);
    try { await work(); load(); } catch (e) { fail(e); }
    finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("aim.title", lang)}</h2>
        <span className="muted small">{tr("aim.sub", lang)}</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>{tr("aim.goals", lang)}</h3>
        <div className="row">
          <input value={title} placeholder={tr("aim.goals.title.ph", lang)}
                 onChange={(e) => setTitle(e.target.value)} />
          <select value={area}
                  onChange={(e) => setArea(e.target.value as GoalArea)}>
            {AREAS.map((a) => (
              <option key={a.id} value={a.id}>{a.label}</option>
            ))}
          </select>
          <input value={target} placeholder={tr("aim.goals.target.ph", lang)}
                 onChange={(e) => setTarget(e.target.value)} />
          <button className="primary" disabled={busy || !title.trim()}
                  onClick={() => run(async () => {
                    await api.addGoal(uid!, {
                      area, title: title.trim(),
                      target: target.trim() || undefined }, token!);
                    setTitle(""); setTarget("");
                  })}>{tr("aim.add", lang)}</button>
        </div>
        {goals.length === 0 && (
          <div className="muted small">{tr("aim.goals.none", lang)}</div>
        )}
        {goals.map((g) => (
          <div key={g.id}
               style={{ padding: "10px 0", borderBottom: "1px solid var(--line)" }}>
            <div><strong>{g.title}</strong>{" "}
              <span className="muted small">
                {AREAS.find((a) => a.id === g.area)?.label ?? g.area}
                {g.target ? ` · ${g.target}` : ""} · {g.status}
              </span>
            </div>
            <div className="row">
              <input type="range" min={0} max={100}
                     value={Math.round((g.progress ?? 0) * 100)}
                     onChange={(e) => run(() => api.updateGoal(
                       uid!, g.id,
                       { progress: Number(e.target.value) / 100 }, token!))} />
              <span className="muted small">
                {Math.round((g.progress ?? 0) * 100)}%
              </span>
              <button disabled={busy}
                      onClick={() => run(() => api.updateGoal(
                        uid!, g.id, { status: "done" }, token!))}>
                {tr("aim.goals.done", lang)}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("aim.habits", lang)}</h3>
        <div className="row">
          <input value={habit} placeholder={tr("aim.habits.ph", lang)}
                 onChange={(e) => setHabit(e.target.value)} />
          <button className="primary" disabled={busy || !habit.trim()}
                  onClick={() => run(async () => {
                    await api.addHabit(uid!, { name: habit.trim() }, token!);
                    setHabit("");
                  })}>{tr("aim.add", lang)}</button>
        </div>
        {habits.length === 0 && (
          <div className="muted small">{tr("aim.habits.none", lang)}</div>
        )}
        {habits.map((h) => (
          <div key={h.id} className="row"
               style={{ padding: "8px 0", borderBottom: "1px solid var(--line)" }}>
            <span style={{ flex: 1 }}>{h.name}</span>
            <span className="muted small">{tr("aim.habits.streak", lang)
              .replace("{n}", String(h.streak))}</span>
            <button disabled={busy}
                    onClick={() => run(() => api.logHabit(uid!, h.id, token!))}>
              {tr("aim.habits.did", lang)}
            </button>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("aim.budget", lang)}</h3>
        <p className="muted small">
          {board
            ? `${board.month} · ${board.days_left} days left in the month`
            : "…"}
        </p>
        <div className="row">
          <input value={category} placeholder={tr("aim.budget.cat.ph", lang)}
                 onChange={(e) => setCategory(e.target.value)} />
          <input value={limit} type="number" placeholder="400"
                 onChange={(e) => setLimit(e.target.value)} />
          <button className="primary" disabled={busy || !limit}
                  onClick={() => run(() => api.setBudget(uid!, {
                    category: category.trim() || undefined,
                    monthly_limit: Number(limit) }, token!))}>
            {tr("aim.budget.set", lang)}
          </button>
        </div>
        {(board?.budgets ?? []).length === 0 && (
          <div className="muted small">{tr("aim.budget.none", lang)}</div>
        )}
        {(board?.budgets ?? []).map((b) => (
          <div key={b.category} className="row"
               style={{ padding: "8px 0", borderBottom: "1px solid var(--line)" }}>
            <span style={{ flex: 1 }}>{b.category}</span>
            <span className="muted small">
              {tr("aim.budget.line", lang)
                .replace("{spent}", String(b.spent))
                .replace("{limit}", String(b.monthly_limit))
                .replace("{standing}", String(b.standing))}
            </span>
            <button disabled={busy}
                    onClick={() => run(() =>
                      api.clearBudget(uid!, b.category, token!))}>
              {tr("aim.budget.remove", lang)}
            </button>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("aim.activity", lang)}</h3>
        <div className="row">
          <input value={activity} placeholder={tr("aim.activity.ph", lang)}
                 onChange={(e) => setActivity(e.target.value)} />
          <button className="primary" disabled={busy || !activity.trim()}
                  onClick={() => run(async () => {
                    await api.logActivity(uid!,
                      { activity: activity.trim() }, token!);
                    setActivity("");
                  })}>{tr("aim.activity.log", lang)}</button>
        </div>
        <p className="muted small">{tr("aim.activity.pitch", lang)}</p>
      </div>
    </div>
  );
}
