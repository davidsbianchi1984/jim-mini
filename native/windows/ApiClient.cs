using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
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
    [property: JsonPropertyName("pace_cue")] PaceCue? Cue);

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

// --- engaged sessions (jim/engaged.py) -------------------------------------
//
// `Coach` is a turn. These are a session: open until sign-off, able to act on
// this person's own records while it is open, and every act landing on a trail
// with the request that would take it back.
//
// `Reversible` and `IrreversibleBecause` are carried separately rather than
// derived from one another. An act that acted and can no longer be taken back
// is a real third state — already undone, or one whose way back the backend
// could not build — and a screen rendering `!Reversible` as "irreversible"
// would tell somebody their journal entry had left the app.
public record EngagedTool(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("says")] string Says,
    [property: JsonPropertyName("acts")] bool Acts,
    [property: JsonPropertyName("reversible")] bool Reversible,
    [property: JsonPropertyName("irreversible_because")] string? IrreversibleBecause);

public record EngagedReach(
    [property: JsonPropertyName("can")] EngagedTool[] Can,
    [property: JsonPropertyName("tools_per_turn")] int ToolsPerTurn,
    [property: JsonPropertyName("acts_per_session")] int ActsPerSession,
    [property: JsonPropertyName("watch_ceiling")] int WatchCeiling);

// One group of switches an engaged session may throw (jim/permits.py).
//
// Says arrives as a sentence rather than a label, because a toggle beside the
// words "what it may read" tells nobody what they are agreeing to. DecidedAt
// being null means never decided — a third state beside on and off, and the
// one that makes "I never agreed to that" answerable.
public record EngagedPermitArea(
    [property: JsonPropertyName("area")] string Area,
    [property: JsonPropertyName("says")] string Says,
    [property: JsonPropertyName("standing")] string Standing,
    [property: JsonPropertyName("granted")] bool Granted,
    [property: JsonPropertyName("decided_at")] string? DecidedAt,
    [property: JsonPropertyName("tools")] string[] Tools);

public record EngagedPermits(
    [property: JsonPropertyName("groups")] EngagedPermitArea[] Groups,
    [property: JsonPropertyName("note")] string Note,
    [property: JsonPropertyName("can")] EngagedTool[] Can);

public record EngagedStep(
    [property: JsonPropertyName("tool")] string? Tool,
    [property: JsonPropertyName("status_code")] int? StatusCode,
    [property: JsonPropertyName("says")] string? Says,
    [property: JsonPropertyName("acts")] bool Acts,
    [property: JsonPropertyName("reversible")] bool Reversible,
    [property: JsonPropertyName("irreversible_because")] string? IrreversibleBecause,
    [property: JsonPropertyName("refused")] string? Refused);

public record EngagedAct(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("tool")] string Tool,
    [property: JsonPropertyName("says")] string Says,
    [property: JsonPropertyName("status_code")] int StatusCode,
    [property: JsonPropertyName("created_at")] string CreatedAt,
    [property: JsonPropertyName("undone_at")] string? UndoneAt,
    [property: JsonPropertyName("reversible")] bool Reversible,
    [property: JsonPropertyName("irreversible_because")] string? IrreversibleBecause);

public record StandingWatch(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("topic")] string Topic,
    [property: JsonPropertyName("area")] string? Area,
    [property: JsonPropertyName("created_at")] string CreatedAt);

public record EngagedSessionTurn(
    [property: JsonPropertyName("role")] string Role,
    [property: JsonPropertyName("content")] string Content,
    [property: JsonPropertyName("created_at")] string CreatedAt);

public record EngagedSession(
    [property: JsonPropertyName("engaged")] bool Engaged,
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("area")] string? Area,
    [property: JsonPropertyName("turns")] EngagedSessionTurn[] Turns,
    [property: JsonPropertyName("acted")] EngagedAct[] Acted,
    [property: JsonPropertyName("watches")] StandingWatch[] Watches);

public record EngagedProvenance(
    [property: JsonPropertyName("generated_by")] string GeneratedBy,
    [property: JsonPropertyName("degraded")] bool Degraded,
    [property: JsonPropertyName("degraded_reason")] string? DegradedReason);

public record EngagedTurnResult(
    [property: JsonPropertyName("engagement_id")] string EngagementId,
    [property: JsonPropertyName("reply")] string Reply,
    // `did`, not `acted`: a session's `acted` is the trail of completed
    // changes, and a turn's list includes refusals, which are not acts. One
    // name may not carry two shapes on the wire.
    [property: JsonPropertyName("did")] EngagedStep[] Did,
    [property: JsonPropertyName("stopped")] string? Stopped,
    [property: JsonPropertyName("engaged")] bool Engaged,
    [property: JsonPropertyName("watches")] StandingWatch[] Watches,
    [property: JsonPropertyName("generation")] EngagedProvenance Provenance);

public record EngagedSignOff(
    [property: JsonPropertyName("engagement_id")] string EngagementId,
    [property: JsonPropertyName("signed_off")] bool SignedOff,
    [property: JsonPropertyName("deposited")] int Deposited,
    [property: JsonPropertyName("watches")] StandingWatch[] Watches);

public record EngagedUndone(
    [property: JsonPropertyName("act_id")] string ActId,
    [property: JsonPropertyName("undone")] bool Undone,
    [property: JsonPropertyName("tool")] string Tool,
    [property: JsonPropertyName("says")] string Says);

public record WatchCleared(
    [property: JsonPropertyName("watch_id")] string WatchId,
    [property: JsonPropertyName("cleared")] bool Cleared,
    [property: JsonPropertyName("topic")] string Topic);

/// The acknowledgement every `remove` door answers with. One shape rather than
/// five near-identical ones: what a caller reads is `removed`, and the id it
/// echoes back is already the id the caller sent.
public record Removed(
    [property: JsonPropertyName("removed")] bool Yes);

/// What a habit's day answers with, ticked or unticked. `streak` is recomputed
/// rather than adjusted — removing a day out of the middle does not shorten a
/// streak by one, it breaks it.
public record HabitLogged(
    [property: JsonPropertyName("habit_id")] string HabitId,
    [property: JsonPropertyName("day")] string Day,
    [property: JsonPropertyName("streak")] int Streak);

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

/// <summary>What a QRME sign-in answers with: either the link, or the
/// question.</summary>
/// <remarks><c>Linked</c> false with a <c>Choose</c> list means nothing has
/// happened yet — the account holds more than one profile of the person and
/// one has to be picked.</remarks>
public record SelfProfileCandidate(
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("shown_as")] string? ShownAs,
    [property: JsonPropertyName("kind")] string? Kind);

public record SelfProfileSignedIn(
    [property: JsonPropertyName("linked")] bool Linked,
    [property: JsonPropertyName("profile_id")] string? ProfileId,
    [property: JsonPropertyName("choose")] SelfProfileCandidate[]? Choose);

public record SelfProfilePreview(
    bool Linked,
    string[]? Consented,
    bool? Empty);

public record Habit(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("streak")] int? Streak);

public record Meal(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("logged")] string Logged,
    [property: JsonPropertyName("described_by")] string DescribedBy,
    [property: JsonPropertyName("photo_sealed")] bool PhotoSealed,
    [property: JsonPropertyName("created_at")] string? CreatedAt);

public record Drill(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("question")] string Question,
    [property: JsonPropertyName("probes")] string[]? Probes,
    [property: JsonPropertyName("critique")] string? Critique,
    [property: JsonPropertyName("described_by")] string? DescribedBy,
    [property: JsonPropertyName("answered_at")] string? AnsweredAt);

public record Letter(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("week_start")] string WeekStart,
    [property: JsonPropertyName("body")] string Body,
    [property: JsonPropertyName("described_by")] string DescribedBy,
    [property: JsonPropertyName("created_at")] string? CreatedAt);

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
    [property: JsonPropertyName("alert_texts")] string[]? AlertTexts,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("tier")] string? Tier,
    [property: JsonPropertyName("accepted_by")] string? AcceptedBy,
    [property: JsonPropertyName("created_at")] string? CreatedAt,
    // True on every row this queue holds, because JIM cannot place a call at
    // any tier: a beacon alarm is ceilinged below emergency services, and a
    // crash watch that reached the top rung issued a dispatch *request*.
    [property: JsonPropertyName("call_emergency_services_yourself")]
    bool? CallEmergencyServicesYourself = null,
    // Whether a safety floor was cut to reach this tier.
    [property: JsonPropertyName("clipped_by_ceiling")]
    bool? ClippedByCeiling = null);

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
    [property: JsonPropertyName("first_aid_rating")] string? FirstAidRating);

public record RoboticsCatalog(
    [property: JsonPropertyName("robots")] RobotSpec[] Robots);

public record Robot(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("model")] string Model,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("escalation_directive")] string? EscalationDirective,
    [property: JsonPropertyName("first_aid_rating")] string? FirstAidRating,
    [property: JsonPropertyName("commands")] string[]? Commands);

public record RobotCmdResult(
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("instruction")] string? Instruction,
    [property: JsonPropertyName("spoken_steps")] string[]? SpokenSteps,
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
    [property: JsonPropertyName("app_providers")] CatalogProvider[] Providers);

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

public record AccessReportRow(
    [property: JsonPropertyName("doing")] string Doing,
    [property: JsonPropertyName("wall")] string Wall,
    [property: JsonPropertyName("help")] string? Help,
    [property: JsonPropertyName("lang")] string Lang,
    [property: JsonPropertyName("created_at")] string CreatedAt);

public record AccessReportsState(
    [property: JsonPropertyName("reports")] AccessReportRow[] Reports,
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
    [property: JsonPropertyName("helped_count")] int HelpedCount,
    [property: JsonPropertyName("answered_count")] int AnsweredCount);

public record AdaptationDetail(
    [property: JsonPropertyName("what_helps")] Dictionary<string, HelpTally>? WhatHelps,
    [property: JsonPropertyName("tone")] string? Tone,
    [property: JsonPropertyName("occupation")] string? Occupation,
    [property: JsonPropertyName("method")] string? Method);

/// Claim 11's user-specific model, derived locally from this user's own stored
/// history — nothing was sent to a model vendor to build it.
public record Finetune(
    /// A rebuild count, not a semantic version — `/health` uses `version`
    /// for the latter and the two cannot share a wire name.
    [property: JsonPropertyName("build")] int Build,
    [property: JsonPropertyName("backend")] string Backend,
    [property: JsonPropertyName("examples")] int Examples,
    [property: JsonPropertyName("helped_count")] int HelpedCount,
    [property: JsonPropertyName("did_not_help")] int DidNotHelp,
    [property: JsonPropertyName("method")] string Method,
    [property: JsonPropertyName("digest")] string Digest,
    [property: JsonPropertyName("trained_at")] string TrainedAt,
    [property: JsonPropertyName("active")] bool? Active);

public record FinetuneSwitchResult(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("active")] bool Active,
    [property: JsonPropertyName("digest")] string Digest,
    [property: JsonPropertyName("backend")] string Backend);

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

/// <summary>What the presence says it is. <c>Boundaries</c> is the half that
/// matters: a boundary a screen cannot render is one nobody can be shown.
/// </summary>
public record PresenceWho(
    [property: JsonPropertyName("says")] string Says,
    [property: JsonPropertyName("note")] string Note,
    [property: JsonPropertyName("works_offline")] bool WorksOffline,
    [property: JsonPropertyName("hands_free")] bool HandsFree,
    [property: JsonPropertyName("boundaries")] Dictionary<string, PresenceBoundary>? Boundaries);

public record PresenceBoundary(
    [property: JsonPropertyName("stands")] bool Stands,
    [property: JsonPropertyName("says")] string Says);

/// <summary>One unprompted turn — or silence, which is an outcome rather
/// than an empty response. <c>Because</c> is why, and a presence that cannot
/// show its reason is one nobody can argue with.</summary>
public record PresenceBeat(
    [property: JsonPropertyName("slot")] string Slot,
    [property: JsonPropertyName("speak")] bool Speak,
    [property: JsonPropertyName("register")] string Register,
    [property: JsonPropertyName("english")] string English,
    [property: JsonPropertyName("deepened_line")] string? DeepenedLine,
    [property: JsonPropertyName("because")] string[]? Because);

public record PresenceDay(
    [property: JsonPropertyName("beats")] PresenceBeat[]? Beats,
    [property: JsonPropertyName("offline")] bool Offline);

public record PresenceArea(
    [property: JsonPropertyName("area")] string Area,
    [property: JsonPropertyName("standing")] string Standing);

public record PresenceBaseline(
    [property: JsonPropertyName("known_areas")] int KnownAreas,
    [property: JsonPropertyName("of")] int Of,
    [property: JsonPropertyName("needed_network")] bool NeededNetwork,
    [property: JsonPropertyName("areas")] Dictionary<string, PresenceArea>? Areas);

public record PresenceOffer(
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("who")] string? Who,
    [property: JsonPropertyName("topic")] string? Topic);

public record PresenceReach(
    [property: JsonPropertyName("offers")] PresenceOffer[]? Offers,
    [property: JsonPropertyName("note")] string Note);

public record PresenceSurfaceRow(
    [property: JsonPropertyName("surface")] string Surface,
    [property: JsonPropertyName("chosen")] bool Chosen,
    [property: JsonPropertyName("reads_health_aloud")] bool ReadsHealthAloud,
    [property: JsonPropertyName("note")] string Note);

public record PresenceSurfaces(
    [property: JsonPropertyName("chosen_surface")] string Chosen,
    [property: JsonPropertyName("rule")] string Rule,
    [property: JsonPropertyName("surfaces")] PresenceSurfaceRow[]? Surfaces);

/// <summary>How the presence carries itself, and what the dial leaves
/// alone. <c>Unchanged</c> is decoded and rendered rather than trusted from a
/// comment: a bearing that quietly narrowed what a health guardian watches
/// would be a setting that hurts whoever turned it.</summary>
/// <summary>A beat plus the room's verdict on it. The withholding is decided
/// on the server, before anything is synthesised: the surface rule spent a
/// release as a caption next to a button, reported by <c>surfaces()</c> and
/// read by nothing.</summary>
public record PresenceSpoken(
    [property: JsonPropertyName("speaks_on")] string SpeaksOn,
    [property: JsonPropertyName("spoken")] bool Spoken,
    [property: JsonPropertyName("shown")] bool Shown,
    [property: JsonPropertyName("withheld")] string[]? Withheld,
    [property: JsonPropertyName("why_not_aloud")] string WhyNotAloud,
    [property: JsonPropertyName("surface_has_audio")] bool SurfaceHasAudio,
    [property: JsonPropertyName("english")] string English,
    [property: JsonPropertyName("speak")] bool Speak);

public record PresenceBearingEffect(
    [property: JsonPropertyName("says")] string Says);

public record PresenceBearingView(
    [property: JsonPropertyName("bearing")] string Bearing,
    [property: JsonPropertyName("default")] string Default,
    [property: JsonPropertyName("choices")] string[]? Choices,
    [property: JsonPropertyName("effect")] PresenceBearingEffect? Effect,
    [property: JsonPropertyName("unchanged")] Dictionary<string, string>? Unchanged,
    [property: JsonPropertyName("note")] string Note);

public record PresenceGrowth(
    [property: JsonPropertyName("beats_spoken")] int BeatsSpoken,
    [property: JsonPropertyName("areas_i_can_see")] int AreasSeen,
    [property: JsonPropertyName("of")] int Of,
    [property: JsonPropertyName("about_myself")] string AboutMyself);

public record CommunityView(
    [property: JsonPropertyName("qrme_url")] string? QrmeUrl,
    [property: JsonPropertyName("language")] string? Language,
    [property: JsonPropertyName("rooms")] CommunityRoom[] Rooms,
    [property: JsonPropertyName("places")] CommunityPlace[] Places,
    [property: JsonPropertyName("note")] string Note,
    [property: JsonPropertyName("posture")] CommunityPosture Posture);

/// The export bundle, counted rather than modelled.
/// <summary>What came back from an erase: how many rows went, by table.</summary>
public sealed class ErasedReceipt
{
    public Dictionary<string, int> Deleted { get; set; } = new();
}

public sealed class UserExport
{
    public Dictionary<string, List<Dictionary<string, object>>> Tables { get; set; } = new();
    public string Note { get; set; } = "";
}

public sealed class ApiClient
{
    public static ApiClient Shared { get; } = new();

    private readonly HttpClient _http = new() { BaseAddress = new Uri("http://127.0.0.1:8000") };

    /// <summary>Every request this client sends, and the one place the
    /// reader's language is attached to it.
    ///
    /// <para>The header used to be set in the shared send helper — and the
    /// calls that went straight to <c>_http.SendAsync</c> instead never got
    /// it. Those are the uploads, the streams and the raw-response reads, and
    /// every refusal they draw arrived in English no matter what the machine
    /// was set to. A funnel only funnels what goes into it.</para></summary>
    /// <summary>Everything this deployment holds about a person, by table.
    ///
    /// <para>The erase has been on the console since it existed and this had
    /// no route at all.</para></summary>
    public Task<UserExport> ExportEverything(string uid, string token) =>
        Send<UserExport>(new HttpRequestMessage(HttpMethod.Get, $"/data/{uid}"), token);

    /// <summary>
    /// The other direction, and the one this shell had no door for either.
    /// A person could take their data from 0.60.0 and could not end it; both
    /// halves of <em>it is yours</em> have to be reachable from the same
    /// place or only one of them is true.
    /// </summary>
    public Task<ErasedReceipt> EraseEverything(string uid, string token) =>
        Send<ErasedReceipt>(new HttpRequestMessage(HttpMethod.Delete, $"/data/{uid}"), token);

    private Task<HttpResponseMessage> Dispatch(HttpRequestMessage req)
    {
        req.Headers.TryAddWithoutValidation("accept-language", L10n.DeviceLanguage());
        // The person's own model key, if this machine holds one. Sent as a
        // header rather than stored server-side: the backend puts it in a
        // context var for the length of the call and never writes it down.
        var llmKey = AppState.Current.LlmKey;
        if (!string.IsNullOrEmpty(llmKey))
            req.Headers.TryAddWithoutValidation("x-llm-api-key", llmKey);
        // The deployment invite key: a published deployment sets
        // JIM_SIGNUP_KEY and refuses account creation without it. The
        // backend reads it only on the routes it gates.
        var signupKey = AppState.Current.SignupKey;
        if (!string.IsNullOrEmpty(signupKey))
            req.Headers.TryAddWithoutValidation("x-signup-key", signupKey);
        return _http.SendAsync(req);
    }

