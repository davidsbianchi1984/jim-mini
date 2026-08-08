import SwiftUI

/// What this deployment can and cannot reach.
///
/// Offline mode was settable and unreadable: the flag existed, the guarantee
/// was written in a docstring, and there was nowhere on a phone to see the
/// answer.
///
///     asked     can the guarantee be turned on
///     mattered  can it be checked
///
/// Read-only on purpose. The posture is set in the deployment's environment,
/// not by somebody signed into the app — a switch here would imply otherwise.
struct OfflinePostureCard: View {
    @EnvironmentObject var state: AppState
    @State private var posture: OfflinePosture?

    var body: some View {
        Group {
            if let posture {
                VStack(alignment: .leading, spacing: 6) {
                    Text(L10n.t("offline.title", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    Text(posture.offline
                         ? L10n.t("offline.on", state.language) : L10n.t("offline.off", state.language))
                        .font(.caption.bold())
                        .foregroundStyle(posture.offline ? Theme.green : Theme.t2)
                    Text(posture.local_destinations_allowed)
                        .font(.caption2).foregroundStyle(Theme.t2)
                    ForEach(posture.guarantees, id: \.self) { line in
                        Text("• " + line).font(.caption2).foregroundStyle(Theme.t2)
                    }
                }
            }
        }
        .task {
            posture = try? await ApiClient.shared.offlineStatus()
        }
    }
}
