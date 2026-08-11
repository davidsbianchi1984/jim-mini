import SwiftUI

/// The specialist economy: who stands behind each condition, the QRME
/// attach bracket, handing over a multi-step task, preparing a medical
/// referral (nothing releases without the QRME signing ceremony), and the
/// consented provider's view of you. Console doors (Attending, Care Team);
/// this is the phone's.
struct SpecialistsCard: View {
    @EnvironmentObject var state: AppState
    @State private var roster: [SpecialistRow] = []
    @State private var catalog: SpecialistCatalog?
    @State private var catalogRefused: String?
    @State private var condition = "anxiety"
    @State private var goal = ""
    @State private var started: SpecialistTaskStarted?
    @State private var tasks: [SpecialistTaskRow] = []
    @State private var opened: SpecialistTaskView?
    @State private var clinicians: ClinicianSearch?
    @State private var prepared: ReferralPrepared?
    @State private var requests: [ReferralRequestRow] = []
    @State private var provider: ProviderSummary?
    @State private var providerRefused: String?
    @State private var busy = false
    @State private var error: String?

    // The server's own condition vocabulary, as ConditionDeclare spells it.
    private let conditions = ["anxiety", "depression", "stress", "phobia",
                              "financial_stress", "relationship",
                              "physical_distress", "physical_injury"]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("att.spec", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            HStack(spacing: 8) {
                Button(L10n.t("att.spec.local", state.language)) { seed(false) }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy)
                Button(L10n.t("att.spec.hosted", state.language)) { seed(true) }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy)
            }
            if roster.isEmpty {
                Text(L10n.t("att.spec.none", state.language))
                    .font(.caption2).foregroundStyle(Theme.t3)
            }
            ForEach(roster, id: \.condition) { row in
                Text("\(row.condition) — \(row.label) · \(row.mode)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }

            Divider().background(Theme.line)
            Text(L10n.t("ct.spec", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            Text(L10n.t("ct.spec.choose", state.language))
                .font(.caption2).foregroundStyle(Theme.t3)
            if let catalogRefused {
                Text(catalogRefused).font(.caption2).foregroundStyle(Theme.t3)
            }
            if let starters = catalog?.starters {
                if starters.isEmpty {
                    Text(L10n.t("ct.spec.empty", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }
                ForEach(Array(starters.prefix(6).enumerated()),
                        id: \.offset) { _, starter in
                    HStack {
                        Text(starter.display_name ?? starter.profile_id ?? "")
                            .font(.caption2).foregroundStyle(Theme.txt)
                        Spacer()
                        Button(L10n.t("ct.spec.attach", state.language)) {
                            attach(starter)
                        }
                        .font(.caption2).foregroundStyle(Theme.brandA)
                        .disabled(busy || starter.profile_id == nil)
                    }
                }
            }

            Divider().background(Theme.line)
            Text(L10n.t("att.hand", state.language))
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
            TextField(L10n.t("att.hand.ph", state.language), text: $goal)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            HStack(spacing: 8) {
                Button(L10n.t("att.hand.go", state.language)) { hand() }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(busy || goal.isEmpty)
                Button(L10n.t("att.hand.who", state.language)) { who() }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy)
            }
            if let started {
                Text(started.started ? (started.id ?? "")
                                     : (started.reason ?? ""))
                    .font(.caption2)
                    .foregroundStyle(started.started ? Theme.green : Theme.amber)
            }
            if let clinicians {
                ForEach(Array(clinicians.clinicians.prefix(4).enumerated()),
                        id: \.offset) { _, clinician in
                    Text(clinician.label ?? clinician.display_name ?? "")
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                if let reason = clinicians.reason,
                   clinicians.clinicians.isEmpty {
                    Text(reason).font(.caption2).foregroundStyle(Theme.t3)
                }
            }
            ForEach(tasks, id: \.id) { task in
                HStack {
                    Text("\(task.goal) · \(task.status)")
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Spacer()
                    Button(L10n.t("att.open", state.language)) { open(task.id) }
                        .font(.caption2).foregroundStyle(Theme.brandA)
                        .disabled(busy)
                    Button(L10n.t("att.advance", state.language)) {
                        advance(task.id)
                    }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy)
                }
            }
            if let opened {
                let phase = opened.next_phase ?? ""
                let note = opened.note ?? ""
                Text("\(opened.status) · \(phase) \(note)")
                    .font(.caption2).foregroundStyle(Theme.t3)
            }

            Divider().background(Theme.line)
            Text(L10n.t("att.ref", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Button(L10n.t("att.ref.prep", state.language)
                    .replacingOccurrences(of: "{c}", with: condition)) {
                prepare()
            }
            .font(.caption2).foregroundStyle(Theme.brandA)
            .disabled(busy)
            if let prepared {
                Text(prepared.prepared ? (prepared.note ?? "")
                                       : (prepared.reason ?? ""))
                    .font(.caption2)
                    .foregroundStyle(prepared.prepared ? Theme.t2 : Theme.amber)
            }
            if requests.isEmpty {
                Text(L10n.t("att.ref.none", state.language))
                    .font(.caption2).foregroundStyle(Theme.t3)
            }
            ForEach(requests, id: \.id) { request in
                HStack {
                    Text(request.condition)
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Spacer()
                    Button(L10n.t("att.ref.released", state.language)) {
                        released(request.id)
                    }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy)
                }
            }

            Divider().background(Theme.line)
            Button(L10n.t("att.med.see", state.language)) { see() }
                .font(.caption2).foregroundStyle(Theme.brandA)
                .disabled(busy)
            if let provider {
                let name = provider.display_name ?? ""
                let conditions = provider.known_conditions.joined(separator: ", ")
                Text("\(name) · \(conditions) · \(provider.escalations)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            if let providerRefused {
                Text(providerRefused).font(.caption2).foregroundStyle(Theme.t3)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        roster = (try? await ApiClient.shared.specialists()) ?? []
        do { catalog = try await ApiClient.shared.specialistsCatalog() }
        catch { catalogRefused = error.localizedDescription }
        guard let uid = state.uid, let token = state.token else { return }
        tasks = (try? await ApiClient.shared.specialistTasks(uid: uid,
                                                             token: token)) ?? []
        requests = (try? await ApiClient.shared.referralRequests(
            uid: uid, token: token)) ?? []
    }

    private func run(_ work: @escaping () async throws -> Void) {
        busy = true; error = nil
        Task {
            do { try await work() }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func seed(_ tandem: Bool) {
        run {
            if tandem { _ = try await ApiClient.shared.seedTandemSpecialists() }
            else { _ = try await ApiClient.shared.seedSpecialists() }
            roster = (try? await ApiClient.shared.specialists()) ?? []
        }
    }

    private func attach(_ starter: CatalogStarter) {
        guard let pid = starter.profile_id else { return }
        run {
            _ = try await ApiClient.shared.attachSpecialist(
                condition: condition, qrmeProfileId: pid,
                label: starter.display_name ?? pid)
            roster = (try? await ApiClient.shared.specialists()) ?? []
        }
    }

    private func hand() {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            started = try await ApiClient.shared.startSpecialistTask(
                uid: uid, token: token, condition: condition,
                goal: goal.trimmingCharacters(in: .whitespaces))
            goal = ""
            tasks = (try? await ApiClient.shared.specialistTasks(
                uid: uid, token: token)) ?? []
        }
    }

    private func who() {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            clinicians = try await ApiClient.shared.referralClinicians(
                uid: uid, token: token, condition: condition)
        }
    }

    private func open(_ taskId: String) {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            opened = try await ApiClient.shared.specialistTask(
                uid: uid, token: token, taskId: taskId)
        }
    }

    private func advance(_ taskId: String) {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            opened = try await ApiClient.shared.advanceSpecialistTask(
                uid: uid, token: token, taskId: taskId)
            tasks = (try? await ApiClient.shared.specialistTasks(
                uid: uid, token: token)) ?? []
        }
    }

    private func prepare() {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            // The console's own placeholder clinician on a deployment with
            // no QRME directory; a real directory answers through `who()`.
            prepared = try await ApiClient.shared.prepareReferral(
                uid: uid, token: token, condition: condition,
                providerId: clinicians?.clinicians.first?.id ?? "prv_local")
            requests = (try? await ApiClient.shared.referralRequests(
                uid: uid, token: token)) ?? []
        }
    }

    private func released(_ requestId: String) {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            _ = try await ApiClient.shared.markReferralReleased(
                uid: uid, token: token, requestId: requestId)
        }
    }

    private func see() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil; providerRefused = nil
        Task {
            do {
                provider = try await ApiClient.shared.providerSummary(
                    uid: uid, token: token)
            } catch { providerRefused = error.localizedDescription }
            busy = false
        }
    }
}
