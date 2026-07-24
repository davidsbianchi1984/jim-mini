import Foundation

// MARK: - Wire models (mirror jim/api.py)

struct EnrollResult: Decodable { let id: String; let display_name: String; let user_token: String }

struct PaceCue: Decodable { let light: String; let audio: String }

struct Pace: Decodable {
    let compressions_per_minute: Int
    let compression_to_breath_ratio: String
    let cue: PaceCue?
}

struct FirstAid: Decodable {
    let kind: String                   // "cpr" | "aed" | ...
    let call_emergency_services: Bool?
    let steps: [String]
    let pace: Pace?
}

struct Evidence: Decodable {
    let publisher: String
    let title: String
    let url: String
    let supports: String?
}

struct Provenance: Decodable {
    let method: String
    let generated_by: String
    let evidence: [Evidence]
    let disclaimer: String
}

struct Guidance: Decodable {
    let delivered: Bool
    let source: String?
    let content: String
    let references: [String]?
    let first_aid: FirstAid?
    let provenance: Provenance?
    let language: String?
    let translation_note: String?
}

struct LanguageInfo: Decodable {
    let code: String
    let label: String
    let safety_content_translated: Bool?
}

struct LanguagesList: Decodable {
    let languages: [LanguageInfo]
    let defaultCode: String
    enum CodingKeys: String, CodingKey {
        case languages
        case defaultCode = "default"
    }
}

struct LanguageChoice: Decodable { let language: String; let label: String }

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

struct ProviderInfo: Decodable {
    let name: String
    let label: String
    let configured: Bool
}

struct ModelsList: Decodable {
    let providers: [ProviderInfo]
    let defaultName: String
    enum CodingKeys: String, CodingKey {
        case providers
        case defaultName = "default"
    }
}

struct ModelChoice: Decodable { let provider: String; let effective: String }

struct EscalationPolicy: Decodable {
    let sensitivity: String
    let ladder: [String]
    let by_severity: [String: String]
}

struct FlowStep: Decodable { let step: String; let label: String; let detail: String }

struct RobotDirective: Decodable { let robot: String; let directive: String }

struct EmergencyResult: Decodable {
    let emergency: Bool
    let flow: [FlowStep]
    let robot_directives: [RobotDirective]?
}

struct RobotSpec: Decodable {
    let model: String
    let label: String
    let maker: String
    let kind: String
    let first_aid: String?             // "perform" | "assist" | nil
}

struct RoboticsCatalog: Decodable { let robots: [RobotSpec] }

struct Robot: Decodable {
    let id: String
    let model: String
    let name: String
    let status: String?
    let escalation_directive: String?
    let first_aid: String?
    let commands: [String]?
}

struct RobotCmdResult: Decodable {
    let status: String
    let note: String?
    let instruction: String?           // perform_cpr confirmation gate
    let spoken: [String]?              // guide_first_aid playbook steps
    let sequence: [String]?            // auto_defib resuscitation sequence
    let pace: Pace?
    let safeguards: [String]?
}

struct WaiverState: Decodable {
    let kind: String
    let terms: [String]
    let signed: Bool
    let signature: String?
    let signed_at: String?
}

struct MedicalCardIssued: Decodable {
    let token: String
    let view_url: String
    let qr_svg_url: String
}

struct SourceRow: Decodable { let source: String; let consented: Bool }

struct SocialConn: Decodable {
    let id: String
    let platform: String
    let direction: String
    let handle: String?
}

struct CatalogApp: Decodable { let app: String; let label: String; let capabilities: [String] }
struct CatalogProvider: Decodable { let provider: String; let label: String; let apps: [CatalogApp] }
struct AppsCatalog: Decodable { let providers: [CatalogProvider] }

struct AppConn: Decodable {
    let id: String
    let provider: String
    let app: String
}

struct MedicalCard: Decodable {
    let name: String?
    let age: Int?
    let known_conditions: [String]?
    let resting_heart_rate: Int?
    let emergency_contact: EmergencyContact?
    struct EmergencyContact: Decodable { let name: String?; let phone: String? }
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

    // MARK: Model selection

    func models() async throws -> ModelsList { try await request("/models") }

    func userModel(uid: String, token: String) async throws -> ModelChoice {
        try await request("/model/\(uid)", token: token)
    }

    func setModel(uid: String, token: String, provider: String) async throws -> ModelChoice {
        try await request("/model/\(uid)", method: "PUT",
                          body: ["provider": provider], token: token)
    }

    // MARK: Language

    func languages() async throws -> LanguagesList { try await request("/languages") }

    func userLanguage(uid: String, token: String) async throws -> LanguageChoice {
        try await request("/language/\(uid)", token: token)
    }

    func setLanguage(uid: String, token: String, code: String) async throws -> LanguageChoice {
        try await request("/language/\(uid)", method: "PUT",
                          body: ["language": code], token: token)
    }

