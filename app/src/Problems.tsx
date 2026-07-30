import { useState } from "react";
import { CONSOLE_VERSION } from "./api";
import {
  clearProblems, problemReport, problems, type Problem,
} from "./errors";

/**
 * What went wrong, and exactly what leaves if you decide to share it.
 *
 * The preview is not a description of the report — it *is* the report, from the
 * same function that produces the copied text. A screen that summarised the
 * payload in prose would be making a promise the code could quietly break; this
 * one can only be wrong in the way the payload is wrong.
 *
 * Nothing here transmits. The buffer is local, and getting a report to a
 * developer is a copy and a paste somebody chooses to make. That is not a
 * limitation to apologise for: the backend ships inside the installer, so for a
 * desktop user there is no server on the other end to send to anyway.
 */
export function Problems() {
  const [rows, setRows] = useState<Problem[]>(problems);
  const [showing, setShowing] = useState(false);
  const [copied, setCopied] = useState(false);

  const report = JSON.stringify(problemReport(CONSOLE_VERSION), null, 2);

  return (
    <div className="card">
      <h3>What went wrong</h3>
      <p className="muted small">
        Failed requests this app has seen, kept on this device. The operation
        and the status code are recorded; the error message is not, because
        those messages quote what you typed — a device name, a place on your
        body, a language code. You can read the message when it happens; it is
        yours, and it does not belong in a log.
      </p>

      {rows.length === 0 && <p className="muted small">Nothing has failed.</p>}
      {rows.map((r) => (
        <div key={r.fingerprint} className="row">
          <code>{r.op}</code>
          <span className="muted">
            {r.status === 0 ? "no answer" : r.status}
          </span>
          {r.count > 1 && <span className="muted">×{r.count}</span>}
          <span className="muted">{r.day}</span>
        </div>
      ))}

      {rows.length > 0 && (
        <>
          <div className="row">
            <button onClick={() => setShowing(!showing)}>
              {showing ? "Hide" : "Show me exactly what would be shared"}
            </button>
            <button
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(report);
                  setCopied(true);
                } catch {
                  // Clipboard permission is not guaranteed. Falling back to
                  // showing the text is more useful than an error, because the
                  // text is the deliverable either way.
                  setShowing(true);
                }
              }}>
              {copied ? "Copied" : "Copy the report"}
            </button>
            <button
              onClick={() => {
                clearProblems();
                setRows([]);
                setCopied(false);
              }}>
              Clear
            </button>
          </div>
          {showing && <pre className="small">{report}</pre>}
        </>
      )}
    </div>
  );
}
