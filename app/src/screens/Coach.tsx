import { useState } from "react";
import { api, type Guidance } from "../api";
import { useSession } from "../store";

const AREAS = ["mental_health", "health_fitness", "career", "relationships"];

export function Coach() {
  const { session } = useSession();
  const [area, setArea] = useState("mental_health");
  const [message, setMessage] = useState("I've been feeling stressed about work.");
  const [reply, setReply] = useState<Guidance | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask() {
    if (!session.userId || !session.userToken || !message.trim()) return;
    setBusy(true); setError(null);
    try { setReply(await api.coach(session.userId, { area, message }, session.userToken)); }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Coach</h2>
        <span className="muted small">24/7 across your life</span>
      </header>
      <div className="card">
        <label>Area
          <select value={area} onChange={(e) => setArea(e.target.value)}>
            {AREAS.map((a) => <option key={a}>{a}</option>)}
          </select>
        </label>
        <label>What's on your mind?
          <textarea rows={3} value={message} onChange={(e) => setMessage(e.target.value)} />
        </label>
        <button className="primary" onClick={ask} disabled={busy}>{busy ? "Thinking…" : "Ask the coach"}</button>
        {error && <div className="error">⚠ {error}</div>}
      </div>
      {reply?.content && (
        <div className="card guidance">
          <div className="guidance-src">{area.replace("_", " ")} · guidance</div>
          <p>{reply.content}</p>
        </div>
      )}
    </div>
  );
}
