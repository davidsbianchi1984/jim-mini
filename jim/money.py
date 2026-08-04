"""The money guardian: accounts, balances, and a mandate — proactively.

## The finding

JIM already watched money the way it watches sleep: consented spending
events fill budget tallies, `life._budget_insights` warns at 80% and 100%
of a plan, `forecast_spending` projects the month, and the finance coach
can hand a question to Marcus Bell through the tandem. What it could not do
was *hold* anything: there was nowhere to put an account — checking,
savings, brokerage, crypto — so there was no balance to watch, no cushion
to warn about, no savings goal to coach toward, and nothing to invest.

    asked     is spending watched
    mattered  is the money watched

## The four rules that shape this module

1. **Credentials only ever live in the vault.** An account number, routing
   number or exchange API key is exactly the private data the PDI tandem
   exists for. `add_account` seals them there and keeps locally only what a
   screen may show: institution, kind, a label, the last four digits. On a
   plan with no vault the registration is *refused* — storing a routing
   number in the clear is not a degraded mode, it is the thing this suite
   is built to never do.

2. **Warnings ride the existing proactive ladder.** A low balance produces
   a `guardian` event with ``severity="checkin"`` and an insight — the same
   machinery as a drift band. Money is never an emergency escalation:
   nothing here rings an emergency contact, because an overdraft is not a
   collapse, and a ladder that cried wolf about rent would be ignored about
   breathing.

3. **The mandate is a handover, not a default.** "Let JIM invest for me" is
   off until the owner writes it down: enabled, a per-order cap, a monthly
   cap, the asset classes allowed, and a scope in words. It is Pro-gated
   (`synthetic_agents` — delegated work is delegated work), revocable at a
   stroke, and every order JIM proposes under it is logged. **Orders are
   proposals**: this deployment has no brokerage connector, and the order
   record says `proposed` rather than pretending an execution happened.
   When a connector exists it executes within the same caps; nothing about
   the consent shape changes.

4. **A warning carries its doors.** Every money warning names where help
   is: the finance coach, the AI specialist through the tandem (Marcus
   Bell), and — when the tandem is up — real people at desks, near the
   user's locality or across the map. Bridging the gap is the point of
   noticing it.
"""

from __future__ import annotations

import json

from . import db, i18n

#: Balance below this fraction of the monthly budget (or below the absolute
#: floor) is "running low". Deliberately generous — a warning that fires on
#: every grocery run teaches the person to ignore the one about rent.
LOW_FRACTION = 0.25
LOW_FLOOR = 100.0

ACCOUNT_KINDS = ("checking", "savings", "brokerage", "crypto")

#: What the mandate may touch, by name. `crypto` is deliberately present —
#: the owner decides, not the module — and deliberately not a default.
ASSET_CLASSES = ("index_funds", "bonds", "stocks", "crypto")


class MoneyError(ValueError):
    """A money operation that cannot stand."""


# --------------------------------------------------------------------------
# accounts

def add_account(user_id: str, kind: str, institution: str, label: str,
                account_number: str | None, routing_number: str | None,
                api_key: str | None, pdi) -> dict:
    """Register an account. The numbers go to the vault or nowhere.

    ``pdi`` is the *user's* vault (`api._vault`), None on an open plan —
    and None refuses, because rule 1 is the module's spine.
    """
    if kind not in ACCOUNT_KINDS:
        raise MoneyError(
            f"unknown account kind {kind!r}; expected one of "
            f"{', '.join(ACCOUNT_KINDS)}")
    if not (institution or "").strip():
        raise MoneyError("name the institution — a bank, a broker, an "
                         "exchange")
    secrets = {k: v for k, v in (("account_number", account_number),
                                 ("routing_number", routing_number),
                                 ("api_key", api_key)) if v}
    if secrets and pdi is None:
        raise MoneyError(
            "account credentials are private data and only ever live in "
            "the vault; this plan has no vault, so they were not stored — "
            "upgrade to a private plan or register the account without "
            "numbers")

    account_id = db.new_id("mac")
    vault_key = None
    if secrets:
        from . import life
        vault_key = life.vault_store(
            pdi, user_id, f"jim/{user_id}/money/{account_id}", secrets)

    last4 = (account_number or "")[-4:] or None
    conn = db.connect()
    conn.execute(
        "INSERT INTO money_accounts (id, user_id, kind, institution, label,"
        " last4, vault_key, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (account_id, user_id, kind, institution.strip(),
         (label or institution).strip(), last4, vault_key, db.utcnow()))
    conn.commit()
    return _account(account_id)


