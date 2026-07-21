// Minimal, safe preload. The renderer talks to the QRME API over plain fetch;
// this just exposes a tiny surface for the app to know it runs under Electron.
const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("qrmeDesktop", {
  isElectron: true,
  platform: process.platform,
});
