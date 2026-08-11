import SwiftUI

/// Channel 2 — the microphone JIM listens through. Both vocabularies come
/// from the server so the picker cannot offer a value the handler refuses,
/// and the rules travel with the options rather than being retyped here.
/// Console door since task #106; this is the phone's.
struct MicCard: View {
    @EnvironmentObject var state: AppState
    @State private var mic: MicStateRow?
    @State private var types: MicTypeChoices?
    @State private var gains: MicGainChoices?
    @State private var history: [MicEventRow] = []
    @State private var deviceName = ""
    @State private var micType = ""
    @State private var handoverReason = ""
    @State private var showHistory = false
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.ch.mic", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)

            if let mic, mic.attached == true {
                Text("\(mic.device ?? "") · \(mic.mic_type ?? "")")
                    .font(.caption.bold()).foregroundStyle(Theme.txt)
                if let hears = mic.hears, !hears.isEmpty {
                    Text(hears).font(.caption2).foregroundStyle(Theme.t2)
                }
                if mic.capped == true {
                    Text(L10n.t("ns.ch.mic.capped", state.language))
                        .font(.caption2).foregroundStyle(Theme.amber)
                }
                if let gains {
                    Picker(L10n.t("ns.ch.mic.which", state.language),
                           selection: Binding(
                               get: { mic.gain ?? gains.defaultGain },
                               set: { setGain($0) })) {
                        ForEach(gains.levels, id: \.gain) { level in
                            Text(level.gain).tag(level.gain)
                        }
                    }.pickerStyle(.segmented).disabled(busy)
                }
                HStack {
                    Button(L10n.t("ns.ch.mic.detach", state.language)) { detach() }
                        .font(.caption2.bold()).foregroundStyle(Theme.red)
                        .disabled(busy)
                    if mic.listening == true {
                        Button(L10n.t("ns.ch.mic.release", state.language)) { release() }
                            .font(.caption2.bold()).foregroundStyle(Theme.amber)
                            .disabled(busy)
                    }
                }
                // The hand-over: lending JIM your ear, with the reason on
                // the record before the microphone opens.
                TextField(L10n.t("ns.ch.mic.handover", state.language),
                          text: $handoverReason)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                    .onSubmit { handOver() }
            } else {
                Text(L10n.t("ns.ch.mic.none", state.language))
                    .font(.caption2).foregroundStyle(Theme.t3)
                TextField(L10n.t("ns.ch.mic.kind", state.language),
                          text: $deviceName)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                if let types {
                    Picker(L10n.t("ns.ch.mic.which", state.language),
                           selection: $micType) {
                        ForEach(types.personal + types.ambient, id: \.self) {
                            Text($0).tag($0)
                        }
                    }.pickerStyle(.menu)
                }
                Button(L10n.t("ns.ch.mic.attach", state.language)) { attach() }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(busy || deviceName.isEmpty || micType.isEmpty)
            }

            Button(L10n.t("ns.ch.hist", state.language)) {
                showHistory.toggle()
                if showHistory { loadHistory() }
            }.font(.caption2).foregroundStyle(Theme.brandA)
            if showHistory {
                ForEach(history.prefix(6)) { event in
                    HStack {
                        Text("\(event.device) · \(event.gain)")
                            .font(.caption2).foregroundStyle(Theme.t2)
                        if event.live {
                            Text(L10n.t("ns.ch.hist.live", state.language))
                                .font(.caption2.bold()).foregroundStyle(Theme.green)
                        }
                    }
                }
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task {
            await load()
            types = try? await ApiClient.shared.micTypes()
            gains = try? await ApiClient.shared.micGains()
            if micType.isEmpty, let first = types?.personal.first {
                micType = first
            }
        }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        mic = try? await ApiClient.shared.micState(uid: uid, token: token)
    }

    private func loadHistory() {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            history = (try? await ApiClient.shared.micHistory(
                uid: uid, token: token)) ?? []
        }
    }

    private func run(_ work: @escaping () async throws -> MicStateRow) {
        busy = true; error = nil
        Task {
            do { mic = try await work() }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func attach() {
        guard let uid = state.uid, let token = state.token else { return }
        let name = deviceName.trimmingCharacters(in: .whitespaces)
        run { try await ApiClient.shared.attachMic(
            uid: uid, token: token, deviceName: name, micType: micType) }
    }

    private func detach() {
        guard let uid = state.uid, let token = state.token else { return }
        run { try await ApiClient.shared.detachMic(uid: uid, token: token) }
    }

    private func setGain(_ gain: String) {
        guard let uid = state.uid, let token = state.token else { return }
        run { try await ApiClient.shared.setMicGain(
            uid: uid, token: token, gain: gain) }
    }

    private func handOver() {
        guard let uid = state.uid, let token = state.token else { return }
        let reason = handoverReason.trimmingCharacters(in: .whitespaces)
        guard !reason.isEmpty else { return }
        handoverReason = ""
        // "earpiece": the hand-over requires the occupying call to be on a
        // private route — jim/mic.py refuses it on speaker, where the watch
        // would hear both sides.
        run { try await ApiClient.shared.handOverMic(
            uid: uid, token: token, reason: reason, route: "earpiece") }
    }

    private func release() {
        guard let uid = state.uid, let token = state.token else { return }
        run { try await ApiClient.shared.releaseMic(uid: uid, token: token) }
    }
}
