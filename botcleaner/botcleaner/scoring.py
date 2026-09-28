"""The detection engine: every connection gets a 0-100 bot score and its reasons.

Signals are combined with a noisy-OR: each fired signal independently "votes"
with probability ``weight * strength`` that the account is automated or fake,
and the score is the chance at least one vote is right. That keeps the score
monotone (more evidence never lowers it), bounded, and explainable: each
reason's contribution is its own ``weight * strength``, so the top three
reasons shown to the user are exactly the three that moved the score most.

The engine detects automation and fakes only. Being inactive, new-ish, or
unpopular is never enough on its own to reach "Suspicious".
"""
from __future__ import annotations

import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from typing import Iterable, Optional

from . import imagehash
from .models import Connection, Direction, Label, Reason, ScoredAccount, label_for

# Base weight of each signal: the most it can contribute on its own.
WEIGHTS: dict[str, float] = {
    # profile
    "new_account": 0.35,
    "bot_wave": 0.30,
    "handle_pattern": 0.30,
    "default_photo": 0.25,
    "stock_photo": 0.40,
    "follow_ratio": 0.35,
    "spam_bio": 0.40,
    "empty_bio": 0.10,
    # friends/followers list
    "arrival_burst": 0.35,
    "coordinated_burst": 0.55,
    "zero_mutual": 0.30,
    "clone": 0.92,
    "shared_photo": 0.50,
    "ring": 0.40,
    "cross_platform": 0.15,
    "one_way": 0.30,
    # following list
    "follow_back_bait": 0.50,
    "handle_drift": 0.30,
    "hijacked": 0.65,
    "engagement_farm": 0.35,
    "inflated_audience": 0.45,
    "follow_spree": 0.20,
    # behaviour
    "fixed_interval": 0.55,
    "round_the_clock": 0.30,
    "repeated_content": 0.40,
    "repost_only": 0.25,
}

SPAM_WORDS = re.compile(
    r"\b(crypto|bitcoin|btc|eth|forex|airdrop|giveaway|dm (me )?for|cash ?app|onlyfans|"
    r"18\+|nsfw|investment|profit|earn \$|click (the )?link|free followers|promo|sugar ?daddy)\b",
    re.I,
)
LINK = re.compile(r"(https?://|www\.|bit\.ly|t\.me/|linktr\.ee)", re.I)
BAIT = re.compile(
    r"(follow for follow|f4f|like if you|comment .* below|tag (a|3|three) friends|share to win|"
    r"type ['\"]?yes|99% (of people )?(can't|won't))",
    re.I,
)
NAME_DIGITS = re.compile(r"^[A-Za-z]+[._]?[A-Za-z]*\d{4,}$")

# Known waves of bot signups (platform-agnostic defaults; ops can extend).
DEFAULT_BOT_WAVES: list[tuple[datetime, datetime]] = []


def _utc(d: Optional[datetime]) -> Optional[datetime]:
    if d is None:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _norm_name(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z\s]", "", s)
    return " ".join(s.split())


def _random_handle(handle: str) -> bool:
    """Heuristic for machine-generated handles: long consonant runs or high digit share."""
    h = handle.lower().lstrip("@")
    if len(h) < 8:
        return False
    digits = sum(ch.isdigit() for ch in h)
    if digits / len(h) >= 0.4:
        return True
    letters = re.sub(r"[^a-z]", "", h)
    if len(letters) >= 8 and re.search(r"[bcdfghjklmnpqrstvwxz]{5,}", letters):
        return True
    return False


def _machine_handle(handle: str) -> bool:
    h = handle.lstrip("@")
    return bool(h) and (bool(NAME_DIGITS.match(h)) or _random_handle(h))


def _handles_alike(a: str, b: str) -> bool:
    a, b = re.sub(r"[^a-z0-9]", "", a.lower()), re.sub(r"[^a-z0-9]", "", b.lower())
    if not a or not b:
        return True  # platform gives no handles (Facebook exports): the name is all we have
    return a in b or b in a or SequenceMatcher(None, a, b).ratio() >= 0.75


