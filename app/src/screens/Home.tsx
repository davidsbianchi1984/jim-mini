import { useEffect, useState } from "react";
import { api, type BaselineMetric, type ScheduleView } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

export function Home({ go }: {
  go: (t: "monitor" | "coach" | "checkin" | "meds" | "careteam") => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [baseline, setBaseline] = useState<BaselineMetric[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session.userId || !session.userToken) return;
    api.baseline(session.userId, session.userToken).then(setBaseline).catch((e) => setError((e as Error).message));
  }, [session.userId]);

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("hom.title", lang)}</h2>
        <span className="dot-online">{tr("hom.on", lang)}</span>
      </header>

      <div className="profile-hero">
        <div className="orb big" />
        <div>
          <h3>{tr("hom.hi", lang)
            .replace("{name}", String(session.displayName))}</h3>
          <div className="muted">{tr("hom.watching", lang)}</div>
        </div>
      </div>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>{tr("hom.baseline", lang)}</h3>
        {baseline.length === 0 ? (
          <div className="muted">{tr("hom.baseline.none", lang)}</div>
        ) : (
          <table className="tbl">
            <thead><tr><th>{tr("hom.th.metric", lang)}</th><th>{tr("hom.th.value", lang)}</th>
              <th>{tr("hom.th.state", lang)}</th><th>{tr("hom.th.samples", lang)}</th></tr></thead>
            <tbody>
              {baseline.map((m) => (
                <tr key={m.metric}>
                  <td>{m.metric}</td><td className="green">{m.value ?? "—"}</td>
                  <td className="muted">{m.state ?? "—"}</td><td className="muted small">{m.samples ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="actions">
        <button className="primary" onClick={() => go("monitor")}>{tr("hom.go.monitor", lang)}</button>
        <button onClick={() => go("coach")}>{tr("hom.go.coach", lang)}</button>
        <button onClick={() => go("checkin")}>{tr("hom.go.checkin", lang)}</button>
        <button onClick={() => go("meds")}>{tr("hom.go.meds", lang)}</button>
        <button onClick={() => go("careteam")}>{tr("hom.go.careteam", lang)}</button>
      </div>

      <ScheduleCard />
    </div>
  );
}

// The Guardian's calendar, on the front door. Every visible string comes
// from the view's own `labels` — composed server-side in the reader's
// language — because this console has no translation table and its English
// backlog is a ratchet that only shrinks. Until the view loads there is
// nothing to say, so nothing is said.
function ScheduleCard() {
  const { session } = useSession();
  const [view, setView] = useState<ScheduleView | null>(null);
  const [title, setTitle] = useState("");
  const [when, setWhen] = useState("");
  const [where, setWhere] = useState("");
  const [emailMe, setEmailMe] = useState(false);
  const [note, setNote] = useState<string | null>(null);

  async function load() {
    if (!session.userId || !session.userToken) return;
    try {
      setView(await api.scheduleView(session.userId, session.userToken));
    } catch { /* the card stays empty */ }
  }
  useEffect(() => { load(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [session.userId]);

  if (!view) return null;
  const L = view.labels;

  async function book() {
    if (!session.userId || !session.userToken) return;
    setNote(null);
    try {
      await api.scheduleBook(session.userId, {
        title: title.trim(), when: when.trim(),
        where: where.trim() || undefined,
        email_reminder: emailMe,
      }, session.userToken);
      setTitle(""); setWhen(""); setWhere("");
      load();
    } catch (e) { setNote((e as Error).message); }
  }

  async function cancel(id: string) {
    if (!session.userId || !session.userToken) return;
    try {
      await api.scheduleCancel(session.userId, id, session.userToken);
      load();
    } catch (e) { setNote((e as Error).message); }
  }

  return (
    <div className="card">
      <h3>{L.title}</h3>
      <p className="muted small">{view.note}</p>
      <div className="row">
        <label>{L.what}
          <input value={title} onChange={(e) => setTitle(e.target.value)} />
        </label>
        <label>{L.when}
          <input value={when} onChange={(e) => setWhen(e.target.value)} />
        </label>
        <label>{L.where}
          <input value={where} onChange={(e) => setWhere(e.target.value)} />
        </label>
      </div>
      <label className="row">
        <input type="checkbox" checked={emailMe} disabled={!view.email_available}
               onChange={(e) => setEmailMe(e.target.checked)} />
        <span className="muted small">
          {view.email_available ? L.email_me : L.no_email}</span>
      </label>
      <button className="primary" disabled={!title.trim() || !when.trim()}
              onClick={book}>{L.book}</button>
      {view.appointments.length > 0 && <h3>{L.upcoming}</h3>}
      {view.appointments.map((a) => (
        <div key={a.id} className="row" style={{ justifyContent: "space-between" }}>
          <span>{a.title} · <span className="muted small">
            {a.whenat.slice(0, 16).replace("T", " ")}
            {a.whereat ? ` · ${a.whereat}` : ""}</span></span>
          <button onClick={() => cancel(a.id)}>{L.cancel}</button>
        </div>
      ))}
      {note && <div className="muted small">{note}</div>}
    </div>
  );
}