def _account(account_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM money_accounts WHERE id=?", (account_id,)).fetchone()
    if row is None:
        raise MoneyError("no such account")
    out = dict(row)
    # The key proves custody without being the secret; the numbers never
    # come back through this module at all.
    out["credentials"] = "vaulted" if out.pop("vault_key") else "none"
    return out


def accounts_for(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM money_accounts WHERE user_id=? ORDER BY created_at",
        (user_id,)).fetchall()
    return [_account(r["id"]) for r in rows]


# --------------------------------------------------------------------------
# observations → the proactive ladder

def observe(user_id: str, account_id: str, balance: float | None,
            note: str | None, lang: str, pdi=None, qrme=None) -> dict:
    """A balance reading against an account, and everything it wakes.

    The reading is the sensor; this is the interpreter. Low balance and
    savings progress are computed here, warnings are written as guardian
    events + insights (severity ``checkin`` — rule 2), the mandate engine
    gets a look (rule 3), and any warning carries its doors (rule 4).
    """
    account = _account(account_id)
    if account["user_id"] != user_id:
        raise MoneyError("that account belongs to somebody else")

    conn = db.connect()
    if balance is not None:
        conn.execute(
            "INSERT INTO money_balances (id, account_id, balance, note,"
            " observed_at) VALUES (?,?,?,?,?)",
            (db.new_id("mbl"), account_id, float(balance), note,
             db.utcnow()))
        conn.commit()

    warnings = check(user_id, lang, pdi=pdi, qrme=qrme)
    proposed = _mandate_engine(user_id, lang)
    return {"account": _account(account_id), "recorded": balance is not None,
            "warnings": warnings, "orders_proposed": proposed}


def _latest_balances(user_id: str) -> dict[str, float]:
    conn = db.connect()
    out: dict[str, float] = {}
    for acc in conn.execute(
            "SELECT id FROM money_accounts WHERE user_id=?",
            (user_id,)).fetchall():
        row = conn.execute(
            "SELECT balance FROM money_balances WHERE account_id=?"
            " ORDER BY observed_at DESC LIMIT 1", (acc["id"],)).fetchone()
        if row is not None:
            out[acc["id"]] = row["balance"]
    return out


def _monthly_budget_total(user_id: str) -> float:
    row = db.connect().execute(
        "SELECT COALESCE(SUM(monthly_limit),0) AS s FROM budgets"
        " WHERE user_id=?", (user_id,)).fetchone()
    return float(row["s"] or 0)


def check(user_id: str, lang: str, pdi=None, qrme=None) -> list[dict]:
    """The proactive pass. Called on every observation; cheap enough to be.

    Returns the warnings raised *this* pass. Each is also written as a
    guardian event and an insight, so the Home feed and the events log say
    the same thing the response does.
    """
    from . import guardian, life

    warnings: list[dict] = []
    balances = _latest_balances(user_id)
    liquid = sum(v for aid, v in balances.items()
                 if _account(aid)["kind"] in ("checking", "savings"))
    budget = _monthly_budget_total(user_id)
    floor = max(LOW_FLOOR, budget * LOW_FRACTION) if budget else LOW_FLOOR

    if balances and liquid < floor:
        doors = _doors(user_id, qrme)
        message = i18n.money_text("low_balance", lang).format(
            balance=f"{liquid:.0f}", floor=f"{floor:.0f}")
        warnings.append({"kind": "low_balance", "message": message,
                         "doors": doors})
        guardian._event(user_id, "money_low", condition="financial_stress",
                        severity="checkin",
                        detail={"liquid": liquid, "floor": floor},
                        pdi=pdi, vault_scope="money")
        life._insight(user_id, "alert", message, area="finance",
                      source="money")

    goal = savings_goal(user_id)
    if goal and balances:
        saved = sum(v for aid, v in balances.items()
                    if _account(aid)["kind"] == "savings")
        if saved >= goal["goal"] and not goal.get("reached_at"):
            conn = db.connect()
            conn.execute(
                "UPDATE savings_goals SET reached_at=? WHERE user_id=?",
                (db.utcnow(), user_id))
            conn.commit()
            message = i18n.money_text("goal_reached", lang).format(
                goal=f"{goal['goal']:.0f}")
            warnings.append({"kind": "goal_reached", "message": message})
            life._insight(user_id, "suggestion", message, area="finance",
                          source="money")
    return warnings


def _doors(user_id: str, qrme) -> dict:
    """Where help is, attached to the warning that makes it relevant.

    The coach and the tandem specialist are always doors. Real people at
    desks are listed when the tandem is up — near the user's locality when
    one is set, and across the map when not.
    """
    out: dict = {
        "coach": "/coach/{user_id} (area: finance)",
        "specialist": None,
        "desks": [],
    }
    from . import specialists
    spec = specialists.for_area("finance")
    if spec is not None and spec.get("qrme_profile_id"):
        out["specialist"] = {"label": spec.get("label"),
                             "route": "/coach/{user_id}/specialist"}
    if qrme is not None:
        try:
            desks = qrme.desks()
            out["desks"] = [
                {"desk_id": d.get("id"), "name": d.get("display_name"),
                 "trade": d.get("trade"), "location": d.get("location")}
                for d in desks
                if "finan" in (d.get("trade") or "").lower()
                or "money" in (d.get("trade") or "").lower()
            ][:5]
        except Exception:
            out["desks"] = []
    return out


# --------------------------------------------------------------------------
# savings

def set_savings(user_id: str, goal: float, note: str | None) -> dict:
    if goal <= 0:
        raise MoneyError("a savings goal is a positive number")
    conn = db.connect()
    conn.execute(
        "INSERT INTO savings_goals (user_id, goal, note, set_at, reached_at)"
        " VALUES (?,?,?,?,NULL) ON CONFLICT (user_id) DO UPDATE SET"
        " goal=excluded.goal, note=excluded.note, set_at=excluded.set_at,"
        " reached_at=NULL",
        (user_id, float(goal), note, db.utcnow()))
    conn.commit()
    return savings_goal(user_id)


def savings_goal(user_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM savings_goals WHERE user_id=?", (user_id,)).fetchone()
    return dict(row) if row else None


# --------------------------------------------------------------------------
# the mandate

def set_mandate(user_id: str, enabled: bool, cap_per_order: float,
                monthly_cap: float, asset_classes: list[str],
                scope: str) -> dict:
    """The handover, written down. Rule 3 in full: nothing about this is
    implicit, and disabling it is one call with no questions asked."""
    if enabled:
        if not (scope or "").strip():
            raise MoneyError(
                "a mandate needs a written scope: what JIM may do with your "
                "money, in words you would show your own accountant")
        if cap_per_order <= 0 or monthly_cap <= 0:
            raise MoneyError("a mandate needs positive caps — per order and "
                             "per month")
        bad = [a for a in asset_classes if a not in ASSET_CLASSES]
        if bad:
            raise MoneyError(
                f"unknown asset class(es): {', '.join(bad)}; expected among "
                f"{', '.join(ASSET_CLASSES)}")
        if not asset_classes:
            raise MoneyError("name at least one asset class the mandate "
                             "covers")
    conn = db.connect()
    conn.execute(
        "INSERT INTO money_mandates (user_id, enabled, cap_per_order,"
        " monthly_cap, asset_classes, scope, updated_at)"
        " VALUES (?,?,?,?,?,?,?) ON CONFLICT (user_id) DO UPDATE SET"
        " enabled=excluded.enabled, cap_per_order=excluded.cap_per_order,"
        " monthly_cap=excluded.monthly_cap,"
        " asset_classes=excluded.asset_classes, scope=excluded.scope,"
        " updated_at=excluded.updated_at",
        (user_id, int(enabled), float(cap_per_order), float(monthly_cap),
         json.dumps(list(asset_classes)), (scope or "").strip(),
         db.utcnow()))
    conn.commit()
    return mandate(user_id)


def mandate(user_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM money_mandates WHERE user_id=?",
        (user_id,)).fetchone()
    if row is None:
        return None
    out = dict(row)
    out["enabled"] = bool(out["enabled"])
    out["asset_classes"] = json.loads(out["asset_classes"] or "[]")
    return out


def _month() -> str:
    return db.utcnow()[:7]


def _mandate_engine(user_id: str, lang: str) -> list[dict]:
    """JIM investing on the user's behalf — inside the mandate, or not at
    all.

    The one strategy shipped is the boring one Marcus Bell would teach:
    when liquid cash exceeds the cushion (the low-balance floor, doubled),
    propose moving the excess into the mandate's first asset class, capped
    per order and per month. Proposals, logged; see rule 3 for why nothing
    executes.
    """
    m = mandate(user_id)
    if not m or not m["enabled"]:
        return []
    conn = db.connect()
    spent = conn.execute(
        "SELECT COALESCE(SUM(amount),0) AS s FROM money_orders"
        " WHERE user_id=? AND month=?", (user_id, _month())).fetchone()["s"]
    room = m["monthly_cap"] - float(spent or 0)
    if room <= 0:
        return []

    balances = _latest_balances(user_id)
    liquid = sum(v for aid, v in balances.items()
                 if _account(aid)["kind"] in ("checking", "savings"))
    budget = _monthly_budget_total(user_id)
    cushion = 2 * (max(LOW_FLOOR, budget * LOW_FRACTION)
                   if budget else LOW_FLOOR)
    excess = liquid - cushion
    if excess <= 0:
        return []

    amount = round(min(excess, m["cap_per_order"], room), 2)
    asset = m["asset_classes"][0]
    order_id = db.new_id("ord")
    conn.execute(
        "INSERT INTO money_orders (id, user_id, asset_class, amount, month,"
        " status, rationale, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (order_id, user_id, asset, amount, _month(), "proposed",
         i18n.money_text("order_rationale", lang).format(
             excess=f"{excess:.0f}", cushion=f"{cushion:.0f}"),
         db.utcnow()))
    conn.commit()
    return [_order(order_id)]


def _order(order_id: str) -> dict:
    return dict(db.connect().execute(
        "SELECT * FROM money_orders WHERE id=?", (order_id,)).fetchone())


def orders_for(user_id: str) -> list[dict]:
    return [dict(r) for r in db.connect().execute(
        "SELECT * FROM money_orders WHERE user_id=? ORDER BY created_at"
        " DESC LIMIT 50", (user_id,)).fetchall()]


# --------------------------------------------------------------------------
# the overview

def view(user_id: str, lang: str, qrme=None) -> dict:
    """Everything the Money card renders — labels included, because the
    desktop console has no translation table of its own and the backlog it
    would grow is a ratchet. The server speaks the reader's language; the
    screen just shows it."""
    goal = savings_goal(user_id)
    balances = _latest_balances(user_id)
    accounts = accounts_for(user_id)
    for acc in accounts:
        acc["balance"] = balances.get(acc["id"])
    m = mandate(user_id)
    return {
        "accounts": accounts,
        "savings": goal,
        "mandate": m,
        "orders": orders_for(user_id),
        "doors": _doors(user_id, qrme),
        "note": i18n.money_text("custody_note", lang),
        "labels": i18n.money_labels(lang),
    }