    public void SetBase(string url) => _http.BaseAddress = new Uri(url.TrimEnd('/'));

    /// The address this client talks to — for the rare door that hands a
    /// page to the system browser instead of reading it itself.
    public Uri Base => _http.BaseAddress!;


    /// <summary>What the deployment can and cannot reach. Read-only: the
    /// posture is set in the deployment's environment, not in the app.</summary>
    /// What the Guardian carries across sessions about this person. Counts
    /// and timings only — the vector is derived from tallies and holds
    /// nothing anybody wrote.
    // The transparency half of the coach's long-term memory: what it can
    // find again, read back from the vault, droppable one moment at a time.
    public Task<MemoryShelf> MemoryShelfFor(string uid, string token) =>
        Send<MemoryShelf>(new HttpRequestMessage(HttpMethod.Get,
            $"/memory/{uid}"), token);

    public Task<MemoryForgotten> ForgetMemory(string uid, string kind,
                                              string reference, string token) =>
        Send<MemoryForgotten>(new HttpRequestMessage(HttpMethod.Delete,
            $"/memory/{uid}/{kind}/{reference}"), token);

    public async Task<ContinuityState> Continuity(string uid, string token) =>
        await Send<ContinuityState>(new HttpRequestMessage(HttpMethod.Get,
            $"/continuity/{uid}"), token);

    /// Drop it. Every derived thing here has to be droppable by the person it
    /// was derived from.
    public async Task<Forgotten> ForgetContinuity(string uid, string token) =>
        await Send<Forgotten>(new HttpRequestMessage(HttpMethod.Delete,
            $"/continuity/{uid}"), token);

    public async Task<OfflinePosture> OfflineStatus() =>
        await Send<OfflinePosture>(new HttpRequestMessage(HttpMethod.Get,
            "/offline/status"));

    // -- The far end, and the widgets: the console-first debt paid ----------
    // (the doorless record's own words). Nine routes only the console could
    // reach; these are this shell's doors to them.

    public Task<FarEndOut> FarEnd(string uid, string token) =>
        Send<FarEndOut>(new HttpRequestMessage(HttpMethod.Get,
            $"/farend/{uid}"), token);

    public Task<FarEndOut> SetFarEnd(string uid, string? email, bool? consent,
                                     string token) =>
        Send<FarEndOut>(Put($"/farend/{uid}",
            new { email, consent }, token));

    public Task<StudioLimitsOut> StudioLimits() =>
        Send<StudioLimitsOut>(new HttpRequestMessage(HttpMethod.Get,
            "/studio/limits"));

    public Task<WidgetListOut> Widgets(string uid, string token) =>
        Send<WidgetListOut>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/widgets"), token);

    public Task<WidgetOut> Widget(string uid, string widgetId, string token) =>
        Send<WidgetOut>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/widgets/{widgetId}"), token);

    public Task<WidgetOut> WriteWidget(string uid, string name, string source,
                                       string token) =>
        Send<WidgetOut>(Post($"/users/{uid}/widgets",
            new { name, source }, token));

    public Task<WidgetOut> ReviseWidget(string uid, string widgetId,
                                        string name, string source,
                                        string token) =>
        Send<WidgetOut>(Put($"/users/{uid}/widgets/{widgetId}",
            new { name, source }, token));

    public Task<WidgetRemovedOut> RemoveWidget(string uid, string widgetId,
                                               string token) =>
        Send<WidgetRemovedOut>(new HttpRequestMessage(HttpMethod.Delete,
            $"/users/{uid}/widgets/{widgetId}"), token);

    public Task<WidgetRanOut> RunWidget(string uid, string widgetId,
                                        string token) =>
        Send<WidgetRanOut>(Post($"/users/{uid}/widgets/{widgetId}/run",
            new { }, token));

    /// <summary>The same send, with the caller's bearer attached.
    ///
    /// <para>Four calls were written against an overload that did not exist.
    /// Rather than open-coding the header at each of them, the overload they
    /// assumed is the one worth having: a token-bearing request is the common
    /// case in this client, and every place that hand-rolled it is a place
    /// that could forget to.</para></summary>
    private Task<T> Send<T>(HttpRequestMessage req, string token)
    {
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        return Send<T>(req);
    }

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

        // The language the reader actually speaks. Every sentence the backend
        // composes on a public route is chosen from this header, and no native
        // shell was sending it.

