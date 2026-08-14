import SwiftUI

/// The voice this deployment speaks in — provider, voice, and whether
/// replies are read aloud. The key is write-only: the route says whether
/// one is set and never says it back. Console door since 0.6.0; this is
/// the phone's.
struct VoiceSettingsCard: View {
    @EnvironmentObject var state: AppState
    @State private var settings: VoiceSettingsOut?
    @State private var quota: VoiceQuotaOut?
    @State private var provider = ""
    @State private var voiceId = ""
    @State private var apiKey = ""
    @State private var speakReplies = true
    @State private var busy = false
    @State private var error: String?

    // The provider vocabulary is the backend's PROVIDERS tuple; the
    // describe route answers the current one but does not enumerate them.
    private let providers = ["elevenlabs", "openai", "device"]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.vs.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let settings {
                if settings.provider == "device" {
                    Text(L10n.t("ns.vs.pitch", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                } else {
                    Text(L10n.t("ns.vs.through", state.language)
                            .replacingOccurrences(of: "{provider}",
                                                  with: settings.provider)
                            .replacingOccurrences(of: "{env}",
                                with: settings.key_source == "environment"
                                    ? " (env)" : ""))
                        .font(.caption2).foregroundStyle(Theme.green)
                }
            }

            // The allowance. A spent one used to be invisible here: the send
            // is refused, this shell falls back to the device's own voice on
            // any non-ok status, and the Guardian went on talking in a
            // flatter voice with nobody told why. Amber rather than red —
            // it still speaks, just not in the chosen voice.
            if let quota {
                Text(L10n.t(quota.exhausted ? "ns.vs.spent" : "ns.vs.left",
                            state.language)
                        .replacingOccurrences(of: "{left}",
                                              with: "\(quota.left)")
                        .replacingOccurrences(of: "{limit}",
                                              with: "\(quota.limit)"))
                    .font(.caption2)
                    .foregroundStyle(quota.exhausted ? Theme.amber : Theme.t2)
            }

            HStack(spacing: 8) {
                ForEach(providers, id: \.self) { name in
                    Button(name) { provider = name }
                        .font(.caption2.bold())
                        .foregroundStyle(provider == name ? .white : Theme.t2)
                        .padding(.horizontal, 10).padding(.vertical, 6)
                        .background(provider == name ? Theme.brandA
                                                     : Theme.scrBot)
                        .clipShape(Capsule())
                }
            }

            if provider != "device", let settings {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(settings.voices, id: \.id) { voice in
                            Button("\(voice.name) · \(voice.note)") {
                                voiceId = voice.id
                            }
                            .font(.caption2)
                            .foregroundStyle(voiceId == voice.id
                                             ? .white : Theme.t2)
                            .padding(.horizontal, 10).padding(.vertical, 6)
                            .background(voiceId == voice.id ? Theme.brandA
                                                            : Theme.scrBot)
                            .clipShape(Capsule())
                        }
                    }
                }
                SecureField(settings.key_set
                            ? L10n.t("ns.ml.saved", state.language)
                            : "sk-…",
                            text: $apiKey)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
            }

            Toggle(isOn: $speakReplies) {
                Text(L10n.t("ns.vs.hear", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }

            HStack {
                Button(L10n.t("ns.set.save", state.language)) { save() }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(busy || provider.isEmpty)
                Button(L10n.t("ns.bas.reset", state.language)) { clear() }
                    .font(.caption2).foregroundStyle(Theme.red)
                    .disabled(busy)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        settings = try? await ApiClient.shared.voiceSettings()
        // `try?` deliberately: a deployment on the device voice, or on a
        // provider that publishes no balance, answers 503 here, and that is
        // an absence of a line rather than a failure to report.
        quota = try? await ApiClient.shared.voiceQuota()
        if let settings {
            if provider.isEmpty { provider = settings.provider }
            if voiceId.isEmpty { voiceId = settings.voice_id ?? "" }
            speakReplies = settings.speak_replies
        }
    }

    private func save() {
        busy = true; error = nil
        Task {
            do {
                settings = try await ApiClient.shared.saveVoiceSettings(
                    provider: provider,
                    // `.whitespaces` and not `.whitespacesAndNewlines` was
                    // the whole difference: a key copied from a dashboard
                    // arrives with a trailing newline, which this stripped
                    // spaces around and sent anyway. The other three clients
                    // strip it, and their agreement is what kept this one
                    // out of sight. `AppState` already used the wider set.
                    apiKey: apiKey.trimmingCharacters(in: .whitespacesAndNewlines),
                    voiceId: voiceId, speakReplies: speakReplies)
                apiKey = ""
                // The provider may have just changed, and with it whether
                // there is an allowance to show at all.
                quota = try? await ApiClient.shared.voiceQuota()
                // And whether what was saved is a key at all. Saving used to
                // report only that the string had been written down; a key
                // the service refuses looked identical to one it accepts
                // until somebody asked to be spoken to.
                if let check = try? await ApiClient.shared.checkVoiceKey(),
                   !check.ok {
                    self.error = L10n.t("ns.vs.\(check.verdict)",
                                        state.language)
                }
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func clear() {
        busy = true; error = nil
        Task {
            do {
                settings = try await ApiClient.shared.clearVoiceSettings()
                provider = settings?.provider ?? ""
                voiceId = ""
                quota = try? await ApiClient.shared.voiceQuota()
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
