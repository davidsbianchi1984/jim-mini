import SwiftUI

/// Tell it what you did: an ordinary activity is context, not a reading —
/// it gives the Guardian the why behind a moved heart rate before it has to
/// guess one. Console door (Aims) since 0.30.x; this is the phone's.
struct ActivityCard: View {
    @EnvironmentObject var state: AppState
    @State private var activity = ""
    @State private var note = ""
    @State private var watch: ActivityWatch?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("aim.activity", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("aim.activity.pitch", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            TextField(L10n.t("aim.activity.ph", state.language),
                      text: $activity)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            TextField(L10n.t("brg.told.note.ph", state.language), text: $note)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Button(L10n.t("aim.activity.log", state.language)) { log() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy || activity.isEmpty)
            if let intervention = watch?.intervention {
                // The proactive voice: it noticed a struggle building and
                // spoke before being asked.
                Text(intervention.content)
                    .font(.caption2).foregroundStyle(Theme.amber)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
    }

    private func log() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                watch = try await ApiClient.shared.observeActivity(
                    uid: uid, token: token,
                    activity: activity.trimmingCharacters(in: .whitespaces),
                    note: note)
                activity = ""; note = ""
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
