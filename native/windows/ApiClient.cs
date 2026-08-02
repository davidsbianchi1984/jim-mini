using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace JimGuardian;

// MARK: wire models (mirror jim/api.py)

public record EnrollResult(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("user_token")] string UserToken);

public record PaceCue(
    [property: JsonPropertyName("light")] string Light,
    [property: JsonPropertyName("audio")] string Audio);

public record Pace(
    [property: JsonPropertyName("compressions_per_minute")] int CompressionsPerMinute,
    [property: JsonPropertyName("compression_to_breath_ratio")] string CompressionToBreathRatio,
    [property: JsonPropertyName("cue")] PaceCue? Cue);

public record FirstAid(
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("call_emergency_services")] bool? CallEmergencyServices,
    [property: JsonPropertyName("steps")] string[] Steps,
    [property: JsonPropertyName("pace")] Pace? Pace);

public record Evidence(
    [property: JsonPropertyName("publisher")] string Publisher,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("url")] string Url,
    [property: JsonPropertyName("supports")] string? Supports);

public record Provenance(
    [property: JsonPropertyName("method")] string Method,
    [property: JsonPropertyName("generated_by")] string GeneratedBy,
    [property: JsonPropertyName("evidence")] Evidence[] EvidenceList,
    [property: JsonPropertyName("disclaimer")] string Disclaimer);

public record ChildCreated(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("child_token")] string ChildToken,
    [property: JsonPropertyName("oversight")] string Oversight,
    [property: JsonPropertyName("sensitivity")] string? Sensitivity);

public record ChildSummary(
    [property: JsonPropertyName("child_id")] string ChildId,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("age")] int Age,
    [property: JsonPropertyName("oversight")] string Oversight);

public record ChildEvent(
    [property: JsonPropertyName("type")] string Type,
    [property: JsonPropertyName("condition")] string? Condition,
    [property: JsonPropertyName("severity")] string? Severity);

public record FamilyControlsState(
    [property: JsonPropertyName("paused")] bool Paused,
    [property: JsonPropertyName("quiet_start")] string? QuietStart,
    [property: JsonPropertyName("quiet_end")] string? QuietEnd,
    [property: JsonPropertyName("note")] string? Note);

public record GuardianChild(
    [property: JsonPropertyName("child_id")] string ChildId,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("light")] string Light,
    [property: JsonPropertyName("critical_24h")] int? Critical24h,
    [property: JsonPropertyName("escalations_24h")] int? Escalations24h,
    [property: JsonPropertyName("paused")] bool? Paused,
    [property: JsonPropertyName("quiet_hours")] string? QuietHours);

public record GuardianFace(
    [property: JsonPropertyName("children")] GuardianChild[] Children,
    [property: JsonPropertyName("haptic")] string? Haptic);

public record ChildOverview(
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("oversight")] string Oversight,
    [property: JsonPropertyName("critical_events")] int? CriticalEvents,
    [property: JsonPropertyName("events")] ChildEvent[]? Events,
    [property: JsonPropertyName("privacy_note")] string? PrivacyNote,
    [property: JsonPropertyName("note")] string? Note);

public record Custody(
    [property: JsonPropertyName("vaulted")] bool Vaulted,
    [property: JsonPropertyName("pdi_key")] string? PdiKey,
    [property: JsonPropertyName("note")] string? Note);

public record CustodyList(
    [property: JsonPropertyName("records")] string[] Records,
    [property: JsonPropertyName("count")] int Count,
    [property: JsonPropertyName("chain_intact")] bool? ChainIntact);

public record CustodySealed(
    [property: JsonPropertyName("cipher")] string? Cipher,
    [property: JsonPropertyName("created_at")] string? CreatedAt);

public record CustodyAudit([property: JsonPropertyName("count")] int Count);

public record CustodyChain([property: JsonPropertyName("intact")] bool? Intact);

public record CustodyProvenance(
    [property: JsonPropertyName("key")] string Key,
    [property: JsonPropertyName("origin")] string Origin,
    [property: JsonPropertyName("sealed")] CustodySealed? Sealed,
    [property: JsonPropertyName("audit")] CustodyAudit? Audit,
    [property: JsonPropertyName("chain")] CustodyChain? Chain);

public record Guidance(
    [property: JsonPropertyName("delivered")] bool Delivered,
    [property: JsonPropertyName("source")] string? Source,
    [property: JsonPropertyName("content")] string Content,
    [property: JsonPropertyName("references")] string[]? References,
    [property: JsonPropertyName("first_aid")] FirstAid? FirstAidPlaybook,
    [property: JsonPropertyName("provenance")] Provenance? ProvenanceInfo,
    [property: JsonPropertyName("translation_note")] string? TranslationNote,
    [property: JsonPropertyName("specialist")] string? Specialist,
    // The *offer*, distinct from the line above: `specialist` is a name
    // the monitoring path fills in; this is whether one may be asked.
    [property: JsonPropertyName("specialist_offer")] SpecialistOffer? SpecialistOffer,
    [property: JsonPropertyName("qrme_profile_id")] string? QrmeProfileId,
    [property: JsonPropertyName("custody")] Custody? CustodyInfo);

