import { useEffect, useState } from "react";
import { api, getBase, getLlmKey, setBase, setLlmKey, type PairInfo, type SeedReport, type WatchChannel } from "../api";
import { ProviderTiles } from "../ProviderTiles";
import { say } from "../speech";
import { useSession } from "../store";

export function Settings() {
  const { session, signOut } = useSession();
  const [base, setBaseInput] = useState(getBase());
  const [health, setHealth] = useState<string>("…");
  const [saved, setSaved] = useState(false);
  const [llmKey, setLlmKeyInput] = useState(getLlmKey());
  const [keySaved, setKeySaved] = useState(false);
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
      <ModelPanel />

      <VoicePanel />

      <WatchPanel />

      <MailPanel />

      <div className="card">
        <h3>Your model API key</h3>
        <p className="muted small">
          Paste your own key (Anthropic <code>sk-ant-…</code>, or OpenAI / xAI /
          Gemini for those providers) and your Guardian's replies run on your
          credential. It stays on this device and rides only your own requests —
          the server never stores it. Leave it empty to use whatever key the
          deployment lends.
        </p>
        <label>API key
          <input type="password" value={llmKey} placeholder="sk-…"
                 onChange={(e) => setLlmKeyInput(e.target.value)} />
        </label>
        <button className="primary" onClick={() => {
          setLlmKey(llmKey); setKeySaved(true); setTimeout(() => setKeySaved(false), 1500);
        }}>{keySaved ? "Saved ✓" : llmKey.trim() ? "Save key" : "Clear key"}</button>
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


// Where this deployment sends mail through. Until a host is set here (or in
// the environment), no verification email can reach anybody — the message
// goes to the server's log instead, which is why local signup does not wait
// for one. Fill this in and the emails become real.
function MailPanel() {
  const [cfg, setCfg] = useState<Awaited<ReturnType<typeof api.getMailSettings>> | null>(null);
  const [host, setHost] = useState("");
  const [port, setPort] = useState(587);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [sender, setSender] = useState("");
  const [publicUrl, setPublicUrl] = useState("");
  const [testTo, setTestTo] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    api.getMailSettings().then((c) => {
      setCfg(c);
      setHost(c.host || ""); setPort(c.port || 587);
      setUsername(c.username || ""); setSender(c.sender || "");
      setPublicUrl(c.public_url || ""); setTestTo(c.username || "");
    }).catch(() => setCfg(null));
  }
  useEffect(load, []);

  async function run(fn: () => Promise<unknown>, ok: string) {
    setBusy(true); setError(null); setNote(null);
    try { await fn(); setNote(ok); load(); }
    catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <div className="card">
      <h3>Email delivery</h3>
      <p className="muted small">
        {cfg?.transport === "smtp"
          ? <>Mail goes out through <b>{cfg.host}</b>{cfg.source === "environment" && " (set by environment variables)"}. New accounts must verify by email.</>
          : <>No mail server configured, so <b>nothing can be emailed</b> — verification messages are written to this app's log and signup on this machine simply goes straight in. Point it at a mail account below to send real verification links. For Gmail, turn on 2-Step Verification and create an <b>App password</b>; paste that here, not your normal password.</>}
      </p>
      {cfg?.source !== "environment" && (<>
        <div className="row">
          <label>Mail server<input value={host} placeholder="smtp.gmail.com" onChange={(e) => setHost(e.target.value)} /></label>
          <label>Port<input type="number" value={port} onChange={(e) => setPort(Number(e.target.value))} /></label>
        </div>
        <label>Username<input value={username} placeholder="you@gmail.com" onChange={(e) => setUsername(e.target.value)} /></label>
        <label>Password {cfg?.password_set && <span className="muted small">(saved — type to replace)</span>}
          <input type="password" value={password} placeholder="app password" onChange={(e) => setPassword(e.target.value)} />
        </label>
        <label>From address<input value={sender} placeholder="you@gmail.com" onChange={(e) => setSender(e.target.value)} /></label>
        <label>Link address <span className="muted small">— what verification links point at</span>
          <input value={publicUrl} placeholder="http://127.0.0.1:8000" onChange={(e) => setPublicUrl(e.target.value)} />
        </label>
        <div className="actions">
          <button className="primary" disabled={busy || !host.trim()}
                  onClick={() => run(() => api.saveMailSettings({
                    host, port, username, password: password || undefined,
                    sender, public_url: publicUrl }), "Saved.")}>
            {busy ? "Saving…" : "Save mail settings"}
          </button>
          {cfg?.transport === "smtp" && (
            <button disabled={busy} onClick={() => run(() => api.clearMailSettings(), "Cleared.")}>
              Clear
            </button>
          )}
        </div>
      </>)}
      {cfg?.transport === "smtp" && (<>
        <label>Send a test message to<input value={testTo} placeholder="you@example.com" onChange={(e) => setTestTo(e.target.value)} /></label>
        <button disabled={busy || !testTo.trim()}
                onClick={() => run(() => api.testMailSettings(testTo.trim()),
                  `Sent to ${testTo.trim()} — check the inbox.`)}>
          {busy ? "Sending…" : "Send test email"}
        </button>
      </>)}
      {note && <div className="muted small">{note}</div>}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}


// Which model answers — click a tile. The switchboard has always been in the
// backend; a person should not have to know that a PUT exists.
function ModelPanel() {
  const { session } = useSession();
  const [providers, setProviders] = useState<Awaited<ReturnType<typeof api.listModels>>["providers"]>([]);
  const [chosen, setChosen] = useState("auto");
  const [effective, setEffective] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function load() {
    api.listModels().then((m) => setProviders(m.providers)).catch(() => setProviders([]));
    if (session.userId && session.userToken) {
      api.getModelChoice(session.userId, session.userToken)
        .then((c) => { setChosen(c.provider); setEffective(c.effective); })
        .catch(() => undefined);
    }
  }
  useEffect(load, [session.userId]);

  async function pick(name: string) {
    if (!session.userId || !session.userToken) return;
    setBusy(true); setError(null);
    try {
      const r = await api.setModelChoice(session.userId, name, session.userToken);
      setChosen(r.provider); setEffective(r.effective);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <div className="card">
      <h3>Which model answers</h3>
      <p className="muted small">
        Your Guardian's replies can run on any of these. Pick one and every
        reply uses it; <b>Automatic</b> uses whichever is configured.
        {effective && chosen !== effective && (
          <> Right now it resolves to <b>{effective}</b> — the one you picked
          has no key on this deployment yet.</>)}
      </p>
      <ProviderTiles providers={providers} chosen={chosen}
                     effective={effective} onPick={pick} busy={busy} />
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}

// The Guardian's voice. Without a service the device's own voice reads
// replies aloud — free, no account — so this panel is about *upgrading* the
// voice, never about switching speech on.
function VoicePanel() {
  const [cfg, setCfg] = useState<Awaited<ReturnType<typeof api.getVoiceSettings>> | null>(null);
  const [provider, setProvider] = useState("device");
  const [apiKey, setApiKey] = useState("");
  const [voiceId, setVoiceId] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    api.getVoiceSettings().then((c) => {
      setCfg(c); setProvider(c.provider); setVoiceId(c.voice_id || "");
    }).catch(() => setCfg(null));
  }
  useEffect(load, []);

  async function save(next?: Partial<{ provider: string; voice_id: string; speak_replies: boolean }>) {
    setBusy(true); setError(null); setNote(null);
    try {
      await api.saveVoiceSettings({
        provider: next?.provider ?? provider,
        api_key: apiKey || undefined,
        voice_id: next?.voice_id ?? voiceId,
        speak_replies: next?.speak_replies,
      });
      setApiKey(""); setNote("Saved."); load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  const voices = cfg?.voices || [];
  return (
    <div className="card">
      <h3>Voice</h3>
      <p className="muted small">
        {cfg?.provider === "device"
          ? <>Replies are read aloud in <b>your device's own voice</b> — no account needed. Add an ElevenLabs or OpenAI key for a natural one, and to talk back by microphone.</>
          : <>Speaking through <b>{cfg?.provider}</b>{cfg?.key_source === "environment" && " (key from the environment)"}. Talking back by microphone works too.</>}
      </p>
      <div className="voice-row">
        {["device", "elevenlabs", "openai"].map((p) => (
          <button key={p} className={provider === p ? "primary" : ""}
                  disabled={busy}
                  onClick={() => { setProvider(p); if (p === "device") save({ provider: p }); }}>
            {p === "device" ? "Device voice" : p === "elevenlabs" ? "ElevenLabs" : "OpenAI"}
          </button>
        ))}
      </div>
      {provider !== "device" && (<>
        <label>API key {cfg?.key_set && <span className="muted small">(saved — type to replace)</span>}
          <input type="password" value={apiKey} placeholder={provider === "elevenlabs" ? "ElevenLabs key" : "sk-…"}
                 onChange={(e) => setApiKey(e.target.value)} />
        </label>
        {voices.length > 0 && (
          <label>Voice
            <select value={voiceId} onChange={(e) => { setVoiceId(e.target.value); save({ voice_id: e.target.value }); }}>
              {voices.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} — {v.gender}, {v.note}
                </option>
              ))}
            </select>
          </label>
        )}
        <div className="actions">
          <button className="primary" disabled={busy} onClick={() => save()}>
            {busy ? "Saving…" : "Save voice settings"}
          </button>
          <button disabled={busy}
                  onClick={() => say("Hello — this is the voice your Guardian will speak in.")}>
            Hear it
          </button>
        </div>
      </>)}
      {provider === "device" && (
        <button disabled={busy}
                onClick={() => say("Hello — this is your device's own voice.")}>
          Hear it
        </button>
      )}
      {note && <div className="muted small">{note}</div>}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}

function WatchPanel() {
  const { session } = useSession();
  const [ch, setCh] = useState<WatchChannel | null>(null);
  const [copied, setCopied] = useState(false);
  const [busy, setBusy] = useState(false);
  const [report, setReport] = useState<SeedReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    if (!session.userId || !session.userToken) return;
    api.getWatchChannel(session.userId, session.userToken)
      .then(setCh).catch(() => setCh(null));
  }
  useEffect(load, [session.userId]);

  if (!session.userId || !session.userToken) return null;

  async function rotate() {
    setBusy(true); setError(null);
    try { setCh(await api.rotateWatchChannel(session.userId!, session.userToken!)); }
    catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function upload(file: File) {
    setBusy(true); setError(null); setReport(null);
    try {
      setReport(await api.seedWatchExport(session.userId!, session.userToken!, file));
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <div className="card">
      <h3>Apple Watch</h3>
      <p className="muted small">
        No app to install. An iPhone <b>Shortcuts automation</b> drips readings
        to the address below, and the Health app's <b>export</b> teaches JIM
        your baseline from the history your watch already recorded.
      </p>
      {ch ? (<>
        <label>Drip address (paste into the Shortcut)
          <input readOnly value={ch.drip_url} onFocus={(e) => e.currentTarget.select()} />
        </label>
        <div className="actions">
          <button className="primary" onClick={() => {
            navigator.clipboard?.writeText(ch.drip_url);
            setCopied(true); setTimeout(() => setCopied(false), 1500);
          }}>{copied ? "Copied ✓" : "Copy address"}</button>
          <button disabled={busy} onClick={rotate}>New address</button>
        </div>
        <div className="muted small" style={{ marginTop: 8 }}>
          {ch.drips > 0
            ? <>Received <b>{ch.drips}</b> reading{ch.drips === 1 ? "" : "s"} · last {ch.last_drip_at ? new Date(ch.last_drip_at).toLocaleString() : "—"}</>
            : "Nothing has arrived yet — run the Shortcut once by hand to test it."}
        </div>
        <details style={{ marginTop: 10 }}>
          <summary className="muted small">Set up the Shortcut (one time)</summary>
          <ol className="muted small">
            {ch.shortcut.map((s, i) => <li key={i}>{s}</li>)}
          </ol>
        </details>
        <div style={{ marginTop: 12 }}>
          <label>Seed the baseline from a Health export
            <input type="file" accept=".zip,.xml" disabled={busy}
                   onChange={(e) => { const f = e.target.files?.[0]; if (f) upload(f); e.target.value = ""; }} />
          </label>
          <div className="muted small">{ch.seed_hint}</div>
        </div>
        {report && (
          <div className="muted small" style={{ marginTop: 8 }}>
            {Object.entries(report.seeded).map(([metric, r]) => (
              <div key={metric}>
                <b>{metric.replace(/_/g, " ")}</b>: {r.days} day{r.days === 1 ? "" : "s"} folded,
                baseline {r.baseline}{r.provisional ? " (still learning)" : " — established"}
              </div>
            ))}
          </div>
        )}
      </>) : <div className="muted small">Sign in to mint your drip address.</div>}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
