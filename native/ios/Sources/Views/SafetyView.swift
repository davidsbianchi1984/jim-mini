import SwiftUI

/// Safety: the Emergency button and flow, the escalation policy (with the
/// sensitivity dial), and the robot helpers — behind a segmented switcher.
struct SafetyView: View {
    enum Tab: String, CaseIterable {
        case alarms = "Alarms", sos = "SOS", crash = "Crash",
             medical = "Med ID", policy = "Policy", robots = "Robots",
             vault = "Vault"

        /// Android has rendered this strip from the table for rounds;
        /// these are its keys, not new ones. Only iOS was still
        /// showing the raw values, because they live in a `case`
        /// clause and nothing looks there.
        func label(_ lang: String) -> String {
            switch self {
            case .alarms: return L10n.t("alarm.lead.short", lang)
            case .sos: return L10n.t("sos", lang)
            case .crash: return L10n.t("cw.short", lang)
            case .medical: return L10n.t("mid.short", lang)
            case .policy: return L10n.t("cw.policy", lang)
            case .robots: return L10n.t("rob.short", lang)
            case .vault: return L10n.t("cust", lang)
            }
        }
    }
    // Alarms first, and the default. Somebody opening this screen has usually
    // been paged; the thing they were paged about should not be behind a tab
    // they have to find.
    // The strip reads its words from the table now, and the table
    // needs the language.
    @EnvironmentObject var state: AppState
    @State private var tab: Tab = .alarms

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Picker("", selection: $tab) {
                    ForEach(Tab.allCases, id: \.self) {
                        Text($0.label(state.language)).tag($0)
                    }
                }.pickerStyle(.segmented)

                switch tab {
                case .alarms: AlarmsSection()
                case .sos: SOSSection()
                case .crash: CrashWatchSection()
                case .medical: MedicalSection()
                case .policy: PolicySection()
                case .robots: RobotsSection()
                case .vault: CustodySection()
                }
            }.padding(20)
        }
    }
}

// MARK: Alarms — somebody scanned a care code, and somebody has to answer

/// The gap this section closes: JIM's phones could *raise* an emergency and
/// even command a bound robot to perform CPR, and could not answer the alarm
/// about it. There was no occurrence of the word "alarm" anywhere in this
/// shell.
///
/// That matters more here than the same gap would on a desktop. An alarm is
/// raised when a stranger scans the care code on somebody's door, and the
/// household relay pages a responder — a neighbour, an on-call carer. They
/// are paged on their phone. Accepting is the act that stops the escalation
/// ladder climbing to emergency services, so a responder who cannot accept
/// on the device they were paged on leaves only the path that ends in an
/// ambulance.
private struct AlarmsSection: View {
    @EnvironmentObject var state: AppState
    @State private var rows: [AlarmRow] = []
    @State private var responder = ""
    @State private var question = ""
    @State private var guidance: AlarmGuidance?
    @State private var said: String?
    @State private var busy = false
    @State private var error: String?

