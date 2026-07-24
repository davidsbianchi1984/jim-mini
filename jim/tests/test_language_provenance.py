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
