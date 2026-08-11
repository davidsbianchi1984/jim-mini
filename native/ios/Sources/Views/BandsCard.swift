import SwiftUI

/// Baseline bands: *your* normal, and how far from it counts. Crossing a
/// band is a check-in, never an escalation — the alarm layer lives
/// elsewhere and is untouched from here. Console door since 0.6.0; this
/// is the phone's.
struct BandsCard: View {
    @EnvironmentObject var state: AppState
    @State private var bands: [BandRow] = []
    @State private var busy: String?
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.bas.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.bas.sub", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)

            if bands.isEmpty {
                Text(L10n.t("ns.bas.none", state.language))
                    .font(.caption2).foregroundStyle(Theme.t3)
            }
            ForEach(bands, id: \.metric) { band in
                bandRow(band)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    @ViewBuilder
    private func bandRow(_ band: BandRow) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(band.label).font(.caption.bold())
                    .foregroundStyle(Theme.txt)
                Spacer()
                Text("±\(trim(band.margin))\(band.unit)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            if band.provisional {
                Text(L10n.t("ns.bas.learning", state.language)
                        .replacingOccurrences(of: "{n}",
                                              with: String(band.samples)))
                    .font(.caption2).foregroundStyle(Theme.t3)
            } else {
                Text(L10n.t("ns.bas.usual", state.language)
                        .replacingOccurrences(of: "{v}",
                            with: "\(trim(band.baseline ?? 0))\(band.unit)")
                        .replacingOccurrences(of: "{lo}",
                            with: "\(trim(band.low_edge ?? 0))\(band.unit)")
                        .replacingOccurrences(of: "{hi}",
                            with: "\(trim(band.high_edge ?? 0))\(band.unit)"))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack(spacing: 10) {
                // Narrower is told sooner; wider tolerates a wanderer.
                Button("−") { nudge(band, by: -step(band)) }
                    .font(.caption.bold()).foregroundStyle(Theme.brandA)
                    .disabled(busy == band.metric
                              || band.margin - step(band) <= 0)
                Button("+") { nudge(band, by: step(band)) }
                    .font(.caption.bold()).foregroundStyle(Theme.brandA)
                    .disabled(busy == band.metric)
                Toggle(isOn: binding(band, low: true)) {
                    Text(L10n.t("ns.bas.drop", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                .toggleStyle(.button)
                .disabled(busy == band.metric)
                Toggle(isOn: binding(band, low: false)) {
                    Text(L10n.t("ns.bas.climb", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                .toggleStyle(.button)
                .disabled(busy == band.metric)
                if band.source == "user" {
                    Button(L10n.t("ns.bas.reset", state.language)) {
                        reset(band)
                    }
                    .font(.caption2).foregroundStyle(Theme.t3)
                    .disabled(busy == band.metric)
                }
            }
        }
    }

    private func trim(_ value: Double) -> String {
        value == value.rounded() ? String(Int(value))
                                 : String(format: "%.1f", value)
    }

    private func step(_ band: BandRow) -> Double {
        band.unit == "°C" ? 0.1 : 0.5
    }

    private func binding(_ band: BandRow, low: Bool) -> Binding<Bool> {
        Binding(
            get: { low ? band.watch_low : band.watch_high },
            set: { value in
                change(band, margin: nil,
                       watchHigh: low ? nil : value,
                       watchLow: low ? value : nil)
            })
    }

    private func nudge(_ band: BandRow, by delta: Double) {
        change(band, margin: max(0.1, band.margin + delta),
               watchHigh: nil, watchLow: nil)
    }

    private func change(_ band: BandRow, margin: Double?,
                        watchHigh: Bool?, watchLow: Bool?) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = band.metric; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.setBand(
                    uid: uid, token: token, metric: band.metric,
                    margin: margin, watchHigh: watchHigh, watchLow: watchLow)
            } catch { self.error = error.localizedDescription }
            busy = nil
            await load()
        }
    }

    private func reset(_ band: BandRow) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = band.metric; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.resetBand(
                    uid: uid, token: token, metric: band.metric)
            } catch { self.error = error.localizedDescription }
            busy = nil
            await load()
        }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        bands = (try? await ApiClient.shared.bands(uid: uid,
                                                   token: token))?.bands ?? []
    }
}