    private var open: [AlarmRow] { rows.filter { $0.state == "open" } }

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if open.isEmpty {
                Text(L10n.t("alarm.none", state.language))
                    .font(.subheadline).foregroundStyle(Theme.t2)
                Text(L10n.t("alarm.lead", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
            }

            ForEach(open) { a in
                VStack(alignment: .leading, spacing: 10) {
                    HStack {
                        Text(L10n.t("alarm.raised", state.language))
                            .font(.headline).foregroundStyle(Theme.red)
                        Spacer()
                        Text(a.tier ?? "").font(.caption2).foregroundStyle(Theme.t2)
                    }
                    ForEach(a.messages ?? [], id: \.self) { m in
                        Text("“\(m)”").font(.subheadline)
                    }

                    if let who = a.accepted_by {
                        // Accepted is not cleared. The server says so in its
                        // own response and this shell repeats it rather than
                        // greying the card out.
                        Text(L10n.t("alarm.attending", state.language)
                            .replacingOccurrences(of: "{who}", with: who))
                            .font(.caption).foregroundStyle(Theme.amber)
                    } else {
                        // A named responder, because the backend refuses an
                        // empty one: "someone accepted it" is the thing this
                        // relay exists to stop being enough.
                        TextField(L10n.t("res.name", state.language), text: $responder)
                            .textFieldStyle(.roundedBorder)
                        Button {
                            act { try await Api.shared.acceptAlarm(
                                uid: state.uid ?? "", alarmId: a.id,
                                responder: responder, token: state.token ?? "") }
                        } label: {
                            Text(L10n.t("alarm.going", state.language)).frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent).tint(Theme.brandA)
                        .disabled(busy || responder.trimmingCharacters(
                            in: .whitespaces).isEmpty)
                    }

                    HStack {
                        Button(L10n.t("alarm.cannot_go", state.language)) {
                            act { try await Api.shared.escalateAlarm(
                                uid: state.uid ?? "", alarmId: a.id,
                                token: state.token ?? "") }
                        }.tint(Theme.red).disabled(busy)
                        Spacer()
                        Button(L10n.t("alarm.clear", state.language)) {
                            act { try await Api.shared.clearAlarm(
                                uid: state.uid ?? "", alarmId: a.id,
                                token: state.token ?? "") }
                        }.disabled(busy)
                    }.font(.caption)

                    HStack {
                        TextField(L10n.t("sos.whatdo", state.language), text: $question)
                            .textFieldStyle(.roundedBorder)
                        Button(L10n.t("sos.ask", state.language)) {
                            Task {
                                busy = true; error = nil
                                do {
                                    guidance = try await Api.shared.alarmGuidance(
                                        alarmId: a.id, question: question,
                                        token: state.token ?? "")
                                } catch { self.error = error.localizedDescription }
                                busy = false
                            }
                        }.disabled(busy || question.trimmingCharacters(
                            in: .whitespaces).isEmpty)
                    }
                }
                .padding(14)
                .background(Theme.card).clipShape(RoundedRectangle(cornerRadius: 12))
            }

            if let g = guidance {
                VStack(alignment: .leading, spacing: 6) {
                    Text(g.answer).font(.subheadline)
                    if let n = g.note {
                        Text(n).font(.caption2).foregroundStyle(Theme.t2)
                    }
                }
                .padding(14)
                .background(Theme.card).clipShape(RoundedRectangle(cornerRadius: 12))
            }

            if let s = said {
                Text(s).font(.caption).foregroundStyle(Theme.t2)
            }
            if let e = error {
                Text(e).font(.caption).foregroundStyle(Theme.red)
            }

            Text(L10n.t("alarm.not_emergency", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        do { rows = try await Api.shared.alarms(uid: uid, token: token) }
        catch { self.error = error.localizedDescription }
    }

    private func act(_ work: @escaping () async throws -> AlarmAck) {
        Task {
            busy = true; error = nil; said = nil
            do {
                let out = try await work()
                said = out.note
                await load()
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}

// MARK: Crash watch — armed in advance; unanswered questions send help

private struct CrashWatchSection: View {
    @EnvironmentObject var state: AppState
    @State private var st: CrashWatchStatus?
    @State private var name = ""
    @State private var channel = ""
    @State private var attempts = 3
    @State private var window = 5.0
    @State private var ems = false
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if st?.asking == true {
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("alarm.asking", state.language))
                        .font(.headline).foregroundStyle(Theme.amber)
                    Text(L10n.t("alarm.concern", state.language)
                        .replacingOccurrences(of: "{concern}", with: st?.concern ?? "")
                        .replacingOccurrences(of: "{n}", with: "\(st?.attempt ?? 1)")
                        .replacingOccurrences(of: "{total}", with: "\(st?.attempts ?? 3)"))
                        .font(.caption).foregroundStyle(Theme.t2)
                    Button(action: respond) {
                        Text(L10n.t("alarm.im_okay", state.language)).bold()
                            .frame(maxWidth: .infinity).padding(.vertical, 12)
                            .background(Theme.green).foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                }.card()
            }
            if st?.tripped == true {
                Text(L10n.t("alarm.tripped", state.language)
                    .replacingOccurrences(of: "{name}", with: st?.trusted_name ?? ""))
                    .font(.footnote).foregroundStyle(Theme.red)
            }
            VStack(alignment: .leading, spacing: 10) {
                Text(L10n.t("cw", state.language)).font(.headline).foregroundStyle(Theme.txt)
                Text(L10n.t("cw.sub", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
                TextField(L10n.t("cw.trusted", state.language), text: $name)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("cw.reach", state.language), text: $channel)
                    .textFieldStyle(.roundedBorder)
                Stepper("Attempts: \(attempts)", value: $attempts, in: 1...10)
                    .foregroundStyle(Theme.txt)
                Stepper("Minutes per attempt: \(Int(window))", value: $window,
                        in: 1...60, step: 1)
                    .foregroundStyle(Theme.txt)
                Toggle(L10n.t("alarm.ems", state.language), isOn: $ems)
                    .font(.caption).foregroundStyle(Theme.t2)
                HStack {
                    Button(action: arm) {
                        HStack { if busy { ProgressView().tint(.white) }
                                 Text(st?.armed == true ? L10n.t("action.update", state.language)
                                                : L10n.t("cw.arm", state.language)).bold() }
                            .frame(maxWidth: .infinity).padding(.vertical, 12)
                            .background(Theme.brand).foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }.disabled(busy)
                    if st?.armed == true {
                        Button(L10n.t("cw.disarm", state.language)) { disarm() }
                            .font(.caption.bold()).foregroundStyle(Theme.red)
                    }
                }
                if st?.armed == true && st?.asking != true && st?.tripped != true {
                    Text(L10n.t("alarm.armed", state.language)
                        .replacingOccurrences(of: "{name}", with: st?.trusted_name ?? "")
                        .replacingOccurrences(of: "{n}", with: "\(st?.attempts ?? 3)"))
                        .font(.caption).foregroundStyle(Theme.green)
                }
            }.card()
            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
        }
        .onAppear(perform: refresh)
    }

    private func took(_ r: CrashWatchStatus) {
        st = r
        if let n = r.trusted_name, !n.isEmpty { name = n }
        if let a = r.attempts { attempts = a }
        if let w = r.window_minutes { window = w }
        ems = r.contact_emergency_services ?? false
    }

    private func refresh() {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            if let r = try? await ApiClient.shared.crashWatch(uid: uid, token: token) {
                took(r)
            }
        }
    }

    private func arm() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                took(try await ApiClient.shared.armCrashWatch(
                    uid: uid, token: token, name: name, channel: channel,
                    attempts: attempts, windowMinutes: window, ems: ems))
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func disarm() {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            if let r = try? await ApiClient.shared.disarmCrashWatch(uid: uid, token: token) {
                took(r)
            }
        }
    }

    private func respond() {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            if let r = try? await ApiClient.shared.imOkay(uid: uid, token: token) {
                took(r)
            }
        }
    }
}

// MARK: Medical ID — the first-responder card + QR

private struct MedicalSection: View {
    @EnvironmentObject var state: AppState
    @State private var issued: MedicalCardIssued?
    @State private var card: MedicalCard?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 8) {
                Text(L10n.t("mid", state.language)).font(.headline).foregroundStyle(Theme.txt)
                Text(L10n.t("mid.sub", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
                Button(action: issue) {
                    HStack { if busy { ProgressView().tint(.white) }
                             Text(L10n.t(issued == nil ? "mid.issue" : "mid.rotate", state.language)).bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 12)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }.disabled(busy)
            }.card()

            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

            if let issued {
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("mid.issued", state.language)).font(.headline).foregroundStyle(Theme.green)
                    Text(L10n.t("mid.print", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    Text(issued.qr_svg_url)
                        .font(.system(.caption, design: .monospaced))
                        .foregroundStyle(Theme.t2)
                    if let c = card {
                        Divider().overlay(Theme.line)
                        Text(L10n.t("mid.responder", state.language)).font(.subheadline.bold())
                            .foregroundStyle(Theme.txt)
                        row(L10n.t("med.name", state.language), c.name ?? "—")
                        row(L10n.t("med.age", state.language), c.age.map(String.init) ?? "—")
                        row(L10n.t("med.hr", state.language), c.resting_heart_rate.map { "\($0) bpm" } ?? "—")
                        row(L10n.t("med.conditions", state.language),
                            (c.known_conditions?.isEmpty == false)
                                ? c.known_conditions!.joined(separator: ", ") : "none declared")
                        if let ec = c.emergency_contact {
                            row(L10n.t("med.contact", state.language), "\(ec.name ?? "—") · \(ec.phone ?? "—")")
                        }
                    }
                    Button(L10n.t("mid.revoke", state.language)) { revoke() }
                        .font(.caption.bold()).foregroundStyle(Theme.red)
                }.card()
            }
        }
    }

