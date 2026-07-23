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
                    MonitorView().tabItem { Label("Monitor", systemImage: "waveform.path.ecg") }
                    CheckinView().tabItem { Label("Check-in", systemImage: "leaf") }
                    CoachView().tabItem { Label("Coach", systemImage: "bubble.left.and.text.bubble.right") }
                    LifeView().tabItem { Label("Life", systemImage: "target") }
                    SafetyView().tabItem { Label("Safety", systemImage: "sos.circle") }
                }
                .tint(Theme.brandA)
            } else {
                WelcomeView()
            }
        }
    }
}
