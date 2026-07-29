import { useEffect, useState } from "react";
import { api, CONSOLE_VERSION, clearBase, getBase } from "./api";

/**
 * The version handshake, made visible.
 *
 * A stale backend from an older install answers /health perfectly well and
 * then serves an older API — so the app looks alive while every newer
 * screen (medications, care team, coach context) answers "Not Found" with
 * no explanation. The Electron shell already refuses to adopt a
 * version-mismatched backend on its own port, but a *stored* base URL (for
 * example the machine's LAN address saved for the phone bridge) can still
 * route the console to whatever old process holds that address.
 *
 * This banner closes the loop from the console side: compare the console's
 * build version against what /health reports, and on mismatch say so in a
 * sentence, with the one-click fix when there is one.
 */
export function VersionGuard() {
  const [backend, setBackend] = useState<string | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    let alive = true;
    api.health()
      // A backend so old it predates the version field is exactly the case.
      .then((h) => { if (alive) setBackend(h.version || "(older than 0.5)"); })
      .catch(() => { /* unreachable is the connection panel's story */ });
    return () => { alive = false; };
  }, []);

  if (dismissed || backend === null || backend === CONSOLE_VERSION) return null;

  const desktop = (window as {
    jimDesktop?: { backendUrl?: string | null } }).jimDesktop?.backendUrl;
  const stored = typeof localStorage !== "undefined"
    ? localStorage.getItem("jim.base") : null;
  // The one-click cure: when this app started its own backend but a stored
  // address is steering the console elsewhere, drop the address and reload.
  const canRepoint = Boolean(desktop && stored);

  return (
    <div className="version-guard" role="alert">
      <span>
        <b>Two versions of JIM are answering.</b> This app is
        v{CONSOLE_VERSION}, but the backend at {getBase()} is
        v{backend} — an older install is still running, which is why newer
        screens say “Not Found”.
      </span>
      {canRepoint ? (
        <button className="vg-fix"
                onClick={() => { clearBase(); location.reload(); }}>
          Use this app’s own backend
        </button>
      ) : (
        <span className="vg-hint">
          Quit the older JIM app (or end a leftover “jim-backend” process —
          a restart of the computer also works), then reopen this app.
        </span>
      )}
      <button className="vg-close" onClick={() => setDismissed(true)}
              aria-label="Dismiss">×</button>
    </div>
  );
}