public record LanguageInfo(
    [property: JsonPropertyName("code")] string Code,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("safety_content_translated")] bool SafetyTranslated);

public record LanguagesList(
    [property: JsonPropertyName("languages")] LanguageInfo[] Languages,
    [property: JsonPropertyName("default")] string Default);

public record LanguageChoice(
    [property: JsonPropertyName("language")] string Language,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("mode")] string? Mode);

public record TranslateResult(
    [property: JsonPropertyName("text")] string Text,
    [property: JsonPropertyName("translation")] string Translation,
    [property: JsonPropertyName("language")] string Language,
    [property: JsonPropertyName("engine")] string Engine,
    [property: JsonPropertyName("note")] string? Note);

public record MonitorResult(
    [property: JsonPropertyName("detected")] bool Detected,
    [property: JsonPropertyName("condition")] string? Condition,
    [property: JsonPropertyName("severity")] string? Severity,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("guidance")] Guidance? Guidance);

public record CheckinGuardian(
    [property: JsonPropertyName("guidance")] Guidance? Guidance);

public record CheckinResult(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("guardian")] CheckinGuardian Guardian);

public record BaselineMetric(
    [property: JsonPropertyName("metric")] string Metric,
    [property: JsonPropertyName("value")] double? Value,
    [property: JsonPropertyName("state")] string? State,
    [property: JsonPropertyName("samples")] int? Samples);

public record Goal(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("area")] string Area,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("target")] string? Target,
    [property: JsonPropertyName("status")] string? Status);

// The user's own QRME profile, as this shell reads it. The preview is shown
// as the message itself, so `Brief` stays a raw element rather than a model
// that could quietly drop a category the server decided to send.
public record SelfProfileStatus(
    bool Linked,
    string? ProfileId,
    string[] Consented);

public record SelfProfilePreview(
    bool Linked,
    string[]? Consented,
    bool? Empty);

public record Habit(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("streak")] int? Streak);

public record JournalItem(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("text")] string? Text,
    [property: JsonPropertyName("created_at")] string? CreatedAt);

public record ProviderInfo(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("configured")] bool Configured);

public record ModelsList(
    [property: JsonPropertyName("providers")] ProviderInfo[] Providers,
    [property: JsonPropertyName("default")] string Default);

public record ModelChoice(
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("effective")] string Effective);

/// <summary>An open alarm, raised when somebody scanned a care code on a door.
///
/// <para><c>AcceptedBy</c> is the point of the record. Accepting and clearing
/// are separate acts and the backend keeps them apart deliberately — accepting
/// says somebody is coming, clearing says it is over. An accepted alarm is
/// still <c>open</c>, and this shell shows it that way: conflating them is how
/// an alarm gets marked handled by the act of being seen.</para></summary>
public record AlarmRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("beacon_id")] string? BeaconId,
    [property: JsonPropertyName("messages")] string[]? Messages,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("tier")] string? Tier,
    [property: JsonPropertyName("accepted_by")] string? AcceptedBy,
    [property: JsonPropertyName("created_at")] string? CreatedAt);

public record AlarmAck(
    [property: JsonPropertyName("alarm")] string? Alarm,
    [property: JsonPropertyName("accepted_by")] string? AcceptedBy,
    [property: JsonPropertyName("state")] string? State,
    [property: JsonPropertyName("note")] string? Note);

public record AlarmGuidance(
    [property: JsonPropertyName("answer")] string Answer,
    [property: JsonPropertyName("note")] string? Note);

public record CrashWatchStatus(
    [property: JsonPropertyName("armed")] bool Armed,
    [property: JsonPropertyName("trusted_name")] string? TrustedName,
    [property: JsonPropertyName("attempts")] int? Attempts,
    [property: JsonPropertyName("window_minutes")] double? WindowMinutes,
    [property: JsonPropertyName("contact_emergency_services")] bool? ContactEms,
    [property: JsonPropertyName("asking")] bool? Asking,
    [property: JsonPropertyName("attempt")] int? Attempt,
    [property: JsonPropertyName("concern")] string? Concern,
    [property: JsonPropertyName("tripped")] bool? Tripped);

public record EscalationPolicy(
    [property: JsonPropertyName("sensitivity")] string Sensitivity,
    [property: JsonPropertyName("ladder")] string[] Ladder,
    [property: JsonPropertyName("by_severity")] System.Collections.Generic.Dictionary<string, string> BySeverity);

public record FlowStep(
    [property: JsonPropertyName("step")] string Step,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("detail")] string Detail);

public record RobotDirective(
    [property: JsonPropertyName("robot")] string RobotName,
    [property: JsonPropertyName("directive")] string Directive);

