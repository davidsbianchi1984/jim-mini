import SwiftUI

/// Care: the three ways you interact with your Guardian — live monitoring,
/// mood check-ins, and coaching — behind one tab so the bar stays at five.
struct CareView: View {
    enum Tab: String, CaseIterable { case monitor = "Monitor", checkin = "Check-in", coach = "Coach" }
    @State private var tab: Tab = .monitor

    var body: some View {
        VStack(spacing: 0) {
            Picker("", selection: $tab) {
                ForEach(Tab.allCases, id: \.self) { Text($0.rawValue).tag($0) }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 20).padding(.top, 12)

            switch tab {
            case .monitor: MonitorView()
            case .checkin: CheckinView()
            case .coach: CoachView()
            }
        }
    }
}
