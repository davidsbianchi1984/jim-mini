import SwiftUI

/// Where this deployment sends mail through — and the test button that
/// proves it can, because a settings screen that saves without delivering
/// is how an app ends up insisting it emailed somebody. The password is
/// write-only. Console door since 0.4.x; this is the phone's.
struct MailSettingsCard: View {
    @EnvironmentObject var state: AppState
    @State private var settings: MailSettingsOut?
    @State private var host = ""
    @State private var port = "587"
    @State private var username = ""
    @State private var password = ""
    @State private var sender = ""
    @State private var publicUrl = ""
    @State private var testTo = ""
    @State private var testSentTo: String?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.ml.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let settings {
                if settings.transport == "smtp" {
                    Text(L10n.t("ns.ml.smtp", state.language)
                            .replacingOccurrences(of: "{host}",
                                                  with: settings.host ?? "")
                            .replacingOccurrences(of: "{env}",
                                with: settings.source == "environment"
                                    ? " (env)" : ""))
                        .font(.caption2).foregroundStyle(Theme.green)
                } else {
                    Text(L10n.t("ns.ml.none", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
            }

            Text(L10n.t("ns.ml.host", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField(L10n.t("ns.ml.host.ph", state.language), text: $host)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Text(L10n.t("ns.ml.port", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField("587", text: $port)
                .keyboardType(.numberPad)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Text(L10n.t("ns.ml.user", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField(L10n.t("ns.ml.user.ph", state.language),
                      text: $username)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Text(L10n.t("ns.ml.pass", state.language)
                 + (settings?.password_set == true
                    ? " " + L10n.t("ns.ml.saved", state.language) : ""))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            SecureField(L10n.t("ns.ml.pass.ph", state.language),
                        text: $password)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Text(L10n.t("ns.ml.from", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField(L10n.t("ns.ml.user.ph", state.language), text: $sender)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Text(L10n.t("ns.ml.link", state.language)
                 + L10n.t("ns.ml.link.note", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            TextField(L10n.t("ns.ml.link.ph", state.language),
                      text: $publicUrl)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))

            HStack {
                Button(L10n.t("ns.set.save", state.language)) { save() }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(busy || host.isEmpty)
                Button(L10n.t("ns.bas.reset", state.language)) { clear() }
                    .font(.caption2).foregroundStyle(Theme.red)
                    .disabled(busy)
            }

            Text(L10n.t("ns.ml.test", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            HStack {
                TextField(L10n.t("ns.ml.test.ph", state.language),
                          text: $testTo)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                Button(L10n.t("ns.ml.test", state.language)) { test() }
                    .font(.caption2.bold()).foregroundStyle(Theme.brandA)
                    .disabled(busy || testTo.isEmpty)
            }
            if let testSentTo {
                Text("✓ \(testSentTo)")
                    .font(.caption2).foregroundStyle(Theme.green)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        settings = try? await ApiClient.shared.mailSettings()
        if let settings {
            if host.isEmpty { host = settings.host ?? "" }
            port = String(settings.port)
            if username.isEmpty { username = settings.username ?? "" }
            if sender.isEmpty { sender = settings.sender ?? "" }
            if publicUrl.isEmpty { publicUrl = settings.public_url }
        }
    }

    private func save() {
        busy = true; error = nil
        Task {
            do {
                settings = try await ApiClient.shared.saveMailSettings(
                    host: host.trimmingCharacters(in: .whitespaces),
                    port: Int(port) ?? 587,
                    username: username.trimmingCharacters(in: .whitespaces),
                    password: password,
                    sender: sender.trimmingCharacters(in: .whitespaces),
                    publicUrl: publicUrl.trimmingCharacters(in: .whitespaces))
                password = ""
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func clear() {
        busy = true; error = nil
        Task {
            do {
                settings = try await ApiClient.shared.clearMailSettings()
                host = ""; username = ""; password = ""; sender = ""
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func test() {
        busy = true; error = nil; testSentTo = nil
        Task {
            do {
                let out = try await ApiClient.shared.testMail(
                    to: testTo.trimmingCharacters(in: .whitespaces))
                if out.sent { testSentTo = out.to }
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
