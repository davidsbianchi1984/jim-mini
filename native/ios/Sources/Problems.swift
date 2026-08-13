import Foundation

/// What went wrong, recorded without recording anything private.
///
/// The console's `app/src/errors.ts` in this repository. Same rules, same
/// refusals, a different language — and written from that file rather than
/// invented again, so the two cannot drift into disagreeing about what a
/// failure may say about itself.
///
/// Every failed request passes through one place in `ApiClient`, so one call
/// there catches the lot. The hard part is not the catching. The backends put
/// user input straight into their error messages:
///
///     no device called 'Pixel Buds' on this account
///     unknown site 'knee'; one of scalp, face, eye, mouth…
///
/// Good messages for the person reading them, and device names and body sites
/// to anybody else. The message is shown and never written down. The path goes
/// the same way: `/profiles/prf_0de08e794ed0/chat` identifies a person,
/// `POST /profiles/{id}/chat` identifies a bug, and only the second is kept.
///
/// The redaction happens on the way *in*, so there is never a moment when the
/// stored buffer holds something that would later have to be scrubbed.
enum Problems {

    /// One failure, with nothing in it that belongs to anybody.
    struct Problem: Codable {
        /// `POST /profiles/{id}/chat` — the operation, not the instance.
        var op: String
        /// HTTP status, or 0 when the request never reached a server.
        var status: Int
        var count: Int
        /// ISO date only. A timestamp to the second is a movement record.
        var day: String
        var fingerprint: String
        /// How much of `count` has already been reported. A number, not a
        /// flag: a row keeps accumulating after a send, and the next report
        /// owes the difference.
        var sent: Int
    }

    private static let key = "app.problems"
    private static let limit = 50

    /// A segment that identifies a *thing* rather than naming a route.
    /// Deliberately wide: over-redacting costs a little precision in a bug
    /// report, under-redacting costs somebody their privacy, and only one of
    /// those is recoverable. The suffix length is unbounded because an id
    /// minted short is still an id — requiring six hex characters let
    /// `cap_9f2`, `req_77aa` and `usr_1` through when the console's version
    /// of this was first written.
    private static let idLike: [NSRegularExpression] = [
        try! NSRegularExpression(pattern: "^[a-z]{2,8}_[0-9a-z]+$",
                                 options: .caseInsensitive),
        try! NSRegularExpression(
            pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            options: .caseInsensitive),
        try! NSRegularExpression(pattern: "^[0-9]+$"),
        try! NSRegularExpression(pattern: "^[A-Za-z0-9_-]{24,}$"),
    ]

    /// A path with every identifying segment replaced by `{id}`.
    static func redact(_ path: String) -> String {
        let noQuery = path.split(separator: "?", maxSplits: 1,
                                 omittingEmptySubsequences: false)[0]
        return noQuery.split(separator: "/", omittingEmptySubsequences: false)
            .map { seg -> String in
                let s = String(seg)
                guard !s.isEmpty else { return s }
                let range = NSRange(s.startIndex..., in: s)
                let looksLikeAnId = idLike.contains {
                    $0.firstMatch(in: s, range: range) != nil
                }
                return looksLikeAnId ? "{id}" : s
            }
            .joined(separator: "/")
    }

    /// Non-reversible by construction — its input already carries nothing
    /// private. FNV-1a, matching the console so the same failure fingerprints
    /// the same on a phone and on a desktop.
    private static func fingerprint(_ op: String, _ status: Int) -> String {
        var h: UInt32 = 2166136261
        for byte in Array("\(op)|\(status)".utf8) {
            h ^= UInt32(byte)
            h = h &* 16777619
        }
        return String(format: "%08x", h)
    }

    private static func read() -> [Problem] {
        guard let data = UserDefaults.standard.data(forKey: key),
              let rows = try? JSONDecoder().decode([Problem].self, from: data)
        else { return [] }
        return rows
    }

