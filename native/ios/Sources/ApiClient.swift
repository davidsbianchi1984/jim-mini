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

struct Custody: Decodable {
    let vaulted: Bool                  // sealed in the PDI vault?
    let pdi_key: String?               // provenance lookup handle in PDI
    let note: String?                  // honest report when sealing failed
}

struct Guidance: Decodable {
    let delivered: Bool
    let source: String?                // "local" | "tandem"
    let content: String
    let references: [String]?
    let first_aid: FirstAid?
    let provenance: Provenance?
    let language: String?
    let translation_note: String?
    let specialist: String?            // named expert behind this condition
    // The *offer*, distinct from the line above: `specialist` is a name the
    // monitoring path fills in, this is whether one is available to ask.
    let specialist_offer: SpecialistOffer?
    let qrme_profile_id: String?       // set when routed tandem via QRME
    let custody: Custody?              // tandem exchanges sealed in PDI
}

// The offline coach's store and syllabus (jim/pipeline.py): what the
// stack predicts from, what JIM should study next, and what one press
// of study did.
// MARK: - engaged sessions (jim/engaged.py)
//
// `coach` above is a turn. These are a session: open until sign-off, able to
// act on this person's own records while it is open, and every act landing on
// a trail with the request that would take it back.
//
// `reversible` and `irreversible_because` are carried separately rather than
// derived from one another. An act that acted and can no longer be taken back
// is a real third state — already undone, or one whose way back the backend
// could not build — and a screen rendering `!reversible` as "irreversible"
// would tell somebody their journal entry had left the app.

struct EngagedTool: Decodable, Identifiable {
    let name: String
    let says: String
    let acts: Bool
    let reversible: Bool
    let irreversible_because: String?
    var id: String { name }
}

struct EngagedReach: Decodable {
    let can: [EngagedTool]
    let tools_per_turn: Int
    let acts_per_session: Int
    let watch_ceiling: Int
}

struct EngagedStep: Decodable, Identifiable {
    let tool: String?
    let answered: Int?
    let says: String?
    let acts: Bool?
    let reversible: Bool?
    let irreversible_because: String?
    let refused: String?
    var id: String { (tool ?? "?") + (refused ?? "") + String(answered ?? 0) }
}

struct EngagedAct: Decodable, Identifiable {
    let id: String
    let tool: String
    let says: String
    let answered: Int
    let created_at: String
    let undone_at: String?
    let reversible: Bool
    let irreversible_because: String?
}

struct StandingWatch: Decodable, Identifiable {
    let id: String
    let topic: String
    let area: String?
    let created_at: String
    let cleared_at: String?
    let engagement_id: String?
}

struct EngagedSessionTurn: Decodable, Identifiable {
    let role: String
    let content: String
    let created_at: String
    var id: String { created_at + role }
}

struct EngagedSession: Decodable {
    let engaged: Bool
    let id: String?
    let area: String?
    let opened_at: String?
    let turns: [EngagedSessionTurn]
    let acted: [EngagedAct]
    let watches: [StandingWatch]
}

struct EngagedProvenance: Decodable {
    let generated_by: String
    let degraded: Bool
    let degraded_reason: String?
}

struct EngagedTurnResult: Decodable {
    let engagement_id: String
    let reply: String
    // `did`, not `acted`: a session's `acted` is the trail of completed
    // changes, and a turn's list includes refusals, which are not acts. One
    // name may not carry two shapes on the wire.
    let did: [EngagedStep]
    let stopped: String?
    let engaged: Bool
    let watches: [StandingWatch]
    let provenance: EngagedProvenance
}

struct EngagedSignOff: Decodable {
    let engagement_id: String
    let signed_off: Bool
    let deposited: Int
    let watches: [StandingWatch]
    let acted: [EngagedAct]
}

struct EngagedUndone: Decodable {
    let act_id: String
    let undone: Bool
    let answered: Int
    let tool: String
    let says: String
}

/// The acknowledgement every `remove` door answers with. One shape rather
/// than five near-identical ones: what a caller reads is `removed`, and the
/// id it echoes back is already the id the caller sent.
struct Removed: Decodable { let removed: Bool }

/// What a habit's day answers with, ticked or unticked. `streak` is
/// recomputed rather than adjusted — removing a day out of the middle does
/// not shorten a streak by one, it breaks it.
struct HabitLogged: Decodable {
    let habit_id: String
    let day: String
    let streak: Int
}

struct WatchCleared: Decodable {
    let watch_id: String
    let cleared: Bool
    let topic: String
}

struct CoachStoreEntry: Decodable {
    let topic: String
    let lesson: String
    let source: String
    let model: String?
    let area: String?
}

struct CoachStore: Decodable {
    let pack: Int
    let excursions: [CoachStoreEntry]
    let deposits: [CoachStoreEntry]
}

struct CoachSuggestion: Decodable {
    let area: String
    let topic: String
    let why: String
}

struct CoachCurriculum: Decodable {
    let suggested: [CoachSuggestion]
    let note: String
}

struct CoachStudied: Decodable {
    let studied: String
    let folded: Bool
    let left_host: Bool
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

struct LanguageChoice: Decodable { let language: String; let label: String; let mode: String? }

struct TranslateResult: Decodable {
    let text: String
    let translation: String
    let language: String
    let engine: String                 // "hand" | provider name | "stub" | "none"
    let note: String?
}

struct CustodyList: Decodable {
    let records: [String]
    let count: Int
    let chain_intact: Bool?
}

struct CustodyProvenance: Decodable {
    struct Sealed: Decodable { let cipher: String?; let created_at: String? }
    struct Audit: Decodable { let count: Int? }
    struct Chain: Decodable { let intact: Bool? }
    let key: String
    let origin: String
    let sealed: Sealed?
    let audit: Audit?
    let chain: Chain?
}

struct ChildCreated: Decodable {
    let id: String
    let child_token: String            // shown once: goes on the child's device
    let oversight: String              // "full" | "alerts_only"
    let sensitivity: String?
    let emergency_contact: String?
}

struct ChildSummary: Decodable {
    let child_id: String
    let display_name: String
    let age: Int
    let relationship: String
    let oversight: String              // full | alerts_only | ended
}

struct ChildEvent: Decodable {
    let type: String
    let condition: String?
    let severity: String?
    let created_at: String
}

struct ChildOverview: Decodable {
    let child_id: String
    let display_name: String?
    let age: Int?
    let oversight: String
    let critical_events: Int?
    let events: [ChildEvent]?
    let privacy_note: String?
    let note: String?                  // set when oversight has ended
}

struct FamilyControlsState: Decodable {
    let paused: Bool
    let quiet_start: String?
    let quiet_end: String?
    let note: String?
}

struct GuardianChild: Decodable {
    let child_id: String
    let display_name: String
    let light: String                  // green | orange | red | idle
    let critical_24h: Int?
    let escalations_24h: Int?
    let paused: Bool?
    let quiet_hours: String?
}

struct GuardianFace: Decodable {
    let children: [GuardianChild]
    let haptic: String?                // "alert" when a child needs someone
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

/// The user's own QRME profile, as this shell reads it.
///
/// `brief` is deliberately `[String: AnyDecodable]`-free: the preview is shown
/// as the message itself, so the shell renders the server's JSON rather than a
/// model that could quietly drop a category the server had decided to send.
struct SelfProfileStatus: Decodable {
    var linked: Bool
    var profileId: String?
    var consented: [String]

    enum CodingKeys: String, CodingKey {
        case linked
        case profileId = "profile_id"
        case consented
    }
}

struct SelfProfilePreview: Decodable {
    var linked: Bool
    var consented: [String]?
    var empty: Bool?
}

struct SelfProfileSent: Decodable {
    var sent: Bool
}

struct Habit: Decodable {
    let id: String
    let name: String
    let streak: Int?
}

struct Meal: Decodable, Identifiable {
    let id: String
    let note: String?
    let logged: String
    let described_by: String
    let photo_sealed: Bool
    let created_at: String?
}

struct Drill: Decodable, Identifiable {
    let id: String
    let kind: String
    let question: String
    let probes: [String]?
    let critique: String?
    let described_by: String?
    let answered_at: String?
}

struct Letter: Decodable, Identifiable {
    let id: String
    let week_start: String
    let body: String
    let described_by: String
    let created_at: String?
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

/// An open alarm, raised when somebody scanned a care code on a door.
///
/// `accepted_by` is the whole point of the type. `accept` and `clear` are
/// different acts and the backend keeps them apart deliberately — accepting
/// says somebody is coming, clearing says it is over. An alarm that has been
/// accepted is still `open`, and this shell must show it that way, because
/// conflating the two is how an alarm gets marked handled by the act of being
/// seen.
struct AlarmRow: Decodable, Identifiable {
    let id: String
    let beacon_id: String?
    let messages: [String]?
    let state: String
    let tier: String?
    let accepted_by: String?
    let created_at: String?
    let cleared_at: String?
}

struct AlarmAck: Decodable {
    let alarm: String?
    let accepted_by: String?
    let state: String?
    let note: String?
}

struct AlarmGuidance: Decodable {
    let alarm: String?
    let source: String?
    let answer: String
    let note: String?
}

struct CrashWatchStatus: Decodable {
    let armed: Bool
    let trusted_name: String?
    let attempts: Int?
    let window_minutes: Double?
    let contact_emergency_services: Bool?
    let asking: Bool?
    let attempt: Int?
    let concern: String?
    let tripped: Bool?
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
    let spoken_steps: [String]?        // guide_first_aid playbook steps
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

// MARK: The effectiveness loop, the user-specific model, and the name

/// Spec [0039]: guidance that went out gets asked about.
struct OpenFollowup: Decodable, Identifiable {
    let id: String
    let condition: String
    let severity: String?
    let asked_at: String?
    let question: String
}

struct FollowupRecord: Decodable, Identifiable {
    let id: String
    let condition: String
    let severity: String?
    let asked_at: String?
    let answered_at: String?
    let helped: Bool?
    let note: String?
    let escalated_to: String?
}

struct FollowupState: Decodable {
    let open: [OpenFollowup]
    let history: [FollowupRecord]
}

struct LiveAssistanceOption: Decodable, Identifiable {
    let kind: String
    let name: String?
    let channel: String?
    let note: String?
    var id: String { kind + (name ?? "") }
}

struct LiveAssistance: Decodable {
    let options: [LiveAssistanceOption]
    let contact_alerted: Bool
    let note: String?
}

/// "It helped" resumes monitoring; "it did not" runs the ladder again with the
/// ineffective-guidance rung and names the humans reachable right now.
struct FollowupAnswered: Decodable {
    let answered: Bool
    let reason: String?
    let helped: Bool?
    let next: String?
    let live_assistance: LiveAssistance?
}

struct HelpTally: Decodable {
    let helped: Int
    let did_not: Int
    let answered: Int
    let hit_rate: Double?
}

struct CheckinTrend: Decodable {
    let count: Int
    let avg_mood: Double?
    let avg_stress: Double?
}

/// Claim 11's user-specific model, derived locally from this user's own stored
/// history. Nothing was sent to a model vendor to build it.
struct AdaptationDetail: Decodable {
    let known_conditions: [String]
    let what_helps: [String: HelpTally]
    let areas_brought: [String: Int]
    let checkins: CheckinTrend
    let tone: String?
    let explain_level: String?
    let beliefs_posture: String?
    let occupation: String?
    let method: String?
}

struct AdaptationProfile: Decodable {
    let built: Bool
    let note: String?
    let evidence_items: Int?
    let confidence: Double?
    let vaulted: Bool?
    let rebuilt_at: String?
    let profile: AdaptationDetail?
}

/// What anonymity costs and does not cost, said out loud, so the tradeoff is a
/// choice rather than a surprise.
struct Finetune: Decodable {
    let version: Int
    let backend: String
    let examples: Int
    let helped: Int
    let did_not_help: Int
    let weights: [Double]
    let method: String
    let digest: String
    let trained_at: String
    let active: Bool?
}

struct FinetuneSwitchResult: Decodable {
    let user_id: String
    let active: Bool
    let digest: String
    let backend: String
}

struct AnonymityPosture: Decodable {
    let anonymous: Bool
    let known_as: String?
    let legal_name_on_record: Bool
    let keeps: [String]
    let costs: [String]
}

// MARK: The community door (FIG. 2 boxes 222–226)

struct CommunityRoom: Decodable, Identifiable {
    let id: String
    let topic: String?
    let channel: String?
    let participants: Int?
    let url: String?
}

struct CommunityPlace: Decodable, Identifiable {
    let locality: String
    let region: String?
    let listings: Int?
    var id: String { locality + (region ?? "") }
}

/// What JIM will and will not do with the community it points at. Stated as
/// data rather than prose so the screen cannot drift from the behaviour.
struct CommunityPosture: Decodable {
    let mirrored_here: Bool
    let posts_on_your_behalf: Bool
    let health_data_shared: Bool
}

/// What the presence says it is. `boundaries` is the half that matters: a
/// boundary a screen cannot render is a boundary nobody can be shown.
struct PresenceWho: Decodable {
    let name: String
    let kind: String
    let says: String
    let note: String
    let hands_free: Bool
    let works_offline: Bool
    let areas: [String]
    let boundaries: [String: PresenceBoundary]
}

struct PresenceBoundary: Decodable {
    let value: Bool
    let says: String
}

/// One unprompted turn — or silence, which is an outcome here rather than an
/// empty response. `line_key` and `slots` rather than a sentence: the words
/// are composed on this side, in the reader's own language.
struct PresenceBeat: Decodable {
    let speak: Bool
    let slot: String
    let register: String
    let area: String?
    let line_key: String
    let because: [String]
    let english: String
    let initiative: Bool
    let wants_reply: Bool
    let offline: Bool
    let deepened: Bool
    let deepened_line: String?
}

struct PresenceDay: Decodable {
    let beats: [PresenceBeat]
    let hands_free: Bool
    let offline: Bool
}

struct PresenceArea: Decodable {
    let area: String
    let standing: String
    let known: Bool
}

struct PresenceBaseline: Decodable {
    let known_areas: Int
    let of: Int
    let needed_network: Bool
    let needed_model: Bool
    let areas: [String: PresenceArea]
}

struct PresenceOffer: Decodable {
    let kind: String
    let id: String?
    let who: String?
    let topic: String?
    let trade: String?
    let human: Bool?
    let ai: Bool?
}

struct PresenceReach: Decodable {
    let offers: [PresenceOffer]
    let posture: [String: Bool]
    let note: String
}

struct PresenceSurfaceRow: Decodable {
    let surface: String
    let audio: Bool
    let visual: Bool
    let note: String
    let chosen: Bool
    let reads_health_aloud: Bool
    let withholds: [String]
}

struct PresenceSurfaces: Decodable {
    let chosen: String
    let rule: String
    let glasses_makes: [String]
    let surfaces: [PresenceSurfaceRow]
}

/// How it carries itself, and what the dial does not touch.
///
/// `unchanged` is decoded and rendered rather than trusted from a comment: a
/// bearing that quietly narrowed what a health guardian watches would be a
/// setting that hurts whoever turned it, so the screen shows the claim.
/// A beat plus the room's verdict on it.
///
/// The withholding is decided on the server, before anything is synthesised:
/// the surface rule spent a release as a caption next to a button, reported
/// by `surfaces()` and read by nothing.
struct PresenceSpoken: Decodable {
    let speaks_on: String
    let spoken: Bool
    let shown: Bool
    let withheld: [String]
    let why_not_aloud: String
    let surface_is_private: Bool
    let surface_has_audio: Bool
    let english: String
    let speak: Bool
    let due: Bool?
    let slot_from_hour: String?
}

struct PresenceBearingEffect: Decodable {
    let registers: [String]
    let asks_about_your_day: Bool
    let keeps_company: Bool
    let says: String
}

struct PresenceBearingView: Decodable {
    let bearing: String
    let `default`: String
    let choices: [String]
    let effect: PresenceBearingEffect
    let unchanged: [String: String]
    let note: String
}

struct PresenceGrowth: Decodable {
    let beats_spoken: Int
    let areas_i_can_see: Int
    let of: Int
    let what_i_changed: [String]
    let about_myself: String
    let still_synthetic: Bool
}

struct CommunityView: Decodable {
    let qrme_url: String?
    let language: String?
    let rooms: [CommunityRoom]
    let places: [CommunityPlace]
    let note: String
    let posture: CommunityPosture
}

struct ImproveReceipt: Decodable { let id: String; let status: String }

struct ImproveItem: Decodable, Identifiable {
    let id: String
    let category: String
    let message: String
    let status: String
}

struct AccessReceipt: Decodable { let id: String; let status: String; let note: String? }
struct AccessReportRow: Decodable, Identifiable {
    let id: String; let lang: String; let doing: String; let wall: String
    let help: String?; let status: String; let created_at: String
}
struct AccessReportsState: Decodable { let reports: [AccessReportRow]; let total: Int }

struct ImproveState: Decodable {
    let mine: [ImproveItem]
    let tally: [String: Int]
    let total: Int
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

