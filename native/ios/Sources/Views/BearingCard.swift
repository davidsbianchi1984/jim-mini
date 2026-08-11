import SwiftUI

/// The Guardian's bearing: the tone it speaks in, what it was told —
/// conditions, context from other sources, a word said unprompted — whether
/// its answers landed, and what it made of all that. Console door (Bearing)
/// since 0.30.x; this is the phone's.
struct BearingCard: View {
    @EnvironmentObject var state: AppState
    @State private var tone = "balanced"
    @State private var condition = "anxiety"
    @State private var conditionNote = ""
    @State private var known: [String] = []
    @State private var source = ""
    @State private var contextRefused: String?
    @State private var said: CompanionSaid?
    @State private var report: ProgressReport?
    @State private var insightRows: [InsightRow] = []
    @State private var eventRows: [EventRow] = []
    @State private var calmDone: [CalmHistoryRow] = []
    @State private var exchanges: [CoachExchange] = []
    @State private var busy = false
    @State private var error: String?

    // The tone chips are the console's three; the condition list is the
    // server's own vocabulary from ConditionDeclare.
    private let tones = [("direct", "brg.speak.direct"),
                         ("balanced", "brg.speak.balanced"),
                         ("cautious", "brg.speak.cautious")]
    private let conditions = ["anxiety", "depression", "stress", "phobia",
                              "financial_stress", "relationship",
                              "physical_distress", "physical_injury"]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("brg.speak.tone", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            HStack(spacing: 8) {
                ForEach(tones, id: \.0) { choice, key in
                    Button(L10n.t(key, state.language)) {
                        tone = choice
                    }
                    .font(.caption2)
                    .foregroundStyle(tone == choice ? .white : Theme.t2)
                    .padding(.horizontal, 10).padding(.vertical, 6)
                    .background(tone == choice ? Theme.brandA : Theme.scrBot)
                    .clipShape(Capsule())
                }
                Button(L10n.t("brg.speak.go", state.language)) { speak() }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy)
            }

            Divider().background(Theme.line)
            Text(L10n.t("brg.told", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(conditions, id: \.self) { choice in
                        Button(choice) { condition = choice }
                            .font(.caption2)
                            .foregroundStyle(condition == choice
                                             ? .white : Theme.t2)
                            .padding(.horizontal, 8).padding(.vertical, 4)
                            .background(condition == choice ? Theme.brandA
                                                            : Theme.scrBot)
                            .clipShape(Capsule())
                    }
                }
            }
            TextField(L10n.t("brg.told.note.ph", state.language),
                      text: $conditionNote)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Button(L10n.t("brg.told.tell", state.language)) { tell() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy)
            if !known.isEmpty {
                Text(known.joined(separator: " · "))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack(spacing: 8) {
                TextField(L10n.t("brg.told.src.ph", state.language),
                          text: $source)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                Button(L10n.t("brg.told.ctx", state.language)) { context() }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy || source.isEmpty)
            }
            if let contextRefused {
                Text(L10n.t("brg.told.refused", state.language)
                        .replacingOccurrences(of: "{err}",
                                              with: contextRefused))
                    .font(.caption2).foregroundStyle(Theme.amber)
            }
            Button(L10n.t("brg.told.say", state.language)) { unprompted() }
                .font(.caption2).foregroundStyle(Theme.brandA)
                .disabled(busy)
            if let said {
                Text(said.content).font(.caption2).foregroundStyle(Theme.t2)
            }

            Divider().background(Theme.line)
            Text(L10n.t("brg.tell", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            HStack(spacing: 8) {
                Button(L10n.t("brg.tell.good", state.language)) { rate("up") }
                    .font(.caption2).foregroundStyle(Theme.green)
                    .disabled(busy)
                Button(L10n.t("brg.tell.bad", state.language)) { rate("down") }
                    .font(.caption2).foregroundStyle(Theme.red)
                    .disabled(busy)
            }

            Divider().background(Theme.line)
            Text(L10n.t("brg.made", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let report {
                Text(L10n.t("brg.made.stats", state.language)
                        .replacingOccurrences(of: "{c}",
                                              with: String(report.checkins.count))
                        .replacingOccurrences(
                            of: "{m}",
                            with: report.checkins.avg_mood.map {
                                String(format: "%.1f", $0) } ?? "—")
                        .replacingOccurrences(of: "{i}",
                                              with: String(insightRows.count))
                        .replacingOccurrences(of: "{e}",
                                              with: String(eventRows.count))
                        .replacingOccurrences(of: "{s}",
                                              with: String(calmDone.count))
                        .replacingOccurrences(of: "{x}",
                                              with: String(exchanges.count)))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            ForEach(insightRows.prefix(3), id: \.id) { row in
                Text(row.message).font(.caption2).foregroundStyle(Theme.t3)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        report = try? await ApiClient.shared.progressReport(uid: uid,
                                                            token: token)
        // Insights are a Pro capability; a plan refusal reads as none yet.
        insightRows = (try? await ApiClient.shared.insights(uid: uid,
                                                            token: token)) ?? []
        eventRows = (try? await ApiClient.shared.events(uid: uid,
                                                        token: token)) ?? []
        calmDone = (try? await ApiClient.shared.calmHistory(uid: uid,
                                                            token: token)) ?? []
        exchanges = (try? await ApiClient.shared.coachHistory(uid: uid,
                                                              token: token)) ?? []
    }

    private func run(_ work: @escaping () async throws -> Void) {
        busy = true; error = nil
        Task {
            do { try await work() }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func speak() {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            _ = try await ApiClient.shared.setPersonality(uid: uid,
                                                          token: token,
                                                          tone: tone)
        }
    }

    private func tell() {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            let r = try await ApiClient.shared.declareCondition(
                uid: uid, token: token, condition: condition,
                note: conditionNote)
            known = r.known_conditions
            conditionNote = ""
        }
    }

    private func context() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil; contextRefused = nil
        Task {
            do {
                _ = try await ApiClient.shared.giveContext(
                    uid: uid, token: token,
                    source: source.trimmingCharacters(in: .whitespaces),
                    kind: "event",
                    data: ["title": "something on the calendar"])
            } catch { contextRefused = error.localizedDescription }
            busy = false
        }
    }

    private func unprompted() {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            said = try await ApiClient.shared.companionCheckin(uid: uid,
                                                               token: token)
        }
    }

    private func rate(_ rating: String) {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            _ = try await ApiClient.shared.sendGuidanceFeedback(
                uid: uid, token: token, rating: rating)
        }
    }
}
