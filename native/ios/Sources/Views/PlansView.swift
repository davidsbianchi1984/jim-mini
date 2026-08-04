import SwiftUI

/// The Guardian's calendar, on the device that goes to the appointment.
///
/// Every visible string comes from the view's own `labels` — composed
/// server-side in the reader's language — because the English count behind
/// this shell's tabs is a ratchet and these sections must not feed it.
/// Until a view loads there is nothing to say, so nothing is said.
struct ScheduleSection: View {
    @EnvironmentObject var state: AppState
    @State private var view: ScheduleOverview?
    @State private var title = ""
    @State private var when = ""
    @State private var whereAt = ""
    @State private var emailMe = false
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let v = view {
                let L = v.labels
                VStack(alignment: .leading, spacing: 8) {
                    Text(L["title"] ?? "").font(.headline)
                        .foregroundStyle(Theme.txt)
                    Text(v.note).font(.caption2).foregroundStyle(Theme.t2)
                    TextField(L["what"] ?? "", text: $title)
                        .textFieldStyle(.roundedBorder)
                    TextField(L["when"] ?? "", text: $when)
                        .textFieldStyle(.roundedBorder)
                    TextField(L["where"] ?? "", text: $whereAt)
                        .textFieldStyle(.roundedBorder)
                    Toggle(isOn: $emailMe) {
                        Text(v.email_available ? (L["email_me"] ?? "")
                                               : (L["no_email"] ?? ""))
                            .font(.caption).foregroundStyle(Theme.t2)
                    }.disabled(!v.email_available)
                    Button(L["book"] ?? "") { book() }
                        .disabled(busy || title.isEmpty || when.isEmpty)
                }.card()

                if !v.appointments.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(L["upcoming"] ?? "").font(.subheadline.bold())
                            .foregroundStyle(Theme.txt)
                        ForEach(v.appointments) { a in
                            HStack {
                                let line = a.title + " · "
                                    + String(a.whenat.prefix(16))
                                        .replacingOccurrences(of: "T",
                                                              with: " ")
                                Text(line).font(.caption)
                                    .foregroundStyle(Theme.t2)
                                Spacer()
                                Button(L["cancel"] ?? "") { cancel(a.id) }
                                    .font(.caption2).disabled(busy)
                            }
                        }
                    }.card()
                }
            }
            if let note {
                Text(note).font(.caption).foregroundStyle(Theme.t2)
            }
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        view = try? await ApiClient.shared.scheduleView(uid: uid,
                                                        token: token)
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op(); await load() }
            catch { note = error.localizedDescription }
            busy = false
        }
    }

    private func book() {
        run {
            _ = try await ApiClient.shared.scheduleBook(
                uid: state.uid!, token: state.token!, title: title,
                when: when, where: whereAt, emailReminder: emailMe)
            title = ""; when = ""; whereAt = ""
        }
    }

    private func cancel(_ id: String) {
        run {
            _ = try await ApiClient.shared.scheduleCancel(
                uid: state.uid!, token: state.token!, appointmentId: id)
        }
    }
}

