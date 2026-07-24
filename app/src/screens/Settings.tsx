import { useEffect, useState } from "react";
import { api, getBase, setBase, type PairInfo } from "../api";
import { useSession } from "../store";

export function Settings() {
  const { session, signOut } = useSession();
  const [base, setBaseInput] = useState(getBase());
  const [health, setHealth] = useState<string>("…");
  const [saved, setSaved] = useState(false);
  const [pair, setPair] = useState<PairInfo | null>(null);

  useEffect(() => {
    api.health().then((h) => setHealth(`ok · tandem ${h.tandem ? "on" : "off"}`)).catch(() => setHealth("unreachable"));
    api.pair().then(setPair).catch(() => setPair(null));
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
      {pair && (
        <div className="card">
          <h3>Open on your phone</h3>
          <p className="muted small">{pair.note}</p>
          <div className="pair">
            <img className="pair-qr" src={getBase() + pair.qr_svg} alt="QR code for the console URL on this network" />
            <div>
              <div className="mono pair-url">{pair.console_url}</div>
              <ol className="pair-steps">{pair.how.map((s) => <li key={s}>{s}</li>)}</ol>
            </div>
          </div>
        </div>
      )}
      <div className="card">
        <h3>Your data</h3>
        <p className="muted small">Guidance runs on-device; sensitive payloads seal into the PDI vault when the tandem is on. User: {session.userId}</p>
        <button className="danger" onClick={signOut}>Sign out &amp; end session</button>
      </div>
    </div>
  );
}
