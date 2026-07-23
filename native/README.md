# JIM Guardian — native apps

True-native scaffolds of the JIM-mini / Guardian client for three platforms,
each a separate idiomatic codebase (per the "native per platform" choice), all
talking to the same [JIM backend](../jim/api.py).

| Platform | Stack | Run in | Folder |
| --- | --- | --- | --- |
| **iOS** | Swift + SwiftUI | Xcode Simulator (macOS) | [`ios/`](ios/) |
| **Android** | Kotlin + Jetpack Compose | Android Studio emulator | [`android/`](android/) |
| **Windows** | C# + WinUI 3 | Windows 10/11 desktop | [`windows/`](windows/) |

Each target ships the same screens, exercising the real API end to end:

**Welcome / Enroll** → `POST /enroll` · **Overview** → `GET /baseline` + model
picker (`/models`, `/model/{uid}`) · **Live Monitoring** → `POST /monitor` ·
**Check-in** → `POST /checkin` · **Coach** → `POST /coach` · **Life** (goals /
habits / journal) → `/goals`, `/habits`, `/journal` · **Safety** — SOS + flow
(`/emergency`), escalation policy + sensitivity (`/escalation-policy`,
`/sensitivity`), robot helpers (`/robotics/catalog`, `/robots/{uid}`), and the
Medical ID card (`/medical-id/qr/{uid}`) · **Connect** — consented data
sources (`/sources/{uid}`), social-platform connections (`/social/{uid}` +
collect/publish), and the connected-apps catalog (`/connectors/catalog`,
`/apps/{uid}` + collect)

On the phone form factors, Monitor, Check-in, and Coach sit behind a single
**Care** tab (segmented on iOS, a `TabRow` on Android) so the bottom bar stays
at five destinations; Windows keeps them as flat sidebar items.

They persist the returned `user_token` so the app resumes signed-in, and share
the JIM dark-OLED palette so all three feel like one product. See each folder's
README for the exact build/run commands.

## Start the backend

All three point at the local dev server. From the repo root:

```bash
JIM_CORS_ORIGINS=* uvicorn jim.api:app
```

Host addresses differ by platform, and each client already defaults correctly:

| Platform | Reaches the host at |
| --- | --- |
| iOS Simulator | `http://127.0.0.1:8000` |
| Android emulator | `http://10.0.2.2:8000` |
| Windows | `http://127.0.0.1:8000` |

On a physical phone, point the client at your machine's LAN IP instead.

## Scope

These scaffolds now cover the full tenant-facing surface of
[`jim/api.py`](../jim/api.py): enroll, monitoring, check-in, coaching, goals /
habits / journal, safety (SOS, Medical ID, policy, robots), and the Connect
surface (sources, social platforms, connected apps).

The existing Electron desktop app in [`../app`](../app) still builds the signed
`.dmg` / `.exe` / `.AppImage` installers; these native targets are additive.
