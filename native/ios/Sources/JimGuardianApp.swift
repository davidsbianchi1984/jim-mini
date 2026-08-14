import SwiftUI

@main
struct JimGuardianApp: App {
    @StateObject private var state = AppState()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(state)
                .preferredColorScheme(.dark)
                // What the buffer is for. Detached and unawaited: a
                // diagnostic must never be the reason a launch is slow, and
                // `send` returns an outcome rather than throwing, so there is
                // nothing here to handle. It answers `.awaitingNotice` until
                // somebody has been told and chosen.
                .task { await Problems.send() }
        }
    }
}

/// Switches between the enroll flow and the signed-in tab bar.
struct RootView: View {
    @EnvironmentObject var state: AppState

    var body: some View {
        ZStack(alignment: .top) {
            Theme.bg.ignoresSafeArea()
            if state.isEnrolled {
                TabView {
                    OverviewView().tabItem { Label(L10n.t("tab.overview", state.language), systemImage: "circle.grid.cross") }
                    CareView().tabItem { Label(L10n.t("tab.care", state.language), systemImage: "heart.text.square") }
                    LifeView().tabItem { Label(L10n.t("tab.life", state.language), systemImage: "target") }
                    SafetyView().tabItem { Label(L10n.t("tab.safety", state.language), systemImage: "sos.circle") }
                    ConnectView().tabItem { Label(L10n.t("tab.connect", state.language), systemImage: "link") }
                }
                .tint(Theme.brandA)
            } else {
                WelcomeView()
            }
            // Above the tab bar and above the welcome flow both: a stale
            // backend breaks the screens a signed-out person meets first,
            // and telling them only after they get in would be telling
            // them after the part that fails.
            VersionGuardBar()
        }
    }
}
