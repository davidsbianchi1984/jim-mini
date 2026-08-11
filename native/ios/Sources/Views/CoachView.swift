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

    private let areas = ["mental_health", "health_fitness", "career",
                         "finance", "relationships", "personal_growth"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Life Coach").font(.title2.bold()).foregroundStyle(Theme.txt)
                Text("Talk something through. Your coach knows your baseline and goals.")
                    .font(.footnote).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 12) {
                    Text("Area").font(.caption).foregroundStyle(Theme.t2)
                    Picker("", selection: $area) {
                        ForEach(areas, id: \.self) {
                            Text($0.replacingOccurrences(of: "_", with: " ").capitalized).tag($0)
                        }
                    }.pickerStyle(.menu).tint(Theme.brandA)

                    Text("Message").font(.caption).foregroundStyle(Theme.t2)
                    TextField("What's on your mind?", text: $message, axis: .vertical)
                        .lineLimit(2...5).foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                }.card()

                Button(action: send) {
                    HStack { if busy { ProgressView().tint(.white) }; Text("Ask coach").bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 13))
                }.disabled(message.isEmpty || busy)

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                if let g = reply {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Coach").font(.headline).foregroundStyle(Theme.txt)
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
