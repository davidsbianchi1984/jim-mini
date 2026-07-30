import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import { CONSOLE_VERSION } from "./api";
import { sendProblems } from "./errors";
import { SessionProvider } from "./store";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <SessionProvider>
      <App />
    </SessionProvider>
  </React.StrictMode>,
);

// One shot at launch: hand the collector whatever failed since the last time,
// so bugs that only happen on other people's machines are still findable.
//
// Here rather than in a `useEffect` because this is not part of any screen and
// must not be tied to one mounting; and here rather than in the Electron main
// process because the buffer lives in this window's storage — the main process
// would have to ask for it, and a diagnostic that needs an IPC channel of its
// own is a diagnostic with more ways to go wrong than the bugs it finds. It
// lands beside the update check either way: `setupAutoUpdate()` runs the
// moment this window is created, so the report goes out while the next
// version is coming down.
//
// Deliberately unawaited. Nothing on screen depends on it, nothing waits for
// it, and it resolves to an outcome rather than throwing — see errors.ts.
sendProblems(CONSOLE_VERSION);

// Installable on a phone: the shell is cached so the app opens instantly and
// survives a brief drop in connectivity. Only over http(s) — the Electron
// desktop shell runs from file://, where service workers don't apply.
if ("serviceWorker" in navigator && location.protocol.startsWith("http")) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").catch(() => undefined);
  });
}
