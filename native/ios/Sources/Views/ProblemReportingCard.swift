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
    @State private var answered = Problems.noticeAnswered()
    @State private var sending = Problems.sendingEnabled()
    @State private var showing = false

    private var rows: [[String: Any]] {
        (Problems.report()["problems"] as? [[String: Any]]) ?? []
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("When something breaks").font(.headline)
                .foregroundStyle(Theme.txt)

            if Problems.collectorUrl().isEmpty {
                // Not a failure and not a thing to hide. This build has no
                // address compiled in, so there is nothing to consent to.
                Text("This build reports nowhere. Failures are counted on this "
                     + "device and never leave it.")
                    .font(.footnote).foregroundStyle(Theme.t2)
            } else if !answered {
                Text("This app can send a count of what failed — the operation "
                     + "and the HTTP status, the day it happened, and how many "
                     + "times. Not what you typed, not who you are, not which "
                     + "profile. Nothing that identifies you or anyone else.")
                    .font(.footnote).foregroundStyle(Theme.t2)
                HStack(spacing: 10) {
                    Button("Send counts") { answer(true) }
                        .buttonStyle(.bordered)
                    Button("Do not send") { answer(false) }
                        .buttonStyle(.bordered)
                }
            } else {
                Toggle(isOn: Binding(get: { sending },
                                     set: { on in sending = on
                                            Problems.setSending(on) })) {
                    Text("Send failure counts").font(.subheadline)
                        .foregroundStyle(Theme.txt)
                }
                .tint(Theme.brandA)
            }

            Button(showing ? "Hide what would be sent"
                           : "Show what would be sent") { showing.toggle() }
                .font(.caption).foregroundStyle(Theme.brandA)

            if showing {
                if rows.isEmpty {
                    Text("Nothing is owed. Either nothing has failed, or "
                         + "everything that has was already reported.")
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
