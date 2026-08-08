"""What a page promises a browser before it says anything else.

These products serve a handful of HTML pages that a person reaches **without
an account, on a device that is not theirs**: the sticker a stranger kneels
over, the sealed-carrier card, the page a sign-in provider sends a browser
back to. Until 0.59.3 every one of them went out with no
`Content-Security-Policy`, no `X-Content-Type-Options`, no `X-Frame-Options`
and no `Referrer-Policy` — measured over HTTP, because a `TestClient` reads
none of those and a browser reads all of them.

That was the standing invitation. The thing that walked through it was an
unescaped query parameter on the OAuth callback, rendered straight into the
page: `?error=<script>…</script>` came back verbatim, executing on the
product's own origin. Escaping is the fix for that one. This is the layer that
makes the *next* one harmless.

## Why a nonce rather than `'unsafe-inline'`

A CSP with `script-src 'unsafe-inline'` permits exactly the thing an injected
`<script>` needs, and would have stopped nothing above. So the pages that
carry an inline script emit it through :func:`script_open`, which stamps the
per-response nonce, and the policy names that nonce and nothing else. An
injected tag has no nonce and does not run.

`style-src` keeps `'unsafe-inline'`: the stylesheets are constants in this
package, no page interpolates into them, and a nonce there would buy nothing
a reader would ever notice.

    asked     is the page correct
    mattered  what can a page do that is not
"""

from __future__ import annotations

import contextvars
import html
import secrets

#: Set per request, read by the page builders. The same shape the request-key
#: middleware uses, for the same reason: the value belongs to one request and
#: a stale one is a false statement about the next.
_NONCE: contextvars.ContextVar[str] = contextvars.ContextVar(
    "csp_nonce", default="")

#: Sent on every HTML response. Fixed rather than computed: none of them
#: depends on the page.
HEADERS = {
    # Never let a browser second-guess the declared type. An SVG sniffed as
    # HTML is a script; these products serve SVG on public routes.
    "x-content-type-options": "nosniff",
    # A page reached from a QR sticker should not tell the next host where the
    # reader came from — the referrer is the beacon they scanned.
    "referrer-policy": "no-referrer",
    # Belt to the policy's braces, for readers on browsers that predate it.
    "x-frame-options": "DENY",
}


def new_nonce() -> str:
    """Mint the nonce for this request and make it readable downstream."""
    value = secrets.token_urlsafe(16)
    _NONCE.set(value)
    return value


def nonce() -> str:
    return _NONCE.get()


def script_open() -> str:
    """The opening tag for a page's own inline script.

    Falls back to a bare tag when no nonce is set, which happens only when a
    builder is called outside a request — a test, a preview. That page is not
    served to anyone, and a bare tag there fails loudly under the policy
    rather than silently shipping an unprotected one.
    """
    value = nonce()
    return (f'<script nonce="{html.escape(value)}">' if value
            else "<script>")


def policy(value: str) -> str:
    """The Content-Security-Policy for a self-contained page.

    `default-src 'none'` because these pages fetch nothing: no font host, no
    analytics, no CDN. Everything they need is inline or same-origin, so the
    policy can start from nothing and name the exceptions.
    """
    return "; ".join((
        "default-src 'none'",
        "img-src 'self' data:",
        "style-src 'unsafe-inline'",
        f"script-src 'nonce-{value}'" if value else "script-src 'none'",
        "connect-src 'self'",
        "form-action 'self'",
        "base-uri 'none'",
        "frame-ancestors 'none'",
    ))
