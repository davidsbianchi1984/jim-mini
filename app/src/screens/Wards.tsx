import { useEffect, useState } from "react";
import { api, type ChildDetail, type GuardianWatch,
         type WaiverOffer } from "../api";
import { useSession } from "../store";

/**
 * The people you are answerable for — a child's account, what an adult may
 * see of it, and the one waiver that lets a machine act without asking.
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
  const [watch, setWatch] = useState<GuardianWatch | null>(null);
  const [open, setOpen] = useState<ChildDetail | null>(null);
  const [waiver, setWaiver] = useState<WaiverOffer | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [relationship, setRelationship] =
    useState<"parent" | "legal_guardian">("parent");
  const [signature, setSignature] = useState("");

  const uid = session.userId;
  const token = session.userToken;

  function load() {
    if (!uid || !token) return;
    api.guardianWatch(uid, token).then(setWatch).catch(fail);
    api.children(uid, token).catch(fail);
    api.waivers(uid, token).then(setWaiver).catch(fail);
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
        <h2>Who you watch</h2>
        <span className="muted small">children linked to this account</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>Link a child</h3>
        <div className="row">
          <input value={name} placeholder="Their name"
                 onChange={(e) => setName(e.target.value)} />
          <input value={birthdate} type="date"
                 onChange={(e) => setBirthdate(e.target.value)} />
          <select value={relationship}
                  onChange={(e) => setRelationship(
                    e.target.value as "parent" | "legal_guardian")}>
            <option value="parent">I am their parent</option>
            <option value="legal_guardian">I am their legal guardian</option>
          </select>
          <button className="primary"
                  disabled={busy || !name.trim() || !birthdate}
                  onClick={() => run(async () => {
                    await api.addChild(uid!, {
                      display_name: name.trim(), birthdate,
                      relationship }, token!);
                    setName(""); setBirthdate("");
                  })}>Link</button>
        </div>
        <p className="muted small">
          The child gets their own account and their own token — this links
          you to it, it does not make their record yours to read line by line.
          What you can see is on this page and nothing else.
        </p>
      </div>

      <div className="card">
        <h3>The board</h3>
        {children.length === 0 && (
          <div className="muted small">Nobody linked.</div>
        )}
        {children.map((c) => (
          <div key={c.child_id}
               style={{ padding: "10px 0", borderBottom: "1px solid var(--line)" }}>
            <div className="row">
              <span className={"dot-" + (c.light === "green" ? "online" : "warn")}>●</span>
              <strong style={{ flex: 1 }}>{c.display_name}</strong>
              <span className="muted small">
                {c.age != null ? `${c.age} · ` : ""}{c.oversight} oversight
                {c.paused ? " · paused" : ""}
                {c.quiet_hours ? ` · quiet ${c.quiet_hours}` : ""}
              </span>
            </div>
            <div className="muted small">
              {c.critical_24h ?? 0} critical · {c.escalations_24h ?? 0}{" "}
              escalations in the last day
            </div>
            <div className="row">
              <button disabled={busy}
                      onClick={() => run(async () => {
                        setOpen(await api.child(uid!, c.child_id, token!));
                      })}>Open</button>
              <button disabled={busy}
                      onClick={() => run(async () => {
                        const r = await api.setChildControls(
                          uid!, c.child_id, { paused: !c.paused }, token!);
                        setNote(r.note);
                      })}>
                {c.paused ? "Resume guidance" : "Pause guidance"}
              </button>
              <button disabled={busy}
                      onClick={() => run(async () => {
                        const r = await api.setChildControls(
                          uid!, c.child_id,
                          { quiet_start: "21:00", quiet_end: "07:00" },
                          token!);
                        setNote(r.note);
                      })}>Quiet 9pm–7am</button>
              <button disabled={busy}
                      onClick={() => run(() =>
                        api.removeChild(uid!, c.child_id, token!))}>
                Unlink
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
            {open.age} · {open.relationship} · {open.oversight} oversight ·{" "}
            {open.sensitivity} sensitivity · {open.critical_events} critical
            events on record
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

      <div className="card">
        <h3>{waiver?.kind === "autonomous_resuscitation"
              ? "Automatic resuscitation" : "Waiver"}</h3>
        <p className="muted small">
          A bound, CPR-rated robot will not begin without somebody on scene
          saying so — unless you sign this, and then it will. Read all of it.
        </p>
        {(waiver?.terms ?? []).map((t, i) => (
          <div key={i} style={{ padding: "6px 0" }}>· {t}</div>
        ))}
        {waiver?.signed ? (
          <div className="row">
            <span className="muted small">
              Signed as {waiver.signature}. Withdrawing restores the
              confirm-gated behaviour immediately.
            </span>
            <button disabled={busy}
                    onClick={() => run(() =>
                      api.withdrawWaiver(uid!, token!))}>Withdraw</button>
          </div>
        ) : (
          <div className="row">
            <input value={signature} placeholder="Type your full name"
                   onChange={(e) => setSignature(e.target.value)} />
            <button className="primary" disabled={busy || !signature.trim()}
                    onClick={() => run(() => api.signWaiver(uid!, {
                      signature: signature.trim(), accept: true }, token!))}>
              Sign
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
