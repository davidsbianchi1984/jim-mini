import SwiftUI

/// The presence, in the pocket: the coach that speaks first.
///
/// A companion in the parts worth having — it starts things, it notices
/// without being asked, it reports its own change, and it keeps handing the
/// reader people who are not it.
///
/// The order on this screen is deliberate. **What it will not be comes
/// first**, above any warm sentence, because a guardian that is charming
/// before it is honest has the order wrong — and because this product enrols
/// children, whose guardians should be able to read the refusal without
/// scrolling for it.
///
/// Nothing here decides anything. Whether it speaks, about what, and why, are
/// all the backend's, read from six areas of this person's own history with
/// no network and no model. A phone in a tunnel still gets its day.
struct PresenceView: View {
    @EnvironmentObject var state: AppState
    @State private var who: PresenceWho?
    @State private var day: PresenceDay?
    @State private var base: PresenceBaseline?
    @State private var surf: PresenceSurfaces?
    @State private var reach: PresenceReach?
    @State private var grew: PresenceGrowth?
    @State private var spoken: [String: String] = [:]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(L10n.t("presence.tab", state.language))
                    .font(.title2.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("presence.sub", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)

                // Honest before warm.
                if let w = who {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(L10n.t("presence.what", state.language))
                            .font(.headline).foregroundStyle(Theme.txt)
                        Text(w.says).font(.subheadline).foregroundStyle(Theme.txt)
                        Text(L10n.t("presence.will.not", state.language))
                            .font(.caption).foregroundStyle(Theme.t2)
                        ForEach(Array(w.boundaries.keys.sorted()), id: \.self) { key in
                            if let b = w.boundaries[key] {
                                Text(b.says).font(.caption2).foregroundStyle(Theme.t3)
                            }
                        }
                        Text(w.note).font(.caption2).foregroundStyle(Theme.t3)
                    }.card()
                }

                if let d = day {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(L10n.t("presence.today", state.language))
                            .font(.headline).foregroundStyle(Theme.txt)
                        Text(L10n.t("presence.offline", state.language))
                            .font(.caption2).foregroundStyle(Theme.t3)
                        ForEach(d.beats, id: \.slot) { b in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(b.slot).font(.caption.bold())
                                    .foregroundStyle(Theme.brandA)
                                Text(spoken[b.slot] ?? line(b))
                                    .font(.subheadline).foregroundStyle(Theme.txt)
                                // Why it said this. A presence that cannot
                                // show its reason is one nobody can argue with.
                                ForEach(b.because, id: \.self) { why in
                                    Text(why).font(.caption2)
                                        .foregroundStyle(Theme.t3)
                                }
                                if b.speak {
                                    HStack {
                                        Button(L10n.t("presence.tab", state.language)) {
                                            Task { await hear(b.slot) }
                                        }.font(.caption)
                                        Button(L10n.t("presence.deepen", state.language)) {
                                            Task { await deepen(b.slot) }
                                        }.font(.caption)
                                    }
                                }
                            }
                        }
                    }.card()
                }

                if let bl = base {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(L10n.t("presence.baseline", state.language))
                            .font(.headline).foregroundStyle(Theme.txt)
                        Text("\(bl.known_areas) / \(bl.of)")
                            .font(.caption2).foregroundStyle(Theme.t3)
                        ForEach(Array(bl.areas.keys.sorted()), id: \.self) { key in
                            if let a = bl.areas[key] {
                                HStack {
                                    Text(a.area).font(.caption)
                                        .foregroundStyle(Theme.txt)
                                    Spacer()
                                    Text(a.standing).font(.caption2)
                                        .foregroundStyle(Theme.t3)
                                }
                            }
                        }
                    }.card()
                }

                if let s = surf {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(L10n.t("presence.surfaces", state.language))
                            .font(.headline).foregroundStyle(Theme.txt)
                        Text(s.rule).font(.caption2).foregroundStyle(Theme.t3)
                        ForEach(s.surfaces, id: \.surface) { row in
                            HStack {
                                Button(row.surface) {
                                    Task { await choose(row.surface) }
                                }.font(.caption)
                                Spacer()
                                Text(row.reads_health_aloud
                                     ? L10n.t("presence.aloud", state.language)
                                     : L10n.t("presence.shown", state.language))
                                    .font(.caption2).foregroundStyle(Theme.t3)
                            }
                        }
                    }.card()
                }

                if let r = reach {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(L10n.t("presence.reach", state.language))
                            .font(.headline).foregroundStyle(Theme.txt)
                        Text(r.note).font(.caption2).foregroundStyle(Theme.t3)
                        ForEach(r.offers, id: \.kind) { o in
                            Text((o.who ?? o.topic ?? o.id ?? "—"))
                                .font(.caption).foregroundStyle(Theme.txt)
                        }
                    }.card()
                }

                if let g = grew {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(L10n.t("presence.growth", state.language))
                            .font(.headline).foregroundStyle(Theme.txt)
                        Text("\(g.beats_spoken) · \(g.areas_i_can_see) / \(g.of)")
                            .font(.caption2).foregroundStyle(Theme.t3)
                        // The honest half, in its own words, on the screen
                        // rather than in a docstring nobody reads.
                        Text(g.about_myself).font(.caption2)
                            .foregroundStyle(Theme.t3)
                    }.card()
                }
            }.padding(20)
        }
        .task { await load() }
    }

    /// The beat's own sentence.
    ///
    /// The server sends a key and slots so each client can compose the line
    /// in its reader's language, and the console does exactly that. This
    /// shell does not yet: the ten `presence.*` line rows are in the console
    /// table and not in this one, so the English fallback is what shows here.
    ///
    /// Written down rather than hidden. A key looked up from a variable is
    /// invisible to `test_a_shell_asks_for_a_key_it_has`, so translating them
    /// here without the spelled-out lookups would leave ten rows nothing
    /// asks for — the exact shape that guard exists to catch.
    private func line(_ b: PresenceBeat) -> String { b.english }

    private func load() async {
        guard let uid = state.userId, let token = state.userToken else { return }
        who = try? await ApiClient.shared.presenceWho()
        day = try? await ApiClient.shared.presenceDay(uid: uid, token: token)
        base = try? await ApiClient.shared.presenceBaseline(uid: uid, token: token)
        surf = try? await ApiClient.shared.presenceSurfaces(uid: uid, token: token)
        grew = try? await ApiClient.shared.presenceGrowth(uid: uid, token: token)
        // A missing tandem is not an error here — 409 means "the people live
        // in QRME", and an empty shelf says that better than a red banner.
        reach = try? await ApiClient.shared.presenceReach(uid: uid, token: token)
    }

    /// `/day` is the plan; `/beat` is the utterance, and asking for it is
    /// what counts as having been told.
    private func hear(_ slot: String) async {
        guard let uid = state.userId, let token = state.userToken else { return }
        if let b = try? await ApiClient.shared.presenceBeat(
            uid: uid, token: token, slot: slot) {
            spoken[slot] = b.spoken ?? b.english
        }
    }

    private func deepen(_ slot: String) async {
        guard let uid = state.userId, let token = state.userToken else { return }
        if let b = try? await ApiClient.shared.presenceDeepen(
            uid: uid, token: token, slot: slot) {
            spoken[slot] = b.spoken ?? b.english
        }
    }

    private func choose(_ surface: String) async {
        guard let uid = state.userId, let token = state.userToken else { return }
        surf = try? await ApiClient.shared.presenceChooseSurface(
            uid: uid, token: token, surface: surface)
    }
}