public record EmergencyResult(
    [property: JsonPropertyName("emergency")] bool Emergency,
    [property: JsonPropertyName("flow")] FlowStep[] Flow,
    [property: JsonPropertyName("robot_directives")] RobotDirective[]? RobotDirectives);

public record RobotSpec(
    [property: JsonPropertyName("model")] string Model,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("maker")] string Maker,
    [property: JsonPropertyName("first_aid")] string? FirstAidRating);

public record RoboticsCatalog(
    [property: JsonPropertyName("robots")] RobotSpec[] Robots);

public record Robot(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("model")] string Model,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("escalation_directive")] string? EscalationDirective,
    [property: JsonPropertyName("first_aid")] string? FirstAidRating,
    [property: JsonPropertyName("commands")] string[]? Commands);

public record RobotCmdResult(
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("instruction")] string? Instruction,
    [property: JsonPropertyName("spoken")] string[]? Spoken,
    [property: JsonPropertyName("sequence")] string[]? Sequence,
    [property: JsonPropertyName("pace")] Pace? Pace);

public record WaiverState(
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("terms")] string[] Terms,
    [property: JsonPropertyName("signed")] bool Signed,
    [property: JsonPropertyName("signature")] string? Signature,
    [property: JsonPropertyName("signed_at")] string? SignedAt);

public record MedicalCardIssued(
    [property: JsonPropertyName("token")] string Token,
    [property: JsonPropertyName("qr_svg_url")] string QrSvgUrl);

public record SourceRow(
    [property: JsonPropertyName("source")] string Source,
    [property: JsonPropertyName("consented")] bool Consented);

public record SocialConn(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("platform")] string Platform,
    [property: JsonPropertyName("direction")] string Direction,
    [property: JsonPropertyName("handle")] string? Handle);

public record CatalogApp(
    [property: JsonPropertyName("app")] string App,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("capabilities")] string[] Capabilities);

public record CatalogProvider(
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("apps")] CatalogApp[] Apps);

public record AppsCatalog(
    [property: JsonPropertyName("providers")] CatalogProvider[] Providers);

public record AppConn(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("app")] string App);

public record MedicalContact(
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("phone")] string? Phone);

public record MedicalCard(
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("age")] int? Age,
    [property: JsonPropertyName("known_conditions")] string[]? KnownConditions,
    [property: JsonPropertyName("resting_heart_rate")] int? RestingHeartRate,
    [property: JsonPropertyName("emergency_contact")] MedicalContact? EmergencyContact);

public record ImproveItem(
    [property: JsonPropertyName("category")] string Category,
    [property: JsonPropertyName("message")] string Message,
    [property: JsonPropertyName("status")] string Status);

public record ImproveState(
    [property: JsonPropertyName("mine")] ImproveItem[] Mine,
    [property: JsonPropertyName("tally")] System.Collections.Generic.Dictionary<string, int> Tally,
    [property: JsonPropertyName("total")] int Total);

/// <summary>
/// Async client for the JIM Guardian backend. Windows reaches the local dev
/// server directly on 127.0.0.1.
/// </summary>
// MARK: the effectiveness loop, the user-specific model, and the name

/// Spec [0039]: guidance that went out gets asked about.
public record OpenFollowup(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("condition")] string Condition,
    [property: JsonPropertyName("severity")] string? Severity,
    [property: JsonPropertyName("question")] string Question);

public record FollowupState(
    [property: JsonPropertyName("open")] OpenFollowup[] Open);

public record LiveOption(
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("channel")] string? Channel,
    [property: JsonPropertyName("note")] string? Note);

public record LiveAssistance(
    [property: JsonPropertyName("options")] LiveOption[] Options,
    [property: JsonPropertyName("contact_alerted")] bool ContactAlerted,
    [property: JsonPropertyName("note")] string? Note);

public record FollowupAnswered(
    [property: JsonPropertyName("answered")] bool Answered,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("helped")] bool? Helped,
    [property: JsonPropertyName("next")] string? Next,
    [property: JsonPropertyName("live_assistance")] LiveAssistance? Live);

public record HelpTally(
    [property: JsonPropertyName("helped")] int Helped,
    [property: JsonPropertyName("answered")] int Answered);

public record AdaptationDetail(
    [property: JsonPropertyName("what_helps")] Dictionary<string, HelpTally>? WhatHelps,
    [property: JsonPropertyName("tone")] string? Tone,
    [property: JsonPropertyName("occupation")] string? Occupation,
    [property: JsonPropertyName("method")] string? Method);

/// Claim 11's user-specific model, derived locally from this user's own stored
/// history — nothing was sent to a model vendor to build it.
public record AdaptationProfile(
    [property: JsonPropertyName("built")] bool Built,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("evidence_items")] int EvidenceItems,
    [property: JsonPropertyName("confidence")] double Confidence,
    [property: JsonPropertyName("vaulted")] bool Vaulted,
    [property: JsonPropertyName("profile")] AdaptationDetail? Profile);