    /// The person's own model key, pushed in by `AppState` and sent on every
    /// request as `x-llm-api-key`. Held here rather than reached for from the
    /// request path, which is actor-isolated and must not hop to the main
    /// actor to build a header.
    private var llmKey = ""

    func useLlmKey(_ key: String) { llmKey = key }

    /// The deployment invite key: a published deployment sets
    /// JIM_SIGNUP_KEY and refuses account creation without it. Sent as
    /// `x-signup-key` on every request; the backend reads it only on
    /// the routes it gates.
    private var signupKey = ""

    func useSignupKey(_ key: String) { signupKey = key }
    var base = URL(string: "http://127.0.0.1:8000")!

    func setBase(_ s: String) {
        if let u = URL(string: s.hasSuffix("/") ? String(s.dropLast()) : s) { base = u }
    }


    /// Read-only on purpose: the posture is set in the deployment's
    /// environment, not by somebody signed into the app.
    /// What the Guardian carries across sessions about this person. Counts
    /// and timings only — the vector is derived from tallies and holds
    /// nothing anybody wrote.
    func continuity(uid: String, token: String) async throws -> ContinuityState {
        try await request("/continuity/\(uid)", token: token)
    }

    /// Drop it. Every derived thing here has to be droppable by the person it
    /// was derived from.
    @discardableResult
    func forgetContinuity(uid: String, token: String) async throws -> Forgotten {
        try await request("/continuity/\(uid)", method: "DELETE", token: token)
    }

    func offlineStatus() async throws -> OfflinePosture {
        try await request("/offline/status")
    }

    /// Every request this client sends that does not go through the shared
    /// helper, and the one place the reader's language is attached to it.
    /// A funnel only funnels what goes into it.
    private func dispatch(_ req: URLRequest) async throws -> (Data, URLResponse) {
        var req = req
        req.setValue(L10n.deviceLanguage, forHTTPHeaderField: "accept-language")
        // The person's own model key, if this device holds one. Sent as a
        // header rather than stored server-side: the backend puts it in a
        // context var for the length of the call and never writes it down.
        if !llmKey.isEmpty {
            req.setValue(llmKey, forHTTPHeaderField: "x-llm-api-key")
        }
        if !signupKey.isEmpty {
            req.setValue(signupKey, forHTTPHeaderField: "x-signup-key")
        }
        return try await URLSession.shared.data(for: req)
    }

    /// Everything this deployment holds about a person, by table.
    ///
    /// The erase has been on the console since it existed and this had no
    /// route at all. The phone needs it because a person whose only device
    /// is a phone is exactly the person who cannot use a desktop console to
    /// get their data out.
    func exportEverything(userId: String, token: String) async throws -> UserExport {
        try await request("/data/\(userId)", token: token)
    }

    /// The other direction, and the one this shell had no door for either.
    ///
    /// A person whose only device is a phone could take their data from
    /// 0.60.0 and could not end it. Both halves of *it is yours* have to be
    /// reachable from the same place or only one of them is true.
    func eraseEverything(userId: String, token: String) async throws -> ErasedReceipt {
        try await request("/data/\(userId)", method: "DELETE", token: token)
    }


    struct ProblemRow: Decodable {
        let source: String
        let app_version: String
        let platform: String
        let op: String
        let status_code: Int
        let day: String
        let count: Int
    }
    struct ProblemRows: Decodable { let rows: [ProblemRow] }

    /// The failure aggregate this backend keeps. Reading is the operator's:
    /// the problems key as the token, or nothing when asking from the
    /// machine the backend runs on.
    func problemRows(key: String) async throws -> ProblemRows {
        try await request("/v1/problems", token: key)
    }

    private func request<T: Decodable>(_ path: String, method: String = "GET",
                                       body: [String: Any]? = nil, token: String? = nil,
                                       rawBody: Data? = nil) async throws -> T {
        var req = URLRequest(url: base.appendingPathComponent(path))
        req.httpMethod = method
        req.setValue("application/json", forHTTPHeaderField: "content-type")
        // The language the reader actually speaks. Every sentence the
        // backend composes on a public route is chosen from this header,
        // and no native shell was sending it — the browser sends it for
        // free, which is why the phones were the ones still answering in
        // English after the routes learned to speak.
        req.setValue(L10n.deviceLanguage, forHTTPHeaderField: "accept-language")
        // The person's own model key, if this device holds one. Sent as a
        // header rather than stored server-side: the backend puts it in a
        // context var for the length of the call and never writes it down.
        if !llmKey.isEmpty {
            req.setValue(llmKey, forHTTPHeaderField: "x-llm-api-key")
        }
        if !signupKey.isEmpty {
            req.setValue(signupKey, forHTTPHeaderField: "x-signup-key")
        }
        if let token { req.setValue("Bearer \(token)", forHTTPHeaderField: "authorization") }
        if let body { req.httpBody = try JSONSerialization.data(withJSONObject: body) }
        else if let rawBody { req.httpBody = rawBody }

        let data: Data
        let resp: URLResponse
        do {
            (data, resp) = try await URLSession.shared.data(for: req)
        } catch {
            // Never reached a server. Recorded as status 0; the thrown error
            // still carries its message to the person, who owns it.
            Problems.record(method: method, path: path, status: 0)
            throw error
        }
        guard let http = resp as? HTTPURLResponse else {
            Problems.record(method: method, path: path, status: 0)
            throw ApiError.http("No response")
        }
        guard (200..<300).contains(http.statusCode) else {
            // The status and the operation, never the detail below: these
            // messages quote what the person typed, which is theirs to read
            // and nobody's to keep.
            Problems.record(method: method, path: path, status: http.statusCode)
            // A 422 answers with a *list* of rows, not a string, so `as? String`
            // gave nil and the person saw the status code — less than they saw
            // before their language was ever considered. `message` is the
            // sentence the backend composes beside the rows; read it first.
            let body = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any]
            // A plan refusal (402) puts a *dict* in detail; its `message` is
            // the sentence composed for the reader. Read it too, or the
            // person sees "HTTP 402" where the server wrote them why.
            let structured = (body?["detail"] as? [String: Any])?["message"] as? String
            let said = (body?["message"] as? String) ?? (body?["detail"] as? String) ?? structured
            throw ApiError.http(said ?? "HTTP \(http.statusCode)")
        }
        return try JSONDecoder().decode(T.self, from: data)
    }

    func health() async throws -> Health { try await request("/health") }

    func enroll(name: String, birthdate: String,
                language: String? = nil) async throws -> EnrollResult {
        var body: [String: Any] = ["display_name": name, "birthdate": birthdate,
                                   "terms_consent": true]
        if let language, language != "en" { body["language"] = language }
        return try await request("/enroll", method: "POST", body: body)
    }

    func monitor(uid: String, token: String, heartRate: Int, stress: Double) async throws -> MonitorResult {
        try await request("/monitor/\(uid)", method: "POST",
                          body: ["heart_rate": heartRate, "stress_level": stress], token: token)
    }

    func checkin(uid: String, token: String, mood: Int, energy: Int, note: String) async throws -> CheckinResult {
        try await request("/checkin/\(uid)", method: "POST",
                          body: ["mood": mood, "energy": energy, "note": note], token: token)
    }

    // MARK: engaged sessions
    //
    // The session you leave running. See jim/engaged.py for what it may
    // touch and why the reach is a written list rather than this token's
    // full authority.

    /// What an engaged session can do to you, in sentences.
    ///
    /// No token, deliberately: this is how somebody decides whether to open
    /// one at all, and a list of what a feature would be allowed to touch is
    /// not the feature.
    func engagedReach() async throws -> EngagedReach {
        try await request("/engaged/reach")
    }

    func engaged(uid: String, token: String) async throws -> EngagedSession {
        try await request("/engaged/\(uid)", token: token)
    }

    func engage(uid: String, token: String,
                area: String = "personal_growth") async throws -> EngagedSession {
        try await request("/engaged/\(uid)", method: "POST",
                          body: ["area": area], token: token)
    }

    func engagedTurn(uid: String, token: String,
                     message: String) async throws -> EngagedTurnResult {
        try await request("/engaged/\(uid)/turn", method: "POST",
                          body: ["message": message], token: token)
    }

    /// End the engagement and hand it over. `topics` becomes the standing
    /// watch list the offline Guardian keeps while this person is away.
    func engagedSignOff(uid: String, token: String,
                        topics: [String]) async throws -> EngagedSignOff {
        try await request("/engaged/\(uid)/sign-off", method: "POST",
                          body: ["topics": topics], token: token)
    }

    func engagedActs(uid: String, token: String) async throws -> [EngagedAct] {
        try await request("/engaged/\(uid)/acts", token: token)
    }

    /// Take one act back, through the door that would have undone it by hand.
    func engagedUndo(uid: String, token: String,
                     actId: String) async throws -> EngagedUndone {
        try await request("/engaged/\(uid)/acts/\(actId)/undo",
                          method: "POST", token: token)
    }

    func engagedWatches(uid: String, token: String) async throws -> [StandingWatch] {
        try await request("/engaged/\(uid)/watches", token: token)
    }

    func engagedWatch(uid: String, token: String,
                      topic: String) async throws -> StandingWatch {
        try await request("/engaged/\(uid)/watches", method: "POST",
                          body: ["topic": topic], token: token)
    }

    @discardableResult
    func engagedClearWatch(uid: String, token: String,
                           watchId: String) async throws -> WatchCleared {
        try await request("/engaged/\(uid)/watches/\(watchId)",
                          method: "DELETE", token: token)
    }

    // The ways back the undo trail replays — and doors a person should
    // always have had. Until an engaged session needed to take a check-in
    // back, nothing in this product could delete one.
    @discardableResult
    func removeCheckin(uid: String, token: String,
                       checkinId: String) async throws -> Removed {
        try await request("/checkin/\(uid)/\(checkinId)",
                          method: "DELETE", token: token)
    }

    @discardableResult
    func removeJournal(uid: String, token: String,
                       entryId: String) async throws -> Removed {
        try await request("/journal/\(uid)/\(entryId)",
                          method: "DELETE", token: token)
    }

    @discardableResult
    func removeGoal(uid: String, token: String,
                    goalId: String) async throws -> Removed {
        try await request("/goals/\(uid)/\(goalId)", method: "DELETE",
                          token: token)
    }

