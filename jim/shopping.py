"""Shopping through the tandem: QRME's shops, reached as the user.

The shops live on QRME — businesses and people selling goods and services,
standalone storefronts with no desk semantics. JIM's part is the *buyer's*
side, and it is deliberately thin:

1. **Browsing is anonymous and quiet.** The catalog is read over the same
   public routes a stranger gets; nothing about the user crosses to look.
   An unreachable tandem is an empty shelf, never an error page.
2. **Ordering is the interactor's act.** The order is signed with the same
   per-user QRME interactor the tandem already maintains — one identity to
   revoke, exactly as `docs/tandem.md` promises. No name, no address, no
   payment detail crosses; QRME sees the interactor and the offering.
3. **The history is held here.** What this user bought is their own
   record, in their own JIM, listed from a local table — QRME is never
   asked "what has this person bought" on their behalf, because that
   question answered remotely is a profile of them held elsewhere.
4. **Labels ride the view.** The console renders what the server hands it,
   in the reader's language, because the console has no translation table
   and its English backlog is a ratchet that only shrinks.
"""

from __future__ import annotations

from . import db, guardian, i18n


class ShoppingError(ValueError):
    pass


def browse(qrme, tag: str | None = None) -> list[dict]:
    """Every open QRME shop. Empty on any failure — a shelf, not an alarm."""
    if qrme is None:
        return []
    try:
        return qrme.shops(tag)
    except Exception:
        return []


def shop(qrme, shop_id: str) -> dict | None:
    if qrme is None:
        return None
    try:
        return qrme.shop(shop_id)
    except Exception:
        return None


def order(user_id: str, user: dict, shop_id: str, offering_id: str,
          quantity: int, qrme) -> dict:
    """Place the order as this user's interactor, and keep the receipt here.

    The receipt row stores what the user needs to recognise the purchase —
    title, amount, status — and the QRME order id for the one legitimate
    follow-up (cancelling while `placed`). Nothing else is kept, because a
    purchase history is exactly the kind of quiet profile rule 3 exists to
    keep at home.
    """
    if qrme is None:
        raise ShoppingError(
            "the tandem is not configured; shops live on QRME and there is "
            "no QRME to reach")
    interactor_id = guardian.interactor_for(user_id, user, qrme)
    conn = db.connect()
    token = conn.execute(
        "SELECT qrme_interactor_token FROM tandem_links WHERE user_id=?",
        (user_id,)).fetchone()["qrme_interactor_token"]
    placed = qrme.place_shop_order(shop_id, offering_id, interactor_id,
                                   quantity, token)
    if placed is None:
        raise ShoppingError("the shop refused the order or could not be "
                            "reached; nothing was placed")
    conn.execute(
        "INSERT INTO shop_receipts (id, user_id, qrme_order_id, shop_id,"
        " title, amount, currency, status, placed_at)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (db.new_id("rcp"), user_id, placed["id"], shop_id,
         placed.get("title") or "", float(placed.get("amount") or 0),
         placed.get("currency") or "USD", placed.get("status") or "placed",
         db.utcnow()))
    conn.commit()
    return placed


def cancel(user_id: str, qrme_order_id: str, qrme) -> dict:
    """The buyer's exit, while the seller has not yet moved. Signed with the
    same interactor token the order was placed with."""
    conn = db.connect()
    receipt = conn.execute(
        "SELECT * FROM shop_receipts WHERE user_id=? AND qrme_order_id=?",
        (user_id, qrme_order_id)).fetchone()
    if receipt is None:
        raise ShoppingError("no such order in your history")
    link = conn.execute(
        "SELECT * FROM tandem_links WHERE user_id=?", (user_id,)).fetchone()
    if qrme is None or link is None or not link["qrme_interactor_token"]:
        raise ShoppingError("the tandem is not reachable to carry the "
                            "cancellation")
    out = qrme.advance_shop_order(receipt["shop_id"], qrme_order_id,
                                  "buyer", "cancelled",
                                  link["qrme_interactor_token"])
    if out is None:
        raise ShoppingError("the shop refused the cancellation")
    conn.execute(
        "UPDATE shop_receipts SET status='cancelled' WHERE user_id=? AND"
        " qrme_order_id=?", (user_id, qrme_order_id))
    conn.commit()
    return out


def receipts(user_id: str) -> list[dict]:
    return [dict(r) for r in db.connect().execute(
        "SELECT * FROM shop_receipts WHERE user_id=? ORDER BY placed_at",
        (user_id,)).fetchall()]


def view(user_id: str, lang: str, qrme, tag: str | None = None) -> dict:
    """Everything the Shopping shelf renders — labels included."""
    return {
        "shops": browse(qrme, tag),
        "receipts": receipts(user_id),
        "labels": i18n.shop_labels(lang),
        "note": i18n.shop_text("held_here", lang),
    }
