import SwiftUI

/// Vault custody: every tandem specialist exchange the Guardian sealed into
/// the PDI vault, with the audit-chain status. Tapping a record opens its
/// PDI provenance — origin, seal, audit trail — the proof behind the lock.
struct CustodySection: View {
    @EnvironmentObject var state: AppState
    @State private var list: CustodyList?
    @State private var provenance: [String: CustodyProvenance] = [:]
    @State private var openKey: String?
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 8) {
                Text(L10n.t("cust", state.language)).font(.headline).foregroundStyle(Theme.txt)
                ProblemReportingCard()
                OfflinePostureCard()
                Text(L10n.t("cust.sub", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
                if let list {
                    HStack(spacing: 8) {
                        Text(L10n.t(list.chain_intact == true ? "cust.chain.ok"
                                        : "cust.chain.unknown", state.language))
                            .font(.caption.bold())
                            .foregroundStyle(list.chain_intact == true
                                             ? Theme.green : Theme.amber)
                        Spacer()
                        Text(L10n.fill("cust.sealed", state.language, ["n": "\(list.count)"]))
                            .font(.caption).foregroundStyle(Theme.t2)
                    }
                }
            }.card()

            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

            if let list {
                if list.records.isEmpty {
                    Text(L10n.t("cust.none", state.language))
                        .font(.footnote).foregroundStyle(Theme.t2).card()
                }
                ForEach(list.records, id: \.self) { key in
                    VStack(alignment: .leading, spacing: 6) {
                        Button(action: { toggle(key) }) {
                            HStack(spacing: 8) {
                                Text("🔒").font(.caption)
                                Text(key).font(.caption).foregroundStyle(Theme.txt)
                                    .lineLimit(1).truncationMode(.middle)
                                Spacer()
                                Image(systemName: openKey == key
                                      ? "chevron.up" : "chevron.down")
                                    .font(.caption2).foregroundStyle(Theme.t3)
                            }
                        }
                        if openKey == key, let p = provenance[key] {
                            Divider().overlay(Theme.line)
                            Text(L10n.fill("cust.origin", state.language, ["origin": p.origin]))
                                .font(.caption).foregroundStyle(Theme.txt)
                            if let cipher = p.sealed?.cipher {
                                Text(L10n.fill("cust.seal", state.language, ["cipher": cipher]))
                                    .font(.caption2).foregroundStyle(Theme.t2)
                            }
                            if let n = p.audit?.count {
                                Text(L10n.fill("cust.events", state.language, ["n": "\(n)"]))
                                    .font(.caption2).foregroundStyle(Theme.t2)
                            }
                            Text(L10n.t(p.chain?.intact == true ? "cust.hash.ok"
                                      : "cust.hash.unknown", state.language))
                                .font(.caption2.bold())
                                .foregroundStyle(p.chain?.intact == true
                                                 ? Theme.green : Theme.amber)
                        }
                    }.card()
                }
            }

            // Take it, and end it. Both, in the one place a person comes
            // looking for what this deployment holds about them.
            TakeItWithYouCard()
            EndItCard()
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        do {
            list = try await ApiClient.shared.custody(uid: uid, token: token)
            error = nil
        } catch { self.error = error.localizedDescription }
    }

    private func toggle(_ key: String) {
        if openKey == key { openKey = nil; return }
        openKey = key
        guard provenance[key] == nil,
              let uid = state.uid, let token = state.token else { return }
        Task {
            provenance[key] = try? await ApiClient.shared.custodyProvenance(
                uid: uid, token: token, key: key)
        }
    }
}

/// The portability door. Counts and table names on the phone; the document
/// itself is what the console downloads.
struct TakeItWithYouCard: View {
    @EnvironmentObject var state: AppState
    @State private var held: String?
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("hld.take", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("hld.take.pitch", state.language))
                .font(.caption).foregroundStyle(Theme.t2)
            Button(L10n.t("hld.take.go", state.language)) { load() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(Theme.brand).clipShape(Capsule())
            if let held { Text(held).font(.caption).foregroundStyle(Theme.t2) }
            if let error { Text(error).font(.caption).foregroundStyle(Theme.red) }
        }.card()
    }

    private func load() {
        Task {
            do {
                let all = try await ApiClient.shared.exportEverything(
                    userId: state.uid ?? "", token: state.token ?? "")
                let rows = all.tables.values.reduce(0) { $0 + $1.count }
                held = L10n.t("hld.take.held", state.language)
                    .replacingOccurrences(of: "{t}", with: "\(all.tables.count)")
                    .replacingOccurrences(of: "{r}", with: "\(rows)")
            } catch {
                self.error = error.localizedDescription
            }
        }
    }
}

/// The exit. Beside the portability door on purpose: *take it* and *end it*
/// are the two halves of the same claim, and until now this shell carried
/// only the first one.
struct EndItCard: View {
    @EnvironmentObject var state: AppState
    @State private var typed = ""
    @State private var gone: String?
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("hld.end", state.language))
                .font(.headline).foregroundStyle(Theme.red)
            Text(L10n.t("hld.end.pitch", state.language))
                .font(.caption).foregroundStyle(Theme.t2)
            TextField(L10n.t("hld.end.ph", state.language), text: $typed)
                .textFieldStyle(.roundedBorder).autocorrectionDisabled()
            // Armed only by the word itself. The console asks for the same
            // word for the same reason: there is no undo behind this.
            Button(L10n.t("hld.end.go", state.language)) { end() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(typed == "erase" ? Theme.red : Theme.t3)
                .clipShape(Capsule())
                .disabled(typed != "erase")
            if let gone { Text(gone).font(.caption).foregroundStyle(Theme.t2) }
            if let error { Text(error).font(.caption).foregroundStyle(Theme.red) }
        }.card()
    }

    private func end() {
        Task {
            do {
                _ = try await ApiClient.shared.eraseEverything(
                    userId: state.uid ?? "", token: state.token ?? "")
                gone = L10n.t("hld.end.gone", state.language)
                state.signOut()
            } catch {
                self.error = error.localizedDescription
            }
        }
    }
}
