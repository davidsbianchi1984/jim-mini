import SwiftUI

/// The record and the veil: who has read your record (an empty list with no
/// record kept is a different fact from nobody having looked), where the
/// answers come from, what you contribute to the shared cloud and how to
/// stop, what went out in your name, and the plans this deployment offers.
/// Console doors (What's Held, Safety, Settings); this is the phone's.
struct VeilCard: View {
    @EnvironmentObject var state: AppState
    @State private var log: AccessLog?
    @State private var audit: AuditLog?
    @State private var cloud: CloudStatus?
    @State private var contribution: ContributionView?
    @State private var revoked: ContributionRevoked?
    @State private var incidentRows: [IncidentRow] = []
    @State private var pageRows: [PageRow] = []
    @State private var locality = ""
    @State private var saved: LocalitySaved?
    @State private var planRows: [PlanRow] = []
    @State private var current: MembershipView?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("hld.log", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let log {
                if log.vaulted {
                    Text(L10n.t("hld.log.vaulted", state.language))
                        .font(.caption2).foregroundStyle(Theme.green)
                }
                if log.access_record_kept {
                    Text(L10n.t("hld.log.kept", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    ForEach(Array(log.entries.prefix(5).enumerated()),
                            id: \.offset) { _, entry in
                        let action = entry.action ?? ""
                        let at = entry.at ?? ""
                        Text("\(action) · \(at)")
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                } else {
                    Text(L10n.t("hld.log.empty", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }
                Text(log.note).font(.caption2).foregroundStyle(Theme.t3)
            }

            // The other half of the same question. The card above says who
            // *read* the record; this says what was *done*, and whether the
            // saying of it has been edited since. The chain's state comes
            // first for the same reason the three fields above do: a list
            // nobody can check is a list, not a record.
            Divider().background(Theme.line)
            Text(L10n.t("hld.audit", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let audit {
                if audit.integrity.intact {
                    Text(L10n.t("hld.audit.intact", state.language))
                        .font(.caption2).foregroundStyle(Theme.green)
                } else {
                    Text(L10n.t("hld.audit.broken", state.language)
                            .replacingOccurrences(
                                of: "{seq}",
                                with: audit.integrity.broken_at_seq.map(String.init)
                                    ?? "?"))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                if audit.count == 0 {
                    Text(L10n.t("hld.audit.none", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                    Text(L10n.t("hld.audit.watched", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    ForEach(audit.catalogue, id: \.action) { row in
                        Text(row.description)
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                } else {
                    ForEach(audit.trail.suffix(8), id: \.seq) { row in
                        // The sentence comes from the catalogue this same
                        // answer carried, never from a second copy kept here.
                        let said = audit.catalogue
                            .first { $0.action == row.action }?.description
                            ?? row.action
                        Text("\(said) · \(row.at)")
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                }
                Text(audit.retention).font(.caption2).foregroundStyle(Theme.t3)
            }

            Divider().background(Theme.line)
            Text(L10n.t("hld.where", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let cloud {
                Text(L10n.t("hld.where.cloud", state.language)
                        .replacingOccurrences(of: "{model}",
                                              with: cloud.model ?? "none")
                        .replacingOccurrences(of: "{fallback}",
                                              with: cloud.fallback))
                    .font(.caption2).foregroundStyle(Theme.t2)
                Text(cloud.contribution)
                    .font(.caption2).foregroundStyle(Theme.t3)
            }

            Divider().background(Theme.line)
            Text(L10n.t("set.cloud", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            if let contribution {
                Text(contribution.policy)
                    .font(.caption2).foregroundStyle(Theme.t3)
                if contribution.opted_in {
                    Button(L10n.t("set.cloud.stop", state.language)) {
                        revoke()
                    }
                    .font(.caption2).foregroundStyle(Theme.red)
                    .disabled(busy)
                }
            }
            if let revoked {
                Text(revoked.note).font(.caption2).foregroundStyle(Theme.t2)
            }

            Divider().background(Theme.line)
            Text(L10n.t("sfy.pages", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            Text(L10n.t("sfy.pages.pitch", state.language))
                .font(.caption2).foregroundStyle(Theme.t3)
            if pageRows.isEmpty {
                Text(L10n.t("sfy.pages.none", state.language))
                    .font(.caption2).foregroundStyle(Theme.t3)
            }
            ForEach(Array(pageRows.prefix(5).enumerated()),
                    id: \.offset) { _, page in
                let to = page.to ?? ""
                let when = page.sent_at ?? ""
                Text("\(to) · \(when)")
                    .font(.caption2)
                    .foregroundStyle(page.delivered == true ? Theme.green
                                                            : Theme.t2)
            }
            Text(L10n.t("sfy.history", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            if incidentRows.isEmpty {
                Text(L10n.t("sfy.history.none", state.language))
                    .font(.caption2).foregroundStyle(Theme.t3)
            }
            ForEach(Array(incidentRows.prefix(5).enumerated()),
                    id: \.offset) { _, incident in
                let kind = incident.kind ?? ""
                let at = incident.at ?? ""
                Text("\(kind) · \(at)")
                    .font(.caption2).foregroundStyle(Theme.amber)
            }

            Divider().background(Theme.line)
            Text(L10n.t("set.loc", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            Text(L10n.t("set.loc.pitch", state.language))
                .font(.caption2).foregroundStyle(Theme.t3)
            HStack(spacing: 8) {
                TextField(L10n.t("set.loc.ph", state.language),
                          text: $locality)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                Button(L10n.t("set.save", state.language)) { save() }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy)
            }
            if let saved {
                Text(saved.locality ?? "")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }

            Divider().background(Theme.line)
            Text(L10n.t("hld.plan", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            if let current {
                Text("\(current.title) · $\(Int(current.price_usd))")
                    .font(.caption2.bold()).foregroundStyle(Theme.txt)
                Text(current.storage.means)
                    .font(.caption2).foregroundStyle(Theme.t3)
                let readers = current.storage.who_can_read
                    .joined(separator: ", ")
                Text(L10n.t("hld.plan.canread", state.language)
                        .replacingOccurrences(of: "{list}", with: readers))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            ForEach(planRows, id: \.plan) { plan in
                Button("\(plan.title) · $\(Int(plan.price_usd))") {
                    join(plan.plan)
                }
                .font(.caption2)
                .foregroundStyle(current?.plan == plan.plan ? Theme.green
                                                            : Theme.brandA)
                .disabled(busy || current?.plan == plan.plan)
            }
            Button(L10n.t("hld.plan.cancel", state.language)) { cancel() }
                .font(.caption2).foregroundStyle(Theme.red)
                .disabled(busy)
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        cloud = try? await ApiClient.shared.cloudStatus()
        planRows = (try? await ApiClient.shared.plans())?.plans ?? []
        guard let uid = state.uid, let token = state.token else { return }
        log = try? await ApiClient.shared.accessLog(uid: uid, token: token)
        audit = try? await ApiClient.shared.auditLog(uid: uid, token: token)
        contribution = try? await ApiClient.shared.cloudContribution(
            uid: uid, token: token)
        incidentRows = (try? await ApiClient.shared.incidents(
            uid: uid, token: token)) ?? []
        pageRows = (try? await ApiClient.shared.pages(uid: uid,
                                                      token: token)) ?? []
        current = try? await ApiClient.shared.membership(uid: uid,
                                                         token: token)
    }

    /// Billing is simulated and the server's own sheet says so.
    private func join(_ plan: String) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                current = try await ApiClient.shared.subscribe(
                    uid: uid, token: token, plan: plan)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    /// The person keeps their record, their conditions and every emergency
    /// path.
    private func cancel() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                current = try await ApiClient.shared.cancelMembership(
                    uid: uid, token: token)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func revoke() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                revoked = try await ApiClient.shared.revokeCloudContribution(
                    uid: uid, token: token)
                contribution = try? await ApiClient.shared.cloudContribution(
                    uid: uid, token: token)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func save() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                saved = try await ApiClient.shared.setLocality(
                    uid: uid, token: token,
                    locality: locality.trimmingCharacters(in: .whitespaces))
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
