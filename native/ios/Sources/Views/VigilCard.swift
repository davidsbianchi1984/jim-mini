import SwiftUI

/// The vigil: the alarm that fires on the *absence* of readings. A steward,
/// named and worded in advance, is asked to check on the person when the
/// signals stop. It never calls emergency services — it knocks on a door.
/// Console door since 0.8.0; this is the phone's.
struct VigilCard: View {
    @EnvironmentObject var state: AppState
    @State private var status: VigilStatus?
    @State private var stewardName = ""
    @State private var stewardChannel = ""
    @State private var quietDays = "3"
    @State private var note = ""
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.vg.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.vg.pitch", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)

            if let status {
                if status.tripped == true {
                    Text(L10n.t("ns.vg.tripped", state.language)
                            .replacingOccurrences(of: "{name}",
                                with: status.steward_name ?? "")
                            .replacingOccurrences(of: "{after}",
                                with: L10n.t("ns.vg.after", state.language)
                                    .replacingOccurrences(of: "{n}",
                                        with: String(status.quiet_days ?? 0))))
                        .font(.caption.bold()).foregroundStyle(Theme.amber)
                    Button(L10n.t("ns.vg.okay", state.language)) {
                        run { try await ApiClient.shared.resolveVigil(
                            uid: state.uid!, token: state.token!) }
                    }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Theme.green).clipShape(Capsule())
                } else if status.armed {
                    Text(L10n.t("ns.vg.armed", state.language)
                            .replacingOccurrences(of: "{when}",
                                with: status.silent_hours.map {
                                    "\(Int($0)) h" } ?? "—")
                            .replacingOccurrences(of: "{name}",
                                with: status.steward_name ?? ""))
                        .font(.caption2).foregroundStyle(Theme.green)
                }
            }

            Text(L10n.t("ns.vg.name", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField(L10n.t("ns.vg.name.ph", state.language),
                      text: $stewardName)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Text(L10n.t("ns.vg.reach", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField(L10n.t("ns.vg.reach.ph", state.language),
                      text: $stewardChannel)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Text(L10n.t("ns.vg.days", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField("3", text: $quietDays)
                .keyboardType(.decimalPad)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Text(L10n.t("ns.vg.words", state.language)
                 + L10n.t("ns.vg.words.note", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField(L10n.t("ns.vg.words.ph", state.language), text: $note)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))

            HStack {
                Button(L10n.t(status?.armed == true ? "ns.vg.update"
                                                    : "ns.vg.arm",
                              state.language)) { arm() }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(busy || stewardName.isEmpty
                              || stewardChannel.isEmpty)
                if status?.armed == true {
                    Button(L10n.t("ns.vg.disarm", state.language)) {
                        run { try await ApiClient.shared.disarmVigil(
                            uid: state.uid!, token: state.token!) }
                    }
                    .font(.caption2).foregroundStyle(Theme.red)
                    .disabled(busy)
                }
                // A read, not a sweep — the way to look without acting.
                Button(L10n.t("ns.vg.check", state.language)) {
                    run { try await ApiClient.shared.vigilStatus(
                        uid: state.uid!, token: state.token!) }
                }
                .font(.caption2).foregroundStyle(Theme.t3)
                .disabled(busy)
            }

            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await sweep() }
    }

    /// Opening the screen sweeps — idempotent, trips at most once, and
    /// opening the app is the natural moment to ask whether anybody has
    /// gone quiet. Same choice the console made.
    private func sweep() async {
        guard let uid = state.uid, let token = state.token else { return }
        status = try? await ApiClient.shared.sweepVigil(uid: uid, token: token)
        fill()
    }

    private func fill() {
        guard let status, status.armed else { return }
        if stewardName.isEmpty { stewardName = status.steward_name ?? "" }
        if stewardChannel.isEmpty {
            stewardChannel = status.steward_channel ?? ""
        }
        if let days = status.quiet_days { quietDays = String(days) }
        if note.isEmpty { note = status.note ?? "" }
    }

    private func run(_ work: @escaping () async throws -> VigilStatus) {
        busy = true; error = nil
        Task {
            do { status = try await work() }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func arm() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                status = try await ApiClient.shared.armVigil(
                    uid: uid, token: token,
                    stewardName: stewardName.trimmingCharacters(in: .whitespaces),
                    stewardChannel: stewardChannel.trimmingCharacters(in: .whitespaces),
                    quietDays: Double(quietDays) ?? 3.0,
                    note: note.trimmingCharacters(in: .whitespaces))
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
