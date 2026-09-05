import { useCallback, useEffect, useState } from "react";
import { api, type UnderwayWindow } from "./api";
import { t as tr, visitorLang } from "./l10n";
import { useSession } from "./store";

/**
 * The task window, always on screen — *which agent is running, which tasks
 * are still running*, asked for twice and answerable until now only by
 * visiting five different screens and knowing which five.
 *
 * A tab on the edge dock beside its sibling `GuardianLights` — it was
 * pinned with a minimize-to-a-dot, which is the tell that it was in the
 * way. Unreachable is a state it shows rather than one it hides in: a
 * failed first fetch renders a tab that retries on press. The lights answer *is
 * anything wrong*; this answers *what is my guardian doing*, and they are
 * different questions with different answers, which is why they are two
 * pinned things rather than one crowded one.
 *
 * Unlike the lights, the gathering is **not** done here. One route hands back
 * the whole window, because four shells each deciding what counts as still
 * running is four chances to disagree invisibly — see jim/underway.py. What
 * this file does is say the closed-set words in the reader's language, which
 * is the half that cannot be done on the server: every running row is built
 * from `kind` and `why` through the table below, never from a sentence the
 * backend wrote. (The errand list at the foot is the exception, and says so
 * where it is drawn.)
 *
 * It opens nothing. Every row names the thing it came from, and the screen
 * that already owns that capability is where you act on it — a window over
 * everything that could also act on everything would quietly be the widest
 * door in the product.
 */

const POLL_MS = 15000;

export function Underway({ open, onToggle }:
                         { open: boolean; onToggle: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const [win, setWin] = useState<UnderwayWindow | null>(null);
  const [unreachable, setUnreachable] = useState(false);

  const load = useCallback(() => {
    const { userId, userToken } = session;
    if (!userId || !userToken) return;
    api.underway(userId, userToken)
      .then((w) => { setWin(w); setUnreachable(false); })
      .catch(() => setUnreachable(true)); // keep any last window
  }, [session.userId, session.userToken]);

  useEffect(() => {
    load();
    const timer = setInterval(load, POLL_MS);
    return () => clearInterval(timer);
  }, [load]);

  if (!win) {
    if (!unreachable || !session.userId) return null;
    return (
      <button className="edge-tab uw-tab uw-dot-off" type="button"
              onClick={load}
              aria-label={tr("und.unreachable", lang)}
              title={tr("und.unreachable", lang)}>
        <span className="uw-glyph" aria-hidden="true">⟳</span>
        <span className="edge-tab-word">{tr("dock.underway", lang)}</span>
      </button>
    );
  }

  return (
    <>
      <button className={"edge-tab uw-tab" + (open ? " on" : "")}
              type="button" aria-expanded={open} onClick={onToggle}
              aria-label={tr("dock.underway", lang)}
              title={tr("dock.underway", lang)}>
        <span className="uw-glyph" aria-hidden="true">⟳</span>
        {/* The count that was the whole of the minimized dot rides the tab
            now, so what the dot said is said without opening anything. */}
        <span className="edge-tab-n">{win.underway.length}</span>
        <span className="edge-tab-word">{tr("dock.underway", lang)}</span>
      </button>
      {open && (
    <div className="edge-panel underway" role="status"
         aria-label={tr("dock.underway", lang)}>
      <div className="uw-head">
        <span className="uw-name">{tr("und.title", lang)}</span>
      </div>

      {/* Stated by the server rather than inferred from an empty list, so
          this shell cannot disagree with the other three about it. */}
      {win.quiet && <div className="uw-quiet">{tr("und.quiet", lang)}</div>}

      {win.underway.map((r, i) => (
        <div className="uw-row" key={`${r.kind}-${r.id ?? r.term ?? i}`}>
          <span className="uw-kind">{tr(`und.kind.${r.kind}`, lang)}</span>
          {/* One of the product's own vocabulary words — a monitor's name, a
              call's route. `term` falls back to itself when the table has no
              row, which is a visible gap rather than a confident error. */}
          {r.term && <span className="uw-term">{tr(r.term, lang)}</span>}
          {/* What the person wrote, printed as they wrote it. */}
          {r.words && <span className="uw-words">{r.words}</span>}
          {/* Only said where it adds something. `open` and `on` restate the
              kind; the other four are news. */}
          {r.why !== "open" && r.why !== "on" && (
            <span className="uw-why">{tr(`und.why.${r.why}`, lang)}</span>
          )}
        </div>
      ))}

      {/* Finished, not running — which is why it is a list of its own below
          the rows rather than more rows among them.

          These two strings are the ledger's own and arrive composed, unlike
          the rows above: `pipeline.curriculum` writes an errand's topic and
          its reason in English. That is the existing shape of that data —
          the Coach screen prints the same two fields the same way — and this
          window neither improves nor worsens it. Worth knowing it is there:
          it is the one part of this panel a translated reader still meets in
          English. */}
      {win.today.length > 0 && (
        <div className="uw-today">
          <span className="uw-name">{tr("und.today", lang)}</span>
          {win.today.map((e) => (
            <div className="uw-row" key={e.id}>
              <span className="uw-words">{e.topic}</span>
              <span className="uw-why">{e.why}</span>
            </div>
          ))}
        </div>
      )}

      {/* What it has spent today against what it may. Shown only where the
          pass is allowed at all: a budget line on an account that never
          permitted unattended study is an answer to a question nobody
          asked. */}
      {win.spend.permitted && (
        <div className="uw-foot">
          {tr("und.spend", lang)
            .replace("{n}", String(win.spend.spent_today))
            .replace("{daily}", String(win.spend.daily))}
        </div>
      )}
    </div>
      )}
    </>
  );
}
