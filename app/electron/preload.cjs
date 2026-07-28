// Minimal, safe preload. The renderer talks to the JIM API over plain fetch;
// this just exposes a tiny surface for the app to know it runs under Electron.
const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("jimDesktop", {
  isElectron: true,
  platform: process.platform,
});
