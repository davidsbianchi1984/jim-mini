"""Cloud contribution: seeing exactly what would leave, and undoing what did.

The settings screen has offered *"preview before it leaves"* since the cloud
tier shipped. These are the tests that make it true rather than decorative.
"""

from jim.tests.conftest import enroll


class FakeCloud:
    """A gateway that accepts contributions and records revocations."""

    def __init__(self, accept=True, revoke_ok=True):
        self.accept = accept
        self.revoke_ok = revoke_ok
        self.sent = []
        self.revoked = []

    def contribute(self, payload):
        if not self.accept:
            return False
        self.sent.append(payload)
        return True

    def revoke_contributions(self, refs):
        if not self.revoke_ok:
            return False
        self.revoked.extend(refs)
        return True

    def model_info(self):
        return {"model": "claude-fable-5"}


def _client(tmp_path, monkeypatch, cloud):
    from fastapi.testclient import TestClient

    from jim import db as jim_db
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    monkeypatch.delenv("JIM_QRME_URL", raising=False)
    jim_db.reset()
    from jim.api import create_app
    return TestClient(create_app(cloud_client=cloud))


def _guidance(client, uid):
    """Produce a guidance event — the thing a contribution reports on."""
    r = client.post(f"/monitor/{uid}", json={"heart_rate": 150})
    assert r.status_code in (200, 201), r.text


# -- the preview -------------------------------------------------------------

def test_preview_shows_the_exact_payload_that_would_be_sent(tmp_path, monkeypatch):
    cloud = FakeCloud()
    with _client(tmp_path, monkeypatch, cloud) as client:
        uid = enroll(client, cloud_contribution=True)
        _guidance(client, uid)

        view = client.get(f"/users/{uid}/cloud-contribution").json()
        assert view["opted_in"] is True
        preview = view["preview_next"]
        assert preview["source"] == "jim-mini"
        assert preview["kind"] == "guidance_outcome"
        assert preview["condition"]
        # The one field the moment supplies rather than the record.
        assert preview["rating"] is None
        assert "rating you give" in view["preview_note"]

        # And nothing was sent by looking.
        assert cloud.sent == []


def test_the_preview_is_the_real_payload_not_a_description(tmp_path, monkeypatch):
    """The load-bearing property: preview and send share one builder, so the
    preview cannot drift into describing something the send does not do."""
    cloud = FakeCloud()
    with _client(tmp_path, monkeypatch, cloud) as client:
        uid = enroll(client, cloud_contribution=True)
        _guidance(client, uid)

        preview = client.get(f"/users/{uid}/cloud-contribution").json()["preview_next"]
        client.post(f"/feedback/{uid}", json={"rating": "up"})
        sent = cloud.sent[-1]

        # Identical but for the ref (assigned at send) and the rating.
        assert {k: v for k, v in sent.items() if k not in ("ref", "rating")} == \
               {k: v for k, v in preview.items() if k != "rating"}
        assert sent["rating"] == "up"
        assert sent["ref"]


def test_preview_is_none_with_nothing_to_contribute(tmp_path, monkeypatch):
    with _client(tmp_path, monkeypatch, FakeCloud()) as client:
        uid = enroll(client, cloud_contribution=True)
        view = client.get(f"/users/{uid}/cloud-contribution").json()
        assert view["preview_next"] is None
        assert view["preview_note"] is None


def test_the_payload_never_carries_identity(tmp_path, monkeypatch):
    cloud = FakeCloud()
    with _client(tmp_path, monkeypatch, cloud) as client:
        uid = enroll(client, cloud_contribution=True, display_name="Jordan")
        _guidance(client, uid)
        client.post(f"/feedback/{uid}", json={"rating": "up",
                                              "note": "this really helped"})

        blob = str(cloud.sent[-1])
        assert uid not in blob
        assert "Jordan" not in blob
        assert "this really helped" not in blob     # the note never leaves
        assert set(cloud.sent[-1]) == {
            "ref", "source", "kind", "condition", "severity", "rating"}


# -- the history -------------------------------------------------------------

