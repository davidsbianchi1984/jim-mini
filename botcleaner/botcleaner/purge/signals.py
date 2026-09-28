"""Module B scoring: site-wide bot signals over a platform owner's own accounts.

Same noisy-OR combination as Module A (see ``botcleaner.scoring``) with signals
only a platform can see: signup velocity per IP/subnet/ASN/device fingerprint,
disposable and sequential emails, CAPTCHA timing, headless-browser markers,
honeypots, templated posts across accounts, data-centre logins and inhuman
action timing. Accounts are then grouped into rings.
"""
from __future__ import annotations

import ipaddress
import re
import statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel, Field

WEIGHTS = {
    "signup_velocity_ip": 0.45,
    "signup_velocity_subnet": 0.30,
    "signup_velocity_asn": 0.20,
    "signup_velocity_fingerprint": 0.55,
    "disposable_email": 0.40,
    "sequential_email": 0.55,
    "captcha_timing": 0.35,
    "headless": 0.65,
    "honeypot": 0.85,
    "templated_posts": 0.55,
    "datacenter_ip": 0.35,
    "inhuman_timing": 0.60,
    "random_username": 0.20,
    "no_verification": 0.10,
}

DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com", "temp-mail.org", "yopmail.com",
    "trashmail.com", "sharklasers.com", "getnada.com", "dispostable.com", "maildrop.cc", "throwawaymail.com",
    "fakeinbox.com", "mintemail.com", "mohmal.com", "emailondeck.com", "tempail.com", "burnermail.io",
    "discard.email", "spamgourmet.com", "mailnesia.com", "moakt.com", "tmpmail.org", "1secmail.com",
}

# Hosting/cloud ASNs (subset; owners can extend via config).
DATACENTER_ASNS = {
    "AS16509", "AS14618", "AS8075", "AS15169", "AS396982", "AS14061", "AS16276", "AS24940", "AS63949",
    "AS20473", "AS45102", "AS132203", "AS12876", "AS51167", "AS9009", "AS60068", "AS212238", "AS13335",
}

HEADLESS_UA = re.compile(r"(HeadlessChrome|PhantomJS|puppeteer|playwright|selenium|python-requests|curl/|Go-http-client|node-fetch|axios/)", re.I)


class SiteAccount(BaseModel):
    account_id: str
    username: str = ""
    display_name: str = ""
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    signup_ip: Optional[str] = None
    signup_asn: Optional[str] = None
    device_fingerprint: Optional[str] = None
    user_agent: Optional[str] = None
    webdriver: Optional[bool] = None             # navigator.webdriver reported by the SDK
    captcha_solve_ms: Optional[int] = None
    honeypot_filled: bool = False                # hidden form field had a value
    honeypot_link_hit: bool = False              # followed an invisible link / bait endpoint
    login_ips: list[str] = Field(default_factory=list)
    login_asns: list[str] = Field(default_factory=list)
    action_timestamps: list[datetime] = Field(default_factory=list)
    posts: list[str] = Field(default_factory=list)
    email_verified: Optional[bool] = None
    phone_verified: Optional[bool] = None
    tags: list[str] = Field(default_factory=list)  # e.g. staff, partner, integration


class SiteReason(BaseModel):
    code: str
    text: str
    weight: float


class SiteScore(BaseModel):
    account_id: str
    score: float
    reasons: list[SiteReason]
    ring_id: Optional[str] = None


def _utc(d: Optional[datetime]) -> Optional[datetime]:
    if d is None:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def subnet_of(ip: Optional[str]) -> Optional[str]:
    if not ip:
        return None
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return None
    prefix = 24 if addr.version == 4 else 48
    return str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False))


def _email_parts(email: Optional[str]) -> tuple[str, str]:
    if not email or "@" not in email:
        return "", ""
    local, domain = email.lower().rsplit("@", 1)
    local = local.split("+", 1)[0]
    return local, domain


_TEMPLATE_SUBS = [
    (re.compile(r"https?://\S+|www\.\S+"), "<url>"),
    (re.compile(r"@\w+"), "<user>"),
    (re.compile(r"\d+"), "<n>"),
    (re.compile(r"[^\w<>\s]"), ""),
    (re.compile(r"\s+"), " "),
]


def template_of(text: str) -> str:
    t = text.lower()
    for rx, rep in _TEMPLATE_SUBS:
        t = rx.sub(rep, t)
    return t.strip()


