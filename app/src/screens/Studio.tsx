import { useCallback, useEffect, useState } from "react";

import { api, type AppEdit, type AppEditPosture, type ProviderRow,
         type StudioLimits, type Widget, type WidgetRun } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The Studio — where somebody writes their own tools, for themselves only.
 *
 * A widget is a function they wrote. It runs in a box with no network, one
 * directory, no child processes and finite time; `jim/widgets.py` holds those
 * walls and `jim/tests/test_the_widget_cannot_leave_its_box.py` proves they
 * hold by trying to break each one. Nothing on this screen can reach another
 * person's records, because every door it knocks on is scoped to this user at
 * the API and scoped again in the query behind it.
 *
 *     asked     can a person run their own code here
 *     mattered  can a person run their own code without reaching anybody
 *               else's — this disk holds other people's clinical captures
 *
 * ## The limits are fetched, never written here
 *
 * `/studio/limits` answers the seven numbers the runner actually holds. A
 * screen that stated one of them itself would be a promise the product did
 * not make, and it would go stale the first time the runner changed.
 *
 * ## When the box cannot be built
 *
 * The banner says so, in the reader's language, and **the editor stays**.
 * Somebody on a host with no user namespaces can still write and keep their
 * widgets; what they cannot do is run one, so the run button is the only
 * thing that goes. Hiding the whole screen would lose their work to a
 * deployment detail they did not choose.
 */
const STARTER = `// Your own tool. Whatever it returns is the answer.
module.exports = ({ name }) => {
  return "hello, " + (name || "you");
};
`;