    // MARK: Safety — escalation policy, Emergency, robots

    func escalationPolicy(uid: String, token: String) async throws -> EscalationPolicy {
        try await request("/escalation-policy/\(uid)", token: token)
    }

    func setSensitivity(uid: String, token: String, level: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/sensitivity/\(uid)", method: "PUT",
                                      body: ["level": level], token: token)
    }

    func emergency(uid: String, token: String, situation: String?,
                   location: String?) async throws -> EmergencyResult {
        var body: [String: Any] = [:]
        if let situation, !situation.isEmpty { body["situation"] = situation }
        if let location, !location.isEmpty { body["location"] = location }
        return try await request("/emergency/\(uid)", method: "POST",
                                 body: body, token: token)
    }

    func roboticsCatalog() async throws -> RoboticsCatalog {
        try await request("/robotics/catalog")
    }

    func robots(uid: String, token: String) async throws -> [Robot] {
        try await request("/robots/\(uid)", token: token)
    }

    func bindRobot(uid: String, token: String, model: String) async throws -> Robot {
        try await request("/robots/\(uid)", method: "POST",
                          body: ["model": model], token: token)
    }

    func commandRobot(uid: String, token: String, robotId: String,
                      command: String, arg: String?) async throws -> RobotCmdResult {
        var body: [String: Any] = ["command": command]
        if let arg, !arg.isEmpty { body["arg"] = arg }
        return try await request("/robots/\(uid)/\(robotId)/command",
                                 method: "POST", body: body, token: token)
    }

    // MARK: autonomous-resuscitation waiver

    func waiver(uid: String, token: String) async throws -> WaiverState {
        try await request("/waivers/\(uid)", token: token)
    }

    func signWaiver(uid: String, token: String,
                    signature: String) async throws -> WaiverState {
        struct Signed: Decodable { let signed: Bool }
        _ = try await request("/waivers/\(uid)", method: "POST",
                              body: ["signature": signature, "accept": true],
                              token: token) as Signed
        return try await waiver(uid: uid, token: token)
    }

    func revokeWaiver(uid: String, token: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/waivers/\(uid)", method: "DELETE",
                                      token: token)
    }

    // MARK: Connect — sources, social platforms, connected apps

    func sources(uid: String, token: String) async throws -> [SourceRow] {
        try await request("/sources/\(uid)", token: token)
    }

    func setSource(uid: String, token: String, source: String,
                   consented: Bool) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/sources/\(uid)", method: "PUT",
                                      body: ["source": source,
                                             "consented": consented], token: token)
    }

    func socialConnections(uid: String, token: String) async throws -> [SocialConn] {
        try await request("/social/\(uid)", token: token)
    }

    func socialConnect(uid: String, token: String, platform: String,
                       direction: String, handle: String?) async throws -> SocialConn {
        var body: [String: Any] = ["platform": platform, "direction": direction]
        if let handle, !handle.isEmpty { body["handle"] = handle }
        return try await request("/social/\(uid)", method: "POST", body: body,
                                 token: token)
    }

    func socialCollect(cid: String, token: String, content: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/social/connection/\(cid)/collect",
                                      method: "POST",
                                      body: ["items": [["content": content]]],
                                      token: token)
    }

    func socialPublish(cid: String, token: String, content: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/social/connection/\(cid)/publish",
                                      method: "POST", body: ["content": content],
                                      token: token)
    }

    func appsCatalog() async throws -> AppsCatalog {
        try await request("/connectors/catalog")
    }

    func appConnections(uid: String, token: String) async throws -> [AppConn] {
        try await request("/apps/\(uid)", token: token)
    }

    func appConnect(uid: String, token: String, provider: String,
                    app: String) async throws -> AppConn {
        try await request("/apps/\(uid)", method: "POST",
                          body: ["provider": provider, "app": app], token: token)
    }

    func appCollect(cid: String, token: String, content: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/apps/connector/\(cid)/collect",
                                      method: "POST",
                                      body: ["items": [["content": content]]],
                                      token: token)
    }

    // MARK: Medical ID (first-responder card + QR)

    func issueMedicalCard(uid: String, token: String) async throws -> MedicalCardIssued {
        try await request("/medical-id/qr/\(uid)", method: "POST", token: token)
    }

    func medicalCard(cardToken: String) async throws -> MedicalCard {
        try await request("/medical-id/\(cardToken)")   // public: the card is the credential
    }

    func revokeMedicalCard(uid: String, token: String) async throws {
        var req = URLRequest(url: base.appendingPathComponent("/medical-id/qr/\(uid)"))
        req.httpMethod = "DELETE"
        req.setValue("Bearer \(token)", forHTTPHeaderField: "authorization")
        let (_, resp) = try await URLSession.shared.data(for: req)
        guard let http = resp as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            throw ApiError.http("revoke failed")
        }
    }
}
