import SwiftUI

/// The task window — *which agent is running, which tasks are still running*,
/// asked for twice and answerable until now only by visiting five different
/// screens and knowing which five.
///
/// The gathering is not done here: one route hands back the whole window,
/// because four shells each deciding what counts as still running is four
/// chances to disagree invisibly (see jim/underway.py). What this card does is
/// say the closed-set `kind` and `why` words in the reader's own language,
/// which is the half that cannot be done on the server.
///
/// It opens nothing. Every row names the thing it came from, and the screen
/// that already owns that capability is where you act on it — a window over
/// everything that could also act on everything would quietly be the widest
/// door in the product.
struct UnderwayCard: View {
    @EnvironmentObject var state: AppState
    @State private var win: UnderwayWindow?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("und.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let w = win {
                // Stated by the server rather than inferred from an empty
                // list, so this shell cannot disagree with the other three.
                if w.quiet {
                    Text(L10n.t("und.quiet", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                ForEach(Array(w.underway.enumerated()), id: \.offset) { _, r in
                    VStack(alignment: .leading, spacing: 2) {
                        Text(L10n.t("und.kind.\(r.kind)", state.language))
                            .font(.caption).foregroundStyle(Theme.txt)
                        // One of the product's own vocabulary words — a
                        // monitor's name, a call's route — beside what the
                        // *person* wrote, printed as they wrote it.
                        ForEach([r.term, r.words].compactMap { $0 },
                                id: \.self) { line in
                            Text(line).font(.caption2)
                                .foregroundStyle(Theme.t2)
                        }
                        // Only said where it adds something: `open` and `on`
                        // restate the kind, and the other four are news.
                        if r.why != "open" && r.why != "on" {
                            Text(L10n.t("und.why.\(r.why)", state.language))
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }
                }
                // Finished, not running — a list of its own rather than more
                // rows above. These strings arrive already composed in
                // English from `pipeline.curriculum`, as they do on the Coach
                // screen; that is the existing shape of the ledger and not
                // something this window adds.
                if !w.today.isEmpty {
                    Text(L10n.t("und.today", state.language))
                        .font(.caption.bold()).foregroundStyle(Theme.txt)
                    ForEach(w.today, id: \.id) { e in
                        Text(e.topic).font(.caption2)
                            .foregroundStyle(Theme.t2)
                    }
                }
                // Shown only where the unattended pass is allowed at all: a
                // budget line on an account that never permitted it answers a
                // question nobody asked.
                if w.spend.permitted {
                    Text(L10n.fill("und.spend", state.language,
                                   ["n": String(w.spend.spent_today),
                                    "daily": String(w.spend.daily)]))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
            }
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        win = try? await ApiClient.shared.underway(uid: uid, token: token)
    }
}
