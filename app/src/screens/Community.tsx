import { useEffect, useState } from "react";
import { api, type CommunityView } from "../api";
import { useSession } from "../store";

/**
 * The community door — FIG. 2 boxes 222–226 of the filing.
 *
 * P001's spec describes forums, local events and community interaction for
 * JIM users; all of it lives in QRME, where the moderation and the languages
 * already are. So this screen is a door and says so: rooms and places from
 * the tandem, opened in QRME under the user's own QRME identity, with the
 * health data staying on this side of the wall.
 */
export function Community() {
  const { session } = useSession();
  const [view, setView] = useState<CommunityView | null>(null);
  const [place, setPlace] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function load(locality?: string) {
    if (!session.userId || !session.userToken) return;
    setBusy(true); setError(null);
    try {
      setView(await api.community(session.userId, session.userToken, locality));
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  useEffect(() => { load(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [session.userId]);

  async function open(roomId: string, url: string | null) {
    if (!session.userId || !session.userToken) return;
    // The fact only — never anything from inside the room.
    api.communityVisit(session.userId, roomId, session.userToken).catch(() => {});
    if (url) window.open(url, "_blank");
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Community</h2>
        <span className="muted small">forums, rooms and local events — in QRME</span>
      </header>

      {error && (
        <div className="card">
          <div className="error">⚠ {error}</div>
          <p className="muted small">
            Community lives in QRME. Point this Guardian at your QRME
            deployment (<code>JIM_QRME_URL</code>) and the doors appear here.
          </p>
        </div>
      )}

      {view && (<>
        <div className="card">
          <h3>Where this happens</h3>
          <p>{view.note}</p>
          <ul className="refs">
            <li>Nothing from a room is copied into JIM.</li>
            <li>Nothing is ever posted on your behalf.</li>
            <li>No health data crosses over.</li>
          </ul>
          <div className="muted small">
            Rooms you can read in: <b>{view.language}</b>
            {view.qrme_url ? <> · {view.qrme_url}</> : null}
          </div>
        </div>

        <div className="card">
          <h3>Rooms &amp; forums</h3>
          {view.rooms.length === 0 && (
            <p className="muted small">
              No rooms open right now. Start one in QRME — Rooms → new topic.
            </p>
          )}
          {view.rooms.map((room) => (
            <div className="spec-row" key={room.id}>
              <div>
                <b>{room.topic}</b>
                <div className="muted small">
                  {room.channel} · {room.participants} here
                </div>
              </div>
              <button onClick={() => open(room.id, room.url)}>Open in QRME</button>
            </div>
          ))}
        </div>

        <div className="card">
          <h3>Local events</h3>
          <div className="row">
            <label>Filter by place
              <input value={place} placeholder="e.g. Bend"
                     onChange={(e) => setPlace(e.target.value)} /></label>
          </div>
          <button onClick={() => load(place.trim() || undefined)} disabled={busy}>
            {busy ? "Looking…" : "Show places"}
          </button>
          <ul className="refs">
            {view.places.map((p) => (
              <li key={p.locality}>{p.locality} <span className="muted small">
                ({p.listings} listed)</span></li>
            ))}
          </ul>
          {view.places.length === 0 && (
            <p className="muted small">Nothing claimed for that place yet.</p>
          )}
        </div>
      </>)}
    </div>
  );
}
