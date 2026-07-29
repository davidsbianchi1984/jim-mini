# JIM-mini v0.10.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.10.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.10.0** — a real offline model. One of three interoperating
products, all three cut together at this version.

### The offline helper grows a brain

Until now, "offline" meant a canned fallback that could only explain
itself. Now there is a door to actual local intelligence:

1. Install **Ollama** from [ollama.com](https://ollama.com) — free, one
   installer, Windows/macOS/Linux.
2. In a terminal, run `ollama pull deepseek-r1:1.5b` (or any model your
   machine can carry — `llama3.2` is another good small one).
3. That's it. JIM finds the running daemon on its own: the **Local
   (Ollama)** tile in Settings → Model lights up configured — no key,
   no account, and **nothing ever leaves your machine**.

*Automatic* prefers the local model over the canned stub whenever no
cloud key is set. And offline mode (`JIM_OFFLINE`) uses it too — offline
forbids the network, and a model answering on your own loopback isn't
network. `JIM_OLLAMA_MODEL` and `JIM_OLLAMA_URL` override the defaults
for bigger models or a daemon on another port.

### Settings says what it means

- The backend status line implied a "tandem" switch that never existed;
  it now says plainly the vault tandem is configured by the deployment.
- **Your model API key** moved to sit directly beneath *Which model
  answers*, where it belongs — not stranded below Email delivery.

### Verification

636 tests green, including that the Local tile is honest about an absent
daemon, that a running local model wins Automatic over the stub, that
offline mode uses a running local model and degrades to the stub without
one, and that the fallback's reply now names both ways out.

### Install

If you have 0.7.0 or later, this arrives on its own — one restart when
prompted. Otherwise, download the installer for your OS from the assets
below.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
