import { useCallback, useEffect, useRef, useState } from "react";
import {
  api, getBase, type AlarmRow, type BaselineMetric, type CheckinResult,
  type CrashWatchStatus, type EscalationPolicy, type Guidance,
  type MedicalIdCode, type UnderwayRow, type WatchChannel,
} from "../api";
import { t as tr, type Lang } from "../l10n";
import { listen, primeVoice, say, type Listener } from "../speech";
import { useSession } from "../store";

/**
 * The watch, working — every face in `docs/watch/` as a real screen.
 *
 * Those thirty-six faces shipped as drawings: a design set the README
 * showed and nothing served. The owner's instruction closed the gap from
 * the honest side — *make sure they're implemented and work from each
 * screen* — so this surface is the faces at wrist size, each one standing
 * on the same doors the phone screens use. Nothing here invents a second
 * data path: a check-in logged on face 09 is the same `POST /checkin` the
 * Check-in tab sends, and the agent lights on face 36 read the same task
 * window `Underway` renders.
 *
 * A browser is the wrist this ships on first: any watch, phone or frame
 * that can open `jim-mini.com/#watch` gets the surface, which is the same
 * position `jim/watch.py` takes about the drip channel — the feature was
 * never Apple-shaped, it is a URL. `#watch/<slug>` opens one face
 * directly, and the README's gallery links each drawing to its living
 * counterpart through exactly that door.
 *
 * The CPR face carries its own algorithm, because it must work with the
 * network gone: a 110-beats-per-minute metronome driven by the audio
 * clock (a `setInterval` drifts; an oscillator scheduled on
 * `AudioContext.currentTime` does not), a 30:2 compression counter, and
 * vibration on the devices that have it. The alarm ladder rides beside
 * it and never pretends: JIM cannot place a call at any tier, and the
 * face says so in the same words the alarm queue does.
 */

/** The canonical order — the numbers and slugs of `docs/watch/`. */
export const FACES = [
  "home", "talk", "voice", "health", "heart", "rings", "briefing", "streak",
  "check-in", "insight", "monitoring", "foresight", "emergency", "cpr",
  "medical-id", "sensitivity", "ambient", "companion", "notifications",
  "devices", "guardian", "settings", "breathe", "feedback", "journal",
  "coach", "baseline", "sources", "privacy", "handoff", "offline",
  "conditions", "style", "history", "family", "agents",
] as const;
export type FaceSlug = (typeof FACES)[number];

/** `#watch/05-heart`, `#watch/heart` and `#watch/5` all land on Heart —
 *  the README links carry the numbered slug, a person types the word. */
export function faceFromHash(hash: string): number {
  const m = /^#watch(?:\/(.+))?$/.exec(hash);
  if (!m || !m[1]) return 0;
  const raw = m[1].toLowerCase();
  const numbered = /^(\d+)/.exec(raw);
  if (numbered) {
    const n = parseInt(numbered[1], 10);
    if (n >= 1 && n <= FACES.length) return n - 1;
  }
  const at = FACES.indexOf(raw.replace(/^\d+-/, "") as FaceSlug);
  return at >= 0 ? at : 0;
}

type FaceProps = { uid: string | null; token: string | null; lang: Lang;
                   go: (slug: FaceSlug) => void };