    private func row(_ k: String, _ v: String) -> some View {
        HStack(alignment: .top) {
            Text(k).font(.caption).foregroundStyle(Theme.t2).frame(width: 84, alignment: .leading)
            Text(v).font(.caption).foregroundStyle(Theme.txt)
        }
    }

    private func issue() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                let r = try await ApiClient.shared.issueMedicalCard(uid: uid, token: token)
                issued = r
                card = try? await ApiClient.shared.medicalCard(cardToken: r.token)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func revoke() {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            try? await ApiClient.shared.revokeMedicalCard(uid: uid, token: token)
            issued = nil; card = nil
        }
    }
}

// MARK: SOS — the Emergency button + coordinated flow

private struct SOSSection: View {
    @EnvironmentObject var state: AppState
    @State private var situation = ""
    @State private var location = ""
    @State private var flow: [FlowStep] = []
    @State private var directives: [RobotDirective] = []
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Button(action: trigger) {
                VStack(spacing: 4) {
                    Text(L10n.t("sos", state.language)).font(.system(size: 34, weight: .heavy))
                    Text(busy ? L10n.t("sos.coordinating", state.language) : L10n.t("sos.tap", state.language))
                        .font(.caption)
                }
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity).padding(.vertical, 28)
                .background(Theme.red)
                .clipShape(RoundedRectangle(cornerRadius: 20))
            }.disabled(busy)

            VStack(alignment: .leading, spacing: 10) {
                TextField(L10n.t("sos.what", state.language), text: $situation)
                    .foregroundStyle(Theme.txt)
                TextField(L10n.t("sos.where", state.language), text: $location)
                    .foregroundStyle(Theme.txt)
            }.card()

            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

            if !flow.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("rob.coordinated", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    ForEach(Array(flow.enumerated()), id: \.offset) { i, step in
                        HStack(alignment: .top, spacing: 10) {
                            Text("\(i + 1)").font(.caption.bold())
                                .frame(width: 20, height: 20)
                                .background(Theme.red.opacity(0.2))
                                .foregroundStyle(Theme.red)
                                .clipShape(Circle())
                            VStack(alignment: .leading, spacing: 2) {
                                Text(step.label).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                                Text(step.detail).font(.caption).foregroundStyle(Theme.t2)
                            }
                        }
                    }
                    ForEach(directives, id: \.robot) { d in
                        Text("🤖 \(d.robot): \(d.directive.replacingOccurrences(of: "_", with: " "))")
                            .font(.caption).foregroundStyle(Theme.amber)
                    }
                }.card()
            }
        }
    }

    private func trigger() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                let r = try await ApiClient.shared.emergency(
                    uid: uid, token: token, situation: situation, location: location)
                flow = r.flow
                directives = r.robot_directives ?? []
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}

