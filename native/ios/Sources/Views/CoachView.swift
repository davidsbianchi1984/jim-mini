import SwiftUI

/// Life coach: pick an area, send a message -> POST /coach, show the reply.
struct CoachView: View {
    @EnvironmentObject var state: AppState
    /// The walking conversation. A singleton rather than per-view state: it
    /// has to outlive this screen, which is the entire point of it.
    @ObservedObject private var walking = Walking.shared
    @State private var area = "mental_health"
    @State private var message = ""
    @State private var reply: Guidance?
    @State private var busy = false
    @State private var error: String?
    @State private var fromSpecialist: SpecialistAnswer?

    // The offline coach's store and JIM's syllabus for it (jim/pipeline.py).
    @State private var knows: CoachStore?
    @State private var syllabus: CoachCurriculum?
    @State private var studied: String?
    @State private var studying = false
    // The unattended pass: what it went and learned without being asked.
    @State private var ledger: ErrandLedger?
    @State private var running = false
    @State private var watches: ApiClient.LookoutList?
    @State private var watchUrl = ""
    @State private var watchHours = "24"
    @State private var captureLine: String?
    // The situational half of the same ladder: what the coach noticed during
    // the day, and which half of it settled each one.
    @State private var noticed: NoticeLedger?
    @State private var handling = false