/// The tandem shops shelf: browse QRME's storefronts, order as your own
/// interactor, keep the receipts here. Same label discipline as above.
struct ShoppingSection: View {
    @EnvironmentObject var state: AppState
    @State private var view: ShoppingOverview?
    @State private var shopId = ""
    @State private var offeringId = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let v = view {
                let L = v.labels
                VStack(alignment: .leading, spacing: 8) {
                    Text(L["title"] ?? "").font(.headline)
                        .foregroundStyle(Theme.txt)
                    Text(v.note).font(.caption2).foregroundStyle(Theme.t2)
                    ForEach(v.shops) { s in
                        HStack {
                            let line = s.name + " · " + s.seller
                                + (s.tag.map { " · " + $0 } ?? "")
                            Text(line).font(.caption)
                                .foregroundStyle(Theme.txt)
                            Spacer()
                            Button(L["browse"] ?? "") { shopId = s.id }
                                .font(.caption2)
                        }
                    }
                    TextField(L["title"] ?? "", text: $shopId)
                        .textFieldStyle(.roundedBorder)
                    TextField(L["offerings"] ?? "", text: $offeringId)
                        .textFieldStyle(.roundedBorder)
                    Button(L["order"] ?? "") { order() }
                        .disabled(busy || shopId.isEmpty || offeringId.isEmpty)
                }.card()

                if !v.receipts.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(L["receipts"] ?? "").font(.subheadline.bold())
                            .foregroundStyle(Theme.txt)
                        ForEach(v.receipts) { r in
                            HStack {
                                let line = r.title + " · "
                                    + String(format: "%.2f", r.amount)
                                    + " " + r.currency + " · " + r.status
                                Text(line).font(.caption2)
                                    .foregroundStyle(Theme.t2)
                                Spacer()
                                if r.status == "placed" {
                                    Button(L["cancel"] ?? "") {
                                        cancel(r.qrme_order_id)
                                    }.font(.caption2).disabled(busy)
                                }
                            }
                        }
                    }.card()
                }
            }
            if let note {
                Text(note).font(.caption).foregroundStyle(Theme.t2)
            }
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        view = try? await ApiClient.shared.shoppingView(uid: uid,
                                                        token: token)
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op(); await load() }
            catch { note = error.localizedDescription }
            busy = false
        }
    }

    private func order() {
        run {
            _ = try await ApiClient.shared.shoppingOrder(
                uid: state.uid!, token: state.token!, shopId: shopId,
                offeringId: offeringId, quantity: 1)
            offeringId = ""
        }
    }

    private func cancel(_ qrmeOrderId: String) {
        run {
            _ = try await ApiClient.shared.shoppingCancel(
                uid: state.uid!, token: state.token!,
                qrmeOrderId: qrmeOrderId)
        }
    }
}

