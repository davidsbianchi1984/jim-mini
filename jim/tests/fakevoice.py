"""A voice door that answers the way `docker/voice` does, without a socket.

The one seam :mod:`jim.telephony` opens is :func:`jim.telephony._request`;
this replaces it, so every test of the phone line drives the real
normalisation, refusals, placement record, standing proof and cache, and
only the wire is pretend. What the fake saw is kept on it, so a test can
assert that nothing was asked — the offline and 911 tests turn on that.
"""

from __future__ import annotations

from jim import telephony


class FakeVoice:
    def __init__(self, monkeypatch, *, word: str = "ready",
                 provider: str = "twilio", down: bool = False,
                 refuse_secret: bool = False, jim_secret_accepted: bool = True,
                 from_number: bool = True, webhooks: str = "reachable",
                 refuse_to: tuple[str, ...] = (), place_status: int = 201,
                 place_detail: str | None = None,
                 note: str | None = None, fix: str | None = None):
        self.word = word
        self.provider = provider
        self.down = down
        self.refuse_secret = refuse_secret
        self.jim_secret_accepted = jim_secret_accepted
        self.from_number = from_number
        self.webhooks = webhooks
        self.refuse_to = frozenset(refuse_to)
        self.place_status = place_status
        self.place_detail = place_detail
        self.note = note
        self.fix = fix
        self.seen: list[tuple[str, str, dict | None]] = []
        self.placed: list[dict] = []
        self.standing_reads = 0
        monkeypatch.setattr(telephony, "_request", self._request)

    # The wire, pretend.
    def _request(self, method: str, path: str, body: dict | None = None,
                 timeout: float = 5.0) -> tuple[int, dict]:
        self.seen.append((method, path, body))
        if self.down:
            raise telephony.SidecarUnreachable(
                f"the voice door at {telephony.url()} did not answer: "
                "[Errno 111] Connection refused")
        if self.refuse_secret:
            return 403, {"detail": "invalid voice adapter token"}
        if method == "GET" and path == "/standing":
            self.standing_reads += 1
            return 200, {"word": self.word, "provider": self.provider,
                         "authenticated": True,
                         "from_number": self.from_number,
                         "webhooks": self.webhooks,
                         "jim_secret_accepted": self.jim_secret_accepted,
                         "detail": self.note, "fix": self.fix,
                         "checked_at": "2026-09-03T00:00:00+00:00"}
        if method == "POST" and path == "/calls":
            body = body or {}
            if self.place_status != 201 or body.get("to") in self.refuse_to:
                return (self.place_status if self.place_status != 201 else 422), {
                    "detail": self.place_detail
                    or "the house refused this number: 21211 invalid To"}
            self.placed.append(body)
            return 201, {"placed": True, "provider": self.provider,
                         "provider_call_id": f"CA{len(self.placed):04d}"}
        return 404, {"detail": "no such door"}


SECRET = "s3cret-shared-with-the-sidecar"
#: What the sidecar presents on the call-id doors once the secret is set.
AS_SIDECAR = {"authorization": f"Bearer {SECRET}"}


def wire(monkeypatch, url: str = "http://voice:8800",
         secret: str = SECRET, **kw) -> FakeVoice:
    """A configured, answering voice door — the box with a phone line."""
    monkeypatch.setenv("JIM_VOICE_URL", url)
    monkeypatch.setenv("JIM_VOICE_SECRET", secret)
    telephony.forget_standing()
    return FakeVoice(monkeypatch, **kw)


SITU = {"who": "Ada", "about": "a fall with no answer",
        "what_to_do": "check on her"}
TWO = [{"name": "Rosa", "channel": "+15551110000"},
       {"name": "Sam", "channel": "+15552220000"}]
