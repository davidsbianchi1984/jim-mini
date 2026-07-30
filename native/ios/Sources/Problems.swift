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
}
