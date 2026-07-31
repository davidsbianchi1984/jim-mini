# JIM-mini v0.20.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.20.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.20.1 — the union hid a surface.**

`clientpaths.doorless` unions the console with the iOS, Android and Windows
shells, so a route only the phone calls counts as doored. The union backlog
reads **69**; the console alone cannot reach **109 routes**. The guard
was answering *some client can reach this*, which was true, in place of *this
client can reach this*, which was not.

That is the shape of every defect this audit has produced: a checker answering
a question slightly to the left of the one that matters, and passing. In QRME
the gap turned out to be the entire seller's side of the product — post a
licence offer, see who holds one, revoke it, read what it earned, ask to be
paid — all present on the phone, all absent from the desk.

## Two new guards

- **`test_the_console_is_a_client_too.py`** — the console's own backlog, in
  `console_doorless.txt`, checked in both directions and ratcheted so it cannot
  grow past where it started. The union guard stays; a route no client anywhere
  calls is still worse. A phone-only capability is a legitimate design choice,
  which is what the snapshot is for: deferring one takes a deliberate edit and
  shows up in a diff.
- **`test_a_binding_is_not_a_door.py`** — the same mistake one level down. A
  function in `api.ts` that no screen calls is not a door, and `doorless`
  counted it as one. The docstring on `doorless` had said this was *"a
  discipline rather than something the test can enforce"*; it is enforceable in
  about twenty lines. *The test cannot check this* is a claim worth testing.
  This repository has **four**.

## Fixed

- **`clientpaths.py` was not byte-identical across the three repositories**,
  though it says it is. This copy never received the `fetch`, `window.open`,
  `<img src>` and `<a href>` call forms from 0.20.0, so its backlog counted
  doors that already existed. Restored, and the backlog dropped **73 → 69**: `POST /voice/speak` and `POST /watch/seed/{user_id}` found by the new forms, and both OAuth callbacks correctly exempted.
- **The pairing QR is built from a literal.** `Settings.tsx` rendered it as
  `getBase() + pair.qr_svg`, where the path arrives in a response body — a real
  door no static check can see. `GET /pair/qr.svg` sat in `NOT_A_CLIENT_CALL`
  for exactly that reason, which is an exemption made out of a blind spot; the
  last one of those turned out to have no door at all. Same request, now
  visible to the audit.

## Cut together

QRME, JIM-mini and PDI move on one version number. QRME's 0.20.1 additionally
carries the seller's-side console screen and three money defects the building
of it exposed — including a marketplace sale credited to a profile id while the
statement reads by account id. See [QRME's notes](https://github.com/davidsbianchi1984/qrme/blob/main/RELEASE_NOTES.md).
