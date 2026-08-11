"""Going to the imported link, instead of waiting for a paste.

A ``collect`` connection has always known the account it points at — platform
and handle, enough to build the public URL — and has never once visited it.
``POST /social/connection/{cid}/collect`` stores whatever the owner pastes,
which means the door named *pull the account's posts in as consented context*
was in truth *retype the account's posts in*. The Guardian understands more
of a person's life when it can read the page that person already keeps.

    asked     can collected content inform guidance
    mattered  can the connection fetch it from the address it was given

The fetch half: given the public URL a connection already implies, get the
page and reduce it to the words a person would read there — the title, the
bio line the platform puts in its metadata, and the visible text, capped.
The route that calls this ingests the result as a ``social:<platform>``
context event (sealed into the PDI vault when one is configured), exactly
like a pasted item, with the URL and the fetch time in the content.

What it refuses:

* **Offline deployments do not fetch.** ``offline.enabled()`` is the switch
  every other outbound path honours; the zero-internet guarantee cannot be
  broken because a button was pressed. The refusal says so.
* **A connection without a handle has no address.** 400, with the fix named.
* **Only public pages, as a browser sees them** — no credentials, no
  cookies. This reads what anyone on earth could read at that URL.
"""

from __future__ import annotations

import html as _html
import re
import urllib.request

from . import offline

_MAX_BYTES = 512 * 1024
_MAX_TEXT = 4000
_TIMEOUT = 10.0


def fetch(url: str) -> str:
    """The page as a browser would receive it, capped and decoded leniently.

    The gate lives here, in the function that opens the socket, not only in
    the route above it — a second caller added tomorrow inherits the check
    instead of remembering it.
    """
    offline.allow(url, "the profile-page fetch")
    req = urllib.request.Request(
        url, headers={"User-Agent": "JIM-guardian-context/1.0"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        raw = resp.read(_MAX_BYTES)
    return raw.decode("utf-8", errors="replace")


_STRIP = re.compile(r"<(script|style|noscript)\b.*?</\1>", re.S | re.I)
_TAGS = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def _meta(html: str, *names: str) -> str | None:
    """First matching <meta property/name=… content=…>, either attribute order."""
    for name in names:
        for pat in (
            r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']%s["\']',
        ):
            m = re.search(pat % re.escape(name), html, re.I)
            if m:
                return _html.unescape(m.group(1)).strip()
    return None


def extract(html: str) -> dict:
    """{title, description, text} — the words a reader would take away."""
    title = _meta(html, "og:title", "twitter:title")
    if not title:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
        title = _html.unescape(m.group(1)).strip() if m else None
    description = _meta(html, "og:description", "twitter:description",
                        "description")
    body = _TAGS.sub(" ", _STRIP.sub(" ", html))
    text = _WS.sub(" ", _html.unescape(body)).strip()[:_MAX_TEXT]
    return {"title": title, "description": description, "text": text}
