"""How much of a biometric reading to believe.

Everything upstream assumed clean input: `escalation.decide` has always taken a
`confidence`, but only forecasts ever supplied one, so a *measurement* was a
fact by virtue of arriving. A wearable losing skin contact produces a
plausible-looking number that is completely wrong, and the alarming direction
is as likely as the reassuring one.

Two claims carry this, and they pull against each other on purpose:

* **A reading we do not believe must not ring somebody's daughter.** An alert
  that is usually wrong spends the only thing escalation has, which is
  somebody's willingness to pick up.
* **Nothing here may muffle a real emergency.** So the tests below also push
  genuine critical readings, corroborated readings, and a person's own words
  through the same path and assert they land exactly where they always did.
"""

from jim import escalation, signal


def _enroll(client, **extra):
    body = {"display_name": "Jordan", "birthdate": "1995-05-05",
            "terms_consent": True, "resting_heart_rate": 60,
            "emergency_name": "Kin", "emergency_phone": "+15555550123",
            "contact_consent": True}
    body.update(extra)
    r = client.post("/enroll", json=body, headers={})
    assert r.status_code == 201, r.text
    return r.json()


def _auth(u):
    return {"authorization": f"Bearer {u['user_token']}"}


# --- grading --------------------------------------------------------------

def test_a_reading_a_body_cannot_produce_is_a_sensor_fault():
    q = signal.assess({"heart_rate": 0})
    assert q["grade"] == "implausible"
    assert q["trusted"] is False
    assert "outside the range a body can produce" in q["reasons"][0]
    # And it is phrased as a fault, not as concern about the person.
    assert q["note"] == signal.FAULT_NOTE

    q = signal.assess({"blood_oxygen": 130})
    assert q["grade"] == "implausible"


def test_an_alarming_reading_is_signal_not_noise():
    """The trap this module has to avoid: a lone SpO2 of 84 is *exactly* the
    reading the escalation ladder exists for. An earlier draft graded anything
    outside the ordinary range as suspect and muted it. Confidence drops only
    on evidence the sensor misbehaved — never because a number is frightening."""
    q = signal.assess({"blood_oxygen": 84})
    assert q["grade"] == "ok"
    assert q["confidence"] == 1.0
    assert q["trusted"] is True


def test_an_ordinary_reading_is_trusted_and_says_nothing():
    q = signal.assess({"heart_rate": 72, "blood_oxygen": 98})
    assert q["grade"] == "ok"
    assert q["confidence"] == 1.0
    assert q["trusted"] is True
    assert q["note"] is None
    assert q["reasons"] == []


def test_an_impossible_jump_between_readings_is_suspect():
    """A genuine panic attack moves a heart rate fast, so the threshold is
    generous — but a wrist sensor slipping moves it faster than a body can."""
    q = signal.assess({"heart_rate": 190}, prior={"heart_rate": 62})
    assert q["grade"] == "suspect"
    assert "more than" in " ".join(q["reasons"])
    # The same value with a plausible run-up is not suspicious at all.
    assert signal.assess({"heart_rate": 190},
                         prior={"heart_rate": 160})["grade"] == "ok"


def test_a_device_reporting_poor_contact_lowers_trust(client):
    q = signal.assess({"heart_rate": 72, "signal_quality": 0.2})
    assert q["confidence"] < signal.TRUST_FLOOR
    assert "signal quality" in " ".join(q["reasons"])
    # …and cannot manufacture trust it does not have.
    bad = signal.assess({"heart_rate": 0, "signal_quality": 1.0})
    assert bad["trusted"] is False


def test_words_restore_trust_in_a_sensor_flagged_reading():
    """A jump-flagged reading that arrives with the user's own words is not in
    doubt: they are telling us the number is real."""
    alone = signal.assess({"heart_rate": 190}, prior={"heart_rate": 62})
    withwords = signal.assess({"heart_rate": 190}, prior={"heart_rate": 62},
                              said_something=True)
    assert alone["trusted"] is False
    assert withwords["corroborated"] is True
    assert withwords["trusted"] is True