/// Your circle: contacts by mutual invitation, messages that never leave
/// this deployment, the switches that govern both, and the homepage
/// sandbox. Same label discipline as the sections above — every visible
/// string arrives from the server in the reader's language.
struct CircleSection: View {
    @EnvironmentObject var state: AppState
    @State private var view: CircleOverview?
    @State private var inviteId = ""
    @State private var withId = ""
    @State private var thread: [CircleMessageRow] = []
    @State private var draft = ""
    @State private var headline = ""
    @State private var about = ""
    @State private var bg = "#10251c"
    @State private var accent = "#2fbf8f"
    @State private var lookId = ""
    @State private var looking: CircleHomepageRow?
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let v = view {
                let L = v.labels
                VStack(alignment: .leading, spacing: 8) {
                    Text(L["title"] ?? "").font(.headline)
                        .foregroundStyle(Theme.txt)
                    Text(v.note).font(.caption2).foregroundStyle(Theme.t2)
                    ForEach(v.circle.contacts) { p in
                        HStack {
                            Text(p.display_name ?? p.user_id).font(.caption)
                                .foregroundStyle(Theme.txt)
                            Spacer()
                            Button(L["open"] ?? "") { open(p.user_id) }
                                .font(.caption2).disabled(busy)
                            Button(L["leave"] ?? "") { leave(p.user_id) }
                                .font(.caption2).disabled(busy)
                        }
                    }
                    ForEach(v.circle.invited_me) { p in
                        HStack {
                            let line = (p.display_name ?? p.user_id) + " · "
                                + (L["invited_me"] ?? "")
                            Text(line).font(.caption)
                                .foregroundStyle(Theme.t2)
                            Spacer()
                            Button(L["invite"] ?? "") { invite(p.user_id) }
                                .font(.caption2).disabled(busy)
                        }
                    }
                    ForEach(v.circle.awaiting) { p in
                        let line = (p.display_name ?? p.user_id) + " · "
                            + (L["awaiting"] ?? "")
                        Text(line).font(.caption2).foregroundStyle(Theme.t2)
                    }
                    HStack {
                        TextField(L["invite"] ?? "", text: $inviteId)
                            .textFieldStyle(.roundedBorder)
                        Button(L["invite"] ?? "") { invite(inviteId) }
                            .disabled(busy || inviteId.isEmpty)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L["messages"] ?? "").font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    ForEach(v.threads) { t in
                        HStack {
                            Text(t.other_name ?? t.other_id).font(.caption)
                                .foregroundStyle(Theme.txt)
                            Spacer()
                            Button(L["open"] ?? "") { open(t.other_id) }
                                .font(.caption2).disabled(busy)
                        }
                    }
                    TextField(L["to"] ?? "", text: $withId)
                        .textFieldStyle(.roundedBorder)
                    ForEach(thread) { m in
                        let line = (m.sender_id == state.uid ? "→ " : "← ")
                            + m.body
                        Text(line).font(.caption2).foregroundStyle(Theme.t2)
                    }
                    HStack {
                        TextField("", text: $draft)
                            .textFieldStyle(.roundedBorder)
                        Button(L["send"] ?? "") { send() }
                            .disabled(busy || draft.isEmpty || withId.isEmpty)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L["switches"] ?? "").font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    ForEach(v.features.keys.sorted(), id: \.self) { feature in
                        Toggle(isOn: Binding(
                            get: { v.features[feature] ?? true },
                            set: { on in flip(feature, on) })) {
                            Text(feature == "messaging"
                                 ? (L["sw_messaging"] ?? "")
                                 : (L["sw_homepage"] ?? ""))
                                .font(.caption).foregroundStyle(Theme.t2)
                        }.disabled(busy)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L["page"] ?? "").font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    TextField(L["headline"] ?? "", text: $headline)
                        .textFieldStyle(.roundedBorder)
                    TextField(L["about"] ?? "", text: $about)
                        .textFieldStyle(.roundedBorder)
                    TextField(L["background"] ?? "", text: $bg)
                        .textFieldStyle(.roundedBorder)
                    TextField(L["accent"] ?? "", text: $accent)
                        .textFieldStyle(.roundedBorder)
                    Button(L["save"] ?? "") { save() }.disabled(busy)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L["visit"] ?? "").font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    HStack {
                        TextField(L["visit_id"] ?? "", text: $lookId)
                            .textFieldStyle(.roundedBorder)
                        Button(L["open"] ?? "") { look() }
                            .disabled(busy || lookId.isEmpty)
                    }
                    if let page = looking {
                        let head = (page.display_name ?? page.user_id)
                            + " — " + page.headline
                        Text(head).font(.caption.bold())
                            .foregroundStyle(Theme.txt)
                        Text(page.about).font(.caption2)
                            .foregroundStyle(Theme.t2)
                        ForEach(page.links, id: \.url) { link in
                            Text(link.label + " · " + link.url)
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                        if !page.top_friends.isEmpty {
                            let tops = (L["top"] ?? "") + ": "
                                + page.top_friends
                                    .map { $0.display_name ?? $0.user_id }
                                    .joined(separator: " · ")
                            Text(tops).font(.caption2)
                                .foregroundStyle(Theme.t2)
                        }
                    }
                }.card()
            }
            if let note {
                Text(note).font(.caption).foregroundStyle(Theme.t2)
            }
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        view = try? await ApiClient.shared.circleView(uid: uid, token: token)
        if let page = view?.homepage {
            headline = page.headline; about = page.about
            bg = page.theme.bg; accent = page.theme.accent
        }
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op(); await load() }
            catch { note = error.localizedDescription }
            busy = false
        }
    }

    private func invite(_ otherId: String) {
        run {
            _ = try await ApiClient.shared.circleInvite(
                uid: state.uid!, token: state.token!, otherId: otherId)
            inviteId = ""
        }
    }

    private func leave(_ otherId: String) {
        run {
            _ = try await ApiClient.shared.circleLeave(
                uid: state.uid!, token: state.token!, otherId: otherId)
        }
    }

    private func flip(_ feature: String, _ on: Bool) {
        run {
            _ = try await ApiClient.shared.circleSetFeature(
                uid: state.uid!, token: state.token!, feature: feature,
                enabled: on)
        }
    }

    private func open(_ other: String) {
        withId = other
        run {
            thread = try await ApiClient.shared.circleThread(
                uid: state.uid!, token: state.token!, withId: other)
        }
    }

    private func send() {
        run {
            _ = try await ApiClient.shared.circleSend(
                uid: state.uid!, token: state.token!, to: withId,
                body: draft)
            draft = ""
            thread = try await ApiClient.shared.circleThread(
                uid: state.uid!, token: state.token!, withId: withId)
        }
    }

    private func save() {
        run {
            _ = try await ApiClient.shared.circleEditHomepage(
                uid: state.uid!, token: state.token!, headline: headline,
                about: about, bg: bg, accent: accent)
        }
    }

    private func look() {
        run {
            looking = try await ApiClient.shared.circleHomepage(
                uid: state.uid!, token: state.token!, otherId: lookId)
        }
    }
}