    @discardableResult
    func removeHabit(uid: String, token: String,
                     habitId: String) async throws -> Removed {
        try await request("/habits/\(uid)/\(habitId)", method: "DELETE",
                          token: token)
    }

    @discardableResult
    func unlogHabit(uid: String, token: String, habitId: String,
                    day: String) async throws -> HabitLogged {
        try await request("/habits/\(uid)/\(habitId)/log/\(day)",
                          method: "DELETE", token: token)
    }

    func coach(uid: String, token: String, area: String, message: String) async throws -> Guidance {
        try await request("/coach/\(uid)", method: "POST",
                          body: ["area": area, "message": message], token: token)
    }

    /// Send this question to the QRME specialist covering the area.
    ///
    /// `coach` only *offers*. This is the door the person chooses, because
    /// what crosses the tandem is what they wrote.
    func coachSpecialist(uid: String, token: String, area: String,
                         message: String) async throws -> SpecialistAnswer {
        try await request("/coach/\(uid)/specialist", method: "POST",
                          body: ["area": area, "message": message], token: token)
    }

    // The offline coach's store and syllabus (jim/pipeline.py): what the
    // stack predicts from, what JIM should study next, and the one-press
    // study that imports the findings.
    func coachStore(uid: String, token: String) async throws -> CoachStore {
        try await request("/coach/\(uid)/store", token: token)
    }

    func coachCurriculum(uid: String, token: String) async throws -> CoachCurriculum {
        try await request("/coach/\(uid)/curriculum", token: token)
    }

    func coachStudy(uid: String, token: String, topic: String?,
                    area: String?) async throws -> CoachStudied {
        var body: [String: Any] = [:]
        if let topic { body["topic"] = topic }
        if let area { body["area"] = area }
        return try await request("/coach/\(uid)/study", method: "POST",
                                 body: body, token: token)
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

    // -- the one QRME profile that is this person ---------------------------
    //
    // Every other QRME call in this shell reaches somebody else's profile.
    // These reach their own — see docs/tandem.md, and jim/synthetic_self.py
    // for the boundary. Seeing and revoking what a profile has been told
    // belongs on the phone at least as much as on the desktop: the phone is
    // what somebody has with them when they change their mind.

    func selfProfile(uid: String, token: String) async throws -> SelfProfileStatus {
        try await request("/self-profile/\(uid)", token: token)
    }

    func linkSelfProfile(uid: String, token: String, profileId: String,
                         ownerToken: String) async throws -> SelfProfileStatus {
        try await request("/self-profile/\(uid)", method: "POST",
                          body: ["profile_id": profileId,
                                 "owner_token": ownerToken], token: token)
    }

    func unlinkSelfProfile(uid: String, token: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/self-profile/\(uid)", method: "DELETE",
                                      token: token)
    }

    func consentSelfProfile(uid: String, token: String,
                            categories: [String]) async throws -> SelfProfileStatus {
        try await request("/self-profile/\(uid)/consent", method: "PUT",
                          body: ["categories": categories], token: token)
    }

    /// Exactly what would be sent, built by the code that sends it.
    func previewSelfProfile(uid: String, token: String) async throws -> SelfProfilePreview {
        try await request("/self-profile/\(uid)/preview", token: token)
    }