    private static func write(_ rows: [Problem]) {
        // A full or unavailable store is not worth an error of its own. The
        // diagnostic is the least important thing in the app; it must never be
        // the reason something else fails.
        guard let data = try? JSONEncoder().encode(Array(rows.prefix(limit)))
        else { return }
        UserDefaults.standard.set(data, forKey: key)
    }

    /// Record a failure. Takes the method and raw path, never the message.
    ///
    /// The signature is the safeguard: there is no parameter a detail string
    /// could arrive through, so a future caller cannot pass one in a hurry.
    static func record(method: String, path: String, status: Int) {
        let op = "\(method.uppercased()) \(redact(path))"
        let print = fingerprint(op, status)
        let day = ISO8601DateFormatter().string(from: Date()).prefix(10)
        var rows = read()
        if let i = rows.firstIndex(where: { $0.fingerprint == print }) {
            rows[i].count += 1
            rows[i].day = String(day)
            let hit = rows.remove(at: i)
            rows.insert(hit, at: 0)
        } else {
            rows.insert(Problem(op: op, status: status, count: 1,
                                day: String(day), fingerprint: print, sent: 0),
                        at: 0)
        }
        write(rows)
    }

    /// The whole local history, which is the person's own.
    static func all() -> [Problem] { read() }

    static func clear() { UserDefaults.standard.removeObject(forKey: key) }

    // MARK: - Reporting
    //
    // Everything above this line existed for four releases and did half a job.
    // `record` redacts on the way in and `sent` was documented as "how much of
    // `count` has already been reported" — describing a send that was never
    // written. The buffer filled, capped at fifty, and rolled over. Nothing
    // ever read `sent`, because nothing ever reported.
    //
    //     asked     is the failure recorded without recording anything private
    //     mattered  does the failure reach anybody
    //
    // The console's `app/src/errors.ts` had both halves the whole time. This
    // is the second half, written from that file so the two cannot drift.

    /// Which product this is.
    ///
    /// This file is otherwise identical in all three repositories, so it
    /// cannot work this out for itself. Not defaulted: `"unknown"` is a source
    /// the gateway refuses, so a repo that forgot to set it finds out on the
    /// first report rather than filing one app's bugs under another's name.
    static let source = "jim-mini"

    private static let collectorKey = "app.problems.collector"
    private static let sendKey = "app.problems.send"
    private static let noticeKey = "app.problems.notice"

    /// Baked in at build time, from the Info.plist. Absent means an install
    /// with nowhere to send — the default, and a stronger one than a flag:
    /// there is no address for a later mistake to switch on.
    private static func plist(_ name: String) -> String {
        (Bundle.main.object(forInfoDictionaryKey: name) as? String) ?? ""
    }

    /// Where reports go, or "" for nowhere. A stored value wins over the
    /// built-in one so somebody running their own gateway can point at it,
    /// and so anyone can point at nothing by storing an empty string.
    static func collectorUrl() -> String {
        let stored = UserDefaults.standard.string(forKey: collectorKey)
        let raw = stored ?? plist("ProblemCollector")
        return raw.trimmingCharacters(in: .whitespaces)
            .replacingOccurrences(of: "/+$", with: "",
                                  options: .regularExpression)
    }

    static func setCollectorUrl(_ url: String?) {
        if let url { UserDefaults.standard.set(url, forKey: collectorKey) }
        else { UserDefaults.standard.removeObject(forKey: collectorKey) }
    }

    /// On where a collector exists, and off the moment anyone says so.
    static func sendingEnabled() -> Bool {
        UserDefaults.standard.string(forKey: sendKey) != "off"
    }

    static func setSending(_ on: Bool) {
        UserDefaults.standard.set(on ? "on" : "off", forKey: sendKey)
    }

    /// Nothing leaves this device before somebody has been told and answered.
    /// The gate is the notice, not the switch: a switch defaulting to on is a
    /// decision made on the person's behalf.
    static func noticeAnswered() -> Bool {
        UserDefaults.standard.string(forKey: noticeKey) != nil
    }

