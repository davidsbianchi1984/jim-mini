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

    private let d = UserDefaults.standard

    init() {
        uid = d.string(forKey: "jim.uid")
        token = d.string(forKey: "jim.token")
        displayName = d.string(forKey: "jim.name") ?? ""
        language = d.string(forKey: "jim.lang") ?? "en"
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

    func rememberLanguage(_ code: String) {
        language = code
        d.set(code, forKey: "jim.lang")
    }
}
