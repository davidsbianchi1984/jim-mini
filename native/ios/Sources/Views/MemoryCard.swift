import SwiftUI

/// Remembered moments: the transparency half of the coach's long-term
/// memory (jim/recall.py). What the coach can find again — sealed in the
/// vault, searched by meaning — read back for the person it is about, with
/// a forget button beside every line. Every derived thing in this product
/// has to be visible to the person it was derived from, and droppable by
/// them; the continuity card above holds that rule for the attention
/// vector, and this card holds it for the content.
struct MemoryCard: View {
    @EnvironmentObject var state: AppState
    @State private var shelf: MemoryShelf?

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(L10n.t("mem.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("mem.lead", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            if let shelf {
                if !shelf.readable {
                    Text(L10n.t("mem.unreadable", state.language))
                        .font(.caption2).foregroundStyle(Theme.amber)
                }
                if shelf.memories.isEmpty {
                    Text(L10n.t("cont.nothing", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                ForEach(shelf.memories, id: \.ref) { m in
                    HStack(alignment: .top) {
                        Text(m.kind).font(.caption2.monospaced())
                            .foregroundStyle(Theme.t2)
                        Text(m.line ?? "·").font(.caption2)
                            .foregroundStyle(Theme.txt)
                        Spacer()
                        Button(L10n.t("day.forget", state.language)) {
                            forget(m)
                        }.font(.caption2).tint(Theme.red)
                    }
                }
            }
        }
        .task { await load() }
    }

    private func load() async {
        guard let token = state.token, let uid = state.uid else { return }
        shelf = try? await ApiClient.shared.memoryShelf(uid: uid, token: token)
    }

    private func forget(_ m: MemoryMoment) {
        guard let token = state.token, let uid = state.uid else { return }
        Task {
            _ = try? await ApiClient.shared.forgetMemory(
                uid: uid, kind: m.kind, ref: m.ref, token: token)
            await load()
        }
    }
}
