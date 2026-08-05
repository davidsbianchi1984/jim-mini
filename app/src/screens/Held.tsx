import { useEffect, useState } from "react";
import { api, type AccessLog, type CloudStatus, type Row } from "../api";
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
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [confirm, setConfirm] = useState("");
  const [key, setKey] = useState("journal");

  const uid = session.userId;
  const token = session.userToken;

  function load() {
    if (!uid || !token) return;
    api.accessLog(uid, token).then(setLog).catch(fail);
    api.membership(uid, token).then(setMembership).catch(fail);
    api.plans().then(setPlans).catch(fail);
    api.sources(uid, token).then(setSources).catch(fail);
    api.cloudStatus().then(setCloud).catch(fail);
    api.connectorsCatalog().then(setConnectors).catch(fail);
    // Both of these answer with a refusal on an ordinary deployment — no
    // vault configured, no provider consent given. The refusal is the
    // information, so it is caught and shown rather than thrown away.
    api.custody(uid, token).then(setCustody)
      .catch((e) => setCustodyError((e as Error).message));
    api.providerFor(uid, token).then(setProvider)
      .catch((e) => setProviderError((e as Error).message));
  }
  function fail(e: unknown) { setError((e as Error).message); }
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
            {tr("hld.log.vaulted", lang)} <strong>{log?.vaulted ? "yes" : "no"}</strong>
          </span>
          <span className="muted small">
            {tr("hld.log.kept", lang)}{" "}
            <strong>{log?.access_record_kept ? "yes" : "no"}</strong>
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
              {s.consented ? "Withdraw" : "Allow"}
            </button>
          </div>
        ))}
        <div className="row">
          {["calendar", "mail", "photos", "messages"].map((s) => (
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
      </div>

      <div className="card">
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