// MARK: Policy — the escalation ladder under the sensitivity dial

private struct PolicySection: View {
    @EnvironmentObject var state: AppState
    @State private var policy: EscalationPolicy?
    @State private var level = "balanced"

    private let levels = ["cautious", "balanced", "assertive"]

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 10) {
                Text(L10n.t("cw.sensitivity", state.language)).font(.headline).foregroundStyle(Theme.txt)
                Picker("", selection: $level) {
                    // `capitalized` on the API's own enum member is not a
                    // label — it reads as English on every shell. Windows has
                    // asked the table for these three since its dial was
                    // localized; this shell had never been given the rows.
                    ForEach(levels, id: \.self) {
                        Text(sensitivityLabel($0, state.language)).tag($0)
                    }
                }
                .pickerStyle(.segmented)
                .onChange(of: level) { _ in apply() }
                Text(L10n.t("cw.sensitivity.sub", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
            }.card()

            if let p = policy {
                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("rob.severity", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    ForEach(["info", "guidance", "critical"], id: \.self) { sev in
                        HStack {
                            Text(sev.capitalized).font(.subheadline).foregroundStyle(Theme.txt)
                            Spacer()
                            Text(p.by_severity[sev]?.replacingOccurrences(of: "_", with: " ") ?? "—")
                                .font(.subheadline.bold())
                                .foregroundStyle(sev == "critical" ? Theme.red : Theme.brandA)
                        }
                    }
                }.card()
            }
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        policy = try? await ApiClient.shared.escalationPolicy(uid: uid, token: token)
        if let p = policy { level = p.sensitivity }
    }

    private func apply() {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            try? await ApiClient.shared.setSensitivity(uid: uid, token: token, level: level)
            await load()
        }
    }
}

