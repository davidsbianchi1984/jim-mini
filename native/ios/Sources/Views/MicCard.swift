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
    @State private var channelSaid = ""
    @State private var channelHeard = ""
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
    // The day as it was taken in, and what survived of it.
    @State private var today: TheDay?
    @State private var fresh: FreshnessFacts?
    @State private var hearingStretch: String?
    @State private var hearingImport = false
    // What the rooms noticed, read on the way through rather than out of
    // anything kept.
    @State private var noticedCues: CuesSeen?
    // Two people on one call, each with their own channel 2.
    @State private var pairing: MicPaired?
    @State private var pairWith = ""
    // Two guardians working together, never on the line.
    @State private var links: [LiaisonRow] = []
    @State private var otherId = ""
    @State private var half: LiaisonHalf?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            // Everywhere the monitoring plugs in. The rows that sense other
            // people carry that on their face, and switching one on says the
            // people in that space have been told.
            Text(L10n.t("lia.head", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("lia.lead", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            TextField(L10n.t("lia.who.ph", state.language), text: $otherId)
                .textFieldStyle(.roundedBorder)
            Button(L10n.t("lia.open", state.language)) { openLink() }
                .font(.caption).tint(Theme.brandA)
                .disabled(otherId.isEmpty)
            ForEach(links, id: \.id) { l in
                VStack(alignment: .leading, spacing: 2) {
                    Text(l.about.isEmpty ? l.id : l.about)
                        .font(.caption).foregroundStyle(Theme.txt)
                    // The task is why it is still open — once both sides have
                    // said so. Naming it is the namer's own yes and nothing
                    // more, so the row says which of the three states this
                    // link is in rather than leaving it ambiguous.
                    if !l.task.isEmpty {
                        Text(l.task).font(.caption2)
                            .foregroundStyle(Theme.t2)
                        Text(l.holds_it_open
                                ? L10n.t("lia.holds", state.language)
                                : l.you_agreed
                                ? L10n.t("lia.waiting", state.language)
                                : L10n.t("lia.yours", state.language))
                            .font(.caption2).foregroundStyle(Theme.t2)
                    }
                    Text(l.running ? L10n.t("lia.running", state.language)
                                : L10n.t("lia.closed", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Button(L10n.t("lia.mine", state.language)) {
                        readHalf(l)
                    }.font(.caption).tint(Theme.brandA)
                    if l.running {
                        Button(L10n.t("lia.say", state.language)) {
                            sayAcross(l)
                        }.font(.caption).tint(Theme.brandA)
                        Button(L10n.t("lia.task", state.language)) {
                            nameWork(l)
                        }.font(.caption).tint(Theme.brandA)
                        // The other side's yes. Offered only where there is a
                        // task this person has not already agreed to —
                        // agreeing with yourself is not something the backend
                        // counts, so a button offering it would do nothing.
                        if !l.task.isEmpty && !l.you_agreed {
                            Button(L10n.t("lia.agree", state.language)) {
                                agreeWork(l)
                            }.font(.caption).tint(Theme.brandA)
                        }
                        Button(L10n.t("lia.stop", state.language)) {
                            stopLink(l)
                        }.font(.caption).tint(Theme.t2)
                    }
                    if half?.link_id == l.id, let h = half {
                        Text(L10n.t("lia.bymine", state.language))
                            .font(.caption2).foregroundStyle(Theme.txt)
                        ForEach(Array(h.said_by_mine.enumerated()),
                                id: \.offset) { _, line in
                            Text(line).font(.caption2)
                                .foregroundStyle(Theme.t2)
                        }
                        Text(L10n.t("lia.tomine", state.language))
                            .font(.caption2).foregroundStyle(Theme.txt)
                        ForEach(Array(h.said_to_mine.enumerated()),
                                id: \.offset) { _, line in
                            Text(line).font(.caption2)
                                .foregroundStyle(Theme.t2)
                        }
                    }
                }
            }

            // Two people on one call, each with their own channel 2. Shown
            // only where this person actually has one: pairing is a label on
            // a handover, so a control here on an idle channel would only
            // ever produce a refusal.
            if mic?.listening == true {
                Text(L10n.t("pair.head", state.language))
                    .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("pair.lead", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                if pairing?.paired == true {
                    Text(pairing?.theirs_listening == true
                         ? L10n.t("pair.both", state.language)
                         : L10n.t("pair.waiting", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Button(L10n.t("pair.end", state.language)) {
                        unpair()
                    }.font(.caption).tint(Theme.t2)
                } else {
                    TextField(L10n.t("lia.who.ph", state.language),
                              text: $pairWith)
                        .textFieldStyle(.roundedBorder)
                    Button(L10n.t("pair.go", state.language)) { pairMic() }
                        .font(.caption).tint(Theme.brandA)
                        .disabled(pairWith.isEmpty)
                }
            }

            // What the rooms noticed. Read as the content passes, before the
            // roster is asked whether any may survive — so this list is just
            // as full on a monitor that keeps nothing.
            if let seen = noticedCues {
                Text(L10n.t("cue.head", state.language))
                    .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("cue.lead", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                if seen.lately.isEmpty {
                    Text(L10n.t("cue.none", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                ForEach(Array(seen.lately.enumerated()), id: \.offset) { _, c in
                    VStack(alignment: .leading, spacing: 2) {
                        Text(c.says).font(.caption)
                            .foregroundStyle(Theme.txt)
                        Text("\(c.monitor) · \(c.severity)")
                            .font(.caption2).foregroundStyle(Theme.t2)
                        // Where the grading came from: what it flags it can
                        // explain.
                        Text(c.reference).font(.caption2)
                            .foregroundStyle(Theme.t2)
                    }
                }
            }

            // What those monitors actually took in, and what survived. The
            // drops are here too, each with the promise that dropped it: a
            // record listing only what it kept would be one with its own
            // omissions edited out.
            if let t = today {
                Text(L10n.t("day.head", state.language))
                    .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                if t.account.quiet {
                    Text(L10n.t("day.quiet", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                ForEach(t.account.monitors, id: \.monitor) { m in
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\(m.monitor) — \(m.sensed) "
                             + L10n.t("day.sensed", state.language)
                             + " · \(m.kept) "
                             + L10n.t("day.kept", state.language))
                            .font(.caption).foregroundStyle(Theme.txt)
                        // Which promise dropped what did not survive.
                        ForEach(m.because, id: \.self) { why in
                            Text(L10n.t("day.why.\(why)", state.language))
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }
                }
                // The short list, by construction.
                ForEach(t.survived, id: \.id) { k in
                    HStack {
                        Text(k.content).font(.caption2)
                            .foregroundStyle(Theme.t2)
                        Spacer()
                        Button(L10n.t("day.forget", state.language)) {
                            forget(k)
                        }.font(.caption).tint(Theme.brandA)
                    }
                }
                // A meeting, a call, a working stretch.
                Text(L10n.t("day.meet", state.language))
                    .font(.caption.bold()).foregroundStyle(Theme.txt)
                ForEach(t.stretches, id: \.id) { st in
                    HStack {
                        Text(st.about.isEmpty ? st.monitor : st.about)
                            .font(.caption2).foregroundStyle(Theme.txt)
                        if st.catches_others && st.others_told {
                            Text(L10n.t("day.meet.told", state.language))
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                        Spacer()
                        if st.running {
                            Button(L10n.t("day.meet.hear", state.language)) {
                                hearingStretch = st.id
                                hearingImport = true
                            }.font(.caption).tint(Theme.brandA)
                            Button(L10n.t("day.meet.end", state.language)) {
                                endStretch(st)
                            }.font(.caption).tint(Theme.t2)
                        }
                    }
                }
                // The staleness card — the two ages and the verdict, from
                // the same contract the console reads, beside the channel
                // that produces them.
                if let f = fresh {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(L10n.t("day.fresh.title", state.language))
                            .font(.caption.bold()).foregroundStyle(Theme.txt)
                        Text(f.verdict).font(.caption2)
                            .foregroundStyle(Theme.t2)
                        Text(L10n.t("day.fresh.reading", state.language)
                                .replacingOccurrences(of: "{age}",
                                                      with: age(f.reading_age_ms)))
                            .font(.caption2).foregroundStyle(Theme.t2)
                        Text(L10n.t("day.fresh.beat", state.language)
                                .replacingOccurrences(of: "{age}",
                                                      with: age(f.heartbeat_age_ms)))
                            .font(.caption2).foregroundStyle(Theme.t2)
                        Button(L10n.t("day.fresh.refresh", state.language)) {
                            Task { await beatAndRead() }
                        }.font(.caption).tint(Theme.brandA)
                    }
                }
            }

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
                    // The honest sentence beside the switch: this one can
                    // notice you fell; it cannot hear you call out.
                    Text(L10n.t("cue.canread", state.language) + ": "
                         + ((noticedCues?.can_read[m.name] ?? []).isEmpty
                            ? L10n.t("cue.canread.none", state.language)
                            : (noticedCues?.can_read[m.name] ?? [])
                                .joined(separator: " · ")))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    if m.on {
                        Button(L10n.t("mon.sense", state.language)) {
                            sense(m)
                        }.font(.caption).tint(Theme.brandA)
                        // Begin a meeting on this one. Where it catches other
                        // people the claim that they were told is made here
                        // rather than inherited from the switch above.
                        Button(L10n.t("day.meet.open", state.language)) {
                            startStretch(m)
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
                // Where what the worn microphone picked up reaches the
                // Guardian. The capture itself belongs on the device that
                // is wearing it — a watch app hands its own words in
                // through this same door; this field is the phone's way
                // to carry them for a wearable that relays through it,
                // and the microphone surface stays in TalkCard, where the
                // capability record says the one recorder lives.
                if mic?.listening == true {
                    TextField(L10n.t("ns.ch.mic.heard.say", state.language),
                              text: $channelSaid)
                        .padding(8).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 9))
                        .onSubmit { sendChannelTwo() }
                    if !channelHeard.isEmpty {
                        Text(channelHeard).font(.caption2)
                            .foregroundStyle(Theme.t2)
                    }
                }
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
        .fileImporter(isPresented: $hearingImport,
                      allowedContentTypes: [.audio, .data]) { result in
            if case .success(let url) = result { hearIntoStretch(url) }
        }
        .task {
            await load()
            await beatAndRead()
            types = try? await ApiClient.shared.micTypes()
            gains = try? await ApiClient.shared.micGains()
            if micType.isEmpty, let first = types?.personal.first {
                micType = first
            }
        }
    }

    /// One beat and one read: opening this screen is the shell holding
    /// the channel, which is exactly when the pulse should be sent.
    private func beatAndRead() async {
        guard let uid = state.uid, let token = state.token else { return }
        _ = try? await ApiClient.shared.heartbeat(uid: uid, token: token)
        fresh = try? await ApiClient.shared.freshness(uid: uid, token: token)
    }

    private func age(_ ms: Double?) -> String {
        guard let ms else { return "—" }
        let minutes = Int((ms / 60000).rounded())
        return minutes < 1 ? "<1 min" : "\(minutes) min"
    }

    private func hearIntoStretch(_ url: URL) {
        guard let uid = state.uid, let token = state.token,
              let sid = hearingStretch else { return }
        let scoped = url.startAccessingSecurityScopedResource()
        defer { if scoped { url.stopAccessingSecurityScopedResource() } }
        guard let data = try? Data(contentsOf: url) else { return }
        Task {
            try? await ApiClient.shared.stretchHeard(
                uid: uid, stretchId: sid, data: data, token: token)
            await load()
        }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        mic = try? await ApiClient.shared.micState(uid: uid, token: token)
        calls = (try? await ApiClient.shared.calls(uid: uid,
                                                   token: token)) ?? []
        mons = (try? await ApiClient.shared.monitors(uid: uid,
                                                     token: token)) ?? []
        today = try? await ApiClient.shared.theDay(uid: uid, token: token)
        noticedCues = try? await ApiClient.shared.cues(uid: uid, token: token)
        pairing = try? await ApiClient.shared.micPaired(uid: uid, token: token)
        links = (try? await ApiClient.shared.liaisons(uid: uid,
                                                      token: token)) ?? []
    }

    private func openLink() {
        guard let uid = state.uid, let token = state.token else { return }
        error = nil
        Task {
            do {
                _ = try await ApiClient.shared.openLiaison(
                    uid: uid, token: token, otherId: otherId)
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    /// Their own guardian's half, and only theirs.
    private func readHalf(_ l: LiaisonRow) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            half = try? await ApiClient.shared.liaisonHalf(
                uid: uid, token: token, linkId: l.id)
        }
    }

    private func sayAcross(_ l: LiaisonRow) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            try? await ApiClient.shared.liaisonSaid(
                uid: uid, token: token, linkId: l.id,
                body: L10n.t("lia.said.example", state.language))
            readHalf(l)
        }
    }

    /// The work that outlives the call.
    private func nameWork(_ l: LiaisonRow) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            _ = try? await ApiClient.shared.liaisonTask(
                uid: uid, token: token, linkId: l.id,
                task: L10n.t("lia.task.example", state.language))
            await load()
        }
    }

    /// The other side's yes, to the task as it stands.
    private func agreeWork(_ l: LiaisonRow) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            _ = try? await ApiClient.shared.liaisonAgreed(
                uid: uid, token: token, linkId: l.id)
            await load()
        }
    }

    private func stopLink(_ l: LiaisonRow) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            _ = try? await ApiClient.shared.closeLiaison(
                uid: uid, token: token, linkId: l.id, why: "stopped")
            await load()
        }
    }

    /// Say who else is on this call with their own channel 2.
    private func pairMic() {
        guard let uid = state.uid, let token = state.token else { return }
        error = nil
        Task {
            do {
                _ = try await ApiClient.shared.pairMic(
                    uid: uid, token: token, otherId: pairWith)
                pairWith = ""
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func unpair() {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            _ = try? await ApiClient.shared.unpairMic(uid: uid, token: token)
            await load()
        }
    }

    /// Begin a meeting on this monitor. Where it catches other people the
    /// claim that they were told is made here, not inherited from the switch.
    private func startStretch(_ m: MonitorRow) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            _ = try? await ApiClient.shared.openStretch(
                uid: uid, token: token, monitor: m.name,
                othersTold: m.catches_others)
            await load()
        }
    }

    private func endStretch(_ st: Stretch) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            _ = try? await ApiClient.shared.closeStretch(
                uid: uid, token: token, stretchId: st.id)
            await load()
        }
    }

    /// Drop what was kept of one moment; the fact that it happened stays.
    private func forget(_ k: Moment) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            _ = try? await ApiClient.shared.forgetMoment(
                uid: uid, token: token, momentId: k.id)
            await load()
        }
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

    /// Hand in what channel 2 picked up. Refused by the server unless the
    /// channel is attached and handed over, and unless this is the device
    /// it was lent to — see jim/mic.py.
    private func sendChannelTwo() {
        guard let uid = state.uid, let token = state.token else { return }
        let said = channelSaid.trimmingCharacters(in: .whitespaces)
        guard !said.isEmpty else { return }
        channelSaid = ""
        let device = mic?.device ?? ""
        busy = true
        Task {
            do {
                let out = try await ApiClient.shared.micHeard(
                    uid: uid, token: token, deviceName: device, words: said)
                channelHeard = out.heard ?? ""
                load()
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
