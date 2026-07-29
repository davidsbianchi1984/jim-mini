import { useEffect, useState } from "react";
import { api, CarePlan, CareTeamStatus } from "../api";
import { useSession } from "../store";

// The care team is an organization (jim/careteam.py): link your own QRME
// org, name the desk that speaks for the Guardian, read the joint plans.
// The owner token is the user's own QRME credential, pasted knowingly —
// it never echoes back, and unlinking deletes it.
export function CareTeam() {
  const { session } = useSession();
  const [status, setStatus] = useState<CareTeamStatus | null>(null);
  const [plans, setPlans] = useState<CarePlan[]>([]);
  const [orgId, setOrgId] = useState("");
  const [deptId, setDeptId] = useState("");
  const [ownerToken, setOwnerToken] = useState("");
  const [goal, setGoal] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Care Team</h2>
        <span className="muted small">your own QRME organization, coordinated by the Guardian</span>
      </header>

      {!status?.linked && (
        <div className="card">
          <h3>Link your organization</h3>
          <p className="muted small">
            Found the org and staff its desks in QRME first, then paste its
            id, the desk that speaks for JIM, and your own QRME owner token.
            The token is stored for coordinations only and deleted when you
            unlink; it is never shown again.
          </p>
          <div className="row">
            <label>Org id<input value={orgId} placeholder="org_…"
                                onChange={(e) => setOrgId(e.target.value)} /></label>
            <label>Department id<input value={deptId} placeholder="dep_…"
                                       onChange={(e) => setDeptId(e.target.value)} /></label>
          </div>
          <div className="row">
            <label>Your QRME owner token
              <input type="password" value={ownerToken} placeholder="pasted, never echoed"
                     onChange={(e) => setOwnerToken(e.target.value)} />
            </label>
            <button className="primary" disabled={busy || !orgId.trim() || !deptId.trim() || !ownerToken.trim()}
                    onClick={link}>Link</button>
          </div>
        </div>
      )}

      {status?.linked && (
        <>
          <div className="card">
            <h3>Linked</h3>
            <p className="muted small">
              org {status.org_id} · desk {status.department_id} · credential held
            </p>
            <p className="muted small">
              When a reading drifts outside your band while doses slip, the
              Guardian takes it to the whole team — once a day at most, on
              the calm path only. Summaries cross, never raw readings.
            </p>
            <div className="row">
              <label>Take a goal to the team by hand
                <input value={goal} placeholder="e.g. plan the recovery week"
                       onChange={(e) => setGoal(e.target.value)} />
              </label>
              <button className="primary" disabled={busy || !goal.trim()} onClick={coordinate}>
                {busy ? "Coordinating…" : "Coordinate"}
              </button>
              <button disabled={busy} onClick={unlink}>Unlink</button>
            </div>
          </div>

          {plans.length === 0 && (
            <div className="card"><p className="muted center">No joint plans yet.</p></div>
          )}
          {plans.slice().reverse().map((p) => (
            <div key={p.id} className="card">
              <h3>{p.goal.length > 70 ? p.goal.slice(0, 70) + "…" : p.goal}</h3>
              <p style={{ whiteSpace: "pre-wrap" }}>{p.plan}</p>
              <p className="muted small">
                {p.sealed_in_qrme_vault ? "sealed in the vault · " : ""}
                {new Date(p.created_at).toLocaleString()}
              </p>
            </div>
          ))}
        </>
      )}

      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
