"""Browser tests of every guided and assisted path (PRD section 7.9), plus the console and appeals portal.

Opt-in because they need Chromium:  BOTCLEANER_UI_TESTS=1 pytest tests/test_ui.py
Set CHROMIUM_PATH to use a specific browser binary. CI runs these weekly.
Mobile paths are covered by the phone-sized viewport and the iOS/Android steps.
"""
import json
import os
import shutil
import socket
import tempfile
import threading
import time
from pathlib import Path

import pytest

if os.environ.get("BOTCLEANER_UI_TESTS") != "1":
    pytest.skip("set BOTCLEANER_UI_TESTS=1 to run browser tests", allow_module_level=True)
sync_api = pytest.importorskip("playwright.sync_api")

import uvicorn  # noqa: E402

from botcleaner import evaluation as ev  # noqa: E402
from botcleaner.api import create_app  # noqa: E402

EXT = Path(__file__).resolve().parents[1] / "extension"
PROFILE_HTML = "<!doctype html><html><body><h1>Profile</h1><button id='remove'>Remove</button></body></html>"


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    d = tmp_path_factory.mktemp("ui")
    app = create_app(str(d / "ui.sqlite3"), worker=False)
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    srv = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    t = threading.Thread(target=srv.run, daemon=True)
    t.start()
    while not srv.started:
        time.sleep(0.05)
    now = int(time.time())
    real = [{"title": "", "string_list_data": [{"href": f"https://www.instagram.com/friend.{i}", "value": f"friend.{i}", "timestamp": now - 86400 * (100 + 37 * i)}]} for i in range(40)]
    bots = [{"title": "", "string_list_data": [{"href": f"https://www.instagram.com/lucy{48291730 + i}", "value": f"lucy{48291730 + i}", "timestamp": now - 86400 * 30 + i * 60}]} for i in range(12)]
    (d / "followers_1.json").write_text(json.dumps(real + bots))
    accs, _ = ev.seeded_site(n_real=200, n_bots=60)
    (d / "accounts.json").write_text(json.dumps([a.model_dump(mode="json") for a in accs]))
    yield {"url": f"http://127.0.0.1:{port}", "dir": d, "app": app}
    srv.should_exit = True


def launch(p, **kw):
    exe = os.environ.get("CHROMIUM_PATH")
    return p.chromium.launch(executable_path=exe, **kw) if exe else p.chromium.launch(**kw)


@pytest.mark.parametrize("width,device", [(1280, "web"), (390, "ios")])
def test_personal_cleaner_guided_path(server, width, device):
    B, d = server["url"], server["dir"]
    errors = []
    with sync_api.sync_playwright() as p:
        br = launch(p)
        pg = br.new_page(viewport={"width": width, "height": 900})
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(B + "/")
        pg.fill("#email", f"guided-{width}@example.com")
        pg.click("#signup")
        pg.wait_for_selector("#appView:not(.hidden)")
        pg.set_input_files("#impFile", str(d / "followers_1.json"))
        pg.click("#impGo")
        pg.click("[data-review=instagram]")
        pg.click("#fTabs [data-t=suspicious]")
        pg.wait_for_selector("#flagRows tr")
        assert pg.locator("#flagRows tr").count() == 12
        pg.check("#selAll")
        pg.click("#removeSel")
        pg.select_option("#cMode", "guided")
        pg.click("#cOk")
        pg.wait_for_selector("#gDev")
        pg.select_option("#gDev", device)
        pg.wait_for_timeout(300)
        assert pg.locator("#jobPanel ol.steps li").count() >= 3
        pg.locator("[data-ok]").first.click()
        pg.wait_for_timeout(300)
        assert "pending" in pg.inner_text("#jobPanel")
        # Every platform, device and action has steps on the Removal steps page.
        pg.click("#tabs [data-tab=howto]")
        for plat in ("x", "facebook", "instagram", "tiktok", "linkedin"):
            pg.select_option("#iPlatform", plat)
            for dev in ("web", "ios", "android"):
                pg.select_option("#iDevice", dev)
                for act in pg.eval_on_selector_all("#iAction option", "os => os.map(o => o.value)"):
                    pg.select_option("#iAction", act)
                    pg.wait_for_function("document.querySelectorAll('#iBest ol li').length >= 3")
        assert pg.evaluate("document.documentElement.scrollWidth") <= width
        br.close()
    assert errors == []


def test_assisted_path_web_app(server):
    B, d = server["url"], server["dir"]
    with sync_api.sync_playwright() as p:
        br = launch(p)
        ctx = br.new_context()
        ctx.route("https://www.instagram.com/**", lambda r: r.fulfill(body=PROFILE_HTML, content_type="text/html"))
        pg = ctx.new_page()
        pg.goto(B + "/")
        pg.fill("#email", "assisted@example.com")
        pg.click("#signup")
        pg.wait_for_selector("#appView:not(.hidden)")
        pg.set_input_files("#impFile", str(d / "followers_1.json"))
        pg.click("#impGo")
        pg.click("[data-review=instagram]")
        pg.click("#fTabs [data-t=suspicious]")
        pg.wait_for_selector("#flagRows tr")
        pg.locator("#flagRows input[type=checkbox]").first.check()
        pg.click("#removeSel")
        pg.select_option("#cMode", "assisted")
        pg.click("#cOk")
        with ctx.expect_page() as newp:
            pg.click("#nextBtn")
        profile = newp.value
        profile.wait_for_load_state()
        assert "instagram.com" in profile.url
        pg.click("#aDone")
        pg.wait_for_timeout(300)
        assert "pending" in pg.inner_text("#jobPanel")
        br.close()


