import { useEffect, useState } from "react";
import { api, type ConditionName, type EscalationPolicy,
         type MedicalIdCode, type RelayChannel, type RelayRoster,
         type RelayRota, type Row, type SessionRow,
         type SpecialistRow } from "../api";
import { useSession } from "../store";

/**
 * Who else is looking — the specialists JIM can hand a thing to, the
 * clinicians a referral can reach, the people a relay would wake, and the
 * ladder it climbs to get to them.
 *
 * Twenty-one routes. One correction came out of driving them:
 * `GET /users/{uid}/referral/clinicians` takes a **required** `condition`
 * query parameter. Without it the call is a 422 every time — a door that
 * opens onto a wall is not a door, and a binding written from the route
 * table would have shipped exactly that.
 *
 * The escalation ladder is shown in full rather than summarised, including
 * its floors and its one ceiling. The ceiling is the interesting part and it
 * is the server's own words: a stranger who scanned a care beacon can raise
 * the people watching, never an ambulance. A product that can call
 * emergency services should be legible about who is allowed to make it.
 */

const CONDITIONS: ConditionName[] = [
  "anxiety", "depression", "stress", "phobia", "financial_stress",
  "relationship", "physical_distress", "physical_injury",
];

export function Attending() {
  const { session } = useSession();
  const [specialists, setSpecialists] = useState<SpecialistRow[]>([]);
  const [clinicians, setClinicians] = useState<Row[]>([]);
  const [requests, setRequests] = useState<Row[]>([]);
  const [tasks, setTasks] = useState<Row[]>([]);
  const [task, setTask] = useState<Row | null>(null);
  const [policy, setPolicy] = useState<EscalationPolicy | null>(null);
  const [channel, setChannel] = useState<RelayChannel | null>(null);
  const [roster, setRoster] = useState<RelayRoster | null>(null);
  const [rota, setRota] = useState<RelayRota | null>(null);
  const [session_, setSession_] = useState<SessionRow | null>(null);
  const [code, setCode] = useState<MedicalIdCode | null>(null);
  const [seen, setSeen] = useState<Row | null>(null);
  const [guidance, setGuidance] = useState<Row | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [condition, setCondition] = useState<ConditionName>("anxiety");
  const [goal, setGoal] = useState("");
  const [alarmId, setAlarmId] = useState("");
  const [question, setQuestion] = useState("");
  const [situation, setSituation] = useState("");

  const uid = session.userId;
  const token = session.userToken;

  function load() {
    if (!uid || !token) return;
    api.specialists().then(setSpecialists).catch(fail);
    api.referralRequests(uid, token).then(setRequests).catch(fail);
    api.specialistTasks(uid, token).then(setTasks).catch(fail);
    api.escalationPolicy(uid, token).then(setPolicy).catch(fail);
    api.relayChannel(token).then(setChannel).catch(fail);
    api.relayRoster(token).then(setRoster).catch(fail);
    api.relayRota(token).then(setRota).catch(fail);
  }
  function fail(e: unknown) { setError((e as Error).message); }
  useEffect(load, [uid]);

  async function run(work: () => Promise<unknown>) {
    if (!uid || !token) return;
    setBusy(true); setError(null);
    try { await work(); load(); } catch (e) { fail(e); }
    finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Who else is looking</h2>
        <span className="muted small">specialists, clinicians, and the ladder</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>Specialists</h3>
        <div className="row">
          <button disabled={busy}
                  onClick={() => run(() => api.seedSpecialists(token!))}>
            Install the local set
          </button>
          <button disabled={busy}
                  onClick={() => run(() => api.seedTandemSpecialists(token!))}>
            Install the QRME-hosted set
          </button>
        </div>
        {specialists.length === 0 && (
          <div className="muted small">None installed. Without one, handing a
            thing over answers <em>no tandem specialist</em> and does nothing
            — a refusal, not a silent drop.</div>
        )}
        {specialists.map((s) => (
          <div key={s.condition} className="row"
               style={{ padding: "6px 0", borderBottom: "1px solid var(--line)" }}>
            <span className="muted small" style={{ width: 160 }}>
              {s.condition}
            </span>
            <span style={{ flex: 1 }}>{s.label}</span>
            <span className="muted small">{s.mode}</span>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Hand something over</h3>
        <div className="row">
          <select value={condition}
                  onChange={(e) =>
                    setCondition(e.target.value as ConditionName)}>
            {CONDITIONS.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <input value={goal} placeholder="Get through the week"
                 onChange={(e) => setGoal(e.target.value)} />
          <button className="primary" disabled={busy || !goal.trim()}
                  onClick={() => run(async () => {
                    setTask(await api.handToSpecialist(uid!, {
                      condition, goal: goal.trim() }, token!));
                    setGoal("");
                  })}>Hand it over</button>
          <button disabled={busy}
                  onClick={() => run(async () => {
                    setClinicians(await api.referralClinicians(
                      uid!, condition, token!));
                  })}>Who could see me for this?</button>
        </div>
        {task && (
          <p className="muted small">
            {task.started
              ? `Started · ${String(task.id ?? "")}`
              : `Not started — ${String(task.reason ?? "no reason given")}`}
          </p>
        )}
        {clinicians.map((c, i) => (
          <div key={i} className="muted small" style={{ padding: "4px 0" }}>
            {String(c.label ?? c.display_name ?? JSON.stringify(c))}
          </div>
        ))}
        {tasks.map((t) => (
          <div key={String(t.id)} className="row"
               style={{ padding: "6px 0", borderBottom: "1px solid var(--line)" }}>
            <span style={{ flex: 1 }}>
              {String(t.condition)} — {String(t.goal)}
            </span>
            <span className="muted small">{String(t.status ?? "")}</span>
            <button disabled={busy}
                    onClick={() => run(async () => {
                      setTask(await api.specialistTask(
                        uid!, String(t.id), token!));
                    })}>Open</button>
            <button disabled={busy}
                    onClick={() => run(() => api.advanceSpecialistTask(
                      uid!, String(t.id), token!))}>Advance</button>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Referrals</h3>
        <div className="row">
          <button disabled={busy}
                  onClick={() => run(() => api.prepareReferral(uid!, {
                    condition, provider_id: "prv_local" }, token!))}>
            Prepare one for {condition}
          </button>
        </div>
        {requests.length === 0 && (
          <div className="muted small">No referral has been prepared.</div>
        )}
        {requests.map((r) => (
          <div key={String(r.id)} className="row"
               style={{ padding: "6px 0", borderBottom: "1px solid var(--line)" }}>
            <span style={{ flex: 1 }}>{String(r.condition ?? "")}</span>
            <span className="muted small">{String(r.status ?? "")}</span>
            <button disabled={busy}
                    onClick={() => run(() => api.markReferralReleased(
                      uid!, String(r.id), {}, token!))}>
              Mark released
            </button>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>The ladder</h3>
        {policy && (
          <>
            <p className="muted small">
              Sensitivity <strong>{policy.sensitivity}</strong> ·{" "}
              {policy.ladder.join(" → ")}
            </p>
            {Object.entries(policy.by_severity).map(([k, v]) => (
              <div key={k} className="row"
                   style={{ padding: "4px 0" }}>
                <span className="muted small" style={{ width: 120 }}>{k}</span>
                <span>{v}</span>
              </div>
            ))}
            <p className="muted small">
              Floors — {Object.entries(policy.safety_floors)
                .map(([k, v]) => `${k}: ${v}`).join("; ")}
            </p>
            {Object.values(policy.ceilings).map((v, i) => (
              <p key={i} className="muted small">Ceiling — {v}</p>
            ))}
          </>
        )}
      </div>

      <div className="card">
        <h3>The relay</h3>
        {channel && (
          <p className="muted small">
            Channel {channel.configured ? "configured" : "not configured"}
            {channel.signed ? ", signed" : ""} · {channel.envelope}
            {channel.note ? ` — ${channel.note}` : ""}
          </p>
        )}
        {roster && (
          <p className="muted small">
            Roster: {roster.roster.join(", ")} · ceiling {roster.ceiling}
            {roster.note ? ` — ${roster.note}` : ""}
          </p>
        )}
        {rota && (
          <p className="muted small">
            {rota.anybody_on_shift
              ? `On now: ${rota.on_now.join(", ")}`
              : "Nobody is on shift"} · {rota.timezone}
            {rota.note ? ` — ${rota.note}` : ""}
          </p>
        )}
      </div>

      <div className="card">
        <h3>This sitting</h3>
        <div className="row">
          <button disabled={busy}
                  onClick={() => run(async () => {
                    setSession_(await api.startSession(
                      uid!, { device: "desktop" }, token!));
                  })}>Start a session</button>
          <button disabled={busy || !session_}
                  onClick={() => run(() => api.endSession(
                    uid!, session_!.id, token!))}>End it</button>
        </div>
        {session_ && (
          <p className="muted small">
            {session_.id} · {session_.prior_sessions} sittings before this one
          </p>
        )}
      </div>

      <div className="card">
        <h3>An alarm, and the way out</h3>
        <div className="row">
          <input value={alarmId} placeholder="alarm id"
                 onChange={(e) => setAlarmId(e.target.value)} />
          <input value={question} placeholder="What should I do right now?"
                 onChange={(e) => setQuestion(e.target.value)} />
          <button disabled={busy || !alarmId.trim() || !question.trim()}
                  onClick={() => run(async () => {
                    setGuidance(await api.alarmGuidance(alarmId.trim(),
                      { question: question.trim() }, token!));
                  })}>Ask</button>
        </div>
        {guidance != null && (
          <p className="muted small">{String(guidance.content ?? "")}</p>
        )}
        <div className="row">
          <input value={situation} placeholder="What is happening"
                 onChange={(e) => setSituation(e.target.value)} />
          <button className="danger" disabled={busy}
                  onClick={() => run(() => api.raiseEmergency(uid!, {
                    situation: situation.trim() || undefined }, token!))}>
            Raise an emergency
          </button>
        </div>
        <p className="muted small">
          This is the door that reaches emergency services, and it takes your
          own credential. The uncredentialed one is a scanned care code — a
          bystander at your front door can wake the people watching over you,
          and stops there. Only you can send an ambulance to yourself.
        </p>
      </div>

      <div className="card">
        <h3>Medical ID</h3>
        <div className="row">
          <button disabled={busy}
                  onClick={() => run(async () => {
                    setCode(await api.makeMedicalIdQr(uid!, token!));
                  })}>Make a code</button>
          <button disabled={busy || !code}
                  onClick={() => run(async () => {
                    setSeen(await api.medicalId(code!.token));
                  })}>See what a stranger sees</button>
          <button disabled={busy}
                  onClick={() => run(async () => {
                    await api.revokeMedicalIdQr(uid!, token!);
                    setCode(null); setSeen(null);
                  })}>Revoke</button>
        </div>
        {code && (
          <p className="muted small">
            {code.view_url} · the printable code is at {code.qr_svg_url}
          </p>
        )}
        {seen && (
          <p className="muted small">{JSON.stringify(seen)}</p>
        )}
      </div>
    </div>
  );
}