def test_history_records_exactly_what_left(tmp_path, monkeypatch):
    cloud = FakeCloud()
    with _client(tmp_path, monkeypatch, cloud) as client:
        uid = enroll(client, cloud_contribution=True)
        _guidance(client, uid)
        client.post(f"/feedback/{uid}", json={"rating": "up"})

        history = client.get(f"/users/{uid}/cloud-contribution").json()["contributed"]
        assert len(history) == 1
        assert history[0]["payload"] == cloud.sent[-1]
        assert history[0]["revoked"] is False


def test_a_refused_send_is_not_logged(tmp_path, monkeypatch):
    """Logging a failed post would offer a revoke button for data that never
    left."""
    cloud = FakeCloud(accept=False)
    with _client(tmp_path, monkeypatch, cloud) as client:
        uid = enroll(client, cloud_contribution=True)
        _guidance(client, uid)
        r = client.post(f"/feedback/{uid}", json={"rating": "up"}).json()
        assert r["contributed"] is False

        assert client.get(
            f"/users/{uid}/cloud-contribution").json()["contributed"] == []


def test_opting_out_means_nothing_is_sent(tmp_path, monkeypatch):
    cloud = FakeCloud()
    with _client(tmp_path, monkeypatch, cloud) as client:
        uid = enroll(client)                       # cloud_contribution off
        _guidance(client, uid)
        client.post(f"/feedback/{uid}", json={"rating": "up"})
        assert cloud.sent == []


# -- revocation --------------------------------------------------------------

def test_revoke_turns_it_off_and_deletes_what_already_went(tmp_path, monkeypatch):
    cloud = FakeCloud()
    with _client(tmp_path, monkeypatch, cloud) as client:
        uid = enroll(client, cloud_contribution=True)
        _guidance(client, uid)
        client.post(f"/feedback/{uid}", json={"rating": "up"})
        ref = cloud.sent[-1]["ref"]

        out = client.post(f"/users/{uid}/cloud-contribution/revoke").json()
        assert out["opted_in"] is False
        assert out["revoked"] == 1
        assert out["gateway_deleted"] is True
        assert cloud.revoked == [ref]

        view = client.get(f"/users/{uid}/cloud-contribution").json()
        assert view["opted_in"] is False
        assert view["contributed"][0]["revoked"] is True


def test_revoking_stops_future_contributions_too(tmp_path, monkeypatch):
    cloud = FakeCloud()
    with _client(tmp_path, monkeypatch, cloud) as client:
        uid = enroll(client, cloud_contribution=True)
        _guidance(client, uid)
        client.post(f"/users/{uid}/cloud-contribution/revoke")

        client.post(f"/feedback/{uid}", json={"rating": "up"})
        assert cloud.sent == []


def test_an_unreachable_gateway_does_not_fail_the_revoke(tmp_path, monkeypatch):
    """A user asked for this. The local record is marked either way, and the
    response is honest about which half could not be confirmed."""
    cloud = FakeCloud(revoke_ok=False)
    with _client(tmp_path, monkeypatch, cloud) as client:
        uid = enroll(client, cloud_contribution=True)
        _guidance(client, uid)
        client.post(f"/feedback/{uid}", json={"rating": "up"})

        out = client.post(f"/users/{uid}/cloud-contribution/revoke").json()
        assert out["opted_in"] is False
        assert out["revoked"] == 1
        assert out["gateway_deleted"] is False
        assert "not confirmed" in out["note"]
        # Still marked locally — the user must not see it as shared.
        view = client.get(f"/users/{uid}/cloud-contribution").json()
        assert view["contributed"][0]["revoked"] is True


# -- it is PHI ---------------------------------------------------------------

def test_another_user_cannot_read_the_contribution_view(tmp_path, monkeypatch):
    with _client(tmp_path, monkeypatch, FakeCloud()) as client:
        first = enroll(client, cloud_contribution=True)
        enroll(client, display_name="Mal")          # client now holds Mal's token
        r = client.get(f"/users/{first}/cloud-contribution")
        assert r.status_code == 403
