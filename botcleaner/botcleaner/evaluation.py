"""Testing and validation (§7): accuracy gates, seeded test networks, bias checks.

No model or rule ships unless it passes these gates. ``python -m botcleaner.evaluation``
builds seeded networks (e.g. 500 real + injected bots and clones), scores them,
and prints each gate with pass/fail. The same gates run in the test suite.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from .models import Connection, Direction, Label, Platform, ScoredAccount
from .purge.signals import SiteAccount, SiteScore

GATES_A = {"precision_likely_bot": 0.95, "precision_suspicious": 0.80, "recall": 0.70, "false_flag_rate_max": 0.01}
GATES_B = {"precision_tier3": 0.98, "precision_tier2": 0.90, "recall": 0.80, "false_flag_rate_max": 0.005,
           "overturn_rate_max": 0.05}
BIAS_MAX_RATIO = 2.0

FIRST = ["James", "Mary", "Wei", "Aisha", "Carlos", "Priya", "Olga", "Kwame", "Yuki", "Fatima", "Liam", "Sofia",
         "Mateo", "Chloe", "Arjun", "Nadia", "Tomás", "Ingrid", "Hiro", "Amara", "Ethan", "Zara", "Diego", "Lena",
         "Omar", "Grace", "Ivan", "Mei", "Noah", "Leila", "Samuel", "Ana", "Kofi", "Elif", "Lucas", "Hana"]
LAST = ["Smith", "Garcia", "Chen", "Okafor", "Silva", "Patel", "Ivanova", "Mensah", "Tanaka", "Haddad", "Murphy",
        "Rossi", "Lopez", "Martin", "Sharma", "Karimi", "Novak", "Berg", "Sato", "Diallo", "Brown", "Khan", "Reyes",
        "Weber", "Aziz", "Kim", "Petrov", "Wang", "Walker", "Nasser", "Cohen", "Costa", "Asante", "Yilmaz", "Dubois"]
GROUPS = ["en-NA", "es-LATAM", "zh-APAC", "ar-MENA", "fr-EU", "sw-AFR"]


@dataclass
class Seeded:
    conns: list[Connection]
    truth: dict[str, bool]                 # connection key+direction -> is_bot
    group: dict[str, str] = field(default_factory=dict)
    clones: set[str] = field(default_factory=set)


def _hash(rng: random.Random) -> str:
    return f"{rng.getrandbits(64):016x}"


def _near(h: str, rng: random.Random, bits: int = 2) -> str:
    v = int(h, 16)
    for b in rng.sample(range(64), bits):
        v ^= 1 << b
    return f"{v:016x}"


def tkey(c: Connection) -> str:
    return f"{c.key}:{c.direction.value}"


def seeded_network(n_real: int = 500, n_bots: int = 40, n_clones: int = 10, n_following_bad: int = 15,
                   platform: Platform = Platform.x, seed: int = 7, now: Optional[datetime] = None) -> Seeded:
    """A test network with a known mix. Real people include hard cases (new, no photo, digits)."""
    rng = random.Random(seed)
    now = now or datetime(2026, 6, 1, tzinfo=timezone.utc)
    conns: list[Connection] = []
    truth: dict[str, bool] = {}
    group: dict[str, str] = {}
    clones: set[str] = set()
    real_ids = [f"r{i}" for i in range(n_real)]

    reals: list[Connection] = []
    for i, rid in enumerate(real_ids):
        first, last = rng.choice(FIRST), rng.choice(LAST)
        name = f"{first} {last}"
        style = rng.random()
        if style < 0.08:
            handle = f"{first.lower()}{rng.randint(1970, 2008)}"          # birth year, a real-person pattern
        elif style < 0.5:
            handle = f"{first.lower()}.{last.lower()}{rng.choice(['', '_', str(rng.randint(1, 99))])}"
        else:
            handle = f"{first.lower()}{last.lower()[:3]}{rng.choice(['', 'x', 'official', 'dev'])}"
        created = now - timedelta(days=rng.randint(60, 4000), seconds=rng.randint(0, 86399))  # a few are new
        followers = int(rng.lognormvariate(5.5, 1.0))
        following = int(rng.lognormvariate(5.3, 0.8))
        mutuals = rng.sample(real_ids, rng.randint(2, 25))
        direction = rng.choice([Direction.follower, Direction.following, Direction.follower])
        c = Connection(
            platform=platform, account_id=rid, handle=handle, name=name, direction=direction,
            connected_at=created + timedelta(days=rng.randint(1, max(2, (now - created).days - 1)), seconds=rng.randint(0, 86399)),
            created_at=created, followers_count=followers, following_count=following,
            bio=rng.choice(["", "Coffee, code, cats.", "Nurse. Mom of two.", "Runner | Teacher", "Photographer",
                            "Views my own.", "Student", "Chef at a small bistro"]),
            has_default_avatar=rng.random() < 0.08, avatar_hash=_hash(rng),
            mutual_ids=[m for m in mutuals if m != rid],
        )
        reals.append(c)
        conns.append(c)
        truth[tkey(c)] = False
        group[tkey(c)] = GROUPS[i % len(GROUPS)]

    # Follower bots: arrive in bursts, shared stock photos, number handles, spam bios, ring structure.
    stock = [_hash(rng) for _ in range(3)]
    burst_start = now - timedelta(days=rng.randint(10, 40))
    bot_ids = [f"b{i}" for i in range(n_bots)]
    wave_day = now - timedelta(days=rng.randint(20, 60))
    for i, bid in enumerate(bot_ids):
        first = rng.choice(FIRST)
        created = wave_day + timedelta(minutes=rng.randint(0, 600)) if i % 2 == 0 else now - timedelta(days=rng.randint(5, 80))
        c = Connection(
            platform=platform, account_id=bid,
            handle=f"{first.lower()}{rng.randint(10_000_000, 99_999_999)}" if i % 3 else f"{rng.choice(['xq','zr','kw'])}{_hash(rng)[:9]}",
            name=f"{first} {rng.choice(LAST)}", direction=Direction.follower,
            connected_at=burst_start + timedelta(minutes=rng.randint(0, 50)) if i % 4 != 3 else now - timedelta(days=rng.randint(1, 300)),
            created_at=created, followers_count=rng.randint(0, 40), following_count=rng.randint(1500, 7000),
            bio=rng.choice(["", "DM for crypto signals 🚀 t.me/x", "Earn $500/day click the link", "", "giveaway every week"]),
            has_default_avatar=i % 5 == 0, avatar_hash=None if i % 5 == 0 else rng.choice(stock),
            mutual_ids=rng.sample(bot_ids, 3) if i % 2 == 0 else [],
        )
        conns.append(c)
        truth[tkey(c)] = True

    # Clones: copy a real friend's name and photo, newer account.
    for i in range(n_clones):
        victim = reals[rng.randrange(len(reals))]
        c = Connection(
            platform=platform, account_id=f"c{i}", handle=victim.handle.replace(".", "_") + rng.choice(["_", "1", "x"]),
            name=victim.name, direction=Direction.follower,
            connected_at=now - timedelta(days=rng.randint(1, 20)), created_at=now - timedelta(days=rng.randint(1, 40)),
            followers_count=rng.randint(0, 30), following_count=rng.randint(50, 900),
            bio=victim.bio, avatar_hash=_near(victim.avatar_hash, rng), has_default_avatar=False,
        )
        conns.append(c)
        truth[tkey(c)] = True
        clones.add(tkey(c))

    # Following-side bad actors: follow-back bait, hijacked accounts, engagement farms.
    for i in range(n_following_bad):
        kind = i % 3
        created = now - timedelta(days=rng.randint(200, 3000))
        base = dict(platform=platform, account_id=f"f{i}", handle=f"{rng.choice(FIRST).lower()}{rng.choice(LAST).lower()}",
                    name=f"{rng.choice(FIRST)} {rng.choice(LAST)}", direction=Direction.following,
                    connected_at=now - timedelta(days=rng.randint(30, 400)), created_at=created,
                    followers_count=rng.randint(300, 5000), following_count=rng.randint(300, 5000), avatar_hash=_hash(rng))
        if kind == 0:
            fu = now - timedelta(days=rng.randint(40, 100))
            c = Connection(**{**base, "following_count": rng.randint(4000, 7000), "followers_count": rng.randint(50, 150)},
                           followed_user_at=fu, user_followed_back_at=fu + timedelta(days=1),
                           unfollowed_user_at=fu + timedelta(days=rng.randint(2, 9)), bio="", has_default_avatar=True)
        elif kind == 1:
            c = Connection(**{**base, "handle": f"crypto_gains{rng.randint(1000, 99999)}"}, previous_handles=[base["handle"]],
                           recent_posts=["Huge crypto giveaway! DM for details", "Free BTC airdrop click the link",
                                         "Crypto giveaway! DM for details"],
                           post_timestamps=[now - timedelta(days=900), now - timedelta(days=3), now - timedelta(days=2),
                                            now - timedelta(days=1)])
        else:
            c = Connection(**base, recent_posts=["Like if you agree!", "Tag 3 friends who need this", "Like if you agree!",
                                                  "Type YES if you love your mom", "Like if you agree!"],
                           post_timestamps=[now - timedelta(hours=6 * k) for k in range(12)], repost_ratio=0.97,
                           audience_bot_share=0.7)
        conns.append(c)
        truth[tkey(c)] = True
    return Seeded(conns, truth, group, clones)


def red_team_network(n_real: int = 500, per_level: int = 30, seed: int = 21, now: Optional[datetime] = None) -> tuple[Seeded, dict[str, int]]:
    """Quarterly red-team set (section 7.5): evasive bots added to a normal network.

    Level 1: aged accounts with realistic unique photos and names, but they post
             recycled content on a fixed schedule.
    Level 2: also human posting times; the only tells are zero mutual friends in a
             tightly knit network and following thousands with few followers back.
    Level 3: indistinguishable from people on the data we can see. They're here to
             measure the blind spot honestly, not to be caught.
    Returns the network and each evasive account's level.
    """
    rng = random.Random(seed)
    now = now or datetime(2026, 6, 1, tzinfo=timezone.utc)
    base = seeded_network(n_real=n_real, n_bots=0, n_clones=0, n_following_bad=0, seed=seed, now=now)
    level: dict[str, int] = {}
    for lvl in (1, 2, 3):
        for i in range(per_level):
            first, last = rng.choice(FIRST), rng.choice(LAST)
            created = now - timedelta(days=rng.randint(700, 2400))
            kw = dict(platform=Platform.x, account_id=f"rt{lvl}_{i}", handle=f"{first.lower()}.{last.lower()}{rng.randint(1, 99)}",
                      name=f"{first} {last}", direction=Direction.follower, created_at=created,
                      connected_at=now - timedelta(days=rng.randint(5, 600)), avatar_hash=_hash(rng),
                      bio=rng.choice(["Coffee lover", "Travel | Food", "Dad, runner", "Designer"]), has_default_avatar=False)
            if lvl == 1:
                kw.update(followers_count=rng.randint(150, 900), following_count=rng.randint(150, 900),
                          mutual_ids=rng.sample([f"r{k}" for k in range(n_real)], 3),
                          recent_posts=["Check out this amazing deal!"] * 4 + ["Best offer today, link in bio"],
                          post_timestamps=[now - timedelta(hours=4 * k) for k in range(20)])
            elif lvl == 2:
                kw.update(followers_count=rng.randint(20, 120), following_count=rng.randint(2500, 6000), mutual_ids=[],
                          post_timestamps=[now - timedelta(hours=rng.randint(1, 900)) for _ in range(15)])
            else:
                kw.update(followers_count=rng.randint(150, 900), following_count=rng.randint(150, 900),
                          mutual_ids=rng.sample([f"r{k}" for k in range(n_real)], rng.randint(3, 12)),
                          post_timestamps=[now - timedelta(hours=rng.randint(1, 900)) for _ in range(15)])
            c = Connection(**kw)
            base.conns.append(c)
            base.truth[tkey(c)] = True
            level[tkey(c)] = lvl
    return base, level


def red_team_report(results: list[ScoredAccount], truth: dict[str, bool], level: dict[str, int]) -> dict:
    flagged = lambda r: r.label in (Label.likely_bot, Label.suspicious)  # noqa: E731
    per = {}
    for lvl in (1, 2, 3):
        rs = [r for r in results if level.get(tkey(r.connection)) == lvl]
        per[f"level{lvl}_recall"] = _ratio(sum(flagged(r) for r in rs), len(rs), 0.0)
    reals = [r for r in results if not truth[tkey(r.connection)]]
    per["false_flag_rate"] = _ratio(sum(flagged(r) for r in reals), len(reals), 0.0)
    return per


@dataclass
class Metrics:
    precision_top: float
    precision_mid: float
    recall: float
    false_flag_rate: float
    n_top: int
    n_mid: int
    n_bots: int
    n_real: int

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def _ratio(a: int, b: int, empty: float = 1.0) -> float:
    return a / b if b else empty


def metrics_a(results: list[ScoredAccount], truth: dict[str, bool]) -> Metrics:
    top = [r for r in results if r.label == Label.likely_bot]
    mid = [r for r in results if r.label == Label.suspicious]
    bots = [r for r in results if truth[tkey(r.connection)]]
    reals = [r for r in results if not truth[tkey(r.connection)]]
    flagged = lambda r: r.label in (Label.likely_bot, Label.suspicious)  # noqa: E731
    return Metrics(
        precision_top=_ratio(sum(truth[tkey(r.connection)] for r in top), len(top)),
        precision_mid=_ratio(sum(truth[tkey(r.connection)] for r in mid), len(mid)),
        recall=_ratio(sum(flagged(r) for r in bots), len(bots), 0.0),
        false_flag_rate=_ratio(sum(flagged(r) for r in reals), len(reals), 0.0),
        n_top=len(top), n_mid=len(mid), n_bots=len(bots), n_real=len(reals),
    )


def gates_a(m: Metrics) -> dict[str, bool]:
    return {
        "precision_likely_bot": m.precision_top >= GATES_A["precision_likely_bot"],
        "precision_suspicious": m.precision_mid >= GATES_A["precision_suspicious"],
        "recall": m.recall >= GATES_A["recall"],
        "false_flag_rate": m.false_flag_rate <= GATES_A["false_flag_rate_max"],
    }


def bias_check(results: list[ScoredAccount], truth: dict[str, bool], group: dict[str, str]) -> dict:
    """False-flag rate per group; no group may exceed 2x the overall rate."""
    reals = [r for r in results if not truth[tkey(r.connection)] and tkey(r.connection) in group]
    flagged = lambda r: r.label in (Label.likely_bot, Label.suspicious)  # noqa: E731
    overall = _ratio(sum(flagged(r) for r in reals), len(reals), 0.0)
    per: dict[str, float] = {}
    for g in sorted(set(group.values())):
        rs = [r for r in reals if group[tkey(r.connection)] == g]
        per[g] = _ratio(sum(flagged(r) for r in rs), len(rs), 0.0)
    # With a tiny overall rate, allow one account's worth of noise per group.
    floor = max(overall, 1 / max(1, min(sum(1 for r in reals if group[tkey(r.connection)] == g) for g in per)))
    ok = all(v <= BIAS_MAX_RATIO * floor for v in per.values())
    return {"overall": overall, "per_group": per, "ok": ok}


# ---- Module B -------------------------------------------------------------------------------

def seeded_site(n_real: int = 3000, n_bots: int = 300, seed: int = 11, now: Optional[datetime] = None) -> tuple[list[SiteAccount], dict[str, bool]]:
    rng = random.Random(seed)
    now = now or datetime(2026, 6, 1, tzinfo=timezone.utc)
    accs: list[SiteAccount] = []
    truth: dict[str, bool] = {}
    domains = ["gmail.com", "outlook.com", "yahoo.com", "proton.me", "icloud.com", "example.org"]
    for i in range(n_real):
        first, last = rng.choice(FIRST).lower(), rng.choice(LAST).lower()
        created = now - timedelta(days=rng.randint(1, 1500), minutes=rng.randint(0, 1440))
        start = created + timedelta(hours=1)
        ts = sorted(start + timedelta(seconds=rng.randint(0, 86400 * 30)) for _ in range(rng.randint(8, 40)))
        accs.append(SiteAccount(
            account_id=f"u{i}", username=f"{first}{rng.choice(['', '_', '.'])}{last}{rng.choice(['', str(rng.randint(1, 99))])}",
            email=f"{first}.{last}{rng.randint(1, 999)}@{rng.choice(domains)}", created_at=created,
            signup_ip=f"{rng.randint(11, 200)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}",
            signup_asn=f"AS{rng.randint(1000, 60000)}", device_fingerprint=f"fp{rng.getrandbits(40):x}",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36",
            captcha_solve_ms=rng.randint(2500, 25000), action_timestamps=ts,
            posts=[rng.choice(["Loved this thread", "Anyone tried the new update?", "Great write-up, thanks",
                               "Here's my build log for today", f"Day {rng.randint(1, 300)} of learning guitar"])],
            email_verified=rng.random() > 0.15, tags=["staff"] if i < 5 else [],
        ))
        truth[f"u{i}"] = False
    # Bot farm: a few operators, each with shared devices/IPs, disposable/sequential emails, templated posts.
    for i in range(n_bots):
        op = i % 6
        created = now - timedelta(days=3 + op, minutes=i % 50)
        base_t = created + timedelta(minutes=5)
        accs.append(SiteAccount(
            account_id=f"bot{i}", username=f"user{rng.getrandbits(32):x}",
            email=(f"promo.deals{i}@{'mailinator.com' if op % 2 else 'gmail.com'}"),
            created_at=created, signup_ip=f"45.83.{op}.{10 + (i % 5)}", signup_asn="AS14061" if op < 3 else "AS9009",
            device_fingerprint=f"farm{op}-{i % 4}", user_agent="Mozilla/5.0 HeadlessChrome/126.0" if op % 3 == 0 else
            "Mozilla/5.0 (X11; Linux x86_64) Chrome/126.0", webdriver=op % 3 == 0,
            captcha_solve_ms=rng.randint(200, 700), honeypot_filled=op == 4,
            action_timestamps=[base_t + timedelta(seconds=30 * k) for k in range(20)],
            posts=[f"Get {rng.randint(100, 999)} free followers now at https://spam{op}.example/{i}",
                   f"Earn ${rng.randint(100, 900)} a day from home, DM @promo{op}"],
            email_verified=False, login_asns=["AS14061"],
        ))
        truth[f"bot{i}"] = True
    return accs, truth


def metrics_b(results: list[SiteScore], truth: dict[str, bool], tier2: float = 80, tier3: float = 95,
              flag_min: float = 60) -> Metrics:
    top = [r for r in results if r.score >= tier3]
    mid = [r for r in results if tier2 <= r.score < tier3]
    bots = [r for r in results if truth[r.account_id]]
    reals = [r for r in results if not truth[r.account_id]]
    return Metrics(
        precision_top=_ratio(sum(truth[r.account_id] for r in top), len(top)),
        precision_mid=_ratio(sum(truth[r.account_id] for r in mid), len(mid)),
        recall=_ratio(sum(r.score >= flag_min for r in bots), len(bots), 0.0),
        false_flag_rate=_ratio(sum(r.score >= flag_min for r in reals), len(reals), 0.0),
        n_top=len(top), n_mid=len(mid), n_bots=len(bots), n_real=len(reals),
    )


def gates_b(m: Metrics) -> dict[str, bool]:
    return {
        "precision_tier3": m.precision_top >= GATES_B["precision_tier3"],
        "precision_tier2": m.precision_mid >= GATES_B["precision_tier2"],
        "recall": m.recall >= GATES_B["recall"],
        "false_flag_rate": m.false_flag_rate <= GATES_B["false_flag_rate_max"],
    }


def shadow_compare(old: Iterable[ScoredAccount], new: Iterable[ScoredAccount]) -> dict:
    """Shadow mode: where a candidate model's labels differ from the live model's."""
    o = {tkey(r.connection): r.label for r in old}
    changes: dict[str, int] = {}
    for r in new:
        k = tkey(r.connection)
        if k in o and o[k] != r.label:
            t = f"{o[k].value}->{r.label.value}"
            changes[t] = changes.get(t, 0) + 1
    return {"compared": len(o), "changed": sum(changes.values()), "transitions": changes}


def review_sample(results: list[ScoredAccount], share: float = 0.01, seed: int = 0) -> list[ScoredAccount]:
    """Weekly human review: a random 1% of flags, stratified by platform and score band."""
    rng = random.Random(seed)
    strata: dict[tuple, list[ScoredAccount]] = {}
    for r in results:
        if r.label in (Label.likely_bot, Label.suspicious, Label.low_confidence):
            strata.setdefault((r.connection.platform.value, r.label.value), []).append(r)
    out: list[ScoredAccount] = []
    for items in strata.values():
        out.extend(rng.sample(items, max(1, round(len(items) * share))))
    return out


def main() -> None:  # pragma: no cover - CLI
    from .purge.signals import SiteScorer
    from .scoring import Scorer

    print("Module A — seeded network (500 real + 40 bots + 10 clones + 15 bad follows)")
    s = seeded_network()
    res = Scorer(now=datetime(2026, 6, 1, tzinfo=timezone.utc), stock_hashes=[]).score(s.conns)
    m = metrics_a(res, s.truth)
    failed = [k for k, ok in gates_a(m).items() if not ok]
    for k, v in m.as_dict().items():
        print(f"  {k:18} {v:.4f}" if isinstance(v, float) else f"  {k:18} {v}")
    for k, ok in gates_a(m).items():
        print(f"  gate {k:22} {'PASS' if ok else 'FAIL'}")
    b = bias_check(res, s.truth, s.group)
    if not b["ok"]:
        failed.append("bias")
    print(f"  bias check           {'PASS' if b['ok'] else 'FAIL'} {b['per_group']}")
    clones_found = sum(1 for r in res if tkey(r.connection) in s.clones and r.is_clone)
    print(f"  clone traps fired    {clones_found}/{len(s.clones)}")

    print("\nRed team — evasive bots (30 per level) in a 500-person network")
    rt, lv = red_team_network()
    for k, v in red_team_report(Scorer(now=datetime(2026, 6, 1, tzinfo=timezone.utc)).score(rt.conns), rt.truth, lv).items():
        print(f"  {k:18} {v:.4f}")

    print("\nModule B — seeded site (3000 real + 300 bots)")
    accs, truth = seeded_site()
    mb = metrics_b(SiteScorer().score(accs), truth)
    failed += [k for k, ok in gates_b(mb).items() if not ok]
    for k, v in mb.as_dict().items():
        print(f"  {k:18} {v:.4f}" if isinstance(v, float) else f"  {k:18} {v}")
    for k, ok in gates_b(mb).items():
        print(f"  gate {k:22} {'PASS' if ok else 'FAIL'}")
    if failed:
        raise SystemExit(f"\nFAILED gates: {failed}")


if __name__ == "__main__":  # pragma: no cover
    main()
