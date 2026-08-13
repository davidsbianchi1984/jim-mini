import SwiftUI

/// Guided calm, a workout for the time you have, and a day of meals that
/// fits: protocols and templates, not generations — the counts never vary.
/// Console doors since 0.15.0; these are the phone's.
struct WellnessCard: View {
    @EnvironmentObject var state: AppState
    @State private var catalog: [CalmSessionRow] = []
    @State private var started: CalmStarted?
    @State private var history: [CalmHistoryRow] = []
    @State private var minutes = 20
    @State private var level = "beginner"
    @State private var focus = "mobility"
    @State private var workout: WorkoutPlan?
    @State private var goal = "eat_healthier"
    @State private var days = 2
    @State private var meals: MealPlan?
    @State private var busy = false
    @State private var error: String?

    // The server's own vocabulary for levels and goals; the goal labels are
    // the console's translated rows.
    private let levels = ["beginner", "intermediate", "advanced"]
    private let goals = [("lose_weight", "wel.meals.lose"),
                        ("gain_muscle", "wel.meals.gain"),
                        ("eat_healthier", "wel.meals.healthier")]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("wel.calm", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("wel.calm.pitch", state.language)
                    .replacingOccurrences(of: "{spoken}", with: ""))
                .font(.caption2).foregroundStyle(Theme.t2)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(catalog, id: \.kind) { session in
                        Button(L10n.t("wel.calm.tile", state.language)
                                .replacingOccurrences(of: "{title}",
                                                      with: session.title)
                                .replacingOccurrences(
                                    of: "{n}", with: String(session.minutes))) {
                            begin(session.kind)
                        }
                        .font(.caption2)
                        .foregroundStyle(started?.kind == session.kind
                                         ? .white : Theme.t2)
                        .padding(.horizontal, 10).padding(.vertical, 6)
                        .background(started?.kind == session.kind
                                    ? Theme.brandA : Theme.scrBot)
                        .clipShape(Capsule())
                        .disabled(busy)
                    }
                }
            }
            if let started {
                ForEach(Array(started.steps.enumerated()), id: \.offset) { index, step in
                    Text(L10n.t("wel.calm.step", state.language)
                            .replacingOccurrences(of: "{i}",
                                                  with: String(index + 1))
                            .replacingOccurrences(of: "{n}",
                                                  with: String(started.steps.count))
                            .replacingOccurrences(of: "{sec}",
                                                  with: String(step.seconds))
                         + " — " + step.say)
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                Text(started.note).font(.caption2).foregroundStyle(Theme.t3)
            }
            ForEach(Array(history.prefix(3).enumerated()), id: \.offset) { _, row in
                Text("\(row.title) · \(row.at)")
                    .font(.caption2).foregroundStyle(Theme.t3)
            }

            Divider().background(Theme.line)
            Text(L10n.t("wel.work", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            HStack(spacing: 8) {
                Text(L10n.t("wel.work.minutes", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                Stepper("\(minutes)", value: $minutes, in: 5...90, step: 5)
                    .font(.caption2).foregroundStyle(Theme.txt)
            }
            HStack(spacing: 8) {
                Text(L10n.t("wel.work.level", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                ForEach(levels, id: \.self) { choice in
                    Button(choice) { level = choice }
                        .font(.caption2)
                        .foregroundStyle(level == choice ? .white : Theme.t2)
                        .padding(.horizontal, 8).padding(.vertical, 4)
                        .background(level == choice ? Theme.brandA
                                                    : Theme.scrBot)
                        .clipShape(Capsule())
                }
            }
            field(L10n.t("wel.work.focus", state.language)) {
                TextField("", text: $focus)
            }
            Button(L10n.t("wel.work.build", state.language)) { buildWorkout() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy)
            if let workout {
                ForEach(Array(workout.blocks.prefix(8).enumerated()),
                        id: \.offset) { _, block in
                    Text(block.name
                         + L10n.t("wel.work.block", state.language)
                            .replacingOccurrences(of: "{sec}",
                                                  with: String(block.seconds))
                            .replacingOccurrences(of: "{cue}", with: block.cue))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
            }

            Divider().background(Theme.line)
            Text(L10n.t("wel.meals", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            HStack(spacing: 8) {
                Text(L10n.t("wel.meals.goal", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                ForEach(goals, id: \.0) { choice, key in
                    Button(L10n.t(key, state.language)) { goal = choice }
                        .font(.caption2)
                        .foregroundStyle(goal == choice ? .white : Theme.t2)
                        .padding(.horizontal, 8).padding(.vertical, 4)
                        .background(goal == choice ? Theme.brandA : Theme.scrBot)
                        .clipShape(Capsule())
                }
            }
            HStack(spacing: 8) {
                Text(L10n.t("wel.meals.days", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                Stepper("\(days)", value: $days, in: 1...7)
                    .font(.caption2).foregroundStyle(Theme.txt)
            }
            Button(L10n.t("wel.meals.plan", state.language)) { buildMeals() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy)
            if let meals {
                Text(L10n.t("wel.meals.shape", state.language)
                        .replacingOccurrences(of: "{why}",
                                              with: meals.shape.why)
                        .replacingOccurrences(
                            of: "{kcal}",
                            with: String(meals.shape.orientation_calories)))
                    .font(.caption2).foregroundStyle(Theme.t2)
                ForEach(meals.days, id: \.day_number) { day in
                    Text(L10n.t("wel.meals.day", state.language)
                            .replacingOccurrences(of: "{n}",
                                                  with: String(day.day_number)))
                        .font(.caption2.bold()).foregroundStyle(Theme.t2)
                    ForEach(day.meals, id: \.slot) { meal in
                        Text("\(meal.slot): \(meal.name)")
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                }
                Text(meals.disclaimer).font(.caption2).foregroundStyle(Theme.t3)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task {
            catalog = (try? await ApiClient.shared.calmCatalog())?.sessions ?? []
            await refreshHistory()
        }
    }

    private func field<Content: View>(_ label: String,
                                      @ViewBuilder _ content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label).font(.caption2).foregroundStyle(Theme.t2)
            content()
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
        }
    }

    private func refreshHistory() async {
        guard let uid = state.uid, let token = state.token else { return }
        history = (try? await ApiClient.shared.calmHistory(uid: uid,
                                                           token: token)) ?? []
    }

    private func begin(_ kind: String) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                started = try await ApiClient.shared.startCalm(
                    uid: uid, token: token, kind: kind)
                await refreshHistory()
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func buildWorkout() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                workout = try await ApiClient.shared.workoutPlan(
                    uid: uid, token: token, minutes: minutes, level: level,
                    focus: focus.trimmingCharacters(in: .whitespaces))
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func buildMeals() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                meals = try await ApiClient.shared.mealPlan(
                    uid: uid, token: token, goal: goal, preferences: [],
                    days: days)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
