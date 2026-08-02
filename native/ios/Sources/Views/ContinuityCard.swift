import SwiftUI

/// What the Guardian carries between sessions, on the phone.
///
/// The profile on the console is a snapshot somebody rebuilds. This is the
/// part that moves on its own — and until this release nothing moved at all,
/// because the only thing that built the derived artifact was a button in a
/// desktop console that a phone-only user never sees.
///
///     asked     can a user-specific model be built from the history
///     mattered  does anything ever build it
///
/// Read-only except for forgetting it. Every derived thing in this product
/// has to be droppable by the person it was derived from.
struct ContinuityCard: View {
    @EnvironmentObject var state: AppState
    @State private var carried: ContinuityState?

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(L10n.t("cont.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let carried, carried.built, let vector = carried.vector {
                HStack {
                    Text("\(carried.observations ?? 0) "
                         + L10n.t("cont.observations", state.language))
                        .font(.caption.bold()).foregroundStyle(Theme.txt)
                    Spacer()
                    Button(L10n.t("cont.forget", state.language)) { forget() }
                        .font(.caption).tint(Theme.red)
                }
                Text(carried.conditioning == true
                     ? L10n.t("cont.shaping", state.language)
                     : L10n.t("cont.not_yet", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                ForEach(vector.keys.sorted(), id: \.self) { dim in
                    Text("\(dim): \(Int((vector[dim] ?? 0) * 100))%"
                         + (carried.meanings?[dim].map { " — \($0)" } ?? ""))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                if let method = carried.method {
                    Text(method).font(.caption2).foregroundStyle(Theme.t2)
                }
            } else {
                Text(carried?.note ?? L10n.t("cont.nothing", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            if let carries = carried?.carries {
                Text(carries).font(.caption2).foregroundStyle(Theme.t2)
            }
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.userId, let token = state.token else { return }
        carried = try? await Api.shared.continuity(uid: uid, token: token)
    }

    private func forget() {
        guard let uid = state.userId, let token = state.token else { return }
        Task {
            try? await Api.shared.forgetContinuity(uid: uid, token: token)
            await load()
        }
    }
}
