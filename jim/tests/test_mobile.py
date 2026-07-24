"""Running the Guardian from a phone: pairing details and the served console."""

from pathlib import Path

from jim import mobile


def test_pairing_gives_a_reachable_address_not_loopback(client, monkeypatch):
    monkeypatch.setenv("JIM_LAN_HOST", "192.168.1.42")
    r = client.get("/pair")
    assert r.status_code == 200
    body = r.json()
    # The phone must get an address it can actually reach — 127.0.0.1 on a
    # phone means the phone itself, which is the whole trap this avoids.
    assert body["console_url"].startswith("http://192.168.1.42:")
    assert body["console_url"].endswith("/app/")
    assert "local network" in body["note"].lower()
    assert body["how"]


def test_pairing_says_so_when_no_reachable_address_exists(client, monkeypatch):
    """A loopback answer is useless on a phone, so pairing calls it out and
    says how to fix it instead of handing over an address that can't work."""
    monkeypatch.setenv("JIM_LAN_HOST", "127.0.0.1")
    body = client.get("/pair").json()
    assert body["reachable"] is False
    assert any("cannot reach 127.0.0.1" in step for step in body["how"])
    assert any("JIM_LAN_HOST" in step for step in body["how"])


def test_pairing_qr_encodes_the_console_url(client, monkeypatch):
    monkeypatch.setenv("JIM_LAN_HOST", "192.168.1.42")
    r = client.get("/pair/qr.svg")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/svg+xml")
    assert b"<svg" in r.content


def test_console_is_served_when_built(tmp_path, monkeypatch):
    """When app/ has been built, the API serves it at /app — one origin for
    UI and API, so a phone needs no configuration."""
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html><title>JIM Guardian</title>")
    (dist / "manifest.webmanifest").write_text('{"name":"JIM Guardian"}')
    monkeypatch.setenv("JIM_CONSOLE_DIR", str(dist))

    from fastapi.testclient import TestClient
    from jim.api import create_app

    with TestClient(create_app()) as c:
        assert c.get("/health").json()["console"] is True
        index = c.get("/app/")
        assert index.status_code == 200
        assert "JIM Guardian" in index.text
        assert c.get("/app/manifest.webmanifest").status_code == 200
        # Mounting the console must not shadow the API.
        assert c.get("/health").status_code == 200


def test_console_absent_leaves_the_api_headless(client, monkeypatch):
    """No build, no mount — the API stays fully usable on its own."""
    monkeypatch.setenv("JIM_CONSOLE_DIR", "/nonexistent/dist")
    assert mobile.console_dir() is None
    assert client.get("/health").status_code == 200


def test_shipped_console_declares_itself_installable():
    """The real console in app/: a manifest, an icon, and a service worker
    that never caches API traffic (stale health data is worse than none)."""
    public = Path(__file__).resolve().parents[2] / "app" / "public"
    manifest = (public / "manifest.webmanifest").read_text()
    assert '"display": "standalone"' in manifest
    assert (public / "icon.svg").exists()
    sw = (public / "sw.js").read_text()
    assert "isShellAsset" in sw and "API traffic: untouched" in sw