        HttpResponseMessage res;
        try
        {
            res = await Dispatch(req);
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
                // A plan refusal (402) puts an *object* in detail; its
                // `message` is the sentence composed for the reader.
                else if (root.TryGetProperty("detail", out var dd) && dd.ValueKind == JsonValueKind.Object
                         && dd.TryGetProperty("message", out var dm) && dm.ValueKind == JsonValueKind.String)
                    said = dm.GetString();
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

    // --- engaged sessions -------------------------------------------------
    //
    // The session you leave running. See jim/engaged.py for what it may touch
    // and why the reach is a written list rather than this token's full
    // authority.

    /// <summary>
    /// What an engaged session can do to you, in sentences. No token,
    /// deliberately: this is how somebody decides whether to open one at all,
    /// and a list of what a feature would be allowed to touch is not the
    /// feature.
    /// </summary>
    public Task<EngagedReach> EngagedReach() =>
        Send<EngagedReach>(new HttpRequestMessage(HttpMethod.Get, "/engaged/reach"));

    public Task<EngagedSession> Engaged(string uid, string token) =>
        Send<EngagedSession>(Get($"/engaged/{uid}", token));

    public Task<EngagedSession> Engage(string uid, string token,
                                       string area = "personal_growth") =>
        Send<EngagedSession>(Post($"/engaged/{uid}", new { area }, token));

    public Task<EngagedTurnResult> EngagedTurn(string uid, string token,
                                               string message) =>
        Send<EngagedTurnResult>(Post($"/engaged/{uid}/turn",
            new { message }, token));

    /// <summary>
    /// End the engagement and hand it over. <c>topics</c> becomes the standing
    /// watch list the offline Guardian keeps while this person is away.
    /// </summary>
    public Task<EngagedSignOff> EngagedSignOff(string uid, string token,
                                               string[] topics) =>
        Send<EngagedSignOff>(Post($"/engaged/{uid}/sign-off",
            new { topics }, token));

    public Task<EngagedAct[]> EngagedActs(string uid, string token) =>
        Send<EngagedAct[]>(Get($"/engaged/{uid}/acts", token));

    /// Take one act back, through the door that would have undone it by hand.
    public Task<EngagedUndone> EngagedUndo(string uid, string token,
                                           string actId) =>
        Send<EngagedUndone>(new HttpRequestMessage(HttpMethod.Post,
            $"/engaged/{uid}/acts/{actId}/undo"), token);

    /// <summary>
    /// The groups of switches this session may touch, and which are on.
    ///
    /// The connectors screen turned around to face this account's own
    /// settings. Somebody who wants a thing switched on or off should be able
    /// to say so out loud; this is where they say the Guardian may.
    /// </summary>
    public Task<EngagedPermits> EngagedPermits(string uid, string token) =>
        Send<EngagedPermits>(Get($"/engaged/{uid}/permits", token));

    /// <summary>Switch one group on or off. Both directions, because a grant
    /// that cannot be taken back is not a grant.</summary>
    public Task<EngagedPermitArea> EngagedSetPermit(string uid, string token,
                                                    string area, bool granted) =>
        Send<EngagedPermitArea>(Put($"/engaged/{uid}/permits/{area}",
            new { granted }, token));

    public Task<StandingWatch[]> EngagedWatches(string uid, string token) =>
        Send<StandingWatch[]>(Get($"/engaged/{uid}/watches", token));

    public Task<StandingWatch> EngagedWatch(string uid, string token,
                                            string topic) =>
        Send<StandingWatch>(Post($"/engaged/{uid}/watches", new { topic }, token));

    public Task<WatchCleared> EngagedClearWatch(string uid, string token,
                                                string watchId) =>
        Send<WatchCleared>(new HttpRequestMessage(HttpMethod.Delete,
            $"/engaged/{uid}/watches/{watchId}"), token);

    // The ways back the undo trail replays — and doors a person should always
    // have had. Until an engaged session needed to take a check-in back,
    // nothing in this product could delete one.
    public Task<Removed> RemoveCheckin(string uid, string token, string checkinId) =>
        Send<Removed>(new HttpRequestMessage(HttpMethod.Delete,
            $"/checkin/{uid}/{checkinId}"), token);

    public Task<Removed> RemoveJournal(string uid, string token, string entryId) =>
        Send<Removed>(new HttpRequestMessage(HttpMethod.Delete,
            $"/journal/{uid}/{entryId}"), token);

    public Task<Removed> RemoveGoal(string uid, string token, string goalId) =>
        Send<Removed>(new HttpRequestMessage(HttpMethod.Delete,
            $"/goals/{uid}/{goalId}"), token);

    public Task<Removed> RemoveHabit(string uid, string token, string habitId) =>
        Send<Removed>(new HttpRequestMessage(HttpMethod.Delete,
            $"/habits/{uid}/{habitId}"), token);

    public Task<HabitLogged> UnlogHabit(string uid, string token,
                                        string habitId, string day) =>
        Send<HabitLogged>(new HttpRequestMessage(HttpMethod.Delete,
            $"/habits/{uid}/{habitId}/log/{day}"), token);

    public Task<Guidance> Coach(string uid, string token, string area, string message) =>
        Send<Guidance>(Post($"/coach/{uid}", new { area, message }, token));

    // The offline coach's store and syllabus (jim/pipeline.py): what the
    // stack predicts from, what JIM should study next, and the one-press
    // study that imports the findings.
    public Task<CoachStore> CoachStore(string uid, string token) =>
        Send<CoachStore>(Get($"/coach/{uid}/store", token));

    public Task<CoachCurriculum> CoachCurriculum(string uid, string token) =>
        Send<CoachCurriculum>(Get($"/coach/{uid}/curriculum", token));

    public Task<CoachStudied> CoachStudy(string uid, string token,
                                         string? topic, string? area) =>
        Send<CoachStudied>(Post($"/coach/{uid}/study",
            new { topic, area }, token));

    /// <summary>Open a link to another person's guardian. Refused unless the
    /// two are already each other's contacts.</summary>
    public Task<LiaisonRow> OpenLiaison(string uid, string token,
                                        string otherId, string about = "") =>
        Send<LiaisonRow>(Post($"/liaisons/{uid}",
            new { other_id = otherId, about }, token));

    public Task<LiaisonRow[]> Liaisons(string uid, string token) =>
        Send<LiaisonRow[]>(Get($"/liaisons/{uid}", token));

    /// <summary>Their own guardian's half, and only theirs.</summary>
    public Task<LiaisonHalf> LiaisonHalf(string uid, string token,
                                         string linkId) =>
        Send<LiaisonHalf>(Get($"/liaisons/{uid}/{linkId}", token));

    public async Task LiaisonSaid(string uid, string token, string linkId,
                                  string body)
    {
        var req = Post($"/liaisons/{uid}/{linkId}/said", new { body }, token);
        (await Dispatch(req)).EnsureSuccessStatusCode();
    }

    /// <summary>The work that outlives the call, once both sides have agreed
    /// to it. Naming it is the namer's own yes and nothing more.</summary>
    public Task<LiaisonRow> LiaisonTask(string uid, string token,
                                        string linkId, string task)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
                                         $"/liaisons/{uid}/{linkId}/task")
        {
            Content = JsonContent.Create(new { task }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LiaisonRow>(req);
    }

    /// <summary>The other side's yes, to the task as it stands. No wording of
    /// its own: a second party passing their own text would be proposing
    /// rather than agreeing, and the link could then be held open by two
    /// sentences that only looked like one agreement.</summary>
    public Task<LiaisonRow> LiaisonAgreed(string uid, string token,
                                          string linkId)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
                                         $"/liaisons/{uid}/{linkId}/agreed");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LiaisonRow>(req);
    }

    /// <summary>Which agent is running, and which tasks are still running —
    /// one read across the five things that can be going at once, so somebody
    /// does not have to know which screen owns which. Reads, never acts.
    /// </summary>
    public Task<UnderwayWindow> Underway(string uid, string token) =>
        Send<UnderwayWindow>(Get($"/underway/{uid}", token));

    public Task<LiaisonRow> CloseLiaison(string uid, string token,
                                         string linkId, string why)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
                                         $"/liaisons/{uid}/{linkId}?why={why}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LiaisonRow>(req);
    }

    /// <summary>Say who else is on this call with their own channel 2.
    /// Refused unless this person already has one.</summary>
    public Task<MicPaired> PairMic(string uid, string token, string otherId,
                                   string about = "") =>
        Send<MicPaired>(Post($"/users/{uid}/mic/pair",
            new { other_id = otherId, about }, token));

    public Task<MicPaired> MicPaired(string uid, string token) =>
        Send<MicPaired>(Get($"/users/{uid}/mic/pair", token));

    public Task<MicPaired> UnpairMic(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
                                         $"/users/{uid}/mic/pair");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MicPaired>(req);
    }

    /// <summary>What the monitors noticed, and what each could ever
    /// notice.</summary>
    public Task<CuesSeen> Cues(string uid, string token) =>
        Send<CuesSeen>(Get($"/cues/{uid}", token));

    /// <summary>What was sensed today and what survived of it.</summary>
    public Task<TheDay> Day(string uid, string token) =>
        Send<TheDay>(Get($"/day/{uid}", token));

    // ---- the staleness contract (jim/freshness.py) ----------------------

    /// The wrist channel's pulse apart from the readings — the shell
    /// holding the link to the watch is the road for the beat.
    public Task<HeartbeatSkew> Heartbeat(string uid, string token) =>
        Send<HeartbeatSkew>(Post($"/heartbeat/{uid}",
            new { device_now = DateTimeOffset.UtcNow.ToString("o") }, token));

    /// The two ages and the verdict, on demand.
    public Task<FreshnessFacts> Freshness(string uid, string token) =>
        Send<FreshnessFacts>(Get($"/freshness/{uid}", token));

    /// A recording from inside a meeting, as raw bytes — transcribed on
    /// the way through, the audio never stored.
    public async Task StretchHeard(string uid, string token,
                                   string stretchId, byte[] audio)
    {
        var req = new HttpRequestMessage(HttpMethod.Post,
            $"/day/{uid}/stretches/{stretchId}/heard");
        req.Content = new ByteArrayContent(audio);
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    /// <summary>Begin a meeting or working stretch. Where the monitor catches
    /// other people, somebody has to say they were told — asked again here
    /// rather than inherited from the switch.</summary>
    public Task<Stretch> OpenStretch(string uid, string token, string monitor,
                                     string about = "",
                                     bool othersTold = false) =>
        Send<Stretch>(Post($"/day/{uid}/stretches",
            new { monitor, about, others_told = othersTold }, token));

    public Task<Stretch> CloseStretch(string uid, string token,
                                      string stretchId)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
                                         $"/day/{uid}/stretches/{stretchId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<Stretch>(req);
    }

    /// <summary>Drop what was kept of one moment; the fact that it happened
    /// stays, because a record that loses its own entries is the thing the
    /// daybook exists not to be.</summary>
    public async Task ForgetMoment(string uid, string token, string momentId)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
                                         $"/day/{uid}/moments/{momentId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        (await Dispatch(req)).EnsureSuccessStatusCode();
    }

    /// <summary>Everything that can be plugged in, off rows included.
    /// </summary>
    public Task<MonitorRow[]> Monitors(string uid, string token) =>
        Send<MonitorRow[]>(Get($"/monitors/{uid}", token));

    /// <summary>Switch one on. Anything that senses other people is refused
    /// until <c>othersTold</c> says they know; keeping is its own
    /// decision.</summary>
    public Task<MonitorRow[]> PlugMonitor(string uid, string token,
                                          string name,
                                          string deviceName = "",
                                          bool othersTold = false,
                                          bool keeping = false)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
                                         $"/monitors/{uid}/{name}")
        {
            Content = JsonContent.Create(new
            {
                device_name = deviceName, others_told = othersTold, keeping,
            }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MonitorRow[]>(req);
    }

    public Task<MonitorRow[]> UnplugMonitor(string uid, string token,
                                            string name)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
                                         $"/monitors/{uid}/{name}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MonitorRow[]>(req);
    }

    /// <summary>Anything a monitor perceives comes in through here, and
    /// through the switch check first.</summary>
    public async Task MonitorSensed(string uid, string token, string name)
    {
        var req = Post($"/monitors/{uid}/{name}/sensed", new { }, token);
        (await Dispatch(req)).EnsureSuccessStatusCode();
    }

    /// <summary>Set up an assisted call. It is not listening: what comes back
    /// is the notice to play. <c>number</c> is read for the language and
    /// dropped.</summary>
    public Task<AssistedCall> OpenCall(string uid, string token, string route,
                                       bool recording = false,
                                       string? number = null) =>
        Send<AssistedCall>(Post($"/calls/{uid}",
            new { route, recording, number }, token));

    /// <summary>The notice went out. Confirmed by whatever played it.</summary>
    public async Task CallAnnounced(string uid, string callId, string token)
    {
        var req = Post($"/calls/{uid}/{callId}/announced", new { }, token);
        (await Dispatch(req)).EnsureSuccessStatusCode();
    }

    public Task<CallRow[]> Calls(string uid, string token) =>
        Send<CallRow[]>(Get($"/calls/{uid}", token));

    public async Task EndCall(string uid, string callId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
                                         $"/calls/{uid}/{callId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        (await Dispatch(req)).EnsureSuccessStatusCode();
    }

    /// <summary>Anything the call hands the agent goes through here, and
    /// through the announcement check first.</summary>
    public async Task CallHeard(string uid, string callId, string token)
    {
        var req = Post($"/calls/{uid}/{callId}/heard", new { }, token);
        (await Dispatch(req)).EnsureSuccessStatusCode();
    }

    /// <summary>A draft, read on the device and dropped. Nothing is stored
    /// and nothing is edited — applying a remark is the person's own
    /// act.</summary>
    public Task<Alongside> Alongside(string uid, string token, string draft,
                                     string? area = null) =>
        Send<Alongside>(Post($"/alongside/{uid}", new { draft, area }, token));

    /// <summary>What it went and learned unasked, and what is left to spend
    /// today.</summary>
    public Task<ErrandLedger> Errands(string uid, string token) =>
        Send<ErrandLedger>(Get($"/errands/{uid}", token));

    public record LookoutRow(
        [property: JsonPropertyName("id")] string Id,
        [property: JsonPropertyName("url")] string Url,
        [property: JsonPropertyName("every_hours")] double EveryHours,
        [property: JsonPropertyName("status")] string? Status,
        [property: JsonPropertyName("next_run_at")] string? NextRunAt,
        [property: JsonPropertyName("changed_at")] string? ChangedAt,
        [property: JsonPropertyName("trouble")] string? Trouble);

    public record LookoutList(
        [property: JsonPropertyName("lookouts")] LookoutRow[] Lookouts,
        [property: JsonPropertyName("readable")] bool Readable);

    public record LookoutPage(
        [property: JsonPropertyName("url")] string Url,
        [property: JsonPropertyName("readable")] bool Readable,
        [property: JsonPropertyName("fetched_at")] string? FetchedAt,
        [property: JsonPropertyName("changed_at")] string? ChangedAt,
        [property: JsonPropertyName("chars")] int Chars,
        [property: JsonPropertyName("text")] string? Text);

    public record LookoutPlanted(
        [property: JsonPropertyName("planted")] bool Planted,
        [property: JsonPropertyName("id")] string Id);

    public record LookoutRemoved(
        [property: JsonPropertyName("removed")] bool Removed,
        [property: JsonPropertyName("why")] string? Why);

    // The lookout: a page the vault re-reads on its schedule — JIM never
    // does the watching, and the capture stays sealed in the tandem.
    public Task<LookoutList> Lookouts(string uid, string token) =>
        Send<LookoutList>(Get($"/lookout/{uid}", token));

    public Task<LookoutPlanted> PlantLookout(string uid, string url,
        double everyHours, string token) =>
        Send<LookoutPlanted>(Post($"/lookout/{uid}",
            new { url, every_hours = everyHours }, token));

    public Task<LookoutPage> ReadLookout(string uid, string lid,
        string token) =>
        Send<LookoutPage>(Get($"/lookout/{uid}/{lid}/page", token));

    public Task<LookoutRemoved> DropLookout(string uid, string lid,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/lookout/{uid}/{lid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LookoutRemoved>(req);
    }

    /// <summary>Refused without the permit, and again once the day is spent —
    /// two different sentences, because they are two different things to be
    /// told.</summary>
    public Task<ErrandsRun> RunErrands(string uid, string token) =>
        Send<ErrandsRun>(Post($"/errands/{uid}", new { }, token));

    /// <summary>What the coach noticed during the day, and what settled
    /// each one.</summary>
    public Task<NoticeLedger> Noticed(string uid, string token) =>
        Send<NoticeLedger>(Get($"/noticed/{uid}", token));

    /// <summary>The situational half of the ladder: the offline coach settles
    /// what it can for nothing, and only what it cannot becomes a paid turn.
    /// No budget refusal — a spent day still runs the free half.</summary>
    public Task<NoticedRun> RunNoticed(string uid, string token) =>
        Send<NoticedRun>(Post($"/noticed/{uid}", new { }, token));

    public async Task<BaselineMetric[]> Baseline(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/baseline/{uid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return await Send<BaselineMetric[]>(req);
    }

    // -- life: goals, habits, journal --


    public record ProblemRow(
        [property: JsonPropertyName("source")] string Source,
        [property: JsonPropertyName("app_version")] string AppVersion,
        [property: JsonPropertyName("platform")] string Platform,
        [property: JsonPropertyName("op")] string Op,
        [property: JsonPropertyName("status_code")] int StatusCode,
        [property: JsonPropertyName("day")] string Day,
        [property: JsonPropertyName("count")] int Count);
    public record ProblemRowsResponse(
        [property: JsonPropertyName("rows")] ProblemRow[] Rows);

    // The failure aggregate this backend keeps. Reading is the operator's:
    // the problems key as the token, or nothing when asking from the machine
    // the backend runs on.
    public Task<ProblemRowsResponse> ProblemRows(string key) =>
        Send<ProblemRowsResponse>(Get("/v1/problems", key));

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

    /// <summary>The guardian steps back: the oversight window closes, and
    /// the child account and the recorded consent event remain.
    ///
    /// <para>A guardian link is a standing relationship that outlives the
    /// reason for it — children grow up, custody changes, households end.
    /// iOS has been able to end one since the link was built. This shell
    /// could begin one and not end one, and the route audit said so in
    /// windows_doorless.txt the whole time.</para></summary>
    public async Task UnlinkChild(string gid, string cid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/guardians/{gid}/children/{cid}");
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

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

    /// <summary>The same link, asked for the way a person can answer it.
    /// </summary>
    /// <remarks>
    /// <c>LinkSelfProfile</c> wants a <c>prf_…</c> id and an owner token. The
    /// token is minted once, in QRME's create response, and there is no second
    /// place to read it — so somebody who made the profile elsewhere could not
    /// fill that form in at all. Neither field here is stored on either side.
    /// <para><c>choose</c> comes back when the QRME account holds more than one
    /// profile of the person; send the same body again with
    /// <paramref name="profileId"/>.</para>
    /// </remarks>
    public Task<SelfProfileSignedIn> SignInSelfProfile(string uid,
        string token, string email, string password,
        string? profileId = null) =>
        Send<SelfProfileSignedIn>(Post($"/self-profile/{uid}/sign-in",
            profileId is null ? new { email, password }
                              : (object)new { email, password,
                                              profile_id = profileId },
            token));

    public async Task UnlinkSelfProfile(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, $"/self-profile/{uid}");
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var res = await Dispatch(req);
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
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<Habit[]> Habits(string uid, string token) => Send<Habit[]>(Get($"/habits/{uid}", token));

    public Task<Habit> AddHabit(string uid, string token, string name) =>
        Send<Habit>(Post($"/habits/{uid}", new { name }, token));

    public async Task LogHabit(string uid, string token, string habitId)
    {
        var req = Post($"/habits/{uid}/{habitId}/log", new { }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<JournalItem[]> Journal(string uid, string token) => Send<JournalItem[]>(Get($"/journal/{uid}", token));

    public async Task AddJournal(string uid, string token, string text)
    {
        var req = Post($"/journal/{uid}", new { text }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    /// <summary>Meals: the note is the log, the photo the sealed receipt.</summary>
    public Task<Meal> LogMeal(string uid, string note, string token,
        string? contentB64 = null) =>
        Send<Meal>(Post($"/users/{uid}/meals",
            contentB64 is null ? new { note } : new { note, content = contentB64 },
            token));

    public Task<Meal[]> Meals(string uid, string token) =>
        Send<Meal[]>(Get($"/users/{uid}/meals", token));

    /// <summary>The weekly letter: composed only from what was logged.</summary>
    public Task<Letter> WriteLetter(string uid, string token) =>
        Send<Letter>(Post($"/users/{uid}/letters", new { }, token));

    public Task<Letter[]> Letters(string uid, string token) =>
        Send<Letter[]>(Get($"/users/{uid}/letters", token));

    /// <summary>Interview drills: the bank is local; works offline.</summary>
    public Task<Drill> StartDrill(string uid, string token) =>
        Send<Drill>(Post($"/users/{uid}/drills", new { }, token));

    public Task<Drill> AnswerDrill(string uid, string drillId,
        string answer, string token) =>
        Send<Drill>(Post($"/users/{uid}/drills/{drillId}/answer",
            new { answer }, token));

    public Task<Drill[]> Drills(string uid, string token) =>
        Send<Drill[]>(Get($"/users/{uid}/drills", token));

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
        var res = await Dispatch(req);
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
        var res = await Dispatch(req);
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
                // A plan refusal (402) puts an *object* in detail; its
                // `message` is the sentence composed for the reader.
                else if (root.TryGetProperty("detail", out var dd) && dd.ValueKind == JsonValueKind.Object
                         && dd.TryGetProperty("message", out var dm) && dm.ValueKind == JsonValueKind.String)
                    said = dm.GetString();
            }
            catch { /* non-JSON error body */ }
            throw new HttpRequestException(said ?? $"HTTP {(int)res.StatusCode}");
        }
    }

    public async Task RevokeWaiver(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, $"/waivers/{uid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        var res = await Dispatch(req);
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
        var res = await Dispatch(req);
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
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task SocialScrape(string cid, string token)
    {
        var req = Post($"/social/connection/{cid}/scrape", new { }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task SocialPublish(string cid, string token, string content)
    {
        var req = Post($"/social/connection/{cid}/publish", new { content }, token);
        var res = await Dispatch(req);
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
        var res = await Dispatch(req);
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
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    // -- Help us improve — product feedback (open to anyone) --

    public async Task SubmitImprovement(string? token, string category,
                                        string message, int? rating)
    {
        object body = rating is { } r
            ? new { category, message, rating = r }
            : new { category, message };
        var res = await Dispatch(Post("/improve", body, token));
        res.EnsureSuccessStatusCode();
    }

    public Task<ImproveState> Improvements(string? token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, "/improve");
        if (token is { Length: > 0 }) req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ImproveState>(req);
    }

    // The accessibility door: tokenless on purpose — the person it exists
    // for may be the person the enrollment shut out. The words stay on the
    // deployment; nothing here reaches the problems collector.
    public async Task<string> SendAccessReport(string doing, string wall,
                                               string? help, string lang)
    {
        object body = help is { Length: > 0 } h
            ? new { doing, wall, help = h, lang }
            : new { doing, wall, lang };
        var res = await Dispatch(Post("/access/reports", body, null));
        res.EnsureSuccessStatusCode();
        return "received";
    }

    // Reviewer-token read — the deployment's steward, never a user.
    public Task<AccessReportsState> AccessReports(string reviewerToken)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, "/access/reports");
        req.Headers.Add("authorization", $"Bearer {reviewerToken}");
        return Send<AccessReportsState>(req);
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
        var res = await Dispatch(
            Post($"/community/{uid}/visits", new { room_id = roomId }, token));
        res.EnsureSuccessStatusCode();
    }


    // MARK: The presence — the coach that speaks first
    //
    // Every read here is answered from rows the backend already holds — no
    // model, no second call out. A machine with no connection still gets its
    // day, which is the whole argument of `jim/presence.py`.

    /// <summary>What it is, and what it will not be. No token: the answer
    /// must be the same to a child, a guardian, a clinician and a
    /// regulator.</summary>
    /// <remarks>The token is passed and ignored by the route: this answer is
    /// public by design, and sending the header keeps one code path rather
    /// than a second unauthenticated one.</remarks>
    public Task<PresenceWho> PresenceWho(string token) =>
        Send<PresenceWho>(Get("/presence", token));

    /// <summary>The six areas and where each one stands.</summary>
    public Task<PresenceBaseline> PresenceBaseline(string uid, string token) =>
        Send<PresenceBaseline>(Get($"/presence/{uid}/baseline", token));

    /// <summary>The day's three beats at once — a plan a client can hold and
    /// then lose its connection without losing the day.</summary>
    public Task<PresenceDay> PresenceDay(string uid, string token) =>
        Send<PresenceDay>(Get($"/presence/{uid}/day", token));

    /// <summary>One beat. Asking is what counts as having been told: the
    /// backend records it so the same line does not return tomorrow.</summary>
    public Task<PresenceBeat> PresenceBeat(string uid, string token, string slot) =>
        Send<PresenceBeat>(Get($"/presence/{uid}/beat?slot={slot}", token));

    /// <summary>The same beat with a model's wording. The model may not
    /// decide that there is a beat, which area, or what the evidence
    /// says.</summary>
    public Task<PresenceBeat> PresenceDeepen(string uid, string token, string slot) =>
        Send<PresenceBeat>(Post($"/presence/{uid}/deepen?slot={slot}", new { }, token));

    /// <summary>Other minds — QRME's rooms, desks and profiles, offered.</summary>
    public Task<PresenceReach> PresenceReach(string uid, string token) =>
        Send<PresenceReach>(Get($"/presence/{uid}/reach", token));

    /// <summary>Where it may speak, and what each surface makes it hold
    /// back.</summary>
    public Task<PresenceSurfaces> PresenceSurfaces(string uid, string token) =>
        Send<PresenceSurfaces>(Get($"/presence/{uid}/surfaces", token));

    public Task<PresenceSurfaces> PresenceChooseSurface(string uid, string token,
                                                        string surface) =>
        Send<PresenceSurfaces>(Put($"/presence/{uid}/surface",
            new { speaks_on = surface }, token));

    /// <summary>The beat, and whether this surface may speak it.</summary>
    public Task<PresenceSpoken> PresenceSay(string uid, string token,
                                            string slot) =>
        Send<PresenceSpoken>(Get($"/presence/{uid}/say?slot={slot}", token));

    /// <summary>The hands-free question. Does not record — a machine polling
    /// on a timer must not burn a beat nobody heard.</summary>
    public Task<PresenceSpoken> PresenceDue(string uid, string token) =>
        Send<PresenceSpoken>(Get($"/presence/{uid}/due", token));

    /// <summary>The bearing: companion by default, professional on
    /// request.</summary>
    public Task<PresenceBearingView> PresenceBearing(string uid, string token) =>
        Send<PresenceBearingView>(Get($"/presence/{uid}/bearing", token));

    public Task<PresenceBearingView> PresenceSetBearing(string uid, string token,
                                                        string bearing) =>
        Send<PresenceBearingView>(Put($"/presence/{uid}/bearing",
            new { bearing }, token));

    /// <summary>What it has become, with the counts under it.</summary>
    public Task<PresenceGrowth> PresenceGrowth(string uid, string token) =>
        Send<PresenceGrowth>(Get($"/presence/{uid}/growth", token));

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

    /// <summary>The offline fine-tune. Beside Adaptation and not folded into
    /// it: that one recomputes a profile that conditions a prompt, this one
    /// trains weights.</summary>
    public Task<Finetune> Finetune(string uid, string token) =>
        Send<Finetune>(Get($"/finetune/{uid}", token));

    /// <summary>Train from the history already on record — local work only.
    /// The pass runs with the backend's network blocked.</summary>
    public Task<Finetune> RunFinetune(string uid, string token) =>
        Send<Finetune>(Post($"/finetune/{uid}", new { }, token));

    /// <summary>Training and using are two decisions.</summary>
    public Task<FinetuneSwitchResult> SetFinetuneActive(
            string uid, string token, bool active) =>
        Send<FinetuneSwitchResult>(
            Put($"/finetune/{uid}/active", new { active }, token));

    public Task<AnonymityPosture> Anonymity(string uid, string token) =>
        Send<AnonymityPosture>(Get($"/anonymity/{uid}", token));

    // -- money: the guardian that watches balances (jim/money.py) --
    // The overview carries its own labels in the reader's language; the
    // page renders them and adds no English of its own, because the count
    // behind this shell's tabs is a ratchet that must not grow.

    public Task<MoneyOverview> MoneyOverview(string uid, string token) =>
        Send<MoneyOverview>(Get($"/money/{uid}", token));

    /// <summary>The statement file goes to the vault; the reading is local.</summary>
    public Task<StatementReading> MoneyDropStatement(string uid, string token,
        string accountId, string contentB64) =>
        Send<StatementReading>(Post($"/money/{uid}/statements",
            new { account_id = accountId, content = contentB64 }, token));

    public Task<StatementReading[]> MoneyStatements(string uid, string token) =>
        Send<StatementReading[]>(Get($"/money/{uid}/statements", token));

    /// <summary>A written aggregator consent; status never claims data.</summary>
    public Task<BankLinkOut> MoneyLinkBank(string uid, string token,
        string institution, string aggregator) =>
        Send<BankLinkOut>(Post($"/money/{uid}/links",
            new { institution, aggregator }, token));

    public Task<BankLinkOut[]> MoneyLinks(string uid, string token) =>
        Send<BankLinkOut[]>(Get($"/money/{uid}/links", token));

    public Task<BankLinkOut> MoneySyncBank(string uid, string token,
        string linkId) =>
        Send<BankLinkOut>(Post($"/money/{uid}/links/{linkId}/sync",
            new { }, token));

    public Task<BankLinkOut> MoneyRevokeLink(string uid, string token,
        string linkId)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/money/{uid}/links/{linkId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<BankLinkOut>(req);
    }

    public Task<MoneyAccount> MoneyAddAccount(string uid, string token,
                                              string kind, string institution,
                                              string? accountNumber,
                                              string? routingNumber)
    {
        object body = (string.IsNullOrWhiteSpace(accountNumber),
                       string.IsNullOrWhiteSpace(routingNumber)) switch
        {
            (true, true) => new { kind, institution },
            (false, true) => new { kind, institution, account_number = accountNumber },
            (true, false) => new { kind, institution, routing_number = routingNumber },
            _ => new { kind, institution, account_number = accountNumber,
                       routing_number = routingNumber },
        };
        return Send<MoneyAccount>(Post($"/money/{uid}/accounts", body, token));
    }

    public Task<MoneyObserved> MoneyObserve(string uid, string token,
                                            string accountId, double balance) =>
        Send<MoneyObserved>(Post($"/money/{uid}/observe",
            new { account_id = accountId, balance }, token));

    public Task<SavingsGoal> MoneySetSavings(string uid, string token, double goal) =>
        Send<SavingsGoal>(Put($"/money/{uid}/savings", new { goal }, token));

    // The low-balance floor. Zero is refused server-side — a warning that
    // can never fire is not a setting.
    public Task<MoneyFloor> MoneySetFloor(string uid, string token, double floor) =>
        Send<MoneyFloor>(Put($"/money/{uid}/floor", new { floor }, token));

    // -- schedule + shopping through the tandem --
    // Labels ride the views in the reader's language; the pivots render
    // them and add no English of their own.

    public Task<ScheduleOverview> ScheduleView(string uid, string token) =>
        Send<ScheduleOverview>(Get($"/schedule/{uid}", token));

    public Task<AppointmentRow> ScheduleBook(string uid, string token,
                                             string title, string when,
                                             string? where, bool emailReminder)
    {
        object body = string.IsNullOrWhiteSpace(where)
            ? new { title, when, email_reminder = emailReminder }
            : new { title, when, where, email_reminder = emailReminder };
        return Send<AppointmentRow>(Post($"/schedule/{uid}", body, token));
    }

    public Task<AppointmentRow> ScheduleCancel(string uid, string token,
                                               string appointmentId)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/schedule/{uid}/{appointmentId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<AppointmentRow>(req);
    }

    public Task<ShoppingOverview> ShoppingView(string uid, string token) =>
        Send<ShoppingOverview>(Get($"/shopping/{uid}", token));

    public Task<PlacedTandemOrder> ShoppingOrder(string uid, string token,
                                                 string shopId,
                                                 string offeringId,
                                                 int quantity) =>
        Send<PlacedTandemOrder>(Post($"/shopping/{uid}/order",
            new { shop_id = shopId, offering_id = offeringId, quantity },
            token));

    public Task<PlacedTandemOrder> ShoppingCancel(string uid, string token,
                                                  string qrmeOrderId) =>
        Send<PlacedTandemOrder>(Post($"/shopping/{uid}/cancel",
            new { qrme_order_id = qrmeOrderId }, token));

    // -- your circle: contacts, messages, switches, homepage --
    // Same discipline: the view carries labels; the pivot adds no English.

    public Task<CircleOverview> CircleView(string uid, string token) =>
        Send<CircleOverview>(Get($"/circle/{uid}", token));

    public Task<System.Collections.Generic.Dictionary<string, bool>> CircleSetFeature(
        string uid, string token, string feature, bool enabled) =>
        Send<System.Collections.Generic.Dictionary<string, bool>>(
            Put($"/circle/{uid}/features", new { feature, enabled }, token));

    public Task<CircleTie> CircleInvite(string uid, string token, string otherId) =>
        Send<CircleTie>(Post($"/circle/{uid}/contacts",
            new { other_id = otherId }, token));

    public Task<CircleTie> CircleLeave(string uid, string token, string otherId)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/circle/{uid}/contacts/{otherId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<CircleTie>(req);
    }

    public Task<CircleMessageRow> CircleSend(string uid, string token,
                                             string to, string body) =>
        Send<CircleMessageRow>(Post($"/circle/{uid}/messages",
            new { to, body }, token));

    public Task<CircleThreadBox> CircleThread(string uid, string token,
                                              string withId) =>
        Send<CircleThreadBox>(Get(
            $"/circle/{uid}/messages?with_id={Uri.EscapeDataString(withId)}",
            token));

    public Task<CircleHomepageDoc> CircleHomepage(string uid, string token,
                                                  string otherId) =>
        Send<CircleHomepageDoc>(Get($"/circle/{uid}/homepage/{otherId}", token));

    public Task<CircleHomepageDoc> CircleEditHomepage(string uid, string token,
                                                      string headline,
                                                      string about, string bg,
                                                      string accent) =>
        Send<CircleHomepageDoc>(Put($"/circle/{uid}/homepage",
            new { headline, about, theme = new { bg, accent } }, token));

    /// <summary>The handover, and the way back. Revoking is never plan-gated.</summary>
    public Task<MoneyMandate> MoneySetMandate(string uid, string token, bool enabled,
                                              double capPerOrder, double monthlyCap,
                                              string scope) =>
        Send<MoneyMandate>(Put($"/money/{uid}/mandate",
            new { enabled, cap_per_order = capPerOrder, monthly_cap = monthlyCap,
                  asset_classes = new[] { "index_funds" }, scope }, token));


    // -- care team, clinical captures, and channel 2 — the console doors
    // task #106 built that the desktop shell never got. ------------------

    public Task<CareTeamState> CareTeamState(string uid, string token) =>
        Send<CareTeamState>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/care-team"), token);

    public Task<CareTeamState> CareTeamLink(string uid, string token,
                                            string orgId, string departmentId,
                                            string ownerToken) =>
        Send<CareTeamState>(Put($"/users/{uid}/care-team",
            new { org_id = orgId, department_id = departmentId,
                  owner_token = ownerToken }, token));

    public async Task CareTeamUnlink(string uid, string token)
    {
        // 204: the server says nothing on success, deliberately.
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/users/{uid}/care-team");
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<CarePlanRow> CareTeamCoordinate(string uid, string token,
                                                string goal) =>
        Send<CarePlanRow>(Post($"/users/{uid}/care-team/coordinate",
            new { goal }, token));

    public Task<CarePlanRow[]> CareTeamPlans(string uid, string token) =>
        Send<CarePlanRow[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/care-team/plans"), token);

    public Task<MicTypeChoices> MicTypes() =>
        Send<MicTypeChoices>(new HttpRequestMessage(HttpMethod.Get,
            "/mic/types"));

    public Task<MicGainChoices> MicGains() =>
        Send<MicGainChoices>(new HttpRequestMessage(HttpMethod.Get,
            "/mic/gains"));

    public Task<MicState> MicState(string uid, string token) =>
        Send<MicState>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/mic"), token);

    public Task<MicState> AttachMic(string uid, string token,
                                    string deviceName, string micType) =>
        Send<MicState>(Put($"/users/{uid}/mic",
            new { device_name = deviceName, mic_type = micType }, token));

    public Task<MicState> DetachMic(string uid, string token) =>
        Send<MicState>(new HttpRequestMessage(HttpMethod.Delete,
            $"/users/{uid}/mic"), token);

    public Task<MicState> SetMicGain(string uid, string token, string gain) =>
        Send<MicState>(Put($"/users/{uid}/mic/gain", new { gain }, token));

    /// "earpiece": the hand-over requires the occupying call to be on a
    /// private route — jim/mic.py refuses it on speaker, where the watch
    /// would hear both sides.
    public Task<MicState> HandOverMic(string uid, string token,
                                      string reason) =>
        Send<MicState>(Post($"/users/{uid}/mic/handover",
            new { reason, route = "earpiece" }, token));

    /// Hand in what channel 2 picked up, from the device it was lent to.
    ///
    /// <c>words</c> where the device recognised the speech itself — a
    /// watch with an on-device recogniser answers with nothing but text
    /// leaving the wrist — and <c>audioBase64</c> only where it cannot.
    /// Refused unless a channel is attached and handed over: see
    /// jim/mic.py.
    public Task<MicHeard> MicHeard(string uid, string token,
                                   string deviceName, string? words = null,
                                   string? audioBase64 = null) =>
        Send<MicHeard>(Post($"/users/{uid}/mic/heard",
            new { device_name = deviceName, words, audio_base64 = audioBase64 },
            token));

    public Task<MicState> ReleaseMic(string uid, string token) =>
        Send<MicState>(Post($"/users/{uid}/mic/release", new { }, token));

    public Task<MicEventRow[]> MicHistory(string uid, string token) =>
        Send<MicEventRow[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/mic/history"), token);

    public Task<CaptureVocabulary> CaptureVocabulary() =>
        Send<CaptureVocabulary>(new HttpRequestMessage(HttpMethod.Get,
            "/captures/vocabulary"));

    public Task<CaptureRecord[]> Captures(string uid, string token) =>
        Send<CaptureRecord[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/captures"), token);

    public Task<CaptureRecord> TakeCapture(string uid, string token,
                                           string site, string contentBase64,
                                           string note,
                                           bool intimateConsent) =>
        Send<CaptureRecord>(Post($"/users/{uid}/captures",
            note is { Length: > 0 }
                ? new { kind = "photo", site, content = contentBase64,
                        provenance = "captured",
                        intimate_consent = intimateConsent, note }
                : (object)new { kind = "photo", site, content = contentBase64,
                                provenance = "captured",
                                intimate_consent = intimateConsent }, token));

    public Task<CaptureImageRow> CaptureImage(string uid, string token,
                                              string captureId) =>
        Send<CaptureImageRow>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/captures/{captureId}/image"), token);

    public Task<CaptureAttachOutcome> AttachCaptures(string uid, string token,
                                                     string[] captureIds) =>
        Send<CaptureAttachOutcome>(Post($"/users/{uid}/captures/attach",
            new { capture_ids = captureIds }, token));

    public async Task WithdrawCapture(string uid, string token,
                                      string captureId)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/users/{uid}/captures/{captureId}");
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    // ---- the health core: the cabinet, the vigil, and the baseline bands --

    public Task<MedsBoard> MedsBoard(string uid, string token) =>
        Send<MedsBoard>(new HttpRequestMessage(HttpMethod.Get,
            $"/meds/{uid}"), token);

    public Task<MedRow> AddMed(string uid, string token, string name,
                               string dose, object schedule, string purpose,
                               bool critical) =>
        Send<MedRow>(Post($"/meds/{uid}",
            purpose is { Length: > 0 }
                ? new { name, dose, schedule, critical, purpose }
                : (object)new { name, dose, schedule, critical }, token));

    public Task<MedRow> SetMedCritical(string uid, string token,
                                       string medId, bool critical) =>
        Send<MedRow>(Put($"/meds/{uid}/{medId}", new { critical }, token));

    /// Stopped, not deleted — the route keeps the history honest.
    public Task<MedRow> StopMed(string uid, string token, string medId) =>
        Send<MedRow>(new HttpRequestMessage(HttpMethod.Delete,
            $"/meds/{uid}/{medId}"), token);

    public Task<MedsBoard> LogDose(string uid, string token, string medId,
                                   string action, string? slot) =>
        Send<MedsBoard>(Post($"/meds/{uid}/{medId}/log",
            slot is null ? new { action } : (object)new { action, slot },
            token));

    public Task<MedAdherence> MedAdherence(string uid, string token) =>
        Send<MedAdherence>(new HttpRequestMessage(HttpMethod.Get,
            $"/meds/{uid}/adherence"), token);

    public Task<VigilState> VigilStatus(string uid, string token) =>
        Send<VigilState>(new HttpRequestMessage(HttpMethod.Get,
            $"/vigil/{uid}"), token);

    public Task<VigilState> ArmVigil(string uid, string token,
                                     string stewardName, string stewardChannel,
                                     double quietDays, string note) =>
        Send<VigilState>(Put($"/vigil/{uid}",
            note is { Length: > 0 }
                ? new { steward_name = stewardName,
                        steward_channel = stewardChannel,
                        quiet_days = quietDays, note }
                : (object)new { steward_name = stewardName,
                                steward_channel = stewardChannel,
                                quiet_days = quietDays }, token));

    public Task<VigilState> DisarmVigil(string uid, string token) =>
        Send<VigilState>(new HttpRequestMessage(HttpMethod.Delete,
            $"/vigil/{uid}"), token);

    /// Idempotent silence check; trips at most once. Opening the screen is
    /// the natural moment to ask whether anybody has gone quiet.
    public Task<VigilState> SweepVigil(string uid, string token) =>
        Send<VigilState>(Post($"/vigil/{uid}/sweep", new { }, token));

    /// The "I'm okay" button.
    public Task<VigilState> ResolveVigil(string uid, string token) =>
        Send<VigilState>(Post($"/vigil/{uid}/resolve", new { }, token));

    public Task<BandsOverview> Bands(string uid, string token) =>
        Send<BandsOverview>(new HttpRequestMessage(HttpMethod.Get,
            $"/bands/{uid}"), token);

    public Task<BandRow> SetBand(string uid, string token, string metric,
                                 double? margin, bool? watchHigh,
                                 bool? watchLow)
    {
        // BandSet keeps whatever is in force for omitted fields, so only
        // the fields the caller actually set ride the wire.
        var body = new Dictionary<string, object>();
        if (margin is { } m) body["margin"] = m;
        if (watchHigh is { } h) body["watch_high"] = h;
        if (watchLow is { } l) body["watch_low"] = l;
        return Send<BandRow>(Put($"/bands/{uid}/{metric}", body, token));
    }

    /// Back to the default width for this metric.
    public Task<BandRow> ResetBand(string uid, string token, string metric) =>
        Send<BandRow>(new HttpRequestMessage(HttpMethod.Delete,
            $"/bands/{uid}/{metric}"), token);

    // ---- deployment settings: the voice and the mail desk ------------------

    public Task<VoiceSettingsOut> VoiceSettings() =>
        Send<VoiceSettingsOut>(new HttpRequestMessage(HttpMethod.Get,
            "/settings/voice"));

    public Task<VoiceSettingsOut> SaveVoiceSettings(string provider,
                                                    string apiKey,
                                                    string voiceId,
                                                    bool speakReplies)
    {
        var body = new Dictionary<string, object>
        { ["provider"] = provider, ["speak_replies"] = speakReplies };
        if (apiKey is { Length: > 0 }) body["api_key"] = apiKey;
        if (voiceId is { Length: > 0 }) body["voice_id"] = voiceId;
        return Send<VoiceSettingsOut>(Put("/settings/voice", body));
    }

    public Task<VoiceSettingsOut> ClearVoiceSettings() =>
        Send<VoiceSettingsOut>(new HttpRequestMessage(HttpMethod.Delete,
            "/settings/voice"));

    /// Is the saved key a working key? Saving only ever reported that the
    /// string was written down, and the first anybody knew otherwise was a
    /// raw provider error at the moment they asked to be spoken to.
    public Task<VoiceKeyCheckOut> CheckVoiceKey() =>
        Send<VoiceKeyCheckOut>(Post("/settings/voice/check",
            new Dictionary<string, object>()));

    /// How much speaking is left. Throws on a deployment using the device's
    /// own voice, or a provider that publishes no balance — the page treats
    /// that as "no line to show" rather than an error worth a red row.
    public Task<VoiceQuotaOut> VoiceQuota() =>
        Send<VoiceQuotaOut>(new HttpRequestMessage(HttpMethod.Get,
            "/voice/quota"));

    public Task<MailSettingsOut> MailSettings() =>
        Send<MailSettingsOut>(new HttpRequestMessage(HttpMethod.Get,
            "/settings/mail"));

    public Task<MailSettingsOut> SaveMailSettings(string host, int port,
                                                  string username,
                                                  string password,
                                                  string sender,
                                                  string publicUrl)
    {
        var body = new Dictionary<string, object>
        { ["host"] = host, ["port"] = port };
        if (username is { Length: > 0 }) body["username"] = username;
        if (password is { Length: > 0 }) body["password"] = password;
        if (sender is { Length: > 0 }) body["sender"] = sender;
        if (publicUrl is { Length: > 0 }) body["public_url"] = publicUrl;
        return Send<MailSettingsOut>(Put("/settings/mail", body));
    }

    /// Forget the mail server; delivery falls back to the console.
    public Task<MailSettingsOut> ClearMailSettings() =>
        Send<MailSettingsOut>(new HttpRequestMessage(HttpMethod.Delete,
            "/settings/mail"));

    /// Send a real message now — proof the settings can deliver.
    public Task<MailTestOut> TestMail(string to) =>
        Send<MailTestOut>(Post("/settings/mail/test", new { to }));

    // ---- the guide, the help box, and the dock in the corner ---------------

    public Task<TutorialOutline> TutorialOutline() =>
        Send<TutorialOutline>(new HttpRequestMessage(HttpMethod.Get,
            "/tutorial"));

    public Task<TutorialStep> TutorialStep(string key) =>
        Send<TutorialStep>(new HttpRequestMessage(HttpMethod.Get,
            $"/tutorial/steps/{key}"));

    /// The lesson covering a given screen, so a screen can explain itself.
    public Task<TutorialStep> TutorialForScreen(int number) =>
        Send<TutorialStep>(new HttpRequestMessage(HttpMethod.Get,
            $"/tutorial/for-screen/{number}"));

    public Task<TutorialProgress> StartTutorial(string learnerId) =>
        Send<TutorialProgress>(Post("/tutorial/start",
            new { learner_id = learnerId }));

    public Task<TutorialProgress> TutorialProgress(string learnerId) =>
        Send<TutorialProgress>(new HttpRequestMessage(HttpMethod.Get,
            $"/tutorial/progress/{learnerId}"));

    public Task<TutorialProgress> MarkTutorialDone(string learnerId,
                                                   string lesson) =>
        Send<TutorialProgress>(Post("/tutorial/done",
            new { learner_id = learnerId, lesson }));

    public Task<HelpTopics> HelpTopics() =>
        Send<HelpTopics>(new HttpRequestMessage(HttpMethod.Get,
            "/help/topics"));

    /// The help box: "where is the thing?" It writes nothing.
    public Task<HelpAnswer> AskHelp(string question) =>
        Send<HelpAnswer>(Post("/help", new { question }));

    public Task<DockVocabulary> DockVocabulary() =>
        Send<DockVocabulary>(new HttpRequestMessage(HttpMethod.Get,
            "/dock/faces"));

    public Task<DockState> DockState(string uid, string token) =>
        Send<DockState>(new HttpRequestMessage(HttpMethod.Get,
            $"/dock/{uid}"), token);

    public Task<DockState> ConfigureDock(string uid, string token,
                                         string? corner, string? state,
                                         string? face)
    {
        var body = new Dictionary<string, object>();
        if (corner is { }) body["corner"] = corner;
        if (state is { }) body["state"] = state;
        if (face is { }) body["face"] = face;
        return Send<DockState>(Put($"/dock/{uid}", body, token));
    }

    /// One face, as the pane would draw it. Read-only by construction.
    public Task<DockFace> DockFace(string uid, string token, string name) =>
        Send<DockFace>(new HttpRequestMessage(HttpMethod.Get,
            $"/dock/{uid}/face/{name}"), token);

    /// The screen that can actually do this face's job.
    public Task<DockWhere> DockWhere(string face) =>
        Send<DockWhere>(new HttpRequestMessage(HttpMethod.Get,
            $"/dock/where/{face}"));

    // ---- the wrist and the doorway: watch channel, devices, pairing --------

    public Task<WatchSetup> WatchSetup(string uid, string token,
                                       string device = "apple_watch") =>
        Send<WatchSetup>(new HttpRequestMessage(HttpMethod.Get,
            $"/watch/channel/{uid}?device={device}"), token);

    /// Rotating invalidates the old drip token.
    // The three QR images: the JSON sender cannot carry an image, so the
    // door is the request the opener makes, and Get(...) is what the route
    // audit reads.
    public string PairQrUrl() => Get("/pair/qr.svg").RequestUri!.ToString();

    public string BeaconQrUrl(string bid) =>
        Get($"/c/{bid}/qr.svg").RequestUri!.ToString();

    public string ConnectionQrUrl(string cid) =>
        Get($"/social/connection/{cid}/qr.svg").RequestUri!.ToString();

    // One reading through the Shortcut's own door — the token in the path
    // is the whole credential, so no account token rides along.
    public Task<DripAck> WatchDrip(string dripToken, int heartRate) =>
        Send<DripAck>(Post($"/watch/drip/{dripToken}",
                           new { heart_rate = heartRate }));

    public Task<WatchSetup> RotateWatchChannel(string uid, string token) =>
        Send<WatchSetup>(Post($"/watch/channel/{uid}/rotate", new { },
                              token));

    /// Upload the Health app's export.zip. History folds into baselines
    /// only — enrollment day should be quiet.
    public async Task SeedWatch(string uid, string token, byte[] data)
    {
        var req = new HttpRequestMessage(HttpMethod.Post,
            $"/watch/seed/{uid}");
        req.Content = new ByteArrayContent(data);
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    /// How to open the Guardian on a phone: the console's URL on this
    /// local network. Same Wi-Fi, no app store.
    public Task<PairInfo> PairInfo() =>
        Send<PairInfo>(new HttpRequestMessage(HttpMethod.Get, "/pair"));

    public Task<DeviceRow[]> Devices(string uid, string token) =>
        Send<DeviceRow[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/devices/{uid}"), token);

    public Task<DeviceRow> RegisterDevice(string uid, string token,
                                          string name, string kind,
                                          bool paired) =>
        Send<DeviceRow>(Post($"/devices/{uid}",
            new { name, kind, paired }, token));

    // ---- the account the phones never had ----

    /// A deployment with mail answers pending and sends the code; a local
    /// install with no mail transport activates directly and answers with
    /// the session.
    public Task<SignupResult> Signup(string email, string password,
                                     string name, string? language = null) =>
        Send<SignupResult>(Post("/signup",
            language is { Length: > 0 } && language != "en"
                ? new { email, password, display_name = name,
                        terms_consent = true, language }
                : (object)new { email, password, display_name = name,
                                terms_consent = true }));

    public Task<SignInResult> Signin(string email, string password) =>
        Send<SignInResult>(Post("/signin", new { email, password }));

    /// The code proves the inbox; the user is enrolled here, not at signup,
    /// which is why this answers with the same shape enrollment does.
    public Task<EnrollResult> VerifyEmail(string email, string code) =>
        Send<EnrollResult>(Post("/verify-email", new { email, code }));

    public Task<CodeDelivery> ResendCode(string email) =>
        Send<CodeDelivery>(Post("/verify-email/resend", new { email }));

    public Task<CodeDelivery> RequestPasswordReset(string email) =>
        Send<CodeDelivery>(Post("/password/reset/request", new { email }));

    /// Every existing session dies with the old password.
    public Task<ResetDone> ResetPassword(string email, string code,
                                         string newPassword) =>
        Send<ResetDone>(Post("/password/reset",
            new { email, code, new_password = newPassword }));

    public Task<OauthProviders> OauthProviders() =>
        Send<OauthProviders>(new HttpRequestMessage(HttpMethod.Get,
            "/auth/oauth/providers"));

    /// No redirect_uri: the backend defaults to its own callback page, and
    /// this shell polls the claim rather than intercepting the browser.
    public Task<OauthStarted> OauthStart(string provider) =>
        Send<OauthStarted>(Post($"/auth/oauth/{provider}/start", new { }));

    public Task<OauthClaim> OauthClaim(string state) =>
        Send<OauthClaim>(new HttpRequestMessage(HttpMethod.Get,
            $"/auth/oauth/claim?state={state}"));

    public Task<SessionStarted> StartSession(string uid, string token,
                                             string device) =>
        Send<SessionStarted>(Post($"/sessions/{uid}", new { device }, token));

    public Task<SessionEnded> EndSession(string uid, string token,
                                         string sessionId) =>
        Send<SessionEnded>(Post($"/sessions/{uid}/{sessionId}/end",
            new { }, token));

    // ---- the Guardian learns the day ----

    public Task<CalmCatalog> CalmCatalog() =>
        Send<CalmCatalog>(new HttpRequestMessage(HttpMethod.Get, "/calm"));

    /// A protocol, not a generation — the counts never vary.
    public Task<CalmStarted> StartCalm(string uid, string token, string kind) =>
        Send<CalmStarted>(Post($"/calm/{uid}/{kind}", new { }, token));

    public Task<CalmHistoryRow[]> CalmHistory(string uid, string token) =>
        Send<CalmHistoryRow[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/calm/{uid}/history"), token);

    public Task<WorkoutPlan> WorkoutPlan(string uid, string token, int minutes,
                                         string level, string focus) =>
        Send<WorkoutPlan>(Post($"/fitness/{uid}/plan",
            new { minutes, level, focus }, token));

    public Task<MealPlan> MealPlan(string uid, string token, string goal,
                                   int days) =>
        Send<MealPlan>(Post($"/nutrition/{uid}/plan",
            new { goal, preferences = Array.Empty<string>(), days }, token));

    /// Ambient watching: an ordinary activity is context, not a reading.
    public Task<ActivityWatch> ObserveActivity(string uid, string token,
                                               string activity, string note) =>
        Send<ActivityWatch>(Post($"/activity/{uid}",
            note is { Length: > 0 }
                ? new { activity, note }
                : (object)new { activity }, token));

    public Task<ConditionsKnown> DeclareCondition(string uid, string token,
                                                  string condition,
                                                  string note) =>
        Send<ConditionsKnown>(Post($"/conditions/{uid}",
            note is { Length: > 0 }
                ? new { condition, note }
                : (object)new { condition }, token));

    public Task<PersonalitySaved> SetPersonality(string uid, string token,
                                                 string tone) =>
        Send<PersonalitySaved>(Put($"/personality/{uid}", new { tone }, token));

    /// The server checks the consent, not this shell.
    public Task<ContextAdded> GiveContext(string uid, string token,
                                          string source, string kind) =>
        Send<ContextAdded>(Post($"/context/{uid}",
            new { source, kind, data = new { title = "something on the calendar" } },
            token));

    public Task<Goal> UpdateGoal(string uid, string token, string goalId,
                                 double progress, string status) =>
        Send<Goal>(new HttpRequestMessage(HttpMethod.Patch,
            $"/goals/{uid}/{goalId}")
        { Content = JsonContent.Create(new { progress, status }) }, token);

    public Task<InsightRow[]> Insights(string uid, string token) =>
        Send<InsightRow[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/insights/{uid}"), token);

    public Task<EventRow[]> Events(string uid, string token) =>
        Send<EventRow[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/events/{uid}"), token);

    public Task<ProgressReport> ProgressReport(string uid, string token) =>
        Send<ProgressReport>(new HttpRequestMessage(HttpMethod.Get,
            $"/report/{uid}"), token);

    /// An ambient, unprompted word from the coach.
    public Task<CompanionSaid> CompanionCheckin(string uid, string token) =>
        Send<CompanionSaid>(Post($"/companion/{uid}", new { }, token));

    public Task<FeedbackSaved> SendGuidanceFeedback(string uid, string token,
                                                    string rating) =>
        Send<FeedbackSaved>(Post($"/feedback/{uid}", new { rating }, token));

    public Task<CoachExchange[]> CoachHistory(string uid, string token) =>
        Send<CoachExchange[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/coach/{uid}"), token);

    // ---- the specialist economy ----

    public Task<SpecialistRow[]> Specialists() =>
        Send<SpecialistRow[]>(new HttpRequestMessage(HttpMethod.Get,
            "/specialists"));

    public Task<SpecialistsSeeded> SeedSpecialists() =>
        Send<SpecialistsSeeded>(Post("/specialists/seed", new { }));

    public Task<SpecialistsSeeded> SeedTandemSpecialists() =>
        Send<SpecialistsSeeded>(Post("/specialists/seed/tandem", new { }));

    public Task<SpecialistCatalog> SpecialistsCatalog() =>
        Send<SpecialistCatalog>(new HttpRequestMessage(HttpMethod.Get,
            "/specialists/catalog"));

    /// <summary>Anyone on QRME, not only the thirty-four on the shelf.
    /// Takes a <c>@handle</c>, a <c>prof_…</c> id, or words.</summary>
    public Task<SpecialistSearch> SearchSpecialists(string query) =>
        Send<SpecialistSearch>(new HttpRequestMessage(HttpMethod.Get,
            "/specialists/search?q=" + Uri.EscapeDataString(query)));

    public Task<SpecialistRow> AttachSpecialist(string condition,
                                                string qrmeProfileId,
                                                string label) =>
        Send<SpecialistRow>(Post("/specialists",
            new { condition, mode = "tandem",
                  qrme_profile_id = qrmeProfileId, label }));

    public Task<ClinicianSearch> ReferralClinicians(string uid, string token,
                                                    string condition) =>
        Send<ClinicianSearch>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/referral/clinicians?condition={condition}"), token);

    /// Nothing is released by preparing — the signing ceremony is QRME's.
    public Task<ReferralPrepared> PrepareReferral(string uid, string token,
                                                  string condition,
                                                  string providerId) =>
        Send<ReferralPrepared>(Post($"/users/{uid}/referral/prepare",
            new { condition, provider_id = providerId }, token));

    /// A report, not an action: JIM cannot observe QRME's ceremony.
    public Task<ReferralReleased> MarkReferralReleased(string uid, string token,
                                                       string requestId) =>
        Send<ReferralReleased>(Post(
            $"/users/{uid}/referral/requests/{requestId}/released",
            new { }, token));

    public Task<ReferralRequestRow[]> ReferralRequests(string uid,
                                                       string token) =>
        Send<ReferralRequestRow[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/referral/requests"), token);

    /// A refusal is started:false with a reason — information, not a fault.
    public Task<SpecialistTaskStarted> StartSpecialistTask(string uid,
                                                           string token,
                                                           string condition,
                                                           string goal) =>
        Send<SpecialistTaskStarted>(Post($"/users/{uid}/specialist-tasks",
            new { condition, goal }, token));

    public Task<SpecialistTaskRow[]> SpecialistTasks(string uid, string token) =>
        Send<SpecialistTaskRow[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/specialist-tasks"), token);

    public Task<SpecialistTaskView> SpecialistTask(string uid, string token,
                                                   string taskId) =>
        Send<SpecialistTaskView>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/specialist-tasks/{taskId}"), token);

    public Task<SpecialistTaskView> AdvanceSpecialistTask(string uid,
                                                          string token,
                                                          string taskId) =>
        Send<SpecialistTaskView>(Post(
            $"/users/{uid}/specialist-tasks/{taskId}/advance", new { }, token));

    /// What a consented care provider sees — and so what the person can see
    /// that they see.
    public Task<ProviderSummary> ProviderSummary(string uid, string token) =>
        Send<ProviderSummary>(new HttpRequestMessage(HttpMethod.Get,
            $"/provider/{uid}"), token);

    // ---- the record and the veil ----

    /// An empty list with no record kept is a different fact from nobody
    /// having looked, and the shape says which.
    public Task<AccessLog> AccessLog(string uid, string token) =>
        Send<AccessLog>(new HttpRequestMessage(HttpMethod.Get,
            $"/access-log/{uid}"), token);

    public Task<AuditLog> AuditLog(string uid, string token) =>
        Send<AuditLog>(new HttpRequestMessage(HttpMethod.Get,
            $"/audit/{uid}"), token);

    public Task<CloudStatus> CloudStatus() =>
        Send<CloudStatus>(new HttpRequestMessage(HttpMethod.Get,
            "/cloud/status"));

    public Task<ContributionView> CloudContribution(string uid, string token) =>
        Send<ContributionView>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/cloud-contribution"), token);

    public Task<ContributionRevoked> RevokeCloudContribution(string uid,
                                                             string token) =>
        Send<ContributionRevoked>(Post(
            $"/users/{uid}/cloud-contribution/revoke", new { }, token));

    /// Open, unaccepted alarms on this account's site beacons.
    public Task<IncidentRow[]> Incidents(string uid, string token) =>
        Send<IncidentRow[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/incidents"), token);

    /// Escalations and whether each reached anyone.
    public Task<PageRow[]> Pages(string uid, string token) =>
        Send<PageRow[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/pages"), token);

    /// Used only to find local rooms and events through the community door.
    public Task<LocalitySaved> SetLocality(string uid, string token,
                                           string locality) =>
        Send<LocalitySaved>(Put($"/users/{uid}/locality",
            new { locality }, token));

    public Task<PlansOut> Plans() =>
        Send<PlansOut>(new HttpRequestMessage(HttpMethod.Get, "/plans"));

    // ---- the purse and the membership ----

    public Task<BudgetsOut> Budgets(string uid, string token) =>
        Send<BudgetsOut>(new HttpRequestMessage(HttpMethod.Get,
            $"/budgets/{uid}"), token);

    /// This much per month for this category.
    public Task<BudgetRow> SetBudget(string uid, string token,
                                     string category, double monthlyLimit) =>
        Send<BudgetRow>(Put($"/budgets/{uid}",
            new { category, monthly_limit = monthlyLimit }, token));

    public Task<BudgetRemoved> ClearBudget(string uid, string token,
                                           string category) =>
        Send<BudgetRemoved>(new HttpRequestMessage(HttpMethod.Delete,
            $"/budgets/{uid}/{category}"), token);

    /// The route says account and means the person: tiers are keyed by the
    /// user id, and the bearer must be that user's own.
    public Task<MembershipView> Membership(string uid, string token) =>
        Send<MembershipView>(new HttpRequestMessage(HttpMethod.Get,
            $"/memberships/{uid}"), token);

    /// Join a plan or move between them. Billing is simulated.
    public Task<MembershipView> Subscribe(string uid, string token,
                                          string plan) =>
        Send<MembershipView>(Post($"/memberships/{uid}", new { plan }, token));

    /// End it. The person keeps their record and every emergency path.
    public Task<MembershipView> CancelMembership(string uid, string token) =>
        Send<MembershipView>(new HttpRequestMessage(HttpMethod.Delete,
            $"/memberships/{uid}"), token);

    // ---- the sticker and the relay ----

    /// A sticker someone can scan to reach help on your behalf.
    public Task<BeaconRow[]> Beacons(string uid, string token) =>
        Send<BeaconRow[]>(new HttpRequestMessage(HttpMethod.Get,
            $"/users/{uid}/beacons"), token);

    public Task<BeaconRow> PlaceBeacon(string uid, string token, string label,
                                       string placement) =>
        Send<BeaconRow>(Post($"/users/{uid}/beacons",
            placement is { Length: > 0 }
                ? new { kind = "site", label, placement }
                : (object)new { kind = "site", label }, token));

    public Task<BeaconRetired> RetireBeacon(string bid, string token) =>
        Send<BeaconRetired>(new HttpRequestMessage(HttpMethod.Delete,
            $"/beacons/{bid}"), token);

    /// What a stranger sees before deciding to raise the alarm — public on
    /// purpose, the scanner has no account.
    public Task<BeaconCardOut> BeaconCard(string bid) =>
        Send<BeaconCardOut>(new HttpRequestMessage(HttpMethod.Get,
            $"/c/{bid}/card"));

    public Task<BeaconAlarm> RaiseBeaconAlarm(string bid) =>
        Send<BeaconAlarm>(Post($"/c/{bid}/alarm", new { }));

    /// The scanned page itself is HTML for a stranger's browser; fetching it
    /// proves the door is live before handing it to the system one.
    public async Task<BeaconPage> ScannedBeaconPage(string bid)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/c/{bid}");
        var res = await Dispatch(req);
        var html = await res.Content.ReadAsStringAsync();
        var page = res.RequestMessage?.RequestUri
                   ?? new Uri(Base, req.RequestUri!.ToString());
        return new BeaconPage(html, page);
    }

    // ---- safe knowledge excursions + the community window ----

    public Task<ExcursionRow[]> Excursions(string uid, string token) =>
        Send<ExcursionRow[]>(Get($"/excursions/{uid}", token));

    /// <summary>Study a topic without carrying the person's PHI out; the
    /// row answers with the redaction count and whether it left this host.</summary>
    public Task<ExcursionRow> StartExcursion(string uid, string token,
                                             string topic, string question) =>
        Send<ExcursionRow>(Post($"/excursions/{uid}",
            new { topic, question }, token));

    public Task<ExcursionRow> ExcursionEntry(string cid, string token) =>
        Send<ExcursionRow>(Get($"/excursions/entry/{cid}", token));

    /// <summary>Fold the findings into guidance context; the local model
    /// uses them from then on.</summary>
    public Task<ExcursionLearned> LearnExcursion(string cid, string token) =>
        Send<ExcursionLearned>(Post($"/excursions/entry/{cid}/learn",
            new { }, token));

    public Task<CommunityVisitRow[]> CommunityVisits(string uid, string token) =>
        Send<CommunityVisitRow[]>(Get($"/community/{uid}/visits", token));

    public Task<CommunityFeedView> CommunityFeed(string uid, string token) =>
        Send<CommunityFeedView>(Get($"/community/{uid}/feed", token));

    // ---- the voice pair: say it aloud, and hear what was said ----

    /// <summary>Text in, audio out. A deployment with no speaking service
    /// answers 503 — the card falls back to the device's own voice,
    /// because silence would be the wrong failure.</summary>
    public async Task<byte[]> SpeakAloud(string text)
    {
        var req = Post("/voice/speak", new { text }, null);
        var res = await Dispatch(req);
        if (!res.IsSuccessStatusCode)
            throw new HttpRequestException(await res.Content.ReadAsStringAsync());
        return await res.Content.ReadAsByteArrayAsync();
    }

    /// <summary>Recorded speech in, words out. The audio is not stored
    /// server-side.</summary>
    public Task<Transcribed> Transcribe(string audioBase64, string filename) =>
        Send<Transcribed>(Post("/voice/transcribe",
            new { audio_base64 = audioBase64, filename }, null));

    /// <summary>The backend's own pulse, and whether a QRME tandem stands
    /// behind it.</summary>
    public Task<HealthOut> Health() =>
        Send<HealthOut>(new HttpRequestMessage(HttpMethod.Get, "/health"));

    public Task<RelayChannel> RelayChannel() =>
        Send<RelayChannel>(new HttpRequestMessage(HttpMethod.Get,
            "/relay/channel"));

    public Task<RelayRoster> RelayRoster() =>
        Send<RelayRoster>(new HttpRequestMessage(HttpMethod.Get,
            "/relay/roster"));

    public Task<RelayRota> RelayRota() =>
        Send<RelayRota>(new HttpRequestMessage(HttpMethod.Get,
            "/relay/rota"));

    public Task<SocialBeacon> SocialBeacon(string cid, string token) =>
        Send<SocialBeacon>(new HttpRequestMessage(HttpMethod.Get,
            $"/social/connection/{cid}/beacon"), token);

    public Task<SocialGone> DisconnectSocial(string cid, string token) =>
        Send<SocialGone>(new HttpRequestMessage(HttpMethod.Delete,
            $"/social/connection/{cid}"), token);

    public Task<RobotUnbound> UnbindRobot(string uid, string token,
                                          string robotId) =>
        Send<RobotUnbound>(new HttpRequestMessage(HttpMethod.Delete,
            $"/robots/{uid}/{robotId}"), token);
    // -- the synced address book (jim/contacts.py) ---------------------------
    // The grant is the "contacts" source; the sync REPLACES the book, and
    // the book reads back names — never the numbers. Classic Windows holds
    // no system address book, so this shell's sync is the rows a person
    // types in.

    public sealed class BookRow
    {
        public string id { get; init; } = "";
        public string name { get; init; } = "";
        public bool has_guardian { get; init; }
    }

    public sealed class ContactBook
    {
        public List<BookRow> book { get; init; } = new();
        public int held { get; init; }
    }

    public Task SyncContacts(string uid, IEnumerable<object> entries,
                             string token) =>
        Send<JsonElement>(Put($"/contacts/{uid}", new { entries }, token));

    public Task<ContactBook> ContactsBook(string uid, string token) =>
        Send<ContactBook>(Get($"/contacts/{uid}", token));

}

public record MoneyAccount(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("institution")] string Institution,
    [property: JsonPropertyName("label")] string? Label,
    [property: JsonPropertyName("last4")] string? Last4,
    [property: JsonPropertyName("credentials")] string? Credentials,
    [property: JsonPropertyName("balance")] double? Balance);

public record SavingsGoal(
    [property: JsonPropertyName("goal_amount")] double Goal,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("reached_at")] string? ReachedAt);

// The low-balance trip line — the owner's own when Source is "user", and
// Derived is what clearing it goes back to.
public record MoneyFloor(
    [property: JsonPropertyName("floor")] double Floor,
    [property: JsonPropertyName("source")] string Source,
    [property: JsonPropertyName("derived")] double Derived);

public record MoneyMandate(
    [property: JsonPropertyName("enabled")] bool Enabled,
    [property: JsonPropertyName("scope")] string? Scope);

public record MoneyOrder(
    [property: JsonPropertyName("asset_class")] string AssetClass,
    [property: JsonPropertyName("amount")] double Amount,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("rationale")] string? Rationale);

public record MoneyDesk(
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("trade")] string? Trade,
    [property: JsonPropertyName("location")] string? Location);

public record MoneySpecialistDoor(
    [property: JsonPropertyName("label")] string? Label);

public record MoneyDoors(
    [property: JsonPropertyName("specialist_door")] MoneySpecialistDoor? Specialist,
    [property: JsonPropertyName("desks")] MoneyDesk[] Desks);

public record MoneyWarning(
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("message")] string Message,
    [property: JsonPropertyName("doors")] MoneyDoors? Doors);

public record StatementReading(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("filename")] string Filename,
    [property: JsonPropertyName("line_count")] int LineCount,
    [property: JsonPropertyName("total_in")] double TotalIn,
    [property: JsonPropertyName("total_out")] double TotalOut,
    [property: JsonPropertyName("end_balance")] double? EndBalance);

public record BankLinkOut(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("institution")] string Institution,
    [property: JsonPropertyName("aggregator")] string Aggregator,
    [property: JsonPropertyName("status")] string Status);

public record MoneyOverview(
    [property: JsonPropertyName("accounts")] MoneyAccount[] Accounts,
    [property: JsonPropertyName("savings")] SavingsGoal? Savings,
    [property: JsonPropertyName("mandate")] MoneyMandate? Mandate,
    [property: JsonPropertyName("orders")] MoneyOrder[] Orders,
    [property: JsonPropertyName("note")] string Note,
    [property: JsonPropertyName("labels")] System.Collections.Generic.Dictionary<string, string> Labels);

public record AppointmentRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("whenat")] string WhenAt,
    [property: JsonPropertyName("whereat")] string? WhereAt,
    [property: JsonPropertyName("status")] string Status);

public record ScheduleOverview(
    [property: JsonPropertyName("appointments")] AppointmentRow[] Appointments,
    [property: JsonPropertyName("email_available")] bool EmailAvailable,
    [property: JsonPropertyName("labels")] System.Collections.Generic.Dictionary<string, string> Labels,
    [property: JsonPropertyName("note")] string Note);

public record TandemShop(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("seller")] string Seller,
    [property: JsonPropertyName("tag")] string? Tag);

public record ShopReceipt(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("qrme_order_id")] string QrmeOrderId,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("amount")] double Amount,
    [property: JsonPropertyName("currency")] string Currency,
    [property: JsonPropertyName("status")] string Status);

public record ShoppingOverview(
    [property: JsonPropertyName("shops")] TandemShop[] Shops,
    [property: JsonPropertyName("receipts")] ShopReceipt[] Receipts,
    [property: JsonPropertyName("labels")] System.Collections.Generic.Dictionary<string, string> Labels,
    [property: JsonPropertyName("note")] string Note);

public record PlacedTandemOrder(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("shop_id")] string ShopId,
    [property: JsonPropertyName("status")] string Status);

public record CirclePersonRow(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("display_name")] string? DisplayName);

public record CircleThreadRow(
    [property: JsonPropertyName("other_id")] string OtherId,
    [property: JsonPropertyName("other_name")] string? OtherName,
    [property: JsonPropertyName("messages_count")] int MessagesCount);

public record CircleMessageRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("sender_id")] string SenderId,
    [property: JsonPropertyName("body")] string Body,
    [property: JsonPropertyName("sent_at")] string SentAt);

public record CircleThreadBox(
    [property: JsonPropertyName("messages")] CircleMessageRow[] Messages);

public record CircleLinkRow(
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("url")] string Url);

