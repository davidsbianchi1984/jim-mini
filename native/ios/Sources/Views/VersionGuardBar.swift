import SwiftUI

/// The version handshake, made visible on the phone.
///
/// A stale backend from an older install answers `/health` perfectly well
/// and then serves an older API, so the app looks alive while every newer
/// screen answers "Not Found" with no explanation. The console has said so
/// since the mismatch first cost somebody an evening; this shell could be
/// pointed at the same stale address — `ApiClient.setBase` exists precisely
/// so it can be — and said nothing at all.
///
///     asked     is the backend reachable
///     mattered  is it the backend this build was written against
///
/// Reachability was the only question any shell asked. `/health` has carried
/// the answer to the second one the whole time and three shells decoded it
/// away.
///
/// Dismissible, because a person who knows and is working anyway should not
/// have to read it on every screen; and per-launch rather than remembered,
/// because the condition is real until the address or the backend changes,
/// and a permanently silenced warning about a broken deployment is worse
/// than none.
struct VersionGuardBar: View {
    @EnvironmentObject var state: AppState
    @State private var backend: String?
    @State private var dismissed = false

    var body: some View {
        Group {
            if let backend, !dismissed, backend != Problems.appVersion {
                HStack(alignment: .top, spacing: 10) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(Theme.amber)
                    VStack(alignment: .leading, spacing: 4) {
                        Text(L10n.t("vg.title", state.language))
                            .font(.subheadline.bold())
                        Text(String(format: L10n.t("vg.body", state.language),
                                    Problems.appVersion, ApiClient.shared.base.absoluteString,
                                    backend))
                            .font(.caption)
                        Text(L10n.t("vg.fix", state.language)).font(.caption2)
                            .foregroundColor(Theme.t3)
                    }
                    Spacer(minLength: 0)
                    Button { dismissed = true } label: {
                        Image(systemName: "xmark")
                    }
                    .accessibilityLabel(L10n.t("vg.dismiss", state.language))
                }
                .padding(12)
                .background(Theme.card)
                .cornerRadius(10)
                .padding(.horizontal, 12)
                .accessibilityElement(children: .contain)
            }
        }
        .task {
            // An unreachable backend is the connection panel's story, not
            // this one: a version guard that also complained about being
            // offline would cry wolf every time a phone changed network.
            guard let h = try? await ApiClient.shared.health() else { return }
            // A backend too old to carry the field is the loudest case there
            // is, so it gets a name rather than being read as agreement.
            backend = h.version ?? L10n.t("vg.ancient", state.language)
        }
    }
}
