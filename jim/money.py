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

from . import audit, db, i18n

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


def floor_for(user_id: str) -> dict:
    """The low-balance floor this user actually has — their own when they
    set one, the derived default otherwise. The derived figure rides along
    either way so a screen can show what Reset would go back to."""
    budget = _monthly_budget_total(user_id)
    derived = round(max(LOW_FLOOR, budget * LOW_FRACTION)
                    if budget else LOW_FLOOR, 2)
    row = db.connect().execute(
        "SELECT floor FROM money_floors WHERE user_id=?",
        (user_id,)).fetchone()
    if row:
        return {"floor": round(float(row["floor"]), 2), "source": "user",
                "derived": derived}
    return {"floor": derived, "source": "default", "derived": derived}


def set_floor(user_id: str, floor: float | None) -> dict:
    """Set the low-balance floor, or hand it back to the derived default.

    ``None`` clears rather than zero: a floor of zero would be a warning
    that can never fire wearing a setting's clothes, and the honest way to
    say "decide for me" is to say nothing.
    """
    conn = db.connect()
    if floor is None:
        conn.execute("DELETE FROM money_floors WHERE user_id=?", (user_id,))
    else:
        floor = float(floor)
        if floor <= 0:
            raise MoneyError("a low-balance floor is a positive amount — "
                             "send null to go back to the derived default")
        conn.execute(
            "INSERT INTO money_floors (user_id, floor, set_at)"
            " VALUES (?,?,?) ON CONFLICT (user_id) DO UPDATE SET"
            " floor=excluded.floor, set_at=excluded.set_at",
            (user_id, floor, db.utcnow()))
    conn.commit()
    return floor_for(user_id)


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
    floor = floor_for(user_id)["floor"]

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
    # No transaction can happen — this module has no network path at all —
    # so the audited act is the *grant*, which is the thing a person would
    # later say they did or did not give.
    audit.record("mandate.set" if enabled else "mandate.clear",
                 user_id=user_id,
                 ref=(f"cap {cap_per_order:g}/order, {monthly_cap:g}/month, "
                      + ",".join(asset_classes)) if enabled else None)
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
    # The same floor the low-balance warning trips on — the owner's own
    # when they set one — so raising your floor also pulls the engine's
    # hands back before the warning would ever have to fire.
    cushion = 2 * floor_for(user_id)["floor"]
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
# statements — the file is the reading

#: Aggregators this module knows how to hold a consent for. The link is a
#: written consent and a registration; syncing needs the deployment to hold
#: that aggregator's credentials, and this module never pretends it does.
AGGREGATORS = ("plaid", "tink", "truelayer", "mx")


def drop_statement(user_id: str, account_id: str, filename: str,
                   content_b64: str, lang: str, pdi=None,
                   qrme=None) -> dict:
    """A statement file dropped into the vault and read locally.

    The raw file is sealed exactly as account credentials are (rule 1: the
    vault or nowhere). The reading is deterministic CSV arithmetic on the
    device — a statement is exact numbers, and a model adds nothing to
    exactness but risk. When the statement closes with a balance, that
    balance walks the same `observe` path a hand-typed reading does, so the
    guardian ladder and its doors wake off the file itself.
    """
    import base64 as _b64

    account = _account(account_id)
    if account["user_id"] != user_id:
        raise MoneyError("that account belongs to somebody else")
    if pdi is None:
        raise MoneyError(
            "a bank statement is private data and only ever lives in the "
            "vault; this plan has no vault, so nothing was stored")
    if not (content_b64 or "").strip():
        raise MoneyError("an empty drop holds no statement")
    try:
        raw = _b64.b64decode(content_b64, validate=True)
    except Exception:
        raise MoneyError("the statement could not be read — it is not "
                         "base64") from None

    summary = _read_csv_statement(raw)
    statement_id = db.new_id("stm")
    pdi.put(f"jim/{user_id}/statements/{statement_id}",
            _b64.b64encode(raw).decode())

    conn = db.connect()
    conn.execute(
        "INSERT INTO statements (id, user_id, account_id, filename,"
        " line_count, total_in, total_out, end_balance, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (statement_id, user_id, account_id, (filename or "statement").strip(),
         summary["line_count"], summary["total_in"], summary["total_out"],
         summary["end_balance"], db.utcnow()))
    conn.commit()

    out = {"id": statement_id, "account_id": account_id,
           "filename": (filename or "statement").strip(),
           "statement_sealed": True, **summary}
    if summary["end_balance"] is not None:
        out["observed"] = observe(
            user_id, account_id, summary["end_balance"],
            "statement " + (filename or "statement").strip(), lang,
            pdi=pdi, qrme=qrme)
    return out