public record CircleThemeRow(
    [property: JsonPropertyName("bg")] string Bg,
    [property: JsonPropertyName("accent")] string Accent);

public record CircleHomepageDoc(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("headline")] string Headline,
    [property: JsonPropertyName("about")] string About,
    [property: JsonPropertyName("theme")] CircleThemeRow Theme,
    [property: JsonPropertyName("links")] CircleLinkRow[] Links,
    [property: JsonPropertyName("top_friends")] CirclePersonRow[] TopFriends,
    [property: JsonPropertyName("editable")] bool Editable);

public record CircleRing(
    [property: JsonPropertyName("contacts")] CirclePersonRow[] Contacts,
    [property: JsonPropertyName("invited_me")] CirclePersonRow[] InvitedMe,
    [property: JsonPropertyName("awaiting")] CirclePersonRow[] Awaiting);

public record CircleOverview(
    [property: JsonPropertyName("features")] System.Collections.Generic.Dictionary<string, bool> Features,
    [property: JsonPropertyName("circle")] CircleRing Circle,
    [property: JsonPropertyName("threads")] CircleThreadRow[] Threads,
    [property: JsonPropertyName("homepage")] CircleHomepageDoc Homepage,
    [property: JsonPropertyName("labels")] System.Collections.Generic.Dictionary<string, string> Labels,
    [property: JsonPropertyName("note")] string Note);

