import { useEffect, useState } from "react";
import { api, type AccessLog, type AuditLog, type CloudStatus, type Row,
         type VoiceQuota } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * What is held about you, who holds it, who has read it, and the button
 * that ends all of it.
 *
 * Thirteen routes. The one that mattered most is the one driving caught:
 *
 *     GET /access-log/{uid}
 *
 * It looks like a list and it is not. It answers
 * `{vaulted, access_record_kept, entries, note}` — and on a deployment with
 * no vault, `entries` is empty **because nothing is being recorded**, not
 * because nobody has read anything. Those two are opposite facts and the
 * array alone cannot tell them apart. A binding typed `Row[]` would have
 * mapped over an object, rendered nothing, and shown an empty access log to
 * a user asking who had seen their record. That is the worst available way
 * for this particular screen to fail, so the three fields around `entries`
 * are shown first and the entries second.
 *
 * The same principle runs through the rest: the plan is displayed with its
 * storage posture, not just its price, because what you are buying here is
 * mostly who can read the thing.
 */
export function Held() {
  const { session } = useSession();
  const lang = visitorLang();
  const [log, setLog] = useState<AccessLog | null>(null);
  const [audit, setAudit] = useState<AuditLog | null>(null);
  const [membership, setMembership] = useState<Row | null>(null);
  const [plans, setPlans] = useState<Row | null>(null);
  const [sources, setSources] = useState<Row[]>([]);
  const [custody, setCustody] = useState<Row | null>(null);
  const [custodyError, setCustodyError] = useState<string | null>(null);
  const [provenance, setProvenance] = useState<Row | null>(null);
  const [cloud, setCloud] = useState<CloudStatus | null>(null);
  const [connectors, setConnectors] = useState<Row | null>(null);
  const [provider, setProvider] = useState<Row | null>(null);
  const [providerError, setProviderError] = useState<string | null>(null);
  const [quota, setQuota] = useState<VoiceQuota | null>(null);
  const [quotaError, setQuotaError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [confirm, setConfirm] = useState("");
  const [key, setKey] = useState("journal");
  const [farend, setFarend] = useState<Row | null>(null);
  const [farendEmail, setFarendEmail] = useState("");

  const uid = session.userId;
  const token = session.userToken;

  function load() {
    if (!uid || !token) return;
    api.accessLog(uid, token).then(setLog).catch(fail);
    api.auditLog(uid, token).then(setAudit).catch(fail);
    api.membership(uid, token).then(setMembership).catch(fail);
    api.plans().then(setPlans).catch(fail);
    api.sources(uid, token).then(setSources).catch(fail);
    api.cloudStatus().then(setCloud).catch(fail);
    api.connectorsCatalog().then(setConnectors).catch(fail);
    api.farEnd(uid, token).then(setFarend).catch(fail);
    // Both of these answer with a refusal on an ordinary deployment — no
    // vault configured, no provider consent given. The refusal is the
    // information, so it is caught and shown rather than thrown away.
    api.custody(uid, token).then(setCustody)
      .catch((e) => setCustodyError((e as Error).message));
    api.providerFor(uid, token).then(setProvider)
      .catch((e) => setProviderError((e as Error).message));
    // Same shape, third time: a deployment on the device voice, or on a
    // provider that publishes no balance, answers 503 here. That is the
    // answer, not a failure of the screen.
    api.voiceQuota().then(setQuota)
      .catch((e) => setQuotaError((e as Error).message));
  }
  function fail(e: unknown) { setError((e as Error).message); }

  // The row's sentence comes from the catalogue the same response carried,
  // not from a second copy kept here: two lists of the same actions is one
  // list and one place for them to disagree. An action with no entry in the
  // catalogue falls back to its own name rather than to a blank, so a row
  // written by something newer than this build is still legible.
  function describe(action: string): string {
    return audit?.catalogue.find((a) => a.action === action)?.description
      ?? action;
  }
  useEffect(load, [uid]);

  async function run(work: () => Promise<unknown>) {
    if (!uid || !token) return;
    setBusy(true); setError(null);
    try { await work(); load(); } catch (e) { fail(e); }
    finally { setBusy(false); }
  }

  const storage = (membership?.storage ?? {}) as Record<string, unknown>;

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("hld.title", lang)}</h2>
        <span className="muted small">{tr("hld.sub", lang)}</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>{tr("hld.log", lang)}</h3>
        <div className="row">
          <span className="muted small">
            {tr("hld.log.vaulted", lang)} <strong>{log?.vaulted ? tr("hld.yes", lang)
                                  : tr("hld.no", lang)}</strong>
          </span>
          <span className="muted small">
            {tr("hld.log.kept", lang)}{" "}
            <strong>{log?.access_record_kept ? tr("hld.yes", lang)
                                             : tr("hld.no", lang)}</strong>
          </span>
        </div>
        {log?.note && <p className="muted small">{log.note}</p>}
        {log && !log.access_record_kept && (
          <p className="muted small">{tr("hld.log.empty", lang)}</p>
        )}
        {(log?.entries ?? []).map((e, i) => (
          <div key={i} style={{ padding: "6px 0", borderBottom: "1px solid var(--line)" }}>
            {JSON.stringify(e)}
          </div>
        ))}
      </div>

      {/* The other half of the same question, and the reason the chain can
          honestly sit outside the export bundle and survive an erase: the
          person can always read what was said about them here.

          The chain's state is stated before the entries, for the reason the
          card above states its three fields first — a list you cannot check
          is a list, and "intact" is what turns these rows into a record. */}
      <div className="card">
        <h3>{tr("hld.audit", lang)}</h3>
        {audit && (
          <p className="muted small">
            {audit.integrity.intact
              ? tr("hld.audit.intact", lang)
              : tr("hld.audit.broken", lang).replace(
                  "{seq}", String(audit.integrity.broken_at_seq ?? "?"))}
          </p>
        )}
        {audit?.retention && (
          <p className="muted small">{audit.retention}</p>
        )}
        {audit && audit.count === 0 && (
          <p className="muted small">{tr("hld.audit.none", lang)}</p>
        )}
        {(audit?.trail ?? []).map((e) => (
          <div key={e.seq} className="row"
               style={{ padding: "6px 0", borderBottom: "1px solid var(--line)" }}>
            <span style={{ flex: 1 }}>
              {describe(e.action)}
              {e.ref ? ` — ${e.ref}` : ""}
            </span>
            <span className="muted small">{e.category}</span>
            <span className="muted small">{e.at}</span>
          </div>
        ))}
        {audit && audit.count === 0 && (
          <>
            <p className="muted small"><strong>{tr("hld.audit.watched", lang)}</strong></p>
            {audit.catalogue.map((a) => (
              <p key={a.action} className="muted small">{a.description}</p>
            ))}
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("hld.plan", lang)}</h3>
        <div className="row">
          <strong style={{ flex: 1 }}>
            {String(membership?.title ?? "…")}
          </strong>
          <span className="muted small">
            ${String(membership?.price_usd ?? 0)}
            {membership?.period ? ` / ${String(membership.period)}` : ""}
          </span>
        </div>
        {storage.title != null && (
          <p className="muted small">
            <strong>{String(storage.title)}</strong> — {String(storage.means)}
          </p>
        )}
        {storage.disclosure != null && (
          <p className="muted small">{String(storage.disclosure)}</p>
        )}
        {Array.isArray(storage.who_can_read) && (
          <p className="muted small">
            {tr("hld.plan.canread", lang).replace("{list}",
              (storage.who_can_read as string[]).join(", "))}
          </p>
        )}
        {/* Whether the gate is actually running. The prices below are what
            each tier will cost; while the beta stands enforcement down,
            nobody is refused for the plan they hold, and a price list that
            cannot say so is quoting a paywall that is not there. */}
        {plans?.enforcing === false && plans?.beta_note != null && (
          <p className="muted small">{String(plans.beta_note)}</p>
        )}
        <div className="row">
          {((plans?.plans ?? []) as Row[]).map((p) => (
            <button key={String(p.plan)} disabled={busy}
                    onClick={() => run(() => api.setMembership(
                      uid!, { plan: String(p.plan) }, token!))}>
              {String(p.title)} · ${String(p.price_usd)}
            </button>
          ))}
          <button disabled={busy}
                  onClick={() => run(() =>
                    api.cancelMembership(uid!, token!))}>{tr("hld.plan.cancel", lang)}</button>
        </div>
      </div>

      {/* The far end of the escalation ladder (jim/farend.py). The status
          line is the API's own sentence: the address alerts really go to,
          or the refusal that nobody stands there today — shown rather than
          smoothed over, because an honest empty room can be fixed. Saving
          carries consent in the same motion; the button's label says so. */}
      <div className="card">
        <h3>{tr("hld.farend", lang)}</h3>
        <p className="muted small">
          {farend?.configured
            ? tr("hld.farend.set", lang).replace("{address}",
                String(farend.address))
            : String(farend?.note ?? "")}
        </p>
        {farend?.last_alert != null && (
          <p className="muted small">
            {((farend.last_alert as Row).acked_at != null
                ? tr("hld.farend.acked", lang)
                : tr("hld.farend.unacked", lang))
              .replace("{condition}",
                String((farend.last_alert as Row).condition))
              .replace("{when}", String((farend.last_alert as Row).sent_at)
                .slice(0, 16).replace("T", " "))}
          </p>
        )}
        <div className="row">
          <input value={farendEmail}
                 placeholder={tr("hld.farend.email.ph", lang)}
                 onChange={(e) => setFarendEmail(e.target.value)} />
          <button disabled={busy || !farendEmail.trim()}
                  onClick={() => run(async () => {
                    setFarend(await api.setFarEnd(uid!,
                      { email: farendEmail.trim(), consent: true }, token!));
                  })}>{tr("hld.farend.save", lang)}</button>
          <button disabled={busy}
                  onClick={() => run(async () => {
                    setFarend(await api.setFarEnd(
                      uid!, { email: null }, token!));
                  })}>{tr("hld.farend.clear", lang)}</button>
        </div>
        <p className="muted small">{tr("hld.farend.pitch", lang)}</p>
      </div>

      <div className="card">
        <h3>{tr("hld.custody", lang)}</h3>
        {custodyError && <p className="muted small">{custodyError}</p>}
        {custody && (
          <p className="muted small">{JSON.stringify(custody)}</p>
        )}
        <div className="row">
          <input value={key} placeholder={tr("hld.custody.key.ph", lang)}
                 onChange={(e) => setKey(e.target.value)} />
          <button disabled={busy || !key.trim()}
                  onClick={() => run(async () => {
                    setProvenance(await api.custodyProvenance(
                      uid!, key.trim(), token!));
                  })}>{tr("hld.custody.where", lang)}</button>
        </div>
        <p className="muted small">{tr("hld.custody.pitch", lang)}</p>
        {provenance && (
          <p className="muted small">{JSON.stringify(provenance)}</p>
        )}
      </div>

      <div className="card">
        <h3>{tr("hld.src", lang)}</h3>
        {sources.length === 0 && (
          <div className="muted small">{tr("hld.src.none", lang)}</div>
        )}
        {sources.map((s, i) => (
          <div key={i} className="row"
               style={{ padding: "6px 0", borderBottom: "1px solid var(--line)" }}>
            <span style={{ flex: 1 }}>{String(s.source)}</span>
            <button disabled={busy}
                    onClick={() => run(() => api.setSources(uid!, {
                      source: String(s.source),
                      consented: !s.consented }, token!))}>
              {s.consented ? tr("hld.src.withdraw", lang)
                : tr("hld.src.allow.button", lang)}
            </button>
          </div>
        ))}
        <div className="row">
          {/* Quick allows. Only names the wire accepts (models.Source):
              "mail" and "photos" sat here for a while and every press was
              a 422 — a button that always refuses is a broken promise with
              a label. A standing test now holds this list to the enum. */}
          {["calendar", "messages", "contacts", "location"].map((s) => (
            <button key={s} disabled={busy}
                    onClick={() => run(() => api.setSources(
                      uid!, { source: s, consented: true }, token!))}>
              {tr("hld.src.allow", lang).replace("{source}", s)}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <h3>{tr("hld.where", lang)}</h3>
        {cloud && (
          <p className="muted small">
            {tr("hld.where.cloud", lang)
              .replace("{model}", cloud.cloud ? String(cloud.model) : "none")
              .replace("{fallback}", String(cloud.fallback))}
          </p>
        )}
        {cloud && <p className="muted small">{cloud.contribution}</p>}
        {providerError
          ? <p className="muted small">{providerError}</p>
          : provider && (
            <p className="muted small">
              {tr("hld.where.provider", lang).replace("{provider}",
                String(provider.provider ?? "—"))}
            </p>
          )}
        <p className="muted small">
          {tr("hld.where.connectors", lang).replace("{n}",
            String(((connectors?.providers ?? []) as Row[]).length))}
        </p>
        {/* The allowance. Until this line existed, a spent one was invisible:
            the send is refused, this console and all three phones fall back
            to the device's own voice on any non-ok status, and the Guardian
            went on talking in a flatter voice with nobody told why. The
            exhausted case says what happens next rather than only that a
            number reached zero — "0 left" is a fact, and "it will read to
            you in the device's own voice from here" is the consequence. */}
        {quotaError && <p className="muted small">{quotaError}</p>}
        {quota && (
          <p className="muted small">
            {/* Each key spelled out at its own `tr` rather than chosen by a
                ternary inside one. The dead-key guard reads literal
                arguments, so a key selected before the call is a key it
                reports as translated into ten languages and read by
                nothing — which is exactly what it says when a screen has
                quietly stopped using one. */}
            {quota.exhausted
              ? tr("hld.where.voice.spent", lang)
                  .replace("{provider}", quota.provider)
              : tr("hld.where.voice", lang)
                  .replace("{provider}", quota.provider)
                  .replace("{left}", quota.left.toLocaleString())
                  .replace("{limit}", quota.limit.toLocaleString())}
            {quota.resets_at && " " + tr("hld.where.voice.resets", lang)
              .replace("{when}", quota.resets_at.slice(0, 10))}
          </p>
        )}
      </div>

      <div className="card">
        <h3>{tr("hld.take", lang)}</h3>
        <p className="muted small">{tr("hld.take.pitch", lang)}</p>
        <div className="row">
          <button className="primary" disabled={busy}
                  onClick={() => run(async () => {
                    // Take it before you can end it: the two belong on one
                    // screen, and until this round only the ending was here.
                    const all = await api.exportEverything(uid!, token!);
                    const blob = new Blob([JSON.stringify(all, null, 2)],
                                          { type: "application/json" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `jim-export-${uid}.json`;
                    a.click();
                    URL.revokeObjectURL(url);
                  })}>
            {tr("hld.take.go", lang)}
          </button>
        </div>

        <h3>{tr("hld.end", lang)}</h3>
        <p className="muted small">{tr("hld.end.pitch", lang)}</p>
        <div className="row">
          <input value={confirm} placeholder={tr("hld.end.ph", lang)}
                 onChange={(e) => setConfirm(e.target.value)} />
          <button className="danger" disabled={busy || confirm !== "erase"}
                  onClick={() => run(() =>
                    api.eraseEverything(uid!, token!))}>
            {tr("hld.end.go", lang)}
          </button>
        </div>
      </div>
    </div>
  );
}
