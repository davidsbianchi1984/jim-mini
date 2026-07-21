import { useEffect, useState } from "react";
import { api, type BaselineMetric } from "../api";
import { useSession } from "../store";

export function Home({ go }: { go: (t: "monitor" | "coach" | "checkin") => void }) {
  const { session } = useSession();
  const [baseline, setBaseline] = useState<BaselineMetric[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session.userId || !session.userToken) return;
    api.baseline(session.userId, session.userToken).then(setBaseline).catch((e) => setError((e as Error).message));
  }, [session.userId]);

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Overview</h2>
        <span className="dot-online">● Guardian on</span>
      </header>

      <div className="profile-hero">
        <div className="orb big" />
        <div>
          <h3>Hi, {session.displayName}</h3>
          <div className="muted">Your Guardian is watching — rules are transparent.</div>
        </div>
      </div>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>Learned baseline</h3>
        {baseline.length === 0 ? (
          <div className="muted">No baseline yet — it builds from calm samples in Live Monitoring.</div>
        ) : (
          <table className="tbl">
            <thead><tr><th>metric</th><th>value</th><th>state</th><th>samples</th></tr></thead>
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
        <button className="primary" onClick={() => go("monitor")}>Live Monitoring</button>
        <button onClick={() => go("coach")}>Coach</button>
        <button onClick={() => go("checkin")}>Check-in</button>
      </div>
    </div>
  );
}