public record CircleTie(
    [property: JsonPropertyName("other_id")] string OtherId,
    [property: JsonPropertyName("state")] string State);

public record MoneyObserved(
    [property: JsonPropertyName("recorded")] bool Recorded,
    [property: JsonPropertyName("warnings")] MoneyWarning[] Warnings,
    [property: JsonPropertyName("orders_proposed")] MoneyOrder[] OrdersProposed);

public record OfflinePosture(
    [property: JsonPropertyName("offline")] bool Offline,
    [property: JsonPropertyName("external_transmission_possible")] bool ExternalTransmissionPossible,
    [property: JsonPropertyName("local_destinations_allowed")] string LocalDestinationsAllowed,
    [property: JsonPropertyName("guarantees")] string[] Guarantees);

public record MemoryMoment(
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("ref")] string Ref,
    [property: JsonPropertyName("line")] string? Line,
    [property: JsonPropertyName("at")] string? At);
public record MemoryShelf(
    [property: JsonPropertyName("memories")] MemoryMoment[] Moments,
    [property: JsonPropertyName("readable")] bool Readable,
    [property: JsonPropertyName("held")] int Held);
public record MemoryForgotten(
    [property: JsonPropertyName("forgotten")] bool Forgotten,
    [property: JsonPropertyName("why")] string? Why);

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

