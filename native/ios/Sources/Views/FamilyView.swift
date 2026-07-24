import SwiftUI

/// Family: a parent sets up — and watches over — a child's account. The
/// signed-in adult is the guardian; creating a child records the consent as
/// a relationship, applies protective defaults, and opens an oversight
/// window sized by age (full under 13, alerts-only for teens, closed at 18).
struct FamilyView: View {
    @EnvironmentObject var state: AppState
    @State private var name = ""
    @State private var birthdate = ""
    @State private var phone = ""
    @State private var created: ChildCreated?
    @State private var kids: [ChildSummary] = []
    @State private var overview: ChildOverview?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Set up my child").font(.headline).foregroundStyle(Theme.txt)
                    Text("You enroll as the recorded parent/guardian. The account starts cautious, with you as the emergency contact; cloud sharing stays off. The auto-defib waiver can never be signed for a minor.")
                        .font(.caption).foregroundStyle(Theme.t2)
                    field("child's name", text: $name)
                    field("birthdate (YYYY-MM-DD)", text: $birthdate)
                    field("your phone (emergency line, optional)", text: $phone)
                    Button(action: create) {
                        HStack { if busy { ProgressView().tint(.white) }
                                 Text("Create child account").bold() }
                            .frame(maxWidth: .infinity).padding(.vertical, 12)
                            .background(Theme.brand).foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }.disabled(busy || name.isEmpty || birthdate.isEmpty)
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                if let created {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Child account created").font(.headline).foregroundStyle(Theme.green)
                        Text("Oversight: \(created.oversight == "full" ? "full (under 13)" : "alerts only (teen)") · sensitivity: \(created.sensitivity ?? "cautious")")
                            .font(.caption).foregroundStyle(Theme.t2)
                        Text("Device token — shown once, put it on their watch or phone:")
                            .font(.caption.bold()).foregroundStyle(Theme.amber)
                        Text(created.child_token).font(.caption2.monospaced())
                            .foregroundStyle(Theme.txt).textSelection(.enabled)
                    }.card()
                }

                if !kids.isEmpty {
                    Text("My family").font(.headline).foregroundStyle(Theme.txt)
                    ForEach(kids, id: \.child_id) { kid in
                        Button(action: { open(kid) }) {
                            HStack(spacing: 8) {
                                Circle().fill(light(kid.oversight)).frame(width: 9, height: 9)
                                VStack(alignment: .leading, spacing: 2) {
                                    Text("\(kid.display_name) · \(kid.age)")
                                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                                    Text(tierLabel(kid.oversight))
                                        .font(.caption2).foregroundStyle(Theme.t2)
                                }
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .font(.caption2).foregroundStyle(Theme.t3)
                            }
                        }.card()
                    }
                }

                if let o = overview {
                    VStack(alignment: .leading, spacing: 6) {
                        if let note = o.note {
                            Text("Oversight ended").font(.headline).foregroundStyle(Theme.txt)
                            Text(note).font(.caption).foregroundStyle(Theme.t2)
                        } else {
                            Text("\(o.display_name ?? "Child") — \(tierLabel(o.oversight))")
                                .font(.headline).foregroundStyle(Theme.txt)
                            if let p = o.privacy_note {
                                Text("🔒 \(p)").font(.caption).foregroundStyle(Theme.amber)
                            }
                            if let n = o.critical_events, n > 0 {
                                Text("⚠️ \(n) critical event(s)")
                                    .font(.caption.bold()).foregroundStyle(Theme.red)
                            }
                            ForEach(Array((o.events ?? []).enumerated()), id: \.offset) { _, e in
                                HStack {
                                    Text(e.type).font(.caption).foregroundStyle(Theme.txt)
                                    if let c = e.condition {
                                        Text(c).font(.caption2).foregroundStyle(Theme.t2)
                                    }
                                    Spacer()
                                    if let s = e.severity {
                                        Text(s.uppercased()).font(.caption2.bold())
                                            .foregroundStyle(s == "critical" ? Theme.red : Theme.amber)
                                    }
                                }
                            }
                            if (o.events ?? []).isEmpty {
                                Text("Nothing in the window — quiet is good news.")
                                    .font(.caption).foregroundStyle(Theme.t2)
                            }
                        }
                    }.card()
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func light(_ oversight: String) -> Color {
        switch oversight {
        case "full": return Theme.green
        case "alerts_only": return Theme.amber
        default: return Theme.t3
        }
    }

    private func tierLabel(_ oversight: String) -> String {
        switch oversight {
        case "full": return "full oversight (under 13)"
        case "alerts_only": return "alerts only — their daily life stays private"
        default: return "oversight ended — they're an adult now"
        }
    }

    private func field(_ placeholder: String, text: Binding<String>) -> some View {
        TextField(placeholder, text: text)
            .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
            .padding(10).background(Theme.scrBot)
            .clipShape(RoundedRectangle(cornerRadius: 11))
            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        kids = (try? await ApiClient.shared.children(gid: uid, token: token)) ?? []
    }

    private func create() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                created = try await ApiClient.shared.enrollChild(
                    gid: uid, token: token, name: name, birthdate: birthdate,
                    guardianPhone: phone)
                name = ""; birthdate = ""; phone = ""
            } catch { self.error = error.localizedDescription }
            busy = false
            await load()
        }
    }

    private func open(_ kid: ChildSummary) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            overview = try? await ApiClient.shared.childOverview(
                gid: uid, cid: kid.child_id, token: token)
        }
    }
}