    private let areas = ["mental_health", "health_fitness", "career",
                         "finance", "relationships", "personal_growth"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(L10n.t("coach.title", state.language)).font(.title2.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("coach.pitch", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 12) {
                    Text(L10n.t("coach.area", state.language)).font(.caption).foregroundStyle(Theme.t2)
                    Picker("", selection: $area) {
                        ForEach(areas, id: \.self) {
                            Text($0.replacingOccurrences(of: "_", with: " ").capitalized).tag($0)
                        }
                    }.pickerStyle(.menu).tint(Theme.brandA)

                    Text(L10n.t("coach.msg", state.language)).font(.caption).foregroundStyle(Theme.t2)
                    TextField(L10n.t("coach.msg.ph", state.language), text: $message,
                              axis: .vertical)
                        .lineLimit(2...5).foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                }.card()

                Button(action: send) {
                    HStack { if busy { ProgressView().tint(.white) }; Text(L10n.t("coach.ask", state.language)).bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 13))
                }.disabled(message.isEmpty || busy)

                // Take the conversation with you — out of this app entirely.
                // A web page put away has its recogniser ended by the
                // browser and says so; a phone keeps listening while
                // somebody is looking something up somewhere else, and iOS
                // draws the orange dot for as long as it does.
                //
                //     asked     can the conversation survive a screen change
                //     mattered  can it survive leaving the application
                //
                // The same control ends it. A button that only starts
                // something sends a person hunting through Settings for the
                // way back out. The area travels with it: this screen is the
                // one with the picker, and a walk started from mental health
                // that reverted to the front door's `general` would be a
                // different conversation wearing the same name.
                VStack(alignment: .leading, spacing: 4) {
                    Button {
                        if walking.underway {
                            walking.stop()
                        } else if let uid = state.uid, let token = state.token {
                            walking.start(uid: uid, token: token,
                                          area: area, lang: state.language)
                        }
                    } label: {
                        Text(walking.underway
                             ? L10n.t("walk.end", state.language)
                             : L10n.t("walk.take", state.language))
                            .font(.footnote).foregroundStyle(Theme.brand)
                    }
                    if walking.underway {
                        // What the orange dot means, said before somebody has
                        // to wonder.
                        Text(L10n.t("walk.aloft", state.language))
                            .font(.caption2).foregroundStyle(Theme.t2)
                        if !walking.said.isEmpty {
                            Text(walking.said)
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                        if walking.offline {
                            Text(L10n.t("walk.offline", state.language))
                                .font(.caption2).italic()
                                .foregroundStyle(Theme.t2)
                        }
                    }
                    // Why it stopped, when it stopped for a reason. Blank
                    // when somebody ended it: they know.
                    if !walking.trouble.isEmpty {
                        Text(walking.trouble)
                            .font(.caption2).foregroundStyle(Theme.amber)
                    }
                }

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                if let g = reply {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(L10n.t("tab.coach", state.language)).font(.headline).foregroundStyle(Theme.txt)
                        Text(g.content).font(.subheadline).foregroundStyle(Theme.txt)
                        GuidanceExtras(guidance: g)

                        // A specialist covers this area. An offer, not a send:
                        // what would cross the tandem is what this person just
                        // wrote, so the button is theirs to press and the note
                        // says so before they press it.
                        if let o = g.specialist_offer, o.available,
                           fromSpecialist == nil {
                            Divider().overlay(Theme.line)
                            Text(o.label).font(.subheadline.bold())
                                .foregroundStyle(Theme.txt)
                            Text(o.note).font(.caption2).foregroundStyle(Theme.t2)
                            Button(L10n.t("spec.ask", state.language)) { askSpecialist() }
                                .font(.caption).tint(Theme.brandA).disabled(busy)
                        }
                    }.card()
                }

                if let k = knows {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(L10n.t("cch.knows", state.language))
                            .font(.headline).foregroundStyle(Theme.txt)
                        let counts = "\(k.pack) · +\(k.excursions.count) · +\(k.deposits.count)"
                        Text(counts).font(.caption).foregroundStyle(Theme.t2)
                        if let s = syllabus, !s.suggested.isEmpty {
                            Text(L10n.t("cch.study.head", state.language))
                                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            ForEach(s.suggested, id: \.topic) { sug in
                                HStack(alignment: .top) {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(sug.topic).font(.caption)
                                            .foregroundStyle(Theme.txt)
                                        Text(sug.why).font(.caption2)
                                            .foregroundStyle(Theme.t2)
                                    }
                                    Spacer()
                                    Button(L10n.t("cch.study.go", state.language)) {
                                        study(sug)
                                    }.font(.caption).tint(Theme.brandA)
                                        .disabled(studying)
                                }
                            }
                        }
                        if let studied {
                            let done = L10n.t("cch.study.done", state.language)
                            Text("✓ \(studied) — \(done)")
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }

                        // The pass that runs without being pressed once it is
                        // allowed. The coach answers all day for nothing; this
                        // is what it calls when it could not, and calling
                        // costs — so what is left to spend is shown beside the
                        // button rather than discovered in a refusal.
                        if let l = ledger {
                            Text(L10n.t("err.head", state.language))
                                .font(.subheadline.bold())
                                .foregroundStyle(Theme.txt)
                            if l.permitted {
                                Text("\(l.spent_today)/\(l.daily) · "
                                     + L10n.t("err.today", state.language))
                                    .font(.caption2).foregroundStyle(Theme.t2)
                                Button(L10n.t("err.go", state.language)) {
                                    runErrands()
                                }.font(.caption).tint(Theme.brandA)
                                    .disabled(running
                                              || l.spent_today >= l.daily)
                            } else {
                                Text(L10n.t("err.notallowed", state.language))
                                    .font(.caption2).foregroundStyle(Theme.t2)
                            }
                            ForEach(l.errands, id: \.id) { e in
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(e.topic).font(.caption)
                                        .foregroundStyle(Theme.txt)
                                    Text(e.why).font(.caption2)
                                        .foregroundStyle(Theme.t2)
                                    Text(e.left_host
                                         ? L10n.t("err.left", state.language)
                                         : L10n.t("err.stayed", state.language))
                                        .font(.caption2)
                                        .foregroundStyle(Theme.t2)
                                }
                            }
                        }

