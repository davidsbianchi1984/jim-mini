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
