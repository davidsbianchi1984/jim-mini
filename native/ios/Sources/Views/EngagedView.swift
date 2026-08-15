import SwiftUI

/// The Guardian you leave running.
///
/// `CoachView` is a turn: you ask, it answers, nothing is left holding. This
/// is a session — open until sign-off, able to act on this person's own
/// records while it is open, and every act on a trail they can take back.
///
/// Three things this screen owes a person that the backend cannot:
///
/// **The reach comes before the button.** `engagedReach()` carries no token
/// because it is how somebody decides whether to open one at all. It renders
/// above Engage, not behind a disclosure — a list of what a thing may do to
/// you is not a detail view.
///
/// **An act is never drawn as reversible when it is not.** `reversible` and
/// `irreversible_because` are two fields for a reason: an act that acted and
/// can no longer be taken back is a real third state, and `!reversible`
/// alone would tell somebody their journal entry had left the app.
///
/// **Sign-off is a handover.** The topics field sits on the sign-off card,
/// filled in before the button, because the whole promise is that leaving
/// does not mean being unwatched.
struct EngagedView: View {
    @EnvironmentObject var state: AppState

    @State private var reach: EngagedReach?
    @State private var permits: EngagedPermits?
    @State private var session: EngagedSession?
    @State private var acts: [EngagedAct] = []
    @State private var watching: [StandingWatch] = []
    @State private var said = ""
    @State private var steps: [EngagedStep] = []
    @State private var stopped: String?
    @State private var provenance: EngagedProvenance?
    @State private var topics = ""
    @State private var newWatch = ""
    @State private var busy = false
    @State private var error: String?