@dataclass
class PersonalModel:
    """Per-user adjustments learned from "Real person" / "Definitely a bot" feedback."""

    multipliers: dict[str, float] = field(default_factory=dict)
    whitelist: set[str] = field(default_factory=set)   # connection keys
    confirmed_bots: set[str] = field(default_factory=set)

    def weight(self, code: str) -> float:
        return min(0.97, WEIGHTS[code] * self.multipliers.get(code, 1.0))

    def learn(self, codes: Iterable[str], is_bot: bool) -> None:
        step = 1.08 if is_bot else 0.88
        for c in codes:
            m = self.multipliers.get(c, 1.0) * step
            self.multipliers[c] = max(0.3, min(1.7, m))

    def to_dict(self) -> dict:
        return {
            "multipliers": self.multipliers,
            "whitelist": sorted(self.whitelist),
            "confirmed_bots": sorted(self.confirmed_bots),
        }

    @classmethod
    def from_dict(cls, d: dict | None) -> "PersonalModel":
        d = d or {}
        return cls(
            multipliers=dict(d.get("multipliers", {})),
            whitelist=set(d.get("whitelist", [])),
            confirmed_bots=set(d.get("confirmed_bots", [])),
        )


@dataclass
class _Ctx:
    conns: list[Connection]
    now: datetime
    model: PersonalModel
    stock_hashes: list[str]
    bot_waves: list[tuple[datetime, datetime]]
    burst_keys: set[str] = field(default_factory=set)
    spree_keys: set[str] = field(default_factory=set)
    photo_cluster_keys: set[str] = field(default_factory=set)
    clones: dict[str, tuple[str, float]] = field(default_factory=dict)  # clone key -> (real account_id, strength)
    coordinated_keys: set[str] = field(default_factory=set)
    has_mutual_data: bool = False
    knit_network: bool = False
    names_by_platform: dict[str, set[str]] = field(default_factory=dict)
    platforms: set[str] = field(default_factory=set)
    created_day_clusters: set[str] = field(default_factory=set)
    date_only: set[str] = field(default_factory=set)


