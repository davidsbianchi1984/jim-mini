import SwiftUI

/// Budgets: this much per month for this category. Financial stress is one
/// of the eight conditions the Guardian takes on, and a budget is how it
/// learns the shape of yours. Console door (Aims) since 0.42.x; this is the
/// phone's.
struct BudgetCard: View {
    @EnvironmentObject var state: AppState
    @State private var sheet: BudgetsOut?
    @State private var category = ""
    @State private var limit = 100.0
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("aim.budget", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let sheet {
                if sheet.budgets.isEmpty {
                    Text(L10n.t("aim.budget.none", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }
                ForEach(sheet.budgets, id: \.category) { row in
                    HStack {
                        Text(row.category)
                            .font(.caption2.bold()).foregroundStyle(Theme.txt)
                        Text(L10n.t("aim.budget.line", state.language)
                                .replacingOccurrences(
                                    of: "{spent}",
                                    with: String(format: "$%.0f", row.spent))
                                .replacingOccurrences(
                                    of: "{limit}",
                                    with: String(format: "$%.0f",
                                                 row.monthly_limit))
                                .replacingOccurrences(of: "{standing}",
                                                      with: row.standing))
                            .font(.caption2).foregroundStyle(Theme.t2)
                        Spacer()
                        Button(L10n.t("aim.budget.remove", state.language)) {
                            clear(row.category)
                        }
                        .font(.caption2).foregroundStyle(Theme.red)
                        .disabled(busy)
                    }
                }
            }
            HStack(spacing: 8) {
                TextField(L10n.t("aim.budget.cat.ph", state.language),
                          text: $category)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                Stepper(String(format: "$%.0f", limit), value: $limit,
                        in: 10...5000, step: 10)
                    .font(.caption2).foregroundStyle(Theme.txt)
            }
            Button(L10n.t("aim.budget.set", state.language)) { set() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy || category.isEmpty)
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        sheet = try? await ApiClient.shared.budgets(uid: uid, token: token)
    }

    private func set() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.setBudget(
                    uid: uid, token: token,
                    category: category.trimmingCharacters(in: .whitespaces),
                    monthlyLimit: limit)
                category = ""
                await load()
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func clear(_ category: String) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.clearBudget(
                    uid: uid, token: token, category: category)
                await load()
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
