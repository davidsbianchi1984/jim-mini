# JIM Guardian — iOS (SwiftUI)

A native SwiftUI app for iPhone, wired to the JIM Guardian backend. Four
screens — **Welcome/Enroll → Overview → Live Monitoring → Check-in** — hitting
the real `/enroll`, `/baseline`, `/monitor`, and `/checkin` endpoints.

## Run in the Simulator (macOS)

Requires Xcode 15+ and [XcodeGen](https://github.com/yonyz/XcodeGen)
(`brew install xcodegen`).

```bash
cd native/ios
xcodegen generate          # writes JimGuardian.xcodeproj from project.yml
open JimGuardian.xcodeproj  # then ⌘R with an iPhone simulator selected
```

Start the backend first, on the host (the Simulator shares your Mac's network,
so `127.0.0.1` resolves):

```bash
# from the repo root
JIM_CORS_ORIGINS=* uvicorn jim.api:app
```

The default base URL is `http://127.0.0.1:8000` (see `Sources/ApiClient.swift`).
`Info` in `project.yml` sets `NSAllowsLocalNetworking` so the Simulator can reach
plain-http localhost.

## Layout

| File | Role |
| --- | --- |
| `project.yml` | XcodeGen spec (bundle id, iOS 16 target, ATS exception) |
| `Sources/JimGuardianApp.swift` | `@main` app + root tab bar / enroll switch |
| `Sources/ApiClient.swift` | async `URLSession` client + wire models |
| `Sources/AppState.swift` | enrolled identity + token, persisted |
| `Sources/Theme.swift` | the JIM dark-OLED palette |
| `Sources/Views/*` | Welcome, Overview, Care (Monitor / Check-in / Coach), Life, Safety, Connect |

The tab bar holds five destinations: Monitor, Check-in, and Coach share the
segmented **Care** tab, and **Connect** gathers data sources, social-platform
connections, and the connected-apps catalog.

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
