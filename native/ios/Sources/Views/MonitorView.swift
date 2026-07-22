import SwiftUI

/// Live Monitoring: push a heart-rate / stress sample -> POST /monitor, show
/// whether the Guardian detected anything and any guidance it delivered.
struct MonitorView: View {
    @EnvironmentObject var state: AppState
    @State private var heartRate = 72.0
    @State private var stress = 0.2
    @State private var result: MonitorResult?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Live Monitoring").font(.title2.bold()).foregroundStyle(Theme.txt)
                Text("Send a sample. The Guardian compares it to your baseline.")
                    .font(.footnote).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 18) {
                    slider("Heart rate", value: $heartRate, range: 40...180, unit: "bpm", tint: Theme.red)
                    slider("Stress", value: $stress, range: 0...1, unit: "", tint: Theme.amber, percent: true)
                }.card()

                Button(action: send) {
                    HStack { if busy { ProgressView().tint(.white) }; Text("Send sample").bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 13))
                }.disabled(busy)

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                if let r = result {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack(spacing: 8) {
                            Circle().fill(r.detected ? Theme.red : Theme.green).frame(width: 9, height: 9)
                            Text(r.detected ? (r.condition ?? "Detected").capitalized : "All clear")
                                .font(.headline).foregroundStyle(Theme.txt)
                            if let sev = r.severity {
                                Text(sev.uppercased()).font(.caption2.bold())
                                    .padding(.horizontal, 7).padding(.vertical, 3)
                                    .background(Theme.red.opacity(0.16)).foregroundStyle(Theme.red)
                                    .clipShape(Capsule())
                            }
                        }
                        if let reason = r.reason { Text(reason).font(.footnote).foregroundStyle(Theme.t2) }
                        if let g = r.guidance {
                            Divider().overlay(Theme.line)
                            Text(g.content).font(.subheadline).foregroundStyle(Theme.txt)
                            if let src = g.source {
                                Text("via \(src)").font(.caption).foregroundStyle(Theme.t3)
                            }
                        }
                    }.card()
                }
            }.padding(20)
        }
    }

    private func slider(_ label: String, value: Binding<Double>, range: ClosedRange<Double>,
                        unit: String, tint: Color, percent: Bool = false) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(label).foregroundStyle(Theme.txt)
                Spacer()
                Text(percent ? "\(Int(value.wrappedValue * 100))%" : "\(Int(value.wrappedValue)) \(unit)")
                    .foregroundStyle(tint).bold().monospacedDigit()
            }.font(.subheadline)
            Slider(value: value, in: range).tint(tint)
        }
    }

    private func send() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do { result = try await ApiClient.shared.monitor(uid: uid, token: token,
                                                              heartRate: Int(heartRate), stress: stress) }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
