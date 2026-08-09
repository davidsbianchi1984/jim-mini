import SwiftUI

/// Home: greeting, Guardian status, and the learned baseline (GET /baseline).
struct OverviewView: View {
    @EnvironmentObject var state: AppState
    /// Edited here and written to `AppState` on save, so a half-typed
    /// key never reaches the wire. Saving an empty box is the clear.
    @State private var llmKey = ""
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
                    Text(L10n.t("ov.watching", state.language)).font(.caption.bold()).foregroundStyle(Theme.green)
                }
                Text(L10n.t("ov.hi", state.language)
                    .replacingOccurrences(of: "{name}", with: state.displayName))
                    .font(.title.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("ov.watching.sub", state.language))
                    .font(.subheadline).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("ov.baseline", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    if loading {
                        ProgressView().tint(Theme.brandA)
                    } else if metrics.isEmpty {
                        Text(L10n.t("ov.baseline.none", state.language)
                            .replacingOccurrences(of: "{screen}",
                                with: L10n.t("tab.monitor", state.language)))
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
                    Text(L10n.t("ov.model", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("ov.model.sub", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    Picker("", selection: $provider) {
                        Text(L10n.t("ov.model.auto", state.language)).tag("auto")
                        ForEach(providers, id: \.name) { p in
                            Text(p.label + (p.configured ? "" : " (no key)")).tag(p.name)
                        }
                    }
                    .pickerStyle(.menu).tint(Theme.brandA)
                    .onChange(of: provider) { _ in applyModel() }
                }.card()

                // 0.58.0. The console has offered this since 0.4.3 and the
                // phones never did: a key set there was used there, and the
                // deployment's key used here, on the same account.
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("set.key", state.language))
                        .font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("set.key.pitch", state.language))
                        .font(.footnote).foregroundStyle(Theme.t2)
                    Text(L10n.t("set.key.label", state.language))
                        .font(.caption).foregroundStyle(Theme.t3)
                    SecureField(L10n.t("set.key.ph", state.language), text: $llmKey)
                        .textFieldStyle(.plain).foregroundStyle(Theme.txt)
                    Button(L10n.t("set.save", state.language)) {
                        state.rememberLlmKey(llmKey)
                    }
                    .font(.subheadline.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 14).padding(.vertical, 9)
                    .background(Theme.brandA).clipShape(Capsule())
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("ov.language", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("ov.language.sub", state.language))
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
                            Text(L10n.t("ov.pretranslate", state.language))
                                .font(.subheadline).foregroundStyle(Theme.txt)
                            Text(L10n.t("ov.pretranslate.sub", state.language))
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }
                    .tint(Theme.green)
                    .onChange(of: preTranslate) { _ in applyLanguage() }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("ov.translate", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("ov.translate.sub", state.language)
                        .replacingOccurrences(of: "{lang}", with:
                            languages.first { $0.code == language }?.label
                            ?? L10n.t("ov.translate.yours", state.language)))
                        .font(.caption).foregroundStyle(Theme.t2)
                    TextField(L10n.t("ov.translate.placeholder", state.language), text: $translateInput, axis: .vertical)
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
                        Text(L10n.t("ov.engine", state.language)
                            .replacingOccurrences(of: "{engine}", with: r.engine)
                         + (r.note.map { " — \($0)" } ?? ""))
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                }.card()

                AdaptationCard()
                TrainedModelCard()
                AnonymityCard()

                ImproveCard()

                Button(L10n.t("action.sign_out", state.language)) { state.signOut() }
                    .font(.subheadline).foregroundStyle(Theme.t2)
                    .frame(maxWidth: .infinity).padding(.vertical, 12)
                    .overlay(RoundedRectangle(cornerRadius: 12).stroke(Theme.line, lineWidth: 1))
            }.padding(20)
        }
        .refreshable { await load() }
        .task {
            llmKey = state.llmKey
            await load()
        }
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
            Text(L10n.t("ov.learned", state.language)).font(.headline)
                .foregroundStyle(Theme.txt)
            if let p = profile, p.built, let d = p.profile {
                if let confidence = p.confidence, let evidence = p.evidence_items {
                    Text(L10n.t("ov.confidence", state.language)
                        .replacingOccurrences(of: "{pct}",
                                              with: "\(Int(confidence * 100))")
                        .replacingOccurrences(of: "{n}", with: "\(evidence)"))
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
                            Text(L10n.t("ov.helped", state.language)
                                .replacingOccurrences(of: "{n}",
                                                      with: "\(entry.value.helped)")
                                .replacingOccurrences(of: "{total}",
                                                      with: "\(entry.value.answered)"))
                                .font(.caption).monospacedDigit()
                                .foregroundStyle(entry.value.helped * 2 >= entry.value.answered
                                                 ? Theme.green : Theme.amber)
                        }
                    }
                }
                if let tone = d.tone {
                    Text(L10n.t("ov.tone", state.language)
                        .replacingOccurrences(of: "{tone}", with: tone)).font(.caption)
                        .foregroundStyle(Theme.t3)
                }
                if let job = d.occupation {
                    Text(L10n.t("ov.work", state.language)
                        .replacingOccurrences(of: "{job}", with: job)).font(.caption)
                        .foregroundStyle(Theme.t3)
                }
                if p.vaulted == true {
                    Text(L10n.t("ov.sealed", state.language)).font(.caption2)
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

/// The offline fine-tune, on this phone.
///
/// A separate card from the adaptation profile beside it, on purpose: that one
/// is a profile that conditions a prompt, this one is weights. One card doing
/// both is how a reader ends up unable to say which of the two they have.
struct TrainedModelCard: View {
    @EnvironmentObject var state: AppState
    @State private var ft: Finetune?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ov.ft", state.language)).font(.headline)
                .foregroundStyle(Theme.txt)
            Text(L10n.t("ov.ft.sub", state.language))
                .font(.footnote).foregroundStyle(Theme.t2)

            if let f = ft {
                Text(L10n.fill("ov.ft.from", state.language,
                               ["n": "\(f.examples)"]))
                    .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                // The server's own sentence, shown rather than paraphrased:
                // it is the line that says whether weights or a prompt came
                // out of this, and rewording it here would blur exactly that.
                Text(f.method).font(.caption).foregroundStyle(Theme.t3)
                Toggle(L10n.t("ov.ft.use", state.language),
                       isOn: Binding(get: { f.active ?? false },
                                     set: { setActive($0) }))
                    .font(.subheadline).foregroundStyle(Theme.txt)
                Text(L10n.t("ov.ft.off", state.language))
                    .font(.caption2).foregroundStyle(Theme.t3)
            } else {
                Text(L10n.t("ov.ft.none", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)
            }

            if let error { Text(error).font(.caption).foregroundStyle(Theme.red) }
            Button(L10n.t(busy ? "ov.ft.training" : "ov.ft.train",
                          state.language)) { train() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy)
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        // A 404 until something has been trained, which is the normal state.
        ft = try? await ApiClient.shared.finetune(uid: uid, token: token)
    }

    private func train() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do { ft = try await ApiClient.shared.runFinetune(uid: uid, token: token) }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func setActive(_ on: Bool) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            do {
                _ = try await ApiClient.shared.setFinetuneActive(
                    uid: uid, token: token, active: on)
                await load()
            } catch { self.error = error.localizedDescription }
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
            Text(L10n.t("ov.name", state.language)).font(.headline).foregroundStyle(Theme.txt)
            if let p = posture {
                Text(p.anonymous ? knownAs(p) : L10n.t("ov.name.own", state.language))
                    .font(.subheadline).foregroundStyle(Theme.txt)
                ForEach(p.keeps, id: \.self) { line in
                    Text("✓ " + line).font(.caption).foregroundStyle(Theme.green)
                }
                ForEach(p.costs, id: \.self) { line in
                    Text("• " + line).font(.caption).foregroundStyle(Theme.amber)
                }
                if p.costs.isEmpty && p.anonymous {
                    Text(L10n.t("ov.legal", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }
            } else {
                Text(L10n.t("ov.loading", state.language)).font(.caption).foregroundStyle(Theme.t3)
            }
        }
        .card()
        .task { await load() }
    }

    private func knownAs(_ p: AnonymityPosture) -> String {
        L10n.t("ov.name.pseudonym", state.language)
            .replacingOccurrences(of: "{name}", with: p.known_as
                ?? L10n.t("ov.name.pseudonym.fallback", state.language))
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        posture = try? await ApiClient.shared.anonymity(uid: uid, token: token)
    }
}
