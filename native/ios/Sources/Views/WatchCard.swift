import SwiftUI
import UniformTypeIdentifiers

/// The watch on the wrist: the drip channel's setup card, per wearable
/// family, plus the local pairing address. No app to install — an
/// automation drips readings to the address. Console door since 0.6.0;
/// this is the phone's.
struct WatchCard: View {
    @EnvironmentObject var state: AppState
    @State private var setup: WatchSetup?
    @State private var pair: PairInfo?
    @State private var showSteps = false
    @State private var importing = false
    @State private var busy = false
    @State private var error: String?
    @State private var dripValue = ""
    @State private var dripAck: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.wt.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.wt.lead", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)

            if let setup {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(setup.devices, id: \.key) { device in
                            Button(device.name) { load(device: device.key) }
                                .font(.caption2)
                                .foregroundStyle(setup.device == device.key
                                                 ? .white : Theme.t2)
                                .padding(.horizontal, 10).padding(.vertical, 6)
                                .background(setup.device == device.key
                                            ? Theme.brandA : Theme.scrBot)
                                .clipShape(Capsule())
                        }
                    }
                }
                Text(L10n.t("ns.wt.address", state.language))
                    .font(.caption2.bold()).foregroundStyle(Theme.t2)
                Text(setup.drip_url)
                    .font(.caption2.monospaced()).foregroundStyle(Theme.txt)
                    .textSelection(.enabled)
                let line = "\(setup.drips)" + " · " + (setup.last_drip_at ?? "—")
                Text(line)
                    .font(.caption2).foregroundStyle(Theme.t3)
                // One reading by hand, through the same door the
                // automation uses — the cheapest proof the tether is live.
                HStack(spacing: 8) {
                    TextField(L10n.t("ns.wt.drip.ph", state.language),
                              text: $dripValue)
                        .font(.caption2)
                    Button(L10n.t("ns.wt.drip.now", state.language)) { drip() }
                        .font(.caption2).foregroundStyle(Theme.brandA)
                        .disabled(busy || Int(dripValue) == nil)
                }
                if let dripAck {
                    Text(dripAck).font(.caption2).foregroundStyle(Theme.t2)
                }
                HStack {
                    Button(L10n.t("ns.wt.setup", state.language)) {
                        showSteps.toggle()
                    }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    // Rotating invalidates the old drip token.
                    Button(L10n.t("ns.bas.reset", state.language)) { rotate() }
                        .font(.caption2).foregroundStyle(Theme.red)
                        .disabled(busy)
                    Button(L10n.t("ns.wt.seed", state.language)) {
                        importing = true
                    }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy)
                }
                if showSteps {
                    ForEach(Array(setup.steps.enumerated()), id: \.offset) { index, step in
                        Text("\(index + 1). \(step)")
                            .font(.caption2).foregroundStyle(Theme.t2)
                    }
                }
                Text(setup.seed_hint)
                    .font(.caption2).foregroundStyle(Theme.t3)
            }

            if let pair {
                // The pairing card's own words, straight from the wire.
                ForEach(Array(pair.how.enumerated()), id: \.offset) { _, line in
                    Text(line).font(.caption2.bold())
                        .foregroundStyle(Theme.t2)
                }
                Text(pair.console_url)
                    .font(.caption2.monospaced()).foregroundStyle(Theme.txt)
                    .textSelection(.enabled)
                Text(pair.note).font(.caption2).foregroundStyle(Theme.t3)
                Text(L10n.t("qr.addr", state.language) + " "
                     + ApiClient.shared.pairQrUrl().absoluteString)
                    .font(.caption2.monospaced()).foregroundStyle(Theme.t3)
                    .textSelection(.enabled)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await initial() }
        .fileImporter(isPresented: $importing,
                      allowedContentTypes: [.zip, .xml, .data]) { result in
            if case .success(let url) = result { seed(url) }
        }
    }

    private func initial() async {
        pair = try? await ApiClient.shared.pairInfo()
        guard let uid = state.uid, let token = state.token else { return }
        setup = try? await ApiClient.shared.watchSetup(uid: uid, token: token)
    }

    private func load(device: String) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            // The card is per-family; the query rides the same route.
            setup = try? await ApiClient.shared.watchSetup(
                uid: uid, token: token, device: device)
        }
    }

    private func drip() {
        guard let setup, let hr = Int(dripValue),
              let token = setup.drip_url.split(separator: "/").last
        else { return }
        busy = true
        Task {
            do {
                let ack = try await ApiClient.shared.watchDrip(
                    dripToken: String(token), heartRate: hr)
                dripAck = L10n.t(ack.noticed ? "ns.wt.drip.noticed"
                                             : "ns.wt.drip.ok",
                                 state.language)
                    .replacingOccurrences(of: "{n}", with: String(ack.received))
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func rotate() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                setup = try await ApiClient.shared.rotateWatchChannel(
                    uid: uid, token: token)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func seed(_ url: URL) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                let accessing = url.startAccessingSecurityScopedResource()
                defer { if accessing { url.stopAccessingSecurityScopedResource() } }
                let data = try Data(contentsOf: url)
                try await ApiClient.shared.seedWatch(uid: uid, token: token,
                                                     data: data)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