/// What anonymity keeps and what it costs, said out loud.
public record AnonymityPosture(
    [property: JsonPropertyName("anonymous")] bool Anonymous,
    [property: JsonPropertyName("known_as")] string? KnownAs,
    [property: JsonPropertyName("legal_name_on_record")] bool LegalNameOnRecord,
    [property: JsonPropertyName("keeps")] string[] Keeps,
    [property: JsonPropertyName("costs")] string[] Costs);

// MARK: the community door (FIG. 2 boxes 222-226)

public record CommunityRoom(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("topic")] string? Topic,
    [property: JsonPropertyName("channel")] string? Channel,
    [property: JsonPropertyName("participants")] int Participants,
    [property: JsonPropertyName("url")] string? Url);

public record CommunityPlace(
    [property: JsonPropertyName("locality")] string Locality,
    [property: JsonPropertyName("region")] string? Region,
    [property: JsonPropertyName("listings")] int Listings);

// What JIM will and will not do with the community it points at, as data
// rather than prose, so a screen cannot claim more than the bridge does.
public record CommunityPosture(
    [property: JsonPropertyName("mirrored_here")] bool MirroredHere,
    [property: JsonPropertyName("posts_on_your_behalf")] bool PostsOnYourBehalf,
    [property: JsonPropertyName("health_data_shared")] bool HealthDataShared);

public record CommunityView(
    [property: JsonPropertyName("qrme_url")] string? QrmeUrl,
    [property: JsonPropertyName("language")] string? Language,
    [property: JsonPropertyName("rooms")] CommunityRoom[] Rooms,
    [property: JsonPropertyName("places")] CommunityPlace[] Places,
    [property: JsonPropertyName("note")] string Note,
    [property: JsonPropertyName("posture")] CommunityPosture Posture);

public sealed class ApiClient
{
    public static ApiClient Shared { get; } = new();

    private readonly HttpClient _http = new() { BaseAddress = new Uri("http://127.0.0.1:8000") };

    public void SetBase(string url) => _http.BaseAddress = new Uri(url.TrimEnd('/'));


    /// <summary>What the deployment can and cannot reach. Read-only: the
    /// posture is set in the deployment's environment, not in the app.</summary>
    /// What the Guardian carries across sessions about this person. Counts
    /// and timings only — the vector is derived from tallies and holds
    /// nothing anybody wrote.
    public async Task<ContinuityState> Continuity(string uid, string token) =>
        await Send<ContinuityState>(new HttpRequestMessage(HttpMethod.Get,
            _base + $"/continuity/{uid}"), token);

    /// Drop it. Every derived thing here has to be droppable by the person it
    /// was derived from.
    public async Task<Forgotten> ForgetContinuity(string uid, string token) =>
        await Send<Forgotten>(new HttpRequestMessage(HttpMethod.Delete,
            _base + $"/continuity/{uid}"), token);

    public async Task<OfflinePosture> OfflineStatus() =>
        await Send<OfflinePosture>(new HttpRequestMessage(HttpMethod.Get,
            _base + "/offline/status"));

    private async Task<T> Send<T>(HttpRequestMessage req)
    {
        // The path as written, for the recorder. Read before the send, which
        // consumes `req`. Absolute and relative are both handled: these calls
        // build relative URIs against BaseAddress, but a `RequestUri` that
        // ever arrived absolute would otherwise put the host in the log —
        // not private, but not the operation either.
        var method = req.Method.Method;
        var path = req.RequestUri is { IsAbsoluteUri: true } abs
            ? abs.AbsolutePath
            : req.RequestUri?.ToString() ?? "";

        HttpResponseMessage res;
        try
        {
            res = await _http.SendAsync(req);
        }
        catch
        {
            // Never reached a server. Recorded as status 0; the thrown error
            // still carries its message to the person, who owns it.
            Problems.Record(method, path, 0);
            throw;
        }
        var body = await res.Content.ReadAsStringAsync();
        if (!res.IsSuccessStatusCode)
        {
            // The status and the operation, never the detail below: these
            // messages quote what the person typed, which is theirs to read
            // and nobody's to keep.
            Problems.Record(method, path, (int)res.StatusCode);
            // GetString() throws on an array, which a 422's `detail` is, so the
            // catch swallowed it and the person saw the status code. `message`
            // is the sentence the backend composes beside the rows.
            string? said = null;
            try
            {
                var root = JsonDocument.Parse(body).RootElement;
                if (root.TryGetProperty("message", out var m) && m.ValueKind == JsonValueKind.String)
                    said = m.GetString();
                else if (root.TryGetProperty("detail", out var d) && d.ValueKind == JsonValueKind.String)
                    said = d.GetString();
            }
            catch { /* non-JSON error body */ }
            throw new HttpRequestException(said ?? $"HTTP {(int)res.StatusCode}");
        }
        return JsonSerializer.Deserialize<T>(body)!;
    }