// The offline coach's store and syllabus (jim/pipeline.py): what the stack
// predicts from, what JIM should study next, and what one press of study did.
public record CoachStoreEntry(
    [property: JsonPropertyName("topic")] string Topic,
    [property: JsonPropertyName("lesson")] string Lesson,
    [property: JsonPropertyName("source")] string Source,
    [property: JsonPropertyName("model")] string? Model);

public record CoachStore(
    [property: JsonPropertyName("pack")] int Pack,
    [property: JsonPropertyName("excursions")] CoachStoreEntry[] Excursions,
    [property: JsonPropertyName("deposits")] CoachStoreEntry[] Deposits);

public record CoachSuggestion(
    [property: JsonPropertyName("area")] string Area,
    [property: JsonPropertyName("topic")] string Topic,
    [property: JsonPropertyName("why")] string Why);

public record CoachCurriculum(
    [property: JsonPropertyName("suggested")] CoachSuggestion[] Suggested,
    [property: JsonPropertyName("note")] string Note);

public record CoachStudied(
    [property: JsonPropertyName("studied")] string Studied,
    [property: JsonPropertyName("folded")] bool Folded);

/// <summary>A link between two guardians. <c>Task</c> is what keeps it open
/// past the call — and only once <b>both</b> sides have agreed to it. Three
/// fields rather than one flag, because "you have not agreed", "they have
/// not" and "nobody named anything" are three different things to say.
/// </summary>
public record LiaisonRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("about")] string About,
    [property: JsonPropertyName("task")] string Task,
    [property: JsonPropertyName("running")] bool Running,
    [property: JsonPropertyName("ended_because")] string? EndedBecause,
    [property: JsonPropertyName("opened_at")] string OpenedAt,
    [property: JsonPropertyName("you_agreed")] bool YouAgreed,
    [property: JsonPropertyName("they_agreed")] bool TheyAgreed,
    [property: JsonPropertyName("holds_it_open")] bool HoldsItOpen);

/// <summary>A person's own half: what theirs said, and what it was told. The
/// other person's half was never theirs to read.</summary>
public record LiaisonHalf(
    [property: JsonPropertyName("link_id")] string LinkId,
    [property: JsonPropertyName("about")] string About,
    [property: JsonPropertyName("task")] string Task,
    [property: JsonPropertyName("running")] bool Running,
    [property: JsonPropertyName("said_by_mine")] string[] SaidByMine,
    [property: JsonPropertyName("said_to_mine")] string[] SaidToMine,
    [property: JsonPropertyName("you_agreed")] bool YouAgreed,
    [property: JsonPropertyName("they_agreed")] bool TheyAgreed,
    [property: JsonPropertyName("holds_it_open")] bool HoldsItOpen);

/// <summary>One thing this guardian has running. <c>Kind</c> and <c>Why</c>
/// are closed-set words said in the reader's language by <c>L10n</c>;
/// <c>Term</c> is one of the product's own vocabulary words and <c>Words</c>
/// is what the person wrote.</summary>
public record UnderwayRow(
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("term")] string? Term,
    [property: JsonPropertyName("words")] string? Words,
    [property: JsonPropertyName("since")] string? Since,
    [property: JsonPropertyName("why")] string Why);

/// <summary>What the day's unattended study has spent, against its
/// ceiling.</summary>
public record UnderwaySpend(
    [property: JsonPropertyName("spent_today")] int SpentToday,
    [property: JsonPropertyName("daily")] int Daily,
    [property: JsonPropertyName("permitted")] bool Permitted);

/// <summary>Everything running, what it learned today, and what is left to
/// spend. <c>Quiet</c> is the server's own answer rather than one derived
/// here, so the four shells cannot disagree about what "nothing running"
/// looks like.</summary>
public record UnderwayWindow(
    [property: JsonPropertyName("underway")] UnderwayRow[] Underway,
    [property: JsonPropertyName("quiet")] bool Quiet,
    // Finished, not running — which is why it is a list of its own.
    [property: JsonPropertyName("today")] Errand[] Today,
    [property: JsonPropertyName("spend")] UnderwaySpend Spend);

/// <summary>Two people on one call, each with their own channel 2. A
/// disclosure and nothing else — their device, gain and what they hear were
/// never this person's to read and are not here.</summary>
public record MicPaired(
    [property: JsonPropertyName("paired")] bool Paired,
    [property: JsonPropertyName("with")] string? With,
    [property: JsonPropertyName("yours_listening")] bool YoursListening,
    [property: JsonPropertyName("theirs_listening")] bool TheirsListening,
    [property: JsonPropertyName("both")] bool Both);

/// <summary>A cue read off a camera or a speaker. Read on the way through,
/// never out of anything kept, and the words it was read from are never
/// carried.</summary>
public record Cue(
    [property: JsonPropertyName("cue")] string Which,
    [property: JsonPropertyName("severity")] string Severity,
    [property: JsonPropertyName("says")] string Says,
    [property: JsonPropertyName("monitor")] string Monitor,
    [property: JsonPropertyName("reference")] string Reference,
    [property: JsonPropertyName("tier")] string Tier,
    [property: JsonPropertyName("at")] string At);

/// <summary>What was noticed, and what each monitor could ever notice from
/// its own senses.</summary>
public record CuesSeen(
    [property: JsonPropertyName("lately")] Cue[] Lately,
    [property: JsonPropertyName("can_read")]
        Dictionary<string, string[]> CanRead);

/// <summary>One moment a monitor took something in. <c>Kept</c> is false for
/// most of what is sensed, and the day's rows say which promise stopped it.
/// </summary>
public record Moment(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("monitor")] string Monitor,
    [property: JsonPropertyName("content")] string Content,
    [property: JsonPropertyName("stretch_id")] string? StretchId,
    [property: JsonPropertyName("sensed_at")] string SensedAt);

/// <summary>One monitor's day. <c>Because</c> is a list — keeping switched
/// off in the morning and on by the afternoon is ordinary.</summary>
public record MonitorDay(
    [property: JsonPropertyName("monitor")] string Monitor,
    [property: JsonPropertyName("sensed")] int Sensed,
    [property: JsonPropertyName("kept")] int Kept,
    [property: JsonPropertyName("dropped")] int Dropped,
    [property: JsonPropertyName("because")] string[] Because,
    [property: JsonPropertyName("holds")] string Holds);

public record DayAccount(
    [property: JsonPropertyName("date")] string Date,
    [property: JsonPropertyName("monitors")] MonitorDay[] Monitors,
    [property: JsonPropertyName("sensed")] int Sensed,
    [property: JsonPropertyName("kept")] int Kept,
    [property: JsonPropertyName("quiet")] bool Quiet);

/// <summary>A meeting, a call, or a working stretch. <c>OthersTold</c> is
/// the same claim switching the monitor on demands, asked again.</summary>
public record Stretch(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("monitor")] string Monitor,
    [property: JsonPropertyName("about")] string About,
    [property: JsonPropertyName("others_told")] bool OthersTold,
    [property: JsonPropertyName("catches_others")] bool CatchesOthers,
    [property: JsonPropertyName("running")] bool Running,
    [property: JsonPropertyName("opened_at")] string OpenedAt,
    [property: JsonPropertyName("ended_at")] string? EndedAt,
    [property: JsonPropertyName("moments")] int Moments,
    [property: JsonPropertyName("kept")] int Kept);

public record HeartbeatSkew(
    [property: JsonPropertyName("skew_ms")] double? SkewMs);

public record FreshnessFacts(
    [property: JsonPropertyName("verdict")] string Verdict,
    [property: JsonPropertyName("reading_age_ms")] double? ReadingAgeMs,
    [property: JsonPropertyName("heartbeat_age_ms")] double? HeartbeatAgeMs);

public record TheDay(
    [property: JsonPropertyName("account")] DayAccount Account,
    [property: JsonPropertyName("survived")] Moment[] Survived,
    [property: JsonPropertyName("stretches")] Stretch[] Stretches);

/// <summary>One thing that can be plugged in and sense somebody.
/// <c>CatchesOthers</c> is the field that decides everything else: nothing
/// carrying it is ever on by default, and switching one on is refused until
/// the people in that space have been told.</summary>
public record MonitorRow(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("senses")] string[] Senses,
    [property: JsonPropertyName("placing")] string Placing,
    [property: JsonPropertyName("says")] string Says,
    [property: JsonPropertyName("holds")] string Holds,
    [property: JsonPropertyName("catches_others")] bool CatchesOthers,
    [property: JsonPropertyName("on")] bool On,
    [property: JsonPropertyName("device")] string? Device,
    [property: JsonPropertyName("others_told")] bool OthersTold,
    [property: JsonPropertyName("keeping")] bool Keeping);

/// <summary>One part of the notice: the support-line script in a language the
/// far side might actually speak. More than one where the mix is
/// known.</summary>
public record CallNotice(
    [property: JsonPropertyName("language")] string Language,
    [property: JsonPropertyName("words")] string Words);

public record AssistedCall(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("listening")] bool Listening,
    [property: JsonPropertyName("route")] string Route,
    [property: JsonPropertyName("recording")] bool Recording,
    [property: JsonPropertyName("notices")] CallNotice[] Notices,
    [property: JsonPropertyName("said")] string Said,
    [property: JsonPropertyName("spoken_in")] string[] SpokenIn,
    [property: JsonPropertyName("language_from")] string LanguageFrom);

public record CallRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("route")] string Route,
    [property: JsonPropertyName("said")] string Said,
    [property: JsonPropertyName("spoken_in")] string[] SpokenIn,
    [property: JsonPropertyName("announced_at")] string? AnnouncedAt,
    [property: JsonPropertyName("listened")] bool Listened,
    [property: JsonPropertyName("opened_at")] string OpenedAt);

/// <summary>One remark on a draft. <c>Because</c> is the evidence it came
/// from; <c>Door</c> is set only on an offer, and only ever names a screen
/// this product has.</summary>
public record Remark(
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("says")] string Says,
    [property: JsonPropertyName("because")] string[] Because,
    [property: JsonPropertyName("door")] string? Door);

/// <summary><c>QuietBecause</c> carries the reason there is nothing to say —
/// an empty list on its own cannot tell somebody <i>nothing to add</i> from
/// <i>it did not run</i>.</summary>
public record Alongside(
    [property: JsonPropertyName("remarks")] Remark[] Remarks,
    [property: JsonPropertyName("quiet_because")] string? QuietBecause);

