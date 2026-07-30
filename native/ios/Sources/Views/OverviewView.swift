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
    @State private var preTranslate = true
    @State private var translateInput = ""
    @State private var translateResult: TranslateResult?

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
                    Toggle(isOn: $preTranslate) {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Pre-translate everything")
                                .font(.subheadline).foregroundStyle(Theme.txt)
                            Text("Off keeps originals — translate selectively below.")
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }
                    .tint(Theme.green)
                    .onChange(of: preTranslate) { _ in applyLanguage() }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text("Translate").font(.headline).foregroundStyle(Theme.txt)
                    Text("Anything you run across — a note, a message, a label — into \(languages.first { $0.code == language }?.label ?? "your language").")
                        .font(.caption).foregroundStyle(Theme.t2)
                    TextField("Paste or type text…", text: $translateInput, axis: .vertical)
                        .lineLimit(1...4).foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    Button(L10n.t("action.translate", state.language)) { runTranslate() }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 8)
                        .background(Theme.brandA).clipShape(Capsule())
                        .disabled(translateInput.isEmpty || language == "en")
                    if let r = translateResult {
                        Text(r.translation).font(.subheadline).foregroundStyle(Theme.txt)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 9))
                        Text("engine: \(r.engine)" + (r.note.map { " — \($0)" } ?? ""))
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                }.card()

                AdaptationCard()
                AnonymityCard()

                ImproveCard()

                Button(L10n.t("action.sign_out", state.language)) { state.signOut() }
                    .font(.subheadline).foregroundStyle(Theme.t2)
                    .frame(maxWidth: .infinity).padding(.vertical, 12)
                    .overlay(RoundedRectangle(cornerRadius: 12).stroke(Theme.line, lineWidth: 1))
            }.padding(20)
        }
        .refreshable { await load() }
        .task { await load() }
    }

    private func applyModel() {
        guard let uid = state.uid, let token = state.token else { return }
        Task { _ = try? await ApiClient.shared.setModel(uid: uid, token: token,
                                                        provider: provider) }
    }

    private func applyLanguage() {
        guard let uid = state.uid, let token = state.token else { return }
        state.rememberLanguage(language)
        Task {
            _ = try? await ApiClient.shared.setLanguage(
                uid: uid, token: token, code: language,
                mode: preTranslate ? "pre" : "on_demand")
        }
    }

    private func runTranslate() {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            translateResult = try? await ApiClient.shared.translate(
                uid: uid, token: token, text: translateInput)
        }
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
            preTranslate = (l.mode ?? "pre") == "pre"
            state.rememberLanguage(l.language)   // chrome follows the user
        }
        loading = false
    }
}

// MARK: What JIM has learned about you (claim 11)

/// The user-specific adaptation profile, in plain terms.
///
/// Shown as counts off this user's own history rather than a score, and it says
/// where the profile came from: nothing was sent to a model vendor to build it,
/// and the sealed copy lives in their own vault.
private struct AdaptationCard: View {
    @EnvironmentObject var state: AppState
    @State private var profile: AdaptationProfile?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("What JIM has learned about you").font(.headline)
                .foregroundStyle(Theme.txt)
            if let p = profile, p.built, let d = p.profile {
                if let confidence = p.confidence, let evidence = p.evidence_items {
                    Text("Confidence \(Int(confidence * 100))% — earned from "
                         + "\(evidence) things already on your record.")
                        .font(.caption).foregroundStyle(Theme.t2)
                }
                // Only conditions with enough answers to mean anything: a
                // coincidence is not a finding, and the backend says so too.
                ForEach(d.what_helps.sorted(by: { $0.key < $1.key }), id: \.key) { entry in
                    if entry.value.answered > 0 {
                        HStack {
                            Text(entry.key.replacingOccurrences(of: "_", with: " "))
                                .font(.subheadline).foregroundStyle(Theme.txt)
                            Spacer()
                            Text("helped \(entry.value.helped) of \(entry.value.answered)")
                                .font(.caption).monospacedDigit()
                                .foregroundStyle(entry.value.helped * 2 >= entry.value.answered
                                                 ? Theme.green : Theme.amber)
                        }
                    }
                }
                if let tone = d.tone {
                    Text("Tone you asked for: \(tone)").font(.caption)
                        .foregroundStyle(Theme.t3)
                }
                if let job = d.occupation {
                    Text("Work you named: \(job)").font(.caption)
                        .foregroundStyle(Theme.t3)
                }
                if p.vaulted == true {
                    Text("Sealed in your own vault.").font(.caption2)
                        .foregroundStyle(Theme.green)
                }
                if let method = d.method {
                    Text(method).font(.caption2).foregroundStyle(Theme.t3)
                }
            } else {
                Text(profile?.note
                     ?? "No profile yet — it is built from the history already "
                      + "on record, here on your own device's backend.")
                    .font(.caption).foregroundStyle(Theme.t2)
            }
            Button(busy ? "Rebuilding…" : "Rebuild from my history") { rebuild() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy)
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        profile = try? await ApiClient.shared.adaptation(uid: uid, token: token)
    }

    private func rebuild() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task {
            profile = try? await ApiClient.shared.rebuildAdaptation(uid: uid,
                                                                    token: token)
            busy = false
        }
    }
}

// MARK: Your name here (spec [0031] / box 212)

/// The anonymity posture, stated as a tradeoff rather than a switch: what the
/// choice keeps and what it costs, so it is a decision and not a surprise.
private struct AnonymityCard: View {
    @EnvironmentObject var state: AppState
    @State private var posture: AnonymityPosture?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Your name here").font(.headline).foregroundStyle(Theme.txt)
            if let p = posture {
                Text(p.anonymous
                     ? "You are known here as \(p.known_as ?? "a pseudonym")."
                     : "You are enrolled under your own name.")
                    .font(.subheadline).foregroundStyle(Theme.txt)
                ForEach(p.keeps, id: \.self) { line in
                    Text("✓ " + line).font(.caption).foregroundStyle(Theme.green)
                }
                ForEach(p.costs, id: \.self) { line in
                    Text("• " + line).font(.caption).foregroundStyle(Theme.amber)
                }
                if p.costs.isEmpty && p.anonymous {
                    Text("A legal name is on record for responders.")
                        .font(.caption2).foregroundStyle(Theme.t3)
                }
            } else {
                Text("Loading…").font(.caption).foregroundStyle(Theme.t3)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        posture = try? await ApiClient.shared.anonymity(uid: uid, token: token)
    }
}
