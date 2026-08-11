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
    @State private var face: GuardianFace?
    @State private var openKid: String?
    @State private var pauseOn = false
    @State private var quietStart = ""
    @State private var quietEnd = ""
    @State private var controlsNote: String?
    @State private var unlinking: String?
    @State private var unlinkNote: String?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if let face, !face.children.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(L10n.t("fam", state.language)).font(.headline).foregroundStyle(Theme.txt)
                            Spacer()
                            if face.haptic == "alert" {
                                Text(L10n.t("fam.tapped", state.language)).font(.caption2.bold())
                                    .padding(.horizontal, 7).padding(.vertical, 3)
                                    .background(Theme.red.opacity(0.16))
                                    .foregroundStyle(Theme.red).clipShape(Capsule())
                            }
                        }
                        ForEach(face.children, id: \.child_id) { c in
                            HStack(spacing: 8) {
                                Circle().fill(faceLight(c.light)).frame(width: 9, height: 9)
                                Text(c.display_name).font(.caption.bold()).foregroundStyle(Theme.txt)
                                if (c.critical_24h ?? 0) > 0 {
                                    Text(L10n.t("fam.st.critical", state.language)).font(.caption2.bold()).foregroundStyle(Theme.red)
                                } else if (c.escalations_24h ?? 0) > 0 {
                                    Text(L10n.t("fam.st.escalated", state.language)).font(.caption2).foregroundStyle(Theme.amber)
                                }
                                Spacer()
                                if c.paused == true {
                                    Text(L10n.t("fam.st.paused", state.language)).font(.caption2).foregroundStyle(Theme.t3)
                                }
                                if let q = c.quiet_hours {
                                    Text("🌙 \(q)").font(.caption2).foregroundStyle(Theme.t3)
                                }
                            }
                        }
                    }.card()
                }

                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("fam.setup", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("fam.enrol", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    field(L10n.t("fam.child.name", state.language), text: $name)
                    field(L10n.t("fam.child.dob", state.language), text: $birthdate)
                    field(L10n.t("fam.child.phone", state.language), text: $phone)
                    Button(action: create) {
                        HStack { if busy { ProgressView().tint(.white) }
                                 Text(L10n.t("fam.create", state.language)).bold() }
                            .frame(maxWidth: .infinity).padding(.vertical, 12)
                            .background(Theme.brand).foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }.disabled(busy || name.isEmpty || birthdate.isEmpty)
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                if let created {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(L10n.t("fam.created", state.language)).font(.headline).foregroundStyle(Theme.green)
                        Text(L10n.t("fam.oversight", state.language)
                            .replacingOccurrences(of: "{scope}",
                                                  with: scopeLabel(created.oversight))
                             + " · " + L10n.t("fam.sens", state.language)
                            .replacingOccurrences(of: "{level}", with:
                                sensitivityLabel(created.sensitivity ?? "cautious",
                                                 state.language)))
                            .font(.caption).foregroundStyle(Theme.t2)
                        Text(L10n.t("fam.token", state.language))
                            .font(.caption.bold()).foregroundStyle(Theme.amber)
                        Text(created.child_token).font(.caption2.monospaced())
                            .foregroundStyle(Theme.txt).textSelection(.enabled)
                    }.card()
                }

                if !kids.isEmpty {
                    Text(L10n.t("fam.mine", state.language)).font(.headline).foregroundStyle(Theme.txt)
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

                if openKid != nil {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(L10n.t("fam.controls", state.language)).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                        Text(L10n.t("fam.pause.sub", state.language))
                            .font(.caption2).foregroundStyle(Theme.t3)
                        Toggle(L10n.t("fam.pause", state.language), isOn: $pauseOn)
                            .font(.subheadline).foregroundStyle(Theme.txt).tint(Theme.amber)
                        HStack(spacing: 8) {
                            field(L10n.t("fam.quiet.start", state.language), text: $quietStart)
                            field(L10n.t("fam.quiet.end", state.language), text: $quietEnd)
                        }
                        Button(L10n.t("fam.apply", state.language)) { applyControls() }
                            .font(.caption.bold()).foregroundStyle(.white)
                            .padding(.horizontal, 14).padding(.vertical, 9)
                            .background(Theme.brandA).clipShape(Capsule())
                        if let controlsNote {
                            Text(controlsNote).font(.caption2).foregroundStyle(Theme.green)
                        }

                        // Ending the link. This screen could begin one and not
                        // end one: `enrollChild` was wired and `unlinkChild`
                        // was written and called by nothing.
                        //
                        // A guardian link is a standing relationship — one
                        // adult able to see another person's events, light and
                        // escalations — and it outlives the reason for it.
                        // Children grow up, custody changes, households end.
                        // The surface that creates it has to be able to end
                        // it, or the person who set it up has to find a
                        // desktop to undo it on.
                        Divider().background(Theme.line)
                        Button(role: .destructive) { unlinking = openKid } label: {
                            Text(L10n.t("fam.unlink.this", state.language)).font(.caption.bold())
                        }
                        if let unlinkNote {
                            Text(unlinkNote).font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }.card()
                }

                if let o = overview {
                    VStack(alignment: .leading, spacing: 6) {
                        if let note = o.note {
                            Text(L10n.t("fam.unlinked", state.language)).font(.headline).foregroundStyle(Theme.txt)
                            Text(note).font(.caption).foregroundStyle(Theme.t2)
                        } else {
                            Text("\(childName(o)) — \(tierLabel(o.oversight))")
                                .font(.headline).foregroundStyle(Theme.txt)
                            if let p = o.privacy_note {
                                Text("🔒 \(p)").font(.caption).foregroundStyle(Theme.amber)
                            }
                            if let n = o.critical_events, n > 0 {
                                Text(L10n.t("fam.critical", state.language)
                                    .replacingOccurrences(of: "{n}", with: "\(n)"))
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
                                Text(L10n.t("fam.quiet", state.language))
                                    .font(.caption).foregroundStyle(Theme.t2)
                            }
                        }
                    }.card()
                }

                // The care team: the household's coordination layer, linked
                // from the same screen that watches over its members.
                CareTeamCard()
                // The specialists who stand behind the household's
                // conditions, and everything handed to them.
                SpecialistsCard()
            }.padding(20)
        }
        .task { await load() }
        // Attached to the ScrollView rather than the button: a
        // confirmationDialog on a row inside a ForEach is dismissed with the
        // row when the list reloads, which is exactly when this one fires.
        .confirmationDialog(L10n.t("fam.unlink.ask", state.language),
                            isPresented: .constant(unlinking != nil),
                            titleVisibility: .visible) {
            Button(L10n.t("fam.unlink", state.language), role: .destructive) {
                if let c = unlinking { unlink(c) }
                unlinking = nil
            }
            Button(L10n.t("fam.keep", state.language), role: .cancel) { unlinking = nil }
        } message: {
            Text(L10n.t("fam.theirs", state.language))
        }
    }

    private func faceLight(_ light: String) -> Color {
        switch light {
        case "green": return Theme.green
        case "orange": return Theme.amber
        case "red": return Theme.red
        default: return Theme.t3
        }
    }

    private func applyControls() {
        guard let uid = state.uid, let token = state.token,
              let cid = openKid else { return }
        Task {
            do {
                let r = try await ApiClient.shared.setFamilyControls(
                    gid: uid, cid: cid, token: token, paused: pauseOn,
                    quietStart: quietStart.isEmpty ? nil : quietStart,
                    quietEnd: quietEnd.isEmpty ? nil : quietEnd)
                controlsNote = r.note
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func light(_ oversight: String) -> Color {
        switch oversight {
        case "full": return Theme.green
        case "alerts_only": return Theme.amber
        default: return Theme.t3
        }
    }

    /// A helper rather than the lookup inline, because a table key quoted
    /// inside a string interpolation ends the enclosing literal as far as the
    /// ratchet's `Text\(\s*"([^"]+)"` pattern is concerned — it then reports
    /// the fragment up to that quote as untranslated English. The line was
    /// localized; the measurement could not see that it was.
    private func childName(_ o: ChildOverview) -> String {
        o.display_name ?? L10n.t("fam.child.generic", state.language)
    }

    /// Each branch resolves on its own line. Folding it into one lookup
    /// with a ternary key hides both rows from the dead-key guard: its
    /// ternary pattern stops at the first quote, and the comparison has one.
    private func scopeLabel(_ oversight: String) -> String {
        oversight == "full"
            ? L10n.t("fam.scope.full", state.language)
            : L10n.t("fam.scope.alerts", state.language)
    }

    private func tierLabel(_ oversight: String) -> String {
        switch oversight {
        case "full": return L10n.t("fam.tier.full", state.language)
        case "alerts_only": return L10n.t("fam.tier.alerts", state.language)
        default: return L10n.t("fam.tier.ended", state.language)
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
        face = try? await ApiClient.shared.guardianWatch(gid: uid, token: token)
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

    private func unlink(_ cid: String) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                try await ApiClient.shared.unlinkChild(gid: uid, cid: cid,
                                                       token: token)
                openKid = nil
                unlinkNote = L10n.t("fam.unlinked.note", state.language)
            } catch { self.error = error.localizedDescription }
            busy = false
            await load()
        }
    }

    private func open(_ kid: ChildSummary) {
        guard let uid = state.uid, let token = state.token else { return }
        openKid = kid.child_id
        controlsNote = nil
        if let c = face?.children.first(where: { $0.child_id == kid.child_id }) {
            pauseOn = c.paused ?? false
            let parts = (c.quiet_hours ?? "").split(separator: "–")
            quietStart = parts.count == 2 ? String(parts[0]) : ""
            quietEnd = parts.count == 2 ? String(parts[1]) : ""
        }
        Task {
            overview = try? await ApiClient.shared.childOverview(
                gid: uid, cid: kid.child_id, token: token)
        }
    }
}
