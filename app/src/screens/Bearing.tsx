import { useEffect, useState } from "react";
import { api, type ConditionName, type DockCatalog, type DockState,
         type ImproveBoard, type LanguageOption, type Row } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * How it speaks, what it was told, and what it has made of you.
 *
 * Thirty-two routes, the long tail of the audit. They divide into three
 * honest groups and the screen keeps them apart:
 *
 *   * **Bearing** — language, tone, sensitivity, the voice. Things the user
 *     sets.
 *   * **What it was told** — conditions, context, consented sources. Things
 *     the user gives it, and the one place a refusal is load-bearing:
 *     `POST /context` is a 403 until the source it names has been consented
 *     over in What's Held. Driving that is how we know it is enforced rather
 *     than merely documented.
 *   * **What it made of that** — insights, the report, the event log, the
 *     coach's own history, open follow-ups. Things it wrote about you, shown
 *     back to you, which is the half of a guardian product that is easy to
 *     leave out because nobody complains about not seeing it.
 *
 * The guide and the dock live here too, because the tutorial is the only
 * part of the product whose job is to explain the rest of it, and a guide
 * with no door is a peculiar thing to ship.
 */

const CONDITIONS: ConditionName[] = [
  "anxiety", "depression", "stress", "phobia", "financial_stress",
  "relationship", "physical_distress", "physical_injury",
];

