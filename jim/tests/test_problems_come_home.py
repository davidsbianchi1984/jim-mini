"""The error reports come home: the product's own backend collects them.

The consoles kept a content-free failure log and the only configured place it
could go was a separate gateway most installs never run. A field report on
the sibling product read "this build has no collector configured, so nothing
is sent anywhere" and asked why the results don't funnel back to where
corrections get made. Now they do, here as well: same whitelist contract as
the gateway (`jim/problems.py`), folded into counters, readable by the
operator and nobody else.
"""


def _report(**over):
    base = {
        "source": "jim-mini", "app_version": "0.68.0", "platform": "iPhone",
        "language": "en",
        "problems": [{"op": "POST /users/{id}/checkins", "status": 500,
                      "count": 3, "day": "2026-08-13",
                      "fingerprint": "ab12cd34"}],
    }
    base.update(over)
    return base


def test_a_report_lands_and_folds(client):
    r = client.post("/v1/problems", json=_report())
    assert r.status_code == 202, r.text
    assert r.json() == {"accepted": True, "problems": 1, "failures": 3}
    # The same failure again folds into the same row rather than a new one.
    client.post("/v1/problems", json=_report())
    rows = client.get("/v1/problems").json()["rows"]
    assert len(rows) == 1
    assert rows[0]["count"] == 6
    assert rows[0]["op"] == "POST /users/{id}/checkins"


def test_the_intake_is_a_whitelist(client):
    """A client whose redaction stopped working is refused with the field
    named, never quietly trimmed — in this product the messages it must not
    carry can be health content, which is why the strictness matters more
    here than anywhere else."""
    r = client.post("/v1/problems", json=_report(notes="extra"))
    assert r.status_code == 422
    assert "notes" in r.json()["detail"]
    r = client.post("/v1/problems", json=_report(problems=[{
        "op": "GET /users/usr_8f2k1x9q/checkins", "status": 404,
        "count": 1, "day": "2026-08-13", "fingerprint": "ab12cd34"}]))
    assert r.status_code == 422  # an id survived redaction


def test_reading_is_narrower_than_writing(client, monkeypatch):
    """Anyone may post; the aggregate is a failure map of every version, so
    reading needs the key once one is set."""
    monkeypatch.setenv("JIM_PROBLEMS_KEY", "letmesee")
    client.post("/v1/problems", json=_report())
    assert client.get("/v1/problems").status_code == 401
    assert client.get("/v1/problems", headers={
        "authorization": "Bearer wrong"}).status_code == 403
    ok = client.get("/v1/problems", headers={
        "authorization": "Bearer letmesee"})
    assert ok.status_code == 200
    assert ok.json()["rows"][0]["source"] == "jim-mini"
