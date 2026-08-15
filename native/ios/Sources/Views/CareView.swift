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
            // A scrolling strip of icon-over-label buttons rather than a
            // segmented picker. The picker was the right control while every
            // tab was a word; ABRACADABRA is a drawing now (`JimMiniOSMark`),
            // and a segmented control is about thirty points tall — there is
            // no size at which the mark fits inside one. The console made the
            // same move for the same reason, and its phone bar scrolls
            // sideways too: six tabs at a legible icon size do not fit across
            // a phone, and squeezing them to fit is what made the old glyph a
            // glyph.
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 4) {
                    ForEach(Tab.allCases, id: \.self) { item in
                        Button { tab = item } label: {
                            VStack(spacing: 4) {
                                icon(for: item)
                                Text(item.label(state.language))
                                    .font(.system(size: 10, weight: .semibold))
                                    .lineLimit(2)
                                    .multilineTextAlignment(.center)
                            }
                            .frame(width: 84)
                            .padding(.vertical, 8)
                            // Neutral rather than a brand tint, matching the
                            // console: the mark is black, gold and white, and
                            // a coloured box around it is the one thing on the
                            // tile that belongs to neither.
                            .background(tab == item
                                        ? Color.white.opacity(0.10)
                                        : Color.clear)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                        }
                        .buttonStyle(.plain)
                        .foregroundStyle(tab == item ? Theme.txt : Theme.t2)
                    }
                }
                .padding(.horizontal, 20)
            }
            .padding(.top, 12)

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

    /// One icon per tab. ABRACADABRA is the drawn lockup; the rest are SF
    /// Symbols sized to match it, because a menu where one button is 56pt and
    /// the others are 20pt is not a menu — it is one button that got away.
    @ViewBuilder
    private func icon(for item: Tab) -> some View {
        switch item {
        case .engaged:
            JimMiniOSMark(size: 56)
        default:
            Image(systemName: symbol(for: item))
                .font(.system(size: 30))
                .frame(width: 56, height: 56)
        }
    }

    private func symbol(for item: Tab) -> String {
        switch item {
        case .monitor:  return "waveform.path.ecg"
        case .checkin:  return "leaf"
        case .coach:    return "brain.head.profile"
        case .engaged:  return "triangle"   // unreachable; the mark is drawn
        case .presence: return "person.wave.2"
        case .family:   return "person.2"
        }
    }
}
