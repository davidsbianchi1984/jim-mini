import Foundation

// MARK: - Wire models (mirror jim/api.py)

struct EnrollResult: Decodable { let id: String; let display_name: String; let user_token: String }

struct Guidance: Decodable {
    let delivered: Bool
    let source: String?
    let content: String
    let references: [String]?
}

struct MonitorResult: Decodable {
    let detected: Bool
    let condition: String?
    let severity: String?
    let reason: String?
    let guidance: Guidance?
}

struct CheckinGuardian: Decodable { let detected: Bool; let guidance: Guidance? }
struct CheckinResult: Decodable {
    let id: String
    let mood: Int
    let energy: Int
    let guardian: CheckinGuardian
}

struct BaselineMetric: Decodable {
    let metric: String
    let value: Double?
    let state: String?
    let samples: Int?
}

struct Health: Decodable { let status: String; let tandem: Bool }

struct Goal: Decodable {
    let id: String
    let area: String
    let title: String
    let target: String?
    let status: String?
}

struct Habit: Decodable {
    let id: String
    let name: String
    let streak: Int?
}

struct JournalItem: Decodable {
    let id: String
    let text: String?
    let created_at: String?
}

// MARK: - Client

enum ApiError: LocalizedError {
    case http(String)
    var errorDescription: String? { if case let .http(m) = self { return m }; return nil }
}

/// Async client for the JIM Guardian backend. Defaults to the local dev server;
/// the iOS Simulator shares the host's network, so 127.0.0.1 resolves to your Mac.
actor ApiClient {
    static let shared = ApiClient()
    var base = URL(string: "http://127.0.0.1:8000")!

    func setBase(_ s: String) {
        if let u = URL(string: s.hasSuffix("/") ? String(s.dropLast()) : s) { base = u }
    }

    private func request<T: Decodable>(_ path: String, method: String = "GET",
                                       body: [String: Any]? = nil, token: String? = nil) async throws -> T {
        var req = URLRequest(url: base.appendingPathComponent(path))
        req.httpMethod = method
        req.setValue("application/json", forHTTPHeaderField: "content-type")
        if let token { req.setValue("Bearer \(token)", forHTTPHeaderField: "authorization") }
        if let body { req.httpBody = try JSONSerialization.data(withJSONObject: body) }

        let (data, resp) = try await URLSession.shared.data(for: req)
        guard let http = resp as? HTTPURLResponse else { throw ApiError.http("No response") }
        guard (200..<300).contains(http.statusCode) else {
            let detail = (try? JSONSerialization.jsonObject(with: data) as? [String: Any])?["detail"] as? String
            throw ApiError.http(detail ?? "HTTP \(http.statusCode)")
        }
        return try JSONDecoder().decode(T.self, from: data)
    }

    func health() async throws -> Health { try await request("/health") }

    func enroll(name: String, birthdate: String) async throws -> EnrollResult {
        try await request("/enroll", method: "POST",
                          body: ["display_name": name, "birthdate": birthdate, "terms_consent": true])
    }

    func monitor(uid: String, token: String, heartRate: Int, stress: Double) async throws -> MonitorResult {
        try await request("/monitor/\(uid)", method: "POST",
                          body: ["heart_rate": heartRate, "stress_level": stress], token: token)
    }

    func checkin(uid: String, token: String, mood: Int, energy: Int, note: String) async throws -> CheckinResult {
        try await request("/checkin/\(uid)", method: "POST",
                          body: ["mood": mood, "energy": energy, "note": note], token: token)
    }

    func coach(uid: String, token: String, area: String, message: String) async throws -> Guidance {
        try await request("/coach/\(uid)", method: "POST",
                          body: ["area": area, "message": message], token: token)
    }

    func baseline(uid: String, token: String) async throws -> [BaselineMetric] {
        try await request("/baseline/\(uid)", token: token)
    }

    // MARK: Life — goals, habits, journal

    func goals(uid: String, token: String) async throws -> [Goal] {
        try await request("/goals/\(uid)", token: token)
    }

    func addGoal(uid: String, token: String, area: String, title: String,
                 target: String?) async throws -> Goal {
        var body: [String: Any] = ["area": area, "title": title]
        if let target, !target.isEmpty { body["target"] = target }
        return try await request("/goals/\(uid)", method: "POST", body: body, token: token)
    }

    func habits(uid: String, token: String) async throws -> [Habit] {
        try await request("/habits/\(uid)", token: token)
    }

    func addHabit(uid: String, token: String, name: String) async throws -> Habit {
        try await request("/habits/\(uid)", method: "POST", body: ["name": name], token: token)
    }

    func logHabit(uid: String, token: String, habitId: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/habits/\(uid)/\(habitId)/log", method: "POST", token: token)
    }

    func journal(uid: String, token: String) async throws -> [JournalItem] {
        try await request("/journal/\(uid)", token: token)
    }

    func addJournal(uid: String, token: String, text: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/journal/\(uid)", method: "POST", body: ["text": text], token: token)
    }
}