/// <summary>One errand: a topic the offline coach could not answer, gone and
/// studied. <c>Why</c> names the monitor that asked for it.</summary>
public record Errand(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("topic")] string Topic,
    [property: JsonPropertyName("area")] string Area,
    [property: JsonPropertyName("why")] string Why,
    [property: JsonPropertyName("excursion_id")] string ExcursionId,
    [property: JsonPropertyName("redactions")] int Redactions,
    [property: JsonPropertyName("left_host")] bool LeftHost,
    [property: JsonPropertyName("opened_at")] string OpenedAt);

/// <summary>An empty ledger has three causes — nothing worth studying,
/// nothing left to spend today, nobody ever allowed it — so all three are on
/// the wire.</summary>
public record ErrandLedger(
    // `errands`, not `studied`: the study route's `studied` is the name of one
    // topic, and one wire name carries one type.
    [property: JsonPropertyName("errands")] Errand[] Errands,
    [property: JsonPropertyName("due")] CoachSuggestion[] Due,
    [property: JsonPropertyName("spent_today")] int SpentToday,
    [property: JsonPropertyName("daily")] int Daily,
    [property: JsonPropertyName("permitted")] bool Permitted);

public record ErrandsRun(
    [property: JsonPropertyName("errands")] Errand[] Errands,
    [property: JsonPropertyName("remaining_today")] int RemainingToday,
    [property: JsonPropertyName("nothing_to_study")] bool NothingToStudy);

/// <summary>What the coach noticed, and which half of the ladder settled it.
/// <c>SettledBy</c> is the column worth reading: <c>coach</c> cost nothing,
/// <c>jim</c> cost one of the day's shared turns.</summary>
public record Notice(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("event_id")] string EventId,
    [property: JsonPropertyName("condition")] string Condition,
    [property: JsonPropertyName("severity")] string Severity,
    [property: JsonPropertyName("settled_by")] string SettledBy,
    [property: JsonPropertyName("said")] string Said,
    [property: JsonPropertyName("noticed_at")] string NoticedAt);

public record NoticeDue(
    [property: JsonPropertyName("event_id")] string EventId,
    [property: JsonPropertyName("condition")] string Condition,
    [property: JsonPropertyName("severity")] string Severity,
    [property: JsonPropertyName("noticed_at")] string NoticedAt);

/// <summary>Of everything handled unattended, how much the free half
/// carried. <c>FreeShare</c> is null rather than 0 when nothing has been
/// handled — a bare 0% would say the coach settled none of them.</summary>
public record NoticeSettlement(
    [property: JsonPropertyName("settled_free")] int SettledFree,
    [property: JsonPropertyName("settled_paid")] int SettledPaid,
    [property: JsonPropertyName("free_share")] double? FreeShare,
    [property: JsonPropertyName("permitted")] bool Permitted,
    [property: JsonPropertyName("spent_today")] int SpentToday,
    [property: JsonPropertyName("daily")] int Daily);

public record NoticeLedger(
    [property: JsonPropertyName("handled")] Notice[] Handled,
    [property: JsonPropertyName("waiting")] NoticeDue[] Waiting,
    [property: JsonPropertyName("settlement")] NoticeSettlement Settlement);

public record NoticeBlocked(
    [property: JsonPropertyName("event_id")] string EventId,
    [property: JsonPropertyName("condition")] string Condition);

/// <summary>A spent budget is reported, never refused: the free half is
/// still worth running, so <c>OverBudget</c> names what waits for tomorrow
/// rather than the pass answering 429.</summary>
public record NoticedRun(
    [property: JsonPropertyName("by_coach")] Notice[] ByCoach,
    [property: JsonPropertyName("by_jim")] Notice[] ByJim,
    [property: JsonPropertyName("over_budget")] NoticeBlocked[] OverBudget,
    [property: JsonPropertyName("remaining_today")] int RemainingToday,
    [property: JsonPropertyName("nothing_noticed")] bool NothingNoticed);

public record SpecialistAnswer(
    [property: JsonPropertyName("delivered")] bool Delivered,
    [property: JsonPropertyName("content")] string? Content,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("held_for_owner_approval")] bool HeldForOwnerApproval,
    [property: JsonPropertyName("specialist_who")] SpecialistWho? Specialist,
    [property: JsonPropertyName("answer_provenance")] SpecialistProvenance? Provenance);

public record CarePlanRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("goal")] string Goal,
    [property: JsonPropertyName("plan")] string? Plan,
    [property: JsonPropertyName("sealed_in_qrme_vault")] bool SealedInQrmeVault,
    [property: JsonPropertyName("created_at")] string? CreatedAt);

public record CareTeamState(
    [property: JsonPropertyName("linked")] bool Linked,
    [property: JsonPropertyName("org_id")] string? OrgId,
    [property: JsonPropertyName("department_id")] string? DepartmentId,
    [property: JsonPropertyName("latest_plan")] CarePlanRow? LatestPlan);

/// Channel 2's current state. `capped` means a call is in progress and the
/// agent has narrowed itself regardless of the owner's setting.
public record MicState(
    [property: JsonPropertyName("listening")] bool Listening,
    [property: JsonPropertyName("attached")] bool Attached,
    [property: JsonPropertyName("device")] string? Device,
    [property: JsonPropertyName("mic_type")] string? MicType,
    [property: JsonPropertyName("gain")] string? Gain,
    [property: JsonPropertyName("capped")] bool Capped,
    [property: JsonPropertyName("hears")] string? Hears,
    // unattached | silent | carrying — attached is a permission, and a
    // channel that has never delivered is not one that is listening.
    [property: JsonPropertyName("standing")] string? Standing,
    [property: JsonPropertyName("last_heard")] string? LastHeard,
    [property: JsonPropertyName("note")] string? Note);

/// What channel 2 handed in.
public record MicHeard(
    [property: JsonPropertyName("heard")] string? Heard,
    [property: JsonPropertyName("device")] string? Device,
    [property: JsonPropertyName("reason")] string? Reason);

public record MicEventRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("device")] string Device,
    [property: JsonPropertyName("mic_type")] string MicType,
    [property: JsonPropertyName("gain")] string Gain,
    [property: JsonPropertyName("live")] bool Live,
    [property: JsonPropertyName("started_at")] string StartedAt);

public record MicTypeChoices(
    [property: JsonPropertyName("personal")] string[] Personal,
    [property: JsonPropertyName("ambient")] string[] Ambient,
    [property: JsonPropertyName("rule")] string? Rule);

public record MicGainLevel(
    [property: JsonPropertyName("gain")] string Gain,
    [property: JsonPropertyName("reaches_others")] bool ReachesOthers,
    [property: JsonPropertyName("describes")] string? Describes);

public record MicGainChoices(
    [property: JsonPropertyName("levels")] MicGainLevel[] Levels,
    [property: JsonPropertyName("default")] string Default,
    [property: JsonPropertyName("rule")] string? Rule);

public record CaptureVocabulary(
    [property: JsonPropertyName("kinds")] Dictionary<string, string> Kinds,
    [property: JsonPropertyName("sites")] Dictionary<string, string> Sites,
    [property: JsonPropertyName("intimate_sites")] string[] IntimateSites,
    [property: JsonPropertyName("vault_required")] bool VaultRequired);

public record CaptureRecord(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("site")] string Site,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("intimate")] bool Intimate,
    [property: JsonPropertyName("created_at")] string? CreatedAt);

public record CaptureImageRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("content")] string Content);

public record CaptureAttachOutcome(
    [property: JsonPropertyName("release")] string[]? Release,
    [property: JsonPropertyName("explicit")] string[]? Explicit);

/// One dose slot of a scheduled medication:
/// taken | skipped | upcoming | due | missed.
public record MedSlot(
    [property: JsonPropertyName("slot")] string Slot,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("note")] string? Note);

/// A medication on today's board. Scheduled rows carry Slots; as-needed
/// rows carry TakenToday and MaxPerDay instead — the same union the
/// console renders.
public record MedRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("dose")] string Dose,
    [property: JsonPropertyName("purpose")] string? Purpose,
    [property: JsonPropertyName("critical")] bool Critical,
    [property: JsonPropertyName("notes")] string? Notes,
    [property: JsonPropertyName("archived")] bool Archived,
    [property: JsonPropertyName("created_at")] string? CreatedAt,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("slots")] MedSlot[]? Slots,
    [property: JsonPropertyName("taken_today")] int? TakenToday,
    [property: JsonPropertyName("max_per_day")] int? MaxPerDay);

public record MissedDose(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("slot")] string Slot);

public record MedsBoard(
    [property: JsonPropertyName("date")] string Date,
    [property: JsonPropertyName("medications")] MedRow[] Medications,
    [property: JsonPropertyName("missed_critical")] MissedDose[] MissedCritical,
    [property: JsonPropertyName("disclaimer")] string Disclaimer);

public record AdherenceRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("expected")] int Expected,
    [property: JsonPropertyName("taken")] int Taken,
    [property: JsonPropertyName("rate")] double? Rate);

public record MedAdherence(
    [property: JsonPropertyName("window_days")] int WindowDays,
    [property: JsonPropertyName("adherence_rows")] AdherenceRow[] Medications);

/// The vigil's whole answer. Until armed the route says {"armed": false}
/// and nothing else, which is why everything past Armed is nullable.
public record VigilState(
    [property: JsonPropertyName("armed")] bool Armed,
    [property: JsonPropertyName("steward_name")] string? StewardName,
    [property: JsonPropertyName("steward_channel")] string? StewardChannel,
    [property: JsonPropertyName("quiet_days")] double? QuietDays,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("last_heard_at")] string? LastHeardAt,
    [property: JsonPropertyName("silent_hours")] double? SilentHours,
    [property: JsonPropertyName("threshold_hours")] double? ThresholdHours,
    [property: JsonPropertyName("tripped")] bool? Tripped,
    [property: JsonPropertyName("tripped_at")] string? TrippedAt,
    [property: JsonPropertyName("resolved_at")] string? ResolvedAt);

/// One metric's band: the learned baseline and where the edges sit. Edges
/// are null until the baseline stops being provisional.
public record BandRow(
    [property: JsonPropertyName("metric")] string Metric,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("unit")] string Unit,
    [property: JsonPropertyName("margin")] double Margin,
    [property: JsonPropertyName("watch_high")] bool WatchHigh,
    [property: JsonPropertyName("watch_low")] bool WatchLow,
    [property: JsonPropertyName("source")] string Source,
    [property: JsonPropertyName("baseline")] double? Baseline,
    [property: JsonPropertyName("samples")] int Samples,
    [property: JsonPropertyName("provisional")] bool Provisional,
    [property: JsonPropertyName("low_edge")] double? LowEdge,
    [property: JsonPropertyName("high_edge")] double? HighEdge);

public record BandsOverview(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("sensitivity")] string Sensitivity,
    [property: JsonPropertyName("bands")] BandRow[] Bands);

public record VoiceRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("gender")] string Gender,
    [property: JsonPropertyName("note")] string Note);

/// What the API may say about the voice — never the key itself.
public record VoiceSettingsOut(
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("voice_id")] string? VoiceId,
    [property: JsonPropertyName("speak_replies")] bool SpeakReplies,
    [property: JsonPropertyName("key_set")] bool KeySet,
    [property: JsonPropertyName("key_source")] string KeySource,
    [property: JsonPropertyName("voices")] VoiceRow[] Voices,
    [property: JsonPropertyName("device_fallback")] bool DeviceFallback);

/// The verdict on a saved speaking key.
///
/// `Verdict` is the key, not the sentence — it travels on the wire so each
/// client renders it from its own table. `Detail` is the English behind it,
/// for a verdict this shell has no row for yet.
public record VoiceKeyCheckOut(
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("ok")] bool Ok,
    [property: JsonPropertyName("checked")] bool Checked,
    [property: JsonPropertyName("verdict")] string Verdict,
    [property: JsonPropertyName("detail")] string Detail);

/// What is left of the speaking allowance.
///
/// `Used` is what has been *spent* — the provider's own field is named
/// `character_count`, which reads like a balance and is not one. The
/// backend does the subtraction and floors it at zero, because a spent
/// account reports a count above its limit.
public record VoiceQuotaOut(
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("tier")] string? Tier,
    [property: JsonPropertyName("used")] int Used,
    [property: JsonPropertyName("limit")] int Limit,
    [property: JsonPropertyName("left")] int Left,
    [property: JsonPropertyName("exhausted")] bool Exhausted,
    [property: JsonPropertyName("resets_at")] string? ResetsAt);

/// The mail configuration — never the password, only whether one is set.
/// The far end as the backend says it may be shown: configured or the
/// refusal, never the token.
public record FarEndOut(
    [property: JsonPropertyName("configured")] bool Configured,
    [property: JsonPropertyName("address")] string? Address,
    [property: JsonPropertyName("note")] string? Note);

public record WidgetOut(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("source")] string Source);

public record WidgetListOut(
    [property: JsonPropertyName("widgets")] WidgetOut[] Widgets);

public record WidgetRemovedOut(
    [property: JsonPropertyName("removed")] bool Removed);

/// A failed widget is a 200 carrying `status: error` — the call worked,
/// the code did not (the route's own words).
public record WidgetRanOut(
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("detail")] string? Detail,
    [property: JsonPropertyName("ms")] int? Ms);

/// What the box can do here, and the honest reason when it cannot.
public record StudioLimitsOut(
    [property: JsonPropertyName("available")] bool Available,
    [property: JsonPropertyName("unavailable_because")] string? UnavailableBecause);

public record MailSettingsOut(
    [property: JsonPropertyName("transport")] string Transport,
    [property: JsonPropertyName("source")] string Source,
    [property: JsonPropertyName("host")] string? Host,
    [property: JsonPropertyName("port")] int Port,
    [property: JsonPropertyName("username")] string? Username,
    [property: JsonPropertyName("sender")] string? Sender,
    [property: JsonPropertyName("public_url")] string PublicUrl,
    [property: JsonPropertyName("password_set")] bool PasswordSet);

public record MailTestOut(
    [property: JsonPropertyName("sent")] bool Sent,
    [property: JsonPropertyName("to")] string To);

/// One lesson, text mode: `what` and `screens` are present.
public record TutorialStep(
    [property: JsonPropertyName("key")] string Key,
    [property: JsonPropertyName("chapter")] string Chapter,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("try_it")] string TryIt,
    [property: JsonPropertyName("mode")] string Mode,
    [property: JsonPropertyName("what")] string? What,
    [property: JsonPropertyName("screens")] int[]? Screens);

public record TutorialChapter(
    [property: JsonPropertyName("chapter")] string Chapter,
    [property: JsonPropertyName("lessons")] TutorialStep[] Steps);

/// The whole walkthrough. The count now has its own wire name
/// (`lessons_count`) and the chapter's list is `lessons` — the tally and
/// the list stopped sharing a name when the collision record closed.
public record TutorialOutline(
    [property: JsonPropertyName("guide")] string Guide,
    [property: JsonPropertyName("chapters")] TutorialChapter[] Chapters);

public record TutorialProgress(
    [property: JsonPropertyName("learner_id")] string LearnerId,
    [property: JsonPropertyName("guide")] string Guide,
    [property: JsonPropertyName("next_lesson")] TutorialStep? Step,
    [property: JsonPropertyName("done")] int Done,
    [property: JsonPropertyName("total")] int Total,
    [property: JsonPropertyName("finished")] bool Finished,
    [property: JsonPropertyName("note")] string Note);

public record HelpTopics(
    [property: JsonPropertyName("topics")] string[] Topics,
    [property: JsonPropertyName("disclosure")] string Disclosure);

public record HelpAnswer(
    [property: JsonPropertyName("answer")] string Answer,
    [property: JsonPropertyName("source")] string Source,
    [property: JsonPropertyName("ai")] bool Ai,
    [property: JsonPropertyName("disclosure")] string Disclosure);

/// Everything needed to draw the pane. `faces` is a name-to-description
/// table here and a chosen-names list on the per-user settings — recorded
/// in wire_name_collisions, both being the wire's own words since 0.19.x.
public record DockVocabulary(
    [property: JsonPropertyName("faces")] Dictionary<string, string> Faces,
    [property: JsonPropertyName("corners")] Dictionary<string, string> Corners,
    [property: JsonPropertyName("states")] Dictionary<string, string> States,
    [property: JsonPropertyName("per_surface")] string[] PerSurface,
    [property: JsonPropertyName("acts")] bool Acts);

public record DockState(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("corner")] string Corner,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("face")] string? Face,
    [property: JsonPropertyName("chosen_faces")] string[] Faces,
    [property: JsonPropertyName("set")] bool Chosen,
    [property: JsonPropertyName("wanted")] string Wanted,
    [property: JsonPropertyName("forced")] bool Forced,
    [property: JsonPropertyName("why")] string? Why);

public record DockFace(
    [property: JsonPropertyName("face")] string Face,
    [property: JsonPropertyName("shows")] string Shows,
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("surface_id")] string? SurfaceId,
    [property: JsonPropertyName("acts")] bool Acts,
    [property: JsonPropertyName("never")] string[] Never);

public record DockWhere(
    [property: JsonPropertyName("face")] string Face,
    [property: JsonPropertyName("screen")] int Screen,
    [property: JsonPropertyName("path")] string Path,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("opens_dock_face")] string OpensDockFace);

public record WatchDeviceRow(
    [property: JsonPropertyName("key")] string Key,
    [property: JsonPropertyName("name")] string Name);

/// The setup card: drip URL, this device's recipe, arrivals so far.
public record DripAck(
    [property: JsonPropertyName("received")] int Received,
    [property: JsonPropertyName("noticed")] bool Noticed);

public record WatchSetup(
    [property: JsonPropertyName("drip_url")] string DripUrl,
    [property: JsonPropertyName("phone_reachable")] bool PhoneReachable,
    [property: JsonPropertyName("last_drip_at")] string? LastDripAt,
    [property: JsonPropertyName("drips")] int Drips,
    [property: JsonPropertyName("device")] string Device,
    [property: JsonPropertyName("devices")] WatchDeviceRow[] Devices,
    [property: JsonPropertyName("steps")] string[] Steps,
    [property: JsonPropertyName("seed_hint")] string SeedHint);