                        // The lookout: a page the vault re-reads on its
                        // schedule and re-seals in place — JIM never does
                        // the watching. Behind the same study permit as
                        // the errands above.
                        if let w = watches, ledger?.permitted == true {
                            Text(L10n.t("lkt.title", state.language))
                                .font(.subheadline.bold())
                                .foregroundStyle(Theme.txt)
                            TextField(L10n.t("lkt.url", state.language),
                                      text: $watchUrl)
                                .textFieldStyle(.roundedBorder)
                            TextField(L10n.t("lkt.hours", state.language),
                                      text: $watchHours)
                                .textFieldStyle(.roundedBorder)
                            Button(L10n.t("lkt.plant", state.language)) {
                                Task {
                                    guard let uid = state.uid,
                                          let token = state.token else { return }
                                    _ = try? await ApiClient.shared.plantLookout(
                                        uid: uid, url: watchUrl,
                                        everyHours: Double(watchHours) ?? 24,
                                        token: token)
                                    watchUrl = ""
                                    watches = try? await ApiClient.shared
                                        .lookouts(uid: uid, token: token)
                                }
                            }.font(.caption).tint(Theme.brandA)
                                .disabled(watchUrl.isEmpty)
                            ForEach(w.lookouts, id: \.id) { watch in
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(watch.url).font(.caption)
                                        .foregroundStyle(Theme.txt)
                                    Text(String(watch.every_hours) + "h"
                                         + (watch.status.map { " · " + $0 } ?? "")
                                         + (watch.next_run_at.map {
                                             " · " + String($0.prefix(16)) } ?? "")
                                         + (watch.changed_at.map {
                                             " · " + L10n.fill(
                                                 "lkt.changed", state.language,
                                                 ["when": String($0.prefix(10))])
                                         } ?? ""))
                                        .font(.caption2)
                                        .foregroundStyle(Theme.t2)
                                    if let trouble = watch.trouble {
                                        Text(trouble).font(.caption2)
                                            .foregroundStyle(Color.red)
                                    }
                                    HStack {
                                        Button(L10n.t("lkt.read",
                                                      state.language)) {
                                            Task {
                                                guard let uid = state.uid,
                                                      let token = state.token
                                                else { return }
                                                if let page = try? await
                                                    ApiClient.shared.lookoutPage(
                                                        uid: uid, lid: watch.id,
                                                        token: token) {
                                                    captureLine =
                                                        (page.fetched_at ?? "—")
                                                        + " · "
                                                        + String(page.chars)
                                                        + (page.changed_at.map {
                                                            " · " + L10n.fill(
                                                                "lkt.changed",
                                                                state.language,
                                                                ["when": String($0.prefix(10))])
                                                        } ?? "")
                                                }
                                            }
                                        }.font(.caption2)
                                        Button(L10n.t("lkt.drop",
                                                      state.language)) {
                                            Task {
                                                guard let uid = state.uid,
                                                      let token = state.token
                                                else { return }
                                                _ = try? await ApiClient.shared
                                                    .dropLookout(uid: uid,
                                                                 lid: watch.id,
                                                                 token: token)
                                                watches = try? await ApiClient
                                                    .shared.lookouts(uid: uid,
                                                                     token: token)
                                            }
                                        }.font(.caption2)
                                    }
                                }
                            }
                            if let captureLine {
                                Text(captureLine).font(.caption2)
                                    .foregroundStyle(Theme.t2)
                            }
                        }

                        // The other half of the same ladder: what the coach
                        // could not *settle*, rather than what it could not
                        // answer. Each row says which half dealt with it,
                        // because that difference is the product claim and it
                        // is invisible unless it is written down.
                        if let n = noticed {
                            Text(L10n.t("ntc.head", state.language))
                                .font(.subheadline.bold())
                                .foregroundStyle(Theme.txt)
                            if n.settlement.permitted {
                                if let share = n.settlement.free_share, share >= 0 {
                                    Text(L10n.fill("ntc.free", state.language, [
                                        "n": String(n.settlement.settled_free),
                                        "total": String(n.settlement.settled_free
                                                        + n.settlement.settled_paid)]))
                                        .font(.caption2)
                                        .foregroundStyle(Theme.t2)
                                }
                                Button(L10n.t("ntc.go", state.language)) {
                                    runNoticed()
                                }.font(.caption).tint(Theme.brandA)
                                    .disabled(handling)
                            } else {
                                Text(L10n.t("ntc.notallowed", state.language))
                                    .font(.caption2).foregroundStyle(Theme.t2)
                            }
                            ForEach(n.handled, id: \.id) { row in
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(row.condition).font(.caption)
                                        .foregroundStyle(Theme.txt)
                                    Text(row.settled_by == "coach"
                                         ? L10n.t("ntc.by.coach", state.language)
                                         : L10n.t("ntc.by.jim", state.language))
                                        .font(.caption2)
                                        .foregroundStyle(Theme.t2)
                                }
                            }
                        }
                    }.card()
                }

                if let a = fromSpecialist {
                    VStack(alignment: .leading, spacing: 6) {
                        Text((a.specialist_who?.label ?? L10n.t("spec.fallback", state.language))
                             + " · " + L10n.t("spec.via", state.language))
                            .font(.headline).foregroundStyle(Theme.txt)
                        if a.delivered, let content = a.content {
                            Text(content).font(.subheadline)
                                .foregroundStyle(Theme.txt)
                        } else if a.held_for_owner_approval == true {
                            Text(L10n.t("spec.held", state.language))
                                .font(.caption).foregroundStyle(Theme.amber)
                        } else {
                            Text((a.reason ?? "")
                                 + (a.note.map { " — \($0)" } ?? ""))
                                .font(.caption).foregroundStyle(Theme.amber)
                        }
                        if let p = a.answer_provenance {
                            Text(p.method).font(.caption2).foregroundStyle(Theme.t2)
                            Text(L10n.t("spec.shared", state.language) + ": " + p.shared)
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }.card()
                }
            
                // The Guardian's bearing: tone, what it was told, whether
                // its answers landed, and what it made of that.
                BearingCard()
            }.padding(20)
        }
        .onAppear { loadKnows() }
    }

    private func loadKnows() {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            knows = try? await ApiClient.shared.coachStore(uid: uid, token: token)
            syllabus = try? await ApiClient.shared.coachCurriculum(uid: uid,
                                                                   token: token)
            ledger = try? await ApiClient.shared.errands(uid: uid, token: token)
            watches = try? await ApiClient.shared.lookouts(uid: uid,
                                                           token: token)
            noticed = try? await ApiClient.shared.noticed(uid: uid, token: token)
        }
    }

    /// Deal with what the coach noticed during the day. No budget guard on
    /// the button, unlike the errands one: this pass is worth running on a
    /// spent day, because the offline coach settles what it can for nothing.
    private func runNoticed() {
        guard let uid = state.uid, let token = state.token else { return }
        handling = true
        Task {
            _ = try? await ApiClient.shared.runNoticed(uid: uid, token: token)
            handling = false
            loadKnows()
        }
    }

    /// Let it go and study, unattended, whatever the coach could not answer.
    private func runErrands() {
        guard let uid = state.uid, let token = state.token else { return }
        running = true
        Task {
            _ = try? await ApiClient.shared.runErrands(uid: uid, token: token)
            running = false
            loadKnows()
        }
    }

    private func study(_ sug: CoachSuggestion) {
        guard let uid = state.uid, let token = state.token else { return }
        studying = true
        Task {
            do {
                let r = try await ApiClient.shared.coachStudy(
                    uid: uid, token: token, topic: sug.topic, area: sug.area)
                studied = r.studied
                loadKnows()
            } catch { self.error = error.localizedDescription }
            studying = false
        }
    }

    private func askSpecialist() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                fromSpecialist = try await ApiClient.shared.coachSpecialist(
                    uid: uid, token: token, area: area, message: message)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func send() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            fromSpecialist = nil
            do { reply = try await ApiClient.shared.coach(uid: uid, token: token, area: area, message: message) }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