    private var open: Bool { session?.engaged == true }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(L10n.t("eng.title", state.language))
                    .font(.title2.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("eng.pitch", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)

                if let error {
                    Text(error).font(.footnote).foregroundStyle(Theme.red)
                }

                reachCard
                permitsCard
                sessionCard
                trailCard
                if open { signOffCard }
                watchCard
            }
            .padding(20)
        }
        .background(Theme.bg)
        .task { await load() }
    }

    // MARK: what it may do to you, before you let it near anything

    @ViewBuilder private var reachCard: some View {
        if let reach {
            VStack(alignment: .leading, spacing: 8) {
                Text(L10n.t("eng.reach", state.language))
                    .font(.headline).foregroundStyle(Theme.txt)
                Text(L10n.t("eng.reach.note", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                ForEach(reach.can) { tool in
                    HStack(alignment: .top, spacing: 8) {
                        Text(tool.acts ? L10n.t("eng.acts", state.language)
                                       : L10n.t("eng.reads", state.language))
                            .font(.caption2.bold())
                            .foregroundStyle(tool.acts ? Theme.amber : Theme.t2)
                            .frame(width: 62, alignment: .leading)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(tool.says).font(.caption).foregroundStyle(Theme.txt)
                            if tool.irreversible_because != nil {
                                Text(L10n.t("eng.forever", state.language))
                                    .font(.caption2).foregroundStyle(Theme.red)
                            }
                        }
                    }
                }
            }.card()
        }
    }

    // MARK: the switches, beside the reach

    /// What this person has let it change, and the toggles that change that.
    ///
    /// It sits directly under the reach card on purpose: "what it can do" and
    /// "what I have let it do" are one question with two answers, and putting
    /// them on separate screens would be the menu problem this feature exists
    /// to answer.
    @ViewBuilder private var permitsCard: some View {
        if let permits {
            VStack(alignment: .leading, spacing: 10) {
                Text(L10n.t("eng.permits", state.language))
                    .font(.headline).foregroundStyle(Theme.txt)
                Text(L10n.t("eng.permits.note", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                ForEach(permits.groups) { area in
                    HStack(alignment: .top, spacing: 10) {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(L10n.t("eng.permit.\(area.area)", state.language))
                                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Text(area.says)
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                        Spacer(minLength: 8)
                        // The toggle carries the state, never the effect. A
                        // control labelled with what pressing it would do and
                        // one labelled with what is true now look identical
                        // and mean opposite things.
                        Toggle("", isOn: Binding(
                            get: { area.granted },
                            set: { on in Task { await flip(area.area, on) } }))
                            .labelsHidden().disabled(busy)
                    }
                }
                Text(permits.note).font(.caption2).foregroundStyle(Theme.t2)
            }.card()
        }
    }

    // MARK: the session itself

    @ViewBuilder private var sessionCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            if !open {
                Text(L10n.t("eng.none", state.language))
                    .font(.headline).foregroundStyle(Theme.txt)
                Text(L10n.t("eng.none.note", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
                Button(action: { Task { await engage() } }) {
                    Text(L10n.t("eng.open", state.language)).bold()
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 13))
                }.disabled(busy)
            } else {
                ForEach(session?.turns ?? []) { turn in
                    VStack(alignment: .leading, spacing: 2) {
                        Text(turn.role == "user"
                             ? L10n.t("eng.you", state.language)
                             : L10n.t("eng.jim", state.language))
                            .font(.caption2.bold()).foregroundStyle(Theme.t2)
                        Text(turn.content).font(.subheadline)
                            .foregroundStyle(Theme.txt)
                    }
                }

                // What it did this turn, under the reply where it can be
                // checked. An assistant that changes something and then
                // describes the change in prose is asking to be believed.
                ForEach(steps) { step in
                    if let refused = step.refused {
                        // The refusal key alone. It was labelled "cannot be
                        // taken back" in the first draft, which is the wrong
                        // sentence twice over: a refused step changed nothing,
                        // so there is nothing to take back — and the
                        // interpolated literal read to the English-behind-the
                        // -tab-bar guard as prose.
                        Text(refused)
                            .font(.caption2).foregroundStyle(Theme.red)
                    } else {
                        HStack(spacing: 6) {
                            Text("\(step.answered ?? 0)")
                                .font(.caption2.bold()).foregroundStyle(Theme.t2)
                            Text(step.says ?? step.tool ?? "")
                                .font(.caption).foregroundStyle(Theme.txt)
                            if step.acts == true && step.reversible != true {
                                Text(L10n.t("eng.forever", state.language))
                                    .font(.caption2).foregroundStyle(Theme.red)
                            }
                        }
                    }
                }

                // Who actually answered, and the one stop this screen has
                // that the coach does not: the offline model can answer but
                // cannot act, so a turn it served says so rather than
                // handing over canned prose from a surface that acts.
                if stopped == "engaged.needs_the_online_model" {
                    Text(L10n.t("eng.offline", state.language))
                        .font(.caption2).foregroundStyle(Theme.amber)
                } else if provenance?.degraded == true {
                    Text(L10n.t("eng.offline", state.language))
                        .font(.caption2).foregroundStyle(Theme.amber)
                }

                TextField(L10n.t("eng.say.ph", state.language), text: $said,
                          axis: .vertical)
                    .lineLimit(2...5).foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 11))
                    .overlay(RoundedRectangle(cornerRadius: 11)
                        .stroke(Theme.line, lineWidth: 1))

                Button(action: { Task { await speak() } }) {
                    HStack {
                        if busy { ProgressView().tint(.white) }
                        Text(L10n.t("eng.say", state.language)).bold()
                    }
                    .frame(maxWidth: .infinity).padding(.vertical, 14)
                    .background(Theme.brand).foregroundStyle(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 13))
                }.disabled(busy || said.isEmpty)
            }
        }.card()
    }

    // MARK: the undo trail
    //
    // Shown whether or not a session is open, because the thing somebody
    // wants to take back is usually noticed afterwards.

    private var trailCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("eng.trail", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("eng.trail.note", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            if acts.isEmpty {
                Text(L10n.t("eng.trail.none", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
            }
            ForEach(acts) { act in
                HStack(alignment: .top) {
                    Text(act.says).font(.caption).foregroundStyle(Theme.txt)
                    Spacer()
                    if act.undone_at != nil {
                        Text(L10n.t("eng.undone", state.language))
                            .font(.caption2).foregroundStyle(Theme.t2)
                    } else if act.reversible {
                        Button(L10n.t("eng.undo", state.language)) {
                            Task { await undo(act) }
                        }.font(.caption).tint(Theme.brandA).disabled(busy)
                    } else {
                        Text(L10n.t("eng.forever", state.language))
                            .font(.caption2).foregroundStyle(Theme.red)
                    }
                }
            }
        }.card()
    }

    // MARK: signing off, and what stays behind

    private var signOffCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("eng.off", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("eng.off.note", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            TextField(L10n.t("eng.off.ph", state.language), text: $topics,
                      axis: .vertical)
                .lineLimit(2...5).foregroundStyle(Theme.txt)
                .padding(10).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11)
                    .stroke(Theme.line, lineWidth: 1))
            Button(L10n.t("eng.off", state.language)) {
                Task { await signOff() }
            }.font(.callout).tint(Theme.brandA).disabled(busy)
        }.card()
    }

    private var watchCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("eng.watch", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("eng.watch.note", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            if watching.isEmpty {
                Text(L10n.t("eng.watch.none", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
            }
            ForEach(watching) { watch in
                HStack {
                    Text(watch.topic).font(.caption).foregroundStyle(Theme.txt)
                    Spacer()
                    Button(L10n.t("eng.watch.stop", state.language)) {
                        Task { await stopWatching(watch) }
                    }.font(.caption2).tint(Theme.t2).disabled(busy)
                }
            }
            HStack {
                TextField(L10n.t("eng.watch.ph", state.language),
                          text: $newWatch)
                    .foregroundStyle(Theme.txt)
                Button(L10n.t("eng.open", state.language)) {
                    Task { await keepWatching() }
                }.font(.caption).tint(Theme.brandA)
                 .disabled(busy || newWatch.isEmpty)
            }
            .padding(10).background(Theme.scrBot)
            .clipShape(RoundedRectangle(cornerRadius: 11))
        }.card()
    }

    // MARK: doing it

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        reach = try? await ApiClient.shared.engagedReach()
        do {
            session = try await ApiClient.shared.engaged(uid: uid, token: token)
            acts = try await ApiClient.shared.engagedActs(uid: uid, token: token)
            // From the watch list rather than the session's copy of it: the
            // card shows what is being watched for whether or not anybody is
            // engaged — that is what makes a watch *standing* — and taking it
            // from the session would go stale the moment one closed.
            watching = try await ApiClient.shared.engagedWatches(uid: uid, token: token)
            permits = try await ApiClient.shared.engagedPermits(uid: uid, token: token)
        } catch { self.error = error.localizedDescription }
    }

    /// Switch a group on or off, then re-read rather than patch in place — a
    /// grant is the sort of thing somebody double-checks, and a screen showing
    /// its own guess would be showing them their tap, not the record.
    private func flip(_ area: String, _ granted: Bool) async {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        defer { busy = false }
        do {
            try await ApiClient.shared.engagedSetPermit(
                uid: uid, token: token, area: area, granted: granted)
            permits = try await ApiClient.shared.engagedPermits(uid: uid, token: token)
        } catch { self.error = error.localizedDescription }
    }

    private func engage() async {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        defer { busy = false }
        do {
            session = try await ApiClient.shared.engage(uid: uid, token: token)
            await load()
        } catch { self.error = error.localizedDescription }
    }

    private func speak() async {
        guard let uid = state.uid, let token = state.token else { return }
        let message = said.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !message.isEmpty else { return }
        busy = true; error = nil
        defer { busy = false }
        do {
            let turn = try await ApiClient.shared.engagedTurn(uid: uid, token: token,
                                                        message: message)
            steps = turn.did
            stopped = turn.stopped
            provenance = turn.provenance
            said = ""
            await load()
        } catch { self.error = error.localizedDescription }
    }

    private func undo(_ act: EngagedAct) async {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        defer { busy = false }
        do {
            _ = try await ApiClient.shared.engagedUndo(uid: uid, token: token,
                                                 actId: act.id)
            await load()
        } catch { self.error = error.localizedDescription }
    }

    private func signOff() async {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        defer { busy = false }
        let named = topics.split(separator: "\n")
            .map { $0.trimmingCharacters(in: .whitespaces) }
            .filter { !$0.isEmpty }
        do {
            let out = try await ApiClient.shared.engagedSignOff(uid: uid, token: token,
                                                          topics: named)
            watching = out.watches
            topics = ""; steps = []; stopped = nil; provenance = nil
            await load()
        } catch { self.error = error.localizedDescription }
    }

    private func keepWatching() async {
        guard let uid = state.uid, let token = state.token else { return }
        let topic = newWatch.trimmingCharacters(in: .whitespaces)
        guard !topic.isEmpty else { return }
        do {
            _ = try await ApiClient.shared.engagedWatch(uid: uid, token: token,
                                                  topic: topic)
            newWatch = ""
            await load()
        } catch { self.error = error.localizedDescription }
    }

    private func stopWatching(_ watch: StandingWatch) async {
        guard let uid = state.uid, let token = state.token else { return }
        do {
            try await ApiClient.shared.engagedClearWatch(uid: uid, token: token,
                                                    watchId: watch.id)
            await load()
        } catch { self.error = error.localizedDescription }
    }
}
