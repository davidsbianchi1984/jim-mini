import SwiftUI

/// Care: the three ways you interact with your Guardian — live monitoring,
/// mood check-ins, and coaching — behind one tab so the bar stays at five.
struct CareView: View {
    enum Tab: String, CaseIterable {
        case monitor = "Monitor", checkin = "Check-in",
             coach = "Coach", engaged = "Engaged",
             presence = "Presence", family = "Family"

        /// English lived in the `case` clause, where no `Text("…")`
        /// pattern looks — the same shape ConnectView had, written
        /// down at 0.47.2 as belonging to the round that takes this
        /// screen. The raw value is the stored identity and does not
        /// move; only the words come from the table.
        func label(_ lang: String) -> String {
            switch self {
            case .monitor: return L10n.t("tab.monitor", lang)
            case .checkin: return L10n.t("tab.checkin", lang)
            case .coach: return L10n.t("tab.coach", lang)
            case .engaged: return L10n.t("eng.tab", lang)
            case .presence: return L10n.t("presence.tab", lang)
            case .family: return L10n.t("tab.family", lang)
            }
        }
    }
    // The strip reads its words from the table now, and the table
    // needs the language.
    @EnvironmentObject var state: AppState
    @State private var tab: Tab = .monitor

    var body: some View {
        VStack(spacing: 0) {
            Picker("", selection: $tab) {
                ForEach(Tab.allCases, id: \.self) {
                        Text($0.label(state.language)).tag($0)
                    }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 20).padding(.top, 12)

            switch tab {
            case .monitor: MonitorView()
            case .checkin: CheckinView()
            case .coach: CoachView()
            // The coach answers a turn; this one stays engaged and can act.
            // Same group for the same reason the presence is here — they are
            // faces of one thing, and splitting them across the bar would
            // ask a person to know which of three doors they wanted before
            // they knew what they were asking for.
            case .engaged: EngagedView()
            // The coach answers; the presence speaks first. Same screen
            // group because they are two halves of one thing.
            case .presence: PresenceView()
            case .family: FamilyView()
            }
        }
    }
}
