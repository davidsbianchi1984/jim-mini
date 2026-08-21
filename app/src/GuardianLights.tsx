import { useCallback, useEffect, useState } from "react";
import { api, type AlarmRow, type CrashWatchStatus, type VigilStatus } from "./api";
import { standEar, type EarState } from "./ear";
import { t as tr, visitorLang } from "./l10n";
import { useSession } from "./store";

/**
 * The Guardian's lights, always on screen — QRME's agent-lights widget,
 * for the product whose "agents" are the watches it keeps. Green is the
 * Guardian watching; amber is it asking for you (the crash watch mid
 * check-in); red is an open alarm or a tripped vigil. Pinned bottom-left
 * like its sibling, minimizable to a dot, and — the lesson its sibling
 * paid for — unreachable is a state it shows, not one it hides in: a
 * failed first fetch renders an unlit dot that retries on press.
 *
 * Built from routes the console already opens (alarms, vigil, crash
 * watch): a glance is not a new capability, so it gets no new door.
 */

const POLL_MS = 15000;
const MIN_KEY = "jim.lights.min";
// The standing ear's switch, remembered per browser like the minimize —
// a consent this person gave on this machine, never a default.
const EAR_KEY = "jim.ear.on";

const COLORS = { green: "#43e08a", amber: "#ffb84d", red: "#e0687a" };

type Glance = {
  alarms: AlarmRow[];
  vigil: VigilStatus | null;
  crash: CrashWatchStatus | null;
};

function worst(g: Glance): keyof typeof COLORS {
  if (g.alarms.length > 0 || g.vigil?.tripped) return "red";
  if (g.crash?.asking) return "amber";
  return "green";
}

