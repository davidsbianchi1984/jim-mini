import { useCallback, useEffect, useState } from "react";
import {
  api, type AlarmRow, type BeaconRow, type IncidentRow, type PageRow,
} from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The answering end of the crash watch.
 *
 * JIM could already raise an alarm — an unanswered check-in, a scanned
 * beacon, a fall through the watch drip — and every route for *resolving*
 * one had existed for versions with nothing calling it. Accepting an alarm,
 * clearing it, escalating it, seeing which pages went out and which
 * incidents were recorded: all reachable from the backend, none reachable
 * from a person. An alarm nobody can answer is worse than no alarm at all,
 * because the system has told somebody help is coming.
 *
 * Three things here are deliberate:
 *
 * - **Open alarms first, and separately.** Arriving at this screen during an
 *   emergency, the only question is what still needs a human. History is
 *   below the fold, not mixed in.
 * - **Accepting names a responder.** The backend requires it, and it is the
 *   right requirement: "someone is coming" is not a state, it is a person.
 * - **Escalation is not hidden behind a confirm.** In the moment it is
 *   needed, a modal is an obstacle. Clearing is the one that asks, because
 *   clearing is the irreversible direction.
 */
export function Safety() {
  const { session } = useSession();
  const lang = visitorLang();
  const [alarms, setAlarms] = useState<AlarmRow[]>([]);
  const [incidents, setIncidents] = useState<IncidentRow[]>([]);
  const [pages, setPages] = useState<PageRow[]>([]);
  const [beacons, setBeacons] = useState<BeaconRow[]>([]);
  const [responder, setResponder] = useState("");
  const [label, setLabel] = useState("");
  const [placement, setPlacement] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uid = session.userId;
  const token = session.userToken;

  const load = useCallback(() => {
    if (!uid || !token) return;
    setError(null);
    api.alarms(uid, token).then(setAlarms)
      .catch((e) => setError((e as Error).message));
    api.incidents(uid, token).then(setIncidents).catch(() => setIncidents([]));
    api.pages(uid, token).then(setPages).catch(() => setPages([]));
    api.beacons(uid, token).then(setBeacons).catch(() => setBeacons([]));
  }, [uid, token]);
  useEffect(load, [load]);

  async function run(action: () => Promise<unknown>) {
    setBusy(true); setError(null);
    try {
      await action();
      load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  // "open" is whatever the server has not marked cleared. The state strings
  // are the server's vocabulary, so the check is for the cleared end rather
  // than a list of open ones this screen would have to keep in step.
  const open = alarms.filter((a) => a.state !== "cleared" && !a.cleared_at);
  const past = alarms.filter((a) => a.state === "cleared" || a.cleared_at);

  if (!uid || !token) return <p>{tr("sfy.signin", lang)}</p>;

  return (
    <section className="screen">
      <h2>{tr("sfy.title", lang)}</h2>
      {error && <p className="error">{error}</p>}

      <h3>{tr("sfy.needs", lang)} {open.length > 0 && <span className="pill">{open.length}</span>}</h3>
      {open.length === 0 && <p className="muted">{tr("sfy.needs.none", lang)}</p>}
      {open.map((a) => (
        <div key={a.id} className="card alarm">
          <div className="row">
            <strong>{a.tier}</strong>
            <span className="muted">{a.state}</span>
            {a.created_at && <span className="muted">{a.created_at.slice(0, 16).replace("T", " ")}</span>}
          </div>
          {a.accepted_by
            ? <p>{tr("sfy.onway", lang).replace("{who}", String(a.accepted_by))}</p>
            : (
              <div className="row">
                <input
                  value={responder}
                  placeholder={tr("sfy.responder.ph", lang)}
                  onChange={(e) => setResponder(e.target.value)} />
                <button
                  disabled={busy || !responder.trim()}
                  onClick={() => run(() =>
                    api.acceptAlarm(uid, a.id, responder.trim(), token))}>
                  {tr("sfy.going", lang)}
                </button>
              </div>
            )}
          {(a.messages ?? []).map((m, i) => (
            <p key={i} className="muted">{m.from}: {m.text}</p>
          ))}
          <div className="row">
            <button
              disabled={busy}
              onClick={() => run(() => api.escalateAlarm(uid, a.id, token))}>
              {tr("sfy.escalate", lang)}
            </button>
            <button
              disabled={busy}
              onClick={() => {
                if (confirm("Clear this alarm? Do it only once the person is safe."))
                  run(() => api.clearAlarm(uid, a.id, token));
              }}>
              {tr("sfy.clear", lang)}
            </button>
          </div>
        </div>
      ))}

      <h3>{tr("sfy.beacons", lang)}</h3>
      <p className="muted">{tr("sfy.beacons.pitch", lang)}</p>
      {beacons.map((b) => (
        <div key={b.id} className="card">
          <div className="row">
            <strong>{b.label}</strong>
            {b.placement && <span className="muted">{b.placement}</span>}
            <span className="muted">{tr("sfy.beacons.scans", lang)
              .replace("{n}", String(b.scans))
              .replace("{s}", b.scans === 1 ? "" : "s")}</span>
            {!b.active && <span className="muted">{tr("sfy.beacons.retired", lang)}</span>}
          </div>
          <a href={b.scan_url} target="_blank" rel="noreferrer">{b.scan_url}</a>
        </div>
      ))}
      <div className="row">
        <input value={label} placeholder={tr("sfy.beacons.label.ph", lang)}
          onChange={(e) => setLabel(e.target.value)} />
        <input value={placement} placeholder={tr("sfy.beacons.where.ph", lang)}
          onChange={(e) => setPlacement(e.target.value)} />
        <button
          disabled={busy || !label.trim()}
          onClick={() => run(async () => {
            await api.placeBeacon(uid, {
              label: label.trim(),
              placement: placement.trim() || undefined,
            }, token);
            setLabel(""); setPlacement("");
          })}>
          {tr("sfy.beacons.place", lang)}
        </button>
      </div>

      <h3>{tr("sfy.pages", lang)}</h3>
      <p className="muted">{tr("sfy.pages.pitch", lang)}</p>
      {pages.length === 0 && <p className="muted">{tr("sfy.pages.none", lang)}</p>}
      {pages.map((p, i) => (
        <div key={String(p.id ?? i)} className="card">
          <div className="row">
            <span>{String(p.to ?? "—")}</span>
            <span className="muted">{p.delivered ? "delivered" : "not delivered"}</span>
            {p.sent_at && <span className="muted">{String(p.sent_at).slice(0, 16).replace("T", " ")}</span>}
          </div>
        </div>
      ))}

      <h3>{tr("sfy.history", lang)}</h3>
      {past.length === 0 && incidents.length === 0
        && <p className="muted">{tr("sfy.history.none", lang)}</p>}
      {past.map((a) => (
        <div key={a.id} className="card muted">
          <div className="row">
            <span>{a.tier}</span>
            <span>{tr("sfy.history.cleared", lang)}</span>
            {a.accepted_by && <span>{tr("sfy.history.answered", lang)
              .replace("{who}", String(a.accepted_by))}</span>}
          </div>
        </div>
      ))}
      {incidents.map((it, i) => (
        <div key={String(it.id ?? i)} className="card muted">
          <div className="row">
            <span>{String(it.kind ?? "incident")}</span>
            {it.at && <span>{String(it.at).slice(0, 16).replace("T", " ")}</span>}
          </div>
          {it.detail && <p>{String(it.detail)}</p>}
        </div>
      ))}
    </section>
  );
}
