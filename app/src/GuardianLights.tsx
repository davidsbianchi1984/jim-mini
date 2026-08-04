import { useCallback, useEffect, useState } from "react";
import { api, type AlarmRow, type CrashWatchStatus, type VigilStatus } from "./api";
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
  }, [session.userId, session.userToken]);

  useEffect(() => {
    load();
    const timer = setInterval(load, POLL_MS);
    return () => clearInterval(timer);
  }, [load]);

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
      <div className="wl-foot">
        {tone === "green" ? tr("lights.quiet", lang)
          : tone === "amber" ? tr("lights.asking", lang)
          : tr("lights.alarm", lang)}
      </div>
    </div>
  );
}