export function GuardianLights() {
  const { session } = useSession();
  const lang = visitorLang();
  const [glance, setGlance] = useState<Glance | null>(null);
  const [unreachable, setUnreachable] = useState(false);
  const [min, setMin] = useState(() => localStorage.getItem(MIN_KEY) === "1");
  // The standing ear: while a sound-sensing monitor is plugged in, the
  // console can keep the device's recogniser listening and hand everything
  // heard to that monitor's door, where the cue vocabulary (jim/cues.py)
  // decides what any of it means. The row only appears when such a monitor
  // is on — an ear with no door to bring sound to would be surveillance
  // with extra steps.
  const [soundMonitor, setSoundMonitor] = useState<string | null>(null);
  const [earOn, setEarOn] = useState(
    () => localStorage.getItem(EAR_KEY) === "1");
  const [ear, setEar] = useState<EarState>("off");

  const load = useCallback(() => {
    const { userId, userToken } = session;
    if (!userId || !userToken) return;
    Promise.allSettled([
      api.alarms(userId, userToken, true),
      api.getVigil(userId, userToken),
      api.crashWatch(userId, userToken),
    ]).then(([a, v, c]) => {
      if (a.status === "rejected" && v.status === "rejected"
          && c.status === "rejected") {
        setUnreachable(true); // keep any last glance
        return;
      }
      setUnreachable(false);
      setGlance({
        alarms: a.status === "fulfilled" ? a.value : [],
        vigil: v.status === "fulfilled" ? v.value : null,
        crash: c.status === "fulfilled" ? c.value : null,
      });
    });
    // Separately, and allowed to fail without dimming the glance: is any
    // sound-sensing monitor plugged in for the ear to feed? Polled with the
    // rest so plugging an earpiece on the monitors screen shows the row
    // here without a reload — and unplugging it takes the row away.
    api.monitors(userId, userToken).then((rows) => {
      const hears = rows.find((r) => r.on && r.senses.includes("sound"));
      setSoundMonitor(hears ? hears.name : null);
    }).catch(() => { /* the glance rows carry the reachability story */ });
  }, [session.userId, session.userToken]);

  useEffect(() => {
    load();
    const timer = setInterval(load, POLL_MS);
    return () => clearInterval(timer);
  }, [load]);

  // The ear's lifetime is exactly the switch's: on with a plugged sound
  // monitor, it stands (and survives the widget being minimized — the dot
  // still names the account being listened for); off, unplugged, or signed
  // out, it stops. The server's door re-checks consent on every submission,
  // so a monitor unplugged mid-listen is refused there, not trusted here.
  useEffect(() => {
    const { userId, userToken } = session;
    if (!earOn || !soundMonitor || !userId || !userToken) {
      setEar("off");
      return;
    }
    const standing = standEar(userId, userToken, soundMonitor, setEar);
    return () => standing.stop();
  }, [earOn, soundMonitor, session.userId, session.userToken]);

  const flipEar = () => {
    const v = !earOn;
    setEarOn(v);
    if (v) localStorage.setItem(EAR_KEY, "1");
    else localStorage.removeItem(EAR_KEY);
  };

  if (!glance) {
    if (!unreachable || !session.userId) return null;
    return (
      <button className="wl-dot wl-dot-off"
              onClick={load}
              aria-label={tr("lights.unreachable", lang)}
              title={tr("lights.unreachable", lang)} />
    );
  }
  const tone = worst(glance);

  const setMinimized = (v: boolean) => {
    setMin(v);
    if (v) localStorage.setItem(MIN_KEY, "1");
    else localStorage.removeItem(MIN_KEY);
  };

  if (min) {
    return (
      <button className="wl-dot" style={{ background: COLORS[tone] }}
              onClick={() => setMinimized(false)}
              aria-label={tr("lights.show", lang)}
              title={tr("lights.title", lang)} />
    );
  }

  const rows = [
    { color: COLORS.red, label: tr("lights.alarms", lang),
      n: glance.alarms.length },
    { color: glance.vigil?.tripped ? COLORS.red : COLORS.green,
      label: tr("lights.vigil", lang),
      n: glance.vigil?.armed ? 1 : 0 },
    { color: glance.crash?.asking ? COLORS.amber : COLORS.green,
      label: tr("lights.crash", lang),
      n: glance.crash?.armed ? 1 : 0 },
  ];

  return (
    <div className="watch-lights" role="status"
         aria-label={tr("lights.title", lang)}
         style={{ borderColor: COLORS[tone] }}>
      <div className="wl-head">
        <span className="wl-name">{tr("lights.title", lang)}</span>
        <button className="wl-min" onClick={() => setMinimized(true)}
                aria-label={tr("lights.hide", lang)}>–</button>
      </div>
      {rows.map((r) => (
        <div className="wl-row" key={r.label}>
          <span className="wl-light" style={{ background: r.color }} />
          <span className="wl-count">{r.n}</span>
          <span className="wl-label">{r.label}</span>
        </div>
      ))}
      {soundMonitor && (
        <div className="wl-row">
          <span className="wl-light"
                style={{ background: ear === "listening" ? COLORS.green
                  : earOn ? COLORS.amber : "var(--muted)" }} />
          <span className="wl-count">{ear === "listening" ? 1 : 0}</span>
          <button className="wl-ear" onClick={flipEar}
                  aria-label={earOn ? tr("lights.ear.stop", lang)
                    : tr("lights.ear.start", lang)}
                  title={earOn ? tr("lights.ear.stop", lang)
                    : tr("lights.ear.start", lang)}>
            {tr("lights.ear", lang)}
          </button>
        </div>
      )}
      {soundMonitor && earOn && ear !== "off" && (
        <div className="wl-foot">
          {ear === "listening" ? tr("lights.ear.on", lang)
            : ear === "refused" ? tr("lights.ear.refused", lang)
            : tr("lights.ear.none", lang)}
        </div>
      )}
      <div className="wl-foot">
        {tone === "green" ? tr("lights.quiet", lang)
          : tone === "amber" ? tr("lights.asking", lang)
          : tr("lights.alarm", lang)}
      </div>
    </div>
  );
}