def test_assisted_path_browser_extension(server):
    """The extension opens the profile and shows steps; it never clicks the page's buttons."""
    B, d = server["url"], server["dir"]
    from fastapi.testclient import TestClient

    c = TestClient(server["app"])
    tok = c.post("/api/signup", json={"email": "ext@example.com"}).json()["token"]
    H = {"Authorization": f"Bearer {tok}"}
    c.post("/api/import/instagram", headers=H, files={"file": ("followers_1.json", (d / "followers_1.json").read_bytes(), "application/json")})
    bots = c.get("/api/flags?tab=suspicious", headers=H).json()[:2]
    job = c.post("/api/removals", headers=H, json={"platform": "instagram", "mode": "assisted",
                 "accounts": [{"account_id": b["account_id"], "direction": "follower"} for b in bots]}).json()

    # Test copy of the extension with the local server pre-granted (the real one asks at runtime).
    ext = Path(tempfile.mkdtemp()) / "ext"
    shutil.copytree(EXT, ext)
    m = json.loads((ext / "manifest.json").read_text())
    m["host_permissions"] = [B + "/*"]
    (ext / "manifest.json").write_text(json.dumps(m))

    with sync_api.sync_playwright() as p:
        # Extensions need full Chromium; Playwright's default headless shell can't load them.
        kw = dict(headless=True, args=[f"--disable-extensions-except={ext}", f"--load-extension={ext}"])
        if os.environ.get("CHROMIUM_PATH"):
            kw["executable_path"] = os.environ["CHROMIUM_PATH"]
        else:
            kw["channel"] = "chromium"
        ctx = p.chromium.launch_persistent_context(tempfile.mkdtemp(), **kw)
        clicks = []
        ctx.expose_binding("reportClick", lambda src, x: clicks.append(x))
        ctx.add_init_script("document.addEventListener('click', e => { if (e.target.id === 'remove') window.reportClick(1); }, true)")
        ctx.route("https://www.instagram.com/**", lambda r: r.fulfill(body=PROFILE_HTML, content_type="text/html"))
        sw = ctx.service_workers[0] if ctx.service_workers else ctx.wait_for_event("serviceworker")
        sw.evaluate(f"chrome.storage.local.set({{server: {json.dumps(B)}, token: {json.dumps(tok)}}})")
        # Hand the extension a tab this test controls; it reuses its removal tab for each profile.
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("about:blank")
        sw.evaluate("chrome.tabs.query({}).then(t => chrome.storage.local.set({removalTab: t[0].id}))")
        res = sw.evaluate(f"openNext({json.dumps(job['id'])})")  # what the popup's "Open first profile" does
        assert res["state"] == "open"
        page.wait_for_url("https://www.instagram.com/**")
        page.wait_for_load_state()
        page.get_by_text("Remove follower: ").wait_for()
        assert page.locator("ol li").count() >= 3
        page.get_by_role("button", name="I removed them").click()
        page.get_by_role("button", name="Open next profile").wait_for()
        assert clicks == []  # nothing ever clicked the platform's own Remove button
        ctx.close()
    j = c.get(f"/api/removals/{job['id']}", headers=H).json()
    assert j["counts"].get("pending") == 1


def test_console_and_appeal_portal(server):
    B, d = server["url"], server["dir"]
    errors = []
    with sync_api.sync_playwright() as p:
        br = launch(p)
        pg = br.new_page(viewport={"width": 1280, "height": 900})
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("dialog", lambda dlg: dlg.accept())
        pg.goto(B + "/console")
        pg.fill("#tName", "Forumly")
        pg.click("#createTenant")
        pg.wait_for_selector("#kpis .card")
        pg.click("#tabs [data-tab=connect]")
        pg.set_input_files("#accFile", str(d / "accounts.json"))
        pg.click("#accUpload")
        pg.wait_for_timeout(500)
        pg.click("#tabs [data-tab=overview]")
        pg.click("#scanBtn")
        pg.wait_for_function("document.querySelector('#topReasons .progress')")
        pg.click("#tabs [data-tab=act]")
        pg.click("#dryBtn")
        pg.click("#execBtn")
        pg.wait_for_selector("#batchList table")
        key = pg.evaluate("localStorage.getItem('bc_key')")
        feed = pg.evaluate("k => fetch('/api/purge/feed', {headers: {'X-API-Key': k}}).then(r => r.json())", key)
        token = feed[0]["notice"]["appeal_url"].rsplit("/", 1)[-1]
        pg.goto(B + "/appeal/" + token)
        pg.fill("#st", "I'm a real person who runs the knitting forum.")
        pg.click("#send")
        pg.wait_for_selector("text=Appeal open")
        pg.goto(B + "/console")
        pg.click("#tabs [data-tab=appeals]")
        pg.locator("[data-ap][data-ok='1']").first.click()
        pg.wait_for_timeout(400)
        pg.goto(B + "/appeal/" + token)
        pg.wait_for_selector("text=Appeal approved")
        pg.goto(B + "/console")
        pg.click("#tabs [data-tab=audit]")
        pg.wait_for_selector("#auditOk .chip")
        assert "Chain intact" in pg.inner_text("#auditOk")
        br.close()
    assert errors == []