def _random_username(u: str) -> bool:
    u = u.lower()
    if len(u) < 8:
        return False
    if sum(ch.isdigit() for ch in u) / len(u) >= 0.4:
        return True
    return bool(re.search(r"[bcdfghjklmnpqrstvwxz]{5,}", re.sub(r"[^a-z]", "", u)))


class SiteScorer:
    def __init__(self, velocity_window: timedelta = timedelta(hours=1), velocity_threshold: int = 5,
                 extra_disposable: set[str] | None = None, extra_datacenter_asns: set[str] | None = None,
                 min_template_accounts: int = 3):
        self.window = velocity_window
        self.threshold = velocity_threshold
        self.disposable = DISPOSABLE_DOMAINS | (extra_disposable or set())
        self.dc_asns = DATACENTER_ASNS | (extra_datacenter_asns or set())
        self.min_template = min_template_accounts

    def _velocity(self, accounts: list[SiteAccount], keyfn) -> dict[str, int]:
        """For each account, the most signups sharing its key within any one window."""
        groups: dict[str, list[tuple[datetime, str]]] = defaultdict(list)
        for a in accounts:
            k, t = keyfn(a), _utc(a.created_at)
            if k and t:
                groups[k].append((t, a.account_id))
        out: dict[str, int] = {}
        for items in groups.values():
            items.sort()
            j = 0
            for i in range(len(items)):
                while items[i][0] - items[j][0] > self.window:
                    j += 1
                n = i - j + 1
                for _, aid in items[j:i + 1]:
                    out[aid] = max(out.get(aid, 0), n)
        return out

    def score(self, accounts: list[SiteAccount]) -> list[SiteScore]:
        vel_ip = self._velocity(accounts, lambda a: a.signup_ip)
        vel_sub = self._velocity(accounts, lambda a: subnet_of(a.signup_ip))
        vel_asn = self._velocity(accounts, lambda a: a.signup_asn)
        vel_fp = self._velocity(accounts, lambda a: a.device_fingerprint)

        # Sequential emails: same stem + number, e.g. jane.doe1@, jane.doe2@, jane.doe3@
        stems: dict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
        for a in accounts:
            local, domain = _email_parts(a.email)
            m = re.match(r"^(.*?)(\d+)$", local)
            if m and m.group(1):
                stems[(m.group(1), domain)].append((int(m.group(2)), a.account_id))
        sequential: set[str] = set()
        for items in stems.values():
            if len(items) >= 4:
                nums = sorted(n for n, _ in items)
                steps = [b - a for a, b in zip(nums, nums[1:])]
                if steps and statistics.median(steps) <= 3:
                    sequential.update(aid for _, aid in items)

        # Templated posts shared across accounts.
        # Only templates with fill-in slots (links, mentions) or long bodies count: short
        # everyday phrases ("great post, thanks") are shared by thousands of real people.
        tmpl_accounts: dict[str, set[str]] = defaultdict(set)
        for a in accounts:
            for p in a.posts:
                t = template_of(p)
                if len(t) >= 15 and ("<url>" in t or "<user>" in t or len(t.split()) >= 12):
                    tmpl_accounts[t].add(a.account_id)
        created = {a.account_id: _utc(a.created_at) for a in accounts}
        templated: dict[str, tuple[int, float]] = {}
        for t, ids in tmpl_accounts.items():
            if len(ids) < self.min_template:
                continue
            # Coordinated campaigns come from accounts made close together; organic reuse doesn't.
            times = sorted(c for c in (created[i] for i in ids) if c)
            spread = (times[-1] - times[0]).days if len(times) >= 2 else 0
            strength = 1.0 if spread <= 30 else 0.5 if spread <= 180 else 0.25
            for aid in ids:
                if aid not in templated or templated[aid][1] < strength:
                    templated[aid] = (len(ids), strength)

        results: list[SiteScore] = []
        for a in accounts:
            sigs: list[tuple[str, float, str]] = []
            add = lambda c, s, t: sigs.append((c, max(0.0, min(1.0, s)), t))  # noqa: E731
            aid = a.account_id
            if vel_fp.get(aid, 0) >= self.threshold:
                add("signup_velocity_fingerprint", 1.0, f"{vel_fp[aid]} accounts created from the same device within an hour")
            if vel_ip.get(aid, 0) >= self.threshold:
                add("signup_velocity_ip", 1.0, f"{vel_ip[aid]} accounts created from the same IP address within an hour")
            elif vel_sub.get(aid, 0) >= self.threshold * 2:
                add("signup_velocity_subnet", 1.0, f"{vel_sub[aid]} accounts created from the same network block within an hour")
            elif vel_asn.get(aid, 0) >= self.threshold * 10:
                add("signup_velocity_asn", 1.0, f"{vel_asn[aid]} accounts created from the same provider within an hour")
            local, domain = _email_parts(a.email)
            if domain in self.disposable:
                add("disposable_email", 1.0, f"Signed up with a disposable email address ({domain})")
            if aid in sequential:
                add("sequential_email", 1.0, "Email is one of a numbered series of addresses")
            if a.captcha_solve_ms is not None:
                if a.captcha_solve_ms < 800:
                    add("captcha_timing", 1.0, f"Solved the CAPTCHA in {a.captcha_solve_ms} ms, faster than a person can")
                elif a.captcha_solve_ms > 90_000:
                    add("captcha_timing", 0.5, "CAPTCHA took unusually long, typical of solver services")
            if a.webdriver or (a.user_agent and HEADLESS_UA.search(a.user_agent)):
                add("headless", 1.0, "Signed up from an automated or headless browser")
            if a.honeypot_filled or a.honeypot_link_hit:
                add("honeypot", 1.0, "Filled in a hidden form field or followed an invisible link only bots can see")
            if aid in templated:
                n, strength = templated[aid]
                add("templated_posts", min(1.0, 0.6 + n / 50) * strength,
                    f"Posts the same templated message as {n - 1} other accounts")
            asns = set(a.login_asns) | ({a.signup_asn} if a.signup_asn else set())
            if asns & self.dc_asns:
                add("datacenter_ip", 1.0, "Logs in from data-centre / cloud-hosting IP addresses")
            ts = sorted(_utc(t) for t in a.action_timestamps)
            if len(ts) >= 8:
                gaps = [(y - x).total_seconds() for x, y in zip(ts, ts[1:])]
                mean = statistics.mean(gaps)
                # One same-second pair is normal (double-clicks, coarse timestamps); a habit of it isn't.
                fast = sum(g < 1.0 for g in gaps) / len(gaps)
                if fast >= 0.3 or (mean > 0 and statistics.pstdev(gaps) / mean < 0.05):
                    add("inhuman_timing", 1.0, "Acts with machine-like speed or perfectly regular timing")
            if a.username and _random_username(a.username):
                add("random_username", 1.0, f"Username looks randomly generated ({a.username})")
            if a.email_verified is False and a.phone_verified is not True:
                add("no_verification", 1.0, "Never verified an email or phone number")

            reasons = [SiteReason(code=c, text=t, weight=WEIGHTS[c] * s) for c, s, t in sigs]
            reasons.sort(key=lambda r: r.weight, reverse=True)
            p = 1.0
            for r in reasons:
                p *= 1 - r.weight
            results.append(SiteScore(account_id=aid, score=round(100 * (1 - p), 1), reasons=reasons))

        self._rings(accounts, results, tmpl_accounts)
        return results

    def _rings(self, accounts: list[SiteAccount], results: list[SiteScore], tmpl_accounts: dict[str, set[str]]) -> None:
        """Group suspicious accounts that share a device, IP, or post template."""
        by_id = {r.account_id: r for r in results}
        suspects = {r.account_id for r in results if r.score >= 60}
        parent = {a: a for a in suspects}

        def find(i: str) -> str:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        def union_all(ids: list[str]) -> None:
            ids = [i for i in ids if i in parent]
            for i in ids[1:]:
                parent[find(i)] = find(ids[0])

        shared: dict[tuple[str, str], list[str]] = defaultdict(list)
        for a in accounts:
            if a.account_id not in suspects:
                continue
            for kind, v in (("fp", a.device_fingerprint), ("ip", a.signup_ip)):
                if v:
                    shared[(kind, v)].append(a.account_id)
        for ids in shared.values():
            union_all(ids)
        for ids in tmpl_accounts.values():
            if len(ids) >= self.min_template:
                union_all(sorted(ids))
        groups: dict[str, list[str]] = defaultdict(list)
        for a in suspects:
            groups[find(a)].append(a)
        for root, members in groups.items():
            if len(members) >= 3:
                rid = "ring-" + root
                for m in members:
                    by_id[m].ring_id = rid
