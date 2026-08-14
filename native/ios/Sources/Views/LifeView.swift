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
    @State private var drill: Drill?
    @State private var drillAnswer = ""
    @State private var drillLine: String?
    @State private var drillLog: [Drill] = []

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

            // Interview drills: deal, answer, and the reading names who
            // made it — the coach, or the checklist standing in honestly.
            VStack(alignment: .leading, spacing: 8) {
                Text(L10n.t("drl.title", state.language)).font(.headline).foregroundStyle(Theme.txt)
                Button(L10n.t("drl.deal", state.language)) { deal() }
                    .font(.caption.bold()).disabled(busy)
                if let d = drill {
                    Text(d.question).font(.caption).foregroundStyle(Theme.txt)
                    Text((d.probes ?? []).joined(separator: " · "))
                        .font(.caption2).foregroundStyle(Theme.t3)
                    TextField(L10n.t("drl.answer.ph", state.language),
                              text: $drillAnswer)
                        .textFieldStyle(.roundedBorder)
                    Button(L10n.t("drl.read", state.language)) { readAnswer() }
                        .font(.caption.bold())
                        .disabled(busy || drillAnswer.isEmpty)
                }
                if let drillLine {
                    Text(drillLine).font(.caption2).foregroundStyle(Theme.t2)
                }
                ForEach(drillLog.prefix(3)) { d in
                    Text(d.question).font(.caption2).foregroundStyle(Theme.t3)
                }
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
                        // Parking a goal and deleting one are different
                        // things, and until now only the first had a door:
                        // a goal set by mistake could be marked abandoned
                        // and never removed.
                        Button(L10n.t("aim.goals.remove", state.language)) {
                            Task {
                                guard let uid = state.uid, let token = state.token
                                else { return }
                                try? await ApiClient.shared.removeGoal(
                                    uid: uid, token: token, goalId: g.id)
                                await load()
                            }
                        }.font(.caption2).foregroundStyle(Theme.t2).disabled(busy)
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
        drillLog = (try? await ApiClient.shared.drills(uid: uid, token: token)) ?? []
    }

    private func add() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task {
            _ = try? await ApiClient.shared.addGoal(uid: uid, token: token, area: area, title: title, target: nil)
            title = ""; await load(); busy = false
        }
    }

    private func deal() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task {
            drillLine = nil
            drill = try? await ApiClient.shared.startDrill(uid: uid, token: token)
            busy = false
        }
    }

    private func readAnswer() {
        guard let uid = state.uid, let token = state.token,
              let d = drill else { return }
        busy = true
        Task {
            let read = try? await ApiClient.shared.answerDrill(
                uid: uid, token: token, drillId: d.id, answer: drillAnswer)
            // The reading, or the probes to measure against, honestly.
            drillLine = read?.critique
                ?? (d.probes ?? []).joined(separator: " · ")
            drill = nil; drillAnswer = ""; busy = false
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
                    // A mis-tapped tick, and the way back from an engaged
                    // session that ticked it for you.
                    Button(L10n.t("aim.habits.undid", state.language)) {
                        Task {
                            guard let uid = state.uid, let token = state.token
                            else { return }
                            let today = ISO8601DateFormatter()
                                .string(from: Date()).prefix(10)
                            try? await ApiClient.shared.unlogHabit(
                                uid: uid, token: token, habitId: h.id,
                                day: String(today))
                            await load()
                        }
                    }.font(.caption2).foregroundStyle(Theme.t2)
                    Button(L10n.t("aim.habits.drop", state.language)) {
                        Task {
                            guard let uid = state.uid, let token = state.token
                            else { return }
                            try? await ApiClient.shared.removeHabit(
                                uid: uid, token: token, habitId: h.id)
                            await load()
                        }
                    }.font(.caption2).foregroundStyle(Theme.t2)
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
    @State private var meals: [Meal] = []
    @State private var mealNote = ""
    @State private var letters: [Letter] = []
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
                    // Somebody writing their own diary should always have had
                    // this, and it is the way back from an engaged session
                    // that wrote an entry for them.
                    Button(L10n.t("jrn.remove", state.language)) {
                        Task {
                            guard let uid = state.uid, let token = state.token
                            else { return }
                            try? await ApiClient.shared.removeJournal(
                                uid: uid, token: token, entryId: e.id)
                            await load()
                        }
                    }.font(.caption2).foregroundStyle(Theme.t2)
                }.card()
            }

            // Meals: the note is the log; the photo, when the phone app
            // attaches one, is a sealed receipt. No pretended vision.
            VStack(alignment: .leading, spacing: 8) {
                Text(L10n.t("mea.title", state.language)).font(.headline).foregroundStyle(Theme.txt)
                HStack {
                    TextField(L10n.t("mea.ph", state.language), text: $mealNote)
                        .textFieldStyle(.roundedBorder)
                    Button(L10n.t("mea.log", state.language)) { logMeal() }
                        .font(.caption.bold()).disabled(busy || mealNote.isEmpty)
                }
                ForEach(meals, id: \.id) { m in
                    Text(m.logged + (m.photo_sealed ? " · 🔒" : ""))
                        .font(.caption).foregroundStyle(Theme.t2)
                }
            }.card()

            // The weekly letter: composed only from what was logged.
            VStack(alignment: .leading, spacing: 8) {
                Text(L10n.t("let.title", state.language)).font(.headline).foregroundStyle(Theme.txt)
                Button(L10n.t("let.write", state.language)) { writeLetter() }
                    .font(.caption.bold()).disabled(busy)
                ForEach(letters, id: \.id) { l in
                    VStack(alignment: .leading, spacing: 2) {
                        Text(l.week_start).font(.caption2).foregroundStyle(Theme.t3)
                        Text(l.body).font(.caption).foregroundStyle(Theme.t2)
                    }
                }
            }.card()
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        entries = (try? await ApiClient.shared.journal(uid: uid, token: token)) ?? []
        meals = (try? await ApiClient.shared.meals(uid: uid, token: token)) ?? []
        letters = (try? await ApiClient.shared.letters(uid: uid, token: token)) ?? []
    }

    private func writeLetter() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task { _ = try? await ApiClient.shared.writeLetter(uid: uid, token: token)
            await load(); busy = false }
    }

    private func logMeal() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task { _ = try? await ApiClient.shared.logMeal(uid: uid, token: token, note: mealNote)
            mealNote = ""; await load(); busy = false }
    }

    private func add() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task { try? await ApiClient.shared.addJournal(uid: uid, token: token, text: text)
            text = ""; await load(); busy = false }
    }
}