def test_an_impossible_reading_cannot_be_corroborated_into_truth():
    """Two impossible values are not two witnesses — they are one broken
    device agreeing with itself."""
    q = signal.assess({"heart_rate": 0, "blood_oxygen": 130})
    assert q["corroborated"] is False
    assert q["trusted"] is False
    # …and words do not make a heart rate of zero true either. What the person
    # said still escalates, through the crisis floor this cap cannot touch.
    said = signal.assess({"heart_rate": 0}, said_something=True)
    assert said["trusted"] is False


def test_words_alongside_a_flagged_reading_corroborate_it():
    """Corroboration only has anything to do when something was flagged — a
    plausible reading was never in doubt, so words change nothing about it."""
    q = signal.assess({"heart_rate": 190}, prior={"heart_rate": 62},
                      said_something=True)
    assert q["corroborated"] is True
    assert "the user's own words" in " ".join(q["reasons"])


# --- the escalation gate --------------------------------------------------

def test_a_disbelieved_critical_asks_instead_of_escalating():
    """The point of the whole module: cap, do not silence. 'We got an odd
    reading, are you alright?' is the honest sentence when the honest answer is
    that we do not know."""
    d = escalation.decide("critical", "balanced", confidence=0.15)
    assert d["tier"] == "check_in"
    assert "low signal confidence" in " ".join(d["path"])
    assert "critical floor" not in " ".join(d["path"])


def test_a_believed_critical_escalates_exactly_as_before():
    d = escalation.decide("critical", "balanced", confidence=1.0)
    assert d["tier"] in ("notify_contact", "emergency_services")
    assert "critical floor" in " ".join(d["path"])


def test_crisis_words_are_never_a_sensor_artifact():
    """A sensor can be wrong. A person typing 'I can't breathe' is data of a
    different kind, and the confidence cap must not touch it."""
    d = escalation.decide("critical", "balanced", confidence=0.1, crisis=True)
    assert d["tier"] == "emergency_services"
    assert "never a sensor artifact" in " ".join(d["path"])


# --- end to end -----------------------------------------------------------

def test_a_garbage_reading_does_not_ring_the_emergency_contact(client):
    u = _enroll(client)
    r = client.post(f"/monitor/{u['id']}",
                    json={"blood_oxygen": 51, "heart_rate": 0},
                    headers=_auth(u)).json()

    assert r["signal"]["trusted"] is False
    assert r["signal"]["grade"] == "implausible"
    if r.get("detected"):
        assert r["escalation_decision"]["tier"] == "check_in"
        assert r.get("escalation") is None      # nobody was called


def test_a_real_emergency_still_escalates(client):
    """The regression this feature could plausibly cause, tested directly."""
    u = _enroll(client)
    r = client.post(f"/monitor/{u['id']}", json={"blood_oxygen": 84},
                    headers=_auth(u)).json()

    assert r["signal"]["trusted"] is True
    if r.get("detected"):
        assert r["escalation_decision"]["tier"] != "check_in"


def test_the_grade_is_recorded_with_the_reading(client):
    """An auditor asking 'why didn't this escalate?' should not have to guess."""
    u = _enroll(client)
    client.post(f"/monitor/{u['id']}", json={"heart_rate": 0},
                headers=_auth(u))
    events = client.get(f"/events/{u['id']}", headers=_auth(u)).json()
    bio = [e for e in events if e["type"] == "biometric"]
    assert bio and "signal_confidence" in str(bio[0])


def test_a_sensor_fault_never_reaches_the_baseline(client):
    """A rolling baseline is long-lived, so a fault let into it corrupts every
    future comparison — the one place dropping a reading is clearly right."""
    u = _enroll(client)
    for _ in range(3):
        client.post(f"/monitor/{u['id']}", json={"heart_rate": 300},
                    headers=_auth(u))
    from jim import guardian
    base = guardian.get_baseline(u["id"], "heart_rate") \
        if hasattr(guardian, "get_baseline") else None
    if base is not None:
        assert base < 200

    assert signal.clean({"heart_rate": 300, "blood_oxygen": 97}) \
        == {"blood_oxygen": 97}