// MARK: Robots — guardian responders

private struct RobotsSection: View {
    @EnvironmentObject var state: AppState
    @State private var catalog: [RobotSpec] = []
    @State private var chosen = "neo"
    @State private var robots: [Robot] = []
    @State private var busy = false
    @State private var error: String?
    @State private var cmdResult: String?
    @State private var confirmingCPR: String?    // robot id awaiting confirm
    @State private var waiver: WaiverState?
    @State private var signatureDraft = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 10) {
                Text(L10n.t("rob.bind", state.language)).font(.headline).foregroundStyle(Theme.txt)
                Text(L10n.t("rob.sub", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
                Picker("", selection: $chosen) {
                    ForEach(catalog, id: \.model) {
                        Text("\($0.label) · \($0.maker)").tag($0.model)
                    }
                }.pickerStyle(.menu).tint(Theme.brandA)
                Button(action: bind) {
                    HStack { if busy { ProgressView().tint(.white) }; Text(L10n.t("rob.bind.go", state.language)).bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 12)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }.disabled(busy || catalog.isEmpty)
            }.card()

            waiverCard()

            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
            if let cmdResult {
                Text(cmdResult).font(.caption).foregroundStyle(Theme.green)
            }

            ForEach(robots, id: \.id) { r in
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        Text(r.name).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                        if let rating = r.first_aid {
                            Text(rating == "perform" ? L10n.t("rob.cpr_rated", state.language)
                                             : L10n.t("sos.firstaid", state.language))
                                .font(.caption2.bold())
                                .padding(.horizontal, 6).padding(.vertical, 2)
                                .background(Theme.green.opacity(0.16))
                                .foregroundStyle(Theme.green).clipShape(Capsule())
                        }
                        Spacer()
                        Text((r.status ?? "docked").replacingOccurrences(of: "_", with: " ")
                             .capitalized)
                            .font(.caption).foregroundStyle(Theme.t2)
                    }
                    if let d = r.escalation_directive {
                        Text(L10n.fill("rob.onesc", state.language,
                              ["directive": d.replacingOccurrences(of: "_", with: " ")]))
                            .font(.caption).foregroundStyle(Theme.amber)
                    }
                    if let cmds = r.commands, cmds.contains("fetch_aed") {
                        HStack(spacing: 8) {
                            cmdButton(L10n.t("fa.aed", state.language)) { command(r, "fetch_aed", nil) }
                            cmdButton(L10n.t("fa.coach", state.language)) { command(r, "guide_first_aid", "cpr") }
                            cmdButton(L10n.t("fa.ems", state.language)) { command(r, "meet_responders", nil) }
                        }
                        if cmds.contains("perform_cpr") {
                            HStack(spacing: 8) {
                                if r.status == "performing_cpr" {
                                    cmdButton(L10n.t("fa.stop", state.language), tint: Theme.red) {
                                        command(r, "stop_cpr", nil)
                                    }
                                } else if waiver?.signed == true {
                                    cmdButton(L10n.t("fa.start", state.language), tint: Theme.red) {
                                        command(r, "perform_cpr", nil)
                                    }
                                    cmdButton(L10n.t("res.auto", state.language), tint: Theme.red) {
                                        command(r, "auto_defib", nil)
                                    }
                                } else if confirmingCPR == r.id {
                                    cmdButton(L10n.t("fa.confirm", state.language),
                                              tint: Theme.red) {
                                        confirmingCPR = nil
                                        command(r, "perform_cpr", "confirmed")
                                    }
                                    Button(L10n.t("action.cancel", state.language)) { confirmingCPR = nil }
                                        .font(.caption).foregroundStyle(Theme.t2)
                                } else {
                                    cmdButton(L10n.t("fa.perform", state.language), tint: Theme.red) {
                                        confirmingCPR = r.id
                                        cmdResult = "Confirm the person is unresponsive and not breathing normally. The robot never starts on its own judgement — and never delivers a shock; the AED analyzes, a human presses. (Sign the waiver above to pre-authorize automatic operation.)"
                                    }
                                }
                            }
                        }
                    }
                }.card()
            }
        }
        .task { await load() }
    }

    @ViewBuilder
    private func waiverCard() -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(L10n.t("res.waiver", state.language))
                    .font(.headline).foregroundStyle(Theme.txt)
                Spacer()
                if waiver?.signed == true {
                    Text(L10n.t("res.signed", state.language)).font(.caption2.bold())
                        .padding(.horizontal, 7).padding(.vertical, 3)
                        .background(Theme.green.opacity(0.16))
                        .foregroundStyle(Theme.green).clipShape(Capsule())
                }
            }
            if let w = waiver, w.signed {
                Text(L10n.fill("res.signed.by", state.language, ["name": w.signature ?? ""]))
                    .font(.caption).foregroundStyle(Theme.t2)
                Button(L10n.t("res.revoke", state.language)) { revoke() }
                    .font(.caption.bold()).foregroundStyle(Theme.red)
            } else {
                Text(L10n.t("res.waiver.sub", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
                ForEach((waiver?.terms ?? []).prefix(6), id: \.self) { t in
                    Text("• \(t)").font(.caption2).foregroundStyle(Theme.t3)
                }
                TextField(L10n.t("res.sign.ph", state.language), text: $signatureDraft)
                    .foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 11))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                cmdButton(L10n.t("res.sign", state.language), tint: Theme.brandA) { sign() }
            }
        }.card()
    }

    private func sign() {
        guard let uid = state.uid, let token = state.token,
              !signatureDraft.isEmpty else { return }
        error = nil
        Task {
            do {
                waiver = try await ApiClient.shared.signWaiver(
                    uid: uid, token: token, signature: signatureDraft)
                signatureDraft = ""
                cmdResult = "Waiver signed — automatic resuscitation pre-authorized."
            } catch { self.error = error.localizedDescription }
        }
    }

    private func revoke() {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            try? await ApiClient.shared.revokeWaiver(uid: uid, token: token)
            waiver = try? await ApiClient.shared.waiver(uid: uid, token: token)
            cmdResult = "Waiver revoked — confirm-gated operation restored."
        }
    }

    private func cmdButton(_ label: String, tint: Color = Theme.brandA,
                           _ action: @escaping () -> Void) -> some View {
        Button(label, action: action)
            .font(.caption.bold()).foregroundStyle(.white)
            .padding(.horizontal, 10).padding(.vertical, 7)
            .background(tint).clipShape(Capsule())
    }

    private func command(_ r: Robot, _ command: String, _ arg: String?) {
        guard let uid = state.uid, let token = state.token else { return }
        error = nil
        Task {
            do {
                let res = try await ApiClient.shared.commandRobot(
                    uid: uid, token: token, robotId: r.id,
                    command: command, arg: arg)
                var line = res.note ?? res.instruction ?? res.status
                if let pace = res.pace {
                    line += " · \(pace.compressions_per_minute)/min"
                }
                if let spoken = res.spoken_steps {
                    line = "🔊 " + spoken.joined(separator: " → ")
                }
                if let seq = res.sequence {
                    line = seq.joined(separator: " → ")
                }
                cmdResult = line
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        catalog = (try? await ApiClient.shared.roboticsCatalog())?.robots ?? []
        robots = (try? await ApiClient.shared.robots(uid: uid, token: token)) ?? []
        waiver = try? await ApiClient.shared.waiver(uid: uid, token: token)
    }

    private func bind() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do { _ = try await ApiClient.shared.bindRobot(uid: uid, token: token, model: chosen) }
            catch { self.error = error.localizedDescription }
            await load(); busy = false
        }
    }
}