def _read_csv_statement(raw: bytes) -> dict:
    """Deterministic local arithmetic over a delimited statement.

    Shape assumed: one transaction per line, the amount in the last column
    that parses as a number — or, when a header names ``amount`` and/or
    ``balance``, those columns by name. Unreadable files summarize as zero
    lines; the file is sealed either way, and nothing is guessed.
    """
    text = raw.decode("utf-8", errors="replace")
    rows = [line for line in text.splitlines() if line.strip()]
    if not rows:
        return {"line_count": 0, "total_in": 0.0, "total_out": 0.0,
                "end_balance": None}
    delim = ";" if rows[0].count(";") > rows[0].count(",") else ","

    def _num(cell: str) -> float | None:
        cell = cell.strip().replace("$", "").replace("\u20ac", "")
        try:
            return float(cell.replace(",", "")) if cell else None
        except ValueError:
            return None

    header = [c.strip().lower() for c in rows[0].split(delim)]
    amount_col = header.index("amount") if "amount" in header else None
    balance_col = header.index("balance") if "balance" in header else None
    data = rows[1:] if amount_col is not None or all(
        _num(c) is None for c in rows[0].split(delim)) else rows

    total_in = total_out = 0.0
    line_count = 0
    end_balance = None
    for line in data:
        cells = line.split(delim)
        if amount_col is not None and amount_col < len(cells):
            amount = _num(cells[amount_col])
        else:
            nums = [n for n in (_num(c) for c in cells) if n is not None]
            amount = nums[-1] if nums else None
        if amount is None:
            continue
        line_count += 1
        if amount >= 0:
            total_in += amount
        else:
            total_out += -amount
        if balance_col is not None and balance_col < len(cells):
            balance = _num(cells[balance_col])
            if balance is not None:
                end_balance = balance
    return {"line_count": line_count, "total_in": round(total_in, 2),
            "total_out": round(total_out, 2), "end_balance": end_balance}


def statements_for(user_id: str, limit: int = 12) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id, account_id, filename, line_count, total_in, total_out,"
        " end_balance, created_at FROM statements WHERE user_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (user_id, limit)).fetchall()
    return [{**dict(r), "statement_sealed": True} for r in rows]


# --------------------------------------------------------------------------
# bank links — a consent is written down, never assumed

def link_bank(user_id: str, institution: str, aggregator: str,
              kind: str = "checking", pdi=None) -> dict:
    """Write down a bank-link consent through an aggregator.

    The link registers the account and records which aggregator the owner
    consented to. It needs the vault standing (the tokens an aggregator
    hands back are exactly the private data rule 1 exists for), and its
    status tells the truth: ``consented`` until this deployment holds that
    aggregator's credentials — no data is ever pretended in."""
    if aggregator not in AGGREGATORS:
        raise MoneyError(f"unknown aggregator {aggregator!r}; this module "
                         f"holds consents for {', '.join(AGGREGATORS)}")
    if kind not in ACCOUNT_KINDS:
        raise MoneyError(
            f"unknown account kind {kind!r}; expected one of "
            f"{', '.join(ACCOUNT_KINDS)}")
    if not (institution or "").strip():
        raise MoneyError("name the institution — a bank, a broker, an "
                         "exchange")
    if pdi is None:
        raise MoneyError(
            "a bank link's tokens are private data and only ever live in "
            "the vault; this plan has no vault, so no link was made")

    account = add_account(user_id, kind, institution.strip(),
                          institution.strip(), None, None, None, pdi)
    conn = db.connect()
    link_id = db.new_id("bnk")
    conn.execute(
        "INSERT INTO bank_links (id, user_id, account_id, institution,"
        " aggregator, status, created_at) VALUES (?,?,?,?,?,?,?)",
        (link_id, user_id, account["id"], institution.strip(), aggregator,
         "consented", db.utcnow()))
    conn.commit()
    return _link(link_id)


def _link(link_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM bank_links WHERE id=?", (link_id,)).fetchone()
    if row is None:
        raise MoneyError("no such bank link")
    return dict(row)


def links_for(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM bank_links WHERE user_id=? ORDER BY created_at",
        (user_id,)).fetchall()
    return [_link(r["id"]) for r in rows]


def sync_bank(user_id: str, link_id: str) -> dict:
    """Pull balances through the link — or say exactly why not.

    This deployment holds no aggregator credentials, so the sync refuses
    with the truth instead of inventing balances: the consent stands, and
    a statement drop or a hand-typed reading feeds the same ladder today.
    """
    import os

    link = _link(link_id)
    if link["user_id"] != user_id:
        raise MoneyError("that bank link belongs to somebody else")
    if link["status"] == "revoked":
        raise MoneyError("this bank link was revoked; link again to sync")
    if not os.environ.get(f"{link['aggregator'].upper()}_CLIENT_ID"):
        raise MoneyError(
            f"this deployment holds no {link['aggregator']} credentials — "
            "the consent stands and will sync when the aggregator is "
            "configured; until then, drop a statement or observe a "
            "balance by hand")
    # Credentials present: the client call would land here, tokens to the
    # vault and balances through `observe`. Until a client is wired, the
    # truth is the same refusal — nothing is pretended in.
    raise MoneyError(
        f"the {link['aggregator']} client is not wired into this build; "
        "the consent stands, and nothing was invented in its name")


def revoke_link(user_id: str, link_id: str) -> dict:
    link = _link(link_id)
    if link["user_id"] != user_id:
        raise MoneyError("that bank link belongs to somebody else")
    conn = db.connect()
    conn.execute(
        "UPDATE bank_links SET status='revoked', revoked_at=? WHERE id=?",
        (db.utcnow(), link_id))
    conn.commit()
    return _link(link_id)


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
        "floor": floor_for(user_id),
        "orders": orders_for(user_id),
        "doors": _doors(user_id, qrme),
        "note": i18n.money_text("custody_note", lang),
        "labels": i18n.money_labels(lang),
    }
