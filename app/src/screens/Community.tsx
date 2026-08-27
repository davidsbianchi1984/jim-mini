import { useEffect, useState } from "react";
import { api, type CircleHomepage, type CircleMessage, type CircleView,
         type CommunityView, type ShoppingView } from "../api";
import { t as tr, visitorLang } from "../l10n";
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
  const lang = visitorLang();
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
        <h2>{tr("cmy.title", lang)}</h2>
        <span className="muted small">{tr("cmy.sub", lang)}</span>
      </header>

      {error && (
        <div className="card">
          <div className="error">⚠ {error}</div>
          <p className="muted small">{tr("cmy.unset", lang)}</p>
        </div>
      )}

      {view && (<>
        <div className="card">
          <h3>{tr("cmy.where", lang)}</h3>
          <p>{view.note}</p>
          <ul className="refs">
            <li>{tr("cmy.nocopy", lang)}</li>
            <li>{tr("cmy.nopost", lang)}</li>
            <li>{tr("cmy.nohealth", lang)}</li>
          </ul>
          <div className="muted small">
            {tr("cmy.lang", lang)} <b>{view.language}</b>
            {view.qrme_url ? <> · {view.qrme_url}</> : null}
          </div>
        </div>

        <div className="card">
          <h3>{tr("cmy.rooms", lang)}</h3>
          {view.rooms.length === 0 && (
            <p className="muted small">
              {tr("cmy.rooms.none", lang)}
            </p>
          )}
          {view.rooms.map((room) => (
            <div className="spec-row" key={room.id}>
              <div>
                <b>{room.topic}</b>
                <div className="muted small">
                  {tr("cmy.rooms.here", lang)
                    .replace("{channel}", String(room.channel))
                    .replace("{n}", String(room.participants))}
                </div>
              </div>
              <button onClick={() => open(room.id, room.url)}>{tr("cmy.rooms.open", lang)}</button>
            </div>
          ))}
        </div>

        <div className="card">
          <h3>{tr("cmy.events", lang)}</h3>
          <div className="row">
            <label>{tr("cmy.events.filter", lang)}
              <input value={place} placeholder={tr("cmy.events.ph", lang)}
                     onChange={(e) => setPlace(e.target.value)} /></label>
          </div>
          <button onClick={() => load(place.trim() || undefined)} disabled={busy}>
            {busy ? tr("cmy.looking", lang) : tr("cmy.show", lang)}
          </button>
          <ul className="refs">
            {view.places.map((p) => (
              <li key={p.locality}>{p.locality} <span className="muted small">
                {tr("cmy.events.listed", lang)
                  .replace("{n}", String(p.listings))}</span></li>
            ))}
          </ul>
          {view.places.length === 0 && (
            <p className="muted small">{tr("cmy.events.none", lang)}</p>
          )}
        </div>
      </>)}
      <ShoppingShelf />
      <CircleCard />
    </div>
  );
}

