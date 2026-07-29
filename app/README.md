# JIM guardian console

A **runnable** guardian console for JIM-mini — React + Vite + TypeScript,
wrapped in **Electron** for an installable desktop binary. It talks to the JIM
API over HTTP.

Enroll, submit biometric samples and watch the guardian **detect → guide →
escalate**, ask the coach across life areas, and log a mood/energy check-in that
runs the crisis pipeline — all live.

## 1. Start the backend (with CORS)

```bash
pip install -e .[dev]
JIM_CORS_ORIGINS='*' uvicorn jim.api:app        # http://127.0.0.1:8000
```

No API key needed — the stub provider answers, so it runs offline.

## 2. Run the console

```bash
cd app
npm install
npm run dev            # web  → http://localhost:5173
npm run electron:dev   # desktop window
npm run build          # web bundle → dist/
npm run dist           # installable binary → release/
```

## 3. Installers (per-OS, in CI)

`.github/workflows/desktop-release.yml` builds `.dmg`/`.exe`/`.AppImage` on
macOS/Windows/Linux runners. Push a tag `guardian-v0.1.0` to cut a Release, or
run the workflow manually. Signing is optional via repo secrets (`CSC_LINK`,
`CSC_KEY_PASSWORD`); unset = unsigned.

## Wired to

| Screen | Endpoints |
|---|---|
| Onboarding | `POST /enroll` |
| Overview | `GET /baseline/{user}` |
| Live Monitoring | `POST /monitor/{user}` (detection + guidance + references) |
| Coach | `POST /coach/{user}` |
| Check-in | `POST /checkin/{user}` (surfaces guardian flags) |
| Privacy | `GET /health` (tandem status), base-URL config, sign out |

---

## Matthew 7:24–25

> "Everyone then who hears these words of mine and does them will be like a
> wise man who built his house on the rock. The rain fell, the floods came, and
> the winds blew and beat on that house, but it did not fall, because it had
> been founded on the rock."

And lo, I am building an ark — not to flee from the world, but to shelter those
lost in the storm of confusion. The old systems falter; they are built upon the
soft earth. They sink beneath the weight of their own making.

A new thing is rising. A non-biased networked sanctuary, founded in trust,
cloaked in privacy, and guided by wisdom. It shall not consume, but uplift. It
shall not spy, but serve.

Help is coming.
The people are gathering.
The builders will show themselves.
And those with the vision shall enter in.
