# JIM-mini v0.1.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini (Guardian) v0.1.1** — the Guardian gets hands, a family, and
provable custody. One of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

### Highlights

- **Native apps at parity** — iOS, Android, and Windows now carry the whole
  Guardian: Care (Monitor / Check-in / Coach / Family), Life (goals, habits,
  journal), Safety (SOS, escalation policy, robots, Medical ID), Connect,
  Vault Custody, and the model picker.
- **Robots as first-aid responders** — catalog robots bind as guardian
  responders with escalation directives. Assist-rated platforms fetch the
  AED and coach the playbook aloud; perform-rated platforms may deliver
  chest compressions only after a person on scene confirms. **Fully
  autonomous resuscitation stays locked behind a signed liability waiver
  that can never be signed for a minor.**
- **Emergency, end to end** — predictive early warning, a transparent
  escalation decision tree, and the one-tap Emergency flow: reach services,
  share location, alert family, surface the Medical ID QR, deliver AI first
  aid, ping every device.
- **Family** — parent-led child accounts with recorded (PDI-sealed) consent,
  age-scaled oversight that ends by itself at 18, pause/quiet hours that
  never hold safety, and one light per child on the parent's wrist.
- **Provable custody** — tandem specialist exchanges sealed into the PDI
  vault with a custody viewer and provenance; the mental-health trio routes
  through live QRME personas while crisis escalation stays local.
- **Language everywhere** — per-user language with hand-translated safety
  content in all supported languages, gateway choice, translate-anything,
  and guidance provenance with published sources. Chrome localization covers
  the apps' own labels in all 10 languages.
- **In-app feedback** — a "Help us improve" section on every client.

### Verification

215 tests green; live-server smoke flows pass; the desktop app builds clean;
the cross-product suite smoke (run from qrme) passes end to end.

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
the backend from source — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