// The shops shelf: QRME's storefronts, bought from as this user's own
// interactor, with the receipt history held in JIM. Every visible string
// below comes from the view's `labels` — composed server-side in the
// reader's language — because this console has no translation table and
// its English backlog is a ratchet that only shrinks. Until the view
// loads there is nothing to say, so nothing is said.
function ShoppingShelf() {
  const { session } = useSession();
  const [view, setView] = useState<ShoppingView | null>(null);
  const [shopId, setShopId] = useState("");
  const [offeringId, setOfferingId] = useState("");
  const [qty, setQty] = useState("1");
  const [note, setNote] = useState<string | null>(null);

  async function load() {
    if (!session.userId || !session.userToken) return;
    try {
      setView(await api.shoppingView(session.userId, session.userToken));
    } catch { /* the shelf stays empty */ }
  }
  useEffect(() => { load(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [session.userId]);

  if (!view) return null;
  const L = view.labels;

  async function order() {
    if (!session.userId || !session.userToken) return;
    setNote(null);
    try {
      const placed = await api.shoppingOrder(session.userId,
        { shop_id: shopId.trim(), offering_id: offeringId.trim(),
          quantity: Number(qty) || 1 }, session.userToken);
      setNote(placed.status);
      load();
    } catch (e) { setNote((e as Error).message); }
  }

  async function cancel(qrmeOrderId: string) {
    if (!session.userId || !session.userToken) return;
    try {
      await api.shoppingCancel(session.userId, qrmeOrderId, session.userToken);
      load();
    } catch (e) { setNote((e as Error).message); }
  }

  return (
    <div className="card">
      <h3>{L.title}</h3>
      <p className="muted small">{view.note}</p>
      {view.shops.map((s) => (
        <div key={s.id} className="row" style={{ justifyContent: "space-between" }}>
          <span>{s.name} · <span className="muted small">
            {L.seller}: {s.seller}{s.tag ? ` · ${s.tag}` : ""} ·{" "}
            {L.offerings}: {s.offerings}</span></span>
          <button onClick={() => setShopId(s.id)}>{L.browse}</button>
        </div>
      ))}
      <div className="row">
        <label>{L.title}
          <input value={shopId} onChange={(e) => setShopId(e.target.value)} />
        </label>
        <label>{L.offerings}
          <input value={offeringId}
                 onChange={(e) => setOfferingId(e.target.value)} />
        </label>
        <label>{L.quantity}
          <input value={qty} onChange={(e) => setQty(e.target.value)} />
        </label>
        <button disabled={!shopId.trim() || !offeringId.trim()}
                onClick={order}>{L.order}</button>
      </div>
      {view.receipts.length > 0 && <h3>{L.receipts}</h3>}
      {view.receipts.map((r) => (
        <div key={r.id} className="row" style={{ justifyContent: "space-between" }}>
          <span>{r.title} · {r.amount} {r.currency} ·{" "}
            <span className="muted small">{r.status}</span></span>
          {r.status === "placed" && (
            <button onClick={() => cancel(r.qrme_order_id)}>{L.cancel}</button>
          )}
        </div>
      ))}
      {note && <div className="muted small">{note}</div>}
    </div>
  );
}

// Your circle: the people on this deployment you let in — contacts by
// mutual invitation, messages that never leave the house, the switches
// that govern both, and a homepage sandbox like the old MySpace. Every
// visible string comes from the view's `labels`, composed server-side in
// the reader's language, for the same reason the shelf above does it.
function CircleCard() {
  const { session } = useSession();
  const [view, setView] = useState<CircleView | null>(null);
  const [inviteId, setInviteId] = useState("");
  const [withId, setWithId] = useState("");
  const [thread, setThread] = useState<CircleMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [headline, setHeadline] = useState("");
  const [about, setAbout] = useState("");
  const [bg, setBg] = useState("#10251c");
  const [accent, setAccent] = useState("#2fbf8f");
  const [lookId, setLookId] = useState("");
  const [looking, setLooking] = useState<CircleHomepage | null>(null);
  const [note, setNote] = useState<string | null>(null);

  async function load() {
    if (!session.userId || !session.userToken) return;
    try {
      const v = await api.circleView(session.userId, session.userToken);
      setView(v);
      setHeadline(v.homepage.headline); setAbout(v.homepage.about);
      setBg(v.homepage.theme.bg); setAccent(v.homepage.theme.accent);
    } catch { /* the card stays closed */ }
  }
  useEffect(() => { load(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [session.userId]);

  if (!view) return null;
  const L = view.labels;

  const act = (op: () => Promise<unknown>) => async () => {
    setNote(null);
    try { await op(); await load(); }
    catch (e) { setNote((e as Error).message); }
  };

  const invite = act(() => api.circleInvite(session.userId!,
    inviteId.trim(), session.userToken!));
  const save = act(() => api.circleEditHomepage(session.userId!,
    { headline, about, theme: { bg, accent } }, session.userToken!));
  const flip = (feature: string, enabled: boolean) => act(() =>
    api.circleFeature(session.userId!, { feature, enabled },
      session.userToken!))();

  async function open(other: string) {
    setWithId(other); setNote(null);
    try {
      const box = await api.circleMessages(session.userId!,
        session.userToken!, other);
      setThread(box.messages ?? []);
    } catch (e) { setNote((e as Error).message); }
  }

  async function send() {
    if (!withId.trim() || !draft.trim()) return;
    setNote(null);
    try {
      await api.circleSend(session.userId!,
        { to: withId.trim(), body: draft }, session.userToken!);
      setDraft("");
      await open(withId.trim());
      await load();
    } catch (e) { setNote((e as Error).message); }
  }

  const look = act(async () =>
    setLooking(await api.circleHomepage(session.userId!, lookId.trim(),
      session.userToken!)));

  /** Open a neighbour's page from their row, rather than by typing their id.
   *
   *  The box below still works and is still the only way to reach somebody
   *  whose row is not on this screen. But a contact you already have listed,
   *  by name, should not have to be re-identified by hand to be looked at —
   *  and the id is a UUID, so "type it in" meant "copy it from somewhere".
   *
   *      asked     the friends picture should open their profile homepage
   *      mattered  the only way in was a text box asking for their id
   *
   *  It sets `lookId` as well as fetching, so the box reflects whose page is
   *  on screen instead of contradicting it. */
  const visit = (otherId: string) => act(async () => {
    setLookId(otherId);
    setLooking(await api.circleHomepage(session.userId!, otherId,
      session.userToken!));
  })();

  const leave = (other: string) => act(() => api.circleLeave(
    session.userId!, other, session.userToken!))();

  return (
    <div className="card">
      <h3>{L.title}</h3>
      <p className="muted small">{view.note}</p>

      {view.circle.contacts.map((p) => (
        <div key={p.user_id} className="row"
             style={{ justifyContent: "space-between" }}>
          <button className="linkish neighbour-name"
                  onClick={() => visit(p.user_id)}>
            {p.display_name || p.user_id}
          </button>
          <span>
            <button onClick={() => open(p.user_id)}>{L.open}</button>{" "}
            <button onClick={() => leave(p.user_id)}>{L.leave}</button>
          </span>
        </div>
      ))}
      {view.circle.invited_me.map((p) => (
        <div key={p.user_id} className="row"
             style={{ justifyContent: "space-between" }}>
          <span>{p.display_name || p.user_id} ·{" "}
            <span className="muted small">{L.invited_me}</span></span>
          <button onClick={act(() => api.circleInvite(session.userId!,
            p.user_id, session.userToken!))}>{L.invite}</button>
        </div>
      ))}
      {view.circle.awaiting.map((p) => (
        <div key={p.user_id} className="muted small">
          {p.display_name || p.user_id} · {L.awaiting}</div>
      ))}
      <div className="row">
        <label>{L.invite}
          <input value={inviteId}
                 onChange={(e) => setInviteId(e.target.value)} />
        </label>
        <button disabled={!inviteId.trim()} onClick={invite}>
          {L.invite}</button>
      </div>

      <h3>{L.messages}</h3>
      {view.threads.map((t) => (
        <div key={t.other_id} className="row"
             style={{ justifyContent: "space-between" }}>
          <span>{t.other_name || t.other_id} ·{" "}
            <span className="muted small">{t.messages_count}</span></span>
          <button onClick={() => open(t.other_id)}>{L.open}</button>
        </div>
      ))}
      <div className="row">
        <label>{L.to}
          <input value={withId} onChange={(e) => setWithId(e.target.value)} />
        </label>
      </div>
      {thread.map((m) => (
        <div key={m.id} className="muted small">
          {m.sender_id === session.userId ? `→ ${m.body}` : `← ${m.body}`}
        </div>
      ))}
      <div className="voice-row">
        <input value={draft} onChange={(e) => setDraft(e.target.value)}
               onKeyDown={(e) => e.key === "Enter" && send()} />
        <button disabled={!draft.trim() || !withId.trim()}
                onClick={send}>{L.send}</button>
      </div>

      <h3>{L.switches}</h3>
      {Object.entries(view.features).map(([feature, enabled]) => (
        <label key={feature} className="row">
          <input type="checkbox" checked={enabled}
                 onChange={(e) => flip(feature, e.target.checked)} />
          {feature === "messaging" ? L.sw_messaging : L.sw_homepage}
        </label>
      ))}

      <h3>{L.page}</h3>
      <div style={{ background: bg, borderRadius: 8, padding: 12,
                    borderLeft: `4px solid ${accent}` }}>
        <label>{L.headline}
          <input value={headline}
                 onChange={(e) => setHeadline(e.target.value)} />
        </label>
        <label>{L.about}
          <textarea rows={3} value={about}
                    onChange={(e) => setAbout(e.target.value)} />
        </label>
        <div className="row">
          <label>{L.background}
            <input value={bg} onChange={(e) => setBg(e.target.value)} />
          </label>
          <label>{L.accent}
            <input value={accent}
                   onChange={(e) => setAccent(e.target.value)} />
          </label>
        </div>
        <button className="primary" onClick={save}>{L.save}</button>
      </div>

      <h3>{L.visit}</h3>
      <div className="row">
        <label>{L.visit_id}
          <input value={lookId} onChange={(e) => setLookId(e.target.value)} />
        </label>
        <button disabled={!lookId.trim()} onClick={look}>{L.open}</button>
      </div>
      {looking && (
        <div style={{ background: looking.theme.bg, borderRadius: 8,
                      padding: 12,
                      borderLeft: `4px solid ${looking.theme.accent}` }}>
          <h3 style={{ color: looking.theme.accent }}>
            {looking.display_name} — {looking.headline}</h3>
          <p style={{ whiteSpace: "pre-wrap" }}>{looking.about}</p>
          <ul className="refs">
            {looking.links.map((l) => (
              <li key={l.url}><a href={l.url} target="_blank"
                                 rel="noreferrer">{l.label}</a></li>
            ))}
          </ul>
          {looking.top_friends.length > 0 && (
            <p className="muted small">{L.top}:{" "}
              {looking.top_friends.map((t) => t.display_name)
                .join(" · ")}</p>
          )}
        </div>
      )}

      {note && <div className="muted small">{note}</div>}
    </div>
  );
}
