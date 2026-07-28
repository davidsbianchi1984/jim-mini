// Minimal, safe preload. The renderer talks to the JIM API over plain fetch;
// this exposes a tiny surface for the app to know it runs under Electron —
// plus one action: opening the spawned backend's log file, because that is
// where the emailed-code "console" transport writes when no SMTP is
// configured, and a packaged app has no terminal for a user to look at.
const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("jimDesktop", {
  isElectron: true,
  platform: process.platform,
  openBackendLog: () => ipcRenderer.invoke("open-backend-log"),
});
