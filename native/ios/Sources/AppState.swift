import SwiftUI

/// Holds the enrolled identity + token, persisted to UserDefaults so the app
/// resumes signed-in. Drives the root switch between Welcome and the tab bar.
@MainActor
final class AppState: ObservableObject {
    @Published var uid: String?
    @Published var token: String?
    @Published var displayName: String = ""

    private let d = UserDefaults.standard

    init() {
        uid = d.string(forKey: "jim.uid")
        token = d.string(forKey: "jim.token")
        displayName = d.string(forKey: "jim.name") ?? ""
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
        ["jim.uid", "jim.token", "jim.name"].forEach { d.removeObject(forKey: $0) }
    }
}