    private static HttpRequestMessage Put(string path, object body, string? token = null)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, path) { Content = JsonContent.Create(body) };
        if (token is not null) req.Headers.Add("authorization", $"Bearer {token}");
        return req;
    }

    private static HttpRequestMessage Post(string path, object body, string? token = null)
    {
        var req = new HttpRequestMessage(HttpMethod.Post, path) { Content = JsonContent.Create(body) };
        if (token is not null) req.Headers.Add("authorization", $"Bearer {token}");
        return req;
    }

    public Task<EnrollResult> Enroll(string name, string birthdate,
                                     string? language = null) =>
        Send<EnrollResult>(Post("/enroll",
            language is { Length: > 0 } && language != "en"
                ? new { display_name = name, birthdate, terms_consent = true,
                        language }
                : (object)new { display_name = name, birthdate,
                                terms_consent = true }));

    public Task<MonitorResult> Monitor(string uid, string token, int heartRate, double stress) =>
        Send<MonitorResult>(Post($"/monitor/{uid}",
            new { heart_rate = heartRate, stress_level = stress }, token));

    public Task<CheckinResult> Checkin(string uid, string token, int mood, int energy, string note) =>
        Send<CheckinResult>(Post($"/checkin/{uid}",
            new { mood, energy, note }, token));

    /// Send this question to the QRME specialist covering the area.
    /// `Coach` only offers; this is the door the person chooses.
    public Task<SpecialistAnswer> CoachSpecialist(string uid, string token,
                                                  string area, string message) =>
        Send<SpecialistAnswer>(Post($"/coach/{uid}/specialist",
            new { area, message }, token));

    public Task<Guidance> Coach(string uid, string token, string area, string message) =>
        Send<Guidance>(Post($"/coach/{uid}", new { area, message }, token));

    public async Task<BaselineMetric[]> Baseline(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/baseline/{uid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return await Send<BaselineMetric[]>(req);
    }

    // -- life: goals, habits, journal --

    private HttpRequestMessage Get(string path, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, path);
        req.Headers.Add("authorization", $"Bearer {token}");
        return req;
    }

    // -- family: a parent sets up and watches over a child's account --

    public Task<ChildCreated> EnrollChild(string gid, string token, string name,
                                          string birthdate, string? phone) =>
        Send<ChildCreated>(Post($"/guardians/{gid}/children",
            phone is { Length: > 0 }
                ? new { display_name = name, birthdate, guardian_phone = phone }
                : (object)new { display_name = name, birthdate }, token));

    public Task<ChildSummary[]> Children(string gid, string token) =>
        Send<ChildSummary[]>(Get($"/guardians/{gid}/children", token));

    public Task<ChildOverview> ChildOverviewOf(string gid, string cid, string token) =>
        Send<ChildOverview>(Get($"/guardians/{gid}/children/{cid}", token));

    public Task<FamilyControlsState> SetFamilyControls(
        string gid, string cid, string token, bool? paused,
        string? quietStart, string? quietEnd)
    {
        var body = new System.Collections.Generic.Dictionary<string, object>();
        if (paused is { } p) body["paused"] = p;
        if (quietStart is { Length: > 0 }) body["quiet_start"] = quietStart;
        if (quietEnd is { Length: > 0 }) body["quiet_end"] = quietEnd;
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/guardians/{gid}/children/{cid}/controls")
        { Content = System.Net.Http.Json.JsonContent.Create(body) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<FamilyControlsState>(req);
    }

    public Task<GuardianFace> GuardianWatch(string gid, string token) =>
        Send<GuardianFace>(Get($"/guardians/{gid}/watch", token));

    // -- vault custody: sealed tandem exchanges --

    public Task<CustodyList> Custody(string uid, string token) =>
        Send<CustodyList>(Get($"/custody/{uid}", token));

    public Task<CustodyProvenance> CustodyProvenance(string uid, string token, string key) =>
        Send<CustodyProvenance>(Get(
            $"/custody/{uid}/provenance?key={Uri.EscapeDataString(key)}", token));

    public Task<Goal[]> Goals(string uid, string token) => Send<Goal[]>(Get($"/goals/{uid}", token));

    public Task<Goal> AddGoal(string uid, string token, string area, string title, string? target) =>
        Send<Goal>(Post($"/goals/{uid}",
            target is { Length: > 0 } ? new { area, title, target } : (object)new { area, title }, token));

    // -- the one QRME profile that is this person -----------------------------
    //
    // Every other QRME call in this shell reaches somebody else's profile.
    // These reach their own — see docs/tandem.md, and jim/synthetic_self.py for
    // the boundary. Seeing and revoking what a profile has been told belongs on
    // the phone at least as much as on the desktop.

    public Task<SelfProfileStatus> SelfProfile(string uid, string token) =>
        Send<SelfProfileStatus>(Get($"/self-profile/{uid}", token));

    public Task<SelfProfileStatus> LinkSelfProfile(string uid, string token,
                                                   string profileId, string ownerToken) =>
        Send<SelfProfileStatus>(Post($"/self-profile/{uid}",
            new { profile_id = profileId, owner_token = ownerToken }, token));

    public async Task UnlinkSelfProfile(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, $"/self-profile/{uid}");
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<SelfProfileStatus> ConsentSelfProfile(string uid, string token,
                                                      string[] categories) =>
        Send<SelfProfileStatus>(Put($"/self-profile/{uid}/consent",
            new { categories }, token));

    /// <summary>Exactly what would be sent, built by the code that sends it.</summary>
    public Task<SelfProfilePreview> PreviewSelfProfile(string uid, string token) =>
        Send<SelfProfilePreview>(Get($"/self-profile/{uid}/preview", token));

    public async Task BriefSelfProfile(string uid, string token)
    {
        var req = Post($"/self-profile/{uid}/brief", new { }, token);
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<Habit[]> Habits(string uid, string token) => Send<Habit[]>(Get($"/habits/{uid}", token));

    public Task<Habit> AddHabit(string uid, string token, string name) =>
        Send<Habit>(Post($"/habits/{uid}", new { name }, token));

    public async Task LogHabit(string uid, string token, string habitId)
    {
        var req = Post($"/habits/{uid}/{habitId}/log", new { }, token);
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<JournalItem[]> Journal(string uid, string token) => Send<JournalItem[]>(Get($"/journal/{uid}", token));

    public async Task AddJournal(string uid, string token, string text)
    {
        var req = Post($"/journal/{uid}", new { text }, token);
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    // -- model selection --

    public Task<ModelsList> Models() =>
        Send<ModelsList>(new HttpRequestMessage(HttpMethod.Get, "/models"));

    public Task<ModelChoice> UserModel(string uid, string token) =>
        Send<ModelChoice>(Get($"/model/{uid}", token));

    public Task<ModelChoice> SetModel(string uid, string token, string provider)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, $"/model/{uid}")
        {
            Content = JsonContent.Create(new { provider }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ModelChoice>(req);
    }

    // -- language --

    public Task<LanguagesList> Languages() =>
        Send<LanguagesList>(new HttpRequestMessage(HttpMethod.Get, "/languages"));

    public Task<LanguageChoice> UserLanguage(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/language/{uid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LanguageChoice>(req);
    }

    public Task<LanguageChoice> SetLanguage(string uid, string token, string code,
                                            string mode = "pre")
    {
        var req = new HttpRequestMessage(HttpMethod.Put, $"/language/{uid}")
        {
            Content = JsonContent.Create(new { language = code, mode }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LanguageChoice>(req);
    }

    public Task<TranslateResult> Translate(string uid, string token, string text) =>
        Send<TranslateResult>(Post($"/translate/{uid}", new { text }, token));

    // -- safety: escalation policy, Emergency, robots --

    // The alarms. Routes this shell could not reach at all until 0.23.0 —
    // there was no occurrence of the word "alarm" anywhere in it. A responder
    // is paged on their phone and, holding it, had no way to answer; accepting
    // is what stops the ladder climbing to emergency services.
    public Task<AlarmRow[]> Alarms(string uid, string token) =>
        Send<AlarmRow[]>(Get($"/users/{uid}/alarms", token));

    /// <summary>The responder must be named. The backend refuses an empty one,
    /// because "someone accepted it" is the thing this relay exists to stop
    /// being enough.</summary>
    public Task<AlarmAck> AcceptAlarm(string uid, string alarmId,
                                      string responder, string token) =>
        Send<AlarmAck>(Post($"/users/{uid}/alarms/{alarmId}/accept",
            new { responder }, token));

    public Task<AlarmAck> ClearAlarm(string uid, string alarmId, string token) =>
        Send<AlarmAck>(Post($"/users/{uid}/alarms/{alarmId}/clear",
            new { }, token));

    public Task<AlarmAck> EscalateAlarm(string uid, string alarmId, string token) =>
        Send<AlarmAck>(Post($"/users/{uid}/alarms/{alarmId}/escalate",
            new { }, token));

    /// <summary>Answers even with no specialist reachable — the standing
    /// instruction is the one that is always right and never depends on a
    /// model being up.</summary>
    public Task<AlarmGuidance> AlarmGuidance(string alarmId, string question,
                                             string token) =>
        Send<AlarmGuidance>(Post($"/alarms/{alarmId}/guidance",
            new { question }, token));

    // The crash watch: armed in advance, off by default. The status read is
    // also the clock — polling is what re-asks the question.
    public Task<CrashWatchStatus> CrashWatch(string uid, string token) =>
        Send<CrashWatchStatus>(Get($"/crash-watch/{uid}", token));

    public Task<CrashWatchStatus> ArmCrashWatch(
        string uid, string token, string name, string channel,
        int attempts, double windowMinutes, bool ems) =>
        Send<CrashWatchStatus>(Put($"/crash-watch/{uid}", new
        {
            trusted_name = name,
            trusted_channel = channel,
            attempts,
            window_minutes = windowMinutes,
            contact_emergency_services = ems,
        }, token));

    public Task<CrashWatchStatus> DisarmCrashWatch(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, $"/crash-watch/{uid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<CrashWatchStatus>(req);
    }

    public Task<CrashWatchStatus> ImOkay(string uid, string token) =>
        Send<CrashWatchStatus>(Post($"/crash-watch/{uid}/respond",
            new { }, token));

    public Task<EscalationPolicy> EscalationPolicy(string uid, string token) =>
        Send<EscalationPolicy>(Get($"/escalation-policy/{uid}", token));

    public async Task SetSensitivity(string uid, string token, string level)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, $"/sensitivity/{uid}")
        {
            Content = JsonContent.Create(new { level }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<EmergencyResult> Emergency(string uid, string token,
                                           string? situation, string? location) =>
        Send<EmergencyResult>(Post($"/emergency/{uid}",
            new { situation, location }, token));

    public Task<RoboticsCatalog> Robotics() =>
        Send<RoboticsCatalog>(new HttpRequestMessage(HttpMethod.Get, "/robotics/catalog"));

    public Task<Robot[]> Robots(string uid, string token) =>
        Send<Robot[]>(Get($"/robots/{uid}", token));

    public Task<Robot> BindRobot(string uid, string token, string model) =>
        Send<Robot>(Post($"/robots/{uid}", new { model }, token));

    public Task<RobotCmdResult> CommandRobot(string uid, string token, string robotId,
                                             string command, string? arg) =>
        Send<RobotCmdResult>(Post($"/robots/{uid}/{robotId}/command",
            arg is { Length: > 0 } ? new { command, arg } : (object)new { command },
            token));

    public Task<WaiverState> Waiver(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/waivers/{uid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<WaiverState>(req);
    }

    public async Task SignWaiver(string uid, string token, string signature)
    {
        var req = Post($"/waivers/{uid}", new { signature, accept = true }, token);
        var res = await _http.SendAsync(req);
        if (!res.IsSuccessStatusCode)
        {
            var body = await res.Content.ReadAsStringAsync();
            // GetString() throws on an array, which a 422's `detail` is, so the
            // catch swallowed it and the person saw the status code. `message`
            // is the sentence the backend composes beside the rows.
            string? said = null;
            try
            {
                var root = JsonDocument.Parse(body).RootElement;
                if (root.TryGetProperty("message", out var m) && m.ValueKind == JsonValueKind.String)
                    said = m.GetString();
                else if (root.TryGetProperty("detail", out var d) && d.ValueKind == JsonValueKind.String)
                    said = d.GetString();
            }
            catch { /* non-JSON error body */ }
            throw new HttpRequestException(said ?? $"HTTP {(int)res.StatusCode}");
        }
    }

    public async Task RevokeWaiver(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, $"/waivers/{uid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    // -- Connect: sources, social platforms, connected apps --

    public Task<SourceRow[]> Sources(string uid, string token) =>
        Send<SourceRow[]>(Get($"/sources/{uid}", token));

    public async Task SetSource(string uid, string token, string source, bool consented)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, $"/sources/{uid}")
        {
            Content = JsonContent.Create(new { source, consented }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<SocialConn[]> SocialConnections(string uid, string token) =>
        Send<SocialConn[]>(Get($"/social/{uid}", token));

    public Task<SocialConn> SocialConnect(string uid, string token, string platform,
                                          string direction, string handle) =>
        Send<SocialConn>(Post($"/social/{uid}",
            handle is { Length: > 0 }
                ? new { platform, direction, handle }
                : (object)new { platform, direction }, token));

    public async Task SocialCollect(string cid, string token, string content)
    {
        var req = Post($"/social/connection/{cid}/collect",
            new { items = new[] { new { content } } }, token);
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task SocialPublish(string cid, string token, string content)
    {
        var req = Post($"/social/connection/{cid}/publish", new { content }, token);
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<AppsCatalog> ConnectorCatalog() =>
        Send<AppsCatalog>(new HttpRequestMessage(HttpMethod.Get, "/connectors/catalog"));

    public Task<AppConn[]> AppConnections(string uid, string token) =>
        Send<AppConn[]>(Get($"/apps/{uid}", token));

    public Task<AppConn> AppConnect(string uid, string token, string provider, string app) =>
        Send<AppConn>(Post($"/apps/{uid}", new { provider, app }, token));

    public async Task AppCollect(string cid, string token, string content)
    {
        var req = Post($"/apps/connector/{cid}/collect",
            new { items = new[] { new { content } } }, token);
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    // -- Medical ID (first-responder card + QR) --

    public Task<MedicalCardIssued> IssueMedicalCard(string uid, string token) =>
        Send<MedicalCardIssued>(Post($"/medical-id/qr/{uid}", new { }, token));

    public Task<MedicalCard> MedicalCardView(string cardToken) =>
        Send<MedicalCard>(new HttpRequestMessage(
            HttpMethod.Get, $"/medical-id/{cardToken}"));   // public: the card is the credential

    public async Task RevokeMedicalCard(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, $"/medical-id/qr/{uid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    // -- Help us improve — product feedback (open to anyone) --

    public async Task SubmitImprovement(string? token, string category,
                                        string message, int? rating)
    {
        object body = rating is { } r
            ? new { category, message, rating = r }
            : new { category, message };
        var res = await _http.SendAsync(Post("/improve", body, token));
        res.EnsureSuccessStatusCode();
    }

    public Task<ImproveState> Improvements(string? token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, "/improve");
        if (token is { Length: > 0 }) req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ImproveState>(req);
    }

    // MARK: Community — the door into QRME, and the visit note

    /// <summary>
    /// Rooms and places as QRME serves them, plus the language JIM knows this
    /// user reads. JIM never mirrors the conversation; the posture in the reply
    /// says so, and the page renders those booleans rather than restating them.
    /// </summary>
    public Task<CommunityView> Community(string uid, string token) =>
        Send<CommunityView>(Get($"/community/{uid}", token));

    /// <summary>Record that a door was opened — the visit, and nothing from
    /// inside it.</summary>
    public async Task NoteCommunityVisit(string uid, string token, string roomId)
    {
        var res = await _http.SendAsync(
            Post($"/community/{uid}/visits", new { room_id = roomId }, token));
        res.EnsureSuccessStatusCode();
    }


    // MARK: Followup, adaptation and anonymity

    public Task<FollowupState> Followups(string uid, string token) =>
        Send<FollowupState>(Get($"/followup/{uid}", token));

    /// <summary>
    /// helped=false is not a complaint filed away: it re-runs the escalation
    /// ladder with the ineffective-guidance rung and returns the people who can
    /// help right now.
    /// </summary>
    public Task<FollowupAnswered> AnswerFollowup(string uid, string token,
                                                 bool helped, string? note) =>
        Send<FollowupAnswered>(Post($"/followup/{uid}",
            string.IsNullOrWhiteSpace(note)
                ? new { helped } : new { helped, note }, token));

    public Task<AdaptationProfile> Adaptation(string uid, string token) =>
        Send<AdaptationProfile>(Get($"/adaptation/{uid}", token));

    /// <summary>Rebuild from the history already on record — local work only.</summary>
    public Task<AdaptationProfile> RebuildAdaptation(string uid, string token) =>
        Send<AdaptationProfile>(Post($"/adaptation/{uid}", new { }, token));

    public Task<AnonymityPosture> Anonymity(string uid, string token) =>
        Send<AnonymityPosture>(Get($"/anonymity/{uid}", token));

}

public record OfflinePosture(
    [property: JsonPropertyName("offline")] bool Offline,
    [property: JsonPropertyName("external_transmission_possible")] bool ExternalTransmissionPossible,
    [property: JsonPropertyName("local_destinations_allowed")] string LocalDestinationsAllowed,
    [property: JsonPropertyName("guarantees")] string[] Guarantees);

public record ContinuityState(
    [property: JsonPropertyName("built")] bool Built,
    [property: JsonPropertyName("carries")] string Carries,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("observations")] int Observations,
    [property: JsonPropertyName("conditioning")] bool Conditioning,
    [property: JsonPropertyName("vector")] Dictionary<string, double>? Vector,
    [property: JsonPropertyName("meanings")] Dictionary<string, string>? Meanings,
    [property: JsonPropertyName("method")] string? Method);

public record Forgotten(
    [property: JsonPropertyName("forgotten")] bool Value);

public record SpecialistOffer(
    [property: JsonPropertyName("available")] bool Available,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("qrme_profile_id")] string QrmeProfileId,
    [property: JsonPropertyName("sent")] bool Sent,
    [property: JsonPropertyName("note")] string Note);

public record SpecialistWho(
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("qrme_profile_id")] string QrmeProfileId);

public record SpecialistProvenance(
    [property: JsonPropertyName("method")] string Method,
    [property: JsonPropertyName("shared")] string Shared);

public record SpecialistAnswer(
    [property: JsonPropertyName("delivered")] bool Delivered,
    [property: JsonPropertyName("content")] string? Content,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("held_for_owner_approval")] bool HeldForOwnerApproval,
    [property: JsonPropertyName("specialist")] SpecialistWho? Specialist,
    [property: JsonPropertyName("provenance")] SpecialistProvenance? Provenance);