/// The local pairing card — the console's URL on this network.
public record PairInfo(
    [property: JsonPropertyName("console_url")] string ConsoleUrl,
    [property: JsonPropertyName("api_url")] string ApiUrl,
    [property: JsonPropertyName("console_built")] bool ConsoleBuilt,
    [property: JsonPropertyName("reachable")] bool Reachable,
    [property: JsonPropertyName("hosted")] bool Hosted,
    [property: JsonPropertyName("qr_svg")] string QrSvg,
    [property: JsonPropertyName("how")] string[] How,
    [property: JsonPropertyName("note")] string Note);

public record DeviceRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("transport")] string? Transport,
    [property: JsonPropertyName("has_llm")] bool HasLlm,
    [property: JsonPropertyName("paired")] bool Paired);

/// Signup's two shapes under one roof, the way the route answers: pending
/// with the code out, or — on a local install with no mail transport —
/// activated directly with the session fields filled.
public record SignupResult(
    [property: JsonPropertyName("email")] string Email,
    [property: JsonPropertyName("verified")] bool Verified,
    [property: JsonPropertyName("verification")] string Verification,
    [property: JsonPropertyName("account_id")] string? AccountId,
    [property: JsonPropertyName("code_delivery")] string? CodeDelivery,
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("user_token")] string? UserToken);

public record SignInResult(
    [property: JsonPropertyName("account_id")] string AccountId,
    [property: JsonPropertyName("email")] string Email,
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("user_token")] string UserToken);

public record CodeDelivery(
    [property: JsonPropertyName("email")] string Email,
    [property: JsonPropertyName("code_delivery")] string Delivery);

public record ResetDone(
    [property: JsonPropertyName("email")] string Email,
    [property: JsonPropertyName("reset")] bool Reset);

public record OauthProviderRow(
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("configured")] bool Configured,
    [property: JsonPropertyName("setup")] string? Setup);

public record OauthProviders(
    [property: JsonPropertyName("signin_providers")] OauthProviderRow[] Providers);

public record OauthStarted(
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("url")] string Url);

/// The claim is polled: not-ready is `ready` alone, and ready carries the
/// session — a fresh account's full enrollment or a returning one's token.
public record OauthClaim(
    [property: JsonPropertyName("ready")] bool Ready,
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("user_token")] string? UserToken,
    [property: JsonPropertyName("email")] string? Email);

public record ContinuityTurn(
    [property: JsonPropertyName("role")] string Role,
    [property: JsonPropertyName("content")] string Content);

public record SessionContinuity(
    [property: JsonPropertyName("with")] string With,
    [property: JsonPropertyName("recent_turns")] ContinuityTurn[] RecentTurns,
    [property: JsonPropertyName("note")] string Note);

public record SessionStarted(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("device")] string? Device,
    [property: JsonPropertyName("prior_sessions")] int PriorSessions,
    [property: JsonPropertyName("memory")] string? Memory,
    [property: JsonPropertyName("continuity")] SessionContinuity? Continuity);

public record SessionEnded(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("ended")] bool Ended);

public record CalmSessionRow(
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("minutes")] int Minutes,
    [property: JsonPropertyName("what")] string What);

public record CalmCatalog(
    [property: JsonPropertyName("sessions")] CalmSessionRow[] Sessions);

public record CalmStep(
    [property: JsonPropertyName("say")] string Say,
    [property: JsonPropertyName("seconds")] int Seconds);

/// A protocol, not a generation — the counts never vary.
public record CalmStarted(
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("what")] string What,
    [property: JsonPropertyName("total_seconds")] int TotalSeconds,
    [property: JsonPropertyName("calm_steps")] CalmStep[] Steps,
    [property: JsonPropertyName("note")] string Note);

public record CalmHistoryRow(
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("seconds")] int Seconds,
    [property: JsonPropertyName("at")] string At);

public record WorkoutBlock(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("seconds")] int Seconds,
    [property: JsonPropertyName("cue")] string Cue);

public record WorkoutPlan(
    [property: JsonPropertyName("minutes_asked")] int MinutesAsked,
    [property: JsonPropertyName("level")] string Level,
    [property: JsonPropertyName("focus")] string Focus,
    [property: JsonPropertyName("rest_seconds_between_blocks")] int RestSeconds,
    [property: JsonPropertyName("blocks")] WorkoutBlock[] Blocks);

public record MealRow(
    [property: JsonPropertyName("slot")] string Slot,
    [property: JsonPropertyName("name")] string Name);

public record MealDay(
    [property: JsonPropertyName("day_number")] int DayNumber,
    [property: JsonPropertyName("meals")] MealRow[] Meals);

public record MealShape(
    [property: JsonPropertyName("meals_per_day")] int MealsPerDay,
    [property: JsonPropertyName("orientation_calories")] int OrientationCalories,
    [property: JsonPropertyName("why")] string Why);

public record MealPlan(
    [property: JsonPropertyName("goal")] string Goal,
    [property: JsonPropertyName("preferences")] string[] Preferences,
    [property: JsonPropertyName("shape")] MealShape Shape,
    [property: JsonPropertyName("days")] MealDay[] Days,
    [property: JsonPropertyName("disclaimer")] string Disclaimer);

/// Ambient watching: the why behind a moved heart rate.
public record ActivityWatch(
    [property: JsonPropertyName("activity")] string? Activity,
    [property: JsonPropertyName("proactive")] bool Proactive,
    [property: JsonPropertyName("watching")] bool Watching,
    [property: JsonPropertyName("intervention")] Guidance? Intervention);

public record ConditionsKnown(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("known_conditions")] string[] KnownConditions);

public record PersonalitySaved(
    [property: JsonPropertyName("user_id")] string UserId);

public record InsightRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("area")] string Area,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("message")] string Message,
    [property: JsonPropertyName("source")] string? Source);

public record ContextAdded(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("source")] string Source,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("vaulted")] bool Vaulted,
    [property: JsonPropertyName("insights")] InsightRow[] Insights);

public record FeedbackSaved(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("rating")] string Rating,
    [property: JsonPropertyName("contributed")] bool Contributed);

public record EventRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("type")] string Type,
    [property: JsonPropertyName("condition")] string? Condition,
    [property: JsonPropertyName("severity")] string? Severity,
    [property: JsonPropertyName("created_at")] string CreatedAt);

public record ReportCheckins(
    [property: JsonPropertyName("count")] int Count,
    [property: JsonPropertyName("avg_mood")] double? AvgMood,
    [property: JsonPropertyName("avg_energy")] double? AvgEnergy,
    [property: JsonPropertyName("avg_stress")] double? AvgStress);

public record ProgressReport(
    [property: JsonPropertyName("checkins")] ReportCheckins Checkins,
    [property: JsonPropertyName("detections")] Dictionary<string, int> Detections,
    [property: JsonPropertyName("insights_count")] int InsightsCount,
    [property: JsonPropertyName("journal_entries")] int JournalEntries,
    [property: JsonPropertyName("feedback")] Dictionary<string, int> Feedback);

public record CompanionSaid(
    [property: JsonPropertyName("delivered")] bool Delivered,
    [property: JsonPropertyName("unprompted")] bool Unprompted,
    [property: JsonPropertyName("content")] string Content);

public record CoachExchange(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("area")] string Area,
    [property: JsonPropertyName("role")] string Role,
    [property: JsonPropertyName("content")] string Content,
    [property: JsonPropertyName("created_at")] string CreatedAt);

public record SpecialistRow(
    [property: JsonPropertyName("condition")] string Condition,
    [property: JsonPropertyName("mode")] string Mode,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("qrme_profile_id")] string? QrmeProfileId);

public record SpecialistsSeeded(
    [property: JsonPropertyName("created")] int Created,
    [property: JsonPropertyName("skipped")] int Skipped,
    [property: JsonPropertyName("conditions")] int Conditions);

public record CatalogStarter(
    [property: JsonPropertyName("profile_id")] string? ProfileId,
    [property: JsonPropertyName("display_name")] string? DisplayName);

public record SpecialistCatalog(
    [property: JsonPropertyName("starters")] CatalogStarter[]? Starters,
    [property: JsonPropertyName("note")] string? Note);

/// <summary>One QRME profile the attach bracket found, beyond the curated
/// shelf. <c>Attachable</c> and <c>Standing</c> are two fields rather than
/// one: an age-restricted profile <em>is</em> attachable and still carries a
/// caveat somebody needs to read.</summary>
public record SpecialistFound(
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("purpose")] string? Purpose,
    [property: JsonPropertyName("attachable")] bool Attachable,
    [property: JsonPropertyName("standing")] string? Standing);

public record SpecialistSearch(
    [property: JsonPropertyName("results")] SpecialistFound[]? Results,
    [property: JsonPropertyName("capped")] bool Capped,
    [property: JsonPropertyName("limit")] int Limit);

public record ClinicianRow(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("label")] string? Label,
    [property: JsonPropertyName("display_name")] string? DisplayName);

public record ClinicianSearch(
    [property: JsonPropertyName("area")] string Area,
    [property: JsonPropertyName("locality")] string? Locality,
    [property: JsonPropertyName("clinicians")] ClinicianRow[] Clinicians,
    [property: JsonPropertyName("reason")] string? Reason);

/// Nothing is released by preparing: the package is for the user to read,
/// and the signing ceremony belongs to QRME.
public record ReferralPrepared(
    [property: JsonPropertyName("prepared")] bool Prepared,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("referral_request_id")] string? RequestId,
    [property: JsonPropertyName("display_text")] string? DisplayText,
    [property: JsonPropertyName("note")] string? Note);

public record ReferralRequestRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("condition")] string Condition,
    [property: JsonPropertyName("provider_id")] string ProviderId,
    [property: JsonPropertyName("qrme_referral_id")] string? QrmeReferralId,
    [property: JsonPropertyName("created_at")] string CreatedAt);

public record ReferralReleased(
    [property: JsonPropertyName("referral_request_id")] string RequestId);

/// A refusal is a 200-shaped answer with started:false and a reason.
public record SpecialistTaskStarted(
    [property: JsonPropertyName("started")] bool Started,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("id")] string? Id);

public record SpecialistTaskRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("goal")] string Goal,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("qrme_profile_id")] string? QrmeProfileId,
    [property: JsonPropertyName("created_at")] string CreatedAt,
    [property: JsonPropertyName("updated_at")] string UpdatedAt);

public record SpecialistTaskView(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("goal")] string Goal,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("reachable")] bool Reachable,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("next_phase")] string? NextPhase);

/// What a consented care provider sees.
public record ProviderSummary(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("known_conditions")] string[] KnownConditions,
    [property: JsonPropertyName("escalations")] int Escalations,
    [property: JsonPropertyName("avg_mood")] double? AvgMood);

public record AccessLogEntry(
    [property: JsonPropertyName("action")] string? Action,
    [property: JsonPropertyName("at")] string? At);

/// Who has read your record. An empty list with no record kept is a
/// different fact from nobody having looked.
public record AccessLog(
    [property: JsonPropertyName("vaulted")] bool Vaulted,
    [property: JsonPropertyName("access_record_kept")] bool RecordKept,
    [property: JsonPropertyName("entries")] AccessLogEntry[] Entries,
    [property: JsonPropertyName("note")] string Note);

/// `GET /audit/{uid}` — what was *done*, beside the access log's record of
/// what was *read*.
///
/// `Integrity` is decoded rather than dropped: a list of acts nobody can check
/// is a list, and the chain's state is the half that makes the other half a
/// record. `Catalogue` is what would be recorded, so an empty `Trail` reads as
/// "nothing happened" and not as "nothing is watched". The wire avoids
/// `entries`, `chain` and `actions` — all three already carry other types.
public record AuditIntegrity(
    [property: JsonPropertyName("intact")] bool Intact,
    [property: JsonPropertyName("hashed")] int Hashed,
    [property: JsonPropertyName("broken_at_seq")] int? BrokenAtSeq);

public record AuditEntry(
    [property: JsonPropertyName("seq")] int Seq,
    [property: JsonPropertyName("action")] string Action,
    [property: JsonPropertyName("category")] string Category,
    [property: JsonPropertyName("ref")] string? Ref,
    [property: JsonPropertyName("at")] string At);

public record AuditAction(
    [property: JsonPropertyName("action")] string Action,
    [property: JsonPropertyName("category")] string Category,
    [property: JsonPropertyName("description")] string Description);

public record AuditLog(
    [property: JsonPropertyName("trail")] AuditEntry[] Trail,
    [property: JsonPropertyName("count")] int Count,
    [property: JsonPropertyName("integrity")] AuditIntegrity Integrity,
    [property: JsonPropertyName("catalogue")] AuditAction[] Catalogue,
    [property: JsonPropertyName("retention")] string Retention);

public record CloudStatus(
    [property: JsonPropertyName("cloud")] bool Cloud,
    [property: JsonPropertyName("model")] string? Model,
    [property: JsonPropertyName("fallback")] string Fallback,
    [property: JsonPropertyName("contribution")] string Contribution);

public record ContributionView(
    [property: JsonPropertyName("opted_in")] bool OptedIn,
    [property: JsonPropertyName("policy")] string Policy);

public record ContributionRevoked(
    [property: JsonPropertyName("opted_in")] bool OptedIn,
    [property: JsonPropertyName("revoked")] int Revoked,
    [property: JsonPropertyName("note")] string Note);

public record IncidentRow(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("at")] string? At);

public record PageRow(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("to")] string? To,
    [property: JsonPropertyName("delivered")] bool? Delivered,
    [property: JsonPropertyName("sent_at")] string? SentAt);

public record LocalitySaved(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("locality")] string? Locality);

public record PlanRow(
    [property: JsonPropertyName("plan")] string Plan,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("price_usd")] double PriceUsd,
    [property: JsonPropertyName("period")] string? Period);

public record PlansOut(
    [property: JsonPropertyName("plans")] PlanRow[] Plans);

public record BudgetRow(
    [property: JsonPropertyName("category")] string Category,
    [property: JsonPropertyName("monthly_limit")] double MonthlyLimit,
    [property: JsonPropertyName("spent")] double Spent,
    [property: JsonPropertyName("standing")] string Standing);

public record BudgetsOut(
    [property: JsonPropertyName("month")] string Month,
    [property: JsonPropertyName("days_left")] int DaysLeft,
    [property: JsonPropertyName("budgets")] BudgetRow[] Rows);

public record BudgetRemoved(
    [property: JsonPropertyName("removed")] bool Removed);

/// The storage posture a plan buys, in the plan sheet's own words.
public record StoragePosture(
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("means")] string Means,
    [property: JsonPropertyName("who_can_read")] string[] WhoCanRead);

public record MembershipView(
    [property: JsonPropertyName("account_id")] string AccountId,
    [property: JsonPropertyName("plan")] string Plan,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("price_usd")] double PriceUsd,
    [property: JsonPropertyName("period")] string? Period,
    [property: JsonPropertyName("includes")] string[] Includes,
    [property: JsonPropertyName("locked")] string[] Locked,
    [property: JsonPropertyName("storage")] StoragePosture Storage);

public record BeaconRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("placement")] string? Placement,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("scans")] int Scans,
    [property: JsonPropertyName("active")] bool Active,
    [property: JsonPropertyName("scan_url")] string ScanUrl);

public record BeaconCardOut(
    [property: JsonPropertyName("beacon")] string Beacon,
    [property: JsonPropertyName("first_name")] string? FirstName,
    [property: JsonPropertyName("watched")] bool? Watched,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("badge")] string? Badge,
    [property: JsonPropertyName("call_first")] string? CallFirst);

public record BeaconAlarm(
    [property: JsonPropertyName("alarm")] string Alarm,
    [property: JsonPropertyName("raised")] bool Raised,
    [property: JsonPropertyName("tier")] string? Tier,
    [property: JsonPropertyName("badge")] string? Badge,
    [property: JsonPropertyName("note")] string? Note);

public record BeaconRetired(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("active")] bool Active);

public record RelayChannel(
    [property: JsonPropertyName("configured")] bool Configured,
    [property: JsonPropertyName("envelope")] string? Envelope,
    [property: JsonPropertyName("note")] string Note);

public record RelayRoster(
    [property: JsonPropertyName("configured")] bool Configured,
    [property: JsonPropertyName("roster")] string[] Roster,
    [property: JsonPropertyName("ceiling")] string Ceiling,
    [property: JsonPropertyName("note")] string Note);

public record RelayRota(
    [property: JsonPropertyName("configured")] bool Configured,
    [property: JsonPropertyName("timezone")] string Timezone,
    [property: JsonPropertyName("on_now")] string[] OnNow,
    [property: JsonPropertyName("anybody_on_shift")] bool AnybodyOnShift,
    [property: JsonPropertyName("note")] string Note);

public record SocialBeacon(
    [property: JsonPropertyName("connection")] string Connection,
    [property: JsonPropertyName("platform")] string Platform,
    [property: JsonPropertyName("handle")] string Handle,
    [property: JsonPropertyName("presence_url")] string PresenceUrl);

public record SocialGone(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("status")] string Status);

public record RobotUnbound(
    [property: JsonPropertyName("id")] string? Id);

public record BeaconPage(string Html, Uri Page);

// ---- safe knowledge excursions + the community window ----

/// <summary>One studied topic: how much of the person was redacted out
/// before the question left, and whether it left this host at all.</summary>
public record ExcursionRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("topic")] string Topic,
    [property: JsonPropertyName("redactions")] int Redactions,
    [property: JsonPropertyName("left_host")] bool LeftHost,
    [property: JsonPropertyName("findings")] string? Findings,
    [property: JsonPropertyName("learned")] bool Learned);

public record ExcursionLearned(
    [property: JsonPropertyName("learned")] bool Learned,
    [property: JsonPropertyName("already_learned")] bool AlreadyLearned,
    [property: JsonPropertyName("note")] string? Note);

/// <summary>A community door that was opened — the room's id and the time,
/// and nothing from inside the room.</summary>
public record CommunityVisitRow(
    [property: JsonPropertyName("room_id")] string? RoomId,
    [property: JsonPropertyName("at")] string? At);

public record CommunityFeedItem(
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("topic")] string? Topic);

/// <summary>QRME's public feed through the tandem — read-only by
/// construction, and a 409 in the server's words without an endpoint.</summary>
public record CommunityFeedView(
    [property: JsonPropertyName("note")] string Note,
    [property: JsonPropertyName("open_in_qrme")] string? OpenInQrme,
    [property: JsonPropertyName("items")] CommunityFeedItem[] Items);

// ---- the voice pair: say it aloud, and hear what was said ----

public record Transcribed([property: JsonPropertyName("text")] string Text);

public record HealthOut(
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("tandem")] bool Tandem,
    [property: JsonPropertyName("version")] string? Version);