    func briefSelfProfile(uid: String, token: String) async throws -> SelfProfileSent {
        try await request("/self-profile/\(uid)/brief", method: "POST",
                          token: token)
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

    /// Meals: the note is the log, the photo (base64) is the sealed receipt.
    func logMeal(uid: String, token: String, note: String,
                 contentB64: String? = nil) async throws -> Meal {
        var body: [String: Any] = ["note": note]
        if let contentB64 { body["content"] = contentB64 }
        return try await request("/users/\(uid)/meals", method: "POST",
                                 body: body, token: token)
    }

    func meals(uid: String, token: String) async throws -> [Meal] {
        try await request("/users/\(uid)/meals", token: token)
    }

    func writeLetter(uid: String, token: String) async throws -> Letter {
        try await request("/users/\(uid)/letters", method: "POST",
                          body: [:], token: token)
    }

    func letters(uid: String, token: String) async throws -> [Letter] {
        try await request("/users/\(uid)/letters", token: token)
    }

    /// Interview drills: the bank is server-local; practice works offline.
    func startDrill(uid: String, token: String) async throws -> Drill {
        try await request("/users/\(uid)/drills", method: "POST",
                          body: [:], token: token)
    }

    func answerDrill(uid: String, token: String, drillId: String,
                     answer: String) async throws -> Drill {
        try await request("/users/\(uid)/drills/\(drillId)/answer",
                          method: "POST", body: ["answer": answer],
                          token: token)
    }

    func drills(uid: String, token: String) async throws -> [Drill] {
        try await request("/users/\(uid)/drills", token: token)
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

    func setLanguage(uid: String, token: String, code: String,
                     mode: String = "pre") async throws -> LanguageChoice {
        try await request("/language/\(uid)", method: "PUT",
                          body: ["language": code, "mode": mode], token: token)
    }

    func translate(uid: String, token: String, text: String,
                   to: String? = nil) async throws -> TranslateResult {
        var body: [String: Any] = ["text": text]
        if let to { body["to"] = to }
        return try await request("/translate/\(uid)", method: "POST",
                                 body: body, token: token)
    }

    // MARK: Safety — escalation policy, Emergency, robots

    // The crash watch: armed in advance, off by default. The status read is
    // also the clock — polling is what re-asks the question.
    // MARK: - Alarms
    //
    // The routes this shell could not reach at all until 0.23.0. A responder
    // is paged on their phone and, holding that phone, had no way to answer:
    // accepting is what stops the ladder climbing to emergency services.

    func alarms(uid: String, token: String) async throws -> [AlarmRow] {
        try await request("/users/\(uid)/alarms", token: token)
    }

    /// `responder` must be a name. The backend refuses an empty one, and its
    /// reason is worth carrying up to the button: *"a responder needs a name
    /// — 'someone accepted it' is the thing this relay exists to stop being
    /// enough."*
    func acceptAlarm(uid: String, alarmId: String, responder: String,
                     token: String) async throws -> AlarmAck {
        try await request("/users/\(uid)/alarms/\(alarmId)/accept",
                          method: "POST", body: ["responder": responder],
                          token: token)
    }

    func clearAlarm(uid: String, alarmId: String,
                    token: String) async throws -> AlarmAck {
        try await request("/users/\(uid)/alarms/\(alarmId)/clear",
                          method: "POST", body: [:], token: token)
    }

    func escalateAlarm(uid: String, alarmId: String,
                       token: String) async throws -> AlarmAck {
        try await request("/users/\(uid)/alarms/\(alarmId)/escalate",
                          method: "POST", body: [:], token: token)
    }

    /// Answers even with no specialist reachable — the standing instruction
    /// is the one that is always right and never depends on a model.
    func alarmGuidance(alarmId: String, question: String,
                       token: String) async throws -> AlarmGuidance {
        try await request("/alarms/\(alarmId)/guidance", method: "POST",
                          body: ["question": question], token: token)
    }

    func crashWatch(uid: String, token: String) async throws -> CrashWatchStatus {
        try await request("/crash-watch/\(uid)", token: token)
    }

    func armCrashWatch(uid: String, token: String, name: String,
                       channel: String, attempts: Int, windowMinutes: Double,
                       ems: Bool) async throws -> CrashWatchStatus {
        try await request("/crash-watch/\(uid)", method: "PUT",
                          body: ["trusted_name": name,
                                 "trusted_channel": channel,
                                 "attempts": attempts,
                                 "window_minutes": windowMinutes,
                                 "contact_emergency_services": ems],
                          token: token)
    }

    func disarmCrashWatch(uid: String, token: String) async throws -> CrashWatchStatus {
        try await request("/crash-watch/\(uid)", method: "DELETE", token: token)
    }

    func imOkay(uid: String, token: String) async throws -> CrashWatchStatus {
        try await request("/crash-watch/\(uid)/respond", method: "POST",
                          body: [:], token: token)
    }

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

    // MARK: family — a parent sets up and watches over a child's account

    func enrollChild(gid: String, token: String, name: String,
                     birthdate: String,
                     guardianPhone: String?) async throws -> ChildCreated {
        var body: [String: Any] = ["display_name": name,
                                   "birthdate": birthdate]
        if let guardianPhone, !guardianPhone.isEmpty {
            body["guardian_phone"] = guardianPhone
        }
        return try await request("/guardians/\(gid)/children",
                                 method: "POST", body: body, token: token)
    }

    func children(gid: String, token: String) async throws -> [ChildSummary] {
        try await request("/guardians/\(gid)/children", token: token)
    }

    func childOverview(gid: String, cid: String,
                       token: String) async throws -> ChildOverview {
        try await request("/guardians/\(gid)/children/\(cid)", token: token)
    }

    func setFamilyControls(gid: String, cid: String, token: String,
                           paused: Bool?, quietStart: String?,
                           quietEnd: String?) async throws -> FamilyControlsState {
        var body: [String: Any] = [:]
        if let paused { body["paused"] = paused }
        if let quietStart { body["quiet_start"] = quietStart }
        if let quietEnd { body["quiet_end"] = quietEnd }
        return try await request("/guardians/\(gid)/children/\(cid)/controls",
                                 method: "PUT", body: body, token: token)
    }

    func guardianWatch(gid: String, token: String) async throws -> GuardianFace {
        try await request("/guardians/\(gid)/watch", token: token)
    }

    func unlinkChild(gid: String, cid: String, token: String) async throws {
        struct Ok: Decodable { let linked: Bool }
        let _: Ok = try await request("/guardians/\(gid)/children/\(cid)",
                                      method: "DELETE", token: token)
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

    // MARK: vault custody — sealed tandem exchanges

    func custody(uid: String, token: String) async throws -> CustodyList {
        try await request("/custody/\(uid)", token: token)
    }

    func custodyProvenance(uid: String, token: String,
                           key: String) async throws -> CustodyProvenance {
        let q = key.addingPercentEncoding(
            withAllowedCharacters: .urlQueryAllowed) ?? key
        return try await request("/custody/\(uid)/provenance?key=\(q)",
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

    func socialScrape(cid: String, token: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/social/connection/\(cid)/scrape",
                                      method: "POST", token: token)
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

    // MARK: Help us improve — product feedback (open to anyone)

    func submitImprovement(category: String, message: String, rating: Int?,
                           token: String?) async throws -> ImproveReceipt {
        var body: [String: Any] = ["category": category, "message": message]
        if let rating { body["rating"] = rating }
        return try await request("/improve", method: "POST", body: body, token: token)
    }

    func improvements(token: String?) async throws -> ImproveState {
        try await request("/improve", token: token)
    }

    /// The accessibility door: tokenless on purpose — the person it exists
    /// for may be the person the enrollment shut out. The words stay on the
    /// deployment; nothing here reaches the problems collector.
    func sendAccessReport(doing: String, wall: String, help: String?,
                          lang: String) async throws -> AccessReceipt {
        var body: [String: Any] = ["doing": doing, "wall": wall, "lang": lang]
        if let help, !help.isEmpty { body["help"] = help }
        return try await request("/access/reports", method: "POST", body: body,
                                 token: nil)
    }

    /// Reviewer-token read — the deployment's steward, never a user.
    func accessReports(reviewerToken: String) async throws -> AccessReportsState {
        try await request("/access/reports", token: reviewerToken)
    }

    func revokeMedicalCard(uid: String, token: String) async throws {
        var req = URLRequest(url: base.appendingPathComponent("/medical-id/qr/\(uid)"))
        req.httpMethod = "DELETE"
        req.setValue("Bearer \(token)", forHTTPHeaderField: "authorization")
        let (_, resp) = try await dispatch(req)
        guard let http = resp as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            throw ApiError.http("revoke failed")
        }
    }

    // MARK: Community — the door into QRME, and the visit note

    /// Rooms and places as QRME serves them. JIM adds the language it knows
    /// this user reads and the posture; it never mirrors the conversation.
    func community(uid: String, token: String) async throws -> CommunityView {
        try await request("/community/\(uid)", token: token)
    }

    /// Record that a door was opened — an event on the user's own timeline
    /// and nothing else. No room contents cross back into JIM.
    func noteCommunityVisit(uid: String, token: String, roomId: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/community/\(uid)/visits", method: "POST",
                                     body: ["room_id": roomId], token: token)
    }


    // MARK: The presence — the coach that speaks first
    //
    // Every read here is answered from rows the backend already holds: no
    // model, no network beyond this call. A phone in a tunnel still gets its
    // day, which is the whole argument of `jim/presence.py`.

    /// What it is, and what it will not be. No token: the answer must be the
    /// same to a child, a guardian, a clinician and a regulator.
    func presenceWho() async throws -> PresenceWho {
        try await request("/presence")
    }

    /// The six areas and the evidence behind each standing.
    func presenceBaseline(uid: String, token: String) async throws -> PresenceBaseline {
        try await request("/presence/\(uid)/baseline", token: token)
    }

    /// The day's three beats at once — a plan, so a client can hold it and
    /// then lose its connection without losing the day.
    func presenceDay(uid: String, token: String) async throws -> PresenceDay {
        try await request("/presence/\(uid)/day", token: token)
    }

    /// One beat, and asking for it is what counts as having been told: the
    /// backend records it so the same line does not return tomorrow.
    func presenceBeat(uid: String, token: String,
                      slot: String) async throws -> PresenceBeat {
        try await request("/presence/\(uid)/beat?slot=" + slot, token: token)
    }

    /// The same beat with a model's wording on it. The model may not decide
    /// that there is a beat, which area, or what the evidence says.
    func presenceDeepen(uid: String, token: String,
                        slot: String) async throws -> PresenceBeat {
        try await request("/presence/\(uid)/deepen?slot=" + slot,
                          method: "POST", token: token)
    }

    /// Other minds — QRME's rooms, desks and profiles, offered.
    func presenceReach(uid: String, token: String) async throws -> PresenceReach {
        try await request("/presence/\(uid)/reach", token: token)
    }

    /// Where it may speak, and what each surface makes it hold back.
    func presenceSurfaces(uid: String, token: String) async throws -> PresenceSurfaces {
        try await request("/presence/\(uid)/surfaces", token: token)
    }

    func presenceChooseSurface(uid: String, token: String,
                               surface: String) async throws -> PresenceSurfaces {
        try await request("/presence/\(uid)/surface", method: "PUT",
                          body: ["speaks_on": surface], token: token)
    }

    /// The beat, and whether this surface may speak it.
    func presenceSay(uid: String, token: String,
                     slot: String) async throws -> PresenceSpoken {
        try await request("/presence/\(uid)/say?slot=" + slot, token: token)
    }

    /// The hands-free question: is there something to say right now. Does not
    /// record — a device polling on a timer must not burn a beat nobody heard.
    func presenceDue(uid: String, token: String) async throws -> PresenceSpoken {
        try await request("/presence/\(uid)/due", token: token)
    }

    /// The bearing: companion by default, professional on request.
    func presenceBearing(uid: String, token: String) async throws -> PresenceBearingView {
        try await request("/presence/\(uid)/bearing", token: token)
    }

    func presenceSetBearing(uid: String, token: String,
                            bearing: String) async throws -> PresenceBearingView {
        try await request("/presence/\(uid)/bearing", method: "PUT",
                          body: ["bearing": bearing], token: token)
    }

    /// What it has become, with the counts under it.
    func presenceGrowth(uid: String, token: String) async throws -> PresenceGrowth {
        try await request("/presence/\(uid)/growth", token: token)
    }

    // MARK: Followup, adaptation and anonymity

    func followups(uid: String, token: String) async throws -> FollowupState {
        try await request("/followup/\(uid)", token: token)
    }

    /// `helped: false` is not a complaint filed away — it re-runs the
    /// escalation ladder and returns the humans who can help now.
    func answerFollowup(uid: String, token: String, helped: Bool,
                        note: String? = nil) async throws -> FollowupAnswered {
        var body: [String: Any] = ["helped": helped]
        if let note, !note.isEmpty { body["note"] = note }
        return try await request("/followup/\(uid)", method: "POST",
                                 body: body, token: token)
    }

    func adaptation(uid: String, token: String) async throws -> AdaptationProfile {
        try await request("/adaptation/\(uid)", token: token)
    }

    /// Rebuild from the history already on record. Local work: no history
    /// leaves the device's backend to produce it.
    func rebuildAdaptation(uid: String,
                           token: String) async throws -> AdaptationProfile {
        try await request("/adaptation/\(uid)", method: "POST", token: token)
    }

    // MARK: The offline fine-tune
    //
    // Beside `adaptation` and not folded into it: that one recomputes a
    // profile that conditions a prompt, this one trains weights. A reader who
    // cannot tell which happened has been told nothing useful.

    func finetune(uid: String, token: String) async throws -> Finetune {
        try await request("/finetune/\(uid)", token: token)
    }

    /// Train from the history already on record. Local work: the pass runs
    /// with the backend's network blocked, so nothing about this person's
    /// health goes anywhere to produce it.
    func runFinetune(uid: String, token: String) async throws -> Finetune {
        try await request("/finetune/\(uid)", method: "POST", token: token)
    }

    /// Training and using are two decisions. Off takes effect on the next reply.
    func setFinetuneActive(uid: String, token: String,
                           active: Bool) async throws -> FinetuneSwitchResult {
        try await request("/finetune/\(uid)/active", method: "PUT",
                          body: ["active": active], token: token)
    }

    func anonymity(uid: String, token: String) async throws -> AnonymityPosture {
        try await request("/anonymity/\(uid)", token: token)
    }

}

/// What the deployment can and cannot reach.
///
/// Offline mode was settable and unreadable: the flag existed, the guarantee
/// was written in a docstring, and there was nowhere on a phone to see the
/// answer. A guarantee nobody can check is a guarantee.
struct OfflinePosture: Decodable {
    let offline: Bool
    let external_transmission_possible: Bool
    let local_destinations_allowed: String
    let guarantees: [String]
}

/// The export bundle, counted rather than modelled: reading every column of
/// every table into Swift types would be a second copy of the schema.
/// What came back from an erase: how many rows went, by table.
struct ErasedReceipt: Decodable {
    let deleted: [String: Int]
}

struct UserExport: Decodable {
    let tables: [String: [ExportRow]]
    let note: String
}

struct ExportRow: Decodable {
    init(from decoder: Decoder) throws { }
}

struct ContinuityState: Decodable {
    let built: Bool
    let carries: String
    let note: String?
    let version: Int?
    let observations: Int?
    let conditioning: Bool?
    let vector: [String: Double]?
    let meanings: [String: String]?
    let method: String?
}

struct Forgotten: Decodable { let forgotten: Bool }

struct SpecialistOffer: Decodable {
    let available: Bool
    let label: String
    let qrme_profile_id: String
    let sent: Bool
    let note: String
}

struct SpecialistAnswer: Decodable {
    let delivered: Bool
    let area: String?
    let content: String?
    let reason: String?
    let note: String?
    let held_for_owner_approval: Bool?
    struct Who: Decodable { let label: String; let qrme_profile_id: String }
    let specialist: Who?
    struct Where: Decodable { let method: String; let shared: String }
    let provenance: Where?
}

// MARK: - Money — the guardian that watches balances (jim/money.py)

/// One registered account. `credentials` is "vaulted" or "none" — the numbers
/// themselves never come back through any route, which is rule 1 of the
/// module and the reason there is nothing more sensitive here to hold.
struct MoneyAccount: Decodable {
    let id: String
    let kind: String
    let institution: String
    let label: String?
    let last4: String?
    let credentials: String?
    let balance: Double?
}

struct SavingsGoal: Decodable {
    let goal: Double
    let note: String?
    let reached_at: String?
}

struct MoneyMandate: Decodable {
    let enabled: Bool
    let cap_per_order: Double?
    let monthly_cap: Double?
    let asset_classes: [String]
    let scope: String?
}

struct MoneyOrder: Decodable {
    let asset_class: String
    let amount: Double
    let status: String
    let rationale: String?
}

struct MoneyDoors: Decodable {
    struct Desk: Decodable {
        let desk_id: String?
        let name: String?
        let trade: String?
        let location: String?
    }
    struct Specialist: Decodable { let label: String?; let route: String? }
    let coach: String?
    let specialist: Specialist?
    let desks: [Desk]
}

struct MoneyWarning: Decodable {
    let kind: String
    let message: String
    let doors: MoneyDoors?
}

/// The overview carries its own `labels`, in the reader's language, because
/// no shell has a translation table for this card and the English count
/// behind the tabs is a ratchet that must not grow. The server speaks; the
/// screen shows.
struct MoneyOverview: Decodable {
    let accounts: [MoneyAccount]
    let savings: SavingsGoal?
    let mandate: MoneyMandate?
    let orders: [MoneyOrder]
    let note: String
    let labels: [String: String]
}

struct MoneyObserved: Decodable {
    let account: MoneyAccount
    let recorded: Bool
    let warnings: [MoneyWarning]
    let orders_proposed: [MoneyOrder]
}

extension ApiClient {
    func moneyOverview(uid: String, token: String) async throws -> MoneyOverview {
        try await request("/money/\(uid)", token: token)
    }

    func moneyAddAccount(uid: String, token: String, kind: String,
                         institution: String, label: String?,
                         accountNumber: String?, routingNumber: String?,
                         apiKey: String?) async throws -> MoneyAccount {
        var body: [String: Any] = ["kind": kind, "institution": institution]
        if let label, !label.isEmpty { body["label"] = label }
        if let accountNumber, !accountNumber.isEmpty { body["account_number"] = accountNumber }
        if let routingNumber, !routingNumber.isEmpty { body["routing_number"] = routingNumber }
        if let apiKey, !apiKey.isEmpty { body["api_key"] = apiKey }
        return try await request("/money/\(uid)/accounts", method: "POST",
                                 body: body, token: token)
    }

    func moneyObserve(uid: String, token: String, accountId: String,
                      balance: Double) async throws -> MoneyObserved {
        try await request("/money/\(uid)/observe", method: "POST",
                          body: ["account_id": accountId, "balance": balance],
                          token: token)
    }

    struct StatementRow: Decodable, Identifiable {
        let id: String
        let filename: String
        let line_count: Int
        let total_in: Double
        let total_out: Double
        let end_balance: Double?
    }

    /// The statement file goes to the vault; the reading is local.
    func moneyDropStatement(uid: String, token: String, accountId: String,
                            filename: String,
                            contentB64: String) async throws -> StatementRow {
        try await request("/money/\(uid)/statements", method: "POST",
                          body: ["account_id": accountId,
                                 "filename": filename,
                                 "content": contentB64], token: token)
    }

    func moneyStatements(uid: String,
                         token: String) async throws -> [StatementRow] {
        try await request("/money/\(uid)/statements", token: token)
    }

    struct BankLinkRow: Decodable, Identifiable {
        let id: String
        let institution: String
        let aggregator: String
        let status: String
    }

    /// A written aggregator consent; the status never claims data.
    func moneyLinkBank(uid: String, token: String, institution: String,
                       aggregator: String) async throws -> BankLinkRow {
        try await request("/money/\(uid)/links", method: "POST",
                          body: ["institution": institution,
                                 "aggregator": aggregator], token: token)
    }

    func moneyLinks(uid: String, token: String) async throws -> [BankLinkRow] {
        try await request("/money/\(uid)/links", token: token)
    }

    func moneySyncBank(uid: String, token: String,
                       linkId: String) async throws -> BankLinkRow {
        try await request("/money/\(uid)/links/\(linkId)/sync",
                          method: "POST", body: [:], token: token)
    }

    func moneyRevokeLink(uid: String, token: String,
                         linkId: String) async throws -> BankLinkRow {
        try await request("/money/\(uid)/links/\(linkId)",
                          method: "DELETE", token: token)
    }

    func moneySetSavings(uid: String, token: String,
                         goal: Double) async throws -> SavingsGoal {
        try await request("/money/\(uid)/savings", method: "PUT",
                          body: ["goal": goal], token: token)
    }

    func moneySetMandate(uid: String, token: String, enabled: Bool,
                         capPerOrder: Double, monthlyCap: Double,
                         assetClasses: [String],
                         scope: String) async throws -> MoneyMandate {
        try await request("/money/\(uid)/mandate", method: "PUT",
                          body: ["enabled": enabled,
                                 "cap_per_order": capPerOrder,
                                 "monthly_cap": monthlyCap,
                                 "asset_classes": assetClasses,
                                 "scope": scope], token: token)
    }
}

// MARK: - Schedule + shopping through the tandem (jim/schedule.py, jim/shopping.py)

struct AppointmentRow: Decodable, Identifiable {
    let id: String
    let title: String
    let whenat: String
    let whereat: String?
    let email_reminder: Int
    let qrme_order_id: String?
    let status: String
}

/// Labels ride the view in the reader's language — this shell renders
/// them and adds no English of its own.
struct ScheduleOverview: Decodable {
    let appointments: [AppointmentRow]
    let email_available: Bool
    let labels: [String: String]
    let note: String
}

struct TandemShopRow: Decodable, Identifiable {
    let id: String
    let name: String
    let seller: String
    let tag: String?
    let offerings: Int
}

struct ShopReceiptRow: Decodable, Identifiable {
    let id: String
    let qrme_order_id: String
    let shop_id: String
    let title: String
    let amount: Double
    let currency: String
    let status: String
}

struct ShoppingOverview: Decodable {
    let shops: [TandemShopRow]
    let receipts: [ShopReceiptRow]
    let labels: [String: String]
    let note: String
}

struct PlacedTandemOrder: Decodable {
    let id: String
    let shop_id: String
    let status: String
}

extension ApiClient {
    func scheduleView(uid: String, token: String) async throws -> ScheduleOverview {
        try await request("/schedule/\(uid)", token: token)
    }

    func scheduleBook(uid: String, token: String, title: String, when: String,
                      where whereAt: String?, emailReminder: Bool,
                      shopId: String? = nil,
                      offeringId: String? = nil) async throws -> AppointmentRow {
        var body: [String: Any] = ["title": title, "when": when,
                                   "email_reminder": emailReminder]
        if let whereAt, !whereAt.isEmpty { body["where"] = whereAt }
        if let shopId, !shopId.isEmpty { body["shop_id"] = shopId }
        if let offeringId, !offeringId.isEmpty { body["offering_id"] = offeringId }
        return try await request("/schedule/\(uid)", method: "POST",
                                 body: body, token: token)
    }

    func scheduleCancel(uid: String, token: String,
                        appointmentId: String) async throws -> AppointmentRow {
        try await request("/schedule/\(uid)/\(appointmentId)",
                          method: "DELETE", token: token)
    }

    func shoppingView(uid: String, token: String) async throws -> ShoppingOverview {
        try await request("/shopping/\(uid)", token: token)
    }

    func shoppingOrder(uid: String, token: String, shopId: String,
                       offeringId: String,
                       quantity: Int) async throws -> PlacedTandemOrder {
        try await request("/shopping/\(uid)/order", method: "POST",
                          body: ["shop_id": shopId, "offering_id": offeringId,
                                 "quantity": quantity], token: token)
    }

    func shoppingCancel(uid: String, token: String,
                        qrmeOrderId: String) async throws -> PlacedTandemOrder {
        try await request("/shopping/\(uid)/cancel", method: "POST",
                          body: ["qrme_order_id": qrmeOrderId], token: token)
    }
}

// MARK: - Your circle (contacts, messages, switches, homepage)

struct CirclePersonRow: Decodable, Identifiable {
    let user_id: String
    let display_name: String?
    var id: String { user_id }
}

struct CircleThreadRow: Decodable, Identifiable {
    let other_id: String
    let other_name: String?
    let messages: Int
    let last_at: String
    var id: String { other_id }
}

struct CircleMessageRow: Decodable, Identifiable {
    let id: String
    let sender_id: String
    let body: String
    let sent_at: String
}

struct CircleLinkRow: Decodable {
    let label: String
    let url: String
}

struct CircleThemeRow: Decodable {
    let bg: String
    let accent: String
}

struct CircleHomepageRow: Decodable {
    let user_id: String
    let display_name: String?
    let headline: String
    let about: String
    let theme: CircleThemeRow
    let links: [CircleLinkRow]
    let top_friends: [CirclePersonRow]
    let editable: Bool
}

struct CircleRing: Decodable {
    let contacts: [CirclePersonRow]
    let invited_me: [CirclePersonRow]
    let awaiting: [CirclePersonRow]
}

struct CircleOverview: Decodable {
    let features: [String: Bool]
    let circle: CircleRing
    let threads: [CircleThreadRow]
    let homepage: CircleHomepageRow
    let labels: [String: String]
    let note: String
}

struct CircleTieRow: Decodable {
    let other_id: String
    let state: String
}

extension ApiClient {
    func circleView(uid: String, token: String) async throws -> CircleOverview {
        try await request("/circle/\(uid)", token: token)
    }

    func circleSetFeature(uid: String, token: String, feature: String,
                          enabled: Bool) async throws -> [String: Bool] {
        try await request("/circle/\(uid)/features", method: "PUT",
                          body: ["feature": feature, "enabled": enabled],
                          token: token)
    }

    func circleInvite(uid: String, token: String,
                      otherId: String) async throws -> CircleTieRow {
        try await request("/circle/\(uid)/contacts", method: "POST",
                          body: ["other_id": otherId], token: token)
    }

    func circleLeave(uid: String, token: String,
                     otherId: String) async throws -> CircleTieRow {
        try await request("/circle/\(uid)/contacts/\(otherId)",
                          method: "DELETE", token: token)
    }

    func circleSend(uid: String, token: String, to: String,
                    body: String) async throws -> CircleMessageRow {
        try await request("/circle/\(uid)/messages", method: "POST",
                          body: ["to": to, "body": body], token: token)
    }

    func circleThread(uid: String, token: String,
                      withId: String) async throws -> [CircleMessageRow] {
        struct Box: Decodable { let messages: [CircleMessageRow] }
        let q = withId.addingPercentEncoding(
            withAllowedCharacters: .urlQueryAllowed) ?? withId
        let box: Box = try await request(
            "/circle/\(uid)/messages?with_id=\(q)", token: token)
        return box.messages
    }

    func circleHomepage(uid: String, token: String,
                        otherId: String) async throws -> CircleHomepageRow {
        try await request("/circle/\(uid)/homepage/\(otherId)", token: token)
    }

    func circleEditHomepage(uid: String, token: String, headline: String,
                            about: String, bg: String,
                            accent: String) async throws -> CircleHomepageRow {
        try await request("/circle/\(uid)/homepage", method: "PUT",
                          body: ["headline": headline, "about": about,
                                 "theme": ["bg": bg, "accent": accent]],
                          token: token)
    }
}

// MARK: - Care team, clinical captures, and channel 2 (jim/careteam.py,
// jim/capture.py, jim/secondear.py) — the three console doors task #106
// built that the phones never got.

struct CareTeamPlanRow: Decodable, Identifiable {
    let id: String
    let goal: String
    let plan: String?
    let sealed_in_qrme_vault: Bool?
    let created_at: String?
}

struct CareTeamState: Decodable {
    let linked: Bool
    let org_id: String?
    let department_id: String?
    let credential_held: Bool?
    let latest_plan: CareTeamPlanRow?
}

/// Channel 2's current state. `capped` means a call is in progress and the
/// agent has narrowed itself regardless of the owner's setting.
struct MicStateRow: Decodable {
    let listening: Bool?
    let attached: Bool?
    let device: String?
    let mic_type: String?
    let gain: String?
    let effective_gain: String?
    let capped: Bool?
    let hears: String?
    let reason: String?
    let route: String?
    let note: String?
}

struct MicEventRow: Decodable, Identifiable {
    let id: String
    let device: String
    let mic_type: String
    let gain: String
    let reason: String?
    let live: Bool
    let started_at: String
    let ended_at: String?
}

struct MicTypeChoices: Decodable {
    let personal: [String]
    let ambient: [String]
    let rule: String?
}

/// Gain is not volume: every level is the owner at a different distance,
/// and `reaches_others` says plainly whether anyone else falls inside it.
struct MicGainChoices: Decodable {
    struct Level: Decodable { let gain: String; let reaches_others: Bool
                              let describes: String? }
    let levels: [Level]
    let defaultGain: String
    let rule: String?
    enum CodingKeys: String, CodingKey {
        case levels, rule
        case defaultGain = "default"
    }
}

/// The server describes the whole capture form: what may be photographed,
/// which of those sites are intimate, and how big a file may be.
struct CaptureVocabularyRow: Decodable {
    let kinds: [String: String]
    let sites: [String: String]
    let intimate: [String]
    let vault_required: Bool?
    let max_bytes: Int?
}

struct CaptureRecord: Decodable, Identifiable {
    let id: String
    let kind: String
    let site: String
    let provenance: String?
    let note: String?
    let condition: String?
    let intimate: Bool?
    let sealed: Bool?
    let created_at: String?
}

struct CaptureImageRow: Decodable {
    let id: String
    let kind: String
    let content: String    // base64, straight from the vault
}

struct CaptureAttachOutcome: Decodable {
    let attached: [String]?
    let explicit: [String]?
}

extension ApiClient {
    // -- the care team --------------------------------------------------

    func careTeamState(uid: String, token: String) async throws -> CareTeamState {
        try await request("/users/\(uid)/care-team", token: token)
    }

    func careTeamLink(uid: String, token: String, orgId: String,
                      departmentId: String,
                      ownerToken: String) async throws -> CareTeamState {
        try await request("/users/\(uid)/care-team", method: "PUT",
                          body: ["org_id": orgId,
                                 "department_id": departmentId,
                                 "owner_token": ownerToken], token: token)
    }

    func careTeamUnlink(uid: String, token: String) async throws {
        // The path is written out here, not handed to a helper: the client
        // scan reads paths at `request(` call sites, and a door it cannot
        // see is a door it counts as missing.
        struct Nothing: Decodable {}
        do {
            let _: Nothing = try await request("/users/\(uid)/care-team",
                                               method: "DELETE", token: token)
        } catch is DecodingError {
            // 204: empty body on success is exactly what the route promises.
        }
    }

    func careTeamCoordinate(uid: String, token: String,
                            goal: String) async throws -> CareTeamPlanRow {
        try await request("/users/\(uid)/care-team/coordinate",
                          method: "POST", body: ["goal": goal], token: token)
    }

    func careTeamPlans(uid: String,
                       token: String) async throws -> [CareTeamPlanRow] {
        try await request("/users/\(uid)/care-team/plans", token: token)
    }

    // -- channel 2, the lent microphone ---------------------------------

    func micTypes() async throws -> MicTypeChoices {
        try await request("/mic/types")
    }

    func micGains() async throws -> MicGainChoices {
        try await request("/mic/gains")
    }

    func micState(uid: String, token: String) async throws -> MicStateRow {
        try await request("/users/\(uid)/mic", token: token)
    }

    func attachMic(uid: String, token: String, deviceName: String,
                   micType: String) async throws -> MicStateRow {
        try await request("/users/\(uid)/mic", method: "PUT",
                          body: ["device_name": deviceName,
                                 "mic_type": micType], token: token)
    }

    func detachMic(uid: String, token: String) async throws -> MicStateRow {
        try await request("/users/\(uid)/mic", method: "DELETE", token: token)
    }

    func setMicGain(uid: String, token: String,
                    gain: String) async throws -> MicStateRow {
        try await request("/users/\(uid)/mic/gain", method: "PUT",
                          body: ["gain": gain], token: token)
    }

    func handOverMic(uid: String, token: String, reason: String,
                     route: String) async throws -> MicStateRow {
        try await request("/users/\(uid)/mic/handover", method: "POST",
                          body: ["reason": reason, "route": route],
                          token: token)
    }

    func releaseMic(uid: String, token: String) async throws -> MicStateRow {
        try await request("/users/\(uid)/mic/release", method: "POST",
                          token: token)
    }

    func micHistory(uid: String, token: String) async throws -> [MicEventRow] {
        try await request("/users/\(uid)/mic/history", token: token)
    }

    // -- clinical captures ----------------------------------------------

    func captureVocabulary() async throws -> CaptureVocabularyRow {
        try await request("/captures/vocabulary")
    }

    func captures(uid: String, token: String) async throws -> [CaptureRecord] {
        try await request("/users/\(uid)/captures", token: token)
    }

    func takeCapture(uid: String, token: String, kind: String, site: String,
                     contentBase64: String, note: String?,
                     intimateConsent: Bool) async throws -> CaptureRecord {
        var body: [String: Any] = ["kind": kind, "site": site,
                                   "content": contentBase64,
                                   "provenance": "captured",
                                   "intimate_consent": intimateConsent]
        if let note, !note.isEmpty { body["note"] = note }
        return try await request("/users/\(uid)/captures", method: "POST",
                                 body: body, token: token)
    }

    func captureImage(uid: String, token: String,
                      captureId: String) async throws -> CaptureImageRow {
        try await request("/users/\(uid)/captures/\(captureId)/image",
                          token: token)
    }

    func attachCaptures(uid: String, token: String,
                        captureIds: [String]) async throws -> CaptureAttachOutcome {
        try await request("/users/\(uid)/captures/attach", method: "POST",
                          body: ["capture_ids": captureIds], token: token)
    }

    func withdrawCapture(uid: String, token: String,
                         captureId: String) async throws {
        // The route answers with the tombstoned record, not a verdict —
        // the row remains so a clinician who was shown it sees "withdrawn"
        // rather than a dangling reference.
        let _: CaptureRecord = try await request(
            "/users/\(uid)/captures/\(captureId)", method: "DELETE",
            token: token)
    }
}

// MARK: - The health core: the cabinet, the vigil, and the baseline bands

/// One dose slot of a scheduled medication, as the board answers it:
/// taken | skipped | upcoming | due | missed.
struct MedSlot: Decodable {
    let slot: String
    let status: String
    let note: String?
}

/// A medication on today's board. Scheduled rows carry `slots`; as-needed
/// rows carry `taken_today` and `max_per_day` instead — the same union the
/// console renders.
struct MedRow: Decodable {
    let id: String
    let name: String
    let dose: String
    let purpose: String?
    let critical: Bool
    let notes: String?
    let archived: Bool
    let created_at: String
    let kind: String
    let slots: [MedSlot]?
    let taken_today: Int?
    let max_per_day: Int?
}

struct MissedDose: Decodable {
    let name: String
    let slot: String
}

struct MedsBoard: Decodable {
    let date: String
    let medications: [MedRow]
    let missed_critical: [MissedDose]
    let disclaimer: String
}

struct AdherenceRow: Decodable {
    let id: String
    let name: String
    let expected: Int
    let taken: Int
    let rate: Double?
}

struct MedAdherence: Decodable {
    let days: Int
    let medications: [AdherenceRow]
}

/// The vigil's whole answer. Until armed the route says `{"armed": false}`
/// and nothing else, which is why everything past `armed` is optional.
struct VigilStatus: Decodable {
    let armed: Bool
    let steward_name: String?
    let steward_channel: String?
    let quiet_days: Double?
    let note: String?
    let last_heard_at: String?
    let silent_hours: Double?
    let threshold_hours: Double?
    let tripped: Bool?
    let tripped_at: String?
    let resolved_at: String?
}

/// One metric's band: the learned baseline and where the edges sit. Edges
/// are null until the baseline stops being provisional — a threshold drawn
/// around two readings would be noise wearing a ruler.
struct BandRow: Decodable {
    let metric: String
    let label: String
    let unit: String
    let margin: Double
    let watch_high: Bool
    let watch_low: Bool
    let source: String
    let baseline: Double?
    let samples: Int
    let provisional: Bool
    let low_edge: Double?
    let high_edge: Double?
}

struct BandsOverview: Decodable {
    let user_id: String
    let sensitivity: String
    let bands: [BandRow]
}

extension ApiClient {

    // MARK: Medicine cabinet

    func medsBoard(uid: String, token: String) async throws -> MedsBoard {
        try await request("/meds/\(uid)", token: token)
    }

    func addMed(uid: String, token: String, name: String, dose: String,
                schedule: [String: Any], purpose: String?,
                critical: Bool) async throws -> MedRow {
        var body: [String: Any] = ["name": name, "dose": dose,
                                   "schedule": schedule, "critical": critical]
        if let purpose, !purpose.isEmpty { body["purpose"] = purpose }
        return try await request("/meds/\(uid)", method: "POST",
                                 body: body, token: token)
    }

    func setMedCritical(uid: String, token: String, medId: String,
                        critical: Bool) async throws -> MedRow {
        try await request("/meds/\(uid)/\(medId)", method: "PUT",
                          body: ["critical": critical], token: token)
    }

    /// Stopped, not deleted — the route keeps the history honest.
    func stopMed(uid: String, token: String, medId: String) async throws -> MedRow {
        try await request("/meds/\(uid)/\(medId)", method: "DELETE",
                          token: token)
    }

    func logDose(uid: String, token: String, medId: String, action: String,
                 slot: String?) async throws -> MedsBoard {
        var body: [String: Any] = ["action": action]
        if let slot { body["slot"] = slot }
        return try await request("/meds/\(uid)/\(medId)/log", method: "POST",
                                 body: body, token: token)
    }

    func medAdherence(uid: String, token: String) async throws -> MedAdherence {
        try await request("/meds/\(uid)/adherence", token: token)
    }

    // MARK: The vigil

    func vigilStatus(uid: String, token: String) async throws -> VigilStatus {
        try await request("/vigil/\(uid)", token: token)
    }

    func armVigil(uid: String, token: String, stewardName: String,
                  stewardChannel: String, quietDays: Double,
                  note: String?) async throws -> VigilStatus {
        var body: [String: Any] = ["steward_name": stewardName,
                                   "steward_channel": stewardChannel,
                                   "quiet_days": quietDays]
        if let note, !note.isEmpty { body["note"] = note }
        return try await request("/vigil/\(uid)", method: "PUT",
                                 body: body, token: token)
    }

    func disarmVigil(uid: String, token: String) async throws -> VigilStatus {
        try await request("/vigil/\(uid)", method: "DELETE", token: token)
    }

    /// Idempotent silence check; trips at most once. Opening the screen is
    /// the natural moment to ask whether anybody has gone quiet.
    func sweepVigil(uid: String, token: String) async throws -> VigilStatus {
        try await request("/vigil/\(uid)/sweep", method: "POST", token: token)
    }

    /// The "I'm okay" button.
    func resolveVigil(uid: String, token: String) async throws -> VigilStatus {
        try await request("/vigil/\(uid)/resolve", method: "POST", token: token)
    }

    // MARK: Baseline bands

    func bands(uid: String, token: String) async throws -> BandsOverview {
        try await request("/bands/\(uid)", token: token)
    }

    func setBand(uid: String, token: String, metric: String,
                 margin: Double?, watchHigh: Bool?,
                 watchLow: Bool?) async throws -> BandRow {
        var body: [String: Any] = [:]
        if let margin { body["margin"] = margin }
        if let watchHigh { body["watch_high"] = watchHigh }
        if let watchLow { body["watch_low"] = watchLow }
        return try await request("/bands/\(uid)/\(metric)", method: "PUT",
                                 body: body, token: token)
    }

    /// Back to the default width for this metric.
    func resetBand(uid: String, token: String,
                   metric: String) async throws -> BandRow {
        try await request("/bands/\(uid)/\(metric)", method: "DELETE",
                          token: token)
    }
}

// MARK: - Deployment settings: the voice it speaks in, the mail it sends through

struct VoiceRow: Decodable {
    let id: String
    let name: String
    let gender: String
    let note: String
}

/// What the API may say about the voice — never the key itself.
struct VoiceSettingsOut: Decodable {
    let provider: String
    let voice_id: String?
    let speak_replies: Bool
    let key_set: Bool
    let key_source: String
    let voices: [VoiceRow]
    let device_fallback: Bool
}

/// The mail configuration — never the password, only whether one is set.
struct MailSettingsOut: Decodable {
    let transport: String
    let source: String
    let host: String?
    let port: Int
    let username: String?
    let sender: String?
    let public_url: String
    let password_set: Bool
}

struct MailTestOut: Decodable {
    let sent: Bool
    let to: String
}

extension ApiClient {

    func voiceSettings() async throws -> VoiceSettingsOut {
        try await request("/settings/voice")
    }

    func saveVoiceSettings(provider: String, apiKey: String, voiceId: String,
                           speakReplies: Bool) async throws -> VoiceSettingsOut {
        var body: [String: Any] = ["provider": provider,
                                   "speak_replies": speakReplies]
        if !apiKey.isEmpty { body["api_key"] = apiKey }
        if !voiceId.isEmpty { body["voice_id"] = voiceId }
        return try await request("/settings/voice", method: "PUT",
                                 body: body, token: nil)
    }

    func clearVoiceSettings() async throws -> VoiceSettingsOut {
        try await request("/settings/voice", method: "DELETE")
    }

    func mailSettings() async throws -> MailSettingsOut {
        try await request("/settings/mail")
    }

    func saveMailSettings(host: String, port: Int, username: String,
                          password: String, sender: String,
                          publicUrl: String) async throws -> MailSettingsOut {
        var body: [String: Any] = ["host": host, "port": port]
        if !username.isEmpty { body["username"] = username }
        if !password.isEmpty { body["password"] = password }
        if !sender.isEmpty { body["sender"] = sender }
        if !publicUrl.isEmpty { body["public_url"] = publicUrl }
        return try await request("/settings/mail", method: "PUT", body: body)
    }

    /// Forget the mail server; delivery falls back to the console.
    func clearMailSettings() async throws -> MailSettingsOut {
        try await request("/settings/mail", method: "DELETE")
    }

    /// Send a real message now — a settings screen that saves without ever
    /// proving it can deliver is how an app ends up insisting it emailed
    /// somebody.
    func testMail(to: String) async throws -> MailTestOut {
        try await request("/settings/mail/test", method: "POST",
                          body: ["to": to])
    }
}

// MARK: - The guide, the help box, and the dock in the corner

/// One lesson, text mode: `what` and `screens` are present, `speak` is not.
struct TutorialStep: Decodable {
    let key: String
    let chapter: String
    let title: String
    let try_it: String
    let mode: String
    let what: String?
    let screens: [Int]?
}

struct TutorialChapter: Decodable {
    let chapter: String
    let steps: [TutorialStep]
}

/// The whole walkthrough, chaptered. The count is deliberately not
/// declared: `steps` means the lesson list inside a chapter and the tally
/// here, and one name with two meanings is not a shape to promise.
struct TutorialOutline: Decodable {
    let guide: String
    let chapters: [TutorialChapter]
}

struct TutorialProgress: Decodable {
    let learner_id: String
    let guide: String
    let step: TutorialStep?
    let done: Int
    let total: Int
    let finished: Bool
    let note: String
}

struct HelpTopics: Decodable {
    let topics: [String]
    let disclosure: String
}

struct HelpAnswer: Decodable {
    let answer: String
    let source: String
    let ai: Bool
    let disclosure: String
}

/// Everything needed to draw the pane — the product's shape, not anybody's
/// data. `faces` is a name-to-description table here and a chosen-names
/// list on the per-user settings; both are the wire's own words.
struct DockVocabulary: Decodable {
    let faces: [String: String]
    let corners: [String: String]
    let states: [String: String]
    let per_surface: [String]
    let acts: Bool
}

struct DockState: Decodable {
    let user_id: String
    let corner: String
    let state: String
    let face: String?
    let faces: [String]
    let `set`: Bool
    let wanted: String
    let forced: Bool
    let why: String?
}

struct DockWhere: Decodable {
    let face: String
    let screen: Int
    let path: String
    let title: String
    let opens_dock_face: String
}

struct DockFace: Decodable {
    let face: String
    let shows: String
    let user_id: String
    let surface_id: String?
    let acts: Bool
    let never: [String]
}

extension ApiClient {

    func tutorialOutline() async throws -> TutorialOutline {
        try await request("/tutorial")
    }

    func tutorialStep(key: String) async throws -> TutorialStep {
        try await request("/tutorial/steps/\(key)")
    }

    /// The lesson covering a given screen, so a screen can explain itself.
    func tutorialForScreen(number: Int) async throws -> TutorialStep {
        try await request("/tutorial/for-screen/\(number)")
    }

    func startTutorial(learnerId: String) async throws -> TutorialProgress {
        try await request("/tutorial/start", method: "POST",
                          body: ["learner_id": learnerId])
    }

    func tutorialProgress(learnerId: String) async throws -> TutorialProgress {
        try await request("/tutorial/progress/\(learnerId)")
    }

    func markTutorialDone(learnerId: String,
                          lesson: String) async throws -> TutorialProgress {
        try await request("/tutorial/done", method: "POST",
                          body: ["learner_id": learnerId, "lesson": lesson])
    }

    func helpTopics() async throws -> HelpTopics {
        try await request("/help/topics")
    }

    /// The help box: "where is the thing?" It writes nothing.
    func askHelp(question: String) async throws -> HelpAnswer {
        try await request("/help", method: "POST",
                          body: ["question": question])
    }

    func dockVocabulary() async throws -> DockVocabulary {
        try await request("/dock/faces")
    }

    func dockState(uid: String, token: String) async throws -> DockState {
        try await request("/dock/\(uid)", token: token)
    }

    func configureDock(uid: String, token: String, corner: String?,
                       state: String?, face: String?) async throws -> DockState {
        var body: [String: Any] = [:]
        if let corner { body["corner"] = corner }
        if let state { body["state"] = state }
        if let face { body["face"] = face }
        return try await request("/dock/\(uid)", method: "PUT",
                                 body: body, token: token)
    }

    /// One face, as the pane would draw it. Read-only by construction.
    func dockFace(uid: String, token: String,
                  name: String) async throws -> DockFace {
        try await request("/dock/\(uid)/face/\(name)", token: token)
    }

    /// The screen that can actually do this face's job.
    func dockWhere(face: String) async throws -> DockWhere {
        try await request("/dock/where/\(face)")
    }
}

// MARK: - The wrist and the doorway: watch channel, devices, pairing

struct WatchDeviceRow: Decodable {
    let key: String
    let name: String
}

/// The setup card: drip URL, this device's recipe, arrivals so far — and
/// the device list itself, so the picker renders from the API rather than
/// being hardcoded four times.
struct WatchSetup: Decodable {
    let drip_url: String
    let phone_reachable: Bool
    let last_drip_at: String?
    let drips: Int
    let device: String
    let devices: [WatchDeviceRow]
    let steps: [String]
    let seed_hint: String
}

/// How to open the Guardian on a phone: the console's URL on this local
/// network. Same Wi-Fi, no app store.
struct DripAck: Decodable {
    let received: Int
    let noticed: Bool
}

struct PairInfo: Decodable {
    let console_url: String
    let api_url: String
    let console_built: Bool
    let reachable: Bool
    let hosted: Bool
    let qr_svg: String
    let how: [String]
    let note: String
}

struct DeviceRow: Decodable {
    let id: String
    let user_id: String
    let name: String
    let kind: String
    let transport: String?
    let has_llm: Bool
    let linked_to: String?
    let paired: Bool
    let created_at: String
}

struct SeedReceipt: Decodable {}

extension ApiClient {

    func watchSetup(uid: String, token: String,
                    device: String = "apple_watch") async throws -> WatchSetup {
        try await request("/watch/channel/\(uid)?device=\(device)",
                          token: token)
    }

    /// Rotating invalidates the old drip token; the card re-renders with
    /// the new address.
    func rotateWatchChannel(uid: String, token: String) async throws -> WatchSetup {
        try await request("/watch/channel/\(uid)/rotate", method: "POST",
                          token: token)
    }

    /// Upload the Health app's export.zip (or bare export.xml). History
    /// folds into baselines only — enrollment day should be quiet.
    func seedWatch(uid: String, token: String, data: Data) async throws {
        let _: SeedReceipt = try await request(
            "/watch/seed/\(uid)", method: "POST", token: token, rawBody: data)
    }

    func pairInfo() async throws -> PairInfo {
        try await request("/pair")
    }

    /// The three QR images. The JSON helper cannot carry an image, so the
    /// door is the URL the opener fetches; building it here is what the
    /// route audit reads. Absent a verb, GET stands — URLSession's own
    /// default for a bare URL.
    func pairQrUrl() -> URL {
        base.appendingPathComponent("/pair/qr.svg")
    }

    func beaconQrUrl(bid: String) -> URL {
        base.appendingPathComponent("/c/\(bid)/qr.svg")
    }

    func connectionQrUrl(cid: String) -> URL {
        base.appendingPathComponent("/social/connection/\(cid)/qr.svg")
    }

    /// One reading through the Shortcut's own door. The token in the path
    /// is the whole credential, so no account token rides along — and the
    /// reply carries counts and nothing else, by that route's own rule.
    func watchDrip(dripToken: String, heartRate: Int) async throws -> DripAck {
        try await request("/watch/drip/\(dripToken)", method: "POST",
                          body: ["heart_rate": heartRate])
    }

    func devices(uid: String, token: String) async throws -> [DeviceRow] {
        try await request("/devices/\(uid)", token: token)
    }

    func registerDevice(uid: String, token: String, name: String,
                        kind: String, paired: Bool) async throws -> DeviceRow {
        try await request("/devices/\(uid)", method: "POST",
                          body: ["name": name, "kind": kind,
                                 "paired": paired], token: token)
    }
}

// MARK: - The account the phones never had

/// Two shapes under one roof, the way the route answers: a deployment with
/// mail sends the code and answers pending; a local install with no mail
/// transport activates directly and answers with the session.
struct SignupResult: Decodable {
    let email: String
    let verified: Bool
    let verification: String
    let account_id: String?
    let code_delivery: String?
    let id: String?
    let display_name: String?
    let user_token: String?
}

struct SignInResult: Decodable {
    let account_id: String
    let email: String
    let user_id: String
    let display_name: String?
    let user_token: String
}

struct CodeDelivery: Decodable { let email: String; let code_delivery: String }

struct ResetDone: Decodable { let email: String; let reset: Bool }

struct OAuthProviderRow: Decodable {
    let provider: String
    let name: String
    let configured: Bool
    let setup: String?
}

struct OAuthProviders: Decodable { let providers: [OAuthProviderRow] }

struct OAuthStarted: Decodable {
    let provider: String
    let state: String
    let url: String
}

/// The claim is polled: not-ready is `ready` alone, and ready carries the
/// session — a fresh account's full enrollment or a returning one's token.
struct OAuthClaim: Decodable {
    let ready: Bool
    let id: String?
    let display_name: String?
    let user_token: String?
    let email: String?
}

struct ContinuityTurn: Decodable { let role: String; let content: String }

struct SessionContinuity: Decodable {
    let with: String
    let recent_turns: [ContinuityTurn]
    let note: String
}

struct SessionStarted: Decodable {
    let id: String
    let device: String?
    let prior_sessions: Int
    let memory: String?
    let continuity: SessionContinuity?
}

struct SessionEnded: Decodable { let id: String; let ended: Bool }

extension ApiClient {

    func signup(email: String, password: String, name: String,
                birthdate: String? = nil,
                language: String? = nil) async throws -> SignupResult {
        var body: [String: Any] = ["email": email, "password": password,
                                   "display_name": name,
                                   "terms_consent": true]
        if let birthdate, !birthdate.isEmpty { body["birthdate"] = birthdate }
        if let language, language != "en" { body["language"] = language }
        return try await request("/signup", method: "POST", body: body)
    }

    func signin(email: String, password: String) async throws -> SignInResult {
        try await request("/signin", method: "POST",
                          body: ["email": email, "password": password])
    }

    /// The code proves the inbox; the user is enrolled here, not at signup,
    /// which is why this answers with the same shape enrollment does.
    func verifyEmail(email: String, code: String) async throws -> EnrollResult {
        try await request("/verify-email", method: "POST",
                          body: ["email": email, "code": code])
    }

    func resendCode(email: String) async throws -> CodeDelivery {
        try await request("/verify-email/resend", method: "POST",
                          body: ["email": email])
    }

    func requestPasswordReset(email: String) async throws -> CodeDelivery {
        try await request("/password/reset/request", method: "POST",
                          body: ["email": email])
    }

    /// Every existing session dies with the old password.
    func resetPassword(email: String, code: String,
                       newPassword: String) async throws -> ResetDone {
        try await request("/password/reset", method: "POST",
                          body: ["email": email, "code": code,
                                 "new_password": newPassword])
    }

    func oauthProviders() async throws -> OAuthProviders {
        try await request("/auth/oauth/providers")
    }

    /// No redirect_uri: the backend defaults to its own callback page, and
    /// the phone polls the claim rather than intercepting the browser.
    func oauthStart(provider: String) async throws -> OAuthStarted {
        try await request("/auth/oauth/\(provider)/start", method: "POST",
                          body: [:])
    }

    func oauthClaim(state: String) async throws -> OAuthClaim {
        try await request("/auth/oauth/claim?state=\(state)")
    }

    func startSession(uid: String, token: String,
                      device: String) async throws -> SessionStarted {
        try await request("/sessions/\(uid)", method: "POST",
                          body: ["device": device], token: token)
    }

    func endSession(uid: String, token: String,
                    sessionId: String) async throws -> SessionEnded {
        try await request("/sessions/\(uid)/\(sessionId)/end", method: "POST",
                          token: token)
    }
}

// MARK: - The Guardian learns the day

struct CalmSessionRow: Decodable {
    let kind: String
    let title: String
    let minutes: Int
    let what: String
}

struct CalmCatalog: Decodable { let sessions: [CalmSessionRow] }

struct CalmStep: Decodable { let say: String; let seconds: Int }

/// A protocol, not a generation — the counts never vary.
struct CalmStarted: Decodable {
    let kind: String
    let title: String
    let what: String
    let total_seconds: Int
    let steps: [CalmStep]
    let note: String
}

struct CalmHistoryRow: Decodable {
    let kind: String
    let title: String
    let seconds: Int
    let at: String
}

struct WorkoutBlock: Decodable { let name: String; let seconds: Int; let cue: String }

struct WorkoutPlan: Decodable {
    let minutes_asked: Int
    let level: String
    let focus: String
    let rest_seconds_between_blocks: Int
    let blocks: [WorkoutBlock]
}

struct MealRow: Decodable { let slot: String; let name: String }

struct MealDay: Decodable { let day_number: Int; let meals: [MealRow] }

struct MealShape: Decodable {
    let meals_per_day: Int
    let orientation_calories: Int
    let why: String
}

struct MealPlan: Decodable {
    let goal: String
    let preferences: [String]
    let shape: MealShape
    let days: [MealDay]
    let disclaimer: String
}

/// Ambient watching: the Guardian noting an ordinary activity so a moved
/// heart rate has a why before it has to guess one.
struct ActivityWatch: Decodable {
    let activity: String?
    let proactive: Bool
    let watching: Bool
    let intervention: Guidance?
}

struct ConditionsKnown: Decodable {
    let user_id: String
    let known_conditions: [String]
}

struct PersonalitySaved: Decodable { let user_id: String }

struct InsightRow: Decodable {
    let id: String
    let area: String
    let kind: String
    let message: String
    let source: String?
}

struct ContextAdded: Decodable {
    let id: String
    let source: String
    let kind: String
    let vaulted: Bool
    let insights: [InsightRow]
}

struct FeedbackSaved: Decodable {
    let id: String
    let rating: String
    let contributed: Bool
}

struct EventRow: Decodable {
    let id: String
    let type: String
    let condition: String?
    let severity: String?
    let created_at: String
}

struct ReportCheckins: Decodable {
    let count: Int
    let avg_mood: Double?
    let avg_energy: Double?
    let avg_stress: Double?
}

struct ProgressReport: Decodable {
    let checkins: ReportCheckins
    let detections: [String: Int]
    let insights: Int
    let journal_entries: Int
    let feedback: [String: Int]
}

struct CompanionSaid: Decodable {
    let delivered: Bool
    let unprompted: Bool
    let content: String
}

struct CoachExchange: Decodable {
    let id: String
    let area: String
    let role: String
    let content: String
    let created_at: String
}

extension ApiClient {

    func calmCatalog() async throws -> CalmCatalog {
        try await request("/calm")
    }

    func startCalm(uid: String, token: String,
                   kind: String) async throws -> CalmStarted {
        try await request("/calm/\(uid)/\(kind)", method: "POST", token: token)
    }

    func calmHistory(uid: String, token: String) async throws -> [CalmHistoryRow] {
        try await request("/calm/\(uid)/history", token: token)
    }

    func workoutPlan(uid: String, token: String, minutes: Int, level: String,
                     focus: String) async throws -> WorkoutPlan {
        try await request("/fitness/\(uid)/plan", method: "POST",
                          body: ["minutes": minutes, "level": level,
                                 "focus": focus], token: token)
    }

    func mealPlan(uid: String, token: String, goal: String,
                  preferences: [String], days: Int) async throws -> MealPlan {
        try await request("/nutrition/\(uid)/plan", method: "POST",
                          body: ["goal": goal, "preferences": preferences,
                                 "days": days], token: token)
    }

    func observeActivity(uid: String, token: String, activity: String,
                         note: String?) async throws -> ActivityWatch {
        var body: [String: Any] = ["activity": activity]
        if let note, !note.isEmpty { body["note"] = note }
        return try await request("/activity/\(uid)", method: "POST",
                                 body: body, token: token)
    }

    func declareCondition(uid: String, token: String, condition: String,
                          note: String?) async throws -> ConditionsKnown {
        var body: [String: Any] = ["condition": condition]
        if let note, !note.isEmpty { body["note"] = note }
        return try await request("/conditions/\(uid)", method: "POST",
                                 body: body, token: token)
    }

    func setPersonality(uid: String, token: String,
                        tone: String) async throws -> PersonalitySaved {
        try await request("/personality/\(uid)", method: "PUT",
                          body: ["tone": tone], token: token)
    }

    /// The server checks the consent, not this shell — a refusal is shown
    /// in the server's words.
    func giveContext(uid: String, token: String, source: String, kind: String,
                     data: [String: Any]) async throws -> ContextAdded {
        try await request("/context/\(uid)", method: "POST",
                          body: ["source": source, "kind": kind,
                                 "data": data], token: token)
    }

    func updateGoal(uid: String, token: String, goalId: String,
                    progress: Double, status: String) async throws -> Goal {
        try await request("/goals/\(uid)/\(goalId)", method: "PATCH",
                          body: ["progress": progress, "status": status],
                          token: token)
    }

    func insights(uid: String, token: String) async throws -> [InsightRow] {
        try await request("/insights/\(uid)", token: token)
    }

    func events(uid: String, token: String) async throws -> [EventRow] {
        try await request("/events/\(uid)", token: token)
    }

    func progressReport(uid: String, token: String) async throws -> ProgressReport {
        try await request("/report/\(uid)", token: token)
    }

    func companionCheckin(uid: String, token: String) async throws -> CompanionSaid {
        try await request("/companion/\(uid)", method: "POST", token: token)
    }

    func sendGuidanceFeedback(uid: String, token: String,
                              rating: String) async throws -> FeedbackSaved {
        try await request("/feedback/\(uid)", method: "POST",
                          body: ["rating": rating], token: token)
    }

    func coachHistory(uid: String, token: String) async throws -> [CoachExchange] {
        try await request("/coach/\(uid)", token: token)
    }
}

// MARK: - The specialist economy

struct SpecialistRow: Decodable {
    let condition: String
    let mode: String
    let label: String
    let qrme_profile_id: String?
}

struct SpecialistsSeeded: Decodable {
    let created: Int
    let skipped: Int
    let conditions: Int
}

struct CatalogStarter: Decodable {
    let profile_id: String?
    let display_name: String?
}

struct SpecialistCatalog: Decodable {
    let starters: [CatalogStarter]?
    let note: String?
}

/// One QRME profile the attach bracket found, beyond the curated shelf.
///
/// `attachable` and `standing` are two fields rather than one: an
/// age-restricted profile *is* attachable and still carries a caveat
/// somebody needs to read, so collapsing the pair would either hide the
/// caveat or refuse a profile that works.
struct SpecialistFound: Decodable, Identifiable {
    let profile_id: String
    let display_name: String
    let purpose: String?
    let blurb: String?
    let found_by: String?
    let attachable: Bool
    let standing: String?

    var id: String { profile_id }
}

struct SpecialistSearch: Decodable {
    let results: [SpecialistFound]
    let capped: Bool
    let limit: Int
}

struct ClinicianRow: Decodable {
    let id: String?
    let label: String?
    let display_name: String?
}

struct ClinicianSearch: Decodable {
    let area: String
    let locality: String?
    let clinicians: [ClinicianRow]
    let reason: String?
}

/// Nothing is released by preparing: the response carries the package for
/// the user to read, and the signing ceremony belongs to QRME.
struct ReferralPrepared: Decodable {
    let prepared: Bool
    let reason: String?
    let referral_request_id: String?
    let display_text: String?
    let note: String?
}

struct ReferralRequestRow: Decodable {
    let id: String
    let condition: String
    let provider_id: String
    let qrme_referral_id: String?
    let created_at: String
}

struct ReferralReleased: Decodable { let referral_request_id: String }

/// A refusal is a 200-shaped answer with `started: false` and a reason —
/// "this specialist doesn't accept delegated work" is information, not a
/// fault.
struct SpecialistTaskStarted: Decodable {
    let started: Bool
    let reason: String?
    let id: String?
}

struct SpecialistTaskRow: Decodable {
    let id: String
    let goal: String
    let status: String
    let qrme_profile_id: String?
    let created_at: String
    let updated_at: String
}

struct SpecialistTaskView: Decodable {
    let id: String
    let goal: String
    let status: String
    let reachable: Bool
    let note: String?
    let next_phase: String?
}

/// What a consented care provider sees — and therefore what the person can
/// see that they see.
struct ProviderSummary: Decodable {
    let user_id: String
    let display_name: String?
    let known_conditions: [String]
    let escalations: Int
    let avg_mood: Double?
}

extension ApiClient {

    func specialists() async throws -> [SpecialistRow] {
        try await request("/specialists")
    }

    func seedSpecialists() async throws -> SpecialistsSeeded {
        try await request("/specialists/seed", method: "POST")
    }

    func seedTandemSpecialists() async throws -> SpecialistsSeeded {
        try await request("/specialists/seed/tandem", method: "POST")
    }

    func specialistsCatalog() async throws -> SpecialistCatalog {
        try await request("/specialists/catalog")
    }

    /// Anyone on QRME, not only the thirty-four on the shelf. Takes a
    /// `@handle`, a `prof_…` id, or words.
    func searchSpecialists(query: String) async throws -> SpecialistSearch {
        let q = query.addingPercentEncoding(
            withAllowedCharacters: .urlQueryAllowed) ?? query
        return try await request("/specialists/search?q=\(q)")
    }

    func attachSpecialist(condition: String, qrmeProfileId: String,
                          label: String) async throws -> SpecialistRow {
        try await request("/specialists", method: "POST",
                          body: ["condition": condition, "mode": "tandem",
                                 "qrme_profile_id": qrmeProfileId,
                                 "label": label])
    }

    func referralClinicians(uid: String, token: String,
                            condition: String) async throws -> ClinicianSearch {
        try await request(
            "/users/\(uid)/referral/clinicians?condition=\(condition)",
            token: token)
    }

    func prepareReferral(uid: String, token: String, condition: String,
                         providerId: String) async throws -> ReferralPrepared {
        try await request("/users/\(uid)/referral/prepare", method: "POST",
                          body: ["condition": condition,
                                 "provider_id": providerId], token: token)
    }

    /// A report, not an action: the signature was raised against QRME's
    /// relying party, which this Guardian cannot observe.
    func markReferralReleased(uid: String, token: String,
                              requestId: String) async throws -> ReferralReleased {
        try await request(
            "/users/\(uid)/referral/requests/\(requestId)/released",
            method: "POST", token: token)
    }

    func referralRequests(uid: String,
                          token: String) async throws -> [ReferralRequestRow] {
        try await request("/users/\(uid)/referral/requests", token: token)
    }

    func startSpecialistTask(uid: String, token: String, condition: String,
                             goal: String) async throws -> SpecialistTaskStarted {
        try await request("/users/\(uid)/specialist-tasks", method: "POST",
                          body: ["condition": condition, "goal": goal],
                          token: token)
    }

    func specialistTasks(uid: String,
                         token: String) async throws -> [SpecialistTaskRow] {
        try await request("/users/\(uid)/specialist-tasks", token: token)
    }

    func specialistTask(uid: String, token: String,
                        taskId: String) async throws -> SpecialistTaskView {
        try await request("/users/\(uid)/specialist-tasks/\(taskId)",
                          token: token)
    }

    func advanceSpecialistTask(uid: String, token: String,
                               taskId: String) async throws -> SpecialistTaskView {
        try await request("/users/\(uid)/specialist-tasks/\(taskId)/advance",
                          method: "POST", token: token)
    }

    func providerSummary(uid: String,
                         token: String) async throws -> ProviderSummary {
        try await request("/provider/\(uid)", token: token)
    }
}

// MARK: - The record and the veil

/// Who has read your record. An empty list with no record being kept is a
/// different fact from nobody having looked, and the shape says which.
struct AccessLog: Decodable {
    let vaulted: Bool
    let access_record_kept: Bool
    let entries: [AccessLogEntry]
    let note: String
}

struct AccessLogEntry: Decodable {
    let action: String?
    let at: String?
}

struct CloudStatus: Decodable {
    let cloud: Bool
    let model: String?
    let fallback: String
    let contribution: String
}

struct ContributionView: Decodable {
    let opted_in: Bool
    let policy: String
}

struct ContributionRevoked: Decodable {
    let opted_in: Bool
    let revoked: Int
    let note: String
}

struct IncidentRow: Decodable {
    let id: String?
    let kind: String?
    let at: String?
}

struct PageRow: Decodable {
    let id: String?
    let to: String?
    let delivered: Bool?
    let sent_at: String?
}

struct LocalitySaved: Decodable {
    let user_id: String
    let locality: String?
}

struct PlanRow: Decodable {
    let plan: String
    let title: String
    let price_usd: Double
    let period: String?
}

struct PlansOut: Decodable { let plans: [PlanRow] }

extension ApiClient {

    func accessLog(uid: String, token: String) async throws -> AccessLog {
        try await request("/access-log/\(uid)", token: token)
    }

    func cloudStatus() async throws -> CloudStatus {
        try await request("/cloud/status")
    }

    func cloudContribution(uid: String,
                           token: String) async throws -> ContributionView {
        try await request("/users/\(uid)/cloud-contribution", token: token)
    }

    func revokeCloudContribution(uid: String,
                                 token: String) async throws -> ContributionRevoked {
        try await request("/users/\(uid)/cloud-contribution/revoke",
                          method: "POST", token: token)
    }

    /// Open, unaccepted alarms on this account's site beacons — incident
    /// scope, never person scope.
    func incidents(uid: String, token: String) async throws -> [IncidentRow] {
        try await request("/users/\(uid)/incidents", token: token)
    }

    /// Escalations and whether each reached anyone.
    func pages(uid: String, token: String) async throws -> [PageRow] {
        try await request("/users/\(uid)/pages", token: token)
    }

    /// Used only to find local rooms and events through the community door.
    func setLocality(uid: String, token: String,
                     locality: String) async throws -> LocalitySaved {
        try await request("/users/\(uid)/locality", method: "PUT",
                          body: ["locality": locality], token: token)
    }

    func plans() async throws -> PlansOut {
        try await request("/plans")
    }
}

// MARK: - The purse and the membership

struct BudgetRow: Decodable {
    let category: String
    let monthly_limit: Double
    let spent: Double
    let standing: String
}

struct BudgetsOut: Decodable {
    let month: String
    let days_left: Int
    let budgets: [BudgetRow]
}

struct BudgetRemoved: Decodable { let removed: Bool }

/// The storage posture a plan buys, in the plan sheet's own words.
struct StoragePosture: Decodable {
    let title: String
    let means: String
    let who_can_read: [String]
}

struct MembershipView: Decodable {
    let account_id: String
    let plan: String
    let title: String
    let price_usd: Double
    let period: String?
    let includes: [String]
    let locked: [String]
    let storage: StoragePosture
}

extension ApiClient {

    func budgets(uid: String, token: String) async throws -> BudgetsOut {
        try await request("/budgets/\(uid)", token: token)
    }

    /// This much per month for this category.
    func setBudget(uid: String, token: String, category: String,
                   monthlyLimit: Double) async throws -> BudgetRow {
        try await request("/budgets/\(uid)", method: "PUT",
                          body: ["category": category,
                                 "monthly_limit": monthlyLimit], token: token)
    }

    func clearBudget(uid: String, token: String,
                     category: String) async throws -> BudgetRemoved {
        try await request("/budgets/\(uid)/\(category)", method: "DELETE",
                          token: token)
    }

    /// The route says account and means the person: tiers are keyed by the
    /// user id, and the bearer must be that user's own.
    func membership(uid: String, token: String) async throws -> MembershipView {
        try await request("/memberships/\(uid)", token: token)
    }

    /// Join a plan or move between them. Billing is simulated and the
    /// response says so.
    func subscribe(uid: String, token: String,
                   plan: String) async throws -> MembershipView {
        try await request("/memberships/\(uid)", method: "POST",
                          body: ["plan": plan], token: token)
    }

    /// End it. The person keeps their record, their conditions and every
    /// emergency path.
    func cancelMembership(uid: String,
                          token: String) async throws -> MembershipView {
        try await request("/memberships/\(uid)", method: "DELETE",
                          token: token)
    }
}

// MARK: - The sticker and the relay

/// A sticker someone can scan to reach help on your behalf. The scanner
/// needs no account and sees only what the owner chose to put on the card.
struct BeaconRow: Decodable {
    let id: String
    let label: String
    let placement: String?
    let kind: String
    let scans: Int
    let active: Bool
    let scan_url: String
}

struct BeaconCardOut: Decodable {
    let beacon: String
    let first_name: String?
    let watched: Bool?
    let note: String?
    let badge: String?
    let call_first: String?
}

struct BeaconAlarm: Decodable {
    let alarm: String
    let raised: Bool
    let tier: String?
    let badge: String?
    let note: String?
}

struct BeaconRetired: Decodable { let id: String; let active: Bool }

struct RelayChannel: Decodable {
    let configured: Bool
    let envelope: String?
    let note: String
}

struct RelayRoster: Decodable {
    let configured: Bool
    let roster: [String]
    let ceiling: String
    let note: String
}

struct RelayRota: Decodable {
    let configured: Bool
    let timezone: String
    let on_now: [String]
    let anybody_on_shift: Bool
    let note: String
}

struct SocialBeacon: Decodable {
    let connection: String
    let platform: String
    let handle: String
    let presence_url: String
}

struct SocialGone: Decodable { let id: String; let status: String }

struct RobotUnbound: Decodable { let id: String? }

extension ApiClient {

    func beacons(uid: String, token: String) async throws -> [BeaconRow] {
        try await request("/users/\(uid)/beacons", token: token)
    }

    func placeBeacon(uid: String, token: String, label: String,
                     placement: String?) async throws -> BeaconRow {
        var body: [String: Any] = ["kind": "site", "label": label]
        if let placement, !placement.isEmpty { body["placement"] = placement }
        return try await request("/users/\(uid)/beacons", method: "POST",
                                 body: body, token: token)
    }

    func retireBeacon(bid: String, token: String) async throws -> BeaconRetired {
        try await request("/beacons/\(bid)", method: "DELETE", token: token)
    }

    /// What a stranger sees before deciding to raise the alarm — public on
    /// purpose, the scanner has no account.
    func beaconCard(bid: String) async throws -> BeaconCardOut {
        try await request("/c/\(bid)/card")
    }

    func raiseBeaconAlarm(bid: String,
                          situation: String?) async throws -> BeaconAlarm {
        var body: [String: Any] = [:]
        if let situation, !situation.isEmpty { body["situation"] = situation }
        return try await request("/c/\(bid)/alarm", method: "POST", body: body)
    }

    /// The scanned page itself is HTML for a stranger's browser; fetching it
    /// proves the door is live before handing the page to the system one.
    func scannedBeaconPage(bid: String) async throws -> String {
        var req = URLRequest(url: base.appendingPathComponent("/c/\(bid)"))
        req.httpMethod = "GET"
        req.setValue(L10n.deviceLanguage, forHTTPHeaderField: "accept-language")
        let (data, _) = try await URLSession.shared.data(for: req)
        return String(data: data, encoding: .utf8) ?? ""
    }

    func relayChannel() async throws -> RelayChannel {
        try await request("/relay/channel")
    }

    func relayRoster() async throws -> RelayRoster {
        try await request("/relay/roster")
    }

    func relayRota() async throws -> RelayRota {
        try await request("/relay/rota")
    }

    func socialBeacon(cid: String, token: String) async throws -> SocialBeacon {
        try await request("/social/connection/\(cid)/beacon", token: token)
    }

    func disconnectSocial(cid: String, token: String) async throws -> SocialGone {
        try await request("/social/connection/\(cid)", method: "DELETE",
                          token: token)
    }

    func unbindRobot(uid: String, token: String,
                     robotId: String) async throws -> RobotUnbound {
        try await request("/robots/\(uid)/\(robotId)", method: "DELETE",
                          token: token)
    }

    // ---- safe knowledge excursions + the community window ----

    func excursions(uid: String, token: String) async throws -> [ExcursionRow] {
        try await request("/excursions/\(uid)", token: token)
    }

    func startExcursion(uid: String, token: String, topic: String,
                        question: String) async throws -> ExcursionRow {
        try await request("/excursions/\(uid)", method: "POST",
                          body: ["topic": topic, "question": question],
                          token: token)
    }

    func excursionEntry(cid: String, token: String) async throws -> ExcursionRow {
        try await request("/excursions/entry/\(cid)", token: token)
    }

    func learnExcursion(cid: String, token: String) async throws -> ExcursionLearned {
        try await request("/excursions/entry/\(cid)/learn", method: "POST",
                          body: [:], token: token)
    }

    func communityVisits(uid: String, token: String) async throws -> [CommunityVisitRow] {
        try await request("/community/\(uid)/visits", token: token)
    }

    func communityFeed(uid: String, token: String) async throws -> CommunityFeedView {
        try await request("/community/\(uid)/feed", token: token)
    }

    // ---- the voice pair: say it aloud, and hear what was said ----

    /// Text in, audio out. A deployment with no speaking service answers
    /// 503 — the card falls back to the device's own voice, because
    /// silence would be the wrong failure.
    func speakAloud(text: String, voiceId: String? = nil) async throws -> Data {
        var req = URLRequest(url: base.appendingPathComponent("/voice/speak"))
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "content-type")
        req.setValue(L10n.deviceLanguage, forHTTPHeaderField: "accept-language")
        var body: [String: Any] = ["text": text]
        if let voiceId, !voiceId.isEmpty { body["voice_id"] = voiceId }
        req.httpBody = try JSONSerialization.data(withJSONObject: body)
        let (data, resp) = try await URLSession.shared.data(for: req)
        guard let http = resp as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
            // The path from the request itself, not a second literal the
            // route audit would have to attribute on its own.
            Problems.record(method: "POST", path: req.url?.path ?? "",
                            status: status)
            let said = (try? JSONSerialization.jsonObject(with: data))
                as? [String: Any]
            let message = (said?["message"] as? String)
                ?? (said?["detail"] as? String) ?? "HTTP \(status)"
            throw ApiError.http(message)
        }
        return data
    }

    /// Recorded speech in, words out. The audio is not stored server-side.
    func transcribe(audioBase64: String,
                    filename: String) async throws -> Transcribed {
        try await request("/voice/transcribe", method: "POST",
                          body: ["audio_base64": audioBase64,
                                 "filename": filename])
    }
}

struct Transcribed: Decodable { let text: String }

// ---- safe knowledge excursions + the community window ----

/// One studied topic: what was asked, how much of the person was redacted
/// out before the question left, whether it left this host at all, and what
/// came back.
struct ExcursionRow: Decodable {
    let id: String
    let topic: String
    let brief: String?
    let redactions: Int
    let left_host: Bool
    let findings: String?
    let learned: Bool
}

struct ExcursionLearned: Decodable {
    let learned: Bool
    let already_learned: Bool
    let note: String?
}

/// A community door that was opened: the room's id and the time, on the
/// person's own timeline, and nothing from inside the room.
struct CommunityVisitRow: Decodable {
    let room_id: String?
    let at: String?
}

struct CommunityFeedItem: Decodable {
    let id: String?
    let kind: String?
    let title: String?
    let topic: String?
}

/// QRME's public feed through the tandem — read-only by construction, and a
/// 409 with the server's own sentence when no QRME endpoint is configured.
struct CommunityFeedView: Decodable {
    let qrme_url: String?
    let language: String?
    let items: [CommunityFeedItem]
    let cursor: String?
    let note: String
    let open_in_qrme: String?
}
