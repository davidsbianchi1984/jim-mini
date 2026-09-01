import { useState } from "react";
import { api, CONSOLE_VERSION, getBase } from "./api";
import {
  clearProblems, collectorUrl, markReported, problemReport, problems,
  sendProblems, sendingEnabled, setSending, type Problem, type SendOutcome,
} from "./errors";
import { t as tr, visitorLang } from "./l10n";

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
  const lang = visitorLang();
  const [rows, setRows] = useState<Problem[]>(problems);
  const [showing, setShowing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [sending, setSendingNow] = useState(false);
  const [said, setSaid] = useState("");
  const [on, setOn] = useState(sendingEnabled);

  // The operator's half: what has reached the server, from every client of
  // this deployment. Reading needs JIM_PROBLEMS_KEY (or a caller on the
  // backend's own machine); the refusal is rendered verbatim when it does.
  const [readerKey, setReaderKey] = useState("");
  const [serverRows, setServerRows] = useState<Awaited<
    ReturnType<typeof api.problemRows>>["rows"] | null>(null);
  const [readError, setReadError] = useState("");

  // An external collector wins where a release stamps one in; the fallback
  // is this deployment's own backend, which serves the same intake.
  const collector = collectorUrl() || getBase();
  // Built once and used for both the preview and the count, so the number
  // beside the button and the text below it can never describe different
  // things.
  const payload = problemReport(CONSOLE_VERSION);
  const report = JSON.stringify(payload, null, 2);
  const unsent = (payload.problems as Problem[]).length;

  return (
    <div className="card" data-screen="22">
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
        Sent to <code>{collector}</code> when the app opens, so the
        people fixing these can see them. Only what the preview below
        shows, and only the part that has not been sent already —
        reopening the app does not send the same failure twice. Nothing
        went anywhere before you answered the notice on first run, and
        this switch is the same answer, changeable whenever you like.
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
              // An external collector goes through the auto-sender's own
              // gate; the backend goes through the app's ordinary wire, so
              // this button is itself the console's door to POST
              // /v1/problems — audit-readable where a raw fetch against a
              // variable address cannot be.
              if (collectorUrl()) {
                setSaid(OUTCOME[await sendProblems(CONSOLE_VERSION)]);
              } else {
                try {
                  await api.reportProblems(payload);
                  markReported(payload);
                  setSaid(OUTCOME["sent"]);
                } catch {
                  setSaid(OUTCOME["failed"]);
                }
              }
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

      {/* The other end of the wire — the retrieval half, for whoever
          operates the server. Ported from the sibling, where a field report
          asked whether these results "get funneled back here to where we
          can make corrections". */}
      <h4>{tr("prob.server", lang)}</h4>
      <p className="muted small">{tr("prob.server.pitch", lang)}</p>
      <div className="row">
        <input type="password" value={readerKey}
               onChange={(e) => setReaderKey(e.target.value)}
               placeholder={tr("prob.key.ph", lang)} style={{ flex: 1 }} />
        <button onClick={async () => {
          setReadError("");
          try {
            setServerRows((await api.problemRows(
              readerKey.trim() || undefined)).rows);
          } catch (e) {
            setServerRows(null);
            setReadError(e instanceof Error ? e.message : String(e));
          }
        }}>{tr("prob.fetch", lang)}</button>
      </div>
      {readError && <p className="small">⚠ {readError}</p>}
      {serverRows && serverRows.length === 0 && (
        <p className="muted small">{tr("prob.none", lang)}</p>
      )}
      {serverRows && serverRows.map((r, i) => (
        <div className="row" key={i}>
          <code>{r.op}</code>
          <span className="muted">{r.status_code}</span>
          <span className="muted">×{r.count}</span>
          <span className="muted">
            {r.source} {r.app_version} · {r.platform} · {r.day}
          </span>
        </div>
      ))}
    </div>
  );
}
