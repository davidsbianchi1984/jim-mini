import { useCallback, useState } from "react";
import { api, type AppEdit, type AppEditPosture } from "../api";
import { t as tr, visitorLang } from "../l10n";

/**
 * Company oversight — the review desk over proposed app edits.
 *
 * A person on the hosted cloud proposes a change to the app itself (or has
 * the coding assistant write one) from the Studio, and it is **held at
 * apply**: nothing reaches running code until oversight approves it, and an
 * approved edit only rides the next publish-merge. Until this screen the
 * desk was API-only, behind the deployment's reviewer token. This is the
 * desk on a screen.
 *
 * The reviewer token (JIM_ADMIN_TOKEN) is the role that stands for the
 * deployment, not any one person's account — the same standing the
 * accessibility reports take — so it is typed here and sent as the bearer
 * on the two oversight doors, never stored beside a user's session. The
 * queue's own words (titles, descriptions, patches, notes) are the
 * server's and render verbatim; every word of chrome runs through the
 * console's ten-language table.
 */
export function Oversight() {
  const lang = visitorLang();
  const [reviewer, setReviewer] = useState("");
  const [awaiting, setAwaiting] = useState<AppEdit[]>([]);
  const [queued, setQueued] = useState<AppEdit[]>([]);
  const [posture, setPosture] = useState<AppEditPosture | null>(null);
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [loaded, setLoaded] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!reviewer.trim()) return;
    setBusy(true); setError(null);
    try {
      const q = await api.oversightQueue(reviewer.trim());
      setAwaiting(q.awaiting); setQueued(q.queued); setPosture(q.posture);
      setLoaded(true);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }, [reviewer]);

  async function decide(edit: AppEdit, action: "approve" | "reject") {
    setBusy(true); setError(null);
    try {
      await api.oversightDecide(edit.id, { action, note: notes[edit.id] || "" },
                                reviewer.trim());
      await load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <section className="screen" data-screen="45">
      <h2>{tr("ov.title", lang)}</h2>
      <p className="muted">{tr("ov.sub", lang)}</p>

      <div className="card">
        <label>{tr("ov.token", lang)}
          <input type="password" value={reviewer}
                 placeholder={tr("ov.token.ph", lang)}
                 onChange={(e) => setReviewer(e.target.value)} />
        </label>
        <button disabled={busy || !reviewer.trim()} onClick={() => void load()}>
          {tr("ov.load", lang)}
        </button>
        {error && <div className="error">{error}</div>}
      </div>

      {posture && (
        <div className="card">
          <p className="muted small">
            {posture.lane === "cloud" ? tr("ov.posture.cloud", lang) : tr("ov.posture.self", lang)}
            {" "}
            {tr("ov.posture.apply", lang)}
          </p>
        </div>
      )}

      {loaded && (<>
        <h3>{tr("ov.awaiting", lang)} <span className="muted small">{awaiting.length}</span></h3>
        {awaiting.length === 0 && <p className="muted small">{tr("ov.none", lang)}</p>}
        {awaiting.map((e) => (
          <div key={e.id} className="card">
            <strong>{e.title}</strong>
            <p style={{ whiteSpace: "pre-wrap" }}>{e.description}</p>
            {e.target && (
              <p className="muted small">{tr("ov.target", lang)} <code>{e.target}</code></p>
            )}
            {e.patch && (<>
              <p className="muted small">{tr("ov.patch", lang)}</p>
              <pre style={{ whiteSpace: "pre-wrap", maxHeight: 240, overflow: "auto" }}>{e.patch}</pre>
            </>)}
            {e.model && (
              <p className="muted small">{tr("ov.by", lang)} <code>{e.model}</code></p>
            )}
            {/* What the assistant's box made of the draft, when it was
                tried: the outcome, the rounds, the tests it named and the
                tail of what they said — a fact beside the diff, never a
                decision. A draft nobody tried says so. */}
            {e.box ? (<>
              <p className="muted small">
                {tr("ov.box", lang)}{" "}
                <b>{tr(`edit.box.status.${e.box.status}`, lang)}</b>
                {" · "}{e.box.rounds} {tr("edit.box.rounds", lang)}
                {" · "}{e.box.tests.length} {tr("edit.box.tests", lang)}
                {e.box.passed != null && <> · {e.box.passed} {tr("edit.box.passed", lang)}</>}
                {e.box.failed != null && e.box.failed > 0 && <> · {e.box.failed} {tr("edit.box.failed", lang)}</>}
                {e.box.detail && <> · {e.box.detail}</>}
              </p>
              {e.box.output && (
                <details>
                  <summary className="muted small">{tr("edit.box.output", lang)}</summary>
                  <pre style={{ whiteSpace: "pre-wrap", maxHeight: 200, overflow: "auto" }}>{e.box.output}</pre>
                </details>
              )}
            </>) : (
              <p className="muted small">{tr("ov.box", lang)} {tr("edit.box.untried", lang)}</p>
            )}
            <textarea rows={2} placeholder={tr("ov.note.ph", lang)}
                      value={notes[e.id] || ""}
                      onChange={(ev) => setNotes({ ...notes, [e.id]: ev.target.value })} />
            <div className="row">
              <button disabled={busy} onClick={() => void decide(e, "approve")}>
                {tr("ov.approve", lang)}
              </button>
              <button disabled={busy} className="secondary"
                      onClick={() => void decide(e, "reject")}>
                {tr("ov.reject", lang)}
              </button>
            </div>
          </div>
        ))}

        <h3>{tr("ov.queued", lang)} <span className="muted small">{queued.length}</span></h3>
        {queued.length === 0 && <p className="muted small">{tr("ov.none", lang)}</p>}
        {queued.map((e) => (
          <div key={e.id} className="card">
            <strong>{e.title}</strong>
            <p className="muted small">
              {tr("ov.decided", lang)} {e.decided_at}
              {e.note && <> · {e.note}</>}
            </p>
          </div>
        ))}
      </>)}
    </section>
  );
}
