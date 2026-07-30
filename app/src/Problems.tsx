import { useState } from "react";
import { CONSOLE_VERSION } from "./api";
import {
  clearProblems, collectorUrl, problemReport, problems, sendProblems,
  sendingEnabled, setSending, type Problem, type SendOutcome,
} from "./errors";

/**
 * What went wrong, and exactly what leaves this device.
 *
 * The preview is not a description of the report — it *is* the report, from the
 * same function that produces the copied text and the posted body. A screen
 * that summarised the payload in prose would be making a promise the code could
 * quietly break; this one can only be wrong in the way the payload is wrong.
 *
 * Two lists on purpose. The rows are the whole history, which is the user's;
 * the preview is the unreported remainder, which is the message. After a send
 * the history is unchanged and the preview is empty, and that difference is the
 * honest picture rather than a bug in the screen.
 */
const OUTCOME: Record<SendOutcome, string> = {
  "sent": "Sent.",
  "nothing-to-send": "Nothing new to send.",
  "turned-off": "Sending is off.",
  "no-collector": "This build has nowhere to send.",
  "awaiting-notice": "Waiting for you to answer the notice first.",
  "failed": "Could not reach the collector — it will try again next time.",
};

export function Problems() {
  const [rows, setRows] = useState<Problem[]>(problems);
  const [showing, setShowing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [sending, setSendingNow] = useState(false);
  const [said, setSaid] = useState("");
  const [on, setOn] = useState(sendingEnabled);

  const collector = collectorUrl();
  // Built once and used for both the preview and the count, so the number
  // beside the button and the text below it can never describe different
  // things.
  const payload = problemReport(CONSOLE_VERSION);
  const report = JSON.stringify(payload, null, 2);
  const unsent = (payload.problems as Problem[]).length;

  return (
    <div className="card">
      <h3>What went wrong</h3>
      <p className="muted small">
        Failed requests this app has seen. The operation and the status code are
        recorded; the error message is not, because those messages quote what
        you typed — a device name, a place on your body, a language code. You
        can read the message when it happens; it is yours, and it does not
        belong in a log.
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

      <p className="muted small">
        {collector
          ? <>Sent to <code>{collector}</code> when the app opens, so the
            people fixing these can see them. Only what the preview below
            shows, and only the part that has not been sent already —
            reopening the app does not send the same failure twice. Nothing
            went anywhere before you answered the notice on first run, and
            this switch is the same answer, changeable whenever you like.</>
          : <>This build has no collector configured, so nothing is sent
            anywhere. The report below exists for you to copy if you want to
            pass it on.</>}
      </p>

      {collector && (
        <div className="row">
          <label>
            <input
              type="checkbox"
              checked={on}
              onChange={(e) => { setSending(e.target.checked); setOn(e.target.checked); }}
            />{" "}
            Send these automatically
          </label>
          <button
            disabled={sending || !unsent}
            onClick={async () => {
              setSendingNow(true);
              const outcome = await sendProblems(CONSOLE_VERSION);
              setSaid(OUTCOME[outcome]);
              setRows(problems());
              setSendingNow(false);
            }}>
            {sending ? "Sending…" : "Send now"}
          </button>
          {said && <span className="muted small">{said}</span>}
        </div>
      )}

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
          {showing && (
            <>
              {unsent === 0 && (
                <p className="muted small">
                  Everything here has been sent already, so the next report is
                  empty. The list above is your copy and stays until you clear
                  it.
                </p>
              )}
              <pre className="small">{report}</pre>
            </>
          )}
        </>
      )}
    </div>
  );
}
