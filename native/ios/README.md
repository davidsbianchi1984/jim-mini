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