/** Shared loader: one fetch, one error line, no face crashing the shell. */
function useDoor<T>(load: (() => Promise<T>) | null, again = 0) {
  const [data, setData] = useState<T | null>(null);
  const [fault, setFault] = useState<string | null>(null);
  useEffect(() => {
    if (!load) return;
    let live = true;
    load().then((d) => { if (live) { setData(d); setFault(null); } })
      .catch((e) => { if (live) setFault(e instanceof Error ? e.message : String(e)); });
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [again, load === null]);
  return { data, fault };
}

function SignIn({ lang }: { lang: Lang }) {
  return <p className="w-note">{tr("w.signin", lang)}</p>;
}

function Fault({ fault }: { fault: string | null }) {
  return fault ? <p className="w-note w-fault">{fault}</p> : null;
}

// ---- 01 · Home -------------------------------------------------------------

function FaceHome({ uid, lang, go }: FaceProps) {
  const { session } = useSession();
  const hour = new Date().getHours();
  // `tr` inside each branch, not around a variable: the dead-key guard
  // reads literal lookups, and a key held in a ternary reads as unused.
  const greet = hour < 12 ? tr("w.home.morning", lang)
    : hour < 18 ? tr("w.home.afternoon", lang) : tr("w.home.evening", lang);
  return (
    <div className="w-center">
      <span className="w-orb" aria-hidden="true" />
      <p className="w-note">{greet}</p>
      <h3 className="w-big-name">{session.displayName || tr("w.home.you", lang)}</h3>
      <button className="w-btn primary" onClick={() => go("talk")}>
        {tr("w.home.talk", lang)}
      </button>
      {!uid && <SignIn lang={lang} />}
    </div>
  );
}

// ---- 02 · Talk and 03 · Voice ---------------------------------------------

function FaceTalk({ uid, token, lang }: FaceProps) {
  const [said, setSaid] = useState("");
  const [reply, setReply] = useState<Guidance | null>(null);
  const [busy, setBusy] = useState(false);
  const [fault, setFault] = useState<string | null>(null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const ask = async () => {
    if (!said.trim()) return;
    setBusy(true); setFault(null);
    try {
      setReply(await api.coach(uid, { area: "general", message: said.trim() }, token));
      setSaid("");
    } catch (e) { setFault(e instanceof Error ? e.message : String(e)); }
    finally { setBusy(false); }
  };
  return (
    <div className="w-center">
      <span className="w-orb" aria-hidden="true" />
      <p className="w-note">{tr("w.talk.how", lang)}</p>
      <input className="w-input" value={said}
             placeholder={tr("w.talk.ph", lang)}
             onChange={(e) => setSaid(e.target.value)}
             onKeyDown={(e) => { if (e.key === "Enter") ask(); }} />
      <button className="w-btn primary" disabled={busy || !said.trim()}
              onClick={ask}>{tr("w.talk.send", lang)}</button>
      {reply && <p className="w-reply">{reply.content}</p>}
      <Fault fault={fault} />
    </div>
  );
}

function FaceVoice({ uid, token, lang }: FaceProps) {
  const [hearing, setHearing] = useState(false);
  const [heard, setHeard] = useState("");
  const [reply, setReply] = useState("");
  const [fault, setFault] = useState<string | null>(null);
  const ear = useRef<Listener | null>(null);
  useEffect(() => () => { ear.current?.stop(); }, []);
  if (!uid || !token) return <SignIn lang={lang} />;
  const start = async () => {
    setHearing(true); setFault(null); setHeard(""); setReply("");
    ear.current = await listen(async (text) => {
      ear.current?.stop(); ear.current = null; setHearing(false);
      setHeard(text);
      try {
        const g = await api.coach(uid, { area: "general", message: text }, token);
        setReply(g.content);
        void say(g.content);
      } catch (e) { setFault(e instanceof Error ? e.message : String(e)); }
    }, (message) => { setHearing(false); setFault(message); });
  };
  const stop = () => { ear.current?.stop(); ear.current = null; setHearing(false); };
  return (
    <div className="w-center">
      <span className={"w-orb" + (hearing ? " live" : "")} aria-hidden="true" />
      <p className="w-note">{hearing ? tr("w.voice.listening", lang)
                                     : tr("w.voice.tap", lang)}</p>
      <button className="w-btn primary"
              onClick={() => (hearing ? stop() : start())}>
        {hearing ? tr("w.voice.stop", lang) : tr("w.voice.speak", lang)}
      </button>
      {heard && <p className="w-note">“{heard}”</p>}
      {reply && <p className="w-reply">{reply}</p>}
      <Fault fault={fault} />
    </div>
  );
}

// ---- 04-05-06 · Health, Heart, Rings --------------------------------------

function FaceHealth({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.getBands(uid!, token!), [uid, token]);
  const { data, fault } = useDoor(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const bands = (data as { bands?: { metric: string; baseline: number | null;
    samples: number }[] } | null)?.bands || [];
  return (
    <div className="w-face-body">
      <div className="w-tiles">
        {bands.slice(0, 4).map((b) => (
          <div className="w-tile" key={b.metric}>
            <b>{b.baseline != null ? Math.round(b.baseline) : "—"}</b>
            <span>{b.metric.replace(/_/g, " ")}</span>
          </div>
        ))}
      </div>
      {bands.length === 0 && <p className="w-note">{tr("w.health.none", lang)}</p>}
      <Fault fault={fault} />
    </div>
  );
}

function FaceHeart({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.getBands(uid!, token!), [uid, token]);
  const { data, fault } = useDoor(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const hr = (data as { bands?: { metric: string; baseline: number | null;
    samples: number; provisional?: boolean }[] } | null)?.bands
    ?.find((b) => b.metric === "heart_rate");
  return (
    <div className="w-center">
      <span className="w-pulse" aria-hidden="true">♥</span>
      <h3 className="w-big">{hr?.baseline != null ? Math.round(hr.baseline) : "—"}</h3>
      <p className="w-note">
        {tr("w.heart.resting", lang)}
        {hr?.provisional ? ` · ${tr("w.provisional", lang)}` : ""}
      </p>
      <Fault fault={fault} />
    </div>
  );
}

function FaceRings({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.goals(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const goals = (data as { id: string; title?: string; name?: string;
    progress?: number }[] | null) || [];
  return (
    <div className="w-face-body">
      {goals.slice(0, 3).map((g, i) => (
        <div className="w-meter-row" key={g.id}>
          <span className={"w-dot c" + i} aria-hidden="true" />
          <span className="w-meter-label">{g.title || g.name || g.id}</span>
          <span className="w-meter-val">
            {g.progress != null ? Math.round(g.progress * 100) + "%" : "·"}
          </span>
        </div>
      ))}
      {goals.length === 0 && <p className="w-note">{tr("w.rings.none", lang)}</p>}
      <Fault fault={fault} />
    </div>
  );
}

// ---- 07 · Briefing and 08 · Streak ----------------------------------------

function FaceBriefing({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.insights(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const rows = (data as { insight?: string; content?: string;
    note?: string }[] | null) || [];
  return (
    <div className="w-face-body">
      {rows.slice(0, 3).map((r, i) => (
        <p className="w-line" key={i}>{r.insight || r.content || r.note || ""}</p>
      ))}
      {rows.length === 0 && <p className="w-note">{tr("w.brief.none", lang)}</p>}
      <Fault fault={fault} />
    </div>
  );
}

function FaceStreak({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.habits(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const habits = (data as { id: string; name: string;
    streak?: number }[] | null) || [];
  const best = habits.reduce((top, h) => Math.max(top, h.streak || 0), 0);
  return (
    <div className="w-center">
      <h3 className="w-big">{best}</h3>
      <p className="w-note">{tr("w.streak.days", lang)}</p>
      {habits[0] && <p className="w-note">{habits[0].name}</p>}
      <Fault fault={fault} />
    </div>
  );
}

// ---- 09 · Check-in and 10 · Insight ---------------------------------------

function FaceCheckin({ uid, token, lang }: FaceProps) {
  const [mood, setMood] = useState(3);
  const [energy, setEnergy] = useState(3);
  const [done, setDone] = useState<CheckinResult | null>(null);
  const [fault, setFault] = useState<string | null>(null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const log = async () => {
    setFault(null);
    try { setDone(await api.checkin(uid, { mood, energy }, token)); }
    catch (e) { setFault(e instanceof Error ? e.message : String(e)); }
  };
  const scale = (value: number, set: (n: number) => void, label: string) => (
    <div className="w-meter-row">
      <span className="w-meter-label">{label}</span>
      {[1, 2, 3, 4, 5].map((n) => (
        <button key={n} className={"w-scale" + (n === value ? " on" : "")}
                aria-label={`${label} ${n}`}
                onClick={() => set(n)}>{n}</button>
      ))}
    </div>
  );
  return (
    <div className="w-face-body">
      {scale(mood, setMood, tr("w.ci.mood", lang))}
      {scale(energy, setEnergy, tr("w.ci.energy", lang))}
      <button className="w-btn primary" onClick={log}>
        {tr("w.ci.log", lang)}
      </button>
      {done && <p className="w-reply">{tr("w.ci.done", lang)}</p>}
      <Fault fault={fault} />
    </div>
  );
}

function FaceInsight({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.insights(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const rows = (data as { insight?: string; content?: string }[] | null) || [];
  const latest = rows[0];
  return (
    <div className="w-center">
      <span className="w-moon" aria-hidden="true">☾</span>
      <p className="w-reply">
        {latest ? (latest.insight || latest.content || "")
                : tr("w.insight.none", lang)}
      </p>
      <Fault fault={fault} />
    </div>
  );
}

// ---- 11-12-13-14 · Monitoring, Foresight, Emergency, CPR -------------------

function FaceMonitoring({ uid, token, lang }: FaceProps) {
  const [again, setAgain] = useState(0);
  const loader = useCallback(() => api.alarms(uid!, token!, true), [uid, token]);
  const { data, fault } = useDoor<AlarmRow[]>(uid && token ? loader : null, again);
  const [okay, setOkay] = useState<CrashWatchStatus | null>(null);
  const [okFault, setOkFault] = useState<string | null>(null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const open = data || [];
  return (
    <div className="w-face-body">
      {open.length === 0 && !okay && (
        <p className="w-note">{tr("w.mon.quiet", lang)}</p>
      )}
      {open.slice(0, 2).map((a) => (
        <p className="w-line w-alert" key={a.id}>
          {a.tier}{a.messages?.[0] ? ` — ${a.messages[0]}` : ""}
        </p>
      ))}
      <button className="w-btn primary" onClick={async () => {
        setOkFault(null);
        try { setOkay(await api.imOkay(uid, token)); setAgain((n) => n + 1); }
        catch (e) { setOkFault(e instanceof Error ? e.message : String(e)); }
      }}>{tr("w.mon.ok", lang)}</button>
      {okay && <p className="w-reply">{tr("w.mon.told", lang)}</p>}
      <Fault fault={fault || okFault} />
    </div>
  );
}

function FaceForesight({ uid, token, lang, go }: FaceProps) {
  const loader = useCallback(() => api.getBands(uid!, token!), [uid, token]);
  const { data, fault } = useDoor(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const bands = (data as { bands?: { metric: string; baseline: number | null;
    provisional?: boolean }[] } | null)?.bands || [];
  const thin = bands.filter((b) => b.provisional).length;
  return (
    <div className="w-center">
      <p className="w-note">
        {thin > 0
          ? tr("w.fore.learning", lang)
          : tr("w.fore.steady", lang)}
      </p>
      <button className="w-btn primary" onClick={() => go("breathe")}>
        {tr("w.fore.breathe", lang)}
      </button>
      <Fault fault={fault} />
    </div>
  );
}

function FaceEmergency({ uid, token, lang, go }: FaceProps) {
  const loader = useCallback(() => api.escalationPolicy(uid!, token!),
                             [uid, token]);
  const { data, fault } = useDoor<EscalationPolicy>(
    uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  return (
    <div className="w-center">
      {/* The one honest button: a telephone link the DEVICE places. JIM
          cannot place a call at any tier — the alarm queue has said so
          since it shipped — so the control hands the number to the thing
          that can dial it, and says which thing did. */}
      <a className="w-btn w-danger" href="tel:911">
        {tr("w.em.call", lang)}
      </a>
      <p className="w-note">{tr("w.em.device", lang)}</p>
      {data?.ladder && (
        <p className="w-note">{data.ladder.slice(0, 3).join(" → ")}</p>
      )}
      <button className="w-btn" onClick={() => go("cpr")}>
        {tr("w.em.cpr", lang)}
      </button>
      <Fault fault={fault} />
    </div>
  );
}

/** The CPR metronome. 110 compressions a minute, scheduled on the audio
 *  clock: `setInterval` drifts under load and a drifting beat is a wrong
 *  compression rate, which on this face is not a cosmetic defect. */
function FaceCpr({ lang }: FaceProps) {
  const [running, setRunning] = useState(false);
  const [beat, setBeat] = useState(0);
  const audio = useRef<AudioContext | null>(null);
  const timer = useRef<number | null>(null);
  const nextAt = useRef(0);
  const count = useRef(0);

  const BPM = 110;
  const PERIOD = 60 / BPM;

  const stop = useCallback(() => {
    if (timer.current != null) window.clearInterval(timer.current);
    timer.current = null;
    audio.current?.close().catch(() => undefined);
    audio.current = null;
    setRunning(false);
  }, []);
  useEffect(() => stop, [stop]);

  const start = () => {
    const Ctx = window.AudioContext
      || (window as unknown as { webkitAudioContext?: typeof AudioContext })
        .webkitAudioContext;
    const ctx = Ctx ? new Ctx() : null;
    audio.current = ctx;
    count.current = 0;
    nextAt.current = ctx ? ctx.currentTime + 0.1 : performance.now() / 1000;
    setRunning(true);
    // The scheduler runs often and *schedules ahead* on the audio clock;
    // the interval's own jitter never reaches the beat.
    timer.current = window.setInterval(() => {
      const now = ctx ? ctx.currentTime : performance.now() / 1000;
      while (nextAt.current < now + 0.15) {
        if (ctx) {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          // Thirty compressions, then a lower pair for the two breaths —
          // the 30:2 rhythm said in sound as well as on the dial.
          const inBreaths = count.current % 32 >= 30;
          osc.frequency.value = inBreaths ? 440 : 880;
          gain.gain.setValueAtTime(0.4, nextAt.current);
          gain.gain.exponentialRampToValueAtTime(0.001, nextAt.current + 0.08);
          osc.connect(gain).connect(ctx.destination);
          osc.start(nextAt.current);
          osc.stop(nextAt.current + 0.09);
        }
        if (navigator.vibrate) navigator.vibrate(30);
        count.current += 1;
        setBeat(count.current);
        nextAt.current += PERIOD;
      }
    }, 60);
  };

  const inBreaths = beat % 32 >= 30;
  return (
    <div className="w-center">
      <h3 className={"w-big" + (running ? " w-pulse-text" : "")}>
        {running ? (inBreaths ? tr("w.cpr.breaths", lang)
                              : String((beat % 32) + (beat % 32 >= 30 ? 0 : 1)))
                 : tr("w.cpr.push", lang)}
      </h3>
      <p className="w-note">{tr("w.cpr.rate", lang)}</p>
      <button className={"w-btn " + (running ? "" : "w-danger")}
              onClick={() => (running ? stop() : start())}>
        {running ? tr("w.cpr.stop", lang) : tr("w.cpr.start", lang)}
      </button>
      <p className="w-note">{tr("w.cpr.how", lang)}</p>
    </div>
  );
}

// ---- 15 · Medical ID and 16 · Sensitivity ---------------------------------

function FaceMedicalId({ uid, token, lang }: FaceProps) {
  const [code, setCode] = useState<MedicalIdCode | null>(null);
  const [fault, setFault] = useState<string | null>(null);
  if (!uid || !token) return <SignIn lang={lang} />;
  return (
    <div className="w-center">
      {code ? (
        <img className="w-qr" src={getBase() + code.qr_svg_url}
             alt={tr("w.mid.title", lang)} />
      ) : (
        <button className="w-btn primary" onClick={async () => {
          setFault(null);
          try { setCode(await api.makeMedicalIdQr(uid, token)); }
          catch (e) { setFault(e instanceof Error ? e.message : String(e)); }
        }}>{tr("w.mid.show", lang)}</button>
      )}
      <p className="w-note">{tr("w.mid.scan", lang)}</p>
      <Fault fault={fault} />
    </div>
  );
}

function FaceSensitivity({ uid, token, lang }: FaceProps) {
  const [level, setLevel] = useState<string | null>(null);
  const [fault, setFault] = useState<string | null>(null);
  const loader = useCallback(() => api.getBands(uid!, token!), [uid, token]);
  const { data } = useDoor(uid && token ? loader : null);
  useEffect(() => {
    const s = (data as { sensitivity?: string } | null)?.sensitivity;
    if (s) setLevel(s);
  }, [data]);
  if (!uid || !token) return <SignIn lang={lang} />;
  return (
    <div className="w-face-body">
      {(["cautious", "balanced", "direct"] as const).map((s) => (
        <button key={s} className={"w-btn" + (level === s ? " primary" : "")}
                onClick={async () => {
                  setFault(null);
                  try {
                    await api.setSensitivity(uid, { level: s }, token);
                    setLevel(s);
                  } catch (e) {
                    setFault(e instanceof Error ? e.message : String(e));
                  }
                }}>
          {tr(`w.sens.${s}`, lang)}
        </button>
      ))}
      <Fault fault={fault} />
    </div>
  );
}

// ---- 17 · Ambient and 18 · Companion --------------------------------------

function FaceAmbient({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.followup(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  const [answered, setAnswered] = useState<string | null>(null);
  const [sendFault, setSendFault] = useState<string | null>(null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const pending = (data as { pending?: boolean; question?: string } | null);
  const answer = async (helped: boolean) => {
    setSendFault(null);
    try {
      await api.answerFollowup(uid, { helped }, token);
      setAnswered(helped ? tr("w.amb.glad", lang) : tr("w.amb.more", lang));
    } catch (e) { setSendFault(e instanceof Error ? e.message : String(e)); }
  };
  return (
    <div className="w-center">
      <p className="w-note">
        {pending?.question || tr("w.amb.hand", lang)}
      </p>
      {!answered ? (
        <div className="w-row">
          <button className="w-btn primary" onClick={() => answer(true)}>
            {tr("w.yes", lang)}
          </button>
          <button className="w-btn" onClick={() => answer(false)}>
            {tr("w.amb.later", lang)}
          </button>
        </div>
      ) : <p className="w-reply">{answered}</p>}
      <Fault fault={fault || sendFault} />
    </div>
  );
}

function FaceCompanion({ uid, token, lang }: FaceProps) {
  const [reply, setReply] = useState("");
  const [note, setNote] = useState("");
  const [fault, setFault] = useState<string | null>(null);
  if (!uid || !token) return <SignIn lang={lang} />;
  return (
    <div className="w-center">
      <p className="w-note">{tr("w.comp.how", lang)}</p>
      <input className="w-input" value={note}
             placeholder={tr("w.comp.ph", lang)}
             onChange={(e) => setNote(e.target.value)} />
      <button className="w-btn primary" disabled={!note.trim()}
              onClick={async () => {
                setFault(null);
                try {
                  const r = await api.askCompanion(
                    uid, { message: note.trim() }, token);
                  setReply(String((r as { content?: string }).content
                    || (r as { says?: string }).says || tr("w.comp.heard", lang)));
                  setNote("");
                } catch (e) {
                  setFault(e instanceof Error ? e.message : String(e));
                }
              }}>{tr("w.comp.reply", lang)}</button>
      {reply && <p className="w-reply">{reply}</p>}
      <Fault fault={fault} />
    </div>
  );
}

// ---- 19 · Notifications and 20 · Devices ----------------------------------

function FaceNotifications({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.events(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const rows = (data as { type: string; created_at?: string;
    condition?: string | null }[] | null) || [];
  return (
    <div className="w-face-body">
      {rows.slice(0, 4).map((e, i) => (
        <p className="w-line" key={i}>
          {e.type.replace(/_/g, " ")}
          {e.condition ? ` · ${e.condition}` : ""}
        </p>
      ))}
      {rows.length === 0 && <p className="w-note">{tr("w.notif.none", lang)}</p>}
      <Fault fault={fault} />
    </div>
  );
}

function FaceDevices({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.getWatchChannel(uid!, token!),
                             [uid, token]);
  const { data, fault } = useDoor<WatchChannel>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  return (
    <div className="w-face-body">
      {data?.devices.slice(0, 4).map((d) => (
        <p className="w-line" key={d.key}>
          {d.name}{d.key === data.device ? " ✓" : ""}
        </p>
      ))}
      <p className="w-note">
        {data
          ? (data.phone_reachable ? tr("w.dev.dripping", lang)
                                  : tr("w.dev.waiting", lang))
          : ""}
      </p>
      <Fault fault={fault} />
    </div>
  );
}

// ---- 21 · Guardian and 22 · Settings --------------------------------------

function FaceGuardian({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.crashWatch(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<CrashWatchStatus>(
    uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const armed = (data as { armed?: boolean } | null)?.armed;
  return (
    <div className="w-center">
      <span className={"w-shield" + (armed ? " on" : "")} aria-hidden="true" />
      <h3 className="w-big">{armed ? tr("w.on", lang) : tr("w.off", lang)}</h3>
      <p className="w-note">{tr("w.guard.rules", lang)}</p>
      <Fault fault={fault} />
    </div>
  );
}

function FaceSettings({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.sources(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const rows = (data as { source: string;
    consented: boolean }[] | null) || [];
  const on = rows.filter((r) => r.consented).length;
  return (
    <div className="w-face-body">
      <p className="w-line">{tr("w.set.sources", lang)}: {on}/{rows.length}</p>
      <p className="w-note">{tr("w.set.where", lang)}</p>
      <Fault fault={fault} />
    </div>
  );
}

// ---- 23 · Breathe and 24 · Feedback ---------------------------------------

function FaceBreathe({ uid, token, lang }: FaceProps) {
  const [phase, setPhase] = useState<"idle" | "in" | "hold" | "out">("idle");
  const timer = useRef<number | null>(null);
  useEffect(() => () => {
    if (timer.current != null) window.clearTimeout(timer.current);
  }, []);
  const step = (next: "in" | "hold" | "out", after: number) => {
    setPhase(next);
    timer.current = window.setTimeout(() => {
      if (next === "in") step("hold", 4000);
      else if (next === "hold") step("out", 6000);
      else step("in", 4000);
    }, after);
  };
  const begin = () => {
    // 4-4-6 box-ish breathing, and the session is told to the backend so
    // the calm history is a record rather than a guess.
    if (uid && token) void api.startCalm(uid, "breathing", token).catch(() => undefined);
    step("in", 4000);
  };
  const stop = () => {
    if (timer.current != null) window.clearTimeout(timer.current);
    setPhase("idle");
  };
  return (
    <div className="w-center">
      <span className={"w-orb w-breathe-" + phase} aria-hidden="true" />
      <p className="w-note">
        {phase === "idle" ? tr("w.br.ready", lang)
          : phase === "in" ? tr("w.br.in", lang)
          : phase === "hold" ? tr("w.br.hold", lang)
          : tr("w.br.out", lang)}
      </p>
      <button className="w-btn primary"
              onClick={() => (phase === "idle" ? begin() : stop())}>
        {phase === "idle" ? tr("w.br.begin", lang) : tr("w.br.done", lang)}
      </button>
    </div>
  );
}

function FaceFeedback({ uid, token, lang }: FaceProps) {
  const [sent, setSent] = useState(false);
  const [fault, setFault] = useState<string | null>(null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const rate = async (rating: "up" | "down") => {
    setFault(null);
    try { await api.sendFeedback(uid, { rating }, token); setSent(true); }
    catch (e) { setFault(e instanceof Error ? e.message : String(e)); }
  };
  return (
    <div className="w-center">
      <p className="w-note">{tr("w.fb.helpful", lang)}</p>
      {!sent ? (
        <div className="w-row">
          <button className="w-btn primary" onClick={() => rate("up")}>
            {tr("w.yes", lang)}
          </button>
          <button className="w-btn" onClick={() => rate("down")}>
            {tr("w.no", lang)}
          </button>
        </div>
      ) : <p className="w-reply">{tr("w.fb.trains", lang)}</p>}
      <Fault fault={fault} />
    </div>
  );
}

// ---- 25 · Journal and 26 · Coach ------------------------------------------

function FaceJournal({ uid, token, lang }: FaceProps) {
  const [text, setText] = useState("");
  const [hearing, setHearing] = useState(false);
  const [kept, setKept] = useState(false);
  const [fault, setFault] = useState<string | null>(null);
  const ear = useRef<Listener | null>(null);
  useEffect(() => () => { ear.current?.stop(); }, []);
  if (!uid || !token) return <SignIn lang={lang} />;
  const dictate = async () => {
    setHearing(true); setFault(null);
    ear.current = await listen((words) => {
      setText((was) => (was ? was + " " : "") + words);
      setHearing(false);
    }, (message) => { setHearing(false); setFault(message); });
  };
  return (
    <div className="w-face-body">
      <input className="w-input" value={text}
             placeholder={tr("w.jr.ph", lang)}
             onChange={(e) => setText(e.target.value)} />
      <div className="w-row">
        <button className={"w-btn" + (hearing ? " w-danger" : "")}
                onClick={() => (hearing
                  ? (ear.current?.stop(), setHearing(false))
                  : dictate())}>
          {hearing ? tr("w.jr.stop", lang) : tr("w.jr.speak", lang)}
        </button>
        <button className="w-btn primary" disabled={!text.trim()}
                onClick={async () => {
                  setFault(null);
                  try {
                    await api.addJournal(uid, text.trim(), token);
                    setText(""); setKept(true);
                  } catch (e) {
                    setFault(e instanceof Error ? e.message : String(e));
                  }
                }}>{tr("w.jr.keep", lang)}</button>
      </div>
      {kept && <p className="w-reply">{tr("w.jr.kept", lang)}</p>}
      <Fault fault={fault} />
    </div>
  );
}

// The wrist's short names for the coach's areas: labels stay short (a
// watch chip has room for one word) and the wire gets the server's own
// vocabulary. These used to be sent raw — "mind", "money", "bonds" — and
// every chip but career was refused at the door; the tightened area type
// on `api.coach` is what finally surfaced it.
const W_AREAS = {
  mind: "mental_health", fitness: "health_fitness", career: "career",
  money: "finance", bonds: "relationships", growth: "personal_growth",
} as const;

function FaceCoach({ uid, token, lang }: FaceProps) {
  const [area, setArea] = useState<keyof typeof W_AREAS>("mind");
  const [said, setSaid] = useState("");
  const [reply, setReply] = useState("");
  const [fault, setFault] = useState<string | null>(null);
  if (!uid || !token) return <SignIn lang={lang} />;
  return (
    <div className="w-face-body">
      <div className="w-row w-wrap">
        {(Object.keys(W_AREAS) as (keyof typeof W_AREAS)[]).map((a) => (
          <button key={a} className={"w-chip" + (a === area ? " on" : "")}
                  onClick={() => setArea(a)}>
            {tr(`w.co.${a}`, lang)}
          </button>
        ))}
      </div>
      <input className="w-input" value={said}
             placeholder={tr("w.co.ph", lang)}
             onChange={(e) => setSaid(e.target.value)} />
      <button className="w-btn primary" disabled={!said.trim()}
              onClick={async () => {
                setFault(null);
                try {
                  const g = await api.coach(
                    uid, { area: W_AREAS[area], message: said.trim() },
                    token);
                  setReply(g.content); setSaid("");
                } catch (e) {
                  setFault(e instanceof Error ? e.message : String(e));
                }
              }}>{tr("w.co.ask", lang)}</button>
      {reply && <p className="w-reply">{reply}</p>}
      <Fault fault={fault} />
    </div>
  );
}

// ---- 27 · Baseline and 28 · Sources ---------------------------------------

function FaceBaseline({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.baseline(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<BaselineMetric[]>(
    uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const resting = data?.find((m) => m.metric === "heart_rate");
  const samples = data?.reduce((n, m) => n + (m.samples || 0), 0) || 0;
  return (
    <div className="w-center">
      <span className="w-ring" aria-hidden="true">
        <b>{resting?.value != null ? Math.round(resting.value) : "—"}</b>
      </span>
      <p className="w-note">{tr("w.base.resting", lang)}</p>
      <p className="w-note">
        {tr("w.base.learning", lang)} · {samples}
      </p>
      <Fault fault={fault} />
    </div>
  );
}

function FaceSources({ uid, token, lang }: FaceProps) {
  const [again, setAgain] = useState(0);
  const loader = useCallback(() => api.sources(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null, again);
  const [flipFault, setFlipFault] = useState<string | null>(null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const rows = (data as { source: string;
    consented: boolean }[] | null) || [];
  return (
    <div className="w-face-body">
      {rows.slice(0, 4).map((s) => (
        <div className="w-meter-row" key={s.source}>
          <span className="w-meter-label">{s.source.replace(/_/g, " ")}</span>
          <button className={"w-toggle" + (s.consented ? " on" : "")}
                  aria-pressed={s.consented}
                  aria-label={s.source}
                  onClick={async () => {
                    setFlipFault(null);
                    try {
                      await api.setSources(
                        uid, { source: s.source, consented: !s.consented },
                        token);
                      setAgain((n) => n + 1);
                    } catch (e) {
                      setFlipFault(e instanceof Error ? e.message : String(e));
                    }
                  }} />
        </div>
      ))}
      {rows.length === 0 && <p className="w-note">{tr("w.src.none", lang)}</p>}
      <Fault fault={fault || flipFault} />
    </div>
  );
}

// ---- 29 · Privacy, 30 · Handoff, 31 · Offline, 32 · Conditions -------------

function FacePrivacy({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.auditLog(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const rows = (data as { entries?: unknown[]; chain_ok?: boolean } | null);
  const entries = Array.isArray(rows) ? rows : rows?.entries || [];
  return (
    <div className="w-center">
      <p className="w-line">
        {rows && !Array.isArray(rows) && rows.chain_ok === false
          ? tr("w.priv.broken", lang) : tr("w.priv.chain", lang)}
      </p>
      <p className="w-note">{entries.length} · {tr("w.priv.entries", lang)}</p>
      <Fault fault={fault} />
    </div>
  );
}

function FaceHandoff({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.careTeamStatus(uid!, token!),
                             [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const team = (data as { linked?: boolean; org_name?: string;
    department?: string } | null);
  return (
    <div className="w-center">
      <p className="w-line">
        {team?.linked
          ? (team.org_name || tr("w.ho.linked", lang))
          : tr("w.ho.none", lang)}
      </p>
      <p className="w-note">{tr("w.ho.revocable", lang)}</p>
      <Fault fault={fault} />
    </div>
  );
}

function FaceOffline({ lang }: FaceProps) {
  const loader = useCallback(() => api.offlineStatus(), []);
  const { data, fault } = useDoor(loader);
  return (
    <div className="w-center">
      <span className={"w-shield" + (data?.offline ? " on" : "")}
            aria-hidden="true" />
      <p className="w-line">
        {data?.offline ? tr("w.offl.nothing", lang) : tr("w.offl.open", lang)}
      </p>
      <Fault fault={fault} />
    </div>
  );
}

function FaceConditions({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.selfProfile(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const known = (data as { known_conditions?: string[] } | null)
    ?.known_conditions || [];
  return (
    <div className="w-face-body">
      {known.slice(0, 4).map((c) => (
        <p className="w-line" key={c}>{c.replace(/_/g, " ")}</p>
      ))}
      {known.length === 0 && <p className="w-note">{tr("w.cond.none", lang)}</p>}
      <p className="w-note">{tr("w.cond.adapts", lang)}</p>
      <Fault fault={fault} />
    </div>
  );
}

// ---- 33 · Style, 34 · History, 35 · Family, 36 · Agents --------------------

function FaceStyle({ uid, token, lang }: FaceProps) {
  const [tone, setTone] = useState("");
  const [set, setSet] = useState(false);
  const [fault, setFault] = useState<string | null>(null);
  if (!uid || !token) return <SignIn lang={lang} />;
  return (
    <div className="w-face-body">
      <p className="w-note">{tr("w.style.shapes", lang)}</p>
      <input className="w-input" value={tone}
             placeholder={tr("w.style.ph", lang)}
             onChange={(e) => setTone(e.target.value)} />
      <button className="w-btn primary" disabled={!tone.trim()}
              onClick={async () => {
                setFault(null);
                try {
                  await api.setPersonality(uid, { tone: tone.trim() }, token);
                  setSet(true); setTone("");
                } catch (e) {
                  setFault(e instanceof Error ? e.message : String(e));
                }
              }}>{tr("w.style.set", lang)}</button>
      {set && <p className="w-reply">{tr("w.style.done", lang)}</p>}
      <Fault fault={fault} />
    </div>
  );
}

function FaceHistory({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.events(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const rows = (data as { type: string;
    created_at?: string }[] | null) || [];
  return (
    <div className="w-face-body">
      {rows.slice(0, 4).map((e, i) => (
        <p className="w-line" key={i}>
          {(e.created_at || "").slice(11, 16)} · {e.type.replace(/_/g, " ")}
        </p>
      ))}
      {rows.length === 0 && <p className="w-note">{tr("w.hist.none", lang)}</p>}
      <Fault fault={fault} />
    </div>
  );
}

function FaceFamily({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.children(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const kids = (data as { id: string; name?: string;
    display_name?: string }[] | null) || [];
  return (
    <div className="w-face-body">
      {kids.slice(0, 3).map((k) => (
        <p className="w-line" key={k.id}>{k.name || k.display_name || k.id}</p>
      ))}
      {kids.length === 0 && <p className="w-note">{tr("w.fam.none", lang)}</p>}
      <Fault fault={fault} />
    </div>
  );
}

function FaceAgents({ uid, token, lang }: FaceProps) {
  const loader = useCallback(() => api.underway(uid!, token!), [uid, token]);
  const { data, fault } = useDoor<unknown>(uid && token ? loader : null);
  if (!uid || !token) return <SignIn lang={lang} />;
  const rows = ((data as { underway?: UnderwayRow[] } | null)?.underway) || [];
  const running = rows.filter((r) => r.why === "open" || r.why === "on"
    || r.why === "agreed").length;
  const waiting = rows.filter((r) => r.why === "proposed").length;
  return (
    <div className="w-face-body">
      <div className="w-meter-row">
        <span className="w-dot c1" aria-hidden="true" />
        <span className="w-meter-label">{tr("w.ag.running", lang)}</span>
        <span className="w-meter-val">{running}</span>
      </div>
      <div className="w-meter-row">
        <span className="w-dot c0" aria-hidden="true" />
        <span className="w-meter-label">{tr("w.ag.needhelp", lang)}</span>
        <span className="w-meter-val">{waiting}</span>
      </div>
      <p className="w-note">{tr("w.ag.open", lang)}</p>
      <Fault fault={fault} />
    </div>
  );
}

// ---- the shell -------------------------------------------------------------

const FACE_OF: Record<FaceSlug, (p: FaceProps) => JSX.Element> = {
  "home": FaceHome, "talk": FaceTalk, "voice": FaceVoice,
  "health": FaceHealth, "heart": FaceHeart, "rings": FaceRings,
  "briefing": FaceBriefing, "streak": FaceStreak, "check-in": FaceCheckin,
  "insight": FaceInsight, "monitoring": FaceMonitoring,
  "foresight": FaceForesight, "emergency": FaceEmergency, "cpr": FaceCpr,
  "medical-id": FaceMedicalId, "sensitivity": FaceSensitivity,
  "ambient": FaceAmbient, "companion": FaceCompanion,
  "notifications": FaceNotifications, "devices": FaceDevices,
  "guardian": FaceGuardian, "settings": FaceSettings, "breathe": FaceBreathe,
  "feedback": FaceFeedback, "journal": FaceJournal, "coach": FaceCoach,
  "baseline": FaceBaseline, "sources": FaceSources, "privacy": FacePrivacy,
  "handoff": FaceHandoff, "offline": FaceOffline, "conditions": FaceConditions,
  "style": FaceStyle, "history": FaceHistory, "family": FaceFamily,
  "agents": FaceAgents,
};

export function Watch({ lang, onClose }: { lang: Lang; onClose: () => void }) {
  const { session } = useSession();
  const [at, setAt] = useState(() => faceFromHash(window.location.hash));
  // The settings read that must not spend the first tap's gesture: primed
  // once for the whole wrist, so Voice and Journal hear on the tap that
  // asked. See test_the_gesture_outlives_the_settings_read.
  useEffect(() => { void primeVoice(); }, []);
  const [grid, setGrid] = useState(false);
  const touch = useRef<number | null>(null);

  // The hash tracks the face, so a README link opens one directly and a
  // reload stays where the wrist was.
  useEffect(() => {
    window.location.hash = `#watch/${String(at + 1).padStart(2, "0")}-${FACES[at]}`;
  }, [at]);
  useEffect(() => {
    const onHash = () => {
      if (window.location.hash.startsWith("#watch")) {
        setAt(faceFromHash(window.location.hash));
      }
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const step = (delta: number) =>
    setAt((i) => (i + delta + FACES.length) % FACES.length);
  const slug = FACES[at];
  const Face = FACE_OF[slug];

  return (
    <div className="watch-stage" role="dialog"
         aria-label={tr("w.title", lang)}>
      <button className="watch-leave" aria-label={tr("w.leave", lang)}
              onClick={() => {
        window.location.hash = "";
        onClose();
      }}>✕</button>
      <div className="watch-frame"
           onTouchStart={(e) => { touch.current = e.touches[0].clientX; }}
           onTouchEnd={(e) => {
             if (touch.current == null) return;
             const dx = e.changedTouches[0].clientX - touch.current;
             touch.current = null;
             if (dx > 44) step(-1); else if (dx < -44) step(1);
           }}>
        <header className="w-head">
          {/* `check-in` → `w.f.checkin`: the table's own key pattern is
              word characters, and a hyphenated key would sit outside every
              completeness check that reads it. */}
          <span className="w-head-title">{tr(`w.f.${slug.replace(/-/g, "")}`, lang)}</span>
          <span className="w-head-time">
            {new Date().toTimeString().slice(0, 5)}
          </span>
        </header>
        {grid ? (
          <div className="w-grid">
            {FACES.map((s, i) => (
              <button key={s} className={"w-grid-cell" + (i === at ? " on" : "")}
                      onClick={() => { setAt(i); setGrid(false); }}>
                {String(i + 1).padStart(2, "0")}
              </button>
            ))}
          </div>
        ) : (
          <Face uid={session.userId || null} token={session.userToken || null}
                lang={lang} go={(s) => setAt(FACES.indexOf(s))} />
        )}
        <footer className="w-foot">
          <button className="w-nav" aria-label={tr("w.prev", lang)}
                  onClick={() => step(-1)}>‹</button>
          <button className="w-index"
                  aria-label={tr("w.all", lang)}
                  aria-expanded={grid}
                  onClick={() => setGrid((g) => !g)}>
            {String(at + 1).padStart(2, "0")} / {FACES.length}
          </button>
          <button className="w-nav" aria-label={tr("w.next", lang)}
                  onClick={() => step(1)}>›</button>
        </footer>
      </div>
    </div>
  );
}
