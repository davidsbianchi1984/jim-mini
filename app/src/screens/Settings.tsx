import { useEffect, useState } from "react";
import { api, getBase, getLlmKey, setBase, setLlmKey, type AdaptationProfile,
         type AnonymityPosture, type CloudContribution, type PairInfo,
         type SeedReport, type VigilStatus,
         type WatchChannel } from "../api";
import { Problems } from "../Problems";
import { ProviderTiles } from "../ProviderTiles";
import { say } from "../speech";
import { useSession } from "../store";

export function Settings() {
  const { session, signOut } = useSession();
  const [base, setBaseInput] = useState(getBase());
  // Claim 11's user-specific model, and spec [0031]'s anonymity posture.
  const [adapt, setAdapt] = useState<AdaptationProfile | null>(null);
  const [anon, setAnon] = useState<AnonymityPosture | null>(null);
  const [adaptBusy, setAdaptBusy] = useState(false);
  const [health, setHealth] = useState<string>("…");
  const [saved, setSaved] = useState(false);
  const [llmKey, setLlmKeyInput] = useState(getLlmKey());
  const [keySaved, setKeySaved] = useState(false);
  const [pair, setPair] = useState<PairInfo | null>(null);

  useEffect(() => {
    api.health().then((h) => setHealth(`ok · vault tandem: ${h.tandem ? "connected" : "not configured (set by the deployment, not a switch)"}`)).catch(() => setHealth("unreachable"));
    api.pair().then(setPair).catch(() => setPair(null));
    if (session.userId && session.userToken) {
      api.adaptation(session.userId, session.userToken).then(setAdapt).catch(() => {});
      api.anonymity(session.userId, session.userToken).then(setAnon).catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session.userId]);

  function save() {
    setBase(base); setSaved(true); setTimeout(() => setSaved(false), 1500);
    api.health().then((h) => setHealth(`ok · vault tandem: ${h.tandem ? "connected" : "not configured (set by the deployment, not a switch)"}`)).catch(() => setHealth("unreachable"));
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

      <VoicePanel />

      <WatchPanel />

      <VigilPanel />

      <MailPanel />

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
        <h3>What JIM has learned about you</h3>
        <p className="muted small">
          A profile derived from your own history — the conditions you
          declared, how your check-ins trend, what you bring up, and which
          guidance has actually helped. It shapes how the coach answers.
          Nothing is sent to a model vendor to build it.
        </p>
        {adapt?.built && adapt.profile ? (
          <>
            <div className="spec-row">
              <div>
                <b>{Math.round((adapt.confidence || 0) * 100)}% confidence</b>
                <div className="muted small">
                  from {adapt.evidence_items} pieces of your own history
                  {adapt.vaulted ? " · sealed in the vault" : ""}
                </div>
              </div>
              <button disabled={adaptBusy} onClick={async () => {
                if (!session.userId || !session.userToken) return;
                setAdaptBusy(true);
                try { setAdapt(await api.rebuildAdaptation(session.userId, session.userToken)); }
                finally { setAdaptBusy(false); }
              }}>Rebuild</button>
            </div>
            <ul className="refs">
              {Object.entries(adapt.profile.what_helps).map(([cond, t]) => (
                <li key={cond}>
                  {cond}: guidance helped {t.helped} of {t.answered} times
                </li>
              ))}
              {adapt.profile.occupation && (
                <li>work: {adapt.profile.occupation}</li>
              )}
              {adapt.profile.tone && <li>tone you asked for: {adapt.profile.tone}</li>}
            </ul>
            <p className="muted small">{adapt.profile.method}</p>
          </>
        ) : (
          <>
            <p className="muted small">{adapt?.note || "Nothing built yet."}</p>
            <button disabled={adaptBusy} onClick={async () => {
              if (!session.userId || !session.userToken) return;
              setAdaptBusy(true);
              try { setAdapt(await api.rebuildAdaptation(session.userId, session.userToken)); }
              finally { setAdaptBusy(false); }
            }}>Build it from my history</button>
          </>
        )}
      </div>

      <div className="card">
        <h3>Your name here</h3>
        {anon ? (anon.anonymous ? (
          <>
            <p>
              You use JIM as <b>{anon.known_as}</b> — a pseudonym. JIM never
              learned your real name.
            </p>
            <ul className="refs">
              {anon.keeps.map((k, i) => <li key={i}>Keeps: {k}</li>)}
              {anon.costs.map((c, i) => <li key={`c${i}`}>Costs: {c}</li>)}
            </ul>
          </>
        ) : (
          <p className="muted small">
            You use JIM under your own name ({anon.known_as}).
          </p>
        )) : <p className="muted small">…</p>}
      </div>

      <CloudContributionCard />
      <LocalityCard />

      <div className="card">
        <h3>Your data</h3>
        <p className="muted small">Guidance runs on-device; sensitive payloads seal into the PDI vault when the tandem is on. User: {session.userId}</p>
        <button className="danger" onClick={signOut}>Sign out &amp; end session</button>
      </div>
      <Problems />
    </div>
  );
}


// What has left this device for the shared model, and the button that stops
// it. The backend has answered both questions for versions; nothing asked.
//
// The counts come from the server rather than being described in prose here,
// because "some anonymised signals" is the kind of reassurance that survives
// the behaviour changing underneath it. A number cannot.
function CloudContributionCard() {
  const { session } = useSession();
  const [state, setState] = useState<CloudContribution | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uid = session.userId, token = session.userToken;
  function load() {
    if (!uid || !token) return;
    api.cloudContribution(uid, token).then(setState).catch(() => setState(null));
  }
  useEffect(load, [uid]);
  if (!uid || !token || !state) return null;

  return (
    <div className="card">
      <h3>What you contribute</h3>
      <p className="muted small">
        {state.opted_in
          ? `Contributing. ${state.contributed} item${state.contributed === 1 ? "" : "s"} have gone to the shared model.`
          : "Not contributing. Nothing from this account has gone to the shared model."}
      </p>
      {state.policy && <p className="muted small">{state.policy}</p>}
      {state.preview_note && <p className="muted small">{state.preview_note}</p>}
      {error && <p className="error">{error}</p>}
      {state.opted_in && (
        <button
          className="danger"
          disabled={busy}
          onClick={async () => {
            if (!confirm("Stop contributing? What has already gone cannot be recalled."))
              return;
            setBusy(true); setError(null);
            try { setState(await api.revokeCloudContribution(uid, token)); }
            catch (e) { setError((e as Error).message); }
            finally { setBusy(false); }
          }}>
          Stop contributing
        </button>
      )}
    </div>
  );
}


// Locality is what the community door searches near, and nothing more. It is
// set here rather than inferred from an IP address on purpose: a guess about
// where somebody lives is not a thing to make quietly.
function LocalityCard() {
  const { session } = useSession();
  const [locality, setLocality] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const uid = session.userId, token = session.userToken;
  if (!uid || !token) return null;

  async function save(value: string | null) {
    setBusy(true); setError(null); setNote(null);
    try {
      await api.setLocality(uid!, value, token!);
      setNote(value ? `Searching near ${value}.` : "Cleared.");
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <div className="card">
      <h3>Where to look</h3>
      <p className="muted small">
        Used only to find local rooms and events through the community door.
        Leave it empty and nothing local is searched for.
      </p>
      <div className="row">
        <input
          value={locality}
          placeholder="Town or city"
          onChange={(e) => setLocality(e.target.value)} />
        <button disabled={busy || !locality.trim()}
          onClick={() => save(locality.trim())}>Save</button>
        <button disabled={busy}
          onClick={() => { setLocality(""); save(null); }}>Clear</button>
      </div>
      {note && <p className="muted small">{note}</p>}
      {error && <p className="error">{error}</p>}
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
      </p>
      <ProviderTiles providers={providers} chosen={chosen}
                     effective={effective} onPick={pick} busy={busy} />
      {/* The truth about what will actually answer. The silent case was the
          bad one: Automatic quietly resolving to the stub while the screen
          full of logos implied a real model was on. */}
      {effective === "stub" && chosen !== "stub" ? (
        <div className="degraded">
          ⚠ Right now replies come from the <b>built-in offline helper</b> —
          no online model has a working key on this machine. Pick a provider
          above and add its key (“Your model API key” below works for all of
          them).
        </div>
      ) : effective && chosen !== "auto" && chosen !== effective && (
        <div className="degraded">
          ⚠ Right now it resolves to <b>{effective}</b> — the one you picked
          has no key on this machine yet.
        </div>
      )}
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

  function desktop(): boolean {
    return Boolean((window as { jimDesktop?: { setLanAccess?: unknown } }).jimDesktop?.setLanAccess);
  }

  async function enableLan() {
    setBusy(true); setError(null);
    try {
      const bridge = (window as unknown as { jimDesktop: { setLanAccess: (on: boolean) => Promise<unknown> } }).jimDesktop;
      await bridge.setLanAccess(true);
      // The backend restarted on the new interface; give it a beat, reload.
      await new Promise((r) => setTimeout(r, 1500));
      load();
    } catch (e) { setError((e as Error).message); }
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
        {/* The truth about the address below: a loopback-bound backend
            serves a Wi-Fi URL nothing answers on. On the desktop the fix
            is one switch away; elsewhere, the card says what to run. */}
        {!ch.phone_reachable && (
          <div className="degraded">
            ⚠ Your phone can't reach this address yet — JIM is only
            listening on this computer.
            {desktop() ? (
              <div style={{ marginTop: 8 }}>
                <button className="primary" disabled={busy} onClick={enableLan}>
                  Let my phone reach JIM on this Wi-Fi
                </button>
                <div className="muted small" style={{ marginTop: 6 }}>
                  Restarts JIM listening on your network. Windows may ask to
                  allow it through the firewall — say yes. Everything personal
                  still requires your sign-in.
                </div>
              </div>
            ) : (
              <div className="muted small" style={{ marginTop: 6 }}>
                Start the backend with network access: python -m jim phone
              </div>
            )}
          </div>
        )}
        {ch.phone_reachable && (
          <div className="muted small">✓ Reachable from your phone on this Wi-Fi.</div>
        )}
        <label>Drip address (paste into the Shortcut's “Get Contents of URL” field)
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

function VigilPanel() {
  const { session } = useSession();
  const [st, setSt] = useState<VigilStatus | null>(null);
  const [name, setName] = useState("");
  const [channel, setChannel] = useState("");
  const [days, setDays] = useState(3);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function load() {
    if (!session.userId || !session.userToken) return;
    // sweep, not just read: opening the app is the natural moment to ask
    // "has anyone gone quiet?" — it is idempotent and trips at most once.
    api.sweepVigil(session.userId, session.userToken).then((s) => {
      setSt(s);
      if (s.armed) {
        setName(s.steward_name || ""); setChannel(s.steward_channel || "");
        setDays(s.quiet_days || 3); setNote(s.note || "");
      }
    }).catch(() => setSt(null));
  }
  useEffect(load, [session.userId]);

  if (!session.userId || !session.userToken) return null;

  async function run(fn: () => Promise<VigilStatus>) {
    setBusy(true); setError(null);
    try { setSt(await fn()); } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <div className="card">
      <h3>The vigil</h3>
      <p className="muted small">
        Every other alarm fires on a reading. This one fires on the <b>absence</b> of
        readings: name someone, and if nothing is heard from you for longer than
        the quiet period, they are asked to check on you. Any reading stands it
        down. It never calls emergency services — it knocks on a door.
      </p>
      {st?.tripped && (
        <div className="degraded">
          ⚠ The vigil has tripped — {st.steward_name} was asked to check on you
          {st.silent_hours != null && <> after {Math.round((st.silent_hours) / 24 * 10) / 10} quiet days</>}.
          <div style={{ marginTop: 8 }}>
            <button className="primary" disabled={busy}
                    onClick={() => run(() => api.resolveVigil(session.userId!, session.userToken!))}>
              I'm okay
            </button>
          </div>
        </div>
      )}
      <div className="row">
        <label>Steward's name<input value={name} placeholder="Who to tell" onChange={(e) => setName(e.target.value)} /></label>
        <label>How to reach them<input value={channel} placeholder="their@email.com" onChange={(e) => setChannel(e.target.value)} /></label>
      </div>
      <label>Quiet days before they're told
        <input type="number" min={1} max={60} value={days} onChange={(e) => setDays(Number(e.target.value))} />
      </label>
      <label>In your own words <span className="muted small">— what they'll read, written now</span>
        <input value={note} placeholder="I live alone — please knock." onChange={(e) => setNote(e.target.value)} />
      </label>
      <div className="actions">
        <button className="primary" disabled={busy || !name.trim() || !channel.trim()}
                onClick={() => run(() => api.armVigil(session.userId!, session.userToken!,
                  { steward_name: name, steward_channel: channel, quiet_days: days, note: note || undefined }))}>
          {st?.armed ? "Update the vigil" : "Arm the vigil"}
        </button>
        {st?.armed && (
          <button disabled={busy}
                  onClick={() => run(() => api.disarmVigil(session.userId!, session.userToken!))}>
            Disarm
          </button>
        )}
      </div>
      {st?.armed && st.last_heard_at && !st.tripped && (
        <div className="muted small">
          Armed · last heard from you {st.silent_hours != null ? `${st.silent_hours}h ago` : "recently"} · steward: {st.steward_name}
        </div>
      )}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
