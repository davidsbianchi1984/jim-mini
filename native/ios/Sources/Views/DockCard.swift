import SwiftUI

/// The dock in the corner: which face the hide-away pane shows, where it
/// sits, and whether it is open at all. The pane never acts — `acts` is
/// false by construction — and a forced state (an active alarm) is shown
/// beside the owner's own choice rather than overwriting it. Console door
/// since 0.19.x; this is the phone's.
struct DockCard: View {
    @EnvironmentObject var state: AppState
    @State private var vocabulary: DockVocabulary?
    @State private var dock: DockState?
    @State private var detail: DockFace?
    @State private var place: DockWhere?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.dk.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let dock {
                Text(L10n.t("ns.dk.line", state.language)
                        .replacingOccurrences(of: "{corner}",
                                              with: dock.corner)
                        .replacingOccurrences(of: "{state}", with: dock.state)
                        .replacingOccurrences(of: "{forced}",
                                              with: dock.forced ? " !" : "")
                        .replacingOccurrences(of: "{face}",
                                              with: dock.face ?? ""))
                    .font(.caption2).foregroundStyle(Theme.t2)
                if let why = dock.why {
                    Text(why).font(.caption2).foregroundStyle(Theme.amber)
                }
            }

            if let vocabulary, let dock {
                // Which face it shows. Per-surface faces are configured
                // only — their detail needs a particular surface to be
                // about, which this card is not.
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(vocabulary.faces.keys.sorted(), id: \.self) { name in
                            Button(name) {
                                configure(face: name)
                                if !vocabulary.per_surface.contains(name) {
                                    showFace(name)
                                }
                            }
                            .font(.caption2)
                            .foregroundStyle(dock.face == name ? .white
                                                               : Theme.t2)
                            .padding(.horizontal, 10).padding(.vertical, 6)
                            .background(dock.face == name ? Theme.brandA
                                                          : Theme.scrBot)
                            .clipShape(Capsule())
                            .disabled(busy)
                        }
                    }
                }
                HStack(spacing: 8) {
                    ForEach(vocabulary.states.keys.sorted(), id: \.self) { name in
                        Button(name) { configure(state: name) }
                            .font(.caption2)
                            .foregroundStyle(dock.wanted == name ? .white
                                                                 : Theme.t2)
                            .padding(.horizontal, 10).padding(.vertical, 6)
                            .background(dock.wanted == name ? Theme.brandA
                                                            : Theme.scrBot)
                            .clipShape(Capsule())
                            .disabled(busy)
                    }
                }
                Button(L10n.t("ns.dk.move", state.language)) {
                    if let other = vocabulary.corners.keys.first(
                        where: { $0 != dock.corner }) {
                        configure(corner: other)
                    }
                }
                .font(.caption2).foregroundStyle(Theme.brandA)
                .disabled(busy)
            }

            if let detail {
                VStack(alignment: .leading, spacing: 2) {
                    Text(detail.face).font(.caption.bold())
                        .foregroundStyle(Theme.txt)
                    Text(detail.shows).font(.caption2)
                        .foregroundStyle(Theme.t2)
                    if let place {
                        Text("→ \(place.title) · \(place.screen)")
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                }
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        vocabulary = try? await ApiClient.shared.dockVocabulary()
        if let uid = state.uid, let token = state.token {
            dock = try? await ApiClient.shared.dockState(uid: uid,
                                                         token: token)
        }
    }

    private func configure(corner: String? = nil, state newState: String? = nil,
                           face: String? = nil) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                dock = try await ApiClient.shared.configureDock(
                    uid: uid, token: token, corner: corner, state: newState,
                    face: face)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func showFace(_ name: String) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            detail = try? await ApiClient.shared.dockFace(uid: uid,
                                                          token: token,
                                                          name: name)
            place = try? await ApiClient.shared.dockWhere(face: name)
        }
    }
}
