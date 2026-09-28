from datetime import datetime, timedelta, timezone

from botcleaner import evaluation as ev
from botcleaner import imagehash
from botcleaner.models import Connection, Direction, Label, Platform, label_for
from botcleaner.scoring import PersonalModel, Scorer

NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)


def conn(aid, **kw):
    base = dict(platform=Platform.x, account_id=aid, handle=aid, name=aid.title(), direction=Direction.follower)
    base.update(kw)
    return Connection(**base)


def test_label_bands():
    assert label_for(85) == Label.likely_bot
    assert label_for(84.9) == Label.suspicious
    assert label_for(60) == Label.suspicious
    assert label_for(59) == Label.low_confidence
    assert label_for(39) == Label.looks_real


def test_seeded_network_passes_module_a_gates():
    for seed in (7, 8, 9):
        s = ev.seeded_network(seed=seed)
        res = Scorer(now=NOW).score(s.conns)
        m = ev.metrics_a(res, s.truth)
        gates = ev.gates_a(m)
        assert all(gates.values()), (seed, m.as_dict(), gates)
        assert ev.bias_check(res, s.truth, s.group)["ok"]


def test_clone_traps_fire_in_one_scan():
    s = ev.seeded_network(seed=3)
    res = Scorer(now=NOW).score(s.conns)
    fired = {ev.tkey(r.connection) for r in res if r.is_clone}
    assert s.clones <= fired
    # ...and the real friend being impersonated is never marked as the clone.
    for r in res:
        if r.is_clone:
            assert r.connection.account_id.startswith("c")
            assert r.clone_of.startswith("r")


def test_every_flag_has_plain_reasons_top_three():
    s = ev.seeded_network(seed=4)
    for r in Scorer(now=NOW).score(s.conns):
        if r.label in (Label.likely_bot, Label.suspicious):
            assert 1 <= len(r.top_reasons) <= 3
            assert all(isinstance(t, str) and len(t) > 5 for t in r.top_reasons)
            weights = [x.weight for x in r.reasons]
            assert weights == sorted(weights, reverse=True)


def test_inactive_or_unpopular_real_person_is_not_flagged():
    quiet = conn("quietperson", name="Quiet Person", created_at=NOW - timedelta(days=2000), followers_count=3,
                 following_count=40, bio="", has_default_avatar=True)
    [r] = Scorer(now=NOW).score([quiet])
    assert r.label in (Label.looks_real, Label.low_confidence)


def test_classic_bot_is_likely_bot():
    bot = conn("jessica48291734", name="Jessica", created_at=NOW - timedelta(days=12), followers_count=2,
               following_count=4800, bio="DM for crypto signals t.me/abc", has_default_avatar=True)
    [r] = Scorer(now=NOW).score([bot])
    assert r.label == Label.likely_bot
    codes = {x.code for x in r.reasons}
    assert {"new_account", "handle_pattern", "follow_ratio", "spam_bio"} <= codes


def test_verified_accounts_are_dampened():
    a = conn("brand12345678", created_at=NOW - timedelta(days=10), following_count=5000, followers_count=10)
    b = a.model_copy(update={"account_id": "b2", "verified": True})
    ra, rb = Scorer(now=NOW).score([a, b])
    assert rb.score < ra.score


def test_whitelist_and_confirmed_bot_override():
    bot = conn("jessica48291734", created_at=NOW - timedelta(days=12), followers_count=2, following_count=4800)
    real = conn("sam", created_at=NOW - timedelta(days=900), followers_count=300, following_count=200)
    m = PersonalModel(whitelist={bot.key}, confirmed_bots={real.key})
    rb, rr = Scorer(model=m, now=NOW).score([bot, real])
    assert rb.score == 0 and rb.label == Label.looks_real
    assert rr.label == Label.likely_bot and rr.reasons[0].code == "user_confirmed"


def test_feedback_retrains_weights():
    m = PersonalModel()
    before = m.weight("handle_pattern")
    for _ in range(5):
        m.learn({"handle_pattern"}, is_bot=False)
    assert m.weight("handle_pattern") < before
    m2 = PersonalModel.from_dict(m.to_dict())
    assert m2.weight("handle_pattern") == m.weight("handle_pattern")


