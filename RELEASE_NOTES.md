# JIM-mini v0.9.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.9.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.9.1** — the drip address now answers. One of three
interoperating products, all three cut together at this version.

### The bug, as reported

The Apple Watch panel handed out a Wi-Fi drip address
(`http://192.168.x.x:8000/…`) — but the desktop app's bundled backend
listened only on the computer itself. A phone POSTing to that address got
"could not connect", and the card never said so.

### What 0.9.1 does

- **The card tells the truth.** If your phone can't reach the address
  yet, an amber notice says so — instead of letting you build a Shortcut
  against a dead URL.
- **One press opens the door**: *"Let my phone reach JIM on this
  Wi-Fi"* restarts the backend listening on your network, permanently
  until you turn it off. Loopback stays the default — private until
  asked. Windows may ask once to allow it through the firewall; say yes.
  Everything personal behind the port still requires your sign-in.
- **The recipe names the paste spot**: the drip address goes into the
  Shortcut's **Get Contents of URL → URL** field — the step now says THIS
  in capitals. And it no longer promises an hourly trigger Shortcuts
  doesn't have: use Time of Day, repeat daily (add an evening automation
  if you like).

### Verification

632 tests green, including that the setup card reports unreachable on a
loopback bind and reachable on a network bind, and that the recipe names
the paste spot.

### Install

If you have 0.7.0 or later, this arrives on its own — one restart when
prompted. Otherwise, download the installer for your OS from the assets
below.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