export function Bearing() {
  const { session } = useSession();
  const lang = visitorLang();
  const [languages, setLanguages] = useState<LanguageOption[]>([]);
  const [mine, setMine] = useState<Row | null>(null);
  const [dock, setDock] = useState<DockState | null>(null);
  const [catalog, setCatalog] = useState<DockCatalog | null>(null);
  const [where, setWhere] = useState<Row | null>(null);
  const [face, setFace] = useState<Row | null>(null);
  const [guide, setGuide] = useState<Row | null>(null);
  const [step, setStep] = useState<Row | null>(null);
  const [progress, setProgress] = useState<Row | null>(null);
  const [topics, setTopics] = useState<string[]>([]);
  const [board, setBoard] = useState<ImproveBoard | null>(null);
  const [insights, setInsights] = useState<Row[]>([]);
  const [report, setReport] = useState<Row | null>(null);
  const [events, setEvents] = useState<Row[]>([]);
  const [followup, setFollowup] = useState<Row | null>(null);
  const [calm, setCalm] = useState<Row[]>([]);
  const [history, setHistory] = useState<Row[]>([]);
  const [said, setSaid] = useState<Row | null>(null);
  const [translated, setTranslated] = useState<Row | null>(null);
  const [contextError, setContextError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [language, setLanguage] = useState("en");
  const [tone, setTone] = useState("");
  const [condition, setCondition] = useState<ConditionName>("anxiety");
  const [conditionNote, setConditionNote] = useState("");
  const [source, setSource] = useState("calendar");
  const [text, setText] = useState("");
  const [idea, setIdea] = useState("");
  const [medId, setMedId] = useState("");
  const [medDose, setMedDose] = useState("");

  const uid = session.userId;
  const token = session.userToken;

  function load() {
    if (!uid || !token) return;
    api.languages().then((l) => setLanguages(l.languages)).catch(fail);
    api.userLanguage(uid, token).then(setMine).catch(fail);
    api.dock(uid, token).then(setDock).catch(fail);
    api.dockFaces().then(setCatalog).catch(fail);
    api.helpTopics().then((t) => setTopics(t.topics)).catch(fail);
    api.improvements().then(setBoard).catch(fail);
    api.insights(uid, token).then(setInsights).catch(fail);
    api.report(uid, token).then(setReport).catch(fail);
    api.events(uid, token).then(setEvents).catch(fail);
    api.followup(uid, token).then(setFollowup).catch(fail);
    api.calmHistory(uid, token).then(setCalm).catch(fail);
    api.coachHistory(uid, token).then(setHistory).catch(fail);
    api.tutorial().then(setGuide).catch(fail);
    api.tutorialProgress(uid).then(setProgress).catch(fail);
  }
  function fail(e: unknown) { setError((e as Error).message); }
  useEffect(load, [uid]);

  async function run(work: () => Promise<unknown>) {
    if (!uid || !token) return;
    setBusy(true); setError(null);
    try { await work(); load(); } catch (e) { fail(e); }
    finally { setBusy(false); }
  }

  const checkins = (report?.checkins ?? {}) as Record<string, unknown>;

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("brg.title", lang)}</h2>
        <span className="muted small">{tr("brg.sub", lang)}</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>{tr("brg.speak", lang)}</h3>
        <div className="row">
          <select value={language}
                  onChange={(e) => setLanguage(e.target.value)}>
            {languages.map((l) => (
              <option key={l.code} value={l.code}>
                {l.label}{l.safety_content_translated ? ""
                  : tr("brg.safety.english", lang)}
              </option>
            ))}
          </select>
          <button className="primary" disabled={busy}
                  onClick={() => run(() => api.setUserLanguage(
                    uid!, { language }, token!))}>{tr("brg.speak.go", lang)}</button>
          <span className="muted small">
            {tr("brg.speak.now", lang)} {String(mine?.label ?? "…")} · {String(mine?.mode ?? "")}
          </span>
        </div>
        <div className="row">
          <input value={tone} placeholder={tr("brg.speak.tone.ph", lang)}
                 onChange={(e) => setTone(e.target.value)} />
          <button disabled={busy || !tone.trim()}
                  onClick={() => run(() => api.setPersonality(
                    uid!, { tone: tone.trim() }, token!))}>{tr("brg.speak.tone", lang)}</button>
          {/* The sensitivity dial moved to the Baseline screen in the
              limits round-up — it scales the drift bands shown there, so
              it lives beside them. (Its select here also offered a third
              level the server never accepted; the move buried that.) */}
          <button disabled={busy}
                  onClick={() => run(() => api.clearVoice(token!))}>
            {tr("brg.speak.voice", lang)}
          </button>
        </div>
        <div className="row">
          <input value={text} placeholder={tr("brg.speak.tr.ph", lang)}
                 onChange={(e) => setText(e.target.value)} />
          <button disabled={busy || !text.trim()}
                  onClick={() => run(async () => {
                    setTranslated(await api.translate(uid!, {
                      text: text.trim(), to: language }, token!));
                  })}>{tr("brg.speak.tr", lang)}</button>
        </div>
        {translated && (
          <p className="muted small">{String(translated.text ?? "")}</p>
        )}
      </div>

      <div className="card">
        <h3>{tr("brg.told", lang)}</h3>
        <div className="row">
          <select value={condition}
                  onChange={(e) =>
                    setCondition(e.target.value as ConditionName)}>
            {CONDITIONS.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <input value={conditionNote} placeholder={tr("brg.told.note.ph", lang)}
                 onChange={(e) => setConditionNote(e.target.value)} />
          <button className="primary" disabled={busy}
                  onClick={() => run(async () => {
                    await api.recordCondition(uid!, {
                      condition, note: conditionNote.trim() || undefined },
                      token!);
                    setConditionNote("");
                  })}>{tr("brg.told.tell", lang)}</button>
        </div>
        <div className="row">
          <input value={source} placeholder={tr("brg.told.src.ph", lang)}
                 onChange={(e) => setSource(e.target.value)} />
          <button disabled={busy}
                  onClick={async () => {
                    setContextError(null);
                    try {
                      await api.giveContext(uid!, {
                        source: source.trim(), kind: "event",
                        data: { title: "something on the calendar" } },
                        token!);
                    } catch (e) { setContextError((e as Error).message); }
                  }}>{tr("brg.told.ctx", lang)}</button>
          <button disabled={busy}
                  onClick={() => run(async () => {
                    setSaid(await api.askCompanion(uid!, {}, token!));
                  })}>{tr("brg.told.say", lang)}</button>
        </div>
        {contextError && (
          <p className="muted small">
            {tr("brg.told.refused", lang).replace("{err}", contextError)}
          </p>
        )}
        {said && <p className="muted small">{String(said.content ?? "")}</p>}
        <div className="row">
          <input value={medId} placeholder={tr("brg.told.med.ph", lang)}
                 onChange={(e) => setMedId(e.target.value)} />
          <input value={medDose} placeholder={tr("brg.told.dose.ph", lang)}
                 onChange={(e) => setMedDose(e.target.value)} />
          <button disabled={busy || !medId.trim()}
                  onClick={() => run(() => api.updateMed(uid!, medId.trim(),
                    { dose: medDose.trim() || undefined }, token!))}>
            {tr("brg.told.med", lang)}
          </button>
        </div>
      </div>

      <div className="card">
        <h3>{tr("brg.made", lang)}</h3>
        <p className="muted small">
          {tr("brg.made.stats", lang)
            .replace("{c}", String(checkins.count ?? 0))
            .replace("{m}", String(checkins.avg_mood ?? "—"))
            .replace("{i}", String(insights.length))
            .replace("{e}", String(events.length))
            .replace("{s}", String(calm.length))
            .replace("{x}", String(history.length))}
        </p>
        {((followup?.open ?? []) as Row[]).length > 0 && (
          <p className="muted small">
            {tr("brg.made.open", lang)
              .replace("{n}", String(((followup?.open ?? []) as Row[]).length))
              .replace("{s}",
                ((followup?.open ?? []) as Row[]).length === 1 ? "" : "s")}
          </p>
        )}
        {insights.slice(0, 8).map((x, i) => (
          <div key={i} style={{ padding: "6px 0", borderBottom: "1px solid var(--line)" }}>
            {String(x.summary ?? x.text ?? JSON.stringify(x))}
          </div>
        ))}
        {events.slice(0, 8).map((x, i) => (
          <div key={i} className="row" style={{ padding: "4px 0" }}>
            <span className="muted small" style={{ width: 180 }}>
              {String(x.type ?? "")}
            </span>
            <span className="muted small">{String(x.created_at ?? "")}</span>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("brg.guide", lang)}</h3>
        <p className="muted small">{String(guide?.guide ?? "…")}</p>
        <div className="row">
          <button disabled={busy}
                  onClick={() => run(() => api.startTutorial(
                    { learner_id: uid! }))}>{tr("brg.guide.start", lang)}</button>
          <button disabled={busy}
                  onClick={() => run(async () => {
                    setStep(await api.tutorialStep("what"));
                  })}>{tr("brg.guide.step", lang)}</button>
          <button disabled={busy}
                  onClick={() => run(async () => {
                    setStep(await api.tutorialForScreen(1));
                  })}>{tr("brg.guide.screen", lang)}</button>
          <button disabled={busy}
                  onClick={() => run(() => api.finishTutorialStep(
                    { learner_id: uid!, lesson: "what" }))}>
            {tr("brg.guide.done", lang)}
          </button>
        </div>
        {progress != null && (
          <p className="muted small">
            {tr("brg.guide.progress", lang)
              .replace("{d}", String(progress.done ?? 0))
              .replace("{t}", String(progress.total ?? 0))}
          </p>
        )}
        {step && (
          <p className="muted small">
            <strong>{String(step.title ?? "")}</strong> —{" "}
            {String(step.what ?? "")} {String(step.try_it ?? "")}
          </p>
        )}
        <h4>{tr("brg.guide.topics", lang)}</h4>
        {topics.slice(0, 6).map((t, i) => (
          <div key={i} className="muted small" style={{ padding: "4px 0" }}>
            · {t}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("brg.dock", lang)}</h3>
        {dock && (
          <p className="muted small">
            {tr("brg.dock.line", lang)
              .replace("{corner}", dock.corner)
              .replace("{state}", dock.state)
              .replace("{forced}",
                dock.forced ? ` · forced (${String(dock.why ?? "")})` : "")
              .replace("{face}", dock.face)}
          </p>
        )}
        <div className="row">
          {(dock?.chosen_faces ?? []).map((f) => (
            <button key={f} disabled={busy}
                    onClick={() => run(async () => {
                      setFace(await api.dockFace(uid!, f, token!));
                      setWhere(await api.dockWhere(f));
                    })}>{f}</button>
          ))}
        </div>
        <div className="row">
          <button disabled={busy}
                  onClick={() => run(() => api.setDock(uid!,
                    { corner: dock?.corner === "bottom_right"
                        ? "bottom_left" : "bottom_right" }, token!))}>
            {tr("brg.dock.move", lang)}
          </button>
          <button disabled={busy}
                  onClick={() => run(() => api.setDock(uid!,
                    { state: dock?.state === "open" ? "handle" : "open" },
                    token!))}>
            {dock?.state === "open" ? tr("brg.dock.tuck", lang)
                                    : tr("brg.dock.open", lang)}
          </button>
        </div>
        {catalog && where != null && (
          <p className="muted small">
            {String(catalog.faces[String(face?.face ?? "")] ?? "")}{" "}
            {String(where.where ?? where.screen ?? "")}
          </p>
        )}
      </div>

      <div className="card">
        <h3>{tr("brg.tell", lang)}</h3>
        <div className="row">
          <input value={idea} placeholder={tr("brg.tell.ph", lang)}
                 onChange={(e) => setIdea(e.target.value)} />
          <button className="primary" disabled={busy || !idea.trim()}
                  onClick={() => run(async () => {
                    await api.suggestImprovement({
                      category: "improvement", message: idea.trim() });
                    setIdea("");
                  })}>{tr("brg.tell.send", lang)}</button>
          <button disabled={busy}
                  onClick={() => run(() => api.sendFeedback(
                    uid!, { rating: "up" }, token!))}>{tr("brg.tell.good", lang)}</button>
          <button disabled={busy}
                  onClick={() => run(() => api.sendFeedback(
                    uid!, { rating: "down" }, token!))}>{tr("brg.tell.bad", lang)}</button>
        </div>
        {board && (
          <p className="muted small">
            {tr("brg.tell.board", lang)
              .replace("{n}", String(board.total))
              .replace("{s}", board.total === 1 ? "" : "s")
              .replace("{m}", String(board.mine.length))}
          </p>
        )}
      </div>
    </div>
  );
}
