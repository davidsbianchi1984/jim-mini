import SwiftUI

/// Home: greeting, Guardian status, and the learned baseline (GET /baseline).
struct OverviewView: View {
    @EnvironmentObject var state: AppState
    @State private var metrics: [BaselineMetric] = []
    @State private var loading = true
    @State private var providers: [ProviderInfo] = []
    @State private var provider = "auto"
    @State private var languages: [LanguageInfo] = []
    @State private var language = "en"

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

                VStack(alignment: .leading, spacing: 8) {
                    Text("Model").font(.headline).foregroundStyle(Theme.txt)
                    Text("Which LLM powers your coaching and guidance.")
                        .font(.caption).foregroundStyle(Theme.t2)
                    Picker("", selection: $provider) {
                        Text("Auto (platform default)").tag("auto")
                        ForEach(providers, id: \.name) { p in
                            Text(p.label + (p.configured ? "" : " (no key)")).tag(p.name)
                        }
                    }
                    .pickerStyle(.menu).tint(Theme.brandA)
                    .onChange(of: provider) { _ in applyModel() }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text("Language").font(.headline).foregroundStyle(Theme.txt)
                    Text("Everything drafted for you — guidance, coaching, first-aid steps, waiver terms — is delivered in this language.")
                        .font(.caption).foregroundStyle(Theme.t2)
                    Picker("", selection: $language) {
                        ForEach(languages, id: \.code) { l in
                            Text(l.label + (l.safety_content_translated == true
                                            ? "" : " (safety steps in English)"))
                                .tag(l.code)
                        }
                    }
                    .pickerStyle(.menu).tint(Theme.brandA)
                    .onChange(of: language) { _ in applyLanguage() }
                }.card()

                Button("Sign out") { state.signOut() }
                    .font(.subheadline).foregroundStyle(Theme.t2)
                    .frame(maxWidth: .infinity).padding(.vertical, 12)
                    .overlay(RoundedRectangle(cornerRadius: 12).stroke(Theme.line, lineWidth: 1))
            }.padding(20)
        }
        .task { await load() }
    }

    private func applyModel() {
        guard let uid = state.uid, let token = state.token else { return }
        Task { _ = try? await ApiClient.shared.setModel(uid: uid, token: token,
                                                        provider: provider) }
    }

    private func applyLanguage() {
        guard let uid = state.uid, let token = state.token else { return }
        Task { _ = try? await ApiClient.shared.setLanguage(uid: uid, token: token,
                                                           code: language) }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        loading = true
        metrics = (try? await ApiClient.shared.baseline(uid: uid, token: token)) ?? []
        providers = (try? await ApiClient.shared.models())?.providers.filter { $0.name != "auto" } ?? []
        if let m = try? await ApiClient.shared.userModel(uid: uid, token: token) {
            provider = m.provider
        }
        languages = (try? await ApiClient.shared.languages())?.languages ?? []
        if let l = try? await ApiClient.shared.userLanguage(uid: uid, token: token) {
            language = l.language
        }
        loading = false
    }
}
