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
