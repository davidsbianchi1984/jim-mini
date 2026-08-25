import SwiftUI

/// Who stands on the far end of the ladder — the person a letter really
/// reaches when JIM decides to notify a contact. Console door since the
/// ladder was built; this is the phone's, and it says the same things:
/// the address or the honest refusal, never the token.
///
///     asked     can a phone say who is on the far end
///     mattered  the ladder ends at a person on every client
struct FarEndCard: View {
    @EnvironmentObject var state: AppState
    @State private var farend: FarEndOut?
    @State private var email = ""
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("nfe.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let farend {
                if farend.configured {
                    Text(farend.address ?? "")
                        .font(.caption2).foregroundStyle(Theme.green)
                } else if let note = farend.note {
                    // The backend's refusal sentence, already in the
                    // reader's language — not a wording of this shell's.
                    Text(note).font(.caption2).foregroundStyle(Theme.t2)
                }
            }
            TextField(L10n.t("nfe.email.ph", state.language), text: $email)
                .keyboardType(.emailAddress)
                .textInputAutocapitalization(.never)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            HStack {
                Button(L10n.t("nfe.save", state.language)) { save() }
                    .font(.caption.bold()).foregroundStyle(Theme.brandA)
                    .disabled(busy || email.trimmingCharacters(
                        in: .whitespaces).isEmpty)
                Button(L10n.t("nfe.clear", state.language)) { clear() }
                    .font(.caption).foregroundStyle(Theme.t2)
                    .disabled(busy)
            }
            Text(L10n.t("nfe.pitch", state.language))
                .font(.caption2).foregroundStyle(Theme.t3)
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        farend = try? await ApiClient.shared.farEnd(uid: uid, token: token)
    }

    private func save() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                // Consent settles in the same motion, as the console's
                // save does — the button's own words carry the condition.
                farend = try await ApiClient.shared.setFarEnd(
                    uid: uid, email: email.trimmingCharacters(in: .whitespaces),
                    consent: true, token: token)
                email = ""
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func clear() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                // Clearing returns the escalation to its honest refusal
                // rather than to silence — the route's own reasoning.
                farend = try await ApiClient.shared.setFarEnd(
                    uid: uid, email: nil, consent: nil, token: token)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
