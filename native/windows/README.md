# JIM Guardian — Windows (WinUI 3)

A native Windows desktop app in C# / WinUI 3 (Windows App SDK), wired to the JIM
Guardian backend. Same four screens as the other targets — **Welcome/Enroll →
Overview → Live Monitoring → Check-in** — behind a `NavigationView`.

## Run

Requires the **.NET 8 SDK** and the **Windows App SDK** workload (Visual Studio
2022 → *".NET Desktop"* + *"Windows App SDK"*, or `winget install
Microsoft.WindowsAppRuntime.1.6`).

**Visual Studio:** open `JimGuardian.csproj`, pick the `x64` configuration, press
**F5**.

**Command line:**

```powershell
cd native\windows
dotnet build -c Debug -r win-x64
dotnet run -c Debug -r win-x64
```

Start the backend first (Windows reaches `localhost` directly):

```powershell
# from the repo root
$env:JIM_CORS_ORIGINS = "*"; uvicorn jim.api:app
```

The default base URL is `http://127.0.0.1:8000` (see `ApiClient.cs`). The app is
built **unpackaged** (`WindowsPackageType=None`), so it is not subject to the
MSIX loopback restriction and can call `127.0.0.1` without an exemption.

## Layout

| File | Role |
| --- | --- |
| `JimGuardian.csproj` | net8.0-windows target, WindowsAppSDK, unpackaged |
| `App.xaml` / `.cs` | app entry + the JIM palette resource dictionary |
| `MainWindow.xaml` / `.cs` | root frame; routes to Welcome or Shell by state |
| `Views/ShellPage.xaml` | `NavigationView` host + sign-out |
| `Views/WelcomePage` | enroll form → `/enroll` |
| `Views/OverviewPage` | greeting + baseline (`/baseline`) |
| `Views/MonitorPage` | heart-rate / stress sample → `/monitor` |
| `Views/CheckinPage` | mood / energy → `/checkin` |
| `ApiClient.cs` | `HttpClient` client + records |
| `AppState.cs` | identity + token, persisted to LocalAppData |