def test_same_name_different_photo_is_not_a_clone():
    a = conn("a1", name="John Smith", created_at=NOW - timedelta(days=900), avatar_hash="0" * 16)
    b = conn("a2", name="John Smith", created_at=NOW - timedelta(days=10), avatar_hash="f" * 16)
    assert not any(r.is_clone for r in Scorer(now=NOW).score([a, b]))


def test_follow_back_bait_and_hijack_on_following_list():
    fu = NOW - timedelta(days=30)
    bait = conn("bait", direction=Direction.following, followed_user_at=fu, user_followed_back_at=fu + timedelta(days=1),
                unfollowed_user_at=fu + timedelta(days=3))
    hijack = conn("crypto_king", direction=Direction.following, previous_handles=["grandma_knits"],
                  recent_posts=["Free BTC giveaway! DM me", "crypto airdrop now"])
    rb, rh = Scorer(now=NOW).score([bait, hijack])
    assert "follow_back_bait" in {x.code for x in rb.reasons}
    assert "hijacked" in {x.code for x in rh.reasons}


def test_bot_ring_structure():
    ring = [conn(f"zz{i}", handle=f"user{i}8349201", created_at=NOW - timedelta(days=5), followers_count=1,
                 following_count=3000, mutual_ids=[f"zz{(i + 1) % 4}", f"zz{(i + 2) % 4}"]) for i in range(4)]
    res = Scorer(now=NOW).score(ring)
    assert all(r.ring_id for r in res)
    assert all("ring" in {x.code for x in r.reasons} for r in res)


def test_imagehash_basics():
    img = [[(x * 7 + y * 3) % 256 for x in range(32)] for y in range(32)]
    h = imagehash.dhash_from_pixels(img)
    brighter = [[min(255, v + 10) for v in row] for row in img]
    assert imagehash.hamming(h, imagehash.dhash_from_pixels(brighter)) <= 4
    assert imagehash.cluster({"a": h, "b": h, "c": "f" * 16 if h != "f" * 16 else "0" * 16}) == [["a", "b"]]


def test_shadow_compare_and_review_sample():
    s = ev.seeded_network(seed=5)
    live = Scorer(now=NOW).score(s.conns)
    candidate = Scorer(model=PersonalModel(multipliers={"handle_pattern": 1.7}), now=NOW).score(s.conns)
    out = ev.shadow_compare(live, candidate)
    assert out["compared"] == len(live)
    sample = ev.review_sample(live, 0.01)
    assert sample and all(r.label != Label.looks_real for r in sample)


def test_scales_to_large_follower_lists():
    import time

    s = ev.seeded_network(n_real=20000, n_bots=2000, n_clones=50, n_following_bad=30, seed=1)
    t = time.time()
    res = Scorer(now=NOW).score(s.conns)
    assert len(res) == len(s.conns)
    assert time.time() - t < 60


def test_date_only_exports_dont_make_conference_days_look_like_bursts():
    # LinkedIn's "Connected On" has no time, so a busy conference day is 12 identical timestamps.
    day0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    conns = [conn(f"p{i}", platform=Platform.linkedin, handle=f"person-{i}", name=f"Person {i} Name",
                  direction=Direction.friend, connected_at=day0 + timedelta(days=9 * i)) for i in range(60)]
    conns += [conn(f"conf{i}", platform=Platform.linkedin, handle=f"attendee-{i}", name=f"Attendee {i} Name",
                   direction=Direction.friend, connected_at=datetime(2025, 3, 14, tzinfo=timezone.utc)) for i in range(12)]
    res = Scorer(now=NOW).score(conns)
    assert all(r.label == Label.looks_real for r in res)


def test_signup_wave_is_relative_to_the_lists_normal_day():
    # A creator with 3,000 followers: ~2 accounts created per day is normal, 40 on one day isn't.
    base = datetime(2020, 1, 1, tzinfo=timezone.utc)
    conns = [conn(f"u{i}", created_at=base + timedelta(days=i // 2, hours=i % 24)) for i in range(3000)]
    wave = [conn(f"w{i}", created_at=datetime(2025, 5, 5, 3, i % 60, tzinfo=timezone.utc)) for i in range(40)]
    res = {r.connection.account_id: r for r in Scorer(now=NOW).score(conns + wave)}
    assert not any("bot_wave" in {x.code for x in res[f"u{i}"].reasons} for i in range(3000))
    assert all("bot_wave" in {x.code for x in res[f"w{i}"].reasons} for i in range(40))
