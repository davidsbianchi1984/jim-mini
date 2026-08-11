import SwiftUI

/// This sitting: a named login session, so any device that starts one
/// resumes the same conversational thread — including a thread begun with a
/// QRME specialist from another product. Console door since 0.14.x; this is
/// the phone's.
struct SessionsCard: View {
    @EnvironmentObject var state: AppState
    @State private var session: SessionStarted?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("att.sit", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            HStack(spacing: 10) {
                Button(L10n.t("att.sit.start", state.language)) { start() }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(busy)
                Button(L10n.t("att.sit.end", state.language)) { end() }
                    .font(.caption2).foregroundStyle(Theme.red)
                    .disabled(busy || session == nil)
            }
            if let session {
                Text(L10n.t("att.sit.prior", state.language)
                        .replacingOccurrences(of: "{id}", with: session.id)
                        .replacingOccurrences(
                            of: "{n}", with: String(session.prior_sessions)))
                    .font(.caption2).foregroundStyle(Theme.t2)
                if let memory = session.memory {
                    Text(memory).font(.caption2).foregroundStyle(Theme.t3)
                }
                if let continuity = session.continuity {
                    ForEach(Array(continuity.recent_turns.enumerated()),
                            id: \.offset) { _, turn in
                        Text("\(turn.role): \(turn.content)")
                            .font(.caption2).foregroundStyle(Theme.t2)
                            .lineLimit(2)
                    }
                    Text(continuity.note)
                        .font(.caption2).foregroundStyle(Theme.t3)
                }
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
    }

    private func start() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                session = try await ApiClient.shared.startSession(
                    uid: uid, token: token, device: "iphone")
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func end() {
        guard let uid = state.uid, let token = state.token,
              let sitting = session else { return }
        busy = true; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.endSession(
                    uid: uid, token: token, sessionId: sitting.id)
                session = nil
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
