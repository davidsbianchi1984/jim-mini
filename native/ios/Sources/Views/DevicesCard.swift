import SwiftUI

/// Physical embodiments: the speakers, glasses, wearables and screens
/// paired to this Guardian. Register in the person's own words; the kind
/// vocabulary is the server's. Console door since 0.19.x; this is the
/// phone's.
struct DevicesCard: View {
    @EnvironmentObject var state: AppState
    @State private var rows: [DeviceRow] = []
    @State private var name = ""
    @State private var kind = "speaker"
    @State private var paired = true
    @State private var busy = false
    @State private var error: String?

    // The server's DeviceRegister kinds, shown in its own words like the
    // mic types are.
    private let kinds = ["wearable", "stationary", "autonomous", "speaker",
                         "phone", "glasses", "headset", "spatial", "other"]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.dv.bluetooth", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            ForEach(rows, id: \.id) { row in
                HStack {
                    Text("\(row.name) · \(row.kind)")
                        .font(.caption2).foregroundStyle(Theme.txt)
                    if row.paired {
                        Text(L10n.t("ns.dv.paired", state.language))
                            .font(.caption2).foregroundStyle(Theme.green)
                    }
                }
            }
            TextField("", text: $name)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(kinds, id: \.self) { choice in
                        Button(choice) { kind = choice }
                            .font(.caption2)
                            .foregroundStyle(kind == choice ? .white : Theme.t2)
                            .padding(.horizontal, 10).padding(.vertical, 6)
                            .background(kind == choice ? Theme.brandA
                                                       : Theme.scrBot)
                            .clipShape(Capsule())
                    }
                }
            }
            Toggle(isOn: $paired) {
                Text(L10n.t("ns.dv.paired", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            Button(L10n.t("ns.dv.bluetooth", state.language)) { register() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy || name.isEmpty)
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        rows = (try? await ApiClient.shared.devices(uid: uid,
                                                    token: token)) ?? []
    }

    private func register() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.registerDevice(
                    uid: uid, token: token,
                    name: name.trimmingCharacters(in: .whitespaces),
                    kind: kind, paired: paired)
                name = ""
            } catch { self.error = error.localizedDescription }
            busy = false
            await load()
        }
    }
}
