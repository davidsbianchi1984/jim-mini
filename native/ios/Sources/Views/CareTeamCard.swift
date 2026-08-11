import SwiftUI

/// The care team: the user's own QRME organization, linked as the household's
/// coordination layer. The owner token is pasted knowingly — QRME's org
/// routes are owner-only and JIM never sneaks around that. Console door
/// since task #106; this is the phone's.
struct CareTeamCard: View {
    @EnvironmentObject var state: AppState
    @State private var team: CareTeamState?
    @State private var plans: [CareTeamPlanRow] = []
    @State private var orgId = ""
    @State private var departmentId = ""
    @State private var ownerToken = ""
    @State private var goal = ""
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.ct.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.ct.sub", state.language))
                .font(.caption).foregroundStyle(Theme.t2)

            if let team, team.linked {
                Text(L10n.t("ns.ct.linked", state.language))
                    .font(.caption.bold()).foregroundStyle(Theme.green)
                Text(L10n.t("ns.ct.linked.pitch", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                Text(L10n.t("ns.ct.linked.line", state.language)
                        .replacingOccurrences(of: "{org}", with: team.org_id ?? "")
                        .replacingOccurrences(of: "{dept}", with: team.department_id ?? ""))
                    .font(.caption2).foregroundStyle(Theme.t2)

                TextField(L10n.t("ns.ct.linked.goal.ph", state.language),
                          text: $goal)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                HStack {
                    Button(L10n.t("ns.ct.linked.goal", state.language)) { coordinate() }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 8)
                        .background(Theme.brandA).clipShape(Capsule())
                        .disabled(busy || goal.trimmingCharacters(in: .whitespaces).isEmpty)
                    Button(L10n.t("ns.ct.linked.unlink", state.language)) { unlink() }
                        .font(.caption2).foregroundStyle(Theme.red)
                        .disabled(busy)
                }

                if plans.isEmpty {
                    Text(L10n.t("ns.ct.plans.none", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                } else {
                    ForEach(plans.prefix(4)) { plan in
                        VStack(alignment: .leading, spacing: 2) {
                            Text(plan.goal).font(.caption.bold())
                                .foregroundStyle(Theme.txt)
                            if let text = plan.plan, !text.isEmpty {
                                Text(text).font(.caption2).lineLimit(4)
                                    .foregroundStyle(Theme.t2)
                            }
                        }
                    }
                }
            } else {
                Text(L10n.t("ns.ct.link.pitch", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                Text(L10n.t("ns.ct.link.org", state.language))
                    .font(.caption2.bold()).foregroundStyle(Theme.t2)
                TextField(L10n.t("ns.ct.link.org.ph", state.language),
                          text: $orgId)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                Text(L10n.t("ns.ct.link.dept", state.language))
                    .font(.caption2.bold()).foregroundStyle(Theme.t2)
                TextField(L10n.t("ns.ct.link.dept.ph", state.language),
                          text: $departmentId)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                Text(L10n.t("ns.ct.link.token", state.language))
                    .font(.caption2.bold()).foregroundStyle(Theme.t2)
                SecureField(L10n.t("ns.ct.link.token.ph", state.language),
                            text: $ownerToken)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                Button(L10n.t("ns.ct.link.go", state.language)) { link() }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(busy || orgId.isEmpty || departmentId.isEmpty
                              || ownerToken.isEmpty)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        team = try? await ApiClient.shared.careTeamState(uid: uid, token: token)
        if team?.linked == true {
            plans = (try? await ApiClient.shared.careTeamPlans(
                uid: uid, token: token)) ?? []
        }
    }

    private func link() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                team = try await ApiClient.shared.careTeamLink(
                    uid: uid, token: token, orgId: orgId.trimmingCharacters(in: .whitespaces),
                    departmentId: departmentId.trimmingCharacters(in: .whitespaces),
                    ownerToken: ownerToken.trimmingCharacters(in: .whitespaces))
                ownerToken = ""
            } catch { self.error = error.localizedDescription }
            busy = false
            await load()
        }
    }

    private func unlink() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                try await ApiClient.shared.careTeamUnlink(uid: uid, token: token)
                team = nil; plans = []
            } catch { self.error = error.localizedDescription }
            busy = false
            await load()
        }
    }

    private func coordinate() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.careTeamCoordinate(
                    uid: uid, token: token,
                    goal: goal.trimmingCharacters(in: .whitespaces))
                goal = ""
            } catch { self.error = error.localizedDescription }
            busy = false
            await load()
        }
    }
}
