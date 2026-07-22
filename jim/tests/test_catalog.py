"""The connected-apps connector catalog."""

from jim import catalog


def test_catalog_endpoint(client):
    body = client.get("/connectors/catalog").json()
    providers = {p["provider"] for p in body["providers"]}
    assert providers == {"apple", "google", "microsoft", "canva"}
    assert body["provider_count"] == 4
    assert body["app_count"] == len(catalog.CONNECTORS)


def test_every_entry_is_well_formed():
    for c in catalog.CONNECTORS:
        assert c["capabilities"], f"{c['app']} has no capabilities"
        assert c["directions"], f"{c['app']} has no directions"
        assert set(c["directions"]) <= {"collect", "act", "produce"}


def test_key_apps_present():
    keys = set(catalog.BY_KEY)
    for expected in [("apple", "photos"), ("apple", "calendar"), ("apple", "mail"),
                     ("apple", "messages"), ("google", "gmail"), ("google", "chrome"),
                     ("microsoft", "file_explorer"), ("microsoft", "m365"),
                     ("canva", "magic_studio")]:
        assert expected in keys, f"missing {expected}"
