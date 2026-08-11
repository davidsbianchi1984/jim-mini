import SwiftUI

/// Ability is not a gate: the accessibility report door.
///
/// Three questions and none is a diagnosis — what were you trying to do,
/// what stood in the way, what would help. Tokenless on the wire, because
/// the person this card exists for may be the person the signup shut out,
/// and the phone keeps no copy: the words go to the deployment and stay
/// there. The reviewer section reads them back with the deployment's own
/// token — the role that stands for the deployment, not for any profile.
struct AccessCard: View {
    @EnvironmentObject var state: AppState
    @State private var doing = ""
    @State private var wall = ""
    @State private var help = ""
    @State private var status: String?
    @State private var reviewer = ""
    @State private var reports: AccessReportsState?
    @State private var reviewStatus: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.acc", state.language)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.acc.lead", state.language))
                .font(.caption).foregroundStyle(Theme.t2)

            field(L10n.t("ns.acc.doing.ph", state.language), text: $doing)
            field(L10n.t("ns.acc.wall.ph", state.language), text: $wall)
            field(L10n.t("ns.acc.help.ph", state.language), text: $help)

            Button(L10n.t("ns.acc.send", state.language)) { send() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(doing.trimmingCharacters(in: .whitespaces).isEmpty
                          || wall.trimmingCharacters(in: .whitespaces).isEmpty)

            if let status { Text(status).font(.caption).foregroundStyle(Theme.green) }

            Divider().overlay(Theme.line)
            HStack(spacing: 6) {
                SecureField(L10n.t("ns.acc.token.ph", state.language), text: $reviewer)
                    .foregroundStyle(Theme.txt)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                Button(L10n.t("ns.acc.load", state.language)) { load() }
                    .font(.caption2.bold()).foregroundStyle(Theme.brandA)
            }
            if let reports {
                if reports.total == 0 {
                    Text(L10n.t("ns.acc.none", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                } else {
                    ForEach(reports.reports.prefix(6), id: \.id) { r in
                        VStack(alignment: .leading, spacing: 2) {
                            Text(r.doing).font(.caption.bold()).foregroundStyle(Theme.txt)
                            Text(r.wall).font(.caption2).foregroundStyle(Theme.t2)
                            if let h = r.help, !h.isEmpty {
                                Text(h).font(.caption2).italic().foregroundStyle(Theme.t2)
                            }
                            Text("\(r.lang) · \(r.created_at)")
                                .font(.caption2).foregroundStyle(Theme.t3)
                        }
                    }
                }
            }
            if let reviewStatus { Text(reviewStatus).font(.caption2).foregroundStyle(Theme.amber) }
        }.card()
    }

    private func field(_ placeholder: String, text: Binding<String>) -> some View {
        TextField(placeholder, text: text, axis: .vertical)
            .lineLimit(1...4).foregroundStyle(Theme.txt)
            .padding(10).background(Theme.scrBot)
            .clipShape(RoundedRectangle(cornerRadius: 11))
            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
    }

    private func send() {
        Task {
            do {
                _ = try await ApiClient.shared.sendAccessReport(
                    doing: doing.trimmingCharacters(in: .whitespaces),
                    wall: wall.trimmingCharacters(in: .whitespaces),
                    help: help.trimmingCharacters(in: .whitespaces),
                    lang: state.language)
                status = L10n.t("ns.acc.sent", state.language)
                doing = ""; wall = ""; help = ""
            } catch { status = error.localizedDescription }
        }
    }

    private func load() {
        Task {
            do {
                reports = try await ApiClient.shared.accessReports(
                    reviewerToken: reviewer.trimmingCharacters(in: .whitespaces))
                reviewStatus = nil
            } catch { reviewStatus = error.localizedDescription }
        }
    }
}
