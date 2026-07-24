"""Per-user language + guidance provenance.

Language: model text is generated in-language; safety-critical deterministic
content (CPR/AED playbooks, waiver terms) is hand-translated (es, fr) and
never machine-mangled. Provenance: every guidance response carries the
published sources it derives from — publisher, document, URL, and what each
supports — plus how and by what it was produced.
"""

from jim.tests.conftest import enroll


def test_language_catalog(client):
    r = client.get("/languages").json()
    codes = {l["code"]: l for l in r["languages"]}
    assert r["default"] == "en"
    # Every supported language now carries hand-translated safety content.
    assert all(l["safety_content_translated"] for l in r["languages"])


def test_set_and_get_language(client):
    uid = enroll(client)
    assert client.get(f"/language/{uid}").json()["language"] == "en"
    r = client.put(f"/language/{uid}", json={"language": "klingon"})
    assert r.status_code == 422
    r = client.put(f"/language/{uid}", json={"language": "es"}).json()
    assert r["language"] == "es" and r["label"] == "Español"
    assert client.get(f"/language/{uid}").json()["language"] == "es"


def test_cardiac_playbook_is_hand_translated(client):
    uid = enroll(client)
    client.put(f"/language/{uid}", json={"language": "es"})
    r = client.post(f"/monitor/{uid}", json={
        "movement": "collapse", "pulse": "absent"}).json()
    g = r["guidance"]
    assert g["language"] == "es"
    aid = g["first_aid"]
    assert aid["language"] == "es"
    assert aid["steps"][0].startswith("Llame")
    assert "metrónomo" in aid["pace"]["cue"]["audio"]
    # The offline stub can't translate free text — the response says so
    # instead of pretending.
    assert "translation_note" in g


def test_french_aed_steps(client):
    uid = enroll(client)
    client.put(f"/language/{uid}", json={"language": "fr"})
    r = client.post(f"/monitor/{uid}", json={"rhythm": "fibrillation"}).json()
    steps = r["guidance"]["first_aid"]["steps"]
    assert any("DEA" in s for s in steps)
    assert steps[0].startswith("Appelez")


def test_waiver_terms_localize(client):
    uid = enroll(client)
    client.put(f"/language/{uid}", json={"language": "es"})
    w = client.get(f"/waivers/{uid}").json()
    assert w["language"] == "es"
    assert any(t.startswith("Autorizo") for t in w["terms"])


def test_robot_coaching_speaks_in_language(client):
    uid = enroll(client)
    client.put(f"/language/{uid}", json={"language": "es"})
    rob = client.post(f"/robots/{uid}", json={"model": "neo"}).json()
    r = client.post(f"/robots/{uid}/{rob['id']}/command",
                    json={"command": "guide_first_aid", "arg": "cpr"}).json()
    assert r["spoken"][0].startswith("Llame")


def test_japanese_playbook_is_hand_translated(client):
    uid = enroll(client)
    client.put(f"/language/{uid}", json={"language": "ja"})
    r = client.post(f"/monitor/{uid}", json={
        "movement": "collapse", "pulse": "absent"}).json()
    assert "救急" in r["guidance"]["first_aid"]["steps"][0]


def test_unknown_strings_fall_back_to_english(client):
    # The fallback mechanism survives: a string without a hand translation
    # stays English rather than being machine-mangled.
    from jim import i18n
    assert i18n.tr("a string nobody translated", "ja") == \
        "a string nobody translated"


def test_every_language_has_complete_safety_coverage(client):
    # Guard against partial translations: every safety string is covered in
    # every supported language, and every playbook step / waiver term is
    # string-keyed to a translation entry.
    from jim import guardian, guidance, i18n
    langs = set(i18n.SUPPORTED) - {i18n.DEFAULT}
    for source, translations in i18n._STRINGS.items():
        missing = langs - set(translations)
        assert not missing, f"{source[:40]!r} missing {sorted(missing)}"
    keyed = set(i18n._STRINGS)
    for kind in ("cpr", "aed"):
        for step in guidance.playbook(kind)["steps"]:
            assert step in keyed, f"unkeyed playbook step: {step[:40]!r}"
    for term in guardian.WAIVER_TERMS:
        assert term in keyed, f"unkeyed waiver term: {term[:40]!r}"


# ---- provenance -------------------------------------------------------------

