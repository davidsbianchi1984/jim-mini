import SwiftUI

/// The notice that has to be answered before anything leaves the device, and
/// the switch that turns it off afterwards.
///
/// The sending half landed last round and answers `.awaitingNotice` on every
/// launch, because there was no surface to answer it on. That is the safe
/// direction to be wrong in, and it is still wrong: a mechanism nobody can
/// reach is a mechanism nobody chose.
///
/// Two rules this card exists to keep:
///
/// * **Show the report, do not describe it.** A card that says "we collect
///   anonymous diagnostics" is asking somebody to take our word for it.
///   `Problems.report` is the same function the sender posts, so what is on
///   screen is the payload, byte for byte. A preview that could drift from
///   the message would be worse than no preview, because it would look like
///   a promise.
/// * **No pre-ticked answer.** Neither button is styled as the expected one
///   and neither is focused by default. A dialog with a bright Yes and a grey
///   No has made the choice already.
struct ProblemReportingCard: View {
    @EnvironmentObject var state: AppState
    @State private var answered = Problems.noticeAnswered()
    @State private var sending = Problems.sendingEnabled()
    @State private var showing = false

    private var rows: [[String: Any]] {
        (Problems.report()["problems"] as? [[String: Any]]) ?? []
    }


    @State private var readerKey = ""
    @State private var serverRows: [ApiClient.ProblemRow]? = nil
    @State private var serverText = ""

    private func fetchRows() {
        Task {
            do {
                let r = try await ApiClient.shared.problemRows(key: readerKey)
                serverRows = r.rows
                serverText = r.rows.map {
                    "\($0.op)  \($0.status_code)  ×\($0.count)  " +
                    "\($0.source) \($0.app_version) · \($0.platform) · \($0.day)"
                }.joined(separator: "\n")
            } catch {
                serverRows = []
                serverText = ""
            }
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.pr", state.language)).font(.headline)
                .foregroundStyle(Theme.txt)

            if Problems.collectorUrl().isEmpty {
                // Not a failure and not a thing to hide. This build has no
                // address compiled in, so there is nothing to consent to.
                Text(L10n.t("ns.pr.nowhere", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)
            } else if !answered {
                Text(L10n.t("ns.pr.explain", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)
                HStack(spacing: 10) {
                    Button(L10n.t("ns.pr.send", state.language)) { answer(true) }
                        .buttonStyle(.bordered)
                    Button(L10n.t("ns.pr.dont", state.language)) { answer(false) }
                        .buttonStyle(.bordered)
                }
            } else {
                Toggle(isOn: Binding(get: { sending },
                                     set: { on in sending = on
                                            Problems.setSending(on) })) {
                    Text(L10n.t("ns.pr.toggle", state.language)).font(.subheadline)
                        .foregroundStyle(Theme.txt)
                }
                .tint(Theme.brandA)
            }

            Button(L10n.t(showing ? "ns.pr.hide" : "ns.pr.show", state.language)) { showing.toggle() }
                .font(.caption).foregroundStyle(Theme.brandA)

            if showing {
                if rows.isEmpty {
                    Text(L10n.t("ns.pr.owed", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                } else {
                    ForEach(rows.indices, id: \.self) { i in
                        let r = rows[i]
                        Text("\(r["op"] as? String ?? "") → "
                             + "\(r["status"] as? Int ?? 0)  ×"
                             + "\(r["count"] as? Int ?? 0)  \(r["day"] as? String ?? "")")
                            .font(.system(.caption2, design: .monospaced))
                            .foregroundStyle(Theme.t2)
                    }
                }
            }
            // The other end of the wire: what has reached this deployment's
            // own backend, from every client of it. Reading needs the
            // problems key (or a caller on the backend's machine); a
            // refusal is rendered verbatim.
            Divider()
            Text(L10n.t("prob.server", state.language))
                .font(.subheadline).foregroundStyle(Theme.txt)
            HStack(spacing: 8) {
                SecureField(L10n.t("prob.key.ph", state.language),
                            text: $readerKey)
                    .font(.footnote)
                Button(L10n.t("prob.fetch", state.language)) { fetchRows() }
                    .buttonStyle(.bordered).font(.footnote)
            }
            if let serverRows {
                Text(serverRows.isEmpty
                     ? L10n.t("prob.none", state.language) : serverText)
                    .font(.caption2.monospaced()).foregroundStyle(Theme.t2)
            }

        }
        .padding(14)
        .background(Theme.card).clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private func answer(_ send: Bool) {
        Problems.answerNotice(send: send)
        answered = true
        sending = send
        // Answering yes is the first moment a send is permitted. Doing it here
        // rather than waiting for the next launch means the person who just
        // agreed sees the buffer drain while the card is still in front of
        // them, instead of being told something happened later.
        if send { Task { await Problems.send() } }
    }
}
