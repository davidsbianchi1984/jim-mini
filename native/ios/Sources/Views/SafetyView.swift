import SwiftUI

/// Safety: the Emergency button and flow, the escalation policy (with the
/// sensitivity dial), and the robot helpers — behind a segmented switcher.
struct SafetyView: View {
    enum Tab: String, CaseIterable {
        case sos = "SOS", medical = "Med ID", policy = "Policy",
             robots = "Robots", vault = "Vault"
    }
    @State private var tab: Tab = .sos

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Picker("", selection: $tab) {
                    ForEach(Tab.allCases, id: \.self) { Text($0.rawValue).tag($0) }
                }.pickerStyle(.segmented)

                switch tab {
                case .sos: SOSSection()
                case .medical: MedicalSection()
                case .policy: PolicySection()
                case .robots: RobotsSection()
                case .vault: CustodySection()
                }
            }.padding(20)
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
                Text("Medical ID").font(.headline).foregroundStyle(Theme.txt)
                Text("A shareable card for first responders: condition-level facts only, readable from a locked phone. Re-issuing rotates the QR and kills the old one.")
                    .font(.caption).foregroundStyle(Theme.t2)
                Button(action: issue) {
                    HStack { if busy { ProgressView().tint(.white) }
                             Text(issued == nil ? "Issue Medical ID" : "Rotate QR").bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 12)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }.disabled(busy)
            }.card()

            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

            if let issued {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Card issued").font(.headline).foregroundStyle(Theme.green)
                    Text("Print or lock-screen the QR at:")
                        .font(.caption).foregroundStyle(Theme.t2)
                    Text(issued.qr_svg_url)
                        .font(.system(.caption, design: .monospaced))
                        .foregroundStyle(Theme.t2)
                    if let c = card {
                        Divider().overlay(Theme.line)
                        Text("What a responder sees").font(.subheadline.bold())
                            .foregroundStyle(Theme.txt)
                        row("Name", c.name ?? "—")
                        row("Age", c.age.map(String.init) ?? "—")
                        row("Resting HR", c.resting_heart_rate.map { "\($0) bpm" } ?? "—")
                        row("Conditions",
                            (c.known_conditions?.isEmpty == false)
                                ? c.known_conditions!.joined(separator: ", ") : "none declared")
                        if let ec = c.emergency_contact {
                            row("Contact", "\(ec.name ?? "—") · \(ec.phone ?? "—")")
                        }
                    }
                    Button("Revoke card") { revoke() }
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
                    Text("SOS").font(.system(size: 34, weight: .heavy))
                    Text(busy ? "Coordinating…" : "Tap for emergency")
                        .font(.caption)
                }
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity).padding(.vertical, 28)
                .background(Theme.red)
                .clipShape(RoundedRectangle(cornerRadius: 20))
            }.disabled(busy)

            VStack(alignment: .leading, spacing: 10) {
                TextField("What's happening? (optional)", text: $situation)
                    .foregroundStyle(Theme.txt)
                TextField("Where are you? (optional)", text: $location)
                    .foregroundStyle(Theme.txt)
            }.card()

            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

            if !flow.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Coordinated response").font(.headline).foregroundStyle(Theme.txt)
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
                Text("Sensitivity").font(.headline).foregroundStyle(Theme.txt)
                Picker("", selection: $level) {
                    ForEach(levels, id: \.self) { Text($0.capitalized).tag($0) }
                }
                .pickerStyle(.segmented)
                .onChange(of: level) { _ in apply() }
                Text("Cautious escalates a rung earlier; assertive a rung later. Crisis language and critical events have floors no dial can lower.")
                    .font(.caption).foregroundStyle(Theme.t2)
            }.card()

            if let p = policy {
                VStack(alignment: .leading, spacing: 10) {
                    Text("How each severity resolves").font(.headline).foregroundStyle(Theme.txt)
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
                Text("Bind a robot").font(.headline).foregroundStyle(Theme.txt)
                Text("Bound robots respond to escalations: mobile bodies come to you; vacuums dock and clear the floor.")
                    .font(.caption).foregroundStyle(Theme.t2)
                Picker("", selection: $chosen) {
                    ForEach(catalog, id: \.model) {
                        Text("\($0.label) · \($0.maker)").tag($0.model)
                    }
                }.pickerStyle(.menu).tint(Theme.brandA)
                Button(action: bind) {
                    HStack { if busy { ProgressView().tint(.white) }; Text("Bind").bold() }
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
                            Text(rating == "perform" ? "CPR-rated" : "first-aid assist")
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
                        Text("On escalation: \(d.replacingOccurrences(of: "_", with: " "))")
                            .font(.caption).foregroundStyle(Theme.amber)
                    }
                    if let cmds = r.commands, cmds.contains("fetch_aed") {
                        HStack(spacing: 8) {
                            cmdButton("Fetch AED") { command(r, "fetch_aed", nil) }
                            cmdButton("Coach CPR") { command(r, "guide_first_aid", "cpr") }
                            cmdButton("Meet EMS") { command(r, "meet_responders", nil) }
                        }
                        if cmds.contains("perform_cpr") {
                            HStack(spacing: 8) {
                                if r.status == "performing_cpr" {
                                    cmdButton("Stop CPR", tint: Theme.red) {
                                        command(r, "stop_cpr", nil)
                                    }
                                } else if waiver?.signed == true {
                                    cmdButton("Start CPR (pre-authorized)", tint: Theme.red) {
                                        command(r, "perform_cpr", nil)
                                    }
                                    cmdButton("Auto-resuscitate", tint: Theme.red) {
                                        command(r, "auto_defib", nil)
                                    }
                                } else if confirmingCPR == r.id {
                                    cmdButton("Confirm: unresponsive, not breathing",
                                              tint: Theme.red) {
                                        confirmingCPR = nil
                                        command(r, "perform_cpr", "confirmed")
                                    }
                                    Button("Cancel") { confirmingCPR = nil }
                                        .font(.caption).foregroundStyle(Theme.t2)
                                } else {
                                    cmdButton("Perform CPR…", tint: Theme.red) {
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
                Text("Autonomous-resuscitation waiver")
                    .font(.headline).foregroundStyle(Theme.txt)
                Spacer()
                if waiver?.signed == true {
                    Text("SIGNED").font(.caption2.bold())
                        .padding(.horizontal, 7).padding(.vertical, 3)
                        .background(Theme.green.opacity(0.16))
                        .foregroundStyle(Theme.green).clipShape(Capsule())
                }
            }
            if let w = waiver, w.signed {
                Text("Signed by \(w.signature ?? "") — CPR-rated robots may start compressions automatically and operate a fully-automatic AED. A shock still only follows the AED's own rhythm analysis.")
                    .font(.caption).foregroundStyle(Theme.t2)
                Button("Revoke — restore confirm-gated operation") { revoke() }
                    .font(.caption.bold()).foregroundStyle(Theme.red)
            } else {
                Text("Unlock automatic operation: CPR that starts on detection, and a fully-automatic AED that shocks on its own analysis after the robot verifies everyone is clear. Until signed, every start needs an on-scene confirmation and no shock is ever delivered.")
                    .font(.caption).foregroundStyle(Theme.t2)
                ForEach((waiver?.terms ?? []).prefix(6), id: \.self) { t in
                    Text("• \(t)").font(.caption2).foregroundStyle(Theme.t3)
                }
                TextField("Type your legal name to sign", text: $signatureDraft)
                    .foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 11))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                cmdButton("Sign & submit waiver", tint: Theme.brandA) { sign() }
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
                if let spoken = res.spoken {
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
