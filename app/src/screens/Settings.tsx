import { useEffect, useState } from "react";
import { t as tr, visitorLang } from "../l10n";
import { api, type BankLinkRow, type StatementRow, getBase, getLlmKey, setBase, setLlmKey, type AdaptationProfile, type ContinuityState, type MoneyView,
         type AnonymityPosture, type CloudContribution, type PairInfo,
         type SeedReport, type VigilStatus,
         type WatchChannel, type Finetune } from "../api";
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
  const [ft, setFt] = useState<Finetune | null>(null);
  const [ftBusy, setFtBusy] = useState(false);
  const [ftError, setFtError] = useState<string | null>(null);
  const [cont, setCont] = useState<ContinuityState | null>(null);
  const lang = visitorLang();
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
      // 404 until something has been trained, which is the normal state.
      api.finetune(session.userId, session.userToken).then(setFt).catch(() => {});
      api.anonymity(session.userId, session.userToken).then(setAnon).catch(() => {});
      api.continuity(session.userId, session.userToken).then(setCont).catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session.userId]);

  function save() {
    setBase(base); setSaved(true); setTimeout(() => setSaved(false), 1500);
    api.health().then((h) => setHealth(`ok · vault tandem: ${h.tandem ? "connected" : "not configured (set by the deployment, not a switch)"}`)).catch(() => setHealth("unreachable"));
  }

  return (
    <div className="screen">
      <header className="screen-head"><h2>{tr("set.title", lang)}</h2></header>
      <div className="card">
        <h3>{tr("set.api", lang)}</h3>
        <label>{tr("set.api.base", lang)}<input value={base} onChange={(e) => setBaseInput(e.target.value)} /></label>
        <button className="primary" onClick={save}>{saved ? "Saved ✓" : "Save"}</button>
        <div className="muted small" style={{ marginTop: 10 }}>{tr("set.api.backend", lang)} {health}</div>
      </div>
      <OfflinePosture />

      <ModelPanel />

      <div className="card">
        <h3>{tr("set.key", lang)}</h3>
        <p className="muted small">{tr("set.key.pitch", lang)}</p>
        <label>{tr("set.key.label", lang)}
          <input type="password" value={llmKey} placeholder={tr("set.key.ph", lang)}
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
          <h3>{tr("set.pair", lang)}</h3>
          <p className="muted small">{pair.note}</p>
          <div className="pair">
            {/* The literal rather than `pair.qr_svg`, which holds this exact
                    string from the server. Same request, and the route audit
                    can see it: a path that only exists in a response body is a
                    door no static check can find, and the last one of those got
                    itself exempted as "not a client call" and then went years
                    without anybody noticing it rendered nowhere. */}
            <img className="pair-qr" src={getBase() + "/pair/qr.svg"} alt={tr("set.pair.alt", lang)} />
            <div>
              <div className="mono pair-url">{pair.console_url}</div>
              <ol className="pair-steps">{pair.how.map((s) => <li key={s}>{s}</li>)}</ol>
            </div>
          </div>
        </div>
      )}
      <div className="card">
        <h3>{tr("set.adapt", lang)}</h3>
        <p className="muted small">{tr("set.adapt.pitch", lang)}</p>
        {adapt?.built && adapt.profile ? (
          <>
            <div className="spec-row">
              <div>
                <b>{tr("set.adapt.conf", lang).replace("{pct}",
                  String(Math.round((adapt.confidence || 0) * 100)))}</b>
                <div className="muted small">
                  {tr("set.adapt.from", lang)
                    .replace("{n}", String(adapt.evidence_items))}
                  {adapt.vaulted ? " · sealed in the vault" : ""}
                </div>
              </div>
              <button disabled={adaptBusy} onClick={async () => {
                if (!session.userId || !session.userToken) return;
                setAdaptBusy(true);
                try { setAdapt(await api.rebuildAdaptation(session.userId, session.userToken)); }
                finally { setAdaptBusy(false); }
              }}>{tr("set.adapt.rebuild", lang)}</button>
            </div>
            <ul className="refs">
              {Object.entries(adapt.profile.what_helps).map(([cond, t]) => (
                <li key={cond}>
                  {tr("set.adapt.helped", lang)
                    .replace("{cond}", cond)
                    .replace("{h}", String(t.helped))
                    .replace("{a}", String(t.answered))}
                </li>
              ))}
              {adapt.profile.occupation && (
                <li>{tr("set.adapt.work", lang)
                  .replace("{what}", String(adapt.profile.occupation))}</li>
              )}
              {adapt.profile.tone && <li>{tr("set.adapt.tone", lang)
                .replace("{tone}", String(adapt.profile.tone))}</li>}
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
            }}>{tr("set.adapt.build", lang)}</button>
          </>
        )}
      </div>

      {/* The offline fine-tune. A separate card from the adaptation profile
          above it on purpose: that one is a profile that conditions a prompt,
          this one is weights. One card doing both is how a reader ends up
          unable to say which of the two they have. */}
      <div className="card">
        <h3>{tr("set.ft.title", lang)}</h3>
        <p className="muted small">{tr("set.ft.sub", lang)}</p>
        {ft ? (
          <>
            <div className="spec-row">
              <div>
                <b>{tr("set.ft.trained", lang)
                  .replace("{n}", String(ft.examples))
                  .replace("{backend}", ft.backend)}</b>
                {/* The server's own sentence, shown rather than paraphrased. */}
                <div className="muted small">{ft.method}</div>
              </div>
              <button disabled={ftBusy} onClick={async () => {
                if (!session.userId || !session.userToken) return;
                setFtBusy(true);
                try { setFt(await api.runFinetune(session.userId, session.userToken)); }
                catch (e) { setFtError((e as Error).message); }
                finally { setFtBusy(false); }
              }}>{tr("set.ft.retrain", lang)}</button>
            </div>
            <label className="spec-row">
              <span>{tr("set.ft.use", lang)}</span>
              <input type="checkbox" checked={!!ft.active}
                     onChange={async (e) => {
                       if (!session.userId || !session.userToken) return;
                       const on = e.target.checked;
                       try {
                         await api.setFinetuneActive(session.userId, session.userToken, on);
                         setFt({ ...ft, active: on });
                       } catch (err) { setFtError((err as Error).message); }
                     }} />
            </label>
            <p className="muted small">{tr("set.ft.offswitch", lang)}</p>
          </>
        ) : (
          <>
            <p className="muted small">{tr("set.ft.none", lang)}</p>
            <button disabled={ftBusy} onClick={async () => {
              if (!session.userId || !session.userToken) return;
              setFtBusy(true); setFtError(null);
              try { setFt(await api.runFinetune(session.userId, session.userToken)); }
              catch (e) { setFtError((e as Error).message); }
              finally { setFtBusy(false); }
            }}>{tr("set.ft.train", lang)}</button>
          </>
        )}
        {ftError && <p className="muted small">{ftError}</p>}
      </div>

      <div className="card">
        <h3>{tr("cont.title", lang)}</h3>
        <p className="muted small">
          {tr("cont.lead", lang)}
        </p>
        {cont?.built && cont.vector ? (
          <>
            <div className="spec-row">
              <div>
                <b>{cont.observations} {tr("cont.observations", lang)}</b>
                <div className="muted small">
                  {cont.conditioning
                    ? tr("cont.shaping", lang)
                    : tr("cont.not_yet", lang)}
                </div>
              </div>
              <button onClick={async () => {
                if (!session.userId || !session.userToken) return;
                await api.forgetContinuity(session.userId, session.userToken);
                setCont(await api.continuity(session.userId, session.userToken));
              }}>{tr("cont.forget", lang)}</button>
            </div>
            <ul className="refs">
              {Object.entries(cont.vector).map(([dim, value]) => (
                <li key={dim}>
                  {dim}: {Math.round(value * 100)}{"%"}
                  {cont.meanings?.[dim] ? ` — ${cont.meanings[dim]}` : ""}
                </li>
              ))}
            </ul>
            <p className="muted small">{cont.method}</p>
          </>
        ) : (
          <p className="muted small">{cont?.note || tr("cont.nothing", lang)}</p>
        )}
        <p className="muted small">{cont?.carries}</p>
      </div>

      <div className="card">
        <h3>{tr("set.anon", lang)}</h3>
        {anon ? (anon.anonymous ? (
          <>
            <p>
              {tr("set.anon.pseudo", lang).replace("{name}", String(anon.known_as))}
            </p>
            <ul className="refs">
              {anon.keeps.map((k, i) => <li key={i}>{tr("set.anon.keeps", lang)
                .replace("{x}", k)}</li>)}
              {anon.costs.map((c, i) => <li key={`c${i}`}>{tr("set.anon.costs", lang)
                .replace("{x}", c)}</li>)}
            </ul>
          </>
        ) : (
          <p className="muted small">
            {tr("set.anon.own", lang).replace("{name}", String(anon.known_as))}
          </p>
        )) : <p className="muted small">…</p>}
      </div>

      <MoneyCard />
      <CloudContributionCard />
      <LocalityCard />

      <div className="card">
        <h3>{tr("set.data", lang)}</h3>
        <p className="muted small">{tr("set.data.note", lang).replace("{uid}", String(session.userId))}</p>
        <button className="danger" onClick={signOut}>{tr("set.data.signout", lang)}</button>
      </div>
      <Problems />
    </div>
  );
}


