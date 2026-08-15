import { useEffect, useState } from "react";
import { api, CarePlan, CareTeamStatus, SpecialistFound } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

// The care team is an organization (jim/careteam.py): link your own QRME
// org, name the desk that speaks for the Guardian, read the joint plans.
// The owner token is the user's own QRME credential, pasted knowingly —
// it never echoes back, and unlinking deletes it.
//: The sentinel a condition's picker carries while it is asking for somebody
//: who is not on the shelf. A value rather than a separate boolean per row,
//: so the picker stays one control and the Attach button can refuse it
//: without needing to know which row opened the search.
const OTHER = "__other__";

export function CareTeam() {
  const { session } = useSession();
  const lang = visitorLang();
  const [status, setStatus] = useState<CareTeamStatus | null>(null);
  const [plans, setPlans] = useState<CarePlan[]>([]);
  const [orgId, setOrgId] = useState("");
  const [deptId, setDeptId] = useState("");
  const [ownerToken, setOwnerToken] = useState("");
  const [goal, setGoal] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [catalog, setCatalog] =
    useState<Awaited<ReturnType<typeof api.specialistsCatalog>> | null>(null);
  const [picks, setPicks] = useState<Record<string, string>>({});
  const [note, setNote] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [found, setFound] = useState<SpecialistFound[]>([]);
  const [searched, setSearched] = useState(false);
  const [capped, setCapped] = useState(false);
  const [limit, setLimit] = useState(0);

  const uid = session.userId!;
  const token = session.userToken!;

  function load() {
    api.careTeamStatus(uid, token).then(setStatus).catch((e) => setError((e as Error).message));
    api.careTeamPlans(uid, token).then(setPlans).catch(() => setPlans([]));
  }
  useEffect(load, [uid]);

  async function link() {
    setBusy(true); setError(null);
    try {
      await api.careTeamLink(uid, token, {
        org_id: orgId.trim(), department_id: deptId.trim(),
        owner_token: ownerToken.trim(),
      });
      setOwnerToken("");           // out of the field the moment it's stored
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function unlink() {
    setBusy(true); setError(null);
    try { await api.careTeamUnlink(uid, token); load(); }
    catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function coordinate() {
    setBusy(true); setError(null);
    try {
      await api.careTeamCoordinate(uid, token, goal.trim());
      setGoal(""); load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  function loadCatalog() {
    api.specialistsCatalog().then(setCatalog).catch(() => setCatalog(null));
  }
  useEffect(loadCatalog, []);

  async function search() {
    const q = query.trim();
    if (!q) return;
    setBusy(true); setError(null);
    try {
      const out = await api.searchSpecialists(q);
      setFound(out.results);
      setCapped(out.capped);
      setLimit(out.limit);
      setSearched(true);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function attach(condition: string) {
    const pid = picks[condition];
    // A starter, or something the search turned up. Looked for in both
    // rather than only the shelf: reading the pick out of `starters` alone
    // is what made every found profile silently unattachable — the click
    // did nothing and said nothing.
    const pick = catalog?.starters.find((s) => s.profile_id === pid)
      || found.find((f) => f.profile_id === pid);
    if (!pid || pid === OTHER || !pick) return;
    setBusy(true); setError(null); setNote(null);
    try {
      await api.attachSpecialist({ condition, mode: "tandem",
        qrme_profile_id: pid, label: pick.display_name });
      setNote(`${pick.display_name} now stands behind ${condition.replace("_", " ")} — their industry knowledge pack rides along.`);
      loadCatalog();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  // Any row asking for somebody off the shelf opens the one search below.
  const seeking = Object.values(picks).includes(OTHER);

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("ct.title", lang)}</h2>
        <span className="muted small">{tr("ct.sub", lang)}</span>
      </header>

      {!status?.linked && (
        <div className="card">
          <h3>{tr("ct.link", lang)}</h3>
          <p className="muted small">{tr("ct.link.pitch", lang)}</p>
          <div className="row">
            <label>{tr("ct.link.org", lang)}<input value={orgId} placeholder={tr("ct.link.org.ph", lang)}
                                onChange={(e) => setOrgId(e.target.value)} /></label>
            <label>{tr("ct.link.dept", lang)}<input value={deptId} placeholder={tr("ct.link.dept.ph", lang)}
                                       onChange={(e) => setDeptId(e.target.value)} /></label>
          </div>
          <div className="row">
            <label>{tr("ct.link.token", lang)}
              <input type="password" value={ownerToken} placeholder={tr("ct.link.token.ph", lang)}
                     onChange={(e) => setOwnerToken(e.target.value)} />
            </label>
            <button className="primary" disabled={busy || !orgId.trim() || !deptId.trim() || !ownerToken.trim()}
                    onClick={link}>{tr("ct.link.go", lang)}</button>
          </div>
        </div>
      )}

      {status?.linked && (
        <>
          <div className="card">
            <h3>{tr("ct.linked", lang)}</h3>
            <p className="muted small">
              {tr("ct.linked.line", lang)
                .replace("{org}", String(status.org_id))
                .replace("{desk}", String(status.department_id))}
            </p>
            <p className="muted small">{tr("ct.linked.pitch", lang)}</p>
            <div className="row">
              <label>{tr("ct.linked.goal", lang)}
                <input value={goal} placeholder={tr("ct.linked.goal.ph", lang)}
                       onChange={(e) => setGoal(e.target.value)} />
              </label>
              <button className="primary" disabled={busy || !goal.trim()} onClick={coordinate}>
                {busy ? tr("ct.coordinating", lang) : tr("ct.coordinate", lang)}
              </button>
              <button disabled={busy} onClick={unlink}>{tr("ct.linked.unlink", lang)}</button>
            </div>
          </div>

          {plans.length === 0 && (
            <div className="card"><p className="muted center">{tr("ct.plans.none", lang)}</p></div>
          )}
          {plans.slice().reverse().map((p) => (
            <div key={p.id} className="card">
              <h3>{p.goal.length > 70 ? p.goal.slice(0, 70) + "…" : p.goal}</h3>
              <p style={{ whiteSpace: "pre-wrap" }}>{p.plan}</p>
              <p className="muted small">
                {p.sealed_in_qrme_vault ? tr("ct.sealed", lang) : ""}
                {new Date(p.created_at).toLocaleString()}
              </p>
            </div>
          ))}
        </>
      )}

      {catalog && (
        <div className="card">
          <h3>{tr("ct.spec", lang)}</h3>
          <p className="muted small">{tr("ct.spec.pitch", lang)}</p>
          {catalog.conditions.map((c) => (
            <div key={c.condition} className="spec-row spec-block">
              <b className="spec-cond">{c.condition.replace("_", " ")}</b>
              <span className="muted small spec-now">
                {c.attached
                  ? `${c.attached.label || "attached"} (${c.attached.mode})`
                  : tr("ct.nobody", lang)}
              </span>
              <select value={picks[c.condition] || ""}
                      onChange={(e) => setPicks((cur) => ({ ...cur, [c.condition]: e.target.value }))}>
                <option value="">{tr("ct.spec.choose", lang)}</option>
                {catalog.starters.map((st) => (
                  <option key={st.profile_id} value={st.profile_id}>
                    {st.display_name}{st.tags?.[0] ? ` — ${st.tags[0]}` : ""}
                  </option>
                ))}
                {/* The shelf is the curated bracket and the right first
                    answer. It is the wrong *only* answer: somebody who
                    already sees a physiotherapist, or who was handed a
                    handle, had no way in at all. */}
                {found.map((f) => (
                  <option key={f.profile_id} value={f.profile_id}>
                    {f.display_name}{f.purpose ? ` — ${f.purpose}` : ""}
                  </option>
                ))}
                <option value={OTHER}>{tr("ct.spec.other", lang)}</option>
              </select>
              <button disabled={busy || !picks[c.condition]
                                || picks[c.condition] === OTHER}
                      onClick={() => attach(c.condition)}>{tr("ct.spec.attach", lang)}</button>
            </div>
          ))}

          {/* Shown once the moment any condition asks for somebody else,
              rather than repeated under every row: one search serves all of
              them, and the result is attachable from whichever row asked. */}
          {seeking && (
            <div className="spec-find">
              <input value={query} placeholder={tr("ct.spec.find.hint", lang)}
                     onChange={(e) => setQuery(e.target.value)}
                     onKeyDown={(e) => { if (e.key === "Enter") search(); }} />
              <button disabled={busy || !query.trim()} onClick={search}>
                {tr("ct.spec.find.go", lang)}
              </button>
              {searched && found.length === 0 && (
                <p className="muted small">{tr("ct.spec.find.none", lang)}</p>
              )}
              {capped && (
                <p className="muted small">
                  {tr("ct.spec.find.capped", lang).replace("{n}", String(limit))}
                </p>
              )}
              <ul className="plain">
                {found.map((f) => (
                  <li key={f.profile_id}>
                    <b>{f.display_name}</b>
                    {f.purpose ? <span className="muted"> — {f.purpose}</span> : null}
                    {/* Written as separate literal lookups rather than one
                        call on an expression: the console's dead-key guard
                        reads literal arguments, and a key reached only
                        through a lookup table reads to it as translated and
                        never used. */}
                    {f.standing === "specialist.departed" && (
                      <em className="danger small"> {tr("ct.spec.stand.departed", lang)}</em>
                    )}
                    {f.standing === "specialist.not_active" && (
                      <em className="danger small"> {tr("ct.spec.stand.not_active", lang)}</em>
                    )}
                    {f.standing === "specialist.adults_only" && (
                      <em className="warn small"> {tr("ct.spec.stand.adults_only", lang)}</em>
                    )}
                    {f.standing === "specialist.unreachable" && (
                      <em className="muted small"> {tr("ct.spec.stand.unreachable", lang)}</em>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {catalog.starters.length === 0 && (
            <p className="muted small">{tr("ct.spec.empty", lang)}</p>
          )}
        </div>
      )}

      {note && <div className="ok-note">{note}</div>}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
