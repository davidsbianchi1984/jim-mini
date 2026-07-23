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
                    OverviewView().tabItem { Label("Overview", systemImage: "circle.grid.cross") }
                    CareView().tabItem { Label("Care", systemImage: "heart.text.square") }
                    LifeView().tabItem { Label("Life", systemImage: "target") }
                    SafetyView().tabItem { Label("Safety", systemImage: "sos.circle") }
                    ConnectView().tabItem { Label("Connect", systemImage: "link") }
                }
                .tint(Theme.brandA)
            } else {
                WelcomeView()
            }
        }
    }
}
