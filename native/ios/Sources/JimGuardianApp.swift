import SwiftUI

@main
struct JimGuardianApp: App {
    @StateObject private var state = AppState()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(state)
                .preferredColorScheme(.dark)
        }
    }
}

/// Switches between the enroll flow and the signed-in tab bar.
struct RootView: View {
    @EnvironmentObject var state: AppState

    var body: some View {
        ZStack {
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
        }
    }
}
