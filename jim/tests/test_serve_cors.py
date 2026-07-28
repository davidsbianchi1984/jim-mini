"""``python -m jim serve`` must answer the packaged console.

The installer ships only the console; the API it calls is started by hand.
With CORS closed the console's every request dies as "Failed to fetch" —
so a loopback ``serve`` defaults CORS open (the posture the in-app hint has
always instructed), while ``--no-cors`` and a non-loopback bind keep it
closed.
"""

from __future__ import annotations

import jim.__main__ as launcher


def _serve(monkeypatch, argv):
    """Run ``main(argv)`` with uvicorn.run captured instead of blocking."""
    calls: dict = {}

    def fake_run(app, host, port):
        calls["app"], calls["host"], calls["port"] = app, host, port

    import uvicorn

    monkeypatch.setattr(uvicorn, "run", fake_run)
    monkeypatch.delenv("JIM_CORS_ORIGINS", raising=False)
    assert launcher.main(argv) == 0
    assert calls["app"] == "jim.api:app"
    return calls


def test_loopback_serve_defaults_cors_open_for_the_console(monkeypatch):
    _serve(monkeypatch, ["serve"])
    import os

    assert os.environ.get("JIM_CORS_ORIGINS") == "*"


def test_no_cors_keeps_the_closed_posture(monkeypatch):
    _serve(monkeypatch, ["serve", "--no-cors"])
    import os

    assert os.environ.get("JIM_CORS_ORIGINS") is None


def test_a_non_loopback_bind_never_defaults_cors_open(monkeypatch):
    _serve(monkeypatch, ["serve", "--host", "0.0.0.0"])
    import os

    assert os.environ.get("JIM_CORS_ORIGINS") is None


def test_an_explicit_allowlist_is_never_overwritten(monkeypatch):
    import os

    monkeypatch.setenv("JIM_CORS_ORIGINS", "https://example.test")

    def fake_run(app, host, port):
        pass

    import uvicorn

    monkeypatch.setattr(uvicorn, "run", fake_run)
    assert launcher.main(["serve"]) == 0
    assert os.environ["JIM_CORS_ORIGINS"] == "https://example.test"