class Scorer:
    def __init__(
        self,
        model: PersonalModel | None = None,
        stock_hashes: Iterable[str] = (),
        bot_waves: Iterable[tuple[datetime, datetime]] = (),
        now: datetime | None = None,
    ):
        self.model = model or PersonalModel()
        self.stock_hashes = list(stock_hashes)
        self.bot_waves = list(bot_waves) or DEFAULT_BOT_WAVES
        self.now = _utc(now) or datetime.now(timezone.utc)

    # ---- whole-list analysis -------------------------------------------------

    def _prepare(self, conns: list[Connection]) -> _Ctx:
        ctx = _Ctx(conns, self.now, self.model, self.stock_hashes, self.bot_waves)
        ctx.platforms = {c.platform.value for c in conns}
        for c in conns:
            ctx.names_by_platform.setdefault(c.platform.value, set()).add(_norm_name(c.name))

        # Some exports only give dates (LinkedIn's "Connected On"), which makes every
        # day's connections share one timestamp. Detect that per platform so it isn't
        # mistaken for bursts or follow sprees.
        ctx.date_only = set()
        times: dict[str, Counter] = defaultdict(Counter)
        for c in conns:
            t = _utc(c.connected_at)
            if t:
                times[c.platform.value][t.timetz().replace(tzinfo=None)] += 1
        for plat, cnt in times.items():
            total = sum(cnt.values())
            if total >= 20 and cnt.most_common(1)[0][1] / total >= 0.9:
                ctx.date_only.add(plat)

        # Arrival bursts: many connections landing in the same hour (or day, for date-only
        # exports) per platform+direction, far above this list's normal rate.
        buckets: dict[tuple, list[Connection]] = defaultdict(list)
        for c in conns:
            t = _utc(c.connected_at)
            if t and c.direction != Direction.following:
                unit = t.replace(hour=0, minute=0, second=0, microsecond=0) if c.platform.value in ctx.date_only \
                    else t.replace(minute=0, second=0, microsecond=0)
                buckets[(c.platform, c.direction, unit)].append(c)
        if buckets:
            sizes = [len(v) for v in buckets.values()]
            med = statistics.median(sizes)
            threshold = max(5, 5 * med)
            for v in buckets.values():
                if len(v) >= threshold:
                    ctx.burst_keys.update(c.key for c in v)
                    # Most of the burst sharing one machine-made handle style is coordination.
                    patterned = [c for c in v if _machine_handle(c.handle)]
                    if len(patterned) >= 5 and len(patterned) / len(v) >= 0.5:
                        ctx.coordinated_keys.update(c.key for c in patterned)

        # Follow sprees: the user followed many accounts within ten minutes.
        following = sorted(
            (c for c in conns if c.direction == Direction.following and c.connected_at
             and c.platform.value not in ctx.date_only),
            key=lambda c: _utc(c.connected_at),
        )
        j = 0
        for i, c in enumerate(following):
            while _utc(following[i].connected_at) - _utc(following[j].connected_at) > timedelta(minutes=10):
                j += 1
            if i - j + 1 >= 10:
                ctx.spree_keys.update(x.key for x in following[j:i + 1])

        # Accounts created on the same day in numbers (a signup wave within this list).
        by_day: dict[tuple, list[Connection]] = defaultdict(list)
        for c in conns:
            if c.created_at:
                by_day[(c.platform, _utc(c.created_at).date())].append(c)
        per_platform_days: dict[str, list[int]] = defaultdict(list)
        for (plat, _day), v in by_day.items():
            per_platform_days[plat.value].append(len(v))
        for (plat, _day), v in by_day.items():
            # A wave is many creations on one day *relative to this list's usual day*.
            typical = statistics.median(per_platform_days[plat.value])
            if len(v) >= max(8, 5 * typical):
                ctx.created_day_clusters.update(c.key for c in v)

        # Shared-photo clusters: one avatar reused across differently named accounts.
        hashes = {c.key: c.avatar_hash for c in conns if c.avatar_hash}
        by_key = {c.key: c for c in conns}
        # Very large lists: match near-identical copies only (recompression flips a few
        # bits), which keeps the search near-linear at a million followers.
        for group in imagehash.cluster(hashes, threshold=6 if len(hashes) <= 50_000 else 3):
            names = {_norm_name(by_key[k].name) for k in group}
            if len(group) >= 3 and len(names) >= 2:
                ctx.photo_cluster_keys.update(group)

        # Clone detection: a newer account with a near-identical name (and photo, if any)
        # to an existing connection on the same platform.
        per_platform: dict[str, list[Connection]] = defaultdict(list)
        for c in conns:
            if c.name.strip():
                per_platform[c.platform.value].append(c)
        for plist in per_platform.values():
            # Distinct accounts (the same account can appear as follower and following).
            accounts: dict[str, Connection] = {}
            for c in plist:
                accounts.setdefault(c.account_id, c)
            by_name: dict[str, list[Connection]] = defaultdict(list)
            for c in accounts.values():
                n = _norm_name(c.name)
                if n:
                    by_name[n].append(c)
            items = list(accounts.values())
            pairs: set[tuple[str, str]] = set()
            for group in by_name.values():
                if len(group) <= 50:
                    for a in group:
                        for b in group:
                            if a.account_id < b.account_id:
                                pairs.add((a.account_id, b.account_id))
                else:
                    # Very common names in huge lists: only near-identical photos can make a clone.
                    hashes = {c.account_id: c.avatar_hash for c in group if c.avatar_hash}
                    for members in imagehash.cluster(hashes, threshold=6):
                        for i, a_id in enumerate(members):
                            for b_id in members[i + 1:]:
                                pairs.add(tuple(sorted((a_id, b_id))))
            # Near matches (typo-squats such as "Jon Smith" vs "John Smith").
            if len(items) <= 3000:
                norm = {c.account_id: _norm_name(c.name) for c in items}
                for i, a in enumerate(items):
                    na = norm[a.account_id]
                    if len(na) < 5:
                        continue
                    for b in items[i + 1:]:
                        nb = norm[b.account_id]
                        if na == nb or abs(len(na) - len(nb)) > 2 or len(nb) < 5:
                            continue
                        if na[0] != nb[0]:
                            continue
                        if SequenceMatcher(None, na, nb).ratio() >= 0.9:
                            pairs.add(tuple(sorted((a.account_id, b.account_id))))
            for a_id, b_id in sorted(pairs):
                a, b = accounts[a_id], accounts[b_id]
                exact = _norm_name(a.name) == _norm_name(b.name)
                if a.avatar_hash and b.avatar_hash:
                    if not imagehash.similar(a.avatar_hash, b.avatar_hash, 12):
                        continue  # same name, clearly different photos: two different people
                    strength = 1.0
                elif not exact or not _handles_alike(a.handle, b.handle):
                    continue  # no photo to compare: a similar name alone isn't impersonation
                else:
                    strength = 0.7  # identical name, no photo evidence: flag for review, don't pre-select
                newer, older = self._newer(a, b)
                if newer is None:
                    continue
                if newer.key in self.model.whitelist:
                    continue
                prev = ctx.clones.get(newer.key)
                if prev:
                    # Several lookalikes: point at the oldest one, the likely original.
                    if self._newer(older, accounts[prev[0]])[0] is older:
                        continue
                    strength = max(strength, prev[1])
                ctx.clones[newer.key] = (older.account_id, strength)

        ctx.has_mutual_data = any(c.mutual_ids for c in conns)
        if ctx.has_mutual_data:
            counts = [len(c.mutual_ids) for c in conns]
            ctx.knit_network = statistics.median(counts) >= 3
        return ctx

    @staticmethod
    def _newer(a: Connection, b: Connection) -> tuple[Optional[Connection], Optional[Connection]]:
        for attr in ("created_at", "connected_at"):
            ta, tb = _utc(getattr(a, attr)), _utc(getattr(b, attr))
            if ta and tb and ta != tb:
                return (a, b) if ta > tb else (b, a)
        return None, None

    # ---- per-account signals -------------------------------------------------

    def _signals(self, c: Connection, ctx: _Ctx) -> list[tuple[str, float, str]]:
        out: list[tuple[str, float, str]] = []
        add = lambda code, s, text: out.append((code, max(0.0, min(1.0, s)), text))  # noqa: E731
        now = ctx.now

        created = _utc(c.created_at)
        if created:
            age = (now - created).days
            if age < 90:
                add("new_account", 1.0 if age < 30 else 0.65, f"Account is only {max(age, 0)} days old")
            if any(_utc(a) <= created <= _utc(b) for a, b in ctx.bot_waves) or c.key in ctx.created_day_clusters:
                add("bot_wave", 1.0, "Created during a wave of look-alike signups")

        handle = c.handle.lstrip("@")
        if handle and NAME_DIGITS.match(handle):
            add("handle_pattern", 1.0, f"Handle is a name followed by a long number (@{handle})")
        elif handle and _random_handle(handle):
            add("handle_pattern", 0.8, f"Handle looks randomly generated (@{handle})")

        if c.has_default_avatar:
            add("default_photo", 1.0, "No profile photo")
        if c.avatar_hash and any(imagehash.similar(c.avatar_hash, s, 6) for s in ctx.stock_hashes):
            add("stock_photo", 1.0, "Profile photo matches a known stock or AI-generated image")

        if c.following_count is not None and c.followers_count is not None:
            ratio = c.following_count / max(c.followers_count, 1)
            if ratio > 20 and c.following_count >= 200:
                add("follow_ratio", min(1.0, 0.6 + math.log10(ratio / 20) / 2),
                    f"Follows {c.following_count:,} accounts but has only {c.followers_count:,} followers")

        if c.bio is not None:
            if SPAM_WORDS.search(c.bio) or (LINK.search(c.bio) and len(c.bio) < 60):
                add("spam_bio", 1.0, "Bio is mostly a promotional or spam link")
            elif not c.bio.strip():
                add("empty_bio", 1.0, "Empty bio")

        # Friends/followers list signals.
        if c.direction != Direction.following:
            if c.key in ctx.burst_keys:
                add("arrival_burst", 1.0 if not c.mutual_ids else 0.5,
                    "Arrived in a burst of many accounts within the same hour")
            if ctx.has_mutual_data and ctx.knit_network and not c.mutual_ids:
                add("zero_mutual", 1.0, "No mutual connections, though most of your network knows each other")
            if (c.direction == Direction.follower and not c.mutual_ids
                    and (c.following_count or 0) >= 1000
                    and (c.followers_count or 0) < (c.following_count or 0) / 5):
                add("one_way", 1.0, f"Follows {c.following_count:,} accounts and nobody you know follows them")
            if c.direction == Direction.friend and len(ctx.platforms) >= 2:
                n = _norm_name(c.name)
                if n and len(n.split()) >= 2 and not any(
                    n in names for p, names in ctx.names_by_platform.items() if p != c.platform.value
                ):
                    add("cross_platform", 1.0, "Appears on none of your other networks")

        if c.key in ctx.clones:
            strength = ctx.clones[c.key][1]
            add("clone", strength, "Near-identical name and photo to an existing friend, but a newer account"
                if strength >= 1 else "Same name as an existing friend, but a newer account")
        if c.key in ctx.coordinated_keys:
            add("coordinated_burst", 1.0, "Part of a burst of accounts with the same machine-made handle style")
        if c.key in ctx.photo_cluster_keys:
            add("shared_photo", 1.0, "Uses the same photo as several other differently named accounts")

        # Following list signals.
        if c.direction == Direction.following:
            fu, fb, uf = _utc(c.followed_user_at), _utc(c.user_followed_back_at), _utc(c.unfollowed_user_at)
            if fu and fb and uf and fu <= fb <= uf:
                days = (uf - fb).days
                add("follow_back_bait", 1.0 if days <= 14 else 0.6,
                    f"Followed you, got a follow back, then unfollowed {days} days later")
            if c.key in ctx.spree_keys and not c.last_interaction_at:
                add("follow_spree", 1.0, "Followed in a rapid batch of suggestions you never interacted with")
            if c.audience_bot_share is not None and c.audience_bot_share >= 0.4:
                add("inflated_audience", min(1.0, (c.audience_bot_share - 0.4) / 0.4 + 0.5),
                    f"About {round(c.audience_bot_share * 100)}% of their own followers look like bots")

        spammy_posts = sum(1 for p in c.recent_posts if SPAM_WORDS.search(p))
        if c.previous_handles or c.previous_names:
            old = (c.previous_handles or c.previous_names)[-1]
            dormant = self._dormant_then_active(c.post_timestamps)
            if spammy_posts >= max(1, len(c.recent_posts) // 3) or dormant:
                add("hijacked", 1.0 if spammy_posts else 0.7,
                    f"Changed name from '{old}' and now posts crypto, giveaway or adult spam"
                    if spammy_posts else f"Dormant account that changed name from '{old}' and suddenly became active")
            else:
                add("handle_drift", 1.0, f"Changed its name or handle (was '{old}') after you connected")

        if c.recent_posts:
            dup_share = 1 - len(set(p.strip().lower() for p in c.recent_posts)) / len(c.recent_posts)
            bait = sum(1 for p in c.recent_posts if BAIT.search(p)) / len(c.recent_posts)
            if len(c.recent_posts) >= 4 and dup_share >= 0.5:
                add("repeated_content", min(1.0, dup_share + 0.2), "Posts the same message over and over")
            if bait >= 0.3 or (spammy_posts / len(c.recent_posts) >= 0.5 and "hijacked" not in {o[0] for o in out}):
                add("engagement_farm", min(1.0, max(bait, spammy_posts / len(c.recent_posts)) + 0.3),
                    "Posts engagement bait or recycled promotional content")

        ts = sorted(_utc(t) for t in c.post_timestamps)
        if len(ts) >= 10:
            gaps = [(b - a).total_seconds() for a, b in zip(ts, ts[1:])]
            mean = statistics.mean(gaps)
            cv = statistics.pstdev(gaps) / mean if mean > 0 else 1.0
            if cv < 0.1:
                # Near-perfect regularity is machine timing; loose regularity may be a scheduling tool.
                add("fixed_interval", 1.0 if cv < 0.02 else 0.7, f"Posts at a fixed interval (every {self._fmt_secs(mean)})")
        if len(ts) >= 50 and len({t.hour for t in ts}) >= 22:
            add("round_the_clock", 1.0, "Posts around the clock, with no time to sleep")
        if c.repost_ratio is not None and c.repost_ratio >= 0.95:
            add("repost_only", 1.0, "Only reposts other accounts, never original content")
        return out

    @staticmethod
    def _dormant_then_active(ts: list[datetime]) -> bool:
        ts = sorted(_utc(t) for t in ts)
        return any((b - a).days >= 180 for a, b in zip(ts, ts[1:]))

    @staticmethod
    def _fmt_secs(s: float) -> str:
        if s < 120:
            return f"{round(s)} seconds"
        if s < 7200:
            return f"{round(s / 60)} minutes"
        return f"{round(s / 3600)} hours"

    def _combine(self, sigs: list[tuple[str, float, str]], c: Connection) -> tuple[float, list[Reason]]:
        reasons = [Reason(code=code, text=text, weight=self.model.weight(code) * s) for code, s, text in sigs]
        reasons.sort(key=lambda r: r.weight, reverse=True)
        p_real = 1.0
        for r in reasons:
            p_real *= 1 - r.weight
        score = 100 * (1 - p_real)
        if c.verified:
            score *= 0.5
        return round(score, 1), reasons

    # ---- entry point -----------------------------------------------------------

    def score(self, conns: list[Connection]) -> list[ScoredAccount]:
        ctx = self._prepare(conns)
        first: dict[str, tuple[float, list[tuple[str, float, str]]]] = {}
        for c in conns:
            sigs = self._signals(c, ctx)
            s, _ = self._combine(sigs, c)
            first[c.key] = (s, sigs)

        # Ring structure: suspicious accounts whose mutuals are only each other.
        suspects = {c.account_id for c in conns if first[c.key][0] >= 50}
        ring_of: dict[str, str] = {}
        ring_members = [
            c for c in conns
            if c.account_id in suspects and len(c.mutual_ids) >= 2 and set(c.mutual_ids) <= suspects
        ]
        if ring_members:
            parent = {c.account_id: c.account_id for c in ring_members}

            def find(i: str) -> str:
                while parent[i] != i:
                    parent[i] = parent[parent[i]]
                    i = parent[i]
                return i

            for c in ring_members:
                for m in c.mutual_ids:
                    if m in parent:
                        parent[find(c.account_id)] = find(m)
            for c in ring_members:
                ring_of[c.account_id] = "ring-" + find(c.account_id)

        results: list[ScoredAccount] = []
        for c in conns:
            sigs = list(first[c.key][1])
            if c.account_id in ring_of:
                sigs.append(("ring", 1.0, "Connected only to other flagged accounts (a bot ring)"))
            score, reasons = self._combine(sigs, c)
            if c.key in self.model.whitelist:
                score = 0.0
            elif c.key in self.model.confirmed_bots:
                score = max(score, 99.0)
                reasons.insert(0, Reason(code="user_confirmed", text="You marked this account as a bot", weight=1.0))
            results.append(ScoredAccount(
                connection=c,
                score=score,
                label=label_for(score),
                reasons=reasons,
                is_clone=c.key in ctx.clones,
                clone_of=ctx.clones[c.key][0] if c.key in ctx.clones else None,
                ring_id=ring_of.get(c.account_id),
            ))
        return results


def flagged(results: list[ScoredAccount], include_low: bool = False) -> list[ScoredAccount]:
    keep = {Label.likely_bot, Label.suspicious} | ({Label.low_confidence} if include_low else set())
    return sorted((r for r in results if r.label in keep), key=lambda r: r.score, reverse=True)


def label_counts(results: list[ScoredAccount]) -> dict[str, int]:
    return dict(Counter(r.label.value for r in results))
