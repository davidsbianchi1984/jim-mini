import SwiftUI

/// Live Monitoring: push a heart-rate / stress sample -> POST /monitor, show
/// whether the Guardian detected anything and any guidance it delivered.
struct MonitorView: View {
    @EnvironmentObject var state: AppState
    @State private var heartRate = 72.0
    @State private var stress = 0.2
    @State private var result: MonitorResult?
    @State private var busy = false
    @State private var error: String?
    // Spec [0039]: guidance that went out gets asked about, and "it did not
    // help" is not filed away — it re-runs the ladder and names people.
    @State private var followups: FollowupState?
    @State private var answered: FollowupAnswered?
    @State private var note = ""

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(L10n.t("mon", state.language)).font(.title2.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("mon.sub", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 18) {
                    slider(L10n.t("ci.hr", state.language), value: $heartRate, range: 40...180, unit: "bpm", tint: Theme.red)
                    slider(L10n.t("ci.stress", state.language), value: $stress, range: 0...1, unit: "", tint: Theme.amber, percent: true)
                }.card()

                // Clinical captures live with monitoring: what the body
                // shows, sealed beside what the body reports.
                CapturesCard()

                // Your normal, and where its edges sit.
                BandsCard()

                Button(action: send) {
                    HStack { if busy { ProgressView().tint(.white) }; Text(L10n.t("mon.send", state.language)).bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 13))
                }.disabled(busy)

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                if let r = result {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack(spacing: 8) {
                            Circle().fill(r.detected ? Theme.red : Theme.green).frame(width: 9, height: 9)
                            Text(r.detected ? (r.condition ?? "Detected").capitalized : "All clear")
                                .font(.headline).foregroundStyle(Theme.txt)
                            if let sev = r.severity {
                                Text(sev.uppercased()).font(.caption2.bold())
                                    .padding(.horizontal, 7).padding(.vertical, 3)
                                    .background(Theme.red.opacity(0.16)).foregroundStyle(Theme.red)
                                    .clipShape(Capsule())
                            }
                        }
                        if let reason = r.reason { Text(reason).font(.footnote).foregroundStyle(Theme.t2) }
                        if let g = r.guidance {
                            Divider().overlay(Theme.line)
                            Text(g.content).font(.subheadline).foregroundStyle(Theme.txt)
                            GuidanceExtras(guidance: g)
                            if let src = g.source {
                                Text("via \(src)").font(.caption).foregroundStyle(Theme.t3)
                            }
                        }
                    }.card()
                }

                followupCard
            }.padding(20)
        }
        .task { await loadFollowups() }
    }

    // MARK: [0039] — the effectiveness loop

    /// Shown whenever guidance is waiting on an answer, whether it arrived in
    /// this session or an earlier one: a question the app dropped is a question
    /// nobody ever answers.
    @ViewBuilder private var followupCard: some View {
        if let open = followups?.open.first {
            VStack(alignment: .leading, spacing: 10) {
                Text(open.question).font(.headline).foregroundStyle(Theme.txt)
                Text(L10n.fill("mon.about", state.language, ["condition": open.condition]))
                    .font(.caption).foregroundStyle(Theme.t2)
                TextField(L10n.t("mon.add", state.language), text: $note)
                    .font(.subheadline).foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 11))
                HStack(spacing: 10) {
                    answerButton(L10n.t("mon.helped", state.language), helped: true, tint: Theme.green)
                    answerButton(L10n.t("mon.didnot", state.language), helped: false, tint: Theme.amber)
                }
            }.card()
        }

        if let a = answered {
            VStack(alignment: .leading, spacing: 8) {
                Text(L10n.t(a.helped == true ? "mon.resumes" : "mon.person", state.language))
                    .font(.headline)
                    .foregroundStyle(a.helped == true ? Theme.green : Theme.amber)
                if let next = a.next {
                    Text(next).font(.caption).foregroundStyle(Theme.t2)
                }
                // The spec's second door: not a tier, a list of people.
                if let live = a.live_assistance {
                    ForEach(live.options) { option in
                        VStack(alignment: .leading, spacing: 1) {
                            Text(option.name ?? option.kind.replacingOccurrences(
                                of: "_", with: " "))
                                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            if let channel = option.channel, !channel.isEmpty {
                                Text(channel).font(.caption).foregroundStyle(Theme.brandA)
                            }
                            if let note = option.note {
                                Text(note).font(.caption2).foregroundStyle(Theme.t3)
                            }
                        }
                        .padding(.vertical, 2)
                    }
                    Text(live.note ?? "").font(.caption2).foregroundStyle(Theme.t3)
                }
                if let reason = a.reason {
                    Text(reason).font(.caption).foregroundStyle(Theme.t3)
                }
            }.card()
        }
    }

    private func answerButton(_ label: String, helped: Bool,
                              tint: Color) -> some View {
        Button(label) { answer(helped) }
            .font(.caption.bold()).foregroundStyle(.white)
            .padding(.horizontal, 14).padding(.vertical, 10)
            .background(tint).clipShape(Capsule())
            .disabled(busy)
    }

    private func loadFollowups() async {
        guard let uid = state.uid, let token = state.token else { return }
        followups = try? await ApiClient.shared.followups(uid: uid, token: token)
    }

    private func answer(_ helped: Bool) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                answered = try await ApiClient.shared.answerFollowup(
                    uid: uid, token: token, helped: helped,
                    note: note.trimmingCharacters(in: .whitespaces))
                note = ""
                await loadFollowups()
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func slider(_ label: String, value: Binding<Double>, range: ClosedRange<Double>,
                        unit: String, tint: Color, percent: Bool = false) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(label).foregroundStyle(Theme.txt)
                Spacer()
                Text(percent ? "\(Int(value.wrappedValue * 100))%" : "\(Int(value.wrappedValue)) \(unit)")
                    .foregroundStyle(tint).bold().monospacedDigit()
            }.font(.subheadline)
            Slider(value: value, in: range).tint(tint)
        }
    }

    private func send() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do { result = try await ApiClient.shared.monitor(uid: uid, token: token,
                                                              heartRate: Int(heartRate), stress: stress) }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
