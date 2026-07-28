// Electron main process. In dev it loads the Vite dev server
// (ELECTRON_START_URL); in production it loads the built bundle from dist/.
//
// The installer also ships the Guardian backend itself — a PyInstaller
// one-file binary under resources/backend/ — and this process is what makes
// the app double-click-and-done: probe for a backend, spawn the bundled one
// when nothing answers, wait for /health, then open the window, and take the
// child down again on quit. A backend the user already runs (or a dev
// checkout without the binary) is left exactly alone.
const { app, BrowserWindow, ipcMain, shell } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const http = require("http");
const path = require("path");

const BACKEND_PORT = process.env.JIM_PORT || "8000";
let backendProc = null;

function probeHealth() {
  return new Promise((resolve) => {
    const req = http.get(
      { host: "127.0.0.1", port: BACKEND_PORT, path: "/health", timeout: 1500 },
      (res) => { res.resume(); resolve(res.statusCode === 200); },
    );
    req.on("error", () => resolve(false));
    req.on("timeout", () => { req.destroy(); resolve(false); });
  });
}

function bundledBackend() {
  const name = process.platform === "win32" ? "jim-backend.exe" : "jim-backend";
  const bin = path.join(process.resourcesPath, "backend", name);
  return fs.existsSync(bin) ? bin : null;
}

async function ensureBackend() {
  if (await probeHealth()) return;          // somebody already runs one
  const bin = bundledBackend();
  if (!bin) return;                          // dev checkout — the console's own
                                             // connection panel says what to do
  const log = fs.createWriteStream(
    path.join(app.getPath("userData"), "backend.log"), { flags: "a" });
  backendProc = spawn(bin, [], {
    env: {
      ...process.env,
      JIM_DB: path.join(app.getPath("userData"), "jim.db"),
      JIM_PORT: String(BACKEND_PORT),
    },
    stdio: ["ignore", "pipe", "pipe"],
  });
  backendProc.stdout.pipe(log);
  backendProc.stderr.pipe(log);
  backendProc.on("exit", () => { backendProc = null; });
  // A frozen backend cold-starts in a few seconds; don't open a window that
  // reports "unreachable" for a backend we are busy starting.
  for (let i = 0; i < 40; i++) {
    if (await probeHealth()) return;
    await new Promise((r) => setTimeout(r, 500));
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1180,
    height: 820,
    minWidth: 900,
    minHeight: 640,
    backgroundColor: "#0d0a20",
    title: "JIM Guardian",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // Open external links in the real browser, not inside the app window.
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  const devUrl = process.env.ELECTRON_START_URL;
  if (devUrl) {
    win.loadURL(devUrl);
  } else {
    win.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  }
}

// The "console" mail transport writes the verification code to the spawned
// backend's log; this is the packaged app's way to actually show it.
ipcMain.handle("open-backend-log", () => {
  const logPath = path.join(app.getPath("userData"), "backend.log");
  if (fs.existsSync(logPath)) return shell.openPath(logPath);
  return "no backend log yet — is a separately-run backend serving this app?";
});

app.whenReady().then(async () => {
  await ensureBackend();
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

// The spawned backend belongs to this app instance: it dies with the window.
app.on("will-quit", () => {
  if (backendProc) backendProc.kill();
});
