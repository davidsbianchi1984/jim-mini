// Minimal, safe preload. The renderer talks to the JIM API over plain fetch;
// this exposes a tiny surface for the app to know it runs under Electron —
// plus one action: opening the spawned backend's log file, because that is
// where the emailed-code "console" transport writes when no SMTP is
// configured, and a packaged app has no terminal for a user to look at.
const { contextBridge, ipcRenderer } = require("electron");

const backendArg = process.argv.find((a) => a.startsWith("--jim-backend-url="));

contextBridge.exposeInMainWorld("jimDesktop", {
  isElectron: true,
  platform: process.platform,
  // The address of the backend this app actually started — the renderer
  // must not guess a port an older install's leftover process may hold.
  backendUrl: backendArg ? backendArg.split("=").slice(1).join("=") : null,
  openBackendLog: () => ipcRenderer.invoke("open-backend-log"),
  // "Let my phone reach JIM on this Wi-Fi" — read and flip the loopback
  // posture. Flipping restarts the spawned backend on the new interface.
  lanAccess: () => ipcRenderer.invoke("lan-access"),
  setLanAccess: (enabled) => ipcRenderer.invoke("set-lan-access", enabled),
});
