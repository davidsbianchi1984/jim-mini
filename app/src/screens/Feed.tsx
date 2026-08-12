import { useCallback, useEffect, useState } from "react";
import { api, type QrmeFeedItem, type QrmeFeedView } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The feed — QRME's, shown here.
 *
 * `jim/community.py` opens with the argument this screen is another instance
 * of: the forums, the moderation and the languages already exist in QRME, and
 * building a second version of them inside a private health guardian would
 * put somebody's medical timeline and their public watching in one database.
 * So JIM shows a door.
 *
 * Three things this screen does *not* do, and says so on the screen rather
 * than only in a comment:
 *
 *   * it cannot post — there is no write binding, by construction;
 *   * it stores nothing about what was watched;
 *   * it sends no health data across, in either direction.
 *
 * And one thing it does not decide: **`plays`**. QRME sends it, JIM renders
 * it. Footage QRME holds plays; anything on somebody else's platform stays a
 * card until a person presses it, so that scrolling does not announce this
 * reader to a company they never chose. Recomputing that here would be a
 * second copy of a rule that is only safe when there is one.
 */
export function Feed() {
  const { session } = useSession();
  const lang = visitorLang();
  const [view, setView] = useState<QrmeFeedView | null>(null);
  const [items, setItems] = useState<QrmeFeedItem[]>([]);
  const [at, setAt] = useState(0);
  const [playing, setPlaying] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async (cursor?: string) => {
    if (!session.userId || !session.userToken) return;
    setBusy(true); setError(null);
    try {
      const got = await api.qrmeFeed(session.userId, session.userToken, cursor);
      setView(got);
      setItems((prev) => (cursor ? [...prev, ...got.items] : got.items));
    } catch (e) {
      setError((e as Error).message);
    } finally { setBusy(false); }
  }, [session.userId, session.userToken]);

  useEffect(() => { load(); }, [load]);

  function go(delta: number) {
    setAt((i) => {
      const next = Math.max(0, Math.min(items.length - 1, i + delta));
      if (view?.cursor && next >= items.length - 2 && !busy) load(view.cursor);
      return next;
    });
  }

  useEffect(() => {
    function key(e: KeyboardEvent) {
      if (e.key === "ArrowDown") { e.preventDefault(); go(1); }
      if (e.key === "ArrowUp") { e.preventDefault(); go(-1); }
    }
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  });

  const item = items[at];

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("feed.title", lang)}</h2>
        <span className="muted small">{tr("feed.sub", lang)}</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      {/* Whose feed this is, said before any of it is shown. */}
      {view && (
        <div className="card">
          <p className="muted small">{view.note}</p>
          <p className="muted small">{tr("feed.cannotpost", lang)}</p>
          {view.open_in_qrme && (
            <a className="muted small" href={view.open_in_qrme}
               target="_blank" rel="noreferrer">
              {tr("feed.openinqrme", lang)}
            </a>
          )}
        </div>
      )}

      {!busy && items.length === 0 && (
        <div className="card">
          <p className="muted small">{tr("feed.empty", lang)}</p>
        </div>
      )}

      {item && (
        <div className="card"
             onWheel={(e) => { if (Math.abs(e.deltaY) > 24) go(e.deltaY > 0 ? 1 : -1); }}>
          <div className="row">
            <span className="pill">{tr(`feed.kind.${item.kind}`, lang)}</span>
            <span className="muted small" style={{ flex: 1 }}>{item.reason}</span>
            <span className="muted small">{at + 1} / {items.length}</span>
          </div>

          {item.kind === "video" && (
            <>
              <video src={(view?.qrme_url ?? "") + item.src} loop autoPlay
                     muted playsInline
                     style={{ width: "100%", borderRadius: 8 }} />
              <p><strong>{item.title}</strong></p>
              <p className="muted small">{item.note}</p>
            </>
          )}

          {item.kind === "offsite" && (
            <>
              {playing[item.id] ? (
                <iframe title={item.title} src={item.facade?.url}
                        style={{ width: "100%", aspectRatio: "16 / 9",
                                 border: 0, borderRadius: 8 }} />
              ) : (
                <>
                  <p><strong>{item.title}</strong></p>
                  <p className="muted small">{item.facade?.platform_name}</p>
                  <button className="primary"
                          onClick={() => setPlaying((p) => ({ ...p, [item.id]: true }))}>
                    {tr("feed.play", lang)}
                  </button>
                </>
              )}
              <p className="muted small">{item.note}</p>
            </>
          )}

          {item.kind === "room" && (
            <>
              <p><strong>{item.topic || tr("feed.room.untitled", lang)}</strong></p>
              <p className="muted small">
                {item.channel} · {item.people} · {item.display_name}
              </p>
              {/* Before the button. Walking in puts you in the room. */}
              <p className="muted small">{item.entering}</p>
              {view?.qrme_url && item.enter && (
                <a className="primary" href={view.qrme_url + item.enter}
                   target="_blank" rel="noreferrer">
                  {tr("feed.enter", lang)}
                </a>
              )}
            </>
          )}

          {item.kind === "party" && (
            <>
              <p><strong>{item.title || tr("feed.room.untitled", lang)}</strong></p>
              <p className="muted small">
                {item.video?.platform_name}
                {typeof item.people === "number" ? ` · ${item.people}` : ""}
              </p>
              {/* Before the link. Joining puts your name in the room — and
                  it happens in QRME, under the user's own QRME identity,
                  the same rule the room and desk cards run on. */}
              <p className="muted small">{item.joining}</p>
              {view?.qrme_url && item.join && (
                <a className="primary" href={view.qrme_url + item.join}
                   target="_blank" rel="noreferrer">
                  {tr("feed.enter", lang)}
                </a>
              )}
            </>
          )}

          {item.kind === "desk" && (
            <>
              <p><strong>{item.display_name}</strong> — {item.trade}</p>
              <p className="muted small">
                {item.presence}{item.location ? ` · ${item.location}` : ""}
              </p>
              {item.blurb && <p>{item.blurb}</p>}
              <p className="muted small">{item.ringing}</p>
              {/* The bell is rung in QRME, where the desk and the person are. */}
              {view?.qrme_url && item.ring && (
                <a className="primary" href={view.qrme_url + item.ring}
                   target="_blank" rel="noreferrer">
                  {tr("feed.ring", lang)}
                </a>
              )}
              {item.shop && (
                <div className="card">
                  <p><strong>{item.shop.name}</strong></p>
                  {item.shop.offerings.map((o) => (
                    <div key={o.id} className="row">
                      <span style={{ flex: 1 }}>{o.title}</span>
                      <span className="muted small">{o.price} {o.currency}</span>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          <div className="row">
            <button disabled={at === 0} onClick={() => go(-1)}>
              {tr("feed.back", lang)}
            </button>
            <button className="primary" onClick={() => go(1)}>
              {tr("feed.next", lang)}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
