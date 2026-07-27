# JIM-mini v0.3.3 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.3.3` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.3.3** — the release where a task working on its own stopped being
something you had to go and check. One of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### The watch face is the ambient one

Three lights, three counts, dimmed at zero — and **no task names**.

This is the surface the round exists for. While somebody is on their phone, the
watch is the one place that can show several tasks at once without getting in
the way. Naming them was the first cut and was wrong: a name is something you
read, and reading is the thing a glance cannot do. The footer says *open on
your phone*, because that is where the answer lives.

| | | |
| --- | --- | --- |
| 🟢 **green** | working · done | in progress, or finished. Nothing wanted from you |
| 🟡 **amber** | needs you | it has stopped and is waiting on a person |
| 🔴 **red** | stopped | it hit an error or was cancelled, and will not continue |

The word rides with the colour, because green alone cannot separate a task that
is still going from one that has finished — and those call for opposite
reactions.

### Screen 67, and an overlay that follows you

**Screen 67** folds every task into one tappable group per light. Somebody
opening it *because* amber appeared should not have to scan a flat list for the
one that changed.

**The overlay** rides over an ordinary screen, and over **every** desktop view —
a task that reports only on its own screen is one you have to remember to go
and check. It is shaped like the watch face rather than as a bar across the
screen: a small translucent box in the corner, three stacked rows, each its own
tap target.

The mapping lives once, in QRME's `agentlight.py`, for all three products.

### The README leads with the screens now

Everything you can look at is above everything you have to read, and the
run / config / API material is gathered under one **Reference** heading at the
bottom — so a command spotted in a screenshot has one place to go and look it
up. Those tables are set smaller, because they are for looking things up in
rather than reading through.

### Verification

380 tests green. Screens regenerated for iOS and Android, the watch for
watchOS, and the desktop console for macOS and Windows.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.3.3` tag), or run `python -m jim`.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
