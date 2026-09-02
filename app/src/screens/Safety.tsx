import { useCallback, useEffect, useState } from "react";
import {
  api, type AlarmRow, type BeaconRow, type CrashWatchStatus,
  type IncidentRow, type PageRow, type WaiverOffer,
} from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The safety front door — reframed by a field report.
 *
 * The report, in its own words: "say if you collapse on the floor and
 * needed help and assistance how are you gonna put a sticker on a door".
 * This screen used to lead with beacons — the *bystander's* path — while
 * the person collapsing had no button at all: the coordinated emergency
 * response existed on the backend and its only console door was on the
 * carer's screen. So the screen now runs in the order of who is pressing:
 *
 * - **Get help now** leads: the account holder's own dispatch-help press,
 *   driving `POST /emergency/{uid}` — emergency contact, Medical ID,
 *   first aid, every connected device — and rendering the server's own
 *   honest note that JIM cannot dial 911 itself.
 * - **When you can't answer** is the automatic path: the crash watch's
 *   live status, and where to arm it if it is not.
 * - **Beacons are the bystander's path** and now say so, below the doors
 *   the person themselves can press.
 *
 * The rest is the answering end, unchanged: open alarms first, accepting
 * names a responder, escalation is never behind a confirm. First-aid and
 * crisis sentences stay the server's English, rendered verbatim — the
 * house rule on safety text — while the chrome around them translates.
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
  const [situation, setSituation] = useState("");
  const [sent, setSent] = useState<Record<string, unknown> | null>(null);
  const [watch, setWatch] = useState<CrashWatchStatus | null>(null);
  const [waiver, setWaiver] = useState<WaiverOffer | null>(null);
  const [signature, setSignature] = useState("");

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
    api.crashWatch(uid, token).then(setWatch).catch(() => setWatch(null));
    api.waivers(uid, token).then(setWaiver).catch(() => setWaiver(null));
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

      <h3>{tr("sfy.help", lang)}</h3>
      <p className="muted">{tr("sfy.help.pitch", lang)}</p>
      <div className="card">
        <div className="row">
          <input value={situation} placeholder={tr("sfy.help.ph", lang)}
            onChange={(e) => setSituation(e.target.value)} />
          <button className="primary" disabled={busy}
            onClick={() => run(async () => {
              setSent(await api.raiseEmergency(uid, {
                situation: situation.trim() || undefined,
              }, token) as Record<string, unknown>);
            })}>
            {tr("sfy.help.go", lang)}
          </button>
        </div>
        {sent && (
          <>
            {/* The server's own words, verbatim and first: what it cannot
                do. Safety sentences stay English by house rule. */}
            {(() => {
              const call = sent.call_emergency_services as
                Record<string, string> | undefined;
              return call && (
                <p><strong>{call.action} — {call.number}.</strong>{" "}
                  {call.note}</p>
              );
            })()}
            {(() => {
              const fam = sent.contact_family as
                Record<string, unknown> | null | undefined;
              return fam
                ? <p>{tr("sfy.help.contacted", lang)
                    .replace("{who}", String(fam.name ?? fam.phone ?? ""))}</p>
                : <p className="muted">{tr("sfy.help.nocontact", lang)}</p>;
            })()}
            {(() => {
              const g = sent.ai_guidance as
                Record<string, unknown> | null | undefined;
              return g?.content
                ? <p className="muted">{String(g.content)}</p> : null;
            })()}
            {Array.isArray(sent.dispatched_alerts)
              && sent.dispatched_alerts.length > 0 && (
              <p className="muted">{tr("sfy.help.devices", lang)
                .replace("{n}", String(sent.dispatched_alerts.length))}</p>
            )}
          </>
        )}
      </div>

      <h3>{tr("sfy.auto", lang)}</h3>
      {watch?.armed ? (
        <p className="muted">
          {tr("sfy.auto.on", lang)
            .replace("{who}", String(watch.trusted_name ?? ""))
            .replace("{n}", String(watch.attempts ?? ""))}
          {watch.contact_emergency_services === true
            && <> {tr("sfy.auto.also", lang)}</>}
        </p>
      ) : (
        <p className="muted">{tr("sfy.auto.off", lang)}</p>
      )}

      {/* The waiver that lets a machine act without asking — here, directly
          under the automatic path it modifies.

          It used to sit on Wards, among a child's account and what an adult
          may see of it, and a field report said what that reads as: *get this
          out of there, it shouldn't belong in who you watch.* It doesn't. The
          waiver is signed by the account holder about their own body; every
          other card on that screen is about somebody else's. It landed there
          for a reason that was never the reader's — a minor can never have
          one signed for them, so the rule lives near the children — but a rule
          about who may not sign is not a reason to file the signing beside
          them.

              asked     why is resuscitation on the screen about my wards
              mattered  the signer is the subject, and that is this screen

          Reuses this screen's `run()` and `busy`, and the existing `wrd.*`
          keys: the sentences were already right, only the room was wrong. */}
      <div className="card">
        <h3>{waiver?.kind === "autonomous_resuscitation"
              ? tr("wrd.resus", lang) : tr("wrd.waiver", lang)}</h3>
        <p className="muted small">{tr("wrd.waiver.pitch", lang)}</p>
        {(waiver?.terms ?? []).map((t, i) => (
          <div key={i} style={{ padding: "6px 0" }}>· {t}</div>
        ))}
        {waiver?.signed ? (
          <div className="row">
            <span className="muted small">
              {tr("wrd.waiver.signed", lang)
                .replace("{signature}", String(waiver.signature))}
            </span>
            <button disabled={busy}
                    onClick={() => run(() =>
                      api.withdrawWaiver(uid!, token!))}>
              {tr("wrd.waiver.withdraw", lang)}
            </button>
          </div>
        ) : (
          <div className="row">
            <input value={signature} placeholder={tr("wrd.waiver.sig.ph", lang)}
                   onChange={(e) => setSignature(e.target.value)} />
            <button className="primary" disabled={busy || !signature.trim()}
                    onClick={() => run(() => api.signWaiver(uid!, {
                      signature: signature.trim(), accept: true }, token!))}>
              {tr("wrd.waiver.sign", lang)}
            </button>
          </div>
        )}
      </div>

      <h3>{tr("sfy.needs", lang)} {open.length > 0 && <span className="pill">{open.length}</span>}</h3>
      {open.length === 0 && <p className="muted">{tr("sfy.needs.none", lang)}</p>}
      {open.map((a) => (
        <div key={a.id} className="card alarm">
          <div className="row">
            <strong>{a.tier}</strong>
            <span className="muted">{a.state}</span>
            {a.created_at && <span className="muted">{a.created_at.slice(0, 16).replace("T", " ")}</span>}
          </div>
          {/* Above the accept row, because it is the thing to do while
              deciding whether to press anything here at all. True on every
              row: a beacon alarm is ceilinged below emergency services, and a
              crash watch at the top rung issued a dispatch request, not a
              call. The stranger's page has said this since it shipped. */}
          {a.call_emergency_services_yourself && (
            <p className="error"><strong>{tr("sfy.cannotdial", lang)}</strong></p>
          )}
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
          {/* Strings, the queue's one shape — a finder's words on a beacon
              alarm, or the crash watch's own sentence. This used to read
              `m.from: m.text` off a shape the server never sent, and every
              beacon message rendered as ": ". */}
          {(a.alert_texts ?? []).map((m, i) => (
            <p key={i} className="muted">{String(m)}</p>
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
      <p className="muted">{tr("sfy.beacons.bystander", lang)}</p>
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
            <span className="muted">{p.delivered ? tr("sfy.delivered", lang)
                             : tr("sfy.undelivered", lang)}</span>
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
