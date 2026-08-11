import SwiftUI

/// Life: goals, habits, and journal behind a segmented switcher.
struct LifeView: View {
    enum Tab: String, CaseIterable {
        case goals = "Goals", habits = "Habits", journal = "Journal",
             money = "Money", schedule = "Schedule", shop = "Shop",
             circle = "Circle"

        /// The strip said *Shop* where the backend already serves
        /// *Shops* through `i18n.shop_labels`, which the desktop
        /// renders — one strip, two spellings. The rows take the
        /// server's English so nothing drifts.
        func label(_ lang: String) -> String {
            switch self {
            case .goals: return L10n.t("life.goals", lang)
            case .habits: return L10n.t("life.habits", lang)
            case .journal: return L10n.t("life.journal", lang)
            case .money: return L10n.t("life.money", lang)
            case .schedule: return L10n.t("life.schedule", lang)
            case .shop: return L10n.t("life.shops", lang)
            case .circle: return L10n.t("life.circle", lang)
            }
        }
    }
    // The strip reads its words from the table now, and the table
    // needs the language.
    @EnvironmentObject var state: AppState
    @State private var tab: Tab = .goals

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Picker("", selection: $tab) {
                    ForEach(Tab.allCases, id: \.self) {
                        Text($0.label(state.language)).tag($0)
                    }
                }.pickerStyle(.segmented)

                switch tab {
                case .goals: GoalsSection(); ActivityCard()
                case .habits: HabitsSection()
                case .journal: JournalSection()
                case .money: MoneySection(); BudgetCard()
                // The dose board is a schedule the body keeps.
                case .schedule: ScheduleSection(); MedsCard()
                case .shop: ShoppingSection()
                case .circle: CircleSection()
                }
            }.padding(20)
        }
    }
}

// MARK: Goals

private struct GoalsSection: View {
    @EnvironmentObject var state: AppState
    @State private var goals: [Goal] = []
    @State private var area = "personal_growth"
    @State private var title = ""
    @State private var busy = false

    private let areas = ["mental_health", "health_fitness", "career",
                         "finance", "relationships", "personal_growth"]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            VStack(alignment: .leading, spacing: 10) {
                Text(L10n.t("goal.new", state.language)).font(.headline).foregroundStyle(Theme.txt)
                Picker("", selection: $area) {
                    ForEach(areas, id: \.self) { Text($0.replacingOccurrences(of: "_", with: " ").capitalized).tag($0) }
                }.pickerStyle(.menu).tint(Theme.brandA)
                TextField(L10n.t("goal.title.ph", state.language), text: $title).foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot).clipShape(RoundedRectangle(cornerRadius: 11))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                Button(action: add) {
                    HStack { if busy { ProgressView().tint(.white) }; Text(L10n.t("goal.add", state.language)).bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 12)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }.disabled(title.isEmpty || busy)
            }.card()

            ForEach(goals, id: \.id) { g in
                VStack(alignment: .leading, spacing: 4) {
                    Text(g.title).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    HStack {
                        Text(g.area.replacingOccurrences(of: "_", with: " ").capitalized)
                            .font(.caption).foregroundStyle(Theme.t2)
                        Spacer()
                        Text((g.status ?? "active").capitalized).font(.caption).foregroundStyle(Theme.t3)
                        if (g.status ?? "active") == "active" {
                            Button(L10n.t("aim.goals.done", state.language)) { finish(g.id) }
                                .font(.caption2).foregroundStyle(Theme.green)
                                .disabled(busy)
                        }
                    }
                }.card()
            }
        }
        .refreshable { await load() }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        goals = (try? await ApiClient.shared.goals(uid: uid, token: token)) ?? []
    }

    private func add() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task {
            _ = try? await ApiClient.shared.addGoal(uid: uid, token: token, area: area, title: title, target: nil)
            title = ""; await load(); busy = false
        }
    }

    private func finish(_ goalId: String) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task {
            _ = try? await ApiClient.shared.updateGoal(
                uid: uid, token: token, goalId: goalId, progress: 1.0,
                status: "completed")
            await load(); busy = false
        }
    }
}

// MARK: Habits

private struct HabitsSection: View {
    @EnvironmentObject var state: AppState
    @State private var habits: [Habit] = []
    @State private var name = ""
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            VStack(alignment: .leading, spacing: 10) {
                Text(L10n.t("habit.new", state.language)).font(.headline).foregroundStyle(Theme.txt)
                TextField(L10n.t("habit.name.ph", state.language), text: $name).foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot).clipShape(RoundedRectangle(cornerRadius: 11))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                Button(action: add) {
                    HStack { if busy { ProgressView().tint(.white) }; Text(L10n.t("habit.add", state.language)).bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 12)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }.disabled(name.isEmpty || busy)
            }.card()

            ForEach(habits, id: \.id) { h in
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(h.name).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                        Text(L10n.t("habit.streak", state.language)
                                .replacingOccurrences(of: "{n}",
                                                      with: String(h.streak ?? 0))).font(.caption).foregroundStyle(Theme.amber)
                    }
                    Spacer()
                    Button(L10n.t("habit.log", state.language)) { logHabit(h.id) }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 14).padding(.vertical, 8)
                        .background(Theme.brandA).clipShape(Capsule())
                }.card()
            }
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        habits = (try? await ApiClient.shared.habits(uid: uid, token: token)) ?? []
    }

    private func add() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task { _ = try? await ApiClient.shared.addHabit(uid: uid, token: token, name: name)
            name = ""; await load(); busy = false }
    }

    private func logHabit(_ id: String) {
        guard let uid = state.uid, let token = state.token else { return }
        Task { try? await ApiClient.shared.logHabit(uid: uid, token: token, habitId: id); await load() }
    }
}

// MARK: Journal

private struct JournalSection: View {
    @EnvironmentObject var state: AppState
    @State private var entries: [JournalItem] = []
    @State private var text = ""
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            VStack(alignment: .leading, spacing: 10) {
                Text(L10n.t("jrn.new", state.language)).font(.headline).foregroundStyle(Theme.txt)
                TextField(L10n.t("jrn.entry.ph", state.language), text: $text,
                          axis: .vertical)
                    .lineLimit(2...5).foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot).clipShape(RoundedRectangle(cornerRadius: 11))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                Button(action: add) {
                    HStack { if busy { ProgressView().tint(.white) }; Text(L10n.t("jrn.save", state.language)).bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 12)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }.disabled(text.isEmpty || busy)
            }.card()

            ForEach(entries.reversed(), id: \.id) { e in
                VStack(alignment: .leading, spacing: 4) {
                    Text(e.text ?? "—").font(.subheadline).foregroundStyle(Theme.txt)
                    if let d = e.created_at { Text(d).font(.caption2).foregroundStyle(Theme.t3) }
                }.card()
            }
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        entries = (try? await ApiClient.shared.journal(uid: uid, token: token)) ?? []
    }

    private func add() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task { try? await ApiClient.shared.addJournal(uid: uid, token: token, text: text)
            text = ""; await load(); busy = false }
    }
}
