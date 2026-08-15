import { useEffect, useState } from "react";
import { api, type ChildDetail, type GuardianWatch } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The people you are answerable for — a child's account and what an adult
 * may see of it.
 *
 * The autonomous-resuscitation waiver used to be here too, and a field report
 * said what that reads as: *get this out of there, it shouldn't belong in who
 * you watch.* It doesn't — the signer is the subject, and every other card on
 * this screen is about somebody else. It now sits on Safety, under the
 * automatic path it modifies. What stays true here is the rule that put it
 * near the children in the first place: a minor can never have one signed for
 * them, which the server enforces and this screen does not need to host.
 *
 * Nine routes, all of them phone-only until now. Two things the server told
 * us when this was driven, both of which would have been wrong if the
 * bindings had been written from the route table:
 *
 *   * `relationship` on a new child is the **adult's** relationship to the
 *     child, and the server accepts `parent` or `legal_guardian` and nothing
 *     else. "daughter" is a 422. That reads backwards until you notice the
 *     field is on the guardian's side of the link.
 *   * The detail view keys the child as `child_id`, not `id`, and returns a
 *     different document from the one in the listing — an age and an event
 *     history rather than a row.
 *
 * The controls are deliberately narrow, and the server says so in its own
 * response: pausing and quiet hours hold everyday guidance only. Monitoring,
 * crisis escalation and the emergency path never pause. That sentence is
 * printed here rather than paraphrased, because a guardian who believes they
 * have switched the watching off has been told something false.
 */
export function Wards() {
  const { session } = useSession();
  const lang = visitorLang();
  const [watch, setWatch] = useState<GuardianWatch | null>(null);
  const [open, setOpen] = useState<ChildDetail | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [relationship, setRelationship] =
    useState<"parent" | "legal_guardian">("parent");

  const uid = session.userId;
  const token = session.userToken;

  function load() {
    if (!uid || !token) return;
    api.guardianWatch(uid, token).then(setWatch).catch(fail);
    api.children(uid, token).catch(fail);
  }
  function fail(e: unknown) { setError((e as Error).message); }
  useEffect(load, [uid]);

  async function run(work: () => Promise<unknown>) {
    if (!uid || !token) return;
    setBusy(true); setError(null);
    try { await work(); load(); } catch (e) { fail(e); }
    finally { setBusy(false); }
  }

  const children = watch?.children ?? [];

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("wrd.title", lang)}</h2>
        <span className="muted small">{tr("wrd.sub", lang)}</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>{tr("wrd.link", lang)}</h3>
        <div className="row">
          <input value={name} placeholder={tr("wrd.link.name.ph", lang)}
                 onChange={(e) => setName(e.target.value)} />
          <input value={birthdate} type="date"
                 onChange={(e) => setBirthdate(e.target.value)} />
          <select value={relationship}
                  onChange={(e) => setRelationship(
                    e.target.value as "parent" | "legal_guardian")}>
            <option value="parent">{tr("wrd.link.parent", lang)}</option>
            <option value="legal_guardian">{tr("wrd.link.guardian", lang)}</option>
          </select>
          <button className="primary"
                  disabled={busy || !name.trim() || !birthdate}
                  onClick={() => run(async () => {
                    await api.addChild(uid!, {
                      display_name: name.trim(), birthdate,
                      relationship }, token!);
                    setName(""); setBirthdate("");
                  })}>{tr("wrd.link.go", lang)}</button>
        </div>
        <p className="muted small">{tr("wrd.link.pitch", lang)}</p>
      </div>

      <div className="card">
        <h3>{tr("wrd.board", lang)}</h3>
        {children.length === 0 && (
          <div className="muted small">{tr("wrd.board.none", lang)}</div>
        )}
        {children.map((c) => (
          <div key={c.child_id}
               style={{ padding: "10px 0", borderBottom: "1px solid var(--line)" }}>
            <div className="row">
              <span className={"dot-" + (c.light === "green" ? "online" : "warn")}>●</span>
              <strong style={{ flex: 1 }}>{c.display_name}</strong>
              <span className="muted small">
                {c.age != null ? `${c.age} · ` : ""}
                {tr("wrd.board.oversight", lang)
                  .replace("{oversight}", String(c.oversight))}
                {c.paused ? tr("wrd.paused.mark", lang) : ""}
                {c.quiet_hours ? ` · quiet ${c.quiet_hours}` : ""}
              </span>
            </div>
            <div className="muted small">
              {tr("wrd.board.counts", lang)
                .replace("{critical}", String(c.critical_24h ?? 0))
                .replace("{escalations}", String(c.escalations_24h ?? 0))}
            </div>
            <div className="row">
              <button disabled={busy}
                      onClick={() => run(async () => {
                        setOpen(await api.child(uid!, c.child_id, token!));
                      })}>{tr("wrd.board.open", lang)}</button>
              <button disabled={busy}
                      onClick={() => run(async () => {
                        const r = await api.setChildControls(
                          uid!, c.child_id, { paused: !c.paused }, token!);
                        setNote(r.note);
                      })}>
                {c.paused ? tr("wrd.resume", lang) : tr("wrd.pause", lang)}
              </button>
              <button disabled={busy}
                      onClick={() => run(async () => {
                        const r = await api.setChildControls(
                          uid!, c.child_id,
                          { quiet_start: "21:00", quiet_end: "07:00" },
                          token!);
                        setNote(r.note);
                      })}>{tr("wrd.board.quiet", lang)}</button>
              <button disabled={busy}
                      onClick={() => run(() =>
                        api.removeChild(uid!, c.child_id, token!))}>
                {tr("wrd.board.unlink", lang)}
              </button>
            </div>
          </div>
        ))}
        {note && <p className="muted small">{note}</p>}
      </div>

      {open && (
        <div className="card">
          <h3>{open.display_name}</h3>
          <div className="muted small">
            {tr("wrd.detail", lang)
              .replace("{age}", String(open.age))
              .replace("{relationship}", String(open.relationship))
              .replace("{oversight}", String(open.oversight))
              .replace("{sensitivity}", String(open.sensitivity))
              .replace("{critical}", String(open.critical_events))}
          </div>
          {open.privacy_note && (
            <p className="muted small">{open.privacy_note}</p>
          )}
          {open.events.map((e, i) => (
            <div key={i} className="row"
                 style={{ padding: "6px 0", borderBottom: "1px solid var(--line)" }}>
              <span style={{ flex: 1 }}>{e.type}</span>
              <span className="muted small">
                {e.condition ?? ""} {e.severity ?? ""}{" "}
                {new Date(e.created_at).toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
