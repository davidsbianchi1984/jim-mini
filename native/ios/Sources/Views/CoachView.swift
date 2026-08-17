import SwiftUI

/// Life coach: pick an area, send a message -> POST /coach, show the reply.
struct CoachView: View {
    @EnvironmentObject var state: AppState
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
                    }.card()
                }

                if let a = fromSpecialist {
                    VStack(alignment: .leading, spacing: 6) {
                        Text((a.specialist?.label ?? L10n.t("spec.fallback", state.language))
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
                        if let p = a.provenance {
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
