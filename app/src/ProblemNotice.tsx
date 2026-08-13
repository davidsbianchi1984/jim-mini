import { useState } from "react";
import { CONSOLE_VERSION } from "./api";
import {
  answerNotice, noticeAnswered, problemReport, sendProblems,
} from "./errors";

/**
 * Told once, before anything is sent.
 *
 * Reports go automatically, which is the right default for a diagnostic that
 * carries nothing of anybody's — but "you can turn it off" is only a real
 * choice if it can be made *before* the first report rather than discovered
 * afterwards in a settings screen nobody opened. So `sendProblems` refuses to
 * send until this has been answered, and this is what answers it.
 *
 * It shows the payload rather than describing it. A notice that summarised
 * the contents in prose would be asking for agreement to a claim; showing the
 * object is asking for agreement to the thing itself, and the object comes
 * from the same function that posts it, so the two cannot drift apart.
 *
 * This used to appear only where an external collector was stamped into the
 * build. Reports now fall back to the deployment's own backend — the same
 * server every other request already reaches — so there is always somewhere
 * for them to go, and the question is always worth asking once.
 */
export function ProblemNotice() {
  const [answered, setAnswered] = useState(noticeAnswered);
  const [showing, setShowing] = useState(false);

  if (answered) return null;

  const report = problemReport(CONSOLE_VERSION);

  const decide = (send: boolean) => {
    answerNotice(send);
    setAnswered(true);
    // Sent now rather than next launch: the person just said yes, and making
    // them reopen the app to act on it would be a strange kind of respect.
    if (send) sendProblems(CONSOLE_VERSION);
  };

  return (
    <div className="problem-notice" role="region"
         aria-label="Error reporting">
      <p>
        <strong>When something in this app fails, we would like to know.</strong>{" "}
        It sends a list of what broke — the operation and the error code, like{" "}
        <code>POST /profiles/&#123;id&#125;/chat → 500</code>. Never the error
        message, never who you are, never anything you typed or stored.
        Nothing has been sent yet, and nothing will be until you answer. You
        can change your mind later: the settings panel that lists these
        reports has the same switch.
      </p>
      <div className="row">
        <button className="pn-yes" onClick={() => decide(true)}>
          That&apos;s fine
        </button>
        <button onClick={() => decide(false)}>No thanks</button>
        <button onClick={() => setShowing(!showing)}>
          {showing ? "Hide" : "Show me exactly what would be sent"}
        </button>
      </div>
      {showing && (
        <pre className="small">{JSON.stringify(report, null, 2)}</pre>
      )}
    </div>
  );
}
