import SwiftUI

/// Home: greeting, Guardian status, and the learned baseline (GET /baseline).
struct OverviewView: View {
    @EnvironmentObject var state: AppState
    @State private var metrics: [BaselineMetric] = []
    @State private var loading = true

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HStack(spacing: 8) {
                    Circle().fill(Theme.green).frame(width: 8, height: 8)
                    Text("Guardian on · watching").font(.caption.bold()).foregroundStyle(Theme.green)
                }
                Text("Hi, \(state.displayName)").font(.title.bold()).foregroundStyle(Theme.txt)
                Text("Your Guardian is watching — the rules are transparent.")
                    .font(.subheadline).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 10) {
                    Text("Learned baseline").font(.headline).foregroundStyle(Theme.txt)
                    if loading {
                        ProgressView().tint(Theme.brandA)
                    } else if metrics.isEmpty {
                        Text("No baseline yet — it builds from calm samples in Monitor.")
                            .font(.footnote).foregroundStyle(Theme.t2)
                    } else {
                        ForEach(metrics, id: \.metric) { m in
                            HStack {
                                Text(m.metric.capitalized).foregroundStyle(Theme.txt)
                                Spacer()
                                Text(m.value.map { String(format: "%.0f", $0) } ?? (m.state ?? "—"))
                                    .foregroundStyle(Theme.t2).monospacedDigit()
                            }.font(.subheadline)
                        }
                    }
                }.card()

                Button("Sign out") { state.signOut() }
                    .font(.subheadline).foregroundStyle(Theme.t2)
                    .frame(maxWidth: .infinity).padding(.vertical, 12)
                    .overlay(RoundedRectangle(cornerRadius: 12).stroke(Theme.line, lineWidth: 1))
            }.padding(20)
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        loading = true
        metrics = (try? await ApiClient.shared.baseline(uid: uid, token: token)) ?? []
        loading = false
    }
}