// The money guardian. Every reader-facing word on this card — headings,
// buttons, placeholders, the custody note, the warnings — arrives from
// `GET /money/{id}` in the reader's language. This console has no
// translation table of its own, and its English backlog is a ratchet that
// only shrinks, so the server speaks and the card shows.
function MoneyCard() {
  const { session } = useSession();
  const [view, setView] = useState<MoneyView | null>(null);
  const [inst, setInst] = useState("");
  const [kind, setKind] = useState("checking");
  const [acct, setAcct] = useState("");
  const [routing, setRouting] = useState("");
  const [obsAccount, setObsAccount] = useState("");
  const [obsBalance, setObsBalance] = useState("");
  const [goal, setGoal] = useState("");
  const [scope, setScope] = useState("");
  const [capOrder, setCapOrder] = useState("");
  const [capMonth, setCapMonth] = useState("");
  const [said, setSaid] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [statements, setStatements] = useState<StatementRow[]>([]);
  const [stmAccount, setStmAccount] = useState("");
  const [stmFile, setStmFile] = useState<{ name: string; b64: string } | null>(null);
  const [links, setLinks] = useState<BankLinkRow[]>([]);
  const [linkInst, setLinkInst] = useState("");
  const [linkAgg, setLinkAgg] = useState("plaid");

  const uid = session.userId, token = session.userToken;
  function load() {
    if (!uid || !token) return;
    api.moneyView(uid, token).then(setView).catch(() => setView(null));
    api.moneyStatements(uid, token).then(setStatements)
      .catch(() => setStatements([]));
    api.moneyLinks(uid, token).then(setLinks).catch(() => setLinks([]));
  }

  function pickStatement(file: File | null) {
    if (!file) { setStmFile(null); return; }
    const reader = new FileReader();
    reader.onload = () => {
      const url = String(reader.result || "");
      setStmFile({ name: file.name, b64: url.slice(url.indexOf(",") + 1) });
    };
    reader.readAsDataURL(file);
  }
  useEffect(load, [uid]);
  if (!uid || !token || !view) return null;
  const L = view.labels;

  async function run(action: () => Promise<unknown>) {
    setError(null); setSaid(null);
    try { await action(); load(); }
    catch (e) { setError((e as Error).message); }
  }

  return (
    <div className="card">
      <h3>{L.title}</h3>
      <p className="muted small">{view.note}</p>
      {error && <p className="error">{error}</p>}
      {said && <p className="muted small">{said}</p>}

      <h4>{L.accounts}</h4>
      {view.accounts.map((a) => (
        <p key={a.id} className="muted small">
          {a.label} · {a.kind} · {a.institution}
          {a.last4 ? ` ····${a.last4}` : ""}
          {a.balance != null ? ` · ${L.balance}: ${a.balance}` : ""}
        </p>
      ))}
      <div className="row">
        <input placeholder={L.institution} value={inst}
          onChange={(e) => setInst(e.target.value)} />
        <select value={kind} onChange={(e) => setKind(e.target.value)}>
          {["checking", "savings", "brokerage", "crypto"].map((k) => (
            <option key={k} value={k}>{k}</option>
          ))}
        </select>
        <input placeholder={L.account_number} value={acct}
          onChange={(e) => setAcct(e.target.value)} />
        <input placeholder={L.routing_number} value={routing}
          onChange={(e) => setRouting(e.target.value)} />
        <button disabled={!inst.trim()}
          onClick={() => run(() => api.moneyAddAccount(uid, {
            kind, institution: inst.trim(),
            account_number: acct.trim() || undefined,
            routing_number: routing.trim() || undefined }, token))}>
          {L.add_account}
        </button>
      </div>

      <h4>{L.record_balance}</h4>
      <div className="row">
        <select value={obsAccount}
          onChange={(e) => setObsAccount(e.target.value)}>
          <option value=""></option>
          {view.accounts.map((a) => (
            <option key={a.id} value={a.id}>{a.label}</option>
          ))}
        </select>
        <input placeholder={L.balance} value={obsBalance}
          onChange={(e) => setObsBalance(e.target.value)} />
        <button disabled={!obsAccount || !obsBalance.trim()}
          onClick={() => run(async () => {
            const out = await api.moneyObserve(uid, {
              account_id: obsAccount,
              balance: Number(obsBalance) }, token);
            setSaid(out.warnings.map((w) => w.message).join(" ") || null);
          })}>
          {L.record_balance}
        </button>
      </div>

      {/* Statements: the file is sealed in the vault and read locally;
          a closing balance walks the same observe path a typed one does. */}
      <h4>{L.statements}</h4>
      <div className="row">
        <select value={stmAccount}
          onChange={(e) => setStmAccount(e.target.value)}>
          <option value=""></option>
          {view.accounts.map((a) => (
            <option key={a.id} value={a.id}>{a.label}</option>
          ))}
        </select>
        <input type="file" accept=".csv,.txt,.pdf"
          onChange={(e) => pickStatement(e.target.files?.[0] ?? null)} />
        <button disabled={!stmAccount || !stmFile}
          onClick={() => run(async () => {
            const out = await api.moneyDropStatement(uid, {
              account_id: stmAccount, filename: stmFile!.name,
              content: stmFile!.b64 }, token);
            setStmFile(null);
            setSaid(`${out.filename} · ${out.line_count} · +${out.total_in}` +
                    ` −${out.total_out}` +
                    (out.end_balance != null ? ` · ${out.end_balance}` : ""));
          })}>
          {L.drop_statement}
        </button>
      </div>
      {statements.map((s) => (
        <p key={s.id} className="muted small">
          {s.filename} · {s.line_count} · +{s.total_in} −{s.total_out}
          {s.end_balance != null ? ` · ${s.end_balance}` : ""}
        </p>
      ))}

      {/* Bank links: a written aggregator consent; the status never
          claims data that was not pulled. */}
      <h4>{L.links}</h4>
      <div className="row">
        <input placeholder={L.institution} value={linkInst}
          onChange={(e) => setLinkInst(e.target.value)} />
        <select value={linkAgg} onChange={(e) => setLinkAgg(e.target.value)}>
          {["plaid", "tink", "truelayer", "mx"].map((a) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>
        <button disabled={!linkInst.trim()}
          onClick={() => run(() => api.moneyLinkBank(uid, {
            institution: linkInst.trim(), aggregator: linkAgg }, token))}>
          {L.link_bank}
        </button>
      </div>
      {links.map((l) => (
        <div key={l.id} className="row">
          <span className="muted small" style={{ flex: 1 }}>
            {l.institution} · {l.aggregator} · {l.status}
          </span>
          <button onClick={() => run(() => api.moneySyncBank(uid, l.id, token))}>
            {L.sync}
          </button>
          {l.status !== "revoked" && (
            <button className="danger"
              onClick={() => run(() => api.moneyRevokeLink(uid, l.id, token))}>
              {L.revoke_link}
            </button>
          )}
        </div>
      ))}

      <h4>{L.savings_goal}</h4>
      <div className="row">
        <input placeholder={L.savings_goal} value={goal}
          onChange={(e) => setGoal(e.target.value)} />
        <button disabled={!goal.trim()}
          onClick={() => run(() => api.moneySetSavings(uid,
            { goal: Number(goal) }, token))}>
          {L.set_goal}
        </button>
        {view.savings && (
          <span className="muted small">{view.savings.goal}</span>
        )}
      </div>

      <h4>{L.mandate}</h4>
      <div className="row">
        <input placeholder={L.cap_per_order} value={capOrder}
          onChange={(e) => setCapOrder(e.target.value)} />
        <input placeholder={L.monthly_cap} value={capMonth}
          onChange={(e) => setCapMonth(e.target.value)} />
        <input placeholder={L.scope} value={scope}
          onChange={(e) => setScope(e.target.value)} />
        <button disabled={!scope.trim() || !capOrder.trim() || !capMonth.trim()}
          onClick={() => run(() => api.moneySetMandate(uid, {
            enabled: true, cap_per_order: Number(capOrder),
            monthly_cap: Number(capMonth),
            asset_classes: ["index_funds"], scope: scope.trim() }, token))}>
          {L.mandate_save}
        </button>
        {view.mandate?.enabled && (
          <button className="danger"
            onClick={() => run(() => api.moneySetMandate(uid,
              { enabled: false }, token))}>
            {L.mandate_revoke}
          </button>
        )}
      </div>
      {view.orders.length > 0 && (
        <>
          <h4>{L.orders}</h4>
          {view.orders.map((o) => (
            <p key={o.id} className="muted small">
              {o.asset_class} · {o.amount} · {o.status}
              {o.rationale ? ` — ${o.rationale}` : ""}
            </p>
          ))}
        </>
      )}
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
  const lang = visitorLang();
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
      <h3>{tr("set.cloud", lang)}</h3>
      <p className="muted small">
        {state.opted_in
          ? `Contributing. ${state.contributed.length} item${state.contributed.length === 1 ? "" : "s"} have gone to the shared model.`
          : "Not contributing. Nothing from this account has gone to the shared model."}
      </p>
      {state.policy && <p className="muted small">{state.policy}</p>}
      {state.preview_note && <p className="muted small">{state.preview_note}</p>}
      {/* The payload itself, verbatim. The note above describes it; this IS
          it — composed by the same function that sends, so what is shown and
          what would leave cannot drift apart. Rendered without a new English
          empty-state sentence on purpose: the console's untranslated backlog
          is a ratchet that only shrinks, and `preview_note` already carries
          the words. */}
      {state.preview_next != null && (
        <pre className="small" style={{ overflowX: "auto" }}>
          {JSON.stringify(state.preview_next, null, 2)}
        </pre>
      )}
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
          {tr("set.cloud.stop", lang)}
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
  const lang = visitorLang();
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
      <h3>{tr("set.loc", lang)}</h3>
      <p className="muted small">{tr("set.loc.pitch", lang)}</p>
      <div className="row">
        <input
          value={locality}
          placeholder={tr("set.loc.ph", lang)}
          onChange={(e) => setLocality(e.target.value)} />
        <button disabled={busy || !locality.trim()}
          onClick={() => save(locality.trim())}>{tr("set.save", lang)}</button>
        <button disabled={busy}
          onClick={() => { setLocality(""); save(null); }}>{tr("set.clear", lang)}</button>
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
  const lang = visitorLang();
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
      <h3>{tr("set.mail", lang)}</h3>
      <p className="muted small">
        {cfg?.transport === "smtp"
          ? tr("set.mail.smtp", lang)
              .replace("{host}", String(cfg.host))
              .replace("{env}", cfg.source === "environment"
                ? " (set by environment variables)" : "")
          : tr("set.mail.none", lang)}
      </p>
      {cfg?.source !== "environment" && (<>
        <div className="row">
          <label>{tr("set.mail.host", lang)}<input value={host} placeholder={tr("set.mail.host.ph", lang)} onChange={(e) => setHost(e.target.value)} /></label>
          <label>{tr("set.mail.port", lang)}<input type="number" value={port} onChange={(e) => setPort(Number(e.target.value))} /></label>
        </div>
        <label>{tr("set.mail.user", lang)}<input value={username} placeholder={tr("set.mail.user.ph", lang)} onChange={(e) => setUsername(e.target.value)} /></label>
        <label>{tr("set.mail.pass", lang)} {cfg?.password_set && <span className="muted small">{tr("set.mail.saved", lang)}</span>}
          <input type="password" value={password} placeholder={tr("set.mail.pass.ph", lang)} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <label>{tr("set.mail.from", lang)}<input value={sender} placeholder={tr("set.mail.user.ph", lang)} onChange={(e) => setSender(e.target.value)} /></label>
        <label>{tr("set.mail.link", lang)} <span className="muted small">{tr("set.mail.link.note", lang)}</span>
          <input value={publicUrl} placeholder={tr("set.mail.link.ph", lang)} onChange={(e) => setPublicUrl(e.target.value)} />
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
              {tr("set.clear", lang)}
            </button>
          )}
        </div>
      </>)}
      {cfg?.transport === "smtp" && (<>
        <label>{tr("set.mail.test", lang)}<input value={testTo} placeholder={tr("set.mail.test.ph", lang)} onChange={(e) => setTestTo(e.target.value)} /></label>
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
  const lang = visitorLang();
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
      <h3>{tr("set.model", lang)}</h3>
      <p className="muted small">{tr("set.model.pitch", lang)}</p>
      <ProviderTiles providers={providers} chosen={chosen}
                     effective={effective} onPick={pick} busy={busy} />
      {/* The truth about what will actually answer. The silent case was the
          bad one: Automatic quietly resolving to the stub while the screen
          full of logos implied a real model was on. */}
      {effective === "stub" && chosen !== "stub" ? (
        <div className="degraded">{tr("set.model.stub", lang)}</div>
      ) : effective && chosen !== "auto" && chosen !== effective && (
        <div className="degraded">
          {tr("set.model.resolves", lang).replace("{effective}", effective)}
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
  const lang = visitorLang();
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
        // Trimmed, like the three phone shells always did. This console was
        // the odd one out, and a key pasted from a dashboard carries a
        // trailing newline often enough that it is the normal case, not the
        // edge one — it reached an HTTP header verbatim and took the whole
        // request down with a 500.
        api_key: apiKey.trim() || undefined,
        voice_id: next?.voice_id ?? voiceId,
        speak_replies: next?.speak_replies,
      });
      setApiKey(""); load();
      // "Saved." was the wrong sentence. It reported that a string had been
      // written down — always true — and said nothing about whether the
      // string was a key. Somebody who pastes the key's *ID*, which the
      // ElevenLabs dashboard shows permanently beside every key while
      // showing the key itself once, got "Saved." here and then a raw
      // provider error several screens away, at the moment they asked to be
      // spoken to. So the provider is asked now and its answer is the line.
      setNote(tr("set.voice.saved", lang));
      try {
        const check = await api.checkVoiceKey();
        const said = tr(`set.voice.${check.verdict}`, lang);
        // A key the service refused belongs in the red box, not in the grey
        // line under it. The grey line is where "Saved." lived, and the
        // whole finding here is that a quiet confirmation was covering a
        // deployment that could not speak.
        if (check.ok) setNote(said);
        else { setNote(null); setError(said); }
      } catch {
        // 503: nothing to check — the device voice, or a provider this
        // check does not cover. "Saved." stands, and is the whole truth.
      }
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  const voices = cfg?.voices || [];
  return (
    <div className="card">
      <h3>{tr("set.voice", lang)}</h3>
      <p className="muted small">
        {cfg?.provider === "device"
          ? tr("set.voice.device", lang)
          : tr("set.voice.through", lang)
              .replace("{provider}", String(cfg?.provider))
              .replace("{env}", cfg?.key_source === "environment"
                ? " (key from the environment)" : "")}
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
        <label>{tr("set.key.label", lang)} {cfg?.key_set && <span className="muted small">{tr("set.mail.saved", lang)}</span>}
          <input type="password" value={apiKey} placeholder={provider === "elevenlabs" ? "ElevenLabs key" : "sk-…"}
                 onChange={(e) => setApiKey(e.target.value)} />
        </label>
        {voices.length > 0 && (
          <label>{tr("set.voice", lang)}
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
            {tr("set.voice.hear", lang)}
          </button>
        </div>
      </>)}
      {provider === "device" && (
        <button disabled={busy}
                onClick={() => say("Hello — this is your device's own voice.")}>
          {tr("set.voice.hear", lang)}
        </button>
      )}
      {note && <div className="muted small">{note}</div>}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}

function WatchPanel() {
  const { session } = useSession();
  const lang = visitorLang();
  const [ch, setCh] = useState<WatchChannel | null>(null);
  const [copied, setCopied] = useState(false);
  const [busy, setBusy] = useState(false);
  const [report, setReport] = useState<SeedReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [device, setDevice] = useState("apple_watch");

  function load(dev = device) {
    if (!session.userId || !session.userToken) return;
    api.getWatchChannel(session.userId, session.userToken, dev)
      .then(setCh).catch(() => setCh(null));
  }
  useEffect(() => load(), [session.userId, device]);

  if (!session.userId || !session.userToken) return null;

  async function rotate() {
    setBusy(true); setError(null);
    try { setCh(await api.rotateWatchChannel(session.userId!, session.userToken!, device)); }
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
      <h3>{tr("watch.title", visitorLang())}</h3>
      <p className="muted small">{tr("watch.lead", visitorLang())}</p>
      {ch && (
        <div className="actions" style={{ flexWrap: "wrap" }}>
          {ch.devices.map((d) => (
            <button key={d.key}
                    className={d.key === device ? "primary" : ""}
                    disabled={busy}
                    onClick={() => setDevice(d.key)}>{d.name}</button>
          ))}
        </div>
      )}
      {ch ? (<>
        {/* The truth about the address below: a loopback-bound backend
            serves a Wi-Fi URL nothing answers on. On the desktop the fix
            is one switch away; elsewhere, the card says what to run. */}
        {!ch.phone_reachable && (
          <div className="degraded">
            {tr("set.watch.unreach", lang)}
            {desktop() ? (
              <div style={{ marginTop: 8 }}>
                <button className="primary" disabled={busy} onClick={enableLan}>
                  {tr("set.watch.lan", lang)}
                </button>
                <div className="muted small" style={{ marginTop: 6 }}>
                  {tr("set.watch.lan.note", lang)}
                </div>
              </div>
            ) : (
              <div className="muted small" style={{ marginTop: 6 }}>
                {tr("set.watch.cli", lang)}
              </div>
            )}
          </div>
        )}
        {ch.phone_reachable && (
          <div className="muted small">{tr("set.watch.ok", lang)}</div>
        )}
        <label>{tr("watch.address", visitorLang())}
          <input readOnly value={ch.drip_url} onFocus={(e) => e.currentTarget.select()} />
        </label>
        <div className="actions">
          <button className="primary" onClick={() => {
            navigator.clipboard?.writeText(ch.drip_url);
            setCopied(true); setTimeout(() => setCopied(false), 1500);
          }}>{copied ? "Copied ✓" : "Copy address"}</button>
          <button disabled={busy} onClick={rotate}>{tr("set.watch.newaddr", lang)}</button>
        </div>
        <div className="muted small" style={{ marginTop: 8 }}>
          {ch.drips > 0
            ? tr("set.watch.received", lang)
                .replace("{n}", String(ch.drips))
                .replace("{s}", ch.drips === 1 ? "" : "s")
                .replace("{when}", ch.last_drip_at
                  ? new Date(ch.last_drip_at).toLocaleString() : "—")
            : "Nothing has arrived yet — run the automation once by hand to test it."}
        </div>
        <details style={{ marginTop: 10 }}>
          <summary className="muted small">{tr("watch.setup", visitorLang())}</summary>
          <ol className="muted small">
            {ch.steps.map((s, i) => <li key={i}>{s}</li>)}
          </ol>
        </details>
        <div style={{ marginTop: 12 }}>
          <label>{tr("watch.seed", visitorLang())}
            <input type="file" accept=".zip,.xml" disabled={busy}
                   onChange={(e) => { const f = e.target.files?.[0]; if (f) upload(f); e.target.value = ""; }} />
          </label>
          <div className="muted small">{ch.seed_hint}</div>
        </div>
        {report && (
          <div className="muted small" style={{ marginTop: 8 }}>
            {Object.entries(report.seeded).map(([metric, r]) => (
              <div key={metric}>
                {tr("set.watch.seeded", lang)
                  .replace("{metric}", metric.replace(/_/g, " "))
                  .replace("{d}", String(r.days))
                  .replace("{s}", r.days === 1 ? "" : "s")
                  .replace("{b}", String(r.baseline))
                  .replace("{tail}", r.provisional
                    ? " (still learning)" : " — established")}
              </div>
            ))}
          </div>
        )}
      </>) : <div className="muted small">{tr("set.watch.signin", lang)}</div>}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}

function VigilPanel() {
  const { session } = useSession();
  const lang = visitorLang();
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
      <h3>{tr("set.vigil", lang)}</h3>
      <p className="muted small">{tr("set.vigil.pitch", lang)}</p>
      {st?.tripped && (
        <div className="degraded">
          {tr("set.vigil.tripped", lang)
            .replace("{name}", String(st.steward_name))
            .replace("{after}", st.silent_hours != null
              ? tr("set.vigil.after", lang).replace("{n}",
                  String(Math.round((st.silent_hours) / 24 * 10) / 10))
              : "")}
          <div style={{ marginTop: 8 }}>
            <button className="primary" disabled={busy}
                    onClick={() => run(() => api.resolveVigil(session.userId!, session.userToken!))}>
              {tr("set.vigil.okay", lang)}
            </button>
          </div>
        </div>
      )}
      <div className="row">
        <label>{tr("set.vigil.name", lang)}<input value={name} placeholder={tr("set.vigil.name.ph", lang)} onChange={(e) => setName(e.target.value)} /></label>
        <label>{tr("set.vigil.reach", lang)}<input value={channel} placeholder={tr("set.vigil.reach.ph", lang)} onChange={(e) => setChannel(e.target.value)} /></label>
      </div>
      <label>{tr("set.vigil.days", lang)}
        <input type="number" min={1} max={60} value={days} onChange={(e) => setDays(Number(e.target.value))} />
      </label>
      <label>{tr("set.vigil.words", lang)} <span className="muted small">{tr("set.vigil.words.note", lang)}</span>
        <input value={note} placeholder={tr("set.vigil.words.ph", lang)} onChange={(e) => setNote(e.target.value)} />
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
            {tr("set.vigil.disarm", lang)}
          </button>
        )}
        {/* A read, not a sweep. Opening this screen sweeps — which is the
            right default, because opening the app is the natural moment to
            ask whether anybody has gone quiet — but a sweep can *trip* the
            vigil and send a stranger to somebody's door. That makes it a
            write, and a write should not be the only way to look at a
            thing. This is the way to look without acting. */}
        <button disabled={busy}
                onClick={() => run(() => api.getVigil(session.userId!, session.userToken!))}>
          {tr("set.vigil.check", lang)}
        </button>
      </div>
      {st?.armed && st.last_heard_at && !st.tripped && (
        <div className="muted small">
          {tr("set.vigil.armed", lang)
            .replace("{when}", st.silent_hours != null
              ? `${st.silent_hours}h ago` : "recently")
            .replace("{name}", String(st.steward_name))}
        </div>
      )}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}


/** What this deployment can and cannot reach.
 *
 *  Offline mode was settable and unreadable: the flag existed, the guarantee
 *  was written in a docstring, and there was nowhere for the person running
 *  the deployment — or an auditor standing behind them — to see the answer.
 *
 *      asked     can the guarantee be turned on
 *      mattered  can it be checked
 *
 *  Read-only on purpose. This is a posture the deployment sets in its
 *  environment, not a switch in a console: a button here would imply somebody
 *  signed into the app can decide whether the host talks to the internet.
 */
function OfflinePosture() {
  const [posture, setPosture] = useState<Awaited<
    ReturnType<typeof api.offlineStatus>> | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    api.offlineStatus().then(setPosture).catch(() => setFailed(true));
  }, []);

  if (failed) return null;
  if (!posture) return <div className="card"><p className="small">…</p></div>;

  return (
    <div className="card">
      <h3>{posture.offline ? "Offline — nothing leaves this host"
                           : "Online"}</h3>
      <p className="small">
        {posture.external_transmission_possible
          ? "This deployment can reach other machines."
          : "Every path out of this host refuses any address that is not "
            + "this machine or its own network."}
      </p>
      <ul className="small muted">
        {posture.guarantees.map((g) => <li key={g}>{g}</li>)}
      </ul>
      <p className="muted small">{posture.local_destinations_allowed}</p>
    </div>
  );
}
