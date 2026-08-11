import SwiftUI

/// The account the phones never had: the shells enrolled anonymously while
/// the console signed up with an email, verified the inbox, recovered lost
/// passwords and opened the "Sign in with ..." doors. Same routes, this
/// screen. Console door since 0.4.x; this is the phone's.
struct AccountCard: View {
    @EnvironmentObject var state: AppState
    @Environment(\.openURL) private var openURL
    let language: String
    @State private var mode = "up"           // up | in | reset
    @State private var email = ""
    @State private var password = ""
    @State private var name = ""
    @State private var code = ""
    @State private var consent = false
    @State private var pending = false       // signed up; the code is out
    @State private var doors: [OAuthProviderRow] = []
    @State private var notice: String?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 8) {
                chip("up", L10n.t("onb.create", language))
                chip("in", L10n.t("onb.signin", language))
                chip("reset", L10n.t("onb.forgot", language))
            }

            field(L10n.t("onb.email", language)) {
                TextField(L10n.t("onb.email.ph", language), text: $email)
                    .textInputAutocapitalization(.never)
                    .keyboardType(.emailAddress)
            }

            if mode == "up" && !pending {
                field(L10n.t("onb.yourname", language)) {
                    TextField("", text: $name)
                }
                field(L10n.t("onb.password.min", language)) {
                    SecureField("", text: $password)
                }
                Toggle(isOn: $consent) {
                    Text(L10n.t("onb.consent", language))
                        .font(.caption2).foregroundStyle(Theme.txt)
                }.tint(Theme.green)
                Button(L10n.t("onb.create", language)) { signup() }
                    .buttonStyle(Primary(enabled: !busy && consent
                                         && !email.isEmpty && !password.isEmpty
                                         && !name.isEmpty))
                    .disabled(busy || !consent || email.isEmpty
                              || password.isEmpty || name.isEmpty)
            }

            if mode == "up" && pending {
                Text("\(L10n.t("onb.verify.sent", language)) \(email)")
                    .font(.caption2).foregroundStyle(Theme.t2)
                Text(L10n.t("onb.verify.type", language))
                    .font(.caption2).foregroundStyle(Theme.t3)
                field(L10n.t("onb.code", language)) {
                    TextField("123456", text: $code).keyboardType(.numberPad)
                }
                HStack {
                    Button(L10n.t("onb.signin", language)) { verify() }
                        .buttonStyle(Primary(enabled: !busy && !code.isEmpty))
                        .disabled(busy || code.isEmpty)
                    Button(L10n.t("onb.code.resend", language)) { resend() }
                        .font(.caption2).foregroundStyle(Theme.brandA)
                        .disabled(busy)
                }
            }

            if mode == "in" {
                field(L10n.t("onb.password.min", language)) {
                    SecureField("", text: $password)
                }
                Button(L10n.t("onb.signin", language)) { signin() }
                    .buttonStyle(Primary(enabled: !busy && !email.isEmpty
                                         && !password.isEmpty))
                    .disabled(busy || email.isEmpty || password.isEmpty)
            }

            if mode == "reset" {
                Text(L10n.t("onb.reset.hint", language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                Button(L10n.t("onb.reset.send", language)) { requestReset() }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy || email.isEmpty)
                field(L10n.t("onb.reset.code", language)) {
                    TextField("123456", text: $code).keyboardType(.numberPad)
                }
                field(L10n.t("onb.password.min", language)) {
                    SecureField("", text: $password)
                }
                Button(L10n.t("onb.reset.send", language)) { reset() }
                    .buttonStyle(Primary(enabled: !busy && !email.isEmpty
                                         && !code.isEmpty && !password.isEmpty))
                    .disabled(busy || email.isEmpty || code.isEmpty
                              || password.isEmpty)
            }

            if !doors.isEmpty && mode != "reset" {
                ForEach(doors, id: \.provider) { door in
                    Button(signWith(door)) {
                        if door.configured { open(door.provider) }
                    }
                    .font(.caption2)
                    .foregroundStyle(door.configured ? Theme.brandA : Theme.t3)
                    .disabled(busy || !door.configured)
                }
            }

            if let notice {
                Text(notice).font(.caption2).foregroundStyle(Theme.t2)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task {
            doors = (try? await ApiClient.shared.oauthProviders())?
                .providers ?? []
        }
    }

    private func chip(_ value: String, _ label: String) -> some View {
        Button(label) { mode = value; error = nil; notice = nil }
            .font(.caption2)
            .foregroundStyle(mode == value ? .white : Theme.t2)
            .padding(.horizontal, 10).padding(.vertical, 6)
            .background(mode == value ? Theme.brandA : Theme.scrBot)
            .clipShape(Capsule())
    }

    private func field<Content: View>(_ label: String,
                                      @ViewBuilder _ content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label).font(.caption2).foregroundStyle(Theme.t2)
            content()
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
        }
    }

    private func signWith(_ door: OAuthProviderRow) -> String {
        let label = L10n.t("onb.signwith", language)
            .replacingOccurrences(of: "{mode}",
                                  with: L10n.t(mode == "up" ? "onb.mode.up"
                                                            : "onb.mode.in",
                                               language))
            .replacingOccurrences(of: "{provider}", with: door.name)
        return door.configured
            ? label : label + L10n.t("onb.oauth.absent", language)
    }

    private func run(_ work: @escaping () async throws -> Void) {
        busy = true; error = nil; notice = nil
        Task {
            do { try await work() }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func signup() {
        run {
            let r = try await ApiClient.shared.signup(
                email: email.trimmingCharacters(in: .whitespaces),
                password: password, name: name, language: language)
            if r.verified, let id = r.id, let token = r.user_token {
                state.signIn(EnrollResult(id: id,
                                          display_name: r.display_name ?? name,
                                          user_token: token))
            } else {
                pending = true
                notice = r.code_delivery
            }
        }
    }

    private func verify() {
        run {
            let r = try await ApiClient.shared.verifyEmail(
                email: email.trimmingCharacters(in: .whitespaces),
                code: code.trimmingCharacters(in: .whitespaces))
            state.signIn(r)
        }
    }

    private func resend() {
        run {
            let r = try await ApiClient.shared.resendCode(
                email: email.trimmingCharacters(in: .whitespaces))
            notice = r.code_delivery
        }
    }

    private func signin() {
        run {
            let r = try await ApiClient.shared.signin(
                email: email.trimmingCharacters(in: .whitespaces),
                password: password)
            state.signIn(EnrollResult(id: r.user_id,
                                      display_name: r.display_name ?? r.email,
                                      user_token: r.user_token))
        }
    }

    private func requestReset() {
        run {
            let r = try await ApiClient.shared.requestPasswordReset(
                email: email.trimmingCharacters(in: .whitespaces))
            notice = r.code_delivery
        }
    }

    private func reset() {
        run {
            _ = try await ApiClient.shared.resetPassword(
                email: email.trimmingCharacters(in: .whitespaces),
                code: code.trimmingCharacters(in: .whitespaces),
                newPassword: password)
            // Every old session died with the old password; sign in fresh.
            code = ""; mode = "in"
            notice = L10n.t("onb.signin", language)
        }
    }

    /// Open the provider's page in the system browser, then poll the claim.
    /// The phone never sees the provider conversation — only whether the
    /// state it minted was honoured.
    private func open(_ provider: String) {
        busy = true; error = nil
        Task {
            do {
                let started = try await ApiClient.shared.oauthStart(
                    provider: provider)
                if let url = URL(string: started.url) { openURL(url) }
                for _ in 0..<40 {
                    try await Task.sleep(nanoseconds: 3_000_000_000)
                    let claim = try await ApiClient.shared.oauthClaim(
                        state: started.state)
                    if claim.ready {
                        if let id = claim.id, let token = claim.user_token {
                            state.signIn(EnrollResult(
                                id: id,
                                display_name: claim.display_name
                                    ?? (claim.email ?? ""),
                                user_token: token))
                        }
                        break
                    }
                }
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}

/// The Welcome screen's primary-button look, shared by the card's actions.
private struct Primary: ButtonStyle {
    let enabled: Bool
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.caption.bold()).foregroundStyle(.white)
            .padding(.horizontal, 12).padding(.vertical, 8)
            .background(Theme.brandA).clipShape(Capsule())
            .opacity(enabled ? 1 : 0.5)
    }
}
