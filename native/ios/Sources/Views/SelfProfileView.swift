import SwiftUI

/// The one QRME profile that is this person.
///
/// Every other tandem surface in this shell reaches somebody else's profile —
/// a clinician's specialist, the care team's org. This reaches their own: the
/// `self` profile that speaks *as* them, and that answers strangers.
///
/// Built around the preview rather than around the switches, because the
/// switches are not the decision. `docs/tandem.md` says what may cross; this
/// shows exactly what would, in the strings that would go, before it does.
/// A phone is what somebody has with them when they change their mind, which
/// is why this is here and not only on the desktop console.
struct SelfProfileSection: View {
    @EnvironmentObject var state: AppState
    @State private var status: SelfProfileStatus?
    @State private var preview: SelfProfilePreview?
    @State private var profileId = ""
    @State private var ownerToken = ""
    @State private var note: String?
    @State private var busy = false

    private let categories = ["language", "wellbeing", "conditions",
                              "medication", "continuity"]

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 8) {
                Text(L10n.t("self.title", state.language)).font(.headline)
                    .foregroundStyle(Theme.txt)
                ProblemReportingCard()
                ContinuityCard()
                Text(L10n.t("self.lead", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
            }.card()

            if status?.linked != true {
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("self.link", state.language)).font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    Text(L10n.t("self.paste", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    TextField(L10n.t("self.profile_id", state.language), text: $profileId)
                        .textFieldStyle(.roundedBorder)
                    SecureField(L10n.t("self.owner_token", state.language), text: $ownerToken)
                        .textFieldStyle(.roundedBorder)
                    Button(L10n.t("self.link_button", state.language)) { link() }
                        .disabled(busy || profileId.isEmpty || ownerToken.isEmpty)
                }.card()
            } else {
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("self.may_know", state.language)).font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    Text(L10n.t("self.until_tick", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    ForEach(categories, id: \.self) { key in
                        Toggle(key, isOn: Binding(
                            get: { status?.consented.contains(key) ?? false },
                            set: { on in setConsent(key, on) }))
                            .disabled(busy)
                            .font(.caption).foregroundStyle(Theme.txt)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("self.exactly", state.language)).font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    if preview?.empty == true {
                        Text(L10n.t("self.nothing_ticked", state.language))
                            .font(.caption).foregroundStyle(Theme.t2)
                    } else {
                        Text((preview?.consented ?? []).joined(separator: " · "))
                            .font(.caption.monospaced()).foregroundStyle(Theme.txt)
                    }
                    Text(L10n.t("self.message_itself", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Button(L10n.t("self.send", state.language)) { brief() }
                        .disabled(busy || preview?.empty == true)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("self.stop", state.language)).font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    Text(L10n.t("self.unlink_note", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    Button(L10n.t("self.unlink", state.language)) { unlink() }
                        .disabled(busy).foregroundStyle(Theme.red)
                }.card()
            }

            if let note {
                Text(note).font(.caption).foregroundStyle(Theme.t2)
            }
        }
        .task { await refresh() }
    }

    private func refresh() async {
        guard let uid = state.uid, let token = state.token else { return }
        status = try? await ApiClient.shared.selfProfile(uid: uid, token: token)
        preview = try? await ApiClient.shared.previewSelfProfile(uid: uid, token: token)
    }

    private func run(_ work: @escaping () async throws -> Void,
                     _ said: String) {
        busy = true
        Task {
            do { try await work(); note = said }
            catch { note = error.localizedDescription }
            await refresh()
            busy = false
        }
    }

    private func link() {
        guard let uid = state.uid, let token = state.token else { return }
        run({ _ = try await ApiClient.shared.linkSelfProfile(
                uid: uid, token: token, profileId: profileId,
                ownerToken: ownerToken) },
            L10n.t("self.linked_note", state.language))
    }

    private func setConsent(_ key: String, _ on: Bool) {
        guard let uid = state.uid, let token = state.token else { return }
        var next = status?.consented ?? []
        if on { next.append(key) } else { next.removeAll { $0 == key } }
        run({ _ = try await ApiClient.shared.consentSelfProfile(
                uid: uid, token: token, categories: next) },
            L10n.t("self.saved", state.language))
    }

    private func brief() {
        guard let uid = state.uid, let token = state.token else { return }
        run({ _ = try await ApiClient.shared.briefSelfProfile(uid: uid, token: token) },
            L10n.t("self.sent", state.language))
    }

    private func unlink() {
        guard let uid = state.uid, let token = state.token else { return }
        run({ try await ApiClient.shared.unlinkSelfProfile(uid: uid, token: token) },
            L10n.t("self.unlinked", state.language))
    }
}
