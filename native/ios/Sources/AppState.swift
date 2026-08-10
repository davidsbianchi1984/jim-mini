import SwiftUI

/// Holds the enrolled identity + token, persisted to UserDefaults so the app
/// resumes signed-in. Drives the root switch between Welcome and the tab bar.
@MainActor
final class AppState: ObservableObject {
    @Published var uid: String?
    @Published var token: String?
    @Published var displayName: String = ""
    // The user's chosen language also drives the app chrome via L10n.
    @Published var language = "en"


    /// The person's own model key, held on this device only and sent per
    /// request as `x-llm-api-key`.
    ///
    /// The console has offered this since 0.4.3 and the phones never did — so
    /// somebody who set their key in the console had it used there and the
    /// deployment's key used here, on the same profile, with nothing saying
    /// so. Never in the account and never on the wire except as the header.
    @Published var llmKey = ""
    @Published var signupKey = ""

    private let d = UserDefaults.standard

    init() {
        uid = d.string(forKey: "jim.uid")
        token = d.string(forKey: "jim.token")
        displayName = d.string(forKey: "jim.name") ?? ""
        language = d.string(forKey: "jim.lang") ?? "en"
        llmKey = d.string(forKey: "jim.llmKey") ?? ""
        let held = llmKey
        Task { await ApiClient.shared.useLlmKey(held) }
        signupKey = d.string(forKey: "jim.signupKey") ?? ""
        let invite = signupKey
        Task { await ApiClient.shared.useSignupKey(invite) }
    }

    var isEnrolled: Bool { uid != nil && token != nil }

    func signIn(_ r: EnrollResult) {
        uid = r.id; token = r.user_token; displayName = r.display_name
        d.set(r.id, forKey: "jim.uid")
        d.set(r.user_token, forKey: "jim.token")
        d.set(r.display_name, forKey: "jim.name")
    }

    func signOut() {
        uid = nil; token = nil; displayName = ""
        ["jim.uid", "jim.token", "jim.name", "jim.lang"].forEach { d.removeObject(forKey: $0) }
    }

    /// Store or clear it. An empty string is the clear: there is no flag to
    /// leave switched on by mistake, and no key means the deployment's.
    func rememberLlmKey(_ key: String) {
        let trimmed = key.trimmingCharacters(in: .whitespacesAndNewlines)
        llmKey = trimmed
        if trimmed.isEmpty { d.removeObject(forKey: "jim.llmKey") }
        else { d.set(trimmed, forKey: "jim.llmKey") }
        Task { await ApiClient.shared.useLlmKey(trimmed) }
    }

    /// The deployment invite key, same clearing rule: empty means none, and
    /// a deployment that never gated signup never needs one.
    func rememberSignupKey(_ key: String) {
        let trimmed = key.trimmingCharacters(in: .whitespacesAndNewlines)
        signupKey = trimmed
        if trimmed.isEmpty { d.removeObject(forKey: "jim.signupKey") }
        else { d.set(trimmed, forKey: "jim.signupKey") }
        Task { await ApiClient.shared.useSignupKey(trimmed) }
    }

    func rememberLanguage(_ code: String) {
        language = code
        d.set(code, forKey: "jim.lang")
    }
}
