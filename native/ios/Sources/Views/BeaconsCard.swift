import SwiftUI

/// The sticker and the relay: beacons a stranger can scan to reach help on
/// your behalf — the scanner needs no account and sees only what you chose
/// to put on the card — and the relay that escalates people, not sirens.
/// Console doors (Safety, Attending); this is the phone's.
struct BeaconsCard: View {
    @EnvironmentObject var state: AppState
    @Environment(\.openURL) private var openURL
    @State private var rows: [BeaconRow] = []
    @State private var label = ""
    @State private var placement = ""
    @State private var card: BeaconCardOut?
    @State private var alarm: BeaconAlarm?
    @State private var channel: RelayChannel?
    @State private var roster: RelayRoster?
    @State private var rota: RelayRota?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("sfy.beacons", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("sfy.beacons.pitch", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            ForEach(rows, id: \.id) { row in
                HStack(spacing: 8) {
                    Text(row.label)
                        .font(.caption2.bold()).foregroundStyle(Theme.txt)
                    Text(L10n.t("sfy.beacons.scans", state.language)
                            .replacingOccurrences(of: "{n}",
                                                  with: String(row.scans)))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    if !row.active {
                        Text(L10n.t("sfy.beacons.retired", state.language))
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                    Spacer()
                    Button(L10n.t("att.open", state.language)) {
                        openPage(row.id)
                    }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy)
                    Button(L10n.t("rch.acc.beacon", state.language)) {
                        preview(row.id)
                    }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy)
                    Button(L10n.t("aim.budget.remove", state.language)) {
                        retire(row.id)
                    }
                    .font(.caption2).foregroundStyle(Theme.red)
                    .disabled(busy || !row.active)
                }
            }
            if let card {
                VStack(alignment: .leading, spacing: 2) {
                    Text(card.first_name ?? "")
                        .font(.caption2.bold()).foregroundStyle(Theme.txt)
                    Text(card.note ?? "")
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Text(card.badge ?? "")
                        .font(.caption2).foregroundStyle(Theme.t3)
                    Button(L10n.t("att.alarm.raise", state.language)) {
                        raise(card.beacon)
                    }
                    .font(.caption2.bold()).foregroundStyle(Theme.red)
                    .disabled(busy)
                }
            }
            if let alarm {
                let badge = alarm.badge ?? ""
                let note = alarm.note ?? ""
                Text("\(badge) \(note)")
                    .font(.caption2).foregroundStyle(Theme.amber)
            }
            TextField(L10n.t("sfy.beacons.label.ph", state.language),
                      text: $label)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            TextField(L10n.t("sfy.beacons.where.ph", state.language),
                      text: $placement)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Button(L10n.t("sfy.beacons.place", state.language)) { place() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy || label.isEmpty)

            Divider().background(Theme.line)
            Text(L10n.t("att.relay", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let channel {
                Text(L10n.t("att.relay.channel", state.language)
                     + ": \(channel.envelope ?? "")")
                    .font(.caption2).foregroundStyle(Theme.t2)
                Text(channel.note).font(.caption2).foregroundStyle(Theme.t3)
            }
            if let roster {
                let names = roster.roster.joined(separator: ", ")
                Text(L10n.t("att.relay.roster", state.language)
                        .replacingOccurrences(of: "{list}", with: names)
                        .replacingOccurrences(of: "{c}", with: roster.ceiling))
                    .font(.caption2).foregroundStyle(Theme.t2)
                Text(roster.note).font(.caption2).foregroundStyle(Theme.t3)
            }
            if let rota {
                let now = rota.on_now.joined(separator: ", ")
                Text("\(now) · \(rota.timezone)")
                    .font(.caption2)
                    .foregroundStyle(rota.anybody_on_shift ? Theme.green
                                                           : Theme.t3)
                Text(rota.note).font(.caption2).foregroundStyle(Theme.t3)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        channel = try? await ApiClient.shared.relayChannel()
        roster = try? await ApiClient.shared.relayRoster()
        rota = try? await ApiClient.shared.relayRota()
        guard let uid = state.uid, let token = state.token else { return }
        rows = (try? await ApiClient.shared.beacons(uid: uid,
                                                    token: token)) ?? []
    }

    private func run(_ work: @escaping () async throws -> Void) {
        busy = true; error = nil
        Task {
            do { try await work() }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func place() {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            _ = try await ApiClient.shared.placeBeacon(
                uid: uid, token: token,
                label: label.trimmingCharacters(in: .whitespaces),
                placement: placement)
            label = ""; placement = ""
            rows = (try? await ApiClient.shared.beacons(
                uid: uid, token: token)) ?? []
        }
    }

    private func retire(_ bid: String) {
        guard let token = state.token else { return }
        run {
            _ = try await ApiClient.shared.retireBeacon(bid: bid,
                                                        token: token)
            if let uid = state.uid {
                rows = (try? await ApiClient.shared.beacons(
                    uid: uid, token: token)) ?? []
            }
        }
    }

    private func preview(_ bid: String) {
        run {
            card = try await ApiClient.shared.beaconCard(bid: bid)
        }
    }

    private func raise(_ bid: String) {
        run {
            alarm = try await ApiClient.shared.raiseBeaconAlarm(
                bid: bid, situation: nil)
        }
    }

    /// Fetch the stranger's page to prove it is live, then hand it to the
    /// system browser — where a scanner would actually read it.
    private func openPage(_ bid: String) {
        run {
            let html = try await ApiClient.shared.scannedBeaconPage(bid: bid)
            let url = await ApiClient.shared.base
                .appendingPathComponent("/c/\(bid)")
            if !html.isEmpty { openURL(url) }
        }
    }
}
