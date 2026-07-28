# JIM-mini v0.4.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.4.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.4.1** — the release where a photograph really reached a
clinician, and free got honest. One of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
this version.

### Show it, rather than describe it

*"It's a bit red"* is the same sentence for a heat rash and for cellulitis.
Clinical capture lets somebody photograph the thing — or film it, when it
only shows in motion — mark where on the body, and send it through a referral
to a real clinician. Four rules, each asserted and mutation-checked:

- **A synthetic agent never receives the image.** It is told one exists,
  where and when — routing, never diagnosis. A model that looks at a mole and
  says "that looks fine" has made a diagnosis with no license and no
  accountability, and a missed melanoma is not undone by the next sentence.
- **Never an intimate site for a child.** No override, no guardian consent
  path, no setting.
- **The pixels never touch JIM's own database.** Vault only; the schema has
  no column that could hold an image; no vault means refused, not degraded.
- **Location is stripped, not promised absent** — a real JPEG parser drops
  the metadata segments, checked against the bytes actually sealed.

And the sentence "it travels with a referral" is now *true*: the referral
package carries the capture's metadata (never bytes) so you read exactly what
would go before signing, intimate sites never ride in on a match, and the
field is `released_to_clinician` — released is not opened, and this app
cannot see the second.

### A free plan, with nothing private about it

Free is the whole Guardian — conditions, guidance, journal, habits, goals,
**and every emergency path** — with the record under **platform custody**:
JIM-mini holds it, you have access, ordinary HTTPS, no vault at any point.
Basic ($20/mo) is the same Guardian sealed under a key you can hold. The
features are identical; the difference is who holds your record, and every
surface that names a plan says so.

Two things the open store refuses — a photograph of a body, and a child's
record on a guardian's account — because the person exposed did not pick the
plan. The health readings are deliberately *not* refused: they are the
emergency path, and a storage refusal in front of an escalation is a paywall
in front of an alarm wearing a privacy argument. **Nothing that answers an
emergency is ever behind a paywall, on any plan, still.**

The vault gate now asks about the *plan* rather than the deployment — a free
account's journal and detections were being sealed into a vault it was not
paying for. Reads and erasure keep the real vault, so a downgraded account
can still read its sealed history and have it purged. And the access log
stopped telling a comfortable lie: on an open plan, an empty list means
nothing was recorded, not that nothing was read — it now says which.

### Verification

525 tests green. Screens 76–80 new, tier and signup screens redrawn for the
free plan, every guard above mutation-checked — one at a time, after checking
them together masked two.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.4.1` tag), run `python -m jim`,
or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
