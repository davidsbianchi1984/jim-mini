import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import { SessionProvider } from "./store";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <SessionProvider>
      <App />
    </SessionProvider>
  </React.StrictMode>,
);

// Installable on a phone: the shell is cached so the app opens instantly and
// survives a brief drop in connectivity. Only over http(s) — the Electron
// desktop shell runs from file://, where service workers don't apply.
if ("serviceWorker" in navigator && location.protocol.startsWith("http")) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").catch(() => undefined);
  });
}
