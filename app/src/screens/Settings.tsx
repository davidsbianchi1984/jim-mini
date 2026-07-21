import { useEffect, useState } from "react";
import { api, getBase, setBase } from "../api";
import { useSession } from "../store";

export function Settings() {
  const { session, signOut } = useSession();
  const [base, setBaseInput] = useState(getBase());
  const [health, setHealth] = useState<string>("…");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.health().then((h) => setHealth(`ok · tandem ${h.tandem ? "on" : "off"}`)).catch(() => setHealth("unreachable"));
  }, []);

  function save() {
    setBase(base); setSaved(true); setTimeout(() => setSaved(false), 1500);
    api.health().then((h) => setHealth(`ok · tandem ${h.tandem ? "on" : "off"}`)).catch(() => setHealth("unreachable"));
  }

  return (
    <div className="screen">
      <header className="screen-head"><h2>Privacy &amp; Connection</h2></header>
      <div className="card">
        <h3>API connection</h3>
        <label>Backend base URL<input value={base} onChange={(e) => setBaseInput(e.target.value)} /></label>
        <button className="primary" onClick={save}>{saved ? "Saved ✓" : "Save"}</button>
        <div className="muted small" style={{ marginTop: 10 }}>Backend: {health}</div>
      </div>
      <div className="card">
        <h3>Your data</h3>
        <p className="muted small">Guidance runs on-device; sensitive payloads seal into the PDI vault when the tandem is on. User: {session.userId}</p>
        <button className="danger" onClick={signOut}>Sign out &amp; end session</button>
      </div>
    </div>
  );
}
