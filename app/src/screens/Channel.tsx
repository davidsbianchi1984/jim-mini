import { useCallback, useEffect, useState } from "react";
import {
  api, type AssistedCall, type CallRow, type CaptureRow,
  type LiaisonHalf, type LiaisonRow, type MonitorRow,
  type CaptureVocabulary, type DeviceRow, type MicEvent, type MicGains,
  type MicState, type MicTypes,
} from "../api";
import { useSession } from "../store";
import { t as tr, visitorLang } from "../l10n";

/**
 * Channel 2 and the clinical camera — the two ways JIM takes something in
 * from the body rather than from a form.
 *
 * Both had complete backends and no caller anywhere. The microphone could be
 * attached, metered, handed to a call and released, and its whole history
 * read back; the camera could seal a photograph into the vault, release a
 * chosen few to a clinician and withdraw one afterwards. None of it was
 * reachable.
 *
 * Every vocabulary on this screen is fetched rather than typed out. The mic
 * types, the gain levels, the twenty-one capture sites and the list of which
 * ones count as intimate all come from the server, so the pickers cannot
 * offer a value the handler would refuse — and so the *rules* travel with the
 * options instead of being restated here, where they would drift.
 */
export function Channel() {
  const { session } = useSession();
  const uid = session.userId;
  const token = session.userToken;

  const [devices, setDevices] = useState<DeviceRow[]>([]);
  const [types, setTypes] = useState<MicTypes | null>(null);
  const [gains, setGains] = useState<MicGains | null>(null);
  const [mic, setMic] = useState<MicState | null>(null);
  const [history, setHistory] = useState<MicEvent[]>([]);
  const [vocab, setVocab] = useState<CaptureVocabulary | null>(null);
  const [captures, setCaptures] = useState<CaptureRow[]>([]);

  const [deviceName, setDeviceName] = useState("");
  const [deviceKind, setDeviceKind] = useState("wearable");
  const [micDevice, setMicDevice] = useState("");
  const [micType, setMicType] = useState("");
  const [site, setSite] = useState("");
  const [kind, setKind] = useState("photo");
  const [note, setNote] = useState("");
  const [condition, setCondition] = useState("");
  const [consent, setConsent] = useState(false);
  const [chosen, setChosen] = useState<string[]>([]);
  // Capture id → the image bytes, once somebody has asked to see it. Not
  // preloaded: these are photographs of a body and they are fetched when
  // the person whose body it is presses the button.
  const [shown, setShown] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [said, setSaid] = useState<string | null>(null);
  // An aid on a call somebody else can hear. It is not listening until the
  // notice has gone out on the line — see jim/oncall.py.
  const [callRoute, setCallRoute] = useState("speaker");
  const [callNumber, setCallNumber] = useState("");
  const [call, setCall] = useState<AssistedCall | null>(null);
  const [calls, setCalls] = useState<CallRow[]>([]);
  // What may sense this person, and through what. Off rows are here too.
  const [mons, setMons] = useState<MonitorRow[]>([]);
  // Two guardians working together. The list answers which are still going
  // and why, and each row's half is what mine said.
  const [links, setLinks] = useState<LiaisonRow[]>([]);
  const [other, setOther] = useState("");
  const [half, setHalf] = useState<LiaisonHalf | null>(null);

  const load = useCallback(() => {
    if (!uid || !token) return;
    api.devices(uid, token).then(setDevices).catch(() => setDevices([]));
    api.micState(uid, token).then(setMic).catch(() => setMic(null));
    api.micHistory(uid, token).then(setHistory).catch(() => setHistory([]));
    api.captures(uid, token).then(setCaptures).catch(() => setCaptures([]));
    api.calls(uid, token).then(setCalls).catch(() => setCalls([]));
    api.monitors(uid, token).then(setMons).catch(() => setMons([]));
    api.liaisons(uid, token).then(setLinks).catch(() => setLinks([]));
  }, [uid, token]);

  useEffect(() => {
    api.micTypes().then(setTypes).catch(() => setTypes(null));
    api.micGains().then(setGains).catch(() => setGains(null));
    api.captureVocabulary().then(setVocab).catch(() => setVocab(null));
  }, []);
  useEffect(load, [load]);

  async function run(action: () => Promise<unknown>, ok?: string) {
    setBusy(true); setError(null); setSaid(null);
    try { await action(); if (ok) setSaid(ok); load(); }
    catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  if (!uid || !token) return <p>{tr("ch.signin", visitorLang())}</p>;

  const intimate = new Set(vocab?.intimate ?? []);
  const siteIsIntimate = site !== "" && intimate.has(site);

  return (
    <section className="screen">
      <h2>{tr("ch.title", visitorLang())}</h2>
      {error && <p className="error">{error}</p>}
      {said && <p className="muted">{said}</p>}

      {/* Two guardians, working together and never on the line. It opens
          only between people who are already each other's contacts, and the
          half shown here is what *this* guardian said — the other person's
          half was never theirs to read. */}
      <h3>{tr("lia.head", visitorLang())}</h3>
      <p className="muted">{tr("lia.lead", visitorLang())}</p>
      <div className="card">
        <input value={other} placeholder={tr("lia.who.ph", visitorLang())}
               onChange={(e) => setOther(e.target.value)} />
        <button disabled={busy || !other.trim()} onClick={() => run(async () => {
          await api.openLiaison(uid!, { other_id: other.trim() }, token!);
          setLinks(await api.liaisons(uid!, token!));
        }, tr("lia.opened", visitorLang()))}>
          {tr("lia.open", visitorLang())}
        </button>
      </div>
      {links.map((l) => (
        <div key={l.id} className="card">
          <div className="row">
            <strong>{l.about || l.with}</strong>
            <span className="pill">
              {l.running ? tr("lia.running", visitorLang())
                      : tr("lia.closed", visitorLang())}
            </span>
          </div>
          {/* The task is why it is still open — once both sides have said
              so. Naming it is the namer's own yes and nothing more, so the
              card says which of the three states this link is in rather
              than showing the words and leaving it ambiguous. */}
          {l.task && (
            <>
              <p className="muted small">{l.task}</p>
              <p className="muted small">
                {l.holds_it_open ? tr("lia.holds", visitorLang())
                  : l.you_agreed ? tr("lia.waiting", visitorLang())
                  : tr("lia.yours", visitorLang())}
              </p>
            </>
          )}
          <button disabled={busy} onClick={() => run(
            async () => setHalf(await api.liaisonHalf(uid!, l.id, token!)))}>
            {tr("lia.mine", visitorLang())}
          </button>
          {l.running && (
            <>
              <button disabled={busy} onClick={() => run(async () => {
                await api.liaisonSaid(uid!, l.id,
                  tr("lia.said.example", visitorLang()), token!);
                setHalf(await api.liaisonHalf(uid!, l.id, token!));
              }, tr("lia.saidit", visitorLang()))}>
                {tr("lia.say", visitorLang())}
              </button>
              <button disabled={busy} onClick={() => run(async () => {
                await api.liaisonTask(uid!, l.id,
                  tr("lia.task.example", visitorLang()), token!);
                setLinks(await api.liaisons(uid!, token!));
              }, tr("lia.tasked", visitorLang()))}>
                {tr("lia.task", visitorLang())}
              </button>
              {/* The other side's yes. Offered only where there is a task
                  this person has not already agreed to — agreeing with
                  yourself is not a thing the backend counts, so a button
                  offering it would be a button that does nothing. */}
              {l.task && !l.you_agreed && (
                <button disabled={busy} onClick={() => run(async () => {
                  await api.liaisonAgreed(uid!, l.id, token!);
                  setLinks(await api.liaisons(uid!, token!));
                }, tr("lia.agreed", visitorLang()))}>
                  {tr("lia.agree", visitorLang())}
                </button>
              )}
              <button disabled={busy} onClick={() => run(async () => {
                await api.closeLiaison(uid!, l.id, "stopped", token!);
                setLinks(await api.liaisons(uid!, token!));
              }, tr("lia.stopped", visitorLang()))}>
                {tr("lia.stop", visitorLang())}
              </button>
            </>
          )}
          {half?.link_id === l.id && (
            <div>
              <p className="small"><strong>{tr("lia.bymine", visitorLang())}</strong></p>
              {half.said_by_mine.map((line, i) => (
                <p key={i} className="muted small">{line}</p>
              ))}
              <p className="small"><strong>{tr("lia.tomine", visitorLang())}</strong></p>
              {half.said_to_mine.map((line, i) => (
                <p key={i} className="muted small">{line}</p>
              ))}
            </div>
          )}
        </div>
      ))}

      {/* Everywhere the monitoring plugs in. The rows that sense other
          people carry that on their face, and switching one on asks whether
          the people in that space have been told — because a hall camera
          going on with nobody having thought about the hall is the failure
          this screen exists to prevent. */}
      <h3>{tr("mon.head", visitorLang())}</h3>
      <p className="muted">{tr("mon.lead", visitorLang())}</p>
      {mons.map((m) => (
        <div key={m.name} className="card">
          <div className="row">
            <strong>{m.says}</strong>
            <span className="muted">{m.senses.join(" · ")}</span>
            {m.catches_others && (
              <span className="pill">{tr("mon.others", visitorLang())}</span>
            )}
          </div>
          <p className="muted small">
            {tr("mon.keeps", visitorLang())} {m.holds}
          </p>
          <p className="muted small">
            {m.on ? tr("mon.on", visitorLang()) : tr("mon.off", visitorLang())}
            {m.on && m.keeping && ` · ${tr("mon.keeping", visitorLang())}`}
          </p>
          {/* Hand it something the monitor perceived. Refused with a 403
              until this row is switched on — the one door. */}
          {m.on && (
            <button disabled={busy} onClick={() => run(
              () => api.monitorSensed(uid!, m.name, token!),
              tr("mon.sensing", visitorLang()))}>
              {tr("mon.sense", visitorLang())}
            </button>
          )}
          {m.on ? (
            <button disabled={busy} onClick={() => run(
              async () => setMons(await api.unplugMonitor(uid!, m.name, token!)),
              tr("mon.unplugged", visitorLang()))}>
              {tr("mon.unplug", visitorLang())}
            </button>
          ) : (
            <button disabled={busy} onClick={() => run(
              async () => setMons(await api.plugMonitor(uid!, m.name,
                { others_told: m.catches_others }, token!)),
              tr("mon.plugged", visitorLang()))}>
              {m.catches_others ? tr("mon.plug.told", visitorLang())
                                : tr("mon.plug", visitorLang())}
            </button>
          )}
        </div>
      ))}

      {/* An aid on a call other people can hear. The notice goes first: this
          card hands back the words and nothing listens until they have been
          played. The number is used to pick the language and is not kept. */}
      <h3>{tr("cal.head", visitorLang())}</h3>
      <p className="muted">{tr("cal.lead", visitorLang())}</p>
      <div className="card">
        <select value={callRoute} onChange={(e) => setCallRoute(e.target.value)}>
          {["speaker", "speakerphone", "car", "conference"].map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        <input value={callNumber} placeholder={tr("cal.number.ph", visitorLang())}
               onChange={(e) => setCallNumber(e.target.value)} />
        <button disabled={busy} onClick={() => run(async () => {
          setCall(await api.openCall(uid!, {
            route: callRoute, number: callNumber || undefined }, token!));
        })}>{tr("cal.open", visitorLang())}</button>

        {call && (
          <div>
            <p className="muted small">{tr("cal.play", visitorLang())}</p>
            {call.notices.map((part) => (
              <p key={part.language} className="small">
                <strong>{part.language}</strong> — {part.words}
              </p>
            ))}
            <p className="muted small">
              {tr("cal.from", visitorLang())} {call.language_from}
            </p>
            <button disabled={busy} onClick={() => run(async () => {
              await api.callAnnounced(uid!, call.id, token!);
              setCall({ ...call, listening: true });
            }, tr("cal.done", visitorLang()))}>
              {tr("cal.played", visitorLang())}
            </button>
            {/* Hand the agent what the call is hearing. Refused with a 409
                until the notice has actually gone out — the one door. */}
            <button disabled={busy} onClick={() => run(
              () => api.callHeard(uid!, call.id, token!),
              tr("cal.listening", visitorLang()))}>
              {tr("cal.listen", visitorLang())}
            </button>
            <button disabled={busy} onClick={() => run(async () => {
              await api.endCall(uid!, call.id, token!);
              setCall(null);
            }, tr("cal.ended", visitorLang()))}>
              {tr("cal.end", visitorLang())}
            </button>
          </div>
        )}
      </div>
      {calls.map((c) => (
        <div key={c.id} className="card">
          <div className="row">
            <strong>{c.route}</strong>
            <span className="muted">{c.spoken_in.join(" · ")}</span>
            {/* A call that never announced never listened, and stays here:
                it is the evidence that the ordering held. */}
            <span className="pill">
              {c.listened ? tr("cal.told", visitorLang())
                          : tr("cal.nevertold", visitorLang())}
            </span>
          </div>
          <p className="muted small">{c.said}</p>
        </div>
      ))}

      <h3>{tr("ch.devices", visitorLang())}</h3>
      <p className="muted">{tr("ch.devices.lead", visitorLang())}</p>
      {devices.map((d) => (
        <div key={d.id} className="card">
          <div className="row">
            <strong>{d.name}</strong>
            <span className="muted">{d.kind}</span>
            {d.transport && <span className="muted">{d.transport}</span>}
            {d.has_llm && <span className="pill">{tr("ch.dev.model", visitorLang())}</span>}
            {d.paired && (
              <span className="pill">{tr("dev.paired", visitorLang())}</span>
            )}
          </div>
        </div>
      ))}
      <div className="row">
        <input value={deviceName} placeholder={tr("ch.dev.name", visitorLang())}
          onChange={(e) => setDeviceName(e.target.value)} />
        <select value={deviceKind} onChange={(e) => setDeviceKind(e.target.value)}>
          {["wearable", "glasses", "headset", "speaker", "phone",
            "stationary", "spatial", "other"].map((k) => (
            <option key={k} value={k}>
              {tr(`dev.kind.${k}`, visitorLang())}
            </option>
          ))}
        </select>
        <button disabled={busy || !deviceName.trim()}
          onClick={() => run(async () => {
            await api.registerDevice(uid, {
              name: deviceName.trim(), kind: deviceKind }, token);
            setDeviceName("");
          }, "Device registered.")}>
          {tr("ch.dev.register", visitorLang())}
        </button>
        {/* The radio does the typing: where the runtime carries Web
            Bluetooth (Chrome, Edge, the desktop shell), the picker returns
            the device's own advertised name — a speaker, a wearable,
            anything nearby — and it registers under that name with its
            transport recorded. Browsers without the API get the truth and
            the manual row, not a dead button. */}
        <button disabled={busy}
          onClick={() => run(async () => {
            const bt = (navigator as unknown as {
              bluetooth?: { requestDevice: (o: object) =>
                Promise<{ name?: string }> } }).bluetooth;
            if (!bt) {
              throw new Error(
                "This browser cannot scan for Bluetooth — use Chrome, "
                + "Edge or the desktop app, or type the device's name "
                + "and register it with the button to the left.");
            }
            const picked = await bt.requestDevice(
              { acceptAllDevices: true });
            const name = (picked.name || "").trim() || "bluetooth device";
            // The chooser found it; the GATT connect is the handshake
            // itself — the OS pairs (and bonds, where the device asks)
            // on this call. A device that refuses still registers, with
            // paired recorded as the fact it is.
            let paired = false;
            try {
              const gatt = (picked as unknown as {
                gatt?: { connect: () => Promise<unknown> } }).gatt;
              if (gatt) { await gatt.connect(); paired = true; }
            } catch { paired = false; }
            await api.registerDevice(uid, {
              name, kind: deviceKind, transport: "bluetooth",
              paired }, token);
          }, "Bluetooth device paired and registered.")}>
          {tr("dev.bluetooth", visitorLang())}
        </button>
      </div>

      <h3>{tr("ch.mic", visitorLang())}</h3>
      {types && <p className="muted">{types.rule}</p>}
      {mic?.listening
        ? (
          <div className="card">
            <div className="row">
              <strong>{mic.device}</strong>
              <span className="muted">{mic.mic_type}</span>
              {mic.reason && <span className="pill">{mic.reason}</span>}
            </div>
            {mic.hears && <p>{mic.hears}</p>}
            {mic.because && <p className="muted">{mic.because}</p>}
            <div className="row">
              {/* Lending channel 2 is not the same act as attaching it, and
                  the backend has always kept them apart: a handover records
                  *why* and *to where*, and whether anybody else was in the
                  room. That last flag is the one that matters — a second ear
                  in a room with other people in it is a different thing from
                  one in an empty room, and the server wants to be told which
                  it is rather than to guess. The console has never asked. */}
              <button disabled={busy}
                onClick={() => run(() => api.handOverMic(uid, {
                  reason: "clinician on the line",
                  route: "care_team",
                  others_present: confirm(
                    "Is anybody else in the room? OK for yes."),
                  primary_device: mic.device ?? undefined,
                }, token), "Handed over.")}>
                {tr("ch.mic.handover", visitorLang())}
              </button>
            </div>
            {mic.capped && (
              <p className="muted">
                {tr("ch.mic.capped", visitorLang()).replace(
                  "{gain}", String(mic.gain))}
              </p>
            )}
            <div className="row">
              {(gains?.levels ?? []).map((lvl) => (
                <button key={lvl.gain}
                  disabled={busy || mic.gain === lvl.gain}
                  title={lvl.describes}
                  onClick={() => run(() => api.setMicGain(uid, lvl.gain, token),
                    `Gain: ${lvl.describes}`)}>
                  {lvl.gain.replace("_", " ")}
                  {lvl.reaches_others ? tr("ch.reaches", visitorLang()) : ""}
                </button>
              ))}
            </div>
            <div className="row">
              <button disabled={busy}
                onClick={() => run(() => api.releaseMic(uid, token),
                  "Released. JIM is not listening.")}>
                {tr("ch.mic.release", visitorLang())}
              </button>
              <button disabled={busy}
                onClick={() => {
                  if (confirm("Detach the microphone entirely?"))
                    run(() => api.detachMic(uid, token), "Detached.");
                }}>
                {tr("ch.mic.detach", visitorLang())}
              </button>
            </div>
          </div>
        )
        : (
          <div className="card">
            <p className="muted">{tr("ch.mic.none", visitorLang())}</p>
            <div className="row">
              <select value={micDevice}
                onChange={(e) => setMicDevice(e.target.value)}>
                <option value="">{tr("ch.mic.which", visitorLang())}</option>
                {devices.map((d) => (
                  <option key={d.id} value={d.name}>{d.name}</option>
                ))}
              </select>
              <select value={micType} onChange={(e) => setMicType(e.target.value)}>
                <option value="">{tr("ch.mic.kind", visitorLang())}</option>
                {(types?.personal ?? []).map((mt) => (
                  <option key={mt} value={mt}>{mt.replace("_", " ")}</option>
                ))}
              </select>
              <button disabled={busy || !micDevice || !micType}
                onClick={() => run(() => api.attachMic(uid,
                  { device_name: micDevice, mic_type: micType }, token),
                  "Attached.")}>
                {tr("ch.mic.attach", visitorLang())}
              </button>
            </div>
            {/* Only the personal list is offered. The ambient microphones are
                shown as refused, with the server's own reason, because a
                missing option raises the question the rule already answers. */}
            {types && types.ambient.length > 0 && (
              <p className="muted">
                {tr("ch.mic.refused", visitorLang())
                  .replace("{list}", types.ambient.join(", "))
                  .replace("{rule}", types.rule)}
              </p>
            )}
          </div>
        )}
      {gains && <p className="muted">{gains.rule}</p>}

      {history.length > 0 && (
        <>
          <h3>{tr("ch.hist", visitorLang())}</h3>
          {history.map((h) => (
            <div key={h.id} className="card muted">
              <div className="row">
                <span>{h.device} · {h.mic_type}</span>
                <span>{h.gain}</span>
                {h.reason && <span>{h.reason}</span>}
                {h.live && <span className="pill">{tr("ch.hist.live", visitorLang())}</span>}
              </div>
              <span>{h.started_at.slice(0, 16).replace("T", " ")}
                {h.ended_at ? ` → ${h.ended_at.slice(11, 16)}` : ""}
                {h.ended_because ? ` (${h.ended_because})` : ""}</span>
            </div>
          ))}
        </>
      )}

      <h3>{tr("ch.cam", visitorLang())}</h3>
      {vocab && (
        <p className="muted">
          {vocab.agent_sees?.join(", ")}{vocab.vault_required
            ? tr("ch.sealed.plan", visitorLang())
            : ""}
        </p>
      )}
      {captures.map((c) => (
        <div key={c.id} className="card">
          <div className="row">
            <label>
              <input type="checkbox"
                checked={chosen.includes(c.id)}
                onChange={(e) => setChosen(e.target.checked
                  ? [...chosen, c.id]
                  : chosen.filter((x) => x !== c.id))} />
              {" "}{vocab?.sites?.[c.site] ?? c.site}
            </label>
            <span className="muted">{c.kind}</span>
            {c.condition && <span className="muted">{c.condition}</span>}
            {intimate.has(c.site) && <span className="pill">{tr("ch.cam.intimate", visitorLang())}</span>}
          </div>
          {c.note && <p className="muted">{c.note}</p>}
          {shown[c.id] && (
            <img src={shown[c.id]} alt={vocab?.sites?.[c.site] ?? c.site}
                 style={{ maxWidth: "100%", borderRadius: 8 }} />
          )}
          <div className="row">
            {/* The image comes back on its own route, not with the listing.
                That is the right shape — a list of body photographs should
                not stream every one of them to draw a row — but it left the
                console showing a person a list of records of their own body
                with no way to see what was in them. Fetching on request is
                the door; it is deliberately one press per capture. */}
            <button disabled={busy || !!shown[c.id]}
              onClick={() => run(async () => {
                const img = await api.captureImage(uid, c.id, token);
                setShown((m) => ({ ...m, [c.id]: img.content }));
              }, "")}>
              {shown[c.id] ? tr("ch.shown", visitorLang())
                : tr("ch.look", visitorLang())}
            </button>
            <button disabled={busy}
              onClick={() => {
                if (confirm("Withdraw this? The vault record is destroyed. A "
                  + "clinician who was shown it will see it was withdrawn."))
                  run(() => api.deleteCapture(uid, c.id, token), "Withdrawn.");
              }}>
              {tr("ch.cam.withdraw", visitorLang())}
            </button>
          </div>
        </div>
      ))}
      {captures.length > 0 && (
        <div className="row">
          <button disabled={busy || chosen.length === 0}
            onClick={() => run(async () => {
              const out = await api.attachCaptures(uid, chosen, token);
              setChosen([]);
              const named = (out.explicit ?? []).length;
              setSaid(named > 0
                ? `Attached. ${named} intimate capture(s) had to be named one at a time — they are never swept in by a match.`
                : "Attached to the referral.");
            })}>
            {tr("ch.cam.attach", visitorLang()).replace(
              "{n}", chosen.length > 0 ? `${chosen.length} ` : "")}
          </button>
        </div>
      )}

      <div className="card">
        <div className="row">
          <select value={site} onChange={(e) => { setSite(e.target.value); setConsent(false); }}>
            <option value="">{tr("ch.cam.where", visitorLang())}</option>
            {Object.entries(vocab?.sites ?? {}).map(([k, label]) => (
              <option key={k} value={k}>{label}{intimate.has(k) ? tr("ch.intimate", visitorLang()) : ""}</option>
            ))}
          </select>
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            {Object.entries(vocab?.kinds ?? {}).map(([k, label]) => (
              <option key={k} value={k} title={label}>{k}</option>
            ))}
          </select>
          <input value={condition} placeholder={tr("ch.cam.for", visitorLang())}
            onChange={(e) => setCondition(e.target.value)} />
        </div>
        <input value={note} placeholder={tr("ch.cam.note", visitorLang())}
          onChange={(e) => setNote(e.target.value)} />
        {siteIsIntimate && (
          <label className="row">
            <input type="checkbox" checked={consent}
              onChange={(e) => setConsent(e.target.checked)} />
            {" "}{tr("ch.cam.consent", visitorLang())}
          </label>
        )}
        <input type="file" accept="image/*,video/*,audio/*"
          onChange={async (e) => {
            const file = e.target.files?.[0];
            if (!file || !site) return;
            if (vocab && file.size > vocab.max_bytes) {
              setError(`That file is ${(file.size / 1048576).toFixed(1)} MB; the limit is ${(vocab.max_bytes / 1048576).toFixed(0)} MB.`);
              return;
            }
            const content = await new Promise<string>((resolve, reject) => {
              const r = new FileReader();
              r.onload = () => resolve(String(r.result));
              r.onerror = () => reject(new Error("could not read that file"));
              r.readAsDataURL(file);
            });
            await run(() => api.takeCapture(uid, {
              kind, site, content,
              // Chosen from the library rather than taken now: the server
              // records the difference, because an imported picture may be
              // older than it looks and the app cannot verify who is in it.
              provenance: "imported",
              note: note.trim() || undefined,
              condition: condition.trim() || undefined,
              intimate_consent: siteIsIntimate ? consent : undefined,
            }, token), "Sealed.");
            setNote(""); setConsent(false);
            e.target.value = "";
          }} />
        {!site && <p className="muted">{tr("ch.cam.site", visitorLang())}</p>}
        {siteIsIntimate && !consent
          && <p className="muted">{tr("ch.cam.tick", visitorLang())}</p>}
      </div>
    </section>
  );
}
