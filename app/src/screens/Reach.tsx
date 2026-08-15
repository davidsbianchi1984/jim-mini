import { useEffect, useState } from "react";
import { api, type PlacedCodeCard, type RobotModel, type Row,
         type SocialBeacon } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The things that reach past this window: a body that can move through the
 * house, a printed code somebody can scan, an account on a platform JIM does
 * not run, and an excursion that goes and asks the open web a question.
 *
 * Twenty-four routes. What they have in common is that each of them crosses
 * a boundary, so each one is shown with what it costs to cross it:
 *
 *   * A robot is bound to an account and takes commands. The catalogue says
 *     per model whether its first-aid rating is `assist` or `perform`, which
 *     is the difference between a machine that helps somebody do CPR and one
 *     that does CPR — so the rating is on the tile, not in a footnote.
 *   * `/c/{bid}` is the path a phone camera lands on after scanning a placed
 *     code. It takes no credential by design: the point of a care code on a
 *     door is that a stranger can use it. What a stranger can *do* with it is
 *     capped one level below emergency services, which is on the ladder over
 *     in Who Else Is Looking.
 *   * An excursion leaves the host. The result carries `redactions` and
 *     `left_host`, and both are shown — the findings without the price of
 *     having asked is half the answer.
 */
export function Reach() {
  const { session } = useSession();
  const lang = visitorLang();
  const [models, setModels] = useState<RobotModel[]>([]);
  const [robots, setRobots] = useState<Row[]>([]);
  const [accounts, setAccounts] = useState<Row[]>([]);
  const [excursions, setExcursions] = useState<Row[]>([]);
  const [entry, setEntry] = useState<Row | null>(null);
  const [visits, setVisits] = useState<Row[]>([]);
  // The scan page is HTML and the codes are SVG. They are held as text
  // because that is what the routes answer — see `reqText` in api.ts, and
  // the note there about how binding them through the JSON helper turned
  // both of them into a silent `null`.
  const [scanned, setScanned] = useState<string | null>(null);
  const [card, setCard] = useState<PlacedCodeCard | null>(null);
  const [beacon, setBeacon] = useState<SocialBeacon | null>(null);
  const [qr, setQr] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [model, setModel] = useState("");
  const [robotName, setRobotName] = useState("");
  const [command, setCommand] = useState("come_here");
  const [platform, setPlatform] = useState("mastodon");
  const [handle, setHandle] = useState("");
  const [direction, setDirection] = useState("publish");
  const [post, setPost] = useState("");
  const [topic, setTopic] = useState("");
  const [question, setQuestion] = useState("");
  const [bid, setBid] = useState("");
  const [dripToken, setDripToken] = useState("");

  const uid = session.userId;
  const token = session.userToken;

  function load() {
    if (!uid || !token) return;
    api.roboticsCatalog().then((c) => setModels(c.robots)).catch(fail);
    api.robots(uid, token).then(setRobots).catch(fail);
    api.socialAccounts(uid, token).then(setAccounts).catch(fail);
    api.excursions(uid, token).then(setExcursions).catch(fail);
    api.communityVisits(uid, token).then(setVisits).catch(fail);
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
        <h2>{tr("rch.title", lang)}</h2>
        <span className="muted small">{tr("rch.sub", lang)}</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      <div className="card">
        <h3>{tr("rch.body", lang)}</h3>
        <div className="row">
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            <option value="">{tr("rch.body.pick", lang)}</option>
            {models.map((m) => (
              <option key={m.model} value={m.model}>
                {tr("rch.body.model", lang)
                  .replace("{label}", m.label)
                  .replace("{maker}", m.maker)
                  .replace("{aid}", m.first_aid)}
              </option>
            ))}
          </select>
          <input value={robotName} placeholder={tr("rch.body.name.ph", lang)}
                 onChange={(e) => setRobotName(e.target.value)} />
          <button className="primary" disabled={busy || !model}
                  onClick={() => run(async () => {
                    await api.bindRobot(uid!, {
                      model, name: robotName.trim() || undefined }, token!);
                    setRobotName("");
                  })}>{tr("rch.body.bind", lang)}</button>
        </div>
        <p className="muted small">{tr("rch.body.rating", lang)}</p>
        {robots.map((r) => (
          <div key={String(r.id)} className="row"
               style={{ padding: "6px 0", borderBottom: "1px solid var(--line)" }}>
            <span style={{ flex: 1 }}>
              {String(r.name ?? r.model)}{" "}
              <span className="muted small">{String(r.model)}</span>
            </span>
            <input value={command} style={{ width: 140 }}
                   onChange={(e) => setCommand(e.target.value)} />
            <button disabled={busy}
                    onClick={() => run(() => api.commandRobot(
                      uid!, String(r.id),
                      { command: command.trim() }, token!))}>{tr("rch.body.send", lang)}</button>
            <button disabled={busy}
                    onClick={() => run(() => api.unbindRobot(
                      uid!, String(r.id), token!))}>{tr("rch.body.unbind", lang)}</button>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("rch.code", lang)}</h3>
        <div className="row">
          <input value={bid} placeholder={tr("rch.code.bid.ph", lang)}
                 onChange={(e) => setBid(e.target.value)} />
          <button disabled={busy || !bid.trim()}
                  onClick={() => run(async () => {
                    setScanned(await api.placedCode(bid.trim()));
                  })}>{tr("rch.code.see", lang)}</button>
          <button disabled={busy || !bid.trim()}
                  onClick={() => run(async () => {
                    setCard(await api.placedCodeCard(bid.trim()));
                  })}>{tr("rch.code.card", lang)}</button>
          <button disabled={busy || !bid.trim()}
                  onClick={() => run(async () => {
                    setQr(await api.placedCodeQr(bid.trim()));
                  })}>{tr("rch.code.printable", lang)}</button>
        </div>
        <div className="row">
          <button disabled={busy || !bid.trim()}
                  onClick={() => run(() => api.raiseFromCode(bid.trim(),
                    { message: "Someone here needs help" }))}>
            {tr("rch.code.raise", lang)}
          </button>
          <button disabled={busy || !bid.trim()}
                  onClick={() => run(() => api.pickUpCode(bid.trim(), token!))}>
            {tr("rch.code.down", lang)}
          </button>
        </div>
        <p className="muted small">{tr("rch.code.pitch", lang)}</p>
        {scanned && (
          <p className="muted small">
            {tr("rch.code.scanned", lang)
              .replace("{n}", String(scanned.length))
              .replace("{path}", `/c/${bid.trim()}`)}
          </p>
        )}
        {card && (
          <p className="muted small">
            <strong>{card.first_name}</strong> — {card.note} {card.call_first}
            {" "}<em>{card.badge}</em>
          </p>
        )}
        {qr && (
          <img alt={tr("rch.code.qr.alt", lang)}
               src={"data:image/svg+xml;utf8," + encodeURIComponent(qr)}
               style={{ width: 160, height: 160 }} />
        )}
      </div>

      <div className="card">
        <h3>{tr("rch.acc", lang)}</h3>
        <div className="row">
          <input value={platform} placeholder={tr("rch.acc.platform.ph", lang)}
                 onChange={(e) => setPlatform(e.target.value)} />
          <input value={handle} placeholder={tr("rch.acc.handle.ph", lang)}
                 onChange={(e) => setHandle(e.target.value)} />
          <select value={direction}
                  onChange={(e) => setDirection(e.target.value)}>
            <option value="publish">{tr("rch.acc.publish.opt", lang)}</option>
            <option value="collect">{tr("rch.acc.collect.opt", lang)}</option>
          </select>
          <button className="primary" disabled={busy || !platform.trim()}
                  onClick={() => run(async () => {
                    await api.connectSocialAccount(uid!, {
                      platform: platform.trim(), direction,
                      handle: handle.trim() || undefined }, token!);
                    setHandle("");
                  })}>{tr("rch.acc.connect", lang)}</button>
        </div>
        {accounts.map((a) => (
          <div key={String(a.id)}
               style={{ padding: "8px 0", borderBottom: "1px solid var(--line)" }}>
            <div className="row">
              <span style={{ flex: 1 }}>
                {String(a.platform)} {String(a.handle ?? "")}
              </span>
              <span className="muted small">{String(a.direction)}</span>
              <button disabled={busy}
                      onClick={() => run(async () => {
                        setBeacon(await api.socialBeaconCard(
                          String(a.id), token!));
                      })}>{tr("rch.acc.beacon", lang)}</button>
              <button disabled={busy}
                      onClick={() => run(async () => {
                        setQr(await api.socialQr(String(a.id), token!));
                      })}>{tr("rch.acc.code", lang)}</button>
              <button disabled={busy}
                      onClick={() => run(() => api.disconnectSocialAccount(
                        String(a.id), token!))}>{tr("rch.acc.disconnect", lang)}</button>
            </div>
            {a.direction === "publish" ? (
              <div className="row">
                <input value={post} placeholder={tr("rch.acc.say.ph", lang)}
                       onChange={(e) => setPost(e.target.value)} />
                <button disabled={busy || !post.trim()}
                        onClick={() => run(async () => {
                          await api.publishToSocial(String(a.id), {
                            content: post.trim() }, token!);
                          setPost("");
                        })}>{tr("rch.acc.publish", lang)}</button>
              </div>
            ) : (
              <div className="row">
                <button disabled={busy}
                        onClick={() => run(() => api.collectFromSocial(
                          String(a.id),
                          { items: [{ content: "a post from elsewhere" }] },
                          token!))}>{tr("rch.acc.collect", lang)}</button>
                {a.handle ? (
                  <button disabled={busy}
                          onClick={() => run(() => api.scrapeSocial(
                            String(a.id), token!))}>
                    {tr("rch.acc.scrape", lang)}
                  </button>
                ) : null}
              </div>
            )}
          </div>
        ))}
      </div>

      {beacon && (
        <div className="card">
          <h3>{beacon.platform} · {beacon.handle}</h3>
          <p className="muted small">
            {tr("rch.beacon.note", lang)
              .replace("{url}", beacon.presence_url ?? "no public address")}
          </p>
        </div>
      )}

      <div className="card">
        <h3>{tr("rch.ask", lang)}</h3>
        <div className="row">
          <input value={topic} placeholder={tr("rch.ask.topic.ph", lang)}
                 onChange={(e) => setTopic(e.target.value)} />
          <input value={question} placeholder={tr("rch.ask.q.ph", lang)}
                 onChange={(e) => setQuestion(e.target.value)} />
          <button className="primary"
                  disabled={busy || !topic.trim() || !question.trim()}
                  onClick={() => run(async () => {
                    await api.startExcursion(uid!, {
                      topic: topic.trim(), question: question.trim(),
                      private: true }, token!);
                    setQuestion("");
                  })}>{tr("rch.ask.go", lang)}</button>
        </div>
        {excursions.map((x) => (
          <div key={String(x.id)}
               style={{ padding: "8px 0", borderBottom: "1px solid var(--line)" }}>
            <div className="row">
              <span style={{ flex: 1 }}>{String(x.topic ?? "")}</span>
              <span className="muted small">
                {x.left_host ? tr("rch.left", lang) : tr("rch.stayed", lang)}
                {x.redactions != null
                  ? ` · ${String(x.redactions)} redactions`
                  : ""}
              </span>
              <button disabled={busy}
                      onClick={() => run(async () => {
                        setEntry(await api.excursionEntry(String(x.id)));
                      })}>{tr("rch.ask.read", lang)}</button>
              <button disabled={busy}
                      onClick={() => run(() => api.learnFromExcursion(
                        String(x.id), token!))}>{tr("rch.ask.keep", lang)}</button>
            </div>
          </div>
        ))}
        {entry && <p className="muted small">{JSON.stringify(entry)}</p>}
        <p className="muted small">{tr("rch.ask.price", lang)}</p>
      </div>

      <div className="card">
        <h3>{tr("rch.wrist", lang)}</h3>
        <p className="muted small">
          {tr("rch.wrist.visits", lang)
            .replace("{n}", String(visits.length))}
        </p>
        <div className="row">
          <input value={dripToken} placeholder={tr("rch.wrist.token.ph", lang)}
                 onChange={(e) => setDripToken(e.target.value)} />
          <button disabled={busy || !dripToken.trim()}
                  onClick={() => run(() => api.watchDrip(dripToken.trim(),
                    { heart_rate: 62 }))}>{tr("rch.wrist.send", lang)}</button>
        </div>
        <p className="muted small">{tr("rch.wrist.pitch", lang)}</p>
      </div>
    </div>
  );
}