    static func answerNotice(send: Bool) {
        UserDefaults.standard.set(send ? "yes" : "no", forKey: noticeKey)
        setSending(send)
    }

    /// Exactly what a report contains — shown on screen and posted, both from
    /// here, so a preview cannot drift from the payload.
    ///
    /// `count` is the *unreported remainder*, and rows with nothing left owing
    /// are absent. So this is not a view of the log; it is the message, and
    /// after a successful send it is legitimately empty.
    static func report(appVersion: String = appVersion) -> [String: Any] {
        let owed = read().compactMap { row -> [String: Any]? in
            let remainder = row.count - row.sent
            guard remainder > 0 else { return nil }
            return ["op": row.op, "status": row.status, "count": remainder,
                    "day": row.day, "fingerprint": row.fingerprint]
        }
        return [
            "source": source,
            "app_version": appVersion,
            "platform": "ios",
            "language": Locale.preferredLanguages.first?
                .split(separator: "-").first.map(String.init) ?? "en",
            "problems": owed,
        ]
    }

    /// Advance each row's watermark by what was actually reported.
    ///
    /// By amount, never by flag: a row goes on counting while the request is
    /// in flight, and that growth is still owed. A flag here would silently
    /// drop every occurrence that happened during the send.
    static func markReported(_ report: [String: Any]) {
        guard let sentRows = report["problems"] as? [[String: Any]] else {
            return
        }
        var owed: [String: Int] = [:]
        for row in sentRows {
            if let f = row["fingerprint"] as? String,
               let n = row["count"] as? Int { owed[f] = n }
        }
        write(read().map { row in
            guard let n = owed[row.fingerprint] else { return row }
            var advanced = row
            advanced.sent += n
            return advanced
        })
    }

    /// This build's version, from the bundle that shipped it.
    ///
    /// Not a constant in the source: a version written down in two places is a
    /// version that disagrees with itself by the second release.
    static var appVersion: String {
        let short = plist("CFBundleShortVersionString")
        return short.isEmpty ? "0.0.0" : short
    }

    enum SendOutcome: String {
        case sent, nothingToSend, turnedOff, noCollector, awaitingNotice, failed
    }

    /// Post what is owed. Never throws, never blocks anything.
    ///
    /// The gateway answers 422 when a report is not the shape it expects,
    /// which would mean this build's redaction has stopped working. That is a
    /// refusal and not a retry: the watermark stays put, nothing is marked
    /// sent, and the next launch tries again with whatever the fix ships.
    ///
    /// Deliberately not routed through `ApiClient`: that records a problem on
    /// every failure, so a failing collector would write a new row each launch
    /// — a log that fills with the story of its own delivery and nothing else.
    @discardableResult
    static func send(appVersion: String = appVersion) async -> SendOutcome {
        let base = collectorUrl()
        guard !base.isEmpty else { return .noCollector }
        guard noticeAnswered() else { return .awaitingNotice }
        guard sendingEnabled() else { return .turnedOff }
        let payload = report(appVersion: appVersion)
        guard let rows = payload["problems"] as? [[String: Any]],
              !rows.isEmpty else { return .nothingToSend }
        // `appendingPathComponent` rather than string splicing, so the route
        // audit can read this call — the send was invisible to it before.
        guard let baseUrl = URL(string: base) else { return .failed }
        let url = baseUrl.appendingPathComponent("/v1/problems")
        guard
              let body = try? JSONSerialization.data(withJSONObject: payload)
        else { return .failed }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "content-type")
        let token = plist("ProblemToken")
        if !token.isEmpty {
            request.setValue("Bearer \(token)",
                             forHTTPHeaderField: "Authorization")
        }
        request.httpBody = body
        request.timeoutInterval = 10

        guard let (_, response) = try? await URLSession.shared.data(for: request),
              let http = response as? HTTPURLResponse,
              (200..<300).contains(http.statusCode)
        else { return .failed }
        markReported(payload)
        return .sent
    }
}