export function Studio() {
  const { session } = useSession();
  const lang = visitorLang();
  const [box, setBox] = useState<StudioLimits | null>(null);
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [open, setOpen] = useState<Widget | null>(null);
  const [name, setName] = useState("");
  const [source, setSource] = useState(STARTER);
  const [given, setGiven] = useState("{}");
  const [answer, setAnswer] = useState<WidgetRun | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Edit the app itself — the submit + approval seam (jim/appedits.py).
  const [editPosture, setEditPosture] = useState<AppEditPosture | null>(null);
  const [edits, setEdits] = useState<AppEdit[]>([]);
  const [editModels, setEditModels] = useState<(ProviderRow & { origin: string })[]>([]);
  const [editModel, setEditModel] = useState("auto");
  const [editTarget, setEditTarget] = useState("");
  const [editInstruction, setEditInstruction] = useState("");
  const [propTitle, setPropTitle] = useState("");
  const [propDesc, setPropDesc] = useState("");

  const uid = session.userId;
  const token = session.userToken;

  const load = useCallback(() => {
    if (!uid || !token) return;
    api.widgets(uid, token)
      .then((r) => setWidgets(r.widgets))
      .catch((e) => setError((e as Error).message));
    api.appEdits(uid, token)
      .then((r) => { setEditPosture(r.posture); setEdits(r.edits); setEditModels(r.models); })
      .catch(() => { setEditPosture(null); setEdits([]); setEditModels([]); });
  }, [uid, token]);

  useEffect(() => {
    api.studioLimits().then(setBox).catch(() => setBox(null));
    load();
  }, [load]);

  async function edit(w: Widget | null) {
    setAnswer(null);
    setError(null);
    if (!w) {
      setOpen(null);
      setName("");
      setSource(STARTER);
      return;
    }
    // Re-read rather than trusting the row from the last listing. The list is
    // a snapshot, and this same account may be open on a phone — editing from
    // a stale copy and saving would silently overwrite whatever the other one
    // wrote. On failure the listed row is still better than an empty editor,
    // so it stands in and the person is told why.
    setOpen(w); setName(w.name); setSource(w.source);
    if (!uid || !token) return;
    try {
      const fresh = await api.readWidget(uid, w.id, token);
      setOpen(fresh); setName(fresh.name); setSource(fresh.source);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function keep() {
    if (!uid || !token) return;
    setBusy(true); setError(null);
    try {
      const saved = open
        ? await api.reviseWidget(uid, open.id, { name, source }, token)
        : await api.writeWidget(uid, { name, source }, token);
      setOpen(saved);
      load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function drop(w: Widget) {
    if (!uid || !token) return;
    setBusy(true); setError(null);
    try {
      await api.removeWidget(uid, w.id, token);
      if (open?.id === w.id) edit(null);
      load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function run() {
    if (!uid || !token || !open) return;
    setBusy(true); setError(null); setAnswer(null);
    let inputs: unknown = {};
    try {
      inputs = given.trim() ? JSON.parse(given) : {};
    } catch {
      // Their JSON, not the server's problem: say so here rather than
      // sending something the widget will be blamed for.
      setError(tr("studio.badinputs", lang));
      setBusy(false);
      return;
    }
    try {
      setAnswer(await api.runWidget(uid, open.id, inputs, token));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (!uid || !token) return <p>{tr("self.signin", lang)}</p>;

  const runnable = box?.available !== false;

  // Every refusal key the Studio can send back, spelled out rather than
  // composed. `tr(someVariable)` hides the key from the dead-key guard, and a
  // key nothing can see is a key nobody notices going missing — which is how
  // a screen ends up printing `widgets.no_netns` at somebody.
  const said: Record<string, string> = {
    "widgets.no_rlimits": tr("widgets.no_rlimits", lang),
    "widgets.no_unshare": tr("widgets.no_unshare", lang),
    "widgets.no_node": tr("widgets.no_node", lang),
    "widgets.node_too_old": tr("widgets.node_too_old", lang),
    "widgets.no_netns": tr("widgets.no_netns", lang),
    "widgets.threw": tr("widgets.threw", lang),
    "widgets.timeout": tr("widgets.timeout", lang),
    "widgets.killed": tr("widgets.killed", lang),
    "widgets.no_answer": tr("widgets.no_answer", lang),
  };

  return (
    <div className="stack" data-screen="40">
      <h2>{tr("studio.title", lang)}</h2>
      <p className="muted">{tr("studio.sub", lang)}</p>

      {box && !box.available && (
        // The honest reason, by key, from this console's own table. The
        // server sends `widgets.no_netns`; a server-written sentence would
        // arrive in whatever language the server happened to hold.
        <div className="card warn">
          {said[box.unavailable_because || ""] || tr("studio.nobox", lang)}
        </div>
      )}

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>{tr("studio.yours", lang)}</h3>
        <button onClick={() => edit(null)}>{tr("studio.new", lang)}</button>
        {widgets.length === 0 && (
          <p className="muted small">{tr("studio.none", lang)}</p>
        )}
        {widgets.map((w) => (
          <div key={w.id} className="row">
            <button className="linkish" onClick={() => edit(w)}>{w.name}</button>
            {/* A save count, not a version string — see `Widget` in api.ts. */}
            <span className="muted small">
              {fill("studio.revision", lang, { n: w.revision })}
            </span>
            <button onClick={() => drop(w)} disabled={busy}>
              {tr("studio.remove", lang)}
            </button>
          </div>
        ))}
      </div>

      {/* Edit the app itself — the submit + approval seam (jim/appedits.py).
          The assistant writes the change with the person's pick from their
          region's model menu. On their own server it is approved as it
          arrives; on the hosted cloud it is held for company oversight; and
          either way nothing here touches the running app — an approved edit
          rides the next publish-merge. */}
      <div className="card">
        <h3>{tr("edit.title", lang)}</h3>
        <p className="muted small">{tr("edit.sub", lang)}</p>
        {editPosture && (
          <p className="muted small">
            <b>{tr(`edit.lane.${editPosture.lane}`, lang)}</b>{" "}
            {tr("edit.never", lang)}
          </p>
        )}
        <label>
          {tr("edit.model", lang)}
          <select value={editModel} onChange={(e) => setEditModel(e.target.value)}>
            <option value="auto">{tr("edit.model.auto", lang)}</option>
            {editModels.map((m) => (
              <option key={m.name} value={m.name}>
                {m.label} · {tr(`edit.origin.${m.origin}`, lang)}
              </option>
            ))}
          </select>
        </label>
        <input value={editTarget} placeholder={tr("edit.target.ph", lang)}
               onChange={(e) => setEditTarget(e.target.value)} />
        <textarea rows={4} value={editInstruction}
                  placeholder={tr("edit.instruction.ph", lang)}
                  onChange={(e) => setEditInstruction(e.target.value)} />
        <button disabled={busy || !editInstruction.trim()} onClick={async () => {
          if (!uid || !token) return;
          setBusy(true); setError(null);
          try {
            await api.draftAppEdit(uid, {
              target: editTarget.trim(), instruction: editInstruction.trim(),
              model: editModel === "auto" ? "" : editModel,
            }, token);
            setEditInstruction(""); load();
          } catch (e) { setError((e as Error).message); }
          finally { setBusy(false); }
        }}>{tr("edit.draft", lang)}</button>
        {/* Or file the change yourself, in your own words, without the
            assistant — the same lane, the same hold. */}
        <p className="muted small">{tr("edit.propose.pitch", lang)}</p>
        <input value={propTitle} placeholder={tr("edit.propose.title.ph", lang)}
               onChange={(e) => setPropTitle(e.target.value)} />
        <textarea rows={3} value={propDesc}
                  placeholder={tr("edit.propose.desc.ph", lang)}
                  onChange={(e) => setPropDesc(e.target.value)} />
        <button disabled={busy || !propTitle.trim() || !propDesc.trim()} onClick={async () => {
          if (!uid || !token) return;
          setBusy(true); setError(null);
          try {
            await api.proposeAppEdit(uid, {
              title: propTitle.trim(), description: propDesc.trim(),
              target: editTarget.trim(),
            }, token);
            setPropTitle(""); setPropDesc(""); load();
          } catch (e) { setError((e as Error).message); }
          finally { setBusy(false); }
        }}>{tr("edit.propose", lang)}</button>
        <h3>{tr("edit.mine", lang)}</h3>
        {edits.length === 0 && <p className="muted small">{tr("edit.none", lang)}</p>}
        {edits.map((e) => (
          <div key={e.id} className="row">
            <span>{e.title}</span>
            <span className="muted small">{tr(`edit.state.${e.state}`, lang)}</span>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{open ? tr("studio.editing", lang) : tr("studio.writing", lang)}</h3>
        <label>
          {tr("studio.name", lang)}
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label>
          {tr("studio.source", lang)}
          <textarea rows={12} value={source} spellCheck={false}
                    onChange={(e) => setSource(e.target.value)} />
        </label>
        <button onClick={keep} disabled={busy || !name.trim()}>
          {open ? tr("studio.save", lang) : tr("studio.keep", lang)}
        </button>
      </div>

      {open && (
        <div className="card">
          <h3>{tr("studio.tryit", lang)}</h3>
          <label>
            {tr("studio.inputs", lang)}
            <textarea rows={3} value={given} spellCheck={false}
                      onChange={(e) => setGiven(e.target.value)} />
          </label>
          {/* No run button at all when the box cannot be built. A control
              that is present and refuses on every press is the dead control
              this codebase does not ship; the banner above already said
              why, in words. */}
          {runnable ? (
            <button onClick={run} disabled={busy}>{tr("studio.run", lang)}</button>
          ) : (
            <p className="muted small">{tr("studio.cannotrun", lang)}</p>
          )}
          {answer && (
            <div className={answer.status === "ok" ? "card" : "error"}>
              <p className="muted small">
                {fill("studio.took", lang, { ms: answer.ms })}
              </p>
              {answer.status === "ok" ? (
                <pre>{answer.truncated
                  ? tr("studio.toobig", lang)
                  : JSON.stringify(answer.value, null, 2)}</pre>
              ) : (
                // `message` is the widget's own error, which belongs beside
                // the editor verbatim; `detail` is a refusal key from this
                // console's table. Whichever the answer carries.
                <p>{answer.message || said[answer.detail || ""]
                     || tr("studio.failed", lang)}</p>
              )}
            </div>
          )}
        </div>
      )}

      {box && (
        <div className="card">
          <h3>{tr("studio.limits", lang)}</h3>
          <p className="muted small">{tr("studio.limits.why", lang)}</p>
          {Object.entries(box.allowances).map(([k, v]) => (
            <div key={k} className="row">
              <span>{tr(`studio.limit.${k}`, lang)}</span>
              <span className="muted">{v}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