def test_guidance_carries_verifiable_provenance(client):
    uid = enroll(client)
    r = client.post(f"/monitor/{uid}", json={
        "movement": "collapse", "pulse": "absent"}).json()
    p = r["guidance"]["provenance"]
    assert "playbook" in p["method"]           # deterministic first aid
    assert p["generated_by"]                   # which model produced the text
    publishers = {e["publisher"] for e in p["evidence"]}
    assert "American Heart Association" in publishers
    urls = " ".join(e["url"] for e in p["evidence"])
    assert "cpr.heart.org" in urls
    assert all(e.get("supports") for e in p["evidence"])
    assert "verify" in p["disclaimer"]


def test_anxiety_guidance_cites_its_sources(client):
    uid = enroll(client)
    r = client.post(f"/monitor/{uid}", json={"heart_rate": 145}).json()
    p = r["guidance"]["provenance"]
    assert "model-generated" in p["method"]
    urls = " ".join(e["url"] for e in p["evidence"])
    assert "nhs.uk" in urls and "apa.org" in urls


def test_coach_reply_carries_provenance(client):
    uid = enroll(client)
    r = client.post(f"/coach/{uid}", json={
        "area": "finance", "message": "How do I start budgeting?"}).json()
    p = r["provenance"]
    assert "model-generated" in p["method"]
    assert p["generated_by"]
    assert "qualified professional" in p["disclaimer"]


# ---- setup gateway, translate mode, and the translate tool ------------------

def test_enroll_can_choose_language_at_the_gateway(client):
    r = client.post("/enroll", json={
        "display_name": "Rosa", "birthdate": "1990-01-01",
        "terms_consent": True, "language": "es"})
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["language"] == "es"
    client.headers["authorization"] = f"Bearer {out['user_token']}"
    pref = client.get(f"/language/{out['id']}").json()
    assert pref["language"] == "es" and pref["mode"] == "pre"
    # Pre-translated from the very first guidance.
    g = client.post(f"/monitor/{out['id']}", json={
        "movement": "collapse", "pulse": "absent"}).json()
    assert g["guidance"]["first_aid"]["steps"][0].startswith("Llame")


def test_enroll_rejects_unknown_language(client):
    r = client.post("/enroll", json={
        "display_name": "Rosa", "terms_consent": True, "language": "klingon"})
    assert r.status_code == 422


def test_on_demand_mode_keeps_originals(client):
    uid = enroll(client)
    client.put(f"/language/{uid}", json={"language": "es",
                                         "mode": "on_demand"})
    assert client.get(f"/language/{uid}").json()["mode"] == "on_demand"
    # Content is delivered in the original English...
    g = client.post(f"/monitor/{uid}", json={
        "movement": "collapse", "pulse": "absent"}).json()
    assert g["guidance"]["first_aid"]["steps"][0].startswith("Call")
    w = client.get(f"/waivers/{uid}").json()
    assert w["terms"][0].startswith("I authorize")
    # ...and flipping back to pre-translated restores delivery in-language.
    client.put(f"/language/{uid}", json={"language": "es", "mode": "pre"})
    g = client.post(f"/monitor/{uid}", json={
        "movement": "collapse", "pulse": "absent"}).json()
    assert g["guidance"]["first_aid"]["steps"][0].startswith("Llame")


def test_translate_tool_hand_strings_and_stub_honesty(client):
    uid = enroll(client)
    client.put(f"/language/{uid}", json={"language": "es",
                                         "mode": "on_demand"})
    # A known safety string translates by hand, even in on-demand mode.
    r = client.post(f"/translate/{uid}", json={
        "text": "Call emergency services now (or have someone else call)."
    }).json()
    assert r["engine"] == "hand" and r["translation"].startswith("Llame")
    # An explicit target overrides the user's choice.
    r = client.post(f"/translate/{uid}", json={
        "text": "metronome tick at 110 beats per minute", "to": "fr"}).json()
    assert r["engine"] == "hand" and "métronome" in r["translation"]
    # Free text on the offline stub: honest note, no fake translation.
    r = client.post(f"/translate/{uid}", json={
        "text": "a note my neighbour left on the door"}).json()
    assert r["engine"] == "stub" and "cannot translate" in r["note"]
    assert r["translation"] == "a note my neighbour left on the door"
    # Unknown targets are refused.
    r = client.post(f"/translate/{uid}", json={"text": "hi", "to": "xx"})
    assert r.status_code == 422
