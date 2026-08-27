import SwiftUI

/// The medicine cabinet: today's board, dose logging, adherence, and adding
/// a medication in the user's own words. Console door since 0.9.0; this is
/// the phone's. JIM is not a pharmacist — the board's own disclaimer says
/// so, and the phone shows it rather than paraphrasing it.
struct MedsCard: View {
    @EnvironmentObject var state: AppState
    @State private var board: MedsBoard?
    @State private var adherence: MedAdherence?
    @State private var showAdherence = false
    @State private var showAdd = false
    @State private var name = ""
    @State private var dose = ""
    @State private var purpose = ""
    @State private var times = ""
    @State private var asNeeded = false
    @State private var ceiling = ""
    @State private var critical = false
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.med.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)

            if let board {
                if !board.missed_critical.isEmpty {
                    Text(L10n.t("ns.med.missed", state.language)
                            .replacingOccurrences(of: "{list}", with:
                                board.missed_critical.map {
                                    "\($0.name) (\($0.slot))"
                                }.joined(separator: ", ")))
                        .font(.caption2).foregroundStyle(Theme.amber)
                }
                Text(L10n.t("ns.med.today", state.language))
                    .font(.caption.bold()).foregroundStyle(Theme.t2)
                if board.medications.isEmpty {
                    Text(L10n.t("ns.med.none", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }
                ForEach(board.medications, id: \.id) { med in
                    medRow(med)
                }
                // The board's own honesty line, verbatim from the wire.
                Text(board.disclaimer)
                    .font(.caption2).foregroundStyle(Theme.t3)
            }

            HStack {
                Button(L10n.t("ns.med.last", state.language)
                        .replacingOccurrences(of: "{n}", with: "7")) {
                    showAdherence.toggle()
                    if showAdherence { Task { await loadAdherence() } }
                }
                .font(.caption2).foregroundStyle(Theme.brandA)
                Button(L10n.t("ns.med.add", state.language)) {
                    showAdd.toggle()
                }
                .font(.caption2).foregroundStyle(Theme.brandA)
            }

            if showAdherence, let adherence {
                ForEach(adherence.adherence_rows, id: \.id) { row in
                    HStack {
                        Text(row.name).font(.caption2)
                            .foregroundStyle(Theme.txt)
                        Spacer()
                        Text(L10n.t("ns.med.of", state.language)
                                .replacingOccurrences(of: "{taken}",
                                                      with: String(row.taken))
                                .replacingOccurrences(of: "{expected}",
                                                      with: String(row.expected)))
                            .font(.caption2).foregroundStyle(Theme.t2)
                    }
                }
            }

            if showAdd { addForm }

            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    @ViewBuilder
    private func medRow(_ med: MedRow) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text("\(med.name) · \(med.dose)")
                    .font(.caption.bold()).foregroundStyle(Theme.txt)
                // The console's "worth a check-in" checkbox, as a toggle.
                Button(L10n.t("ns.med.critical", state.language)) {
                    run { try await ApiClient.shared.setMedCritical(
                        uid: state.uid!, token: state.token!,
                        medId: med.id, critical: !med.critical) }
                }
                .font(.caption2)
                .foregroundStyle(med.critical ? Theme.amber : Theme.t3)
                .lineLimit(1)
                Spacer()
                Button(L10n.t("ns.med.stop", state.language)) {
                    run { try await ApiClient.shared.stopMed(
                        uid: state.uid!, token: state.token!, medId: med.id) }
                }
                .font(.caption2).foregroundStyle(Theme.red)
            }
            if let purpose = med.purpose, !purpose.isEmpty {
                Text(purpose).font(.caption2).foregroundStyle(Theme.t2)
            }
            if med.kind == "as_needed" {
                HStack {
                    Text(L10n.t("ns.med.asneeded.line", state.language)
                            .replacingOccurrences(of: "{n}",
                                with: String(med.taken_today ?? 0))
                            .replacingOccurrences(of: "{max}",
                                with: med.max_per_day.map {
                                    L10n.t("ns.med.asneeded.max", state.language)
                                        .replacingOccurrences(of: "{max}",
                                                              with: String($0))
                                } ?? ""))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Button(L10n.t("ns.med.tookone", state.language)) {
                        logDose(med.id, action: "taken", slot: nil)
                    }
                    .font(.caption2.bold()).foregroundStyle(Theme.green)
                }
            } else if let slots = med.slots {
                ForEach(slots, id: \.slot) { slot in
                    HStack(spacing: 8) {
                        Text("\(slot.slot) · \(slot.status)")
                            .font(.caption2)
                            .foregroundStyle(slot.status == "missed"
                                             ? Theme.amber : Theme.t2)
                        if slot.status == "due" || slot.status == "missed" {
                            Button(L10n.t("ns.med.take", state.language)) {
                                logDose(med.id, action: "taken", slot: slot.slot)
                            }
                            .font(.caption2.bold()).foregroundStyle(Theme.green)
                            Button(L10n.t("ns.med.skip", state.language)) {
                                logDose(med.id, action: "skipped", slot: slot.slot)
                            }
                            .font(.caption2).foregroundStyle(Theme.t3)
                        }
                    }
                }
            }
        }
    }

    private var addForm: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("ns.med.add.pitch", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            Text(L10n.t("ns.med.name", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField(L10n.t("ns.med.name.ph", state.language), text: $name)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Text(L10n.t("ns.med.dose", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField(L10n.t("ns.med.dose.ph", state.language), text: $dose)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Text(L10n.t("ns.med.purpose", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField(L10n.t("ns.med.purpose.ph", state.language),
                      text: $purpose)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Toggle(isOn: $asNeeded) {
                Text(L10n.t("ns.med.asneeded", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            if asNeeded {
                Text(L10n.t("ns.med.ceiling", state.language) + " "
                     + L10n.t("ns.med.ceiling.note", state.language))
                    .font(.caption2.bold()).foregroundStyle(Theme.t2)
                TextField("3", text: $ceiling)
                    .keyboardType(.numberPad)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
            } else {
                Text(L10n.t("ns.med.times", state.language)
                     + L10n.t("ns.med.times.note", state.language))
                    .font(.caption2.bold()).foregroundStyle(Theme.t2)
                TextField("08:00, 20:00", text: $times)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
            }
            Toggle(isOn: $critical) {
                Text(L10n.t("ns.med.critical", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            Button(L10n.t("ns.med.add", state.language)) { add() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy || name.isEmpty || dose.isEmpty
                          || (asNeeded ? false : times.isEmpty))
        }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        board = try? await ApiClient.shared.medsBoard(uid: uid, token: token)
    }

    private func loadAdherence() async {
        guard let uid = state.uid, let token = state.token else { return }
        adherence = try? await ApiClient.shared.medAdherence(uid: uid,
                                                             token: token)
    }

    private func run(_ work: @escaping () async throws -> MedRow) {
        busy = true; error = nil
        Task {
            do { _ = try await work() }
            catch { self.error = error.localizedDescription }
            busy = false
            await load()
        }
    }

    private func logDose(_ medId: String, action: String, slot: String?) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                // The log answers with the refreshed board — one round trip.
                board = try await ApiClient.shared.logDose(
                    uid: uid, token: token, medId: medId,
                    action: action, slot: slot)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func add() {
        guard let uid = state.uid, let token = state.token else { return }
        var schedule: [String: Any]
        if asNeeded {
            schedule = ["as_needed": true]
            if let max = Int(ceiling.trimmingCharacters(in: .whitespaces)),
               max > 0 { schedule["max_per_day"] = max }
        } else {
            schedule = ["times": times.split(separator: ",")
                .map { $0.trimmingCharacters(in: .whitespaces) }
                .filter { !$0.isEmpty }]
        }
        busy = true; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.addMed(
                    uid: uid, token: token,
                    name: name.trimmingCharacters(in: .whitespaces),
                    dose: dose.trimmingCharacters(in: .whitespaces),
                    schedule: schedule,
                    purpose: purpose.trimmingCharacters(in: .whitespaces),
                    critical: critical)
                name = ""; dose = ""; purpose = ""; times = ""
                ceiling = ""; asNeeded = false; critical = false
                showAdd = false
            } catch { self.error = error.localizedDescription }
            busy = false
            await load()
        }
    }
}
