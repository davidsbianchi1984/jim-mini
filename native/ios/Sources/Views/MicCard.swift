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
    // An aid on a call other people can hear. Not listening until the notice
    // has gone out on the line — see jim/oncall.py.
    @State private var callRoute = "speaker"
    @State private var callNumber = ""
    @State private var call: AssistedCall?
    @State private var calls: [CallRow] = []
    // What may sense this person, and through what. Off rows included.
    @State private var mons: [MonitorRow] = []

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            // Everywhere the monitoring plugs in. The rows that sense other
            // people carry that on their face, and switching one on says the
            // people in that space have been told.
            Text(L10n.t("mon.head", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("mon.lead", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            ForEach(mons, id: \.name) { m in
                VStack(alignment: .leading, spacing: 2) {
                    Text(m.says).font(.caption).foregroundStyle(Theme.txt)
                    Text(m.senses.joined(separator: " · ")
                         + (m.catches_others
                            ? " · " + L10n.t("mon.others", state.language)
                            : ""))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Text(L10n.t("mon.keeps", state.language) + " " + m.holds)
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Text(m.on ? L10n.t("mon.on", state.language)
                              : L10n.t("mon.off", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    if m.on {
                        Button(L10n.t("mon.sense", state.language)) {
                            sense(m)
                        }.font(.caption).tint(Theme.brandA)
                        Button(L10n.t("mon.unplug", state.language)) {
                            unplug(m)
                        }.font(.caption).tint(Theme.t2)
                    } else {
                        Button(m.catches_others
                               ? L10n.t("mon.plug.told", state.language)
                               : L10n.t("mon.plug", state.language)) {
                            plug(m)
                        }.font(.caption).tint(Theme.brandA)
                    }
                }
            }

            Text(L10n.t("cal.head", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("cal.lead", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            TextField(L10n.t("cal.number.ph", state.language),
                      text: $callNumber)
                .textFieldStyle(.roundedBorder)
            Button(L10n.t("cal.open", state.language)) { openCall() }
                .font(.caption).tint(Theme.brandA).disabled(busy)
            if let c = call {
                Text(L10n.t("cal.play", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                ForEach(c.notices, id: \.language) { part in
                    Text(part.language + " — " + part.words)
                        .font(.caption2).foregroundStyle(Theme.txt)
                }
                Text(L10n.t("cal.from", state.language) + " "
                     + c.language_from)
                    .font(.caption2).foregroundStyle(Theme.t2)
                Button(L10n.t("cal.played", state.language)) {
                    announce(c)
                }.font(.caption).tint(Theme.brandA).disabled(busy)
                // Refused with a 409 until the notice has gone out. One door.
                Button(L10n.t("cal.listen", state.language)) {
                    listen(c)
                }.font(.caption).tint(Theme.brandA).disabled(busy)
                Button(L10n.t("cal.end", state.language)) {
                    endCall(c)
                }.font(.caption).tint(Theme.t2).disabled(busy)
            }
            ForEach(calls, id: \.id) { row in
                // A call that never announced never listened, and stays here:
                // it is the evidence that the ordering held.
                Text(row.route + " · " + row.spoken_in.joined(separator: " · ")
                     + " · " + L10n.t(row.listened ? "cal.told"
                                                   : "cal.nevertold",
                                      state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }

            Text(L10n.t("ns.ch.mic", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)

            if let mic, mic.attached == true {
                let line = (mic.device ?? "") + " · " + (mic.mic_type ?? "")
                Text(line)
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
        calls = (try? await ApiClient.shared.calls(uid: uid,
                                                   token: token)) ?? []
        mons = (try? await ApiClient.shared.monitors(uid: uid,
                                                     token: token)) ?? []
    }

    /// Switch a monitor on. Anything that senses other people carries the
    /// claim that they were told.
    private func plug(_ m: MonitorRow) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            mons = (try? await ApiClient.shared.plugMonitor(
                uid: uid, token: token, name: m.name,
                othersTold: m.catches_others)) ?? mons
        }
    }

    private func unplug(_ m: MonitorRow) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            mons = (try? await ApiClient.shared.unplugMonitor(
                uid: uid, token: token, name: m.name)) ?? mons
        }
    }

    /// Refused with a 403 until the row is switched on — the one door.
    private func sense(_ m: MonitorRow) {
        guard let uid = state.uid, let token = state.token else { return }
        error = nil
        Task {
            do {
                try await ApiClient.shared.monitorSensed(
                    uid: uid, token: token, name: m.name)
            } catch { self.error = error.localizedDescription }
        }
    }

    /// Set up the call. It is not listening: what comes back is the notice.
    private func openCall() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                call = try await ApiClient.shared.openCall(
                    uid: uid, token: token, route: callRoute,
                    number: callNumber.isEmpty ? nil : callNumber)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func announce(_ c: AssistedCall) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task {
            try? await ApiClient.shared.callAnnounced(uid: uid, callId: c.id,
                                                      token: token)
            busy = false
            await load()
        }
    }

    private func listen(_ c: AssistedCall) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                try await ApiClient.shared.callHeard(uid: uid, callId: c.id,
                                                     token: token)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func endCall(_ c: AssistedCall) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task {
            try? await ApiClient.shared.endCall(uid: uid, callId: c.id,
                                                token: token)
            call = nil
            busy = false
            await load()
        }
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
