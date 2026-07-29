// Electron main process. In dev it loads the Vite dev server
// (ELECTRON_START_URL); in production it loads the built bundle from dist/.
//
// The installer also ships the Guardian backend itself — a PyInstaller
// one-file binary under resources/backend/ — and this process is what makes
// the app double-click-and-done: probe for a backend, spawn the bundled one
// when nothing answers, wait for /health, then open the window, and take the
// child down again on quit. A backend the user already runs (or a dev
// checkout without the binary) is left exactly alone.
const { app, BrowserWindow, dialog, ipcMain, shell } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const http = require("http");
const path = require("path");

const DEFAULT_PORT = Number(process.env.JIM_PORT || 8000);
let backendPort = DEFAULT_PORT;
let backendProc = null;

// Ask the backend on `port` who it is. Returns null when nothing answers.
function probeHealth(port) {
  return new Promise((resolve) => {
    const req = http.get(
      { host: "127.0.0.1", port, path: "/health", timeout: 1500 },
      (res) => {
        let body = "";
        res.on("data", (c) => { body += c; });
        res.on("end", () => {
          if (res.statusCode !== 200) return resolve(null);
          try { resolve(JSON.parse(body)); } catch { resolve({}); }
        });
      },
    );
    req.on("error", () => resolve(null));
    req.on("timeout", () => { req.destroy(); resolve(null); });
  });
}

// A port nothing is listening on, for when the default one is held by a
// backend that is not ours.
function freePort() {
  return new Promise((resolve) => {
    const net = require("net");
    const srv = net.createServer();
    srv.listen(0, "127.0.0.1", () => {
      const { port } = srv.address();
      srv.close(() => resolve(port));
    });
  });
}

// On Windows the frozen backend is a bootloader that spawns the real Python
// process as a child; killing the parent leaves the child holding the port
// forever. That zombie then answers every future launch — including after
// an upgrade — which is how one install's signup outlived three releases.
// Take the whole tree.
function killBackend() {
  if (!backendProc) return;
  const pid = backendProc.pid;
  backendProc = null;
  if (process.platform === "win32") {
    try {
      require("child_process").execFileSync(
        "taskkill", ["/pid", String(pid), "/T", "/F"], { stdio: "ignore" });
      return;
    } catch { /* fall through to the plain kill */ }
  }
  try { process.kill(pid); } catch { /* already gone */ }
}

function bundledBackend() {
  const name = process.platform === "win32" ? "jim-backend.exe" : "jim-backend";
  const bin = path.join(process.resourcesPath, "backend", name);
  return fs.existsSync(bin) ? bin : null;
}

async function ensureBackend() {
  const running = await probeHealth(backendPort);
  if (running && running.version === app.getVersion()) return;  // ours already
  const bin = bundledBackend();
  if (!bin) return;                          // dev checkout — the console's own
                                             // connection panel says what to do
  if (running) {
    // Something answers the default port but is not this version: a zombie
    // from an older install, or another product. Never adopt it — it serves
    // an older API. Take a port of our own instead.
    backendPort = await freePort();
  }
  const log = fs.createWriteStream(
    path.join(app.getPath("userData"), "backend.log"), { flags: "a" });
  backendProc = spawn(bin, [], {
    env: {
      ...process.env,
      JIM_DB: path.join(app.getPath("userData"), "jim.db"),
      JIM_PORT: String(backendPort),
    },
    stdio: ["ignore", "pipe", "pipe"],
  });
  backendProc.stdout.pipe(log);
  backendProc.stderr.pipe(log);
  backendProc.on("exit", () => { backendProc = null; });
  // A frozen backend cold-starts in a few seconds; don't open a window that
  // reports "unreachable" for a backend we are busy starting.
  for (let i = 0; i < 40; i++) {
    const up = await probeHealth(backendPort);
    if (up) return;
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
      // The window is created after the backend is up, so the renderer is
      // told the exact address of *this* app's backend — never a guess at
      // the default port, which an older install's zombie may still hold.
      additionalArguments: [`--jim-backend-url=http://127.0.0.1:${backendPort}`],
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
// The renderer must talk to *our* backend, whatever port it ended up on.
ipcMain.handle("backend-url", () => `http://127.0.0.1:${backendPort}`);

ipcMain.handle("open-backend-log", () => {
  const logPath = path.join(app.getPath("userData"), "backend.log");
  if (fs.existsSync(logPath)) return shell.openPath(logPath);
  return "no backend log yet — is a separately-run backend serving this app?";
});

// Keep the install current. On launch, ask GitHub Releases whether a newer
// version exists. Windows and Linux download it in the background and offer
// a restart; macOS cannot swap an unsigned app under itself, so it gets told
// and taken to the download instead. Every failure path is silent on
// purpose: an update check must never stand between the user and the app.
function setupAutoUpdate() {
  if (!app.isPackaged) return;
  let autoUpdater;
  try {
    ({ autoUpdater } = require("electron-updater"));
  } catch {
    return; // updater not bundled (e.g. a dev build) — the app is unaffected
  }
  const canSelfInstall = process.platform !== "darwin";
  autoUpdater.autoDownload = canSelfInstall;
  autoUpdater.on("error", () => {});
  autoUpdater.on("update-available", async (info) => {
    if (canSelfInstall) return; // downloading; the next event handles it
    const { response } = await dialog.showMessageBox({
      type: "info",
      title: "Update available",
      message: `Version ${info.version} is out (you have ${app.getVersion()}).`,
      detail: "The download page has the new installer.",
      buttons: ["Open download page", "Later"],
      defaultId: 0,
    });
    if (response === 0) {
      shell.openExternal(
        `https://github.com/davidsbianchi1984/jim-mini/releases/latest`);
    }
  });
  autoUpdater.on("update-downloaded", async (info) => {
    const { response } = await dialog.showMessageBox({
      type: "info",
      title: "Update ready",
      message: `Version ${info.version} is downloaded.`,
      detail: "Restart to switch to it. Your data stays where it is.",
      buttons: ["Restart now", "Later"],
      defaultId: 0,
    });
    if (response === 0) {
      killBackend(); // ours dies with us, so the new version starts its own
      autoUpdater.quitAndInstall();
    }
  });
  autoUpdater.checkForUpdates().catch(() => {});
}

app.whenReady().then(async () => {
  await ensureBackend();
  createWindow();
  setupAutoUpdate();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

// The spawned backend belongs to this app instance: it dies with the window,
// process tree and all.
app.on("will-quit", killBackend);
process.on("exit", killBackend);
