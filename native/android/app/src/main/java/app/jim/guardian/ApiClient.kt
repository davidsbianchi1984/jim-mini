package app.jim.guardian

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

// MARK: wire models

data class EnrollResult(val id: String, val displayName: String, val userToken: String)
data class Pace(val perMinute: Int, val ratio: String, val lightCue: String?, val audioCue: String?)
data class FirstAid(val kind: String, val callEms: Boolean, val steps: List<String>, val pace: Pace?)
data class Evidence(val publisher: String, val title: String, val url: String,
                    val supports: String?)
data class Provenance(val method: String, val generatedBy: String,
                      val evidence: List<Evidence>, val disclaimer: String)
data class Custody(val vaulted: Boolean, val pdiKey: String?, val note: String?)
data class CustodyList(val records: List<String>, val chainIntact: Boolean?)
data class CustodyProvenance(val origin: String, val cipher: String?,
                             val auditCount: Int, val chainIntact: Boolean?)
// --- engaged sessions (jim/engaged.py) -------------------------------------
//
// `coach` is a turn. These are a session: open until sign-off, able to act on
// this person's own records while it is open, and every act landing on a
// trail with the request that would take it back.
//
// `reversible` and `irreversibleBecause` are carried separately rather than
// derived from one another. An act that acted and can no longer be taken back
// is a real third state — already undone, or one whose way back the backend
// could not build — and a screen rendering `!reversible` as "irreversible"
// would tell somebody their journal entry had left the app.
data class EngagedTool(val name: String, val says: String, val acts: Boolean,
                       val reversible: Boolean,
                       val irreversibleBecause: String?)

data class EngagedReach(val can: List<EngagedTool>, val toolsPerTurn: Int,
                        val actsPerSession: Int, val watchCeiling: Int)

// One group of switches an engaged session may throw (jim/permits.py).
//
// `says` arrives as a sentence rather than a label, because a toggle beside
// the words "what it may read" tells nobody what they are agreeing to.
// `decidedAt` being null means never decided — a third state beside on and
// off, and the one that makes "I never agreed to that" answerable.
data class EngagedPermitArea(val area: String, val says: String,
                             val standing: String, val granted: Boolean,
                             val decidedAt: String?, val tools: List<String>)

data class EngagedPermits(val groups: List<EngagedPermitArea>, val note: String)

data class EngagedStep(val tool: String?, val answered: Int?, val says: String?,
                       val acts: Boolean, val reversible: Boolean,
                       val irreversibleBecause: String?, val refused: String?)

data class EngagedAct(val id: String, val tool: String, val says: String,
                      val answered: Int, val createdAt: String,
                      val undoneAt: String?, val reversible: Boolean,
                      val irreversibleBecause: String?)

data class StandingWatch(val id: String, val topic: String, val area: String?,
                         val createdAt: String)

data class EngagedTurnRow(val role: String, val content: String,
                          val createdAt: String)

data class EngagedSession(val engaged: Boolean, val id: String?,
                          val area: String?,
                          val turns: List<EngagedTurnRow>,
                          val acted: List<EngagedAct>,
                          val watching: List<StandingWatch>)

data class EngagedTurnResult(val reply: String, val acted: List<EngagedStep>,
                             val stopped: String?, val degraded: Boolean,
                             val generatedBy: String,
                             val watching: List<StandingWatch>)

data class EngagedSignOff(val signedOff: Boolean, val deposited: Int,
                          val watching: List<StandingWatch>)

data class Guidance(val delivered: Boolean, val source: String?, val content: String,
                    val references: List<String> = emptyList(), val firstAid: FirstAid? = null,
                    val provenance: Provenance? = null, val translationNote: String? = null,
                    val specialist: String? = null, val qrmeProfileId: String? = null,
                    val custody: Custody? = null,
                    // The *offer*, distinct from `specialist` above: that is a
                    // name the monitoring path fills in; this is whether one
                    // is available to ask.
                    val specialistOffer: SpecialistOffer? = null)
data class SpecialistOffer(val available: Boolean, val label: String,
                           val qrmeProfileId: String, val sent: Boolean,
                           val note: String)
data class SpecialistAnswer(val delivered: Boolean, val content: String?,
                            val reason: String?, val note: String?,
                            val heldForOwnerApproval: Boolean,
                            val label: String?, val method: String?,
                            val shared: String?)
// The offline coach's store and syllabus (jim/pipeline.py): what the stack
// predicts from, what JIM should study next, and what one press of study did.
data class CoachStoreEntry(val topic: String, val lesson: String,
                           val source: String, val model: String?)
data class CoachStore(val pack: Int, val excursions: List<CoachStoreEntry>,
                      val deposits: List<CoachStoreEntry>)
data class CoachSuggestion(val area: String, val topic: String, val why: String)
data class CoachCurriculum(val suggested: List<CoachSuggestion>, val note: String)
data class CoachStudied(val studied: String, val folded: Boolean)
/** A link between two guardians. `task` is what keeps it open past the call. */
data class LiaisonRow(val id: String, val about: String, val task: String,
                      val running: Boolean, val endedBecause: String?,
                      val openedAt: String,
                      // Naming a task is the namer's own yes and nothing
                      // more: the link outlives the call only once both
                      // sides have agreed. Three fields rather than one
                      // flag, because "you have not agreed", "they have
                      // not" and "nobody named anything" are three
                      // different things for a screen to say.
                      val youAgreed: Boolean, val theyAgreed: Boolean,
                      val holdsItOpen: Boolean)
/** A person's own half: what theirs said, and what it was told. */
data class LiaisonHalf(val linkId: String, val about: String,
                       val task: String, val running: Boolean,
                       val saidByMine: List<String>,
                       val saidToMine: List<String>)
/** One thing this guardian has running. `kind` and `why` are closed-set
 *  words said in the reader's language by L10n; `term` is one of the
 *  product's own vocabulary words and `words` is what the person wrote. */
data class UnderwayRow(val kind: String, val id: String?, val term: String?,
                       val words: String?, val since: String?,
                       val why: String)
/** Everything running, what it learned today, and what is left to spend.
 *  `quiet` is the server's own answer rather than one derived here, so the
 *  four shells cannot disagree about what "nothing running" looks like. */
data class UnderwayWindow(val underway: List<UnderwayRow>,
                          val quiet: Boolean, val today: List<Errand>,
                          val spentToday: Int, val daily: Int,
                          val permitted: Boolean)
/** Two people on one call, each with their own channel 2. A disclosure and
 *  nothing else — their device, gain and what they hear are not here. */
data class MicPaired(val paired: Boolean, val with: String?,
                     val yoursListening: Boolean,
                     val theirsListening: Boolean, val both: Boolean)
/** A cue read off a camera or a speaker. Read on the way through, never out
 *  of anything kept, and the words it was read from are never carried. */
data class Cue(val cue: String, val severity: String, val says: String,
               val monitor: String, val reference: String, val tier: String,
               val at: String)
/** What was noticed, and what each monitor could ever notice. */
data class CuesSeen(val lately: List<Cue>,
                    val canRead: Map<String, List<String>>)
/** One moment a monitor took something in. `kept` is false for most of what
 *  is sensed, and `droppedBecause` says which promise stopped it. */
data class Moment(val id: String, val monitor: String, val content: String,
                  val stretchId: String?, val sensedAt: String)
/** One monitor's day. `because` is a list — keeping switched off in the
 *  morning and on by the afternoon is an ordinary thing to do. */
data class MonitorDay(val monitor: String, val sensed: Int, val kept: Int,
                      val dropped: Int, val because: List<String>,
                      val holds: String)
data class DayAccount(val date: String, val monitors: List<MonitorDay>,
                      val sensed: Int, val kept: Int, val quiet: Boolean)
/** A meeting, a call, or a working stretch. `othersTold` is the same claim
 *  switching the monitor on demands, asked again. */
data class Stretch(val id: String, val monitor: String, val about: String,
                   val othersTold: Boolean, val catchesOthers: Boolean,
                   val running: Boolean, val openedAt: String,
                   val endedAt: String?, val moments: Int, val kept: Int)
data class TheDay(val account: DayAccount, val survived: List<Moment>,
                  val stretches: List<Stretch>)
/** One thing that can be plugged in and sense somebody. `catchesOthers` is
 *  the field that decides everything else: nothing carrying it is ever on by
 *  default, and switching one on is refused until the people in that space
 *  have been told. */
data class MonitorRow(val name: String, val senses: List<String>,
                      val placing: String, val says: String,
                      val holds: String, val catchesOthers: Boolean,
                      val on: Boolean, val device: String?,
                      val othersTold: Boolean, val keeping: Boolean)
/** One part of the notice: the support-line script in a language the far side
 *  might actually speak. More than one where the mix is known. */
data class CallNotice(val language: String, val words: String)
data class AssistedCall(val id: String, val listening: Boolean,
                        val route: String, val recording: Boolean,
                        val notices: List<CallNotice>, val said: String,
                        val spokenIn: List<String>, val languageFrom: String)
data class CallRow(val id: String, val route: String, val said: String,
                   val spokenIn: List<String>, val announcedAt: String?,
                   val listened: Boolean, val openedAt: String)
/** One remark on a draft. `because` is the evidence it came from; `door` is
 *  set only on an offer, and only ever names a screen this product has. */
data class Remark(val kind: String, val says: String,
                  val because: List<String>, val door: String?)
/** `quietBecause` carries the reason there is nothing to say — an empty list
 *  on its own cannot tell somebody *nothing to add* from *it did not run*. */
data class Alongside(val remarks: List<Remark>, val quietBecause: String?)
/** One errand: a topic the offline coach could not answer, gone and studied.
 *  `why` names the monitor that asked for it. */
data class Errand(val id: String, val topic: String, val area: String,
                  val why: String, val excursionId: String,
                  val redactions: Int, val leftHost: Boolean,
                  val openedAt: String)
/** An empty ledger has three causes, so all three ride on the wire: nothing
 *  worth studying, nothing left to spend, or nobody ever allowed it. */
data class ErrandLedger(val errands: List<Errand>,
                        val due: List<CoachSuggestion>,
                        val spentToday: Int, val daily: Int,
                        val permitted: Boolean)
/** What the coach noticed, and which half of the ladder settled it.
 *  `settledBy` is the column worth reading: `coach` cost nothing, `jim` cost
 *  one of the day's shared turns. */
data class Notice(val id: String, val eventId: String,
                  val condition: String, val severity: String,
                  val settledBy: String, val said: String,
                  val noticedAt: String)
/** Of everything handled unattended, how much the free half carried.
 *  `freeShare` is null rather than 0 when nothing has been handled — a bare
 *  0% would say the coach settled none of them. */
data class NoticeSettlement(val settledFree: Int, val settledPaid: Int,
                        val freeShare: Double?, val permitted: Boolean,
                        val spentToday: Int, val daily: Int)
data class NoticeLedger(val handled: List<Notice>,
                        val waiting: List<String>,
                        val settlement: NoticeSettlement)
/** A spent budget is reported, never refused: the free half is still worth
 *  running, so `overBudget` names what waits for tomorrow. */
data class NoticedRun(val byCoach: List<Notice>, val byJim: List<Notice>,
                      val overBudget: List<String>,
                      val remainingToday: Int, val nothingNoticed: Boolean)
data class Lookout(val id: String, val url: String, val everyHours: Double,
                   val status: String?, val nextRunAt: String?,
                   val changedAt: String?, val trouble: String?)
data class LookoutList(val lookouts: List<Lookout>, val readable: Boolean)
data class ErrandsRun(val errands: List<Errand>, val remainingToday: Int,
                      val nothingToStudy: Boolean)
data class LanguageInfo(val code: String, val label: String, val safetyTranslated: Boolean)
data class TranslateResult(val translation: String, val engine: String, val note: String?)
data class ChildCreated(val id: String, val childToken: String,
                        val oversight: String, val sensitivity: String?)
data class ChildSummary(val childId: String, val displayName: String,
                        val age: Int, val oversight: String)
data class ChildEvent(val type: String, val condition: String?,
                      val severity: String?)
data class ChildOverview(val displayName: String?, val oversight: String,
                         val criticalEvents: Int, val events: List<ChildEvent>,
                         val privacyNote: String?, val note: String?)
data class GuardianChild(val childId: String, val displayName: String,
                         val light: String, val critical24h: Int,
                         val escalations24h: Int, val paused: Boolean,
                         val quietHours: String?)
data class GuardianFace(val children: List<GuardianChild>, val haptic: String?)
data class MonitorResult(
    val detected: Boolean, val condition: String?, val severity: String?,
    val reason: String?, val guidance: Guidance?,
)
data class CheckinResult(val id: String, val guidance: Guidance?)
data class BaselineMetric(val metric: String, val value: Double?, val state: String?, val samples: Int?)
data class Goal(val id: String, val area: String, val title: String, val target: String?, val status: String?)
data class Habit(val id: String, val name: String, val streak: Int?)
data class JournalItem(val id: String, val text: String?, val createdAt: String?)
data class ProviderInfo(val name: String, val label: String, val configured: Boolean)
data class FlowStep(val step: String, val label: String, val detail: String)
data class RobotDirective(val robot: String, val directive: String)
data class EmergencyResult(val flow: List<FlowStep>, val directives: List<RobotDirective>)
data class EscalationPolicy(val sensitivity: String, val bySeverity: Map<String, String>)
/// An open alarm, raised when somebody scanned a care code on a door.
///
/// `acceptedBy` is the point of the type. Accepting and clearing are separate
/// acts and the backend keeps them apart on purpose — accepting says somebody
/// is coming, clearing says it is over. An accepted alarm is still `open`, and
/// this shell shows it that way, because conflating them is how an alarm gets
/// marked handled by the act of being seen.
data class AlarmRow(
    val id: String, val beaconId: String, val messages: List<String>,
    val state: String, val tier: String, val acceptedBy: String?,
    val createdAt: String,
    /** True on every row this queue holds, because JIM cannot place a call at
     *  any tier: a beacon alarm is ceilinged below emergency services, and a
     *  crash watch that reached the top rung issued a dispatch *request*. */
    val callEmergencyServicesYourself: Boolean = false,
    /** Whether a safety floor was cut to reach this tier. */
    val clippedByCeiling: Boolean = false,
)

data class AlarmAck(val alarm: String, val acceptedBy: String?,
                    val state: String?, val note: String?)

data class AlarmGuidance(val answer: String, val note: String?)

data class CrashWatch(
    val armed: Boolean, val trustedName: String, val attempts: Int,
    val windowMinutes: Double, val contactEms: Boolean,
    val asking: Boolean, val attempt: Int, val concern: String,
    val tripped: Boolean,
)
data class RobotSpec(val model: String, val label: String, val maker: String,
                     val firstAid: String?)
data class Robot(val id: String, val model: String, val name: String, val status: String?,
                 val directive: String?, val firstAid: String?, val commands: List<String>)
data class RobotCmdResult(val status: String, val note: String?, val instruction: String?,
                          val spokenSteps: List<String>, val sequence: List<String>,
                          val pacePerMinute: Int?)
data class WaiverState(val signed: Boolean, val signature: String?, val terms: List<String>)
data class MedicalCardIssued(val token: String, val qrSvgUrl: String)
// ---- the effectiveness loop, the user-specific model, and the name ----

/** Spec [0039]: guidance that went out gets asked about. */
data class OpenFollowup(val id: String, val condition: String,
                        val severity: String?, val question: String)
data class LiveOption(val kind: String, val name: String?, val channel: String?,
                      val note: String?)
data class FollowupAnswered(val answered: Boolean, val reason: String?,
                            val helped: Boolean?, val next: String?,
                            val options: List<LiveOption>, val liveNote: String?)
data class HelpTally(val helped: Int, val answered: Int)
/** Claim 11's user-specific model, derived locally from this user's own
 *  stored history — nothing was sent to a model vendor to build it. */
data class Finetune(val build: Int, val backend: String, val examples: Int,
                    val helped: Int, val didNotHelp: Int, val method: String,
                    val digest: String, val trainedAt: String,
                    val active: Boolean)
data class AdaptationProfile(val built: Boolean, val note: String?,
                             val evidenceItems: Int, val confidence: Double,
                             val vaulted: Boolean, val whatHelps: Map<String, HelpTally>,
                             val tone: String?, val occupation: String?,
                             val method: String?)
/** What anonymity keeps and what it costs, said out loud. */
data class AnonymityPosture(val anonymous: Boolean, val knownAs: String?,
                            val legalNameOnRecord: Boolean,
                            val keeps: List<String>, val costs: List<String>)

// ---- the community door (FIG. 2 boxes 222-226) ----

data class PresenceWho(val says: String, val note: String,
                       val worksOffline: Boolean, val handsFree: Boolean,
                       /** key → the sentence a screen shows. The values are
                        *  what it will not be, and they are shown before any
                        *  warm line: honest before charming. */
                       val boundaries: Map<String, String>)
data class PresenceArea(val area: String, val standing: String)
data class PresenceBaseline(val known: Int, val of: Int,
                            val neededNetwork: Boolean,
                            val areas: List<PresenceArea>)
/** One unprompted turn — or silence, which is an outcome rather than an
 *  empty response. `because` is why, and a presence that cannot show its
 *  reason is one nobody can argue with. */
data class PresenceBeat(val slot: String, val speak: Boolean,
                        val register: String, val english: String,
                        val deepenedLine: String?, val because: List<String>)
data class PresenceSurfaceRow(val surface: String, val chosen: Boolean,
                              val readsHealthAloud: Boolean, val note: String)
data class PresenceSurfaces(val chosen: String, val rule: String,
                            val surfaces: List<PresenceSurfaceRow>)
data class PresenceGrowth(val beatsSpoken: Int, val areasSeen: Int,
                          val of: Int, val aboutMyself: String)
/** How the presence carries itself, and what the dial leaves alone.
 *
 *  `unchanged` is carried to the screen rather than assumed: a bearing that
 *  quietly narrowed what a health guardian watches would be a setting that
 *  hurts whoever turned it, so the claim is rendered where it can be read. */
/** A beat plus the room's verdict on it. The withholding is decided on the
 *  server, before anything is synthesised: the surface rule spent a release
 *  as a caption next to a button, reported by `surfaces()` and read by
 *  nothing. */
data class PresenceSpoken(val speaksOn: String, val spoken: Boolean,
                          val shown: Boolean, val withheld: List<String>,
                          val whyNotAloud: String, val hasAudio: Boolean,
                          val english: String, val speak: Boolean)
data class PresenceBearingView(val bearing: String, val default: String,
                               val choices: List<String>, val says: String,
                               val unchanged: List<String>, val note: String)
data class CommunityRoom(val id: String, val topic: String?, val channel: String?,
                         val participants: Int, val url: String?)
data class CommunityPlace(val locality: String, val region: String?, val listings: Int)
/** What JIM will and will not do with the community it points at, as data
 *  rather than prose, so a screen cannot claim more than the bridge does. */
data class CommunityPosture(val mirroredHere: Boolean, val postsOnYourBehalf: Boolean,
                            val healthDataShared: Boolean)
data class CommunityView(val qrmeUrl: String?, val language: String?,
                         val rooms: List<CommunityRoom>, val places: List<CommunityPlace>,
                         val note: String, val posture: CommunityPosture)

data class SourceRow(val source: String, val consented: Boolean)
data class SocialConn(val id: String, val platform: String, val direction: String, val handle: String?)
data class CatalogApp(val provider: String, val app: String, val label: String)
data class AppConn(val id: String, val provider: String, val app: String)
data class MedicalCard(val name: String?, val age: Int?, val conditions: List<String>,
                       val restingHr: Int?, val contactName: String?, val contactPhone: String?)

data class ImproveItem(val category: String, val message: String, val status: String)
data class ImproveState(val mine: List<ImproveItem>, val tally: Map<String, Int>, val total: Int)
data class AccessReportRow(val doing: String, val wall: String, val help: String?,
                           val lang: String, val createdAt: String)

class ApiException(message: String) : Exception(message)

/**
 * Coroutine client for the JIM Guardian backend.
 *
 * The Android emulator reaches the host machine at 10.0.2.2, so that is the
 * default. On a physical device, set your machine's LAN IP via [base].
 */
object ApiClient {
    /** The person's own model key, pushed in by the view model and sent on
     *  every request as `x-llm-api-key`. Empty means the deployment's. */
    @Volatile var llmKey: String = ""

    /** The deployment invite key: a published deployment sets
     *  JIM_SIGNUP_KEY and refuses account creation without it. Sent as
     *  `x-signup-key` on every request; the backend reads it only on the
     *  routes it gates. */
    @Volatile var signupKey: String = ""

    @Volatile var base: String = "http://10.0.2.2:8000"
        // Normalised on the way in, the way the console and the Windows
        // shell already do it: a pasted address with a trailing slash
        // otherwise reached every path as a double one. PDI's shell has
        // carried this setter since it was written; these two did not.
        set(value) {
            val trimmed = value.trimEnd('/')
            if (trimmed.isNotBlank()) field = trimmed
        }

    private fun parseGuidance(o: JSONObject?): Guidance? {
        if (o == null) return null
        val refs = o.optJSONArray("references")
        val aidObj = o.optJSONObject("first_aid")
        val aid = aidObj?.let { a ->
            val steps = a.optJSONArray("steps")
            val paceObj = a.optJSONObject("pace")
            val pace = paceObj?.let { pc ->
                val cue = pc.optJSONObject("cue")
                Pace(pc.optInt("compressions_per_minute"),
                    pc.optString("compression_to_breath_ratio", ""),
                    cue?.optString("light", null), cue?.optString("audio", null))
            }
            FirstAid(a.optString("kind", ""), a.optBoolean("call_emergency_services"),
                (0 until (steps?.length() ?: 0)).map { steps!!.getString(it) }, pace)
        }
        val provObj = o.optJSONObject("provenance")
        val prov = provObj?.let { pv ->
            val ev = pv.optJSONArray("evidence")
            Provenance(pv.optString("method", ""), pv.optString("generated_by", ""),
                (0 until (ev?.length() ?: 0)).map { i ->
                    val e = ev!!.getJSONObject(i)
                    Evidence(e.optString("publisher", ""), e.optString("title", ""),
                        e.optString("url", ""), e.optString("supports", null))
                },
                pv.optString("disclaimer", ""))
        }
        return Guidance(o.optBoolean("delivered"), o.optString("source", null),
            o.optString("content", ""),
            (0 until (refs?.length() ?: 0)).map { refs!!.getString(it) }, aid,
            prov, o.optString("translation_note", null),
            o.optString("specialist", null), o.optString("qrme_profile_id", null),
            o.optJSONObject("custody")?.let { c ->
                Custody(c.optBoolean("vaulted"), c.optString("pdi_key", null),
                    c.optString("note", null))
            },
            o.optJSONObject("specialist_offer")?.let { so ->
                SpecialistOffer(so.optBoolean("available"),
                    so.optString("label", ""),
                    so.optString("qrme_profile_id", ""),
                    so.optBoolean("sent"), so.optString("note", ""))
            })
    }


    /** What the deployment can and cannot reach. Read-only: the posture is
     *  set in the deployment's environment, not by somebody signed in. */
    /** What the Guardian carries across sessions. Counts and timings only. */
    suspend fun continuity(uid: String, token: String): ContinuityState =
        withContext(Dispatchers.IO) {
            val o = request("/continuity/$uid", "GET", null, token)
            val vec = o.optJSONObject("vector")
            val means = o.optJSONObject("meanings")
            ContinuityState(
                o.optBoolean("built"),
                o.optString("carries"),
                if (o.isNull("note")) null else o.optString("note"),
                o.optInt("observations"),
                o.optBoolean("conditioning"),
                vec?.keys()?.asSequence()?.associateWith { vec.optDouble(it) }
                    ?: emptyMap(),
                means?.keys()?.asSequence()?.associateWith { means.optString(it) }
                    ?: emptyMap(),
                if (o.isNull("method")) null else o.optString("method"))
        }

    /** Drop it — every derived thing has to be droppable by its subject. */
    suspend fun forgetContinuity(uid: String, token: String): Boolean =
        withContext(Dispatchers.IO) {
            request("/continuity/$uid", "DELETE", null, token)
                .optBoolean("forgotten")
        }

    /** The transparency half of the coach's long-term memory: what it can
     * find again, read back from the vault, droppable one moment at a time. */
    // The lookout: a page the vault re-reads on its schedule — JIM never
    // does the watching, and the capture stays sealed in the tandem.
    suspend fun lookouts(uid: String, token: String): LookoutList =
        withContext(Dispatchers.IO) {
            val o = request("/lookout/$uid", "GET", null, token)
            val arr = o.optJSONArray("lookouts")
            LookoutList(
                (0 until (arr?.length() ?: 0)).map { i ->
                    val w = arr!!.getJSONObject(i)
                    Lookout(
                        w.getString("id"), w.getString("url"),
                        w.getDouble("every_hours"),
                        if (w.isNull("status")) null else w.optString("status"),
                        if (w.isNull("next_run_at")) null
                        else w.optString("next_run_at"),
                        if (w.isNull("changed_at")) null
                        else w.optString("changed_at"),
                        if (w.isNull("trouble")) null
                        else w.optString("trouble"))
                },
                o.optBoolean("readable"))
        }

    suspend fun plantLookout(uid: String, url: String, everyHours: Double,
                             token: String): Boolean =
        withContext(Dispatchers.IO) {
            val body = JSONObject().put("url", url)
                .put("every_hours", everyHours)
            request("/lookout/$uid", "POST", body, token)
                .optBoolean("planted")
        }

    suspend fun lookoutPage(uid: String, lid: String, token: String): String =
        withContext(Dispatchers.IO) {
            val o = request("/lookout/$uid/$lid/page", "GET", null, token)
            (if (o.isNull("fetched_at")) "\u2014"
             else o.optString("fetched_at")) +
                " \u00b7 " + o.optInt("chars")
        }

    suspend fun dropLookout(uid: String, lid: String, token: String): Boolean =
        withContext(Dispatchers.IO) {
            request("/lookout/$uid/$lid", "DELETE", null, token)
                .optBoolean("removed")
        }

    suspend fun memoryShelf(uid: String, token: String): MemoryShelf =
        withContext(Dispatchers.IO) {
            val o = request("/memory/$uid", "GET", null, token)
            val arr = o.optJSONArray("memories")
            MemoryShelf(
                (0 until (arr?.length() ?: 0)).map { i ->
                    val m = arr!!.getJSONObject(i)
                    MemoryMoment(
                        m.getString("kind"), m.getString("ref"),
                        if (m.isNull("line")) null else m.optString("line"),
                        if (m.isNull("at")) null else m.optString("at"))
                },
                o.optBoolean("readable"), o.optInt("held"))
        }

    suspend fun forgetMemory(uid: String, kind: String, ref: String,
                             token: String): Boolean =
        withContext(Dispatchers.IO) {
            request("/memory/$uid/$kind/$ref", "DELETE", null, token)
                .optBoolean("forgotten")
        }

    suspend fun offlineStatus(): OfflinePosture = withContext(Dispatchers.IO) {
        val o = request("/offline/status", "GET", null, null)
        val gs = o.optJSONArray("guarantees")
        OfflinePosture(
            o.optBoolean("offline"),
            o.optBoolean("external_transmission_possible"),
            o.optString("local_destinations_allowed"),
            (0 until (gs?.length() ?: 0)).map { gs!!.getString(it) })
    }

    /**
     * Everything this deployment holds about a person, by table.
     *
     * The erase has been on the console since it existed and this had no
     * route at all. A person whose only device is a phone is exactly the
     * person who cannot use a desktop console to get their data out.
     */
    suspend fun exportEverything(uid: String, token: String): Pair<Int, Int> =
        withContext(Dispatchers.IO) {
            val o = request("/data/$uid", "GET", null, token)
            val tables = o.optJSONObject("tables") ?: org.json.JSONObject()
            var rows = 0
            val names = tables.keys()
            while (names.hasNext()) {
                rows += tables.optJSONArray(names.next())?.length() ?: 0
            }
            Pair(tables.length(), rows)
        }

    /**
     * The other direction, and the one this shell had no door for either.
     *
     * A person whose only device is a phone could take their data from
     * 0.60.0 and could not end it. Both halves of *it is yours* have to be
     * reachable from the same place or only one of them is true. Returns how
     * many rows went, so the screen can say something true afterwards.
     */
    suspend fun eraseEverything(uid: String, token: String): Int =
        withContext(Dispatchers.IO) {
            val o = request("/data/$uid", "DELETE", null, token)
            val gone = o.optJSONObject("deleted") ?: org.json.JSONObject()
            var rows = 0
            val names = gone.keys()
            while (names.hasNext()) rows += gone.optInt(names.next())
            rows
        }


    data class ProblemRow(val op: String, val statusCode: Int, val count: Int,
                          val source: String, val appVersion: String,
                          val platform: String, val day: String)

    // The failure aggregate this backend keeps. Reading is the operator's:
    // the problems key as the token, or nothing when asking from the machine
    // the backend runs on.
    suspend fun problemRows(key: String): List<ProblemRow> {
        val o = JSONObject(request("/v1/problems",
            token = key.ifBlank { null }))
        val arr = o.optJSONArray("rows") ?: return emptyList()
        return (0 until arr.length()).map { i ->
            val r = arr.getJSONObject(i)
            ProblemRow(r.optString("op"), r.optInt("status_code"),
                r.optInt("count"), r.optString("source"),
                r.optString("app_version"), r.optString("platform"),
                r.optString("day"))
        }
    }

    private suspend fun request(
        path: String, method: String = "GET",
        body: JSONObject? = null, token: String? = null,
        raw: ByteArray? = null,
    ): JSONObject = withContext(Dispatchers.IO) {
        val conn = (URL(base + path).openConnection() as HttpURLConnection).apply {
            // HttpURLConnection's verb list is hard-coded and PATCH is not
            // on it — a ProtocolException, not a preference. The server
            // honours x-http-method-override for PATCH alone, so the call
            // sites keep saying PATCH and the wire carries the override.
            requestMethod = if (method == "PATCH") "POST" else method
            if (method == "PATCH") {
                setRequestProperty("x-http-method-override", "PATCH")
            }
            setRequestProperty("content-type", "application/json")
            // The language the reader actually speaks. Every sentence the
            // backend composes on a public route is chosen from this
            // header, and no native shell was sending it.
            setRequestProperty("accept-language", L10n.deviceLanguage())
            llmKey.takeIf { it.isNotEmpty() }?.let {
                setRequestProperty("x-llm-api-key", it) }
            signupKey.takeIf { it.isNotEmpty() }?.let {
                setRequestProperty("x-signup-key", it) }
            token?.let { setRequestProperty("authorization", "Bearer $it") }
            connectTimeout = 8000; readTimeout = 8000
            if (body != null) {
                doOutput = true
                outputStream.use { it.write(body.toString().toByteArray()) }
            } else if (raw != null) {
                doOutput = true
                outputStream.use { it.write(raw) }
            }
        }
        val code = try {
            conn.responseCode
        } catch (e: Exception) {
            // Never reached a server. Recorded as status 0; the thrown error
            // still carries its message to the person, who owns it.
            Problems.record(method, path, 0)
            throw e
        }
        val text = (if (code in 200..299) conn.inputStream else conn.errorStream)
            ?.bufferedReader()?.use { it.readText() } ?: ""
        conn.disconnect()
        if (code !in 200..299) {
            // The status and the operation, never the detail below: these
            // messages quote what the person typed, which is theirs to read
            // and nobody's to keep.
            Problems.record(method, path, code)
            // `optString` coerces a JSONArray through toString(), so a 422 —
            // whose `detail` is pydantic's list of rows — reached the person
            // as raw JSON. `message` is the sentence the backend composes
            // beside the rows; a string `detail` still wins for everything else.
            val said = runCatching {
                val body = JSONObject(text)
                body.optString("message").ifBlank {
                    when (val detail = body.opt("detail")) {
                        is String -> detail
                        // A plan refusal (402) puts a dict in detail; its
                        // `message` is the sentence composed for the reader.
                        is JSONObject -> detail.optString("message")
                        else -> ""
                    }
                }
            }.getOrNull()
            throw ApiException(if (said.isNullOrBlank()) "HTTP $code" else said)
        }
        if (text.isBlank()) JSONObject() else JSONObject(text)
    }

    suspend fun enroll(name: String, birthdate: String,
                       language: String? = null): EnrollResult {
        val body = JSONObject()
            .put("display_name", name).put("birthdate", birthdate).put("terms_consent", true)
        if (!language.isNullOrBlank() && language != "en") body.put("language", language)
        val o = request("/enroll", "POST", body)
        return EnrollResult(o.getString("id"), o.getString("display_name"), o.getString("user_token"))
    }

    suspend fun monitor(uid: String, token: String, heartRate: Int, stress: Double): MonitorResult {
        val o = request("/monitor/$uid", "POST",
            JSONObject().put("heart_rate", heartRate).put("stress_level", stress), token)
        return MonitorResult(
            o.optBoolean("detected"),
            o.optString("condition", null),
            o.optString("severity", null),
            o.optString("reason", null),
            parseGuidance(o.optJSONObject("guidance")),
        )
    }

    // ---- family: a parent sets up and watches over a child's account ----

    suspend fun enrollChild(gid: String, token: String, name: String,
                            birthdate: String, phone: String?): ChildCreated {
        val body = JSONObject().put("display_name", name)
            .put("birthdate", birthdate)
        if (!phone.isNullOrBlank()) body.put("guardian_phone", phone)
        val o = request("/guardians/$gid/children", "POST", body, token)
        return ChildCreated(o.getString("id"), o.getString("child_token"),
            o.optString("oversight", ""), o.optString("sensitivity", null))
    }

    suspend fun children(gid: String, token: String): List<ChildSummary> {
        val arr = getArray("/guardians/$gid/children", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            ChildSummary(o.getString("child_id"), o.optString("display_name", ""),
                o.optInt("age"), o.optString("oversight", ""))
        }
    }

    suspend fun childOverview(gid: String, cid: String,
                              token: String): ChildOverview {
        val o = request("/guardians/$gid/children/$cid", token = token)
        val ev = o.optJSONArray("events")
        return ChildOverview(o.optString("display_name", null),
            o.optString("oversight", ""), o.optInt("critical_events"),
            (0 until (ev?.length() ?: 0)).map { i ->
                val e = ev!!.getJSONObject(i)
                ChildEvent(e.optString("type", ""),
                    e.optString("condition", null),
                    e.optString("severity", null))
            },
            o.optString("privacy_note", null), o.optString("note", null))
    }

    /**
     * The guardian steps back. A guardian link is a standing relationship —
     * one adult able to see another person's events, light and escalations —
     * and it outlives the reason for it: children grow up, custody changes,
     * households end. iOS has been able to end one since the link was built;
     * this shell and the desktop could begin one and not end one.
     */
    suspend fun unlinkChild(gid: String, cid: String, token: String) {
        request("/guardians/$gid/children/$cid", "DELETE", null, token)
    }

    suspend fun setFamilyControls(gid: String, cid: String, token: String,
                                  paused: Boolean?, quietStart: String?,
                                  quietEnd: String?): String {
        val body = JSONObject()
        paused?.let { body.put("paused", it) }
        quietStart?.let { body.put("quiet_start", it) }
        quietEnd?.let { body.put("quiet_end", it) }
        return request("/guardians/$gid/children/$cid/controls", "PUT",
            body, token).optString("note", "applied")
    }

    suspend fun guardianWatch(gid: String, token: String): GuardianFace {
        val o = request("/guardians/$gid/watch", token = token)
        val arr = o.optJSONArray("children")
        return GuardianFace((0 until (arr?.length() ?: 0)).map { i ->
            val c = arr!!.getJSONObject(i)
            GuardianChild(c.getString("child_id"),
                c.optString("display_name", ""), c.optString("light", "idle"),
                c.optInt("critical_24h"), c.optInt("escalations_24h"),
                c.optBoolean("paused"), c.optString("quiet_hours", null))
        }, o.optString("haptic", null))
    }

    suspend fun checkin(uid: String, token: String, mood: Int, energy: Int, note: String): CheckinResult {
        val o = request("/checkin/$uid", "POST",
            JSONObject().put("mood", mood).put("energy", energy).put("note", note), token)
        val g = o.optJSONObject("guardian")?.optJSONObject("guidance")
        return CheckinResult(o.optString("id", ""), parseGuidance(g))
    }

    suspend fun baseline(uid: String, token: String): List<BaselineMetric> {
        // /baseline returns a JSON array; wrap for the shared request() helper.
        val arr = withContext(Dispatchers.IO) {
            val conn = (URL("$base/baseline/$uid").openConnection() as HttpURLConnection).apply {
                    // One of the four connections in this file the shared
                    // helper's accept-language line never reached.
                    setRequestProperty("accept-language", L10n.deviceLanguage())
            llmKey.takeIf { it.isNotEmpty() }?.let {
                setRequestProperty("x-llm-api-key", it) }
            signupKey.takeIf { it.isNotEmpty() }?.let {
                setRequestProperty("x-signup-key", it) }
                setRequestProperty("authorization", "Bearer $token")
                connectTimeout = 8000; readTimeout = 8000
            }
            val text = conn.inputStream.bufferedReader().use { it.readText() }
            conn.disconnect(); org.json.JSONArray(text)
        }
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            BaselineMetric(
                o.getString("metric"),
                if (o.isNull("value")) null else o.optDouble("value"),
                o.optString("state", null),
                if (o.has("samples")) o.optInt("samples") else null,
            )
        }
    }

    // ---- life coach & insights ----

    // ---- vault custody: sealed tandem exchanges ----

    suspend fun custody(uid: String, token: String): CustodyList {
        val o = request("/custody/$uid", token = token)
        val arr = o.optJSONArray("records")
        return CustodyList(
            (0 until (arr?.length() ?: 0)).map { arr!!.getString(it) },
            if (o.isNull("chain_intact")) null else o.getBoolean("chain_intact"))
    }

    suspend fun custodyProvenance(uid: String, token: String,
                                  key: String): CustodyProvenance {
        val o = request("/custody/$uid/provenance?key=" +
            java.net.URLEncoder.encode(key, "UTF-8"), token = token)
        val chain = o.optJSONObject("chain")
        return CustodyProvenance(
            o.optString("origin", ""),
            o.optJSONObject("sealed")?.optString("cipher", null),
            o.optJSONObject("audit")?.optInt("count") ?: 0,
            if (chain == null || chain.isNull("intact")) null
            else chain.getBoolean("intact"))
    }

    // --- engaged sessions -------------------------------------------------
    //
    // The session you leave running. See jim/engaged.py for what it may touch
    // and why the reach is a written list rather than this token's full
    // authority.

    private fun watchRow(o: JSONObject) = StandingWatch(
        o.getString("id"), o.optString("topic", ""),
        if (o.isNull("area")) null else o.optString("area"),
        o.optString("created_at", ""))

    private fun actRow(o: JSONObject) = EngagedAct(
        o.getString("id"), o.optString("tool", ""), o.optString("says", ""),
        o.optInt("answered"), o.optString("created_at", ""),
        if (o.isNull("undone_at")) null else o.optString("undone_at"),
        o.optBoolean("reversible", false),
        if (o.isNull("irreversible_because")) null
        else o.optString("irreversible_because"))

    private fun watches(arr: JSONArray?): List<StandingWatch> =
        (0 until (arr?.length() ?: 0)).map { watchRow(arr!!.getJSONObject(it)) }

    /**
     * What an engaged session can do to you, in sentences.
     *
     * No token, deliberately: this is how somebody decides whether to open
     * one at all, and a list of what a feature would be allowed to touch is
     * not the feature.
     */
    suspend fun engagedReach(): EngagedReach {
        val o = request("/engaged/reach")
        val arr = o.optJSONArray("can") ?: JSONArray()
        return EngagedReach(
            (0 until arr.length()).map { i ->
                val t = arr.getJSONObject(i)
                EngagedTool(t.getString("name"), t.optString("says", ""),
                    t.optBoolean("acts", false),
                    t.optBoolean("reversible", false),
                    if (t.isNull("irreversible_because")) null
                    else t.optString("irreversible_because"))
            },
            o.optInt("tools_per_turn"), o.optInt("acts_per_session"),
            o.optInt("watch_ceiling"))
    }

    private fun session(o: JSONObject): EngagedSession {
        val turns = o.optJSONArray("turns") ?: JSONArray()
        val acted = o.optJSONArray("acted") ?: JSONArray()
        return EngagedSession(
            o.optBoolean("engaged", false),
            if (o.isNull("id")) null else o.optString("id"),
            if (o.isNull("area")) null else o.optString("area"),
            (0 until turns.length()).map { i ->
                val t = turns.getJSONObject(i)
                EngagedTurnRow(t.optString("role", ""), t.optString("content", ""),
                    t.optString("created_at", ""))
            },
            (0 until acted.length()).map { actRow(acted.getJSONObject(it)) },
            watches(o.optJSONArray("watches")))
    }

    suspend fun engaged(uid: String, token: String): EngagedSession =
        session(request("/engaged/$uid", token = token))

    suspend fun engage(uid: String, token: String,
                       area: String = "personal_growth"): EngagedSession =
        session(request("/engaged/$uid", "POST",
            JSONObject().put("area", area), token))

    suspend fun engagedTurn(uid: String, token: String,
                            message: String): EngagedTurnResult {
        val o = request("/engaged/$uid/turn", "POST",
            JSONObject().put("message", message), token)
        // `did`, not `acted`: a session's `acted` is the trail of completed
        // changes, and a turn's list includes refusals, which are not acts.
        val arr = o.optJSONArray("did") ?: JSONArray()
        val pv = o.optJSONObject("provenance")
        return EngagedTurnResult(
            o.optString("reply", ""),
            (0 until arr.length()).map { i ->
                val st = arr.getJSONObject(i)
                EngagedStep(
                    if (st.isNull("tool")) null else st.optString("tool"),
                    if (st.isNull("answered")) null else st.optInt("answered"),
                    if (st.isNull("says")) null else st.optString("says"),
                    st.optBoolean("acts", false),
                    st.optBoolean("reversible", false),
                    if (st.isNull("irreversible_because")) null
                    else st.optString("irreversible_because"),
                    if (st.isNull("refused")) null else st.optString("refused"))
            },
            if (o.isNull("stopped")) null else o.optString("stopped"),
            pv?.optBoolean("degraded", false) ?: false,
            pv?.optString("generated_by", "") ?: "",
            watches(o.optJSONArray("watches")))
    }

    /**
     * End the engagement and hand it over. `topics` becomes the standing
     * watch list the offline Guardian keeps while this person is away.
     */
    suspend fun engagedSignOff(uid: String, token: String,
                               topics: List<String>): EngagedSignOff {
        val body = JSONObject().put("topics", JSONArray(topics))
        val o = request("/engaged/$uid/sign-off", "POST", body, token)
        return EngagedSignOff(o.optBoolean("signed_off", false),
            o.optInt("deposited"), watches(o.optJSONArray("watches")))
    }

    suspend fun engagedActs(uid: String, token: String): List<EngagedAct> {
        val arr = getArray("/engaged/$uid/acts", token)
        return (0 until arr.length()).map { actRow(arr.getJSONObject(it)) }
    }

    /** Take one act back, through the door that would have undone it by hand. */
    suspend fun engagedUndo(uid: String, token: String, actId: String): Boolean =
        request("/engaged/$uid/acts/$actId/undo", "POST", token = token)
            .optBoolean("undone", false)

    /**
     * The groups of switches this session may touch, and which are on.
     *
     * The connectors screen turned around to face this account's own
     * settings. Somebody who wants a thing switched on or off should be able
     * to say so out loud; this is where they say the Guardian may.
     */
    suspend fun engagedPermits(uid: String, token: String): EngagedPermits {
        val o = request("/engaged/$uid/permits", token = token)
        val arr = o.optJSONArray("groups") ?: JSONArray()
        return EngagedPermits(
            (0 until arr.length()).map { i ->
                val a = arr.getJSONObject(i)
                val tools = a.optJSONArray("tools") ?: JSONArray()
                EngagedPermitArea(
                    a.getString("area"), a.optString("says", ""),
                    a.optString("standing", "opened"),
                    a.optBoolean("granted", false),
                    if (a.isNull("decided_at")) null else a.optString("decided_at"),
                    (0 until tools.length()).map { tools.getString(it) })
            },
            o.optString("note", ""))
    }

    /** Switch one group on or off. Both directions, because a grant that
     *  cannot be taken back is not a grant. */
    suspend fun engagedSetPermit(uid: String, token: String, area: String,
                                 granted: Boolean): Boolean =
        request("/engaged/$uid/permits/$area", "PUT",
            JSONObject().put("granted", granted), token)
            .optBoolean("granted", false)

    suspend fun engagedWatches(uid: String, token: String): List<StandingWatch> {
        val arr = getArray("/engaged/$uid/watches", token)
        return (0 until arr.length()).map { watchRow(arr.getJSONObject(it)) }
    }

    suspend fun engagedWatch(uid: String, token: String,
                             topic: String): StandingWatch =
        watchRow(request("/engaged/$uid/watches", "POST",
            JSONObject().put("topic", topic), token))

    suspend fun engagedClearWatch(uid: String, token: String,
                                  watchId: String): Boolean =
        request("/engaged/$uid/watches/$watchId", "DELETE", token = token)
            .optBoolean("cleared", false)

    // The ways back the undo trail replays — and doors a person should always
    // have had. Until an engaged session needed to take a check-in back,
    // nothing in this product could delete one.
    suspend fun removeCheckin(uid: String, token: String, checkinId: String) {
        request("/checkin/$uid/$checkinId", "DELETE", token = token)
    }

    suspend fun removeJournal(uid: String, token: String, entryId: String) {
        request("/journal/$uid/$entryId", "DELETE", token = token)
    }

    suspend fun removeGoal(uid: String, token: String, goalId: String) {
        request("/goals/$uid/$goalId", "DELETE", token = token)
    }

    suspend fun removeHabit(uid: String, token: String, habitId: String) {
        request("/habits/$uid/$habitId", "DELETE", token = token)
    }

    suspend fun unlogHabit(uid: String, token: String, habitId: String,
                           day: String) {
        request("/habits/$uid/$habitId/log/$day", "DELETE", token = token)
    }

    suspend fun coach(uid: String, token: String, area: String, message: String): Guidance {
        val o = request("/coach/$uid", "POST",
            JSONObject().put("area", area).put("message", message), token)
        return parseGuidance(o)!!
    }

    // The offline coach's store and syllabus (jim/pipeline.py): what the
    // stack predicts from, what JIM should study next, and the one-press
    // study that imports the findings.
    suspend fun coachStore(uid: String, token: String): CoachStore {
        val o = request("/coach/$uid/store", token = token)
        fun rows(key: String): List<CoachStoreEntry> {
            val arr = o.optJSONArray(key) ?: return emptyList()
            return (0 until arr.length()).map { i ->
                val e = arr.getJSONObject(i)
                CoachStoreEntry(e.getString("topic"), e.getString("lesson"),
                    e.getString("source"),
                    if (e.isNull("model")) null else e.optString("model"))
            }
        }
        return CoachStore(o.getInt("pack"), rows("excursions"), rows("deposits"))
    }

    suspend fun coachCurriculum(uid: String, token: String): CoachCurriculum {
        val o = request("/coach/$uid/curriculum", token = token)
        val arr = o.getJSONArray("suggested")
        return CoachCurriculum((0 until arr.length()).map { i ->
            val s = arr.getJSONObject(i)
            CoachSuggestion(s.getString("area"), s.getString("topic"),
                s.getString("why"))
        }, o.getString("note"))
    }

    suspend fun coachStudy(uid: String, token: String, topic: String?,
                           area: String?): CoachStudied {
        val body = JSONObject()
        if (topic != null) body.put("topic", topic)
        if (area != null) body.put("area", area)
        val o = request("/coach/$uid/study", "POST", body, token)
        return CoachStudied(o.getString("studied"), o.getBoolean("folded"))
    }

    private fun liaisonOf(o: JSONObject) = LiaisonRow(
        o.getString("id"), o.optString("about", ""), o.optString("task", ""),
        o.optBoolean("running"),
        if (o.isNull("ended_because")) null else o.optString("ended_because"),
        o.optString("opened_at", ""),
        o.optBoolean("you_agreed"), o.optBoolean("they_agreed"),
        o.optBoolean("holds_it_open"))

    /** Open a link to another guardian. Refused unless both already had the
     *  other stored. */
    suspend fun openLiaison(uid: String, token: String, otherId: String,
                            about: String = ""): LiaisonRow =
        liaisonOf(request("/liaisons/$uid", "POST",
            JSONObject().put("other_id", otherId).put("about", about), token))

    suspend fun liaisons(uid: String, token: String): List<LiaisonRow> {
        val arr = JSONArray(request("/liaisons/$uid", token = token).toString())
        return (0 until arr.length()).map { liaisonOf(arr.getJSONObject(it)) }
    }

    /** Their own guardian's half, and only theirs. */
    suspend fun liaisonHalf(uid: String, token: String,
                            linkId: String): LiaisonHalf {
        val o = request("/liaisons/$uid/$linkId", token = token)
        fun lines(key: String): List<String> {
            val arr = o.optJSONArray(key) ?: JSONArray()
            return (0 until arr.length()).map { arr.getString(it) }
        }
        return LiaisonHalf(o.getString("link_id"), o.optString("about", ""),
            o.optString("task", ""), o.optBoolean("running"),
            lines("said_by_mine"), lines("said_to_mine"))
    }

    suspend fun liaisonSaid(uid: String, token: String, linkId: String,
                            body: String) {
        request("/liaisons/$uid/$linkId/said", "POST",
            JSONObject().put("body", body), token)
    }

    /** The work that outlives the call, once both sides have agreed to it.
     *  Naming it counts as the namer's own yes and nothing more. */
    suspend fun liaisonTask(uid: String, token: String, linkId: String,
                            task: String): LiaisonRow =
        liaisonOf(request("/liaisons/$uid/$linkId/task", "PUT",
            JSONObject().put("task", task), token))

    /** The other side's yes, to the task as it stands. No wording of its
     *  own: a second party passing their own text would be proposing rather
     *  than agreeing, and the link could then be held open by two sentences
     *  that only looked like one agreement. */
    suspend fun liaisonAgreed(uid: String, token: String,
                              linkId: String): LiaisonRow =
        liaisonOf(request("/liaisons/$uid/$linkId/agreed", "PUT",
            token = token))

    suspend fun closeLiaison(uid: String, token: String, linkId: String,
                             why: String): LiaisonRow =
        liaisonOf(request("/liaisons/$uid/$linkId?why=$why", "DELETE",
            token = token))

    private fun stretchOf(o: JSONObject) = Stretch(
        o.getString("id"), o.optString("monitor", ""), o.optString("about", ""),
        o.optBoolean("others_told"), o.optBoolean("catches_others"),
        o.optBoolean("running"), o.optString("opened_at", ""),
        if (o.isNull("ended_at")) null else o.optString("ended_at"),
        o.optInt("moments"), o.optInt("kept"))

    private fun pairedOf(o: JSONObject) = MicPaired(
        o.optBoolean("paired"),
        if (o.isNull("with")) null else o.optString("with"),
        o.optBoolean("yours_listening"), o.optBoolean("theirs_listening"),
        o.optBoolean("both"))

    /** Say who else is on this call with their own channel 2. */
    suspend fun pairMic(uid: String, token: String, otherId: String,
                        about: String = ""): MicPaired =
        pairedOf(request("/users/$uid/mic/pair", "POST",
            JSONObject().put("other_id", otherId).put("about", about), token))

    suspend fun micPaired(uid: String, token: String): MicPaired =
        pairedOf(request("/users/$uid/mic/pair", token = token))

    suspend fun unpairMic(uid: String, token: String): MicPaired =
        pairedOf(request("/users/$uid/mic/pair", "DELETE", token = token))

    /** What the monitors noticed, and what each could ever notice. */
    suspend fun cues(uid: String, token: String): CuesSeen {
        val o = request("/cues/$uid", token = token)
        val rows = o.optJSONArray("lately") ?: JSONArray()
        val can = o.optJSONObject("can_read") ?: JSONObject()
        return CuesSeen(
            (0 until rows.length()).map {
                val c = rows.getJSONObject(it)
                Cue(c.optString("cue", ""), c.optString("severity", ""),
                    c.optString("says", ""), c.optString("monitor", ""),
                    c.optString("reference", ""), c.optString("tier", ""),
                    c.optString("at", ""))
            },
            can.keys().asSequence().associateWith { name ->
                val arr = can.optJSONArray(name) ?: JSONArray()
                (0 until arr.length()).map { i -> arr.getString(i) }
            })
    }

    /** What was sensed today and what survived of it. */
    suspend fun theDay(uid: String, token: String): TheDay {
        val o = request("/day/$uid", token = token)
        val d = o.optJSONObject("account") ?: JSONObject()
        val mons = d.optJSONArray("monitors") ?: JSONArray()
        val kept = o.optJSONArray("survived") ?: JSONArray()
        val strs = o.optJSONArray("stretches") ?: JSONArray()
        return TheDay(
            DayAccount(d.optString("date", ""),
                (0 until mons.length()).map {
                    val m = mons.getJSONObject(it)
                    val why = m.optJSONArray("because") ?: JSONArray()
                    MonitorDay(m.getString("monitor"), m.optInt("sensed"),
                        m.optInt("kept"), m.optInt("dropped"),
                        (0 until why.length()).map { i -> why.getString(i) },
                        m.optString("holds", ""))
                },
                d.optInt("sensed"), d.optInt("kept"), d.optBoolean("quiet")),
            (0 until kept.length()).map {
                val k = kept.getJSONObject(it)
                Moment(k.getString("id"), k.optString("monitor", ""),
                    k.optString("content", ""),
                    if (k.isNull("stretch_id")) null else k.optString("stretch_id"),
                    k.optString("sensed_at", ""))
            },
            (0 until strs.length()).map { stretchOf(strs.getJSONObject(it)) })
    }

    /** Begin a meeting or working stretch. Where the monitor catches other
     *  people, somebody has to say they were told — asked again here. */
    suspend fun openStretch(uid: String, token: String, monitor: String,
                            about: String = "",
                            othersTold: Boolean = false): Stretch =
        stretchOf(request("/day/$uid/stretches", "POST",
            JSONObject().put("monitor", monitor).put("about", about)
                .put("others_told", othersTold), token))

    suspend fun closeStretch(uid: String, token: String,
                             stretchId: String): Stretch =
        stretchOf(request("/day/$uid/stretches/$stretchId", "DELETE",
            token = token))

    /** Drop what was kept of one moment; the fact that it happened stays. */
    suspend fun forgetMoment(uid: String, token: String, momentId: String) {
        request("/day/$uid/moments/$momentId", "DELETE", token = token)
    }

    private fun monitorsOf(arr: JSONArray) = (0 until arr.length()).map {
        val o = arr.getJSONObject(it)
        val senses = o.optJSONArray("senses") ?: JSONArray()
        MonitorRow(o.getString("name"),
            (0 until senses.length()).map { i -> senses.getString(i) },
            o.optString("placing", ""), o.optString("says", ""),
            o.optString("holds", ""), o.optBoolean("catches_others"),
            o.optBoolean("on"),
            if (o.isNull("device")) null else o.optString("device"),
            o.optBoolean("others_told"), o.optBoolean("keeping"))
    }

    /** Everything that can be plugged in, off rows included. */
    suspend fun monitors(uid: String, token: String): List<MonitorRow> =
        monitorsOf(JSONArray(request("/monitors/$uid", token = token).toString()))

    /** Switch one on. Anything that senses other people is refused until
     *  `othersTold` says they know; keeping is its own decision. */
    suspend fun plugMonitor(uid: String, token: String, name: String,
                            deviceName: String = "",
                            othersTold: Boolean = false,
                            keeping: Boolean = false): List<MonitorRow> {
        val body = JSONObject().put("device_name", deviceName)
            .put("others_told", othersTold).put("keeping", keeping)
        return monitorsOf(JSONArray(
            request("/monitors/$uid/$name", "PUT", body, token).toString()))
    }

    suspend fun unplugMonitor(uid: String, token: String,
                              name: String): List<MonitorRow> =
        monitorsOf(JSONArray(
            request("/monitors/$uid/$name", "DELETE", token = token).toString()))

    /** Anything a monitor perceives comes in through here, and through the
     *  switch check first. */
    suspend fun monitorSensed(uid: String, token: String, name: String) {
        request("/monitors/$uid/$name/sensed", "POST", token = token)
    }

    private fun noticesOf(arr: JSONArray) = (0 until arr.length()).map {
        val o = arr.getJSONObject(it)
        CallNotice(o.optString("language", ""), o.optString("words", ""))
    }

    private fun stringsOf(arr: JSONArray?) =
        (0 until (arr?.length() ?: 0)).map { arr!!.getString(it) }

    /** Set up an assisted call. It is not listening: what comes back is the
     *  notice to play. `number` is read for the language and dropped. */
    suspend fun openCall(uid: String, token: String, route: String,
                         recording: Boolean = false,
                         number: String? = null): AssistedCall {
        val body = JSONObject().put("route", route).put("recording", recording)
        if (number != null) body.put("number", number)
        val o = request("/calls/$uid", "POST", body, token)
        return AssistedCall(o.getString("id"), o.optBoolean("listening"),
            o.optString("route", ""), o.optBoolean("recording"),
            noticesOf(o.optJSONArray("notices") ?: JSONArray()),
            o.optString("said", ""), stringsOf(o.optJSONArray("spoken_in")),
            o.optString("language_from", ""))
    }

    /** The notice went out. Confirmed by whatever played it. */
    suspend fun callAnnounced(uid: String, callId: String, token: String) {
        request("/calls/$uid/$callId/announced", "POST", token = token)
    }

    suspend fun calls(uid: String, token: String): List<CallRow> {
        val arr = JSONArray(request("/calls/$uid", token = token).toString())
        return (0 until arr.length()).map {
            val o = arr.getJSONObject(it)
            CallRow(o.getString("id"), o.optString("route", ""),
                o.optString("said", ""), stringsOf(o.optJSONArray("spoken_in")),
                if (o.isNull("announced_at")) null else o.optString("announced_at"),
                o.optBoolean("listened"), o.optString("opened_at", ""))
        }
    }

    suspend fun endCall(uid: String, callId: String, token: String) {
        request("/calls/$uid/$callId", "DELETE", token = token)
    }

    /** Anything the call hands the agent goes through here, and through the
     *  announcement check first. */
    suspend fun callHeard(uid: String, callId: String, token: String) {
        request("/calls/$uid/$callId/heard", "POST", token = token)
    }

    /** A draft, read on the device and dropped. Nothing is stored and
     *  nothing is edited — applying a remark is the person's own act. */
    suspend fun alongside(uid: String, token: String, draft: String,
                          area: String? = null): Alongside {
        val body = JSONObject().put("draft", draft)
        if (area != null) body.put("area", area)
        val o = request("/alongside/$uid", "POST", body, token)
        val arr = o.optJSONArray("remarks") ?: JSONArray()
        return Alongside((0 until arr.length()).map { i ->
            val r = arr.getJSONObject(i)
            val why = r.optJSONArray("because") ?: JSONArray()
            Remark(r.getString("kind"), r.optString("says", ""),
                (0 until why.length()).map { why.getString(it) },
                if (r.isNull("door")) null else r.optString("door"))
        }, if (o.isNull("quiet_because")) null
           else o.optString("quiet_because"))
    }

    private fun errandOf(o: JSONObject) = Errand(
        o.getString("id"), o.optString("topic", ""), o.optString("area", ""),
        o.optString("why", ""), o.optString("excursion_id", ""),
        o.optInt("redactions"), o.optBoolean("left_host"),
        o.optString("opened_at", ""))

    private fun errandsOf(arr: JSONArray) =
        (0 until arr.length()).map { errandOf(arr.getJSONObject(it)) }

    /** What it went and learned unasked, and what is left to spend today. */
    suspend fun errands(uid: String, token: String): ErrandLedger {
        val o = request("/errands/$uid", token = token)
        val due = o.optJSONArray("due") ?: JSONArray()
        return ErrandLedger(
            errandsOf(o.optJSONArray("errands") ?: JSONArray()),
            (0 until due.length()).map {
                val s = due.getJSONObject(it)
                CoachSuggestion(s.getString("area"), s.getString("topic"),
                    s.getString("why"))
            },
            o.optInt("spent_today"), o.optInt("daily"),
            o.optBoolean("permitted"))
    }

    /** Which agent is running, and which tasks are still running — one read
     *  across the five things that can be going at once, so somebody does
     *  not have to know which screen owns which. It reads and never acts. */
    suspend fun underway(uid: String, token: String): UnderwayWindow {
        val o = request("/underway/$uid", token = token)
        val rows = o.optJSONArray("underway") ?: JSONArray()
        val spend = o.optJSONObject("spend") ?: JSONObject()
        return UnderwayWindow(
            (0 until rows.length()).map {
                val r = rows.getJSONObject(it)
                UnderwayRow(r.getString("kind"),
                    if (r.isNull("id")) null else r.optString("id"),
                    if (r.isNull("term")) null else r.optString("term"),
                    if (r.isNull("words")) null else r.optString("words"),
                    if (r.isNull("since")) null else r.optString("since"),
                    r.getString("why"))
            },
            o.optBoolean("quiet"),
            errandsOf(o.optJSONArray("today") ?: JSONArray()),
            spend.optInt("spent_today"), spend.optInt("daily"),
            spend.optBoolean("permitted"))
    }

    private fun noticeOf(o: JSONObject) = Notice(
        o.getString("id"), o.optString("event_id", ""),
        o.optString("condition", ""), o.optString("severity", ""),
        o.optString("settled_by", ""), o.optString("said", ""),
        o.optString("noticed_at", ""))

    private fun noticesOf(arr: JSONArray) =
        (0 until arr.length()).map { noticeOf(arr.getJSONObject(it)) }

    private fun blockedOf(arr: JSONArray) = (0 until arr.length()).map {
        arr.getJSONObject(it).optString("condition", "")
    }

    /** What the coach noticed during the day, and what settled each one. */
    suspend fun noticed(uid: String, token: String): NoticeLedger {
        val o = request("/noticed/$uid", token = token)
        val st = o.optJSONObject("settlement") ?: JSONObject()
        return NoticeLedger(
            noticesOf(o.optJSONArray("handled") ?: JSONArray()),
            blockedOf(o.optJSONArray("waiting") ?: JSONArray()),
            NoticeSettlement(st.optInt("settled_free"), st.optInt("settled_paid"),
                if (st.isNull("free_share")) null else st.optDouble("free_share"),
                st.optBoolean("permitted"), st.optInt("spent_today"),
                st.optInt("daily")))
    }

    /** The situational half of the ladder: the offline coach settles what it
     *  can for nothing, and only what it cannot becomes a paid turn. No
     *  budget refusal — a spent day still runs the free half. */
    suspend fun runNoticed(uid: String, token: String): NoticedRun {
        val o = request("/noticed/$uid", "POST", token = token)
        return NoticedRun(
            noticesOf(o.optJSONArray("by_coach") ?: JSONArray()),
            noticesOf(o.optJSONArray("by_jim") ?: JSONArray()),
            blockedOf(o.optJSONArray("over_budget") ?: JSONArray()),
            o.optInt("remaining_today"), o.optBoolean("nothing_noticed"))
    }

    /** Refused without the permit, and again once the day is spent — two
     *  different sentences, because they are two different things. */
    suspend fun runErrands(uid: String, token: String): ErrandsRun {
        val o = request("/errands/$uid", "POST", token = token)
        return ErrandsRun(errandsOf(o.optJSONArray("errands") ?: JSONArray()),
            o.optInt("remaining_today"), o.optBoolean("nothing_to_study"))
    }

    /** Send this question to the QRME specialist covering the area. */
    suspend fun coachSpecialist(uid: String, token: String, area: String,
                                message: String): SpecialistAnswer {
        val o = request("/coach/$uid/specialist", "POST",
            JSONObject().put("area", area).put("message", message), token)
        val who = o.optJSONObject("specialist")
        val prov = o.optJSONObject("provenance")
        return SpecialistAnswer(
            o.optBoolean("delivered"),
            if (o.isNull("content")) null else o.optString("content"),
            if (o.isNull("reason")) null else o.optString("reason"),
            if (o.isNull("note")) null else o.optString("note"),
            o.optBoolean("held_for_owner_approval"),
            who?.optString("label"),
            prov?.optString("method"),
            prov?.optString("shared"))
    }

    private suspend fun getArray(path: String, token: String? = null): org.json.JSONArray = withContext(Dispatchers.IO) {
        val conn = (URL("$base$path").openConnection() as HttpURLConnection).apply {
                    // One of the four connections in this file the shared
                    // helper's accept-language line never reached.
                    setRequestProperty("accept-language", L10n.deviceLanguage())
            llmKey.takeIf { it.isNotEmpty() }?.let {
                setRequestProperty("x-llm-api-key", it) }
            signupKey.takeIf { it.isNotEmpty() }?.let {
                setRequestProperty("x-signup-key", it) }
            token?.let { setRequestProperty("authorization", "Bearer $it") }
            connectTimeout = 8000; readTimeout = 8000
        }
        val text = conn.inputStream.bufferedReader().use { it.readText() }
        conn.disconnect(); org.json.JSONArray(text)
    }

    suspend fun goals(uid: String, token: String): List<Goal> {
        val arr = getArray("/goals/$uid", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            Goal(o.getString("id"), o.optString("area", ""), o.optString("title", ""),
                o.optString("target", null), o.optString("status", null))
        }
    }

    suspend fun addGoal(uid: String, token: String, area: String, title: String, target: String?) {
        val body = JSONObject().put("area", area).put("title", title)
        if (!target.isNullOrBlank()) body.put("target", target)
        request("/goals/$uid", "POST", body, token)
    }

    // -- the one QRME profile that is this person -----------------------------
    //
    // Every other QRME call in this shell reaches somebody else's profile.
    // These reach their own — see docs/tandem.md, and jim/synthetic_self.py for
    // the boundary. Seeing and revoking what a profile has been told belongs on
    // the phone at least as much as on the desktop: the phone is what somebody
    // has with them when they change their mind.

    suspend fun selfProfile(uid: String, token: String): JSONObject =
        request("/self-profile/$uid", token = token)

    suspend fun linkSelfProfile(uid: String, token: String, profileId: String,
                                ownerToken: String): JSONObject =
        request("/self-profile/$uid", "POST",
            JSONObject().put("profile_id", profileId).put("owner_token", ownerToken),
            token)

    /**
     * The same link, asked for the way a person can answer it.
     *
     * [linkSelfProfile] above wants a `prf_…` id and an owner token. The
     * token is minted once, in QRME's create response, and there is no second
     * place to read it — so somebody who made the profile elsewhere could not
     * fill that form in at all.
     *
     * Neither field is stored on either side. `choose` comes back when the
     * QRME account holds more than one profile of the person; the caller
     * sends the same body again with [profileId], which costs no retyping
     * because the form still holds the password.
     */
    suspend fun signInSelfProfile(uid: String, token: String, email: String,
                                  password: String,
                                  profileId: String? = null): JSONObject {
        val body = JSONObject().put("email", email).put("password", password)
        if (profileId != null) body.put("profile_id", profileId)
        return request("/self-profile/$uid/sign-in", "POST", body, token)
    }

    suspend fun unlinkSelfProfile(uid: String, token: String): JSONObject =
        request("/self-profile/$uid", "DELETE", token = token)

    suspend fun consentSelfProfile(uid: String, token: String,
                                   categories: List<String>): JSONObject =
        request("/self-profile/$uid/consent", "PUT",
            JSONObject().put("categories", JSONArray(categories)), token)

    /** Exactly what would be sent, built by the code that sends it. */
    suspend fun previewSelfProfile(uid: String, token: String): JSONObject =
        request("/self-profile/$uid/preview", token = token)

    suspend fun briefSelfProfile(uid: String, token: String): JSONObject =
        request("/self-profile/$uid/brief", "POST", token = token)

    suspend fun habits(uid: String, token: String): List<Habit> {
        val arr = getArray("/habits/$uid", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            Habit(o.getString("id"), o.optString("name", ""), if (o.has("streak")) o.optInt("streak") else null)
        }
    }

    suspend fun addHabit(uid: String, token: String, name: String) {
        request("/habits/$uid", "POST", JSONObject().put("name", name), token)
    }

    suspend fun logHabit(uid: String, token: String, habitId: String) {
        request("/habits/$uid/$habitId/log", "POST", JSONObject(), token)
    }

    suspend fun journal(uid: String, token: String): List<JournalItem> {
        val arr = getArray("/journal/$uid", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            JournalItem(o.getString("id"), if (o.isNull("text")) null else o.optString("text", null),
                o.optString("created_at", null))
        }
    }

    suspend fun addJournal(uid: String, token: String, text: String) {
        request("/journal/$uid", "POST", JSONObject().put("text", text), token)
    }

    /** Meals: the note is the log, the photo (base64) the sealed receipt. */
    suspend fun logMeal(uid: String, note: String, token: String,
                        contentB64: String? = null): String {
        val body = JSONObject().put("note", note)
        if (contentB64 != null) body.put("content", contentB64)
        val o = (request("/users/$uid/meals", "POST", body, token))
        return o.optString("logged")
    }

    suspend fun meals(uid: String, token: String): List<String> {
        val a = getArray("/users/$uid/meals", token)
        return (0 until a.length()).map { i ->
            val o = a.getJSONObject(i)
            o.optString("logged") +
                (if (o.optBoolean("photo_sealed")) " \u00b7 \ud83d\udd12" else "")
        }
    }

    /** The weekly letter: composed only from what was logged. */
    suspend fun writeLetter(uid: String, token: String): String {
        val o = (request("/users/$uid/letters", "POST", JSONObject(), token))
        return o.optString("body")
    }

    suspend fun letters(uid: String, token: String): List<Pair<String, String>> {
        val a = getArray("/users/$uid/letters", token)
        return (0 until a.length()).map { i ->
            val o = a.getJSONObject(i)
            o.optString("week_start") to o.optString("body")
        }
    }

    /** Interview drills: deal one question; Triple(id, question, probes). */
    suspend fun startDrill(uid: String, token: String): Triple<String, String, String> {
        val o = (request("/users/$uid/drills", "POST", JSONObject(), token))
        val probes = o.optJSONArray("probes")
        val joined = (0 until (probes?.length() ?: 0))
            .joinToString(" · ") { probes!!.getString(it) }
        return Triple(o.optString("id"), o.optString("question"), joined)
    }

    /** The reading, or empty when the checklist stands in. */
    suspend fun answerDrill(uid: String, drillId: String, answer: String,
                            token: String): String {
        val o = (request("/users/$uid/drills/$drillId/answer",
            "POST", JSONObject().put("answer", answer), token))
        return if (o.isNull("critique")) "" else o.optString("critique")
    }

    suspend fun drills(uid: String, token: String): List<String> {
        val a = getArray("/users/$uid/drills", token)
        return (0 until a.length()).map { i ->
            a.getJSONObject(i).optString("question")
        }
    }

    // ---- model selection ----

    suspend fun models(): List<ProviderInfo> {
        val arr = request("/models").getJSONArray("providers")
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            ProviderInfo(o.getString("name"), o.getString("label"), o.optBoolean("configured"))
        }
    }

    suspend fun userModel(uid: String, token: String): String {
        return request("/model/$uid", token = token).getString("provider")
    }

    suspend fun setModel(uid: String, token: String, provider: String) {
        request("/model/$uid", "PUT", JSONObject().put("provider", provider), token)
    }

    suspend fun languages(): List<LanguageInfo> {
        val arr = request("/languages").getJSONArray("languages")
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            LanguageInfo(o.getString("code"), o.getString("label"),
                o.optBoolean("safety_content_translated"))
        }
    }

    suspend fun userLanguage(uid: String, token: String): Pair<String, String> {
        val o = request("/language/$uid", token = token)
        return o.getString("language") to o.optString("mode", "pre")
    }

    suspend fun setLanguage(uid: String, token: String, code: String,
                            mode: String = "pre") {
        request("/language/$uid", "PUT",
            JSONObject().put("language", code).put("mode", mode), token)
    }

    suspend fun translate(uid: String, token: String, text: String): TranslateResult {
        val o = request("/translate/$uid", "POST", JSONObject().put("text", text), token)
        return TranslateResult(o.optString("translation", ""),
            o.optString("engine", ""), o.optString("note", null))
    }

    // ---- safety: escalation policy, Emergency, robots ----

    // The alarms. Routes this shell could not reach at all until 0.23.0 —
    // there was no occurrence of the word "alarm" anywhere in it. A responder
    // is paged on their phone and, holding that phone, had no way to answer;
    // accepting is what stops the ladder climbing to emergency services.

    suspend fun alarms(uid: String, token: String): List<AlarmRow> {
        val arr = withContext(Dispatchers.IO) {
            val conn = (URL("$base/users/$uid/alarms").openConnection()
                as HttpURLConnection).apply {
                setRequestProperty("authorization", "Bearer $token")
                // The fifth connection in this file, and the last one the
                // shared helper's accept-language line never reached.
                setRequestProperty("accept-language", L10n.deviceLanguage())
            llmKey.takeIf { it.isNotEmpty() }?.let {
                setRequestProperty("x-llm-api-key", it) }
            signupKey.takeIf { it.isNotEmpty() }?.let {
                setRequestProperty("x-signup-key", it) }
                connectTimeout = 8000; readTimeout = 8000
            }
            val text = conn.inputStream.bufferedReader().use { it.readText() }
            conn.disconnect(); org.json.JSONArray(text)
        }
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            val msgs = o.optJSONArray("messages")
            AlarmRow(
                o.getString("id"), o.optString("beacon_id", ""),
                (0 until (msgs?.length() ?: 0)).map { msgs!!.getString(it) },
                o.optString("state", "open"), o.optString("tier", ""),
                if (o.isNull("accepted_by")) null else o.optString("accepted_by"),
                o.optString("created_at", ""),
                o.optBoolean("call_emergency_services_yourself", false),
                o.optBoolean("clipped_by_ceiling", false),
            )
        }
    }

    /** [responder] must be a name — the backend refuses an empty one, because
     *  "someone accepted it" is the thing this relay exists to stop being
     *  enough. */
    suspend fun acceptAlarm(uid: String, alarmId: String, responder: String,
                            token: String): AlarmAck =
        ackOf(request("/users/$uid/alarms/$alarmId/accept", "POST",
            JSONObject().put("responder", responder), token))

    suspend fun clearAlarm(uid: String, alarmId: String, token: String): AlarmAck =
        ackOf(request("/users/$uid/alarms/$alarmId/clear", "POST",
            JSONObject(), token))

    suspend fun escalateAlarm(uid: String, alarmId: String, token: String): AlarmAck =
        ackOf(request("/users/$uid/alarms/$alarmId/escalate", "POST",
            JSONObject(), token))

    /** Answers even with no specialist reachable — the standing instruction is
     *  the one that is always right and never depends on a model. */
    suspend fun alarmGuidance(alarmId: String, question: String,
                              token: String): AlarmGuidance {
        val o = request("/alarms/$alarmId/guidance", "POST",
            JSONObject().put("question", question), token)
        return AlarmGuidance(o.optString("answer", ""),
            if (o.isNull("note")) null else o.optString("note"))
    }

    private fun ackOf(o: JSONObject) = AlarmAck(
        o.optString("alarm", ""),
        if (o.isNull("accepted_by")) null else o.optString("accepted_by"),
        if (o.isNull("state")) null else o.optString("state"),
        if (o.isNull("note")) null else o.optString("note"),
    )

    // The crash watch: armed in advance, off by default — a critical reading
    // opens "are you okay?", and silence through every attempt sends the
    // help the user programmed. The status read is also the clock.
    suspend fun crashWatch(uid: String, token: String): CrashWatch =
        crashWatchOf(request("/crash-watch/$uid", token = token))

    suspend fun armCrashWatch(uid: String, token: String, name: String,
                              channel: String, attempts: Int,
                              windowMinutes: Double, ems: Boolean): CrashWatch {
        val body = JSONObject().put("trusted_name", name)
            .put("trusted_channel", channel).put("attempts", attempts)
            .put("window_minutes", windowMinutes)
            .put("contact_emergency_services", ems)
        return crashWatchOf(request("/crash-watch/$uid", "PUT", body, token))
    }

    suspend fun disarmCrashWatch(uid: String, token: String): CrashWatch =
        crashWatchOf(request("/crash-watch/$uid", "DELETE", token = token))

    suspend fun imOkay(uid: String, token: String): CrashWatch =
        crashWatchOf(request("/crash-watch/$uid/respond", "POST",
            JSONObject(), token))

    private fun crashWatchOf(o: JSONObject) = CrashWatch(
        o.optBoolean("armed", false), o.optString("trusted_name", ""),
        o.optInt("attempts", 3), o.optDouble("window_minutes", 5.0),
        o.optBoolean("contact_emergency_services", false),
        o.optBoolean("asking", false), o.optInt("attempt", 0),
        o.optString("concern", ""), o.optBoolean("tripped", false),
    )


    suspend fun escalationPolicy(uid: String, token: String): EscalationPolicy {
        val o = request("/escalation-policy/$uid", token = token)
        val sev = o.getJSONObject("by_severity")
        return EscalationPolicy(o.getString("sensitivity"),
            sev.keys().asSequence().associateWith { sev.getString(it) })
    }

    suspend fun setSensitivity(uid: String, token: String, level: String) {
        request("/sensitivity/$uid", "PUT", JSONObject().put("level", level), token)
    }

    suspend fun emergency(uid: String, token: String, situation: String?,
                          location: String?): EmergencyResult {
        val body = JSONObject()
        if (!situation.isNullOrBlank()) body.put("situation", situation)
        if (!location.isNullOrBlank()) body.put("location", location)
        val o = request("/emergency/$uid", "POST", body, token)
        val flow = o.getJSONArray("flow")
        val dirs = o.optJSONArray("robot_directives")
        return EmergencyResult(
            (0 until flow.length()).map { i ->
                val s = flow.getJSONObject(i)
                FlowStep(s.getString("step"), s.getString("label"), s.optString("detail", ""))
            },
            (0 until (dirs?.length() ?: 0)).map { i ->
                val d = dirs!!.getJSONObject(i)
                RobotDirective(d.getString("robot"), d.getString("directive"))
            },
        )
    }

    private fun robotOf(o: JSONObject): Robot {
        val cmds = o.optJSONArray("commands")
        return Robot(
            o.getString("id"), o.optString("model", ""), o.optString("name", ""),
            o.optString("status", null), o.optString("escalation_directive", null),
            o.optString("first_aid", null),
            (0 until (cmds?.length() ?: 0)).map { cmds!!.getString(it) })
    }

    suspend fun roboticsCatalog(): List<RobotSpec> {
        val arr = request("/robotics/catalog").getJSONArray("robots")
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            RobotSpec(o.getString("model"), o.getString("label"), o.getString("maker"),
                o.optString("first_aid", null))
        }
    }

    suspend fun robots(uid: String, token: String): List<Robot> = withContext(Dispatchers.IO) {
        val conn = (URL("$base/robots/$uid").openConnection() as HttpURLConnection).apply {
                    // One of the four connections in this file the shared
                    // helper's accept-language line never reached.
                    setRequestProperty("accept-language", L10n.deviceLanguage())
            llmKey.takeIf { it.isNotEmpty() }?.let {
                setRequestProperty("x-llm-api-key", it) }
            signupKey.takeIf { it.isNotEmpty() }?.let {
                setRequestProperty("x-signup-key", it) }
            setRequestProperty("authorization", "Bearer $token")
            connectTimeout = 8000; readTimeout = 8000
        }
        val text = conn.inputStream.bufferedReader().use { it.readText() }
        conn.disconnect()
        val arr = org.json.JSONArray(text)
        (0 until arr.length()).map { robotOf(arr.getJSONObject(it)) }
    }

    suspend fun bindRobot(uid: String, token: String, model: String): Robot {
        return robotOf(request("/robots/$uid", "POST",
            JSONObject().put("model", model), token))
    }

    suspend fun commandRobot(uid: String, token: String, robotId: String,
                             command: String, arg: String?): RobotCmdResult {
        val body = JSONObject().put("command", command)
        if (!arg.isNullOrBlank()) body.put("arg", arg)
        val o = request("/robots/$uid/$robotId/command", "POST", body, token)
        val spoken = o.optJSONArray("spoken_steps")
        val seq = o.optJSONArray("sequence")
        return RobotCmdResult(
            o.optString("status", ""), o.optString("note", null),
            o.optString("instruction", null),
            (0 until (spoken?.length() ?: 0)).map { spoken!!.getString(it) },
            (0 until (seq?.length() ?: 0)).map { seq!!.getString(it) },
            o.optJSONObject("pace")?.optInt("compressions_per_minute"))
    }

    private fun waiverOf(o: JSONObject): WaiverState {
        val terms = o.optJSONArray("terms")
        return WaiverState(o.optBoolean("signed"), o.optString("signature", null),
            (0 until (terms?.length() ?: 0)).map { terms!!.getString(it) })
    }

    suspend fun waiver(uid: String, token: String): WaiverState =
        waiverOf(request("/waivers/$uid", token = token))

    suspend fun signWaiver(uid: String, token: String, signature: String): WaiverState {
        request("/waivers/$uid", "POST",
            JSONObject().put("signature", signature).put("accept", true), token)
        return waiver(uid, token)
    }

    suspend fun revokeWaiver(uid: String, token: String) {
        request("/waivers/$uid", "DELETE", null, token)
    }

    // ---- Connect: sources, social platforms, connected apps ----

    suspend fun sources(uid: String, token: String): List<SourceRow> {
        val arr = getArray("/sources/$uid", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            SourceRow(o.getString("source"), o.optBoolean("consented"))
        }
    }

    suspend fun setSource(uid: String, token: String, source: String, consented: Boolean) {
        request("/sources/$uid", "PUT",
            JSONObject().put("source", source).put("consented", consented), token)
    }

    private fun socialConnOf(o: JSONObject) = SocialConn(
        o.getString("id"), o.optString("platform", ""), o.optString("direction", ""),
        o.optString("handle", null))

    /** The three QR images. The JSON helper cannot carry an image, and
     *  the door is the fetch the opener does; building the URL here is
     *  what the route audit reads. */
    fun pairQrUrl(): String = java.net.URL("$base/pair/qr.svg").toString()

    fun beaconQrUrl(bid: String): String =
        java.net.URL("$base/c/$bid/qr.svg").toString()

    fun connectionQrUrl(cid: String): String =
        java.net.URL("$base/social/connection/$cid/qr.svg").toString()

    /** One reading through the Shortcut's own door — the token in the path
     *  is the whole credential, so no account token rides along. */
    suspend fun watchDrip(dripToken: String, heartRate: Int): DripAckK {
        val o = request("/watch/drip/$dripToken", "POST",
            JSONObject().put("heart_rate", heartRate))
        return DripAckK(o.optInt("received"), o.optBoolean("noticed"))
    }

    suspend fun socialConnections(uid: String, token: String): List<SocialConn> {
        val arr = getArray("/social/$uid", token)
        return (0 until arr.length()).map { socialConnOf(arr.getJSONObject(it)) }
    }

    suspend fun socialConnect(uid: String, token: String, platform: String,
                              direction: String, handle: String?): SocialConn {
        val body = JSONObject().put("platform", platform).put("direction", direction)
        if (!handle.isNullOrBlank()) body.put("handle", handle)
        return socialConnOf(request("/social/$uid", "POST", body, token))
    }

    suspend fun socialCollect(cid: String, token: String, content: String) {
        request("/social/connection/$cid/collect", "POST",
            JSONObject().put("items", org.json.JSONArray()
                .put(JSONObject().put("content", content))), token)
    }

    suspend fun socialScrape(cid: String, token: String) {
        request("/social/connection/$cid/scrape", "POST", JSONObject(), token)
    }

    suspend fun socialPublish(cid: String, token: String, content: String) {
        request("/social/connection/$cid/publish", "POST",
            JSONObject().put("content", content), token)
    }

    suspend fun appsCatalog(): List<CatalogApp> {
        val providers = request("/connectors/catalog").getJSONArray("providers")
        val out = mutableListOf<CatalogApp>()
        for (i in 0 until providers.length()) {
            val p = providers.getJSONObject(i)
            val apps = p.getJSONArray("apps")
            for (j in 0 until apps.length()) {
                val a = apps.getJSONObject(j)
                out += CatalogApp(p.getString("provider"), a.getString("app"), a.getString("label"))
            }
        }
        return out
    }

    suspend fun appConnections(uid: String, token: String): List<AppConn> {
        val arr = getArray("/apps/$uid", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            AppConn(o.getString("id"), o.optString("provider", ""), o.optString("app", ""))
        }
    }

    suspend fun appConnect(uid: String, token: String, provider: String, app: String) {
        request("/apps/$uid", "POST",
            JSONObject().put("provider", provider).put("app", app), token)
    }

    suspend fun appCollect(cid: String, token: String, content: String) {
        request("/apps/connector/$cid/collect", "POST",
            JSONObject().put("items", org.json.JSONArray()
                .put(JSONObject().put("content", content))), token)
    }

    // ---- Medical ID (first-responder card + QR) ----

    suspend fun issueMedicalCard(uid: String, token: String): MedicalCardIssued {
        val o = request("/medical-id/qr/$uid", "POST", null, token)
        return MedicalCardIssued(o.getString("token"), o.getString("qr_svg_url"))
    }

    suspend fun medicalCard(cardToken: String): MedicalCard {
        val o = request("/medical-id/$cardToken")     // public: the card is the credential
        val conds = o.optJSONArray("known_conditions")
        val contact = o.optJSONObject("emergency_contact")
        return MedicalCard(
            o.optString("name", null),
            if (o.isNull("age")) null else o.optInt("age"),
            (0 until (conds?.length() ?: 0)).map { conds!!.getString(it) },
            if (o.isNull("resting_heart_rate")) null else o.optInt("resting_heart_rate"),
            contact?.optString("name", null), contact?.optString("phone", null))
    }

    suspend fun revokeMedicalCard(uid: String, token: String) {
        request("/medical-id/qr/$uid", "DELETE", null, token)
    }

    // ---- Help us improve — product feedback (open to anyone) ----

    suspend fun submitImprovement(token: String?, category: String,
                                  message: String, rating: Int?) {
        val body = JSONObject().put("category", category).put("message", message)
        if (rating != null) body.put("rating", rating)
        request("/improve", "POST", body, token)
    }

    suspend fun improvements(token: String?): ImproveState {
        val o = request("/improve", token = token)
        val mineArr = o.optJSONArray("mine")
        val mine = (0 until (mineArr?.length() ?: 0)).map { i ->
            val m = mineArr!!.getJSONObject(i)
            ImproveItem(m.optString("category", ""), m.optString("message", ""),
                m.optString("status", ""))
        }
        val tallyObj = o.optJSONObject("tally") ?: JSONObject()
        val tally = tallyObj.keys().asSequence().associateWith { tallyObj.optInt(it) }
        return ImproveState(mine, tally, o.optInt("total"))
    }

    // ---- ability is not a gate: the accessibility door ----

    /** Tokenless on purpose — the person it exists for may be the person
     *  the enrollment shut out. The words stay on the deployment; nothing
     *  here reaches the problems collector. */
    suspend fun sendAccessReport(doing: String, wall: String, help: String?,
                                 lang: String): String {
        val body = JSONObject().put("doing", doing).put("wall", wall)
            .put("lang", lang)
        help?.takeIf { it.isNotBlank() }?.let { body.put("help", it) }
        return request("/access/reports", "POST", body)
            .optString("status", "received")
    }

    /** Reviewer-token read — the deployment's steward, never a user. */
    suspend fun accessReports(reviewerToken: String): List<AccessReportRow> {
        val o = request("/access/reports", token = reviewerToken)
        val arr = o.optJSONArray("reports")
        return (0 until (arr?.length() ?: 0)).map { i ->
            val r = arr!!.getJSONObject(i)
            AccessReportRow(r.optString("doing", ""), r.optString("wall", ""),
                r.optString("help", "").takeIf { it.isNotBlank() },
                r.optString("lang", ""), r.optString("created_at", ""))
        }
    }

    // ---- community: the door into QRME, and the visit note ----

    /**
     * Rooms and places as QRME serves them, plus the language JIM knows this
     * user reads. JIM never mirrors the conversation — the posture in the
     * reply says so, and this maps it through rather than restating it.
     */
    // ---- the presence: the coach that speaks first ----
    //
    // Every read here is answered from rows the backend already holds — no
    // model, no second call out. A phone in a tunnel still gets its day,
    // which is the whole argument of `jim/presence.py`.

    /** What it is, and what it will not be. No token: the answer must be the
     *  same to a child, a guardian, a clinician and a regulator. */
    suspend fun presenceWho(): PresenceWho {
        val o = request("/presence")
        val b = o.optJSONObject("boundaries")
        val bounds = mutableMapOf<String, String>()
        for (key in (b?.keys() ?: emptyList<String>().iterator())) {
            bounds[key] = b!!.getJSONObject(key).optString("says", "")
        }
        return PresenceWho(o.optString("says", ""), o.optString("note", ""),
            o.optBoolean("works_offline"), o.optBoolean("hands_free"), bounds)
    }

    /** The six areas and where each one stands. */
    suspend fun presenceBaseline(uid: String, token: String): PresenceBaseline {
        val o = request("/presence/$uid/baseline", token = token)
        val areas = o.optJSONObject("areas")
        val rows = mutableListOf<PresenceArea>()
        for (key in (areas?.keys() ?: emptyList<String>().iterator())) {
            val a = areas!!.getJSONObject(key)
            rows.add(PresenceArea(a.optString("area", key),
                a.optString("standing", "unknown")))
        }
        return PresenceBaseline(o.optInt("known_areas"), o.optInt("of"),
            o.optBoolean("needed_network"), rows)
    }

    /** The day's three beats at once — a plan a client can hold offline. */
    suspend fun presenceDay(uid: String, token: String): List<PresenceBeat> {
        val arr = request("/presence/$uid/day", token = token).optJSONArray("beats")
        return (0 until (arr?.length() ?: 0)).map { beatOf(arr!!.getJSONObject(it)) }
    }

    /** One beat. Asking is what counts as having been told: the backend
     *  records it so the same line does not return tomorrow. */
    suspend fun presenceBeat(uid: String, token: String, slot: String): PresenceBeat =
        beatOf(request("/presence/$uid/beat?slot=$slot", token = token))

    /** The same beat with a model's wording. The model may not decide that
     *  there is a beat, which area, or what the evidence says. */
    suspend fun presenceDeepen(uid: String, token: String, slot: String): PresenceBeat =
        // Positional, matching every other write in this file — the door
        // audit reads the verb from the literal that follows the path, and a
        // named argument hides it.
        beatOf(request("/presence/$uid/deepen?slot=$slot", "POST", null, token))

    /** Other minds — QRME's rooms, desks and profiles, offered. */
    suspend fun presenceReach(uid: String, token: String): List<String> {
        val arr = request("/presence/$uid/reach", token = token).optJSONArray("offers")
        return (0 until (arr?.length() ?: 0)).map {
            val o = arr!!.getJSONObject(it)
            o.optString("who", o.optString("topic", o.optString("id", "")))
        }
    }

    /** Where it may speak, and what each surface makes it hold back. */
    suspend fun presenceSurfaces(uid: String, token: String): PresenceSurfaces =
        surfacesOf(request("/presence/$uid/surfaces", token = token))

    suspend fun presenceChooseSurface(uid: String, token: String,
                                      surface: String): PresenceSurfaces =
        surfacesOf(request("/presence/$uid/surface", "PUT",
            JSONObject().put("speaks_on", surface), token))

    /** The beat, and whether this surface may speak it. */
    suspend fun presenceSay(uid: String, token: String,
                            slot: String): PresenceSpoken =
        spokenOf(request("/presence/$uid/say?slot=$slot", token = token))

    /** The hands-free question. Does not record — a device polling on a
     *  timer must not burn a beat nobody heard. */
    suspend fun presenceDue(uid: String, token: String): PresenceSpoken =
        spokenOf(request("/presence/$uid/due", token = token))

    private fun spokenOf(o: JSONObject): PresenceSpoken {
        val held = o.optJSONArray("withheld")
        return PresenceSpoken(
            o.optString("speaks_on", ""), o.optBoolean("spoken"),
            o.optBoolean("shown"),
            (0 until (held?.length() ?: 0)).map { held!!.getString(it) },
            o.optString("why_not_aloud", ""),
            o.optBoolean("surface_has_audio"),
            o.optString("english", ""), o.optBoolean("speak"))
    }

    /** The bearing: companion by default, professional on request. */
    suspend fun presenceBearing(uid: String, token: String): PresenceBearingView =
        bearingOf(request("/presence/$uid/bearing", token = token))

    suspend fun presenceSetBearing(uid: String, token: String,
                                   bearing: String): PresenceBearingView =
        bearingOf(request("/presence/$uid/bearing", "PUT",
            JSONObject().put("bearing", bearing), token))

    private fun bearingOf(o: JSONObject): PresenceBearingView {
        val picks = o.optJSONArray("choices")
        val same = o.optJSONObject("unchanged")
        return PresenceBearingView(
            o.optString("bearing", "companion"),
            o.optString("default", "companion"),
            (0 until (picks?.length() ?: 0)).map { picks!!.getString(it) },
            o.optJSONObject("effect")?.optString("says", "") ?: "",
            same?.keys()?.asSequence()?.map { same.optString(it, "") }?.toList()
                ?: emptyList(),
            o.optString("note", ""))
    }

    /** What it has become, with the counts under it. */
    suspend fun presenceGrowth(uid: String, token: String): PresenceGrowth {
        val o = request("/presence/$uid/growth", token = token)
        return PresenceGrowth(o.optInt("beats_spoken"),
            o.optInt("areas_i_can_see"), o.optInt("of"),
            o.optString("about_myself", ""))
    }

    private fun beatOf(o: JSONObject) = PresenceBeat(
        o.optString("slot", ""), o.optBoolean("speak"),
        o.optString("register", ""), o.optString("english", ""),
        if (o.isNull("deepened_line")) null else o.optString("deepened_line"),
        (0 until (o.optJSONArray("because")?.length() ?: 0)).map {
            o.optJSONArray("because")!!.getString(it)
        })

    private fun surfacesOf(o: JSONObject): PresenceSurfaces {
        val arr = o.optJSONArray("surfaces")
        val rows = (0 until (arr?.length() ?: 0)).map {
            val r = arr!!.getJSONObject(it)
            PresenceSurfaceRow(r.optString("surface", ""),
                r.optBoolean("chosen"), r.optBoolean("reads_health_aloud"),
                r.optString("note", ""))
        }
        return PresenceSurfaces(o.optString("chosen", ""),
            o.optString("rule", ""), rows)
    }

    suspend fun community(uid: String, token: String): CommunityView {
        val o = request("/community/$uid", token = token)
        val roomArr = o.optJSONArray("rooms")
        val rooms = (0 until (roomArr?.length() ?: 0)).map { i ->
            val r = roomArr!!.getJSONObject(i)
            CommunityRoom(r.getString("id"),
                if (r.isNull("topic")) null else r.optString("topic"),
                if (r.isNull("channel")) null else r.optString("channel"),
                r.optInt("participants"),
                if (r.isNull("url")) null else r.optString("url"))
        }
        val placeArr = o.optJSONArray("places")
        val places = (0 until (placeArr?.length() ?: 0)).map { i ->
            val pl = placeArr!!.getJSONObject(i)
            CommunityPlace(pl.optString("locality", ""),
                if (pl.isNull("region")) null else pl.optString("region"),
                pl.optInt("listings"))
        }
        val po = o.optJSONObject("posture") ?: JSONObject()
        return CommunityView(
            if (o.isNull("qrme_url")) null else o.optString("qrme_url"),
            if (o.isNull("language")) null else o.optString("language"),
            rooms, places, o.optString("note", ""),
            CommunityPosture(po.optBoolean("mirrored_here"),
                po.optBoolean("posts_on_your_behalf"),
                po.optBoolean("health_data_shared")))
    }

    /** Record that a door was opened — the visit, and nothing from inside it. */
    suspend fun noteCommunityVisit(uid: String, token: String, roomId: String) {
        request("/community/$uid/visits", "POST",
            JSONObject().put("room_id", roomId), token)
    }


    // ---- followup, adaptation and anonymity ----

    suspend fun openFollowups(uid: String, token: String): List<OpenFollowup> {
        val o = request("/followup/$uid", token = token)
        val arr = o.optJSONArray("open")
        return (0 until (arr?.length() ?: 0)).map { i ->
            val f = arr!!.getJSONObject(i)
            OpenFollowup(f.getString("id"), f.optString("condition", ""),
                if (f.isNull("severity")) null else f.optString("severity"),
                f.optString("question", "Did that help?"))
        }
    }

    /**
     * `helped = false` is not a complaint filed away: it re-runs the escalation
     * ladder with the ineffective-guidance rung and returns the people who can
     * help right now.
     */
    suspend fun answerFollowup(uid: String, token: String, helped: Boolean,
                               note: String? = null): FollowupAnswered {
        val body = JSONObject().put("helped", helped)
        if (!note.isNullOrBlank()) body.put("note", note)
        val o = request("/followup/$uid", "POST", body, token)
        val live = o.optJSONObject("live_assistance")
        val optArr = live?.optJSONArray("options")
        val options = (0 until (optArr?.length() ?: 0)).map { i ->
            val op = optArr!!.getJSONObject(i)
            LiveOption(op.optString("kind", ""),
                if (op.isNull("name")) null else op.optString("name"),
                if (op.isNull("channel")) null else op.optString("channel"),
                if (op.isNull("note")) null else op.optString("note"))
        }
        return FollowupAnswered(
            o.optBoolean("answered"),
            if (o.isNull("reason")) null else o.optString("reason"),
            if (o.isNull("helped")) null else o.optBoolean("helped"),
            if (o.isNull("next")) null else o.optString("next"),
            options,
            if (live == null || live.isNull("note")) null else live.optString("note"))
    }

    private fun adaptationOf(o: JSONObject): AdaptationProfile {
        val prof = o.optJSONObject("profile") ?: JSONObject()
        val helpsObj = prof.optJSONObject("what_helps") ?: JSONObject()
        val helps = helpsObj.keys().asSequence().associateWith { k ->
            val t = helpsObj.getJSONObject(k)
            HelpTally(t.optInt("helped"), t.optInt("answered"))
        }
        return AdaptationProfile(
            o.optBoolean("built"),
            if (o.isNull("note")) null else o.optString("note"),
            o.optInt("evidence_items"), o.optDouble("confidence", 0.0),
            o.optBoolean("vaulted"), helps,
            if (prof.isNull("tone")) null else prof.optString("tone"),
            if (prof.isNull("occupation")) null else prof.optString("occupation"),
            if (prof.isNull("method")) null else prof.optString("method"))
    }

    // --- the offline fine-tune ---------------------------------------------
    // Beside adaptation and not folded into it: that one recomputes a profile
    // that conditions a prompt, this one trains weights.

    private fun finetuneOf(o: JSONObject) = Finetune(
        o.optInt("build"), o.optString("backend"), o.optInt("examples"),
        o.optInt("helped"), o.optInt("did_not_help"),
        o.optString("method"), o.optString("digest"),
        o.optString("trained_at"), o.optBoolean("active"))

    suspend fun finetune(uid: String, token: String): Finetune =
        finetuneOf(request("/finetune/$uid", token = token))

    /** Local work: the pass runs with the backend's network blocked. */
    suspend fun runFinetune(uid: String, token: String): Finetune =
        finetuneOf(request("/finetune/$uid", "POST", JSONObject(), token))

    /** Training and using are two decisions. */
    suspend fun setFinetuneActive(uid: String, token: String,
                                  active: Boolean): Boolean =
        request("/finetune/$uid/active", "PUT",
                JSONObject().put("active", active), token).optBoolean("active")

    suspend fun adaptation(uid: String, token: String): AdaptationProfile =
        adaptationOf(request("/adaptation/$uid", token = token))

    /** Rebuild from the history already on record — local work only. */
    suspend fun rebuildAdaptation(uid: String, token: String): AdaptationProfile =
        adaptationOf(request("/adaptation/$uid", "POST", null, token))

    suspend fun anonymity(uid: String, token: String): AnonymityPosture {
        val o = request("/anonymity/$uid", token = token)
        fun list(key: String): List<String> {
            val a = o.optJSONArray(key)
            return (0 until (a?.length() ?: 0)).map { a!!.getString(it) }
        }
        return AnonymityPosture(
            o.optBoolean("anonymous"),
            if (o.isNull("known_as")) null else o.optString("known_as"),
            o.optBoolean("legal_name_on_record"), list("keeps"), list("costs"))
    }

    // ---- money — the guardian that watches balances (jim/money.py) --------
    // The overview carries its own labels in the reader's language; the
    // screen renders them and adds no English of its own, because the count
    // behind this shell's tabs is a ratchet that must not grow.

    private fun moneyAccountOf(o: JSONObject) = MoneyAccount(
        o.getString("id"), o.optString("kind"), o.optString("institution"),
        if (o.isNull("label")) null else o.optString("label"),
        if (o.isNull("last4")) null else o.optString("last4"),
        o.optString("credentials"),
        if (o.isNull("balance")) null else o.optDouble("balance"))

    private fun moneyOrderOf(o: JSONObject) = MoneyOrder(
        o.optString("asset_class"), o.optDouble("amount", 0.0),
        o.optString("status"),
        if (o.isNull("rationale")) null else o.optString("rationale"))

    private fun moneyWarningOf(o: JSONObject): MoneyWarning {
        val doors = o.optJSONObject("doors")
        val desks = mutableListOf<MoneyDesk>()
        doors?.optJSONArray("desks")?.let { a ->
            for (i in 0 until a.length()) {
                val d = a.getJSONObject(i)
                desks.add(MoneyDesk(d.optString("name"), d.optString("trade"),
                                    d.optString("location")))
            }
        }
        val spec = doors?.optJSONObject("specialist")
        return MoneyWarning(o.optString("kind"), o.optString("message"),
                            spec?.optString("label"), desks)
    }

    suspend fun moneyOverview(uid: String, token: String): MoneyOverview {
        val o = request("/money/$uid", token = token)
        val accounts = mutableListOf<MoneyAccount>()
        o.optJSONArray("accounts")?.let { a ->
            for (i in 0 until a.length()) accounts.add(moneyAccountOf(a.getJSONObject(i)))
        }
        val orders = mutableListOf<MoneyOrder>()
        o.optJSONArray("orders")?.let { a ->
            for (i in 0 until a.length()) orders.add(moneyOrderOf(a.getJSONObject(i)))
        }
        val labels = mutableMapOf<String, String>()
        o.optJSONObject("labels")?.let { l ->
            l.keys().forEach { k -> labels[k] = l.getString(k) }
        }
        val goal = o.optJSONObject("savings")
        return MoneyOverview(accounts, goal?.optDouble("goal"), orders,
                             o.optString("note"), labels)
    }

    /** The statement file goes to the vault; the reading is local. */
    suspend fun moneyDropStatement(uid: String, token: String,
                                   accountId: String,
                                   contentB64: String): String {
        val o = (request("/money/$uid/statements", "POST",
            JSONObject().put("account_id", accountId)
                .put("content", contentB64), token))
        return o.optString("filename") + " \u00b7 " + o.optInt("line_count") +
            " \u00b7 +" + o.optDouble("total_in") + " \u2212" +
            o.optDouble("total_out")
    }

    suspend fun moneyStatements(uid: String, token: String): List<String> {
        val a = getArray("/money/$uid/statements", token)
        return (0 until a.length()).map { i ->
            val o = a.getJSONObject(i)
            o.optString("filename") + " \u00b7 " + o.optInt("line_count")
        }
    }

    /** A written aggregator consent; the status never claims data. */
    suspend fun moneyLinkBank(uid: String, token: String, institution: String,
                              aggregator: String): String {
        val o = (request("/money/$uid/links", "POST",
            JSONObject().put("institution", institution)
                .put("aggregator", aggregator), token))
        return o.optString("status")
    }

    suspend fun moneyLinks(uid: String, token: String): List<Triple<String, String, String>> {
        val a = getArray("/money/$uid/links", token)
        return (0 until a.length()).map { i ->
            val o = a.getJSONObject(i)
            Triple(o.optString("id"),
                o.optString("institution") + " \u00b7 " + o.optString("aggregator"),
                o.optString("status"))
        }
    }

    suspend fun moneySyncBank(uid: String, token: String, linkId: String): String {
        val o = (request("/money/$uid/links/$linkId/sync", "POST",
            JSONObject(), token))
        return o.optString("status")
    }

    suspend fun moneyRevokeLink(uid: String, token: String, linkId: String): String {
        val o = (request("/money/$uid/links/$linkId", "DELETE",
            token = token))
        return o.optString("status")
    }

    suspend fun moneyAddAccount(uid: String, token: String, kind: String,
                                institution: String, accountNumber: String?,
                                routingNumber: String?): MoneyAccount {
        val body = JSONObject().put("kind", kind).put("institution", institution)
        if (!accountNumber.isNullOrBlank()) body.put("account_number", accountNumber)
        if (!routingNumber.isNullOrBlank()) body.put("routing_number", routingNumber)
        return moneyAccountOf(request("/money/$uid/accounts", "POST", body, token))
    }

    suspend fun moneyObserve(uid: String, token: String, accountId: String,
                             balance: Double): List<MoneyWarning> {
        val body = JSONObject().put("account_id", accountId).put("balance", balance)
        val o = request("/money/$uid/observe", "POST", body, token)
        val out = mutableListOf<MoneyWarning>()
        o.optJSONArray("warnings")?.let { a ->
            for (i in 0 until a.length()) out.add(moneyWarningOf(a.getJSONObject(i)))
        }
        return out
    }

    suspend fun moneySetSavings(uid: String, token: String, goal: Double) {
        request("/money/$uid/savings", "PUT", JSONObject().put("goal", goal), token)
    }

    // The low-balance floor. Zero is refused server-side — a warning that
    // can never fire is not a setting.
    suspend fun moneySetFloor(uid: String, token: String, floor: Double) {
        request("/money/$uid/floor", "PUT", JSONObject().put("floor", floor), token)
    }

    // ---- schedule + shopping through the tandem ---------------------------
    // Labels ride the views in the reader's language; these panels render
    // them and add no English of their own.

    private fun appointmentOf(o: JSONObject) = Appointment(
        o.getString("id"), o.optString("title"), o.optString("whenat"),
        if (o.isNull("whereat")) null else o.optString("whereat"),
        o.optString("status"))

    suspend fun scheduleView(uid: String, token: String): ScheduleOverview {
        val o = request("/schedule/$uid", token = token)
        val appts = mutableListOf<Appointment>()
        o.optJSONArray("appointments")?.let { a ->
            for (i in 0 until a.length()) appts.add(appointmentOf(a.getJSONObject(i)))
        }
        val labels = mutableMapOf<String, String>()
        o.optJSONObject("labels")?.let { l ->
            l.keys().forEach { k -> labels[k] = l.getString(k) }
        }
        return ScheduleOverview(appts, o.optBoolean("email_available"),
                                labels, o.optString("note"))
    }

    suspend fun scheduleBook(uid: String, token: String, title: String,
                             whenAt: String, whereAt: String?,
                             emailReminder: Boolean): Appointment {
        val body = JSONObject().put("title", title).put("when", whenAt)
            .put("email_reminder", emailReminder)
        if (!whereAt.isNullOrBlank()) body.put("where", whereAt)
        return appointmentOf(request("/schedule/$uid", "POST", body, token))
    }

    suspend fun scheduleCancel(uid: String, token: String,
                               appointmentId: String): Appointment =
        appointmentOf(request("/schedule/$uid/$appointmentId", "DELETE",
                              null, token))

    suspend fun shoppingView(uid: String, token: String): ShoppingOverview {
        val o = request("/shopping/$uid", token = token)
        val shops = mutableListOf<TandemShop>()
        o.optJSONArray("shops")?.let { a ->
            for (i in 0 until a.length()) {
                val s = a.getJSONObject(i)
                shops.add(TandemShop(s.getString("id"), s.optString("name"),
                    s.optString("seller"),
                    if (s.isNull("tag")) null else s.optString("tag")))
            }
        }
        val receipts = mutableListOf<ShopReceipt>()
        o.optJSONArray("receipts")?.let { a ->
            for (i in 0 until a.length()) {
                val r = a.getJSONObject(i)
                receipts.add(ShopReceipt(r.getString("id"),
                    r.optString("qrme_order_id"), r.optString("title"),
                    r.optDouble("amount", 0.0), r.optString("currency"),
                    r.optString("status")))
            }
        }
        val labels = mutableMapOf<String, String>()
        o.optJSONObject("labels")?.let { l ->
            l.keys().forEach { k -> labels[k] = l.getString(k) }
        }
        return ShoppingOverview(shops, receipts, labels, o.optString("note"))
    }

    suspend fun shoppingOrder(uid: String, token: String, shopId: String,
                              offeringId: String, quantity: Int) {
        request("/shopping/$uid/order", "POST",
                JSONObject().put("shop_id", shopId)
                    .put("offering_id", offeringId).put("quantity", quantity),
                token)
    }

    suspend fun shoppingCancel(uid: String, token: String,
                               qrmeOrderId: String) {
        request("/shopping/$uid/cancel", "POST",
                JSONObject().put("qrme_order_id", qrmeOrderId), token)
    }

    // ---- your circle: contacts, messages, switches, homepage ----------

    private fun personOf(o: JSONObject) = CirclePerson(
        o.getString("user_id"),
        if (o.isNull("display_name")) null else o.optString("display_name"))

    private fun circlePageOf(o: JSONObject): CircleHomepage {
        val theme = o.getJSONObject("theme")
        val links = mutableListOf<CircleLink>()
        o.optJSONArray("links")?.let { a ->
            for (i in 0 until a.length()) {
                val l = a.getJSONObject(i)
                links.add(CircleLink(l.optString("label"), l.optString("url")))
            }
        }
        val tops = mutableListOf<CirclePerson>()
        o.optJSONArray("top_friends")?.let { a ->
            for (i in 0 until a.length()) tops.add(personOf(a.getJSONObject(i)))
        }
        return CircleHomepage(o.getString("user_id"),
            if (o.isNull("display_name")) null else o.optString("display_name"),
            o.optString("headline"), o.optString("about"),
            theme.optString("bg"), theme.optString("accent"),
            links, tops, o.optBoolean("editable"))
    }

    private fun messageOf(o: JSONObject) = CircleMessage(
        o.getString("id"), o.getString("sender_id"),
        o.optString("body"), o.optString("sent_at"))

    suspend fun circleView(uid: String, token: String): CircleOverview {
        val o = request("/circle/$uid", token = token)
        val features = mutableMapOf<String, Boolean>()
        o.optJSONObject("features")?.let { f ->
            f.keys().forEach { k -> features[k] = f.getBoolean(k) }
        }
        fun people(key: String): List<CirclePerson> {
            val out = mutableListOf<CirclePerson>()
            o.optJSONObject("circle")?.optJSONArray(key)?.let { a ->
                for (i in 0 until a.length()) out.add(personOf(a.getJSONObject(i)))
            }
            return out
        }
        val threads = mutableListOf<CircleThread>()
        o.optJSONArray("threads")?.let { a ->
            for (i in 0 until a.length()) {
                val t = a.getJSONObject(i)
                threads.add(CircleThread(t.getString("other_id"),
                    if (t.isNull("other_name")) null else t.optString("other_name"),
                    t.optInt("messages")))
            }
        }
        val labels = mutableMapOf<String, String>()
        o.optJSONObject("labels")?.let { l ->
            l.keys().forEach { k -> labels[k] = l.getString(k) }
        }
        return CircleOverview(features, people("contacts"),
            people("invited_me"), people("awaiting"), threads,
            circlePageOf(o.getJSONObject("homepage")), labels,
            o.optString("note"))
    }

    suspend fun circleSetFeature(uid: String, token: String, feature: String,
                                 enabled: Boolean) {
        request("/circle/$uid/features", "PUT",
                JSONObject().put("feature", feature).put("enabled", enabled),
                token)
    }

    suspend fun circleInvite(uid: String, token: String, otherId: String) {
        request("/circle/$uid/contacts", "POST",
                JSONObject().put("other_id", otherId), token)
    }

    suspend fun circleLeave(uid: String, token: String, otherId: String) {
        request("/circle/$uid/contacts/$otherId", "DELETE", token = token)
    }

    suspend fun circleSend(uid: String, token: String, to: String,
                           body: String) {
        request("/circle/$uid/messages", "POST",
                JSONObject().put("to", to).put("body", body), token)
    }

    suspend fun circleThread(uid: String, token: String,
                             withId: String): List<CircleMessage> {
        val o = request("/circle/$uid/messages?with_id=" +
                        java.net.URLEncoder.encode(withId, "UTF-8"),
                        token = token)
        val out = mutableListOf<CircleMessage>()
        o.optJSONArray("messages")?.let { a ->
            for (i in 0 until a.length()) out.add(messageOf(a.getJSONObject(i)))
        }
        return out
    }

    suspend fun circleHomepage(uid: String, token: String,
                               otherId: String): CircleHomepage {
        return circlePageOf(request("/circle/$uid/homepage/$otherId",
                                    token = token))
    }

    suspend fun circleEditHomepage(uid: String, token: String,
                                   headline: String, about: String,
                                   bg: String, accent: String): CircleHomepage {
        return circlePageOf(request("/circle/$uid/homepage", "PUT",
            JSONObject().put("headline", headline).put("about", about)
                .put("theme", JSONObject().put("bg", bg).put("accent", accent)),
            token))
    }

    /** The handover, and the way back. Revoking is never plan-gated. */
    suspend fun moneySetMandate(uid: String, token: String, enabled: Boolean,
                                capPerOrder: Double, monthlyCap: Double,
                                scope: String) {
        val body = JSONObject().put("enabled", enabled)
            .put("cap_per_order", capPerOrder).put("monthly_cap", monthlyCap)
            .put("asset_classes", org.json.JSONArray(listOf("index_funds")))
            .put("scope", scope)
        request("/money/$uid/mandate", "PUT", body, token)
    }


    // MARK: care team, clinical captures, and channel 2 — the console
    // doors task #106 built that the phones never got.

    private fun carePlanOf(o: JSONObject) = CarePlanRow(
        o.getString("id"), o.optString("goal", ""),
        o.optString("plan", null),
        o.optBoolean("sealed_in_qrme_vault", false),
        o.optString("created_at", null))

    private fun careTeamOf(o: JSONObject) = CareTeamState(
        o.optBoolean("linked", false),
        o.optString("org_id", null), o.optString("department_id", null),
        o.optJSONObject("latest_plan")?.let { carePlanOf(it) })

    suspend fun careTeamState(uid: String, token: String): CareTeamState =
        careTeamOf(request("/users/$uid/care-team", token = token))

    suspend fun careTeamLink(uid: String, token: String, orgId: String,
                             departmentId: String,
                             ownerToken: String): CareTeamState {
        val body = JSONObject()
            .put("org_id", orgId).put("department_id", departmentId)
            .put("owner_token", ownerToken)
        return careTeamOf(request("/users/$uid/care-team", "PUT", body, token))
    }

    suspend fun careTeamUnlink(uid: String, token: String) {
        // 204: the server says nothing on success, and request() hands
        // back an empty object rather than choking on the silence.
        request("/users/$uid/care-team", "DELETE", token = token)
    }

    suspend fun careTeamCoordinate(uid: String, token: String,
                                   goal: String): CarePlanRow =
        carePlanOf(request("/users/$uid/care-team/coordinate", "POST",
                           JSONObject().put("goal", goal), token))

    suspend fun careTeamPlans(uid: String, token: String): List<CarePlanRow> {
        val arr = getArray("/users/$uid/care-team/plans", token)
        return (0 until arr.length()).map { carePlanOf(arr.getJSONObject(it)) }
    }

    private fun micStateOf(o: JSONObject) = MicState(
        o.optBoolean("listening", false), o.optBoolean("attached", false),
        o.optString("device", null), o.optString("mic_type", null),
        o.optString("gain", null), o.optBoolean("capped", false),
        o.optString("hears", null))

    suspend fun micTypes(): MicTypeChoices {
        val o = request("/mic/types")
        fun names(key: String): List<String> {
            val a = o.optJSONArray(key) ?: return emptyList()
            return (0 until a.length()).map { a.getString(it) }
        }
        return MicTypeChoices(names("personal"), names("ambient"),
                              o.optString("rule", null))
    }

    suspend fun micGains(): MicGainChoices {
        val o = request("/mic/gains")
        val levels = mutableListOf<MicGainLevel>()
        o.optJSONArray("levels")?.let { a ->
            for (i in 0 until a.length()) {
                val l = a.getJSONObject(i)
                levels.add(MicGainLevel(l.getString("gain"),
                    l.optBoolean("reaches_others", false),
                    l.optString("describes", null)))
            }
        }
        return MicGainChoices(levels, o.optString("default", ""),
                              o.optString("rule", null))
    }

    suspend fun micState(uid: String, token: String): MicState =
        micStateOf(request("/users/$uid/mic", token = token))

    suspend fun attachMic(uid: String, token: String, deviceName: String,
                          micType: String): MicState =
        micStateOf(request("/users/$uid/mic", "PUT",
            JSONObject().put("device_name", deviceName)
                .put("mic_type", micType), token))

    suspend fun detachMic(uid: String, token: String): MicState =
        micStateOf(request("/users/$uid/mic", "DELETE", token = token))

    suspend fun setMicGain(uid: String, token: String, gain: String): MicState =
        micStateOf(request("/users/$uid/mic/gain", "PUT",
                           JSONObject().put("gain", gain), token))

    // "earpiece": the hand-over requires the occupying call to be on a
    // private route — jim/mic.py refuses it on speaker, where the watch
    // would hear both sides.
    suspend fun handOverMic(uid: String, token: String,
                            reason: String): MicState =
        micStateOf(request("/users/$uid/mic/handover", "POST",
            JSONObject().put("reason", reason).put("route", "earpiece"),
            token))

    suspend fun releaseMic(uid: String, token: String): MicState =
        micStateOf(request("/users/$uid/mic/release", "POST", token = token))

    suspend fun micHistory(uid: String, token: String): List<MicEvent> {
        val arr = getArray("/users/$uid/mic/history", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            MicEvent(o.getString("id"), o.optString("device", ""),
                o.optString("mic_type", ""), o.optString("gain", ""),
                o.optBoolean("live", false), o.optString("started_at", ""))
        }
    }

    private fun captureOf(o: JSONObject) = CaptureRecord(
        o.getString("id"), o.optString("kind", "photo"),
        o.optString("site", ""), o.optString("note", null),
        o.optBoolean("intimate", false), o.optBoolean("sealed", false),
        o.optString("created_at", null))

    suspend fun captureVocabulary(): CaptureVocabulary {
        val o = request("/captures/vocabulary")
        fun table(key: String): Map<String, String> {
            val t = o.optJSONObject(key) ?: return emptyMap()
            val out = mutableMapOf<String, String>()
            t.keys().forEach { k -> out[k] = t.getString(k) }
            return out
        }
        val intimate = mutableListOf<String>()
        o.optJSONArray("intimate")?.let { a ->
            for (i in 0 until a.length()) intimate.add(a.getString(i))
        }
        return CaptureVocabulary(table("kinds"), table("sites"), intimate,
                                 o.optBoolean("vault_required", false))
    }

    suspend fun captures(uid: String, token: String): List<CaptureRecord> {
        val arr = getArray("/users/$uid/captures", token)
        return (0 until arr.length()).map { captureOf(arr.getJSONObject(it)) }
    }

    suspend fun takeCapture(uid: String, token: String, site: String,
                            contentBase64: String, note: String,
                            intimateConsent: Boolean): CaptureRecord {
        val body = JSONObject().put("kind", "photo").put("site", site)
            .put("content", contentBase64).put("provenance", "captured")
            .put("intimate_consent", intimateConsent)
        if (note.isNotBlank()) body.put("note", note)
        return captureOf(request("/users/$uid/captures", "POST", body, token))
    }

    suspend fun captureImage(uid: String, token: String,
                             captureId: String): String =
        request("/users/$uid/captures/$captureId/image", token = token)
            .optString("content", "")

    suspend fun attachCaptures(uid: String, token: String,
                               captureIds: List<String>) {
        val ids = org.json.JSONArray()
        captureIds.forEach { ids.put(it) }
        request("/users/$uid/captures/attach", "POST",
                JSONObject().put("capture_ids", ids), token)
    }

    suspend fun withdrawCapture(uid: String, token: String,
                                captureId: String) {
        request("/users/$uid/captures/$captureId", "DELETE", token = token)
    }

    // ---- the health core: the cabinet, the vigil, and the baseline bands --

    private fun medSlotOf(o: JSONObject) = MedSlot(
        o.optString("slot", ""), o.optString("status", ""),
        o.optString("note", null))

    private fun medOf(o: JSONObject): MedRow {
        val slots = o.optJSONArray("slots")?.let { a ->
            (0 until a.length()).map { medSlotOf(a.getJSONObject(it)) }
        }
        return MedRow(
            o.optString("id", ""), o.optString("name", ""),
            o.optString("dose", ""), o.optString("purpose", null),
            o.optBoolean("critical", false), o.optString("notes", null),
            o.optBoolean("archived", false), o.optString("kind", ""),
            slots,
            if (o.has("taken_today")) o.optInt("taken_today") else null,
            if (o.has("max_per_day") && !o.isNull("max_per_day"))
                o.optInt("max_per_day") else null)
    }

    private fun medsBoardOf(o: JSONObject): MedsBoard {
        val meds = mutableListOf<MedRow>()
        o.optJSONArray("medications")?.let { a ->
            for (i in 0 until a.length()) meds.add(medOf(a.getJSONObject(i)))
        }
        val missed = mutableListOf<MissedDose>()
        o.optJSONArray("missed_critical")?.let { a ->
            for (i in 0 until a.length()) {
                val m = a.getJSONObject(i)
                missed.add(MissedDose(m.optString("name", ""),
                                      m.optString("slot", "")))
            }
        }
        return MedsBoard(o.optString("date", ""), meds, missed,
                         o.optString("disclaimer", ""))
    }

    suspend fun medsBoard(uid: String, token: String): MedsBoard =
        medsBoardOf(request("/meds/$uid", token = token))

    suspend fun addMed(uid: String, token: String, name: String, dose: String,
                       schedule: JSONObject, purpose: String,
                       critical: Boolean): MedRow {
        val body = JSONObject().put("name", name).put("dose", dose)
            .put("schedule", schedule).put("critical", critical)
        if (purpose.isNotBlank()) body.put("purpose", purpose)
        return medOf(request("/meds/$uid", "POST", body, token))
    }

    suspend fun setMedCritical(uid: String, token: String, medId: String,
                               critical: Boolean): MedRow =
        medOf(request("/meds/$uid/$medId", "PUT",
                      JSONObject().put("critical", critical), token))

    /** Stopped, not deleted — the route keeps the history honest. */
    suspend fun stopMed(uid: String, token: String, medId: String): MedRow =
        medOf(request("/meds/$uid/$medId", "DELETE", token = token))

    suspend fun logDose(uid: String, token: String, medId: String,
                        action: String, slot: String?): MedsBoard {
        val body = JSONObject().put("action", action)
        if (slot != null) body.put("slot", slot)
        return medsBoardOf(request("/meds/$uid/$medId/log", "POST", body,
                                   token))
    }

    suspend fun medAdherence(uid: String, token: String): List<AdherenceRow> {
        val o = request("/meds/$uid/adherence", token = token)
        val out = mutableListOf<AdherenceRow>()
        o.optJSONArray("medications")?.let { a ->
            for (i in 0 until a.length()) {
                val m = a.getJSONObject(i)
                out.add(AdherenceRow(
                    m.optString("id", ""), m.optString("name", ""),
                    m.optInt("expected"), m.optInt("taken"),
                    if (m.isNull("rate")) null else m.optDouble("rate")))
            }
        }
        return out
    }

    private fun vigilOf(o: JSONObject) = VigilState(
        o.optBoolean("armed", false),
        o.optString("steward_name", null),
        o.optString("steward_channel", null),
        if (o.has("quiet_days")) o.optDouble("quiet_days") else null,
        o.optString("note", null),
        o.optString("last_heard_at", null),
        if (o.has("silent_hours") && !o.isNull("silent_hours"))
            o.optDouble("silent_hours") else null,
        o.optBoolean("tripped", false))

    suspend fun vigilStatus(uid: String, token: String): VigilState =
        vigilOf(request("/vigil/$uid", token = token))

    suspend fun armVigil(uid: String, token: String, stewardName: String,
                         stewardChannel: String, quietDays: Double,
                         note: String): VigilState {
        val body = JSONObject().put("steward_name", stewardName)
            .put("steward_channel", stewardChannel)
            .put("quiet_days", quietDays)
        if (note.isNotBlank()) body.put("note", note)
        return vigilOf(request("/vigil/$uid", "PUT", body, token))
    }

    suspend fun disarmVigil(uid: String, token: String): VigilState =
        vigilOf(request("/vigil/$uid", "DELETE", token = token))

    /** Idempotent silence check; trips at most once. Opening the screen is
     *  the natural moment to ask whether anybody has gone quiet. */
    suspend fun sweepVigil(uid: String, token: String): VigilState =
        vigilOf(request("/vigil/$uid/sweep", "POST", token = token))

    /** The "I'm okay" button. */
    suspend fun resolveVigil(uid: String, token: String): VigilState =
        vigilOf(request("/vigil/$uid/resolve", "POST", token = token))

    private fun bandOf(o: JSONObject) = BandRow(
        o.optString("metric", ""), o.optString("label", ""),
        o.optString("unit", ""), o.optDouble("margin"),
        o.optBoolean("watch_high", false), o.optBoolean("watch_low", false),
        o.optString("source", ""),
        if (o.isNull("baseline")) null else o.optDouble("baseline"),
        o.optInt("samples"), o.optBoolean("provisional", true),
        if (o.isNull("low_edge")) null else o.optDouble("low_edge"),
        if (o.isNull("high_edge")) null else o.optDouble("high_edge"))

    suspend fun bands(uid: String, token: String): List<BandRow> {
        val o = request("/bands/$uid", token = token)
        val out = mutableListOf<BandRow>()
        o.optJSONArray("bands")?.let { a ->
            for (i in 0 until a.length()) out.add(bandOf(a.getJSONObject(i)))
        }
        return out
    }

    suspend fun setBand(uid: String, token: String, metric: String,
                        margin: Double?, watchHigh: Boolean?,
                        watchLow: Boolean?): BandRow {
        val body = JSONObject()
        if (margin != null) body.put("margin", margin)
        if (watchHigh != null) body.put("watch_high", watchHigh)
        if (watchLow != null) body.put("watch_low", watchLow)
        return bandOf(request("/bands/$uid/$metric", "PUT", body, token))
    }

    /** Back to the default width for this metric. */
    suspend fun resetBand(uid: String, token: String,
                          metric: String): BandRow =
        bandOf(request("/bands/$uid/$metric", "DELETE", token = token))

    // ---- deployment settings: the voice and the mail desk ------------------

    private fun voiceSettingsOf(o: JSONObject): VoiceSettingsOut {
        val voices = mutableListOf<VoiceRow>()
        o.optJSONArray("voices")?.let { a ->
            for (i in 0 until a.length()) {
                val v = a.getJSONObject(i)
                voices.add(VoiceRow(v.optString("id", ""),
                    v.optString("name", ""), v.optString("gender", ""),
                    v.optString("note", "")))
            }
        }
        return VoiceSettingsOut(
            o.optString("provider", ""), o.optString("voice_id", null),
            o.optBoolean("speak_replies", true),
            o.optBoolean("key_set", false), o.optString("key_source", ""),
            voices, o.optBoolean("device_fallback", true))
    }

    suspend fun voiceSettings(): VoiceSettingsOut =
        voiceSettingsOf(request("/settings/voice"))

    suspend fun saveVoiceSettings(provider: String, apiKey: String,
                                  voiceId: String,
                                  speakReplies: Boolean): VoiceSettingsOut {
        val body = JSONObject().put("provider", provider)
            .put("speak_replies", speakReplies)
        if (apiKey.isNotBlank()) body.put("api_key", apiKey)
        if (voiceId.isNotBlank()) body.put("voice_id", voiceId)
        return voiceSettingsOf(request("/settings/voice", "PUT", body))
    }

    suspend fun clearVoiceSettings(): VoiceSettingsOut =
        voiceSettingsOf(request("/settings/voice", "DELETE"))

    /**
     * Is the saved key a working key? Saving only ever reported that the
     * string was written down, and the first anybody knew otherwise was a
     * raw provider error at the moment they asked to be spoken to.
     */
    suspend fun checkVoiceKey(): VoiceKeyCheckOut {
        val o = request("/settings/voice/check", "POST", JSONObject())
        return VoiceKeyCheckOut(
            o.optString("provider", ""), o.optBoolean("ok", false),
            o.optBoolean("checked", false), o.optString("verdict", ""),
            o.optString("detail", ""))
    }

    /**
     * How much speaking is left. Throws on a deployment using the device's
     * own voice, or a provider that publishes no balance — the card treats
     * that as "no line to show" rather than an error worth a red row.
     */
    suspend fun voiceQuota(): VoiceQuotaOut {
        val o = request("/voice/quota")
        return VoiceQuotaOut(
            o.optString("provider", ""), o.optString("tier", null),
            o.optInt("used"), o.optInt("limit"), o.optInt("left"),
            o.optBoolean("exhausted", false), o.optString("resets_at", null))
    }

    private fun mailSettingsOf(o: JSONObject) = MailSettingsOut(
        o.optString("transport", ""), o.optString("source", ""),
        o.optString("host", null), o.optInt("port"),
        o.optString("username", null), o.optString("sender", null),
        o.optString("public_url", ""), o.optBoolean("password_set", false))

    suspend fun mailSettings(): MailSettingsOut =
        mailSettingsOf(request("/settings/mail"))

    suspend fun saveMailSettings(host: String, port: Int, username: String,
                                 password: String, sender: String,
                                 publicUrl: String): MailSettingsOut {
        val body = JSONObject().put("host", host).put("port", port)
        if (username.isNotBlank()) body.put("username", username)
        if (password.isNotBlank()) body.put("password", password)
        if (sender.isNotBlank()) body.put("sender", sender)
        if (publicUrl.isNotBlank()) body.put("public_url", publicUrl)
        return mailSettingsOf(request("/settings/mail", "PUT", body))
    }

    /** Forget the mail server; delivery falls back to the console. */
    suspend fun clearMailSettings(): MailSettingsOut =
        mailSettingsOf(request("/settings/mail", "DELETE"))

    /** Send a real message now — proof the settings can deliver. */
    suspend fun testMail(to: String): String {
        val o = request("/settings/mail/test", "POST",
                        JSONObject().put("to", to))
        return o.optString("to", to)
    }

    // ---- the guide, the help box, and the dock in the corner ---------------

    private fun tutorialStepOf(o: JSONObject): TutorialStep {
        val screens = mutableListOf<Int>()
        o.optJSONArray("screens")?.let { a ->
            for (i in 0 until a.length()) screens.add(a.getInt(i))
        }
        return TutorialStep(o.optString("key", ""),
            o.optString("chapter", ""), o.optString("title", ""),
            o.optString("try_it", ""), o.optString("mode", ""),
            o.optString("what", null), screens)
    }

    private fun tutorialProgressOf(o: JSONObject) = TutorialProgress(
        o.optString("learner_id", ""), o.optString("guide", ""),
        o.optJSONObject("step")?.let { tutorialStepOf(it) },
        o.optInt("done"), o.optInt("total"),
        o.optBoolean("finished", false), o.optString("note", ""))

    suspend fun tutorialOutline(): TutorialOutline {
        val o = request("/tutorial")
        val chapters = mutableListOf<TutorialChapter>()
        o.optJSONArray("chapters")?.let { a ->
            for (i in 0 until a.length()) {
                val c = a.getJSONObject(i)
                val steps = mutableListOf<TutorialStep>()
                c.optJSONArray("steps")?.let { s ->
                    for (j in 0 until s.length())
                        steps.add(tutorialStepOf(s.getJSONObject(j)))
                }
                chapters.add(TutorialChapter(c.optString("chapter", ""),
                                             steps))
            }
        }
        return TutorialOutline(o.optString("guide", ""), chapters)
    }

    suspend fun tutorialStep(key: String): TutorialStep =
        tutorialStepOf(request("/tutorial/steps/$key"))

    /** The lesson covering a given screen, so a screen can explain itself. */
    suspend fun tutorialForScreen(number: Int): TutorialStep =
        tutorialStepOf(request("/tutorial/for-screen/$number"))

    suspend fun startTutorial(learnerId: String): TutorialProgress =
        tutorialProgressOf(request("/tutorial/start", "POST",
            JSONObject().put("learner_id", learnerId)))

    suspend fun tutorialProgress(learnerId: String): TutorialProgress =
        tutorialProgressOf(request("/tutorial/progress/$learnerId"))

    suspend fun markTutorialDone(learnerId: String,
                                 lesson: String): TutorialProgress =
        tutorialProgressOf(request("/tutorial/done", "POST",
            JSONObject().put("learner_id", learnerId).put("lesson", lesson)))

    suspend fun helpTopics(): List<String> {
        val o = request("/help/topics")
        val out = mutableListOf<String>()
        o.optJSONArray("topics")?.let { a ->
            for (i in 0 until a.length()) out.add(a.getString(i))
        }
        return out
    }

    /** The help box: "where is the thing?" It writes nothing. */
    suspend fun askHelp(question: String): HelpAnswer {
        val o = request("/help", "POST",
                        JSONObject().put("question", question))
        return HelpAnswer(o.optString("answer", ""),
            o.optString("source", ""), o.optBoolean("ai", false),
            o.optString("disclosure", ""))
    }

    suspend fun dockVocabulary(): DockVocabulary {
        val o = request("/dock/faces")
        fun table(key: String): Map<String, String> {
            val out = mutableMapOf<String, String>()
            o.optJSONObject(key)?.let { t ->
                t.keys().forEach { k -> out[k] = t.getString(k) }
            }
            return out
        }
        val perSurface = mutableListOf<String>()
        o.optJSONArray("per_surface")?.let { a ->
            for (i in 0 until a.length()) perSurface.add(a.getString(i))
        }
        return DockVocabulary(table("faces"), table("corners"),
                              table("states"), perSurface,
                              o.optBoolean("acts", false))
    }

    private fun dockStateOf(o: JSONObject): DockState {
        val chosen = mutableListOf<String>()
        o.optJSONArray("faces")?.let { a ->
            for (i in 0 until a.length()) chosen.add(a.getString(i))
        }
        return DockState(o.optString("user_id", ""),
            o.optString("corner", ""), o.optString("state", ""),
            o.optString("face", null), chosen, o.optBoolean("set", false),
            o.optString("wanted", ""), o.optBoolean("forced", false),
            o.optString("why", null))
    }

    suspend fun dockState(uid: String, token: String): DockState =
        dockStateOf(request("/dock/$uid", token = token))

    suspend fun configureDock(uid: String, token: String, corner: String?,
                              state: String?, face: String?): DockState {
        val body = JSONObject()
        if (corner != null) body.put("corner", corner)
        if (state != null) body.put("state", state)
        if (face != null) body.put("face", face)
        return dockStateOf(request("/dock/$uid", "PUT", body, token))
    }

    /** One face, as the pane would draw it. Read-only by construction. */
    suspend fun dockFace(uid: String, token: String,
                         name: String): DockFace {
        val o = request("/dock/$uid/face/$name", token = token)
        return DockFace(o.optString("face", ""), o.optString("shows", ""))
    }

    /** The screen that can actually do this face's job. */
    suspend fun dockWhere(face: String): DockWhere {
        val o = request("/dock/where/$face")
        return DockWhere(o.optString("face", ""), o.optInt("screen"),
            o.optString("path", ""), o.optString("title", ""))
    }

    // ---- the wrist and the doorway: watch channel, devices, pairing --------

    private fun watchSetupOf(o: JSONObject): WatchSetup {
        val devices = mutableListOf<WatchDeviceRow>()
        o.optJSONArray("devices")?.let { a ->
            for (i in 0 until a.length()) {
                val d = a.getJSONObject(i)
                devices.add(WatchDeviceRow(d.optString("key", ""),
                                           d.optString("name", "")))
            }
        }
        val steps = mutableListOf<String>()
        o.optJSONArray("steps")?.let { a ->
            for (i in 0 until a.length()) steps.add(a.getString(i))
        }
        return WatchSetup(o.optString("drip_url", ""),
            o.optBoolean("phone_reachable", false),
            o.optString("last_drip_at", null), o.optInt("drips"),
            o.optString("device", ""), devices, steps,
            o.optString("seed_hint", ""))
    }

    suspend fun watchSetup(uid: String, token: String,
                           device: String = "apple_watch"): WatchSetup =
        watchSetupOf(request("/watch/channel/$uid?device=$device",
                             token = token))

    /** Rotating invalidates the old drip token. */
    suspend fun rotateWatchChannel(uid: String, token: String): WatchSetup =
        watchSetupOf(request("/watch/channel/$uid/rotate", "POST",
                             token = token))

    /** Upload the Health app's export.zip. History folds into baselines
     *  only — enrollment day should be quiet. */
    suspend fun seedWatch(uid: String, token: String, data: ByteArray) {
        request("/watch/seed/$uid", "POST", token = token, raw = data)
    }

    /** How to open the Guardian on a phone: the console's URL on this
     *  local network. Same Wi-Fi, no app store. */
    suspend fun pairInfo(): PairInfo {
        val o = request("/pair")
        val how = mutableListOf<String>()
        o.optJSONArray("how")?.let { a ->
            for (i in 0 until a.length()) how.add(a.getString(i))
        }
        return PairInfo(o.optString("console_url", ""),
            o.optString("api_url", ""), o.optBoolean("console_built", false),
            o.optBoolean("reachable", false), o.optBoolean("hosted", false),
            o.optString("qr_svg", ""), how, o.optString("note", ""))
    }

    private fun deviceOf(o: JSONObject) = DeviceRow(
        o.optString("id", ""), o.optString("name", ""),
        o.optString("kind", ""), o.optString("transport", null),
        o.optBoolean("has_llm", false), o.optBoolean("paired", false))

    suspend fun devices(uid: String, token: String): List<DeviceRow> {
        val arr = getArray("/devices/$uid", token)
        return (0 until arr.length()).map { deviceOf(arr.getJSONObject(it)) }
    }

    suspend fun registerDevice(uid: String, token: String, name: String,
                               kind: String, paired: Boolean): DeviceRow =
        deviceOf(request("/devices/$uid", "POST",
            JSONObject().put("name", name).put("kind", kind)
                .put("paired", paired), token))

    // ---- the account the phones never had ----

    private fun sessionOf(o: JSONObject): EnrollResult = EnrollResult(
        o.getString("id"), o.optString("display_name", ""),
        o.getString("user_token"))

    /** A deployment with mail answers pending and sends the code; a local
     *  install with no transport activates directly and answers with the
     *  session. */
    suspend fun signup(email: String, password: String, name: String,
                       language: String? = null): SignupResult {
        val body = JSONObject().put("email", email).put("password", password)
            .put("display_name", name).put("terms_consent", true)
        if (!language.isNullOrBlank() && language != "en") body.put("language", language)
        val o = request("/signup", "POST", body)
        return SignupResult(o.getString("email"), o.optBoolean("verified", false),
            o.optString("verification", ""), o.optString("code_delivery", null),
            if (o.has("user_token")) sessionOf(o) else null)
    }

    suspend fun signin(email: String, password: String): SignInResult {
        val o = request("/signin", "POST",
            JSONObject().put("email", email).put("password", password))
        return SignInResult(o.getString("email"), o.getString("user_id"),
            o.optString("display_name", ""), o.getString("user_token"))
    }

    /** The code proves the inbox; the user is enrolled here, not at signup,
     *  which is why this answers with the same shape enrollment does. */
    suspend fun verifyEmail(email: String, code: String): EnrollResult =
        sessionOf(request("/verify-email", "POST",
            JSONObject().put("email", email).put("code", code)))

    suspend fun resendCode(email: String): String =
        request("/verify-email/resend", "POST",
            JSONObject().put("email", email)).optString("code_delivery", "")

    suspend fun requestPasswordReset(email: String): String =
        request("/password/reset/request", "POST",
            JSONObject().put("email", email)).optString("code_delivery", "")

    /** Every existing session dies with the old password. */
    suspend fun resetPassword(email: String, code: String, newPassword: String): Boolean =
        request("/password/reset", "POST",
            JSONObject().put("email", email).put("code", code)
                .put("new_password", newPassword)).optBoolean("reset", false)

    suspend fun oauthProviders(): List<OAuthDoor> {
        val o = request("/auth/oauth/providers")
        val out = mutableListOf<OAuthDoor>()
        o.optJSONArray("providers")?.let { a ->
            for (i in 0 until a.length()) {
                val d = a.getJSONObject(i)
                out.add(OAuthDoor(d.getString("provider"), d.getString("name"),
                    d.optBoolean("configured", false)))
            }
        }
        return out
    }

    /** No redirect_uri: the backend defaults to its own callback page, and
     *  the phone polls the claim rather than intercepting the browser. */
    suspend fun oauthStart(provider: String): OAuthStarted {
        val o = request("/auth/oauth/$provider/start", "POST", JSONObject())
        return OAuthStarted(o.getString("state"), o.getString("url"))
    }

    suspend fun oauthClaim(state: String): OAuthClaim {
        val o = request("/auth/oauth/claim?state=$state")
        if (!o.optBoolean("ready", false)) return OAuthClaim(false, null)
        return OAuthClaim(true, sessionOf(o))
    }

    suspend fun startSession(uid: String, token: String, device: String): SessionStarted {
        val o = request("/sessions/$uid", "POST",
            JSONObject().put("device", device), token)
        val turns = mutableListOf<ContinuityTurn>()
        var continuityNote: String? = null
        o.optJSONObject("continuity")?.let { c ->
            continuityNote = c.optString("note", "")
            c.optJSONArray("recent_turns")?.let { a ->
                for (i in 0 until a.length()) {
                    val t = a.getJSONObject(i)
                    turns.add(ContinuityTurn(t.getString("role"), t.getString("content")))
                }
            }
        }
        return SessionStarted(o.getString("id"), o.optInt("prior_sessions", 0),
            o.optString("memory", null), turns, continuityNote)
    }

    suspend fun endSession(uid: String, token: String, sessionId: String): Boolean =
        request("/sessions/$uid/$sessionId/end", "POST", token = token)
            .optBoolean("ended", false)

    // ---- the Guardian learns the day ----

    suspend fun calmCatalog(): List<CalmSessionRow> {
        val o = request("/calm")
        val out = mutableListOf<CalmSessionRow>()
        o.optJSONArray("sessions")?.let { a ->
            for (i in 0 until a.length()) {
                val s = a.getJSONObject(i)
                out.add(CalmSessionRow(s.getString("kind"), s.getString("title"),
                    s.optInt("minutes", 0), s.optString("what", "")))
            }
        }
        return out
    }

    /** A protocol, not a generation — the counts never vary. */
    suspend fun startCalm(uid: String, token: String, kind: String): CalmStarted {
        val o = request("/calm/$uid/$kind", "POST", token = token)
        val steps = mutableListOf<CalmStep>()
        o.optJSONArray("steps")?.let { a ->
            for (i in 0 until a.length()) {
                val s = a.getJSONObject(i)
                steps.add(CalmStep(s.getString("say"), s.optInt("seconds", 0)))
            }
        }
        return CalmStarted(o.getString("kind"), o.getString("title"),
            steps, o.optString("note", ""))
    }

    suspend fun calmHistory(uid: String, token: String): List<CalmHistoryRow> {
        val arr = getArray("/calm/$uid/history", token)
        return (0 until arr.length()).map { i ->
            val s = arr.getJSONObject(i)
            CalmHistoryRow(s.optString("title", ""), s.optString("at", ""))
        }
    }

    suspend fun workoutPlan(uid: String, token: String, minutes: Int,
                            level: String, focus: String): WorkoutPlanK {
        val o = request("/fitness/$uid/plan", "POST",
            JSONObject().put("minutes", minutes).put("level", level)
                .put("focus", focus), token)
        val blocks = mutableListOf<WorkoutBlockK>()
        o.optJSONArray("blocks")?.let { a ->
            for (i in 0 until a.length()) {
                val b = a.getJSONObject(i)
                blocks.add(WorkoutBlockK(b.getString("name"),
                    b.optInt("seconds", 0), b.optString("cue", "")))
            }
        }
        return WorkoutPlanK(o.getString("level"), o.optString("focus", ""), blocks)
    }

    suspend fun mealPlan(uid: String, token: String, goal: String,
                         days: Int): MealPlanK {
        val o = request("/nutrition/$uid/plan", "POST",
            JSONObject().put("goal", goal)
                .put("preferences", org.json.JSONArray()).put("days", days),
            token)
        val shape = o.optJSONObject("shape")
        val dayRows = mutableListOf<MealDayK>()
        o.optJSONArray("days")?.let { a ->
            for (i in 0 until a.length()) {
                val d = a.getJSONObject(i)
                val meals = mutableListOf<String>()
                d.optJSONArray("meals")?.let { m ->
                    for (j in 0 until m.length()) {
                        val row = m.getJSONObject(j)
                        meals.add("${row.optString("slot", "")}: ${row.optString("name", "")}")
                    }
                }
                dayRows.add(MealDayK(d.optInt("day_number", i + 1), meals))
            }
        }
        return MealPlanK(shape?.optString("why", "") ?: "",
            shape?.optInt("orientation_calories", 0) ?: 0, dayRows,
            o.optString("disclaimer", ""))
    }

    /** Ambient watching: an ordinary activity is context, not a reading. */
    suspend fun observeActivity(uid: String, token: String, activity: String,
                                note: String?): ActivityWatchK {
        val body = JSONObject().put("activity", activity)
        if (!note.isNullOrBlank()) body.put("note", note)
        val o = request("/activity/$uid", "POST", body, token)
        return ActivityWatchK(o.optBoolean("proactive", false),
            o.optBoolean("watching", false),
            parseGuidance(o.optJSONObject("intervention")))
    }

    suspend fun declareCondition(uid: String, token: String, condition: String,
                                 note: String?): List<String> {
        val body = JSONObject().put("condition", condition)
        if (!note.isNullOrBlank()) body.put("note", note)
        val o = request("/conditions/$uid", "POST", body, token)
        val out = mutableListOf<String>()
        o.optJSONArray("known_conditions")?.let { a ->
            for (i in 0 until a.length()) out.add(a.getString(i))
        }
        return out
    }

    suspend fun setPersonality(uid: String, token: String, tone: String) {
        request("/personality/$uid", "PUT", JSONObject().put("tone", tone),
            token)
    }

    /** The server checks the consent, not this shell — a refusal arrives in
     *  the server's words. */
    suspend fun giveContext(uid: String, token: String, source: String,
                            kind: String, data: JSONObject): String =
        request("/context/$uid", "POST",
            JSONObject().put("source", source).put("kind", kind)
                .put("data", data), token).getString("id")

    suspend fun updateGoal(uid: String, token: String, goalId: String,
                           progress: Double, status: String) {
        request("/goals/$uid/$goalId", "PATCH",
            JSONObject().put("progress", progress).put("status", status),
            token)
    }

    suspend fun insights(uid: String, token: String): List<InsightRowK> {
        val arr = getArray("/insights/$uid", token)
        return (0 until arr.length()).map { i ->
            val s = arr.getJSONObject(i)
            InsightRowK(s.optString("id", ""), s.optString("message", ""))
        }
    }

    suspend fun eventsCount(uid: String, token: String): Int =
        getArray("/events/$uid", token).length()

    suspend fun progressReport(uid: String, token: String): ReportK {
        val o = request("/report/$uid", token = token)
        val checkins = o.optJSONObject("checkins")
        return ReportK(checkins?.optInt("count", 0) ?: 0,
            checkins?.optDouble("avg_mood") ?: Double.NaN)
    }

    /** An ambient, unprompted word from the coach. */
    suspend fun companionCheckin(uid: String, token: String): String =
        request("/companion/$uid", "POST", token = token).getString("content")

    suspend fun sendGuidanceFeedback(uid: String, token: String, rating: String) {
        request("/feedback/$uid", "POST", JSONObject().put("rating", rating),
            token)
    }

    suspend fun coachExchangeCount(uid: String, token: String): Int =
        getArray("/coach/$uid", token).length()

    // ---- the specialist economy ----

    suspend fun specialists(): List<SpecialistRowK> {
        val arr = getArray("/specialists")
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            SpecialistRowK(o.getString("condition"), o.optString("mode", ""),
                o.optString("label", ""))
        }
    }

    suspend fun seedSpecialists(): Int =
        request("/specialists/seed", "POST").optInt("created", 0)

    suspend fun seedTandemSpecialists(): Int =
        request("/specialists/seed/tandem", "POST").optInt("created", 0)

    suspend fun specialistsCatalog(): List<CatalogStarterK> {
        val o = request("/specialists/catalog")
        val out = mutableListOf<CatalogStarterK>()
        o.optJSONArray("starters")?.let { a ->
            for (i in 0 until a.length()) {
                val s = a.optJSONObject(i) ?: continue
                out.add(CatalogStarterK(s.optString("profile_id", null),
                    s.optString("display_name", null)))
            }
        }
        return out
    }

    /** Anyone on QRME, not only the thirty-four on the shelf. Takes a
     *  `@handle`, a `prof_…` id, or words. */
    suspend fun searchSpecialists(query: String): SpecialistSearchK {
        val q = java.net.URLEncoder.encode(query, "UTF-8")
        val o = request("/specialists/search?q=$q")
        val rows = mutableListOf<SpecialistFoundK>()
        o.optJSONArray("results")?.let { a ->
            for (i in 0 until a.length()) {
                val s = a.optJSONObject(i) ?: continue
                val pid = s.optString("profile_id", null) ?: continue
                rows.add(SpecialistFoundK(
                    pid,
                    s.optString("display_name", pid),
                    s.optString("purpose", null),
                    s.optBoolean("attachable", true),
                    s.optString("standing", null)))
            }
        }
        return SpecialistSearchK(rows, o.optBoolean("capped", false),
            o.optInt("limit", 0))
    }

    suspend fun attachSpecialist(condition: String, qrmeProfileId: String,
                                 label: String) {
        request("/specialists", "POST",
            JSONObject().put("condition", condition).put("mode", "tandem")
                .put("qrme_profile_id", qrmeProfileId).put("label", label))
    }

    suspend fun referralClinicians(uid: String, token: String,
                                   condition: String): ClinicianSearchK {
        val o = request("/users/$uid/referral/clinicians?condition=$condition",
            token = token)
        val labels = mutableListOf<String>()
        o.optJSONArray("clinicians")?.let { a ->
            for (i in 0 until a.length()) {
                val c = a.optJSONObject(i) ?: continue
                labels.add(c.optString("label",
                    c.optString("display_name", "")))
            }
        }
        return ClinicianSearchK(labels, o.optString("reason", null))
    }

    /** Nothing is released by preparing — the signing ceremony is QRME's. */
    suspend fun prepareReferral(uid: String, token: String, condition: String,
                                providerId: String): ReferralPreparedK {
        val o = request("/users/$uid/referral/prepare", "POST",
            JSONObject().put("condition", condition)
                .put("provider_id", providerId), token)
        return ReferralPreparedK(o.optBoolean("prepared", false),
            o.optString("reason", null), o.optString("note", null))
    }

    /** A report, not an action: JIM cannot observe QRME's ceremony. */
    suspend fun markReferralReleased(uid: String, token: String,
                                     requestId: String) {
        request("/users/$uid/referral/requests/$requestId/released", "POST",
            token = token)
    }

    suspend fun referralRequests(uid: String,
                                 token: String): List<ReferralRequestRowK> {
        val arr = getArray("/users/$uid/referral/requests", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            ReferralRequestRowK(o.getString("id"), o.optString("condition", ""))
        }
    }

    /** A refusal is started:false with a reason — information, not a fault. */
    suspend fun startSpecialistTask(uid: String, token: String,
                                    condition: String, goal: String): TaskStartedK {
        val o = request("/users/$uid/specialist-tasks", "POST",
            JSONObject().put("condition", condition).put("goal", goal), token)
        return TaskStartedK(o.optBoolean("started", false),
            o.optString("reason", null), o.optString("id", null))
    }

    suspend fun specialistTasks(uid: String,
                                token: String): List<SpecialistTaskRowK> {
        val arr = getArray("/users/$uid/specialist-tasks", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            SpecialistTaskRowK(o.getString("id"), o.optString("goal", ""),
                o.optString("status", ""))
        }
    }

    suspend fun specialistTask(uid: String, token: String,
                               taskId: String): SpecialistTaskViewK {
        val o = request("/users/$uid/specialist-tasks/$taskId", token = token)
        return SpecialistTaskViewK(o.optString("status", ""),
            o.optString("next_phase", null), o.optString("note", null))
    }

    suspend fun advanceSpecialistTask(uid: String, token: String,
                                      taskId: String): SpecialistTaskViewK {
        val o = request("/users/$uid/specialist-tasks/$taskId/advance", "POST",
            token = token)
        return SpecialistTaskViewK(o.optString("status", ""),
            o.optString("next_phase", null), o.optString("note", null))
    }




    // ---- the sticker and the relay ----

    /** A sticker someone can scan to reach help on your behalf. */
    suspend fun beacons(uid: String, token: String): List<BeaconRowK> {
        val arr = getArray("/users/$uid/beacons", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            BeaconRowK(o.getString("id"), o.optString("label", ""),
                o.optInt("scans", 0), o.optBoolean("active", true))
        }
    }

    suspend fun placeBeacon(uid: String, token: String, label: String,
                            placement: String?) {
        val body = JSONObject().put("kind", "site").put("label", label)
        if (!placement.isNullOrBlank()) body.put("placement", placement)
        request("/users/$uid/beacons", "POST", body, token)
    }

    suspend fun retireBeacon(bid: String, token: String) {
        request("/beacons/$bid", "DELETE", token = token)
    }

    /** What a stranger sees before deciding to raise the alarm — public on
     *  purpose, the scanner has no account. */
    suspend fun beaconCard(bid: String): BeaconCardK {
        val o = request("/c/$bid/card")
        return BeaconCardK(o.getString("beacon"), o.optString("first_name", ""),
            o.optString("note", ""), o.optString("badge", ""))
    }

    suspend fun raiseBeaconAlarm(bid: String): BeaconAlarmK {
        val o = request("/c/$bid/alarm", "POST", JSONObject())
        return BeaconAlarmK(o.optString("badge", ""), o.optString("note", ""))
    }

    /** The scanned page itself is HTML for a stranger's browser; fetching
     *  it proves the door is live before handing it to the system one. */
    suspend fun scannedBeaconPage(bid: String): BeaconPageK =
        withContext(Dispatchers.IO) {
            val url = URL("$base/c/$bid")
            val conn = (url.openConnection() as HttpURLConnection)
            conn.setRequestProperty("accept-language", L10n.deviceLanguage())
            val text = conn.inputStream.bufferedReader().use { it.readText() }
            conn.disconnect(); BeaconPageK(text, url.toString())
        }

    suspend fun relayChannel(): RelayChannelK {
        val o = request("/relay/channel")
        return RelayChannelK(o.optBoolean("configured", false),
            o.optString("envelope", ""), o.optString("note", ""))
    }

    suspend fun relayRoster(): RelayRosterK {
        val o = request("/relay/roster")
        val names = mutableListOf<String>()
        o.optJSONArray("roster")?.let { a ->
            for (i in 0 until a.length()) names.add(a.getString(i))
        }
        return RelayRosterK(names, o.optString("ceiling", ""),
            o.optString("note", ""))
    }

    suspend fun relayRota(): RelayRotaK {
        val o = request("/relay/rota")
        val onNow = mutableListOf<String>()
        o.optJSONArray("on_now")?.let { a ->
            for (i in 0 until a.length()) onNow.add(a.getString(i))
        }
        return RelayRotaK(o.optString("timezone", ""), onNow,
            o.optBoolean("anybody_on_shift", false), o.optString("note", ""))
    }

    suspend fun socialBeacon(cid: String, token: String): String {
        val o = request("/social/connection/$cid/beacon", token = token)
        return "${o.optString("handle", "")} \u2192 ${o.optString("presence_url", "")}"
    }

    suspend fun disconnectSocial(cid: String, token: String) {
        request("/social/connection/$cid", "DELETE", token = token)
    }

    suspend fun unbindRobot(uid: String, token: String, robotId: String) {
        request("/robots/$uid/$robotId", "DELETE", token = token)
    }

    // ---- safe knowledge excursions + the community window ----

    private fun excursionOf(o: JSONObject) = ExcursionRowK(
        o.getString("id"), o.optString("topic", ""), o.optInt("redactions", 0),
        o.optBoolean("left_host"),
        if (o.isNull("findings")) null else o.optString("findings"),
        o.optBoolean("learned"))

    suspend fun excursions(uid: String, token: String): List<ExcursionRowK> {
        val arr = getArray("/excursions/$uid", token)
        return (0 until arr.length()).map { i -> excursionOf(arr.getJSONObject(i)) }
    }

    /** Study a topic without carrying the person's PHI out: the row answers
     *  with how much was redacted and whether the question left this host. */
    suspend fun startExcursion(uid: String, token: String, topic: String,
                               question: String): ExcursionRowK =
        excursionOf(request("/excursions/$uid", "POST",
            JSONObject().put("topic", topic).put("question", question), token))

    suspend fun excursionEntry(cid: String, token: String): ExcursionRowK =
        excursionOf(request("/excursions/entry/$cid", token = token))

    /** Fold the findings into guidance context; the local model uses them. */
    suspend fun learnExcursion(cid: String, token: String): ExcursionLearnedK {
        val o = request("/excursions/entry/$cid/learn", "POST", JSONObject(), token)
        return ExcursionLearnedK(o.optBoolean("learned"),
            o.optBoolean("already_learned"),
            if (o.isNull("note")) null else o.optString("note"))
    }

    /** The doors that were opened — the room's id and the time, and nothing
     *  from inside the room. */
    suspend fun communityVisits(uid: String, token: String): List<CommunityVisitRowK> {
        val arr = getArray("/community/$uid/visits", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            CommunityVisitRowK(o.optString("room_id", ""), o.optString("at", ""))
        }
    }

    // ---- the voice pair: say it aloud, and hear what was said ----

    /** Text in, audio out. A deployment with no speaking service answers
     *  503 — the panel falls back to the device's own voice, because
     *  silence would be the wrong failure. */
    suspend fun speakAloud(text: String): ByteArray = withContext(Dispatchers.IO) {
        val conn = (URL("$base/voice/speak").openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            setRequestProperty("content-type", "application/json")
            setRequestProperty("accept-language", L10n.deviceLanguage())
            connectTimeout = 8000; readTimeout = 20000
            doOutput = true
            outputStream.use {
                it.write(JSONObject().put("text", text).toString().toByteArray())
            }
        }
        val code = conn.responseCode
        if (code !in 200..299) {
            val said = conn.errorStream?.bufferedReader()?.use { it.readText() } ?: ""
            conn.disconnect()
            // The path from the connection itself, not a second literal
            // the route audit would have to attribute on its own.
            Problems.record("POST", conn.url.path, code)
            val message = runCatching {
                JSONObject(said).optString("message").ifBlank {
                    JSONObject(said).optString("detail")
                }
            }.getOrNull()
            throw ApiException(if (message.isNullOrBlank()) "HTTP $code" else message)
        }
        val bytes = conn.inputStream.use { it.readBytes() }
        conn.disconnect()
        bytes
    }

    /** Recorded speech in, words out. The audio is not stored server-side. */
    suspend fun transcribe(audioBase64: String, filename: String): TranscribedK {
        val o = request("/voice/transcribe", "POST",
            JSONObject().put("audio_base64", audioBase64).put("filename", filename))
        return TranscribedK(o.optString("text", ""))
    }

    /** The backend's own pulse, and whether a QRME tandem stands behind it. */
    /**
     * The backend's own version, for the guard that compares it with this
     * build's. Empty when the field is absent, which is a real answer and
     * not an error: a backend old enough to predate the field is exactly
     * the deployment the guard exists to name. `health` above reads the
     * same response and throws this away, which is why nothing on this
     * shell could tell a stale backend from a current one.
     */
    suspend fun backendVersion(): String {
        return JSONObject(request("/health")).optString("version", "")
    }

    suspend fun health(): HealthK {
        val o = request("/health")
        return HealthK(o.optString("status", ""), o.optBoolean("tandem"))
    }

    /** QRME's public feed through the tandem — read-only by construction,
     *  and a 409 in the server's words when no QRME endpoint is set. */
    suspend fun communityFeed(uid: String, token: String): CommunityFeedViewK {
        val o = request("/community/$uid/feed", token = token)
        val arr = o.optJSONArray("items")
        val items = (0 until (arr?.length() ?: 0)).map { i ->
            val it = arr!!.getJSONObject(i)
            CommunityFeedItemK(
                if (it.isNull("kind")) null else it.optString("kind"),
                if (it.isNull("title")) null else it.optString("title"),
                if (it.isNull("topic")) null else it.optString("topic"))
        }
        return CommunityFeedViewK(o.optString("note", ""),
            if (o.isNull("open_in_qrme")) null else o.optString("open_in_qrme"),
            items)
    }

    // ---- the purse and the membership ----

    suspend fun budgets(uid: String, token: String): List<BudgetRowK> {
        val o = request("/budgets/$uid", token = token)
        val out = mutableListOf<BudgetRowK>()
        o.optJSONArray("budgets")?.let { a ->
            for (i in 0 until a.length()) {
                val b = a.getJSONObject(i)
                out.add(BudgetRowK(b.getString("category"),
                    b.optDouble("monthly_limit", 0.0),
                    b.optDouble("spent", 0.0), b.optString("standing", "")))
            }
        }
        return out
    }

    /** This much per month for this category. */
    suspend fun setBudget(uid: String, token: String, category: String,
                          monthlyLimit: Double) {
        request("/budgets/$uid", "PUT",
            JSONObject().put("category", category)
                .put("monthly_limit", monthlyLimit), token)
    }

    suspend fun clearBudget(uid: String, token: String, category: String) {
        request("/budgets/$uid/$category", "DELETE", token = token)
    }

    /** The route says account and means the person: tiers are keyed by the
     *  user id, and the bearer must be that user's own. */
    suspend fun membership(uid: String, token: String): MembershipK =
        membershipOf(request("/memberships/$uid", token = token))

    /** Join a plan or move between them. Billing is simulated. */
    suspend fun subscribe(uid: String, token: String, plan: String): MembershipK =
        membershipOf(request("/memberships/$uid", "POST",
            JSONObject().put("plan", plan), token))

    /** End it. The person keeps their record and every emergency path. */
    suspend fun cancelMembership(uid: String, token: String): MembershipK =
        membershipOf(request("/memberships/$uid", "DELETE", token = token))

    private fun membershipOf(o: JSONObject): MembershipK {
        val storage = o.optJSONObject("storage")
        val readers = mutableListOf<String>()
        storage?.optJSONArray("who_can_read")?.let { a ->
            for (i in 0 until a.length()) readers.add(a.getString(i))
        }
        return MembershipK(o.getString("plan"), o.optString("title", ""),
            o.optDouble("price_usd", 0.0),
            storage?.optString("means", "") ?: "", readers)
    }

    // ---- the record and the veil ----

    /** An empty list with no record kept is a different fact from nobody
     *  having looked, and the shape says which. */
    suspend fun accessLog(uid: String, token: String): AccessLogK {
        val o = request("/access-log/$uid", token = token)
        val entries = mutableListOf<String>()
        o.optJSONArray("entries")?.let { a ->
            for (i in 0 until a.length()) {
                val e = a.optJSONObject(i) ?: continue
                entries.add("${e.optString("action", "")} \u00b7 ${e.optString("at", "")}")
            }
        }
        return AccessLogK(o.optBoolean("vaulted", false),
            o.optBoolean("access_record_kept", false), entries,
            o.optString("note", ""))
    }

    /** The other half of the same question: what was *done*, and whether the
     *  saying of it has been edited since.
     *
     *  Each row's sentence is taken from the catalogue this same answer
     *  carried, never from a second copy kept in the shell — two lists of the
     *  same actions is one list and one place for them to disagree. An action
     *  the catalogue does not name falls back to its own name, so a row
     *  written by something newer than this build is still legible. */
    suspend fun auditLog(uid: String, token: String): AuditLogK {
        val o = request("/audit/$uid", token = token)
        val says = mutableMapOf<String, String>()
        val watched = mutableListOf<String>()
        o.optJSONArray("catalogue")?.let { a ->
            for (i in 0 until a.length()) {
                val e = a.optJSONObject(i) ?: continue
                val said = e.optString("description", "")
                says[e.optString("action", "")] = said
                watched.add(said)
            }
        }
        val entries = mutableListOf<String>()
        o.optJSONArray("trail")?.let { a ->
            for (i in 0 until a.length()) {
                val e = a.optJSONObject(i) ?: continue
                val action = e.optString("action", "")
                val ref = e.optString("ref", "")
                val said = says[action] ?: action
                val tail = if (ref.isEmpty()) "" else " — $ref"
                entries.add("$said$tail · ${e.optString("at", "")}")
            }
        }
        val chain = o.optJSONObject("integrity")
        return AuditLogK(entries, o.optInt("count", 0),
            chain?.optBoolean("intact", false) ?: false,
            if (chain != null && chain.has("broken_at_seq"))
                chain.optInt("broken_at_seq") else null,
            watched, o.optString("retention", ""))
    }

    suspend fun cloudStatus(): CloudStatusK {
        val o = request("/cloud/status")
        return CloudStatusK(o.optBoolean("cloud", false),
            o.optString("model", null), o.optString("fallback", ""),
            o.optString("contribution", ""))
    }

    suspend fun cloudContribution(uid: String, token: String): ContributionK {
        val o = request("/users/$uid/cloud-contribution", token = token)
        return ContributionK(o.optBoolean("opted_in", false),
            o.optString("policy", ""))
    }

    suspend fun revokeCloudContribution(uid: String, token: String): String =
        request("/users/$uid/cloud-contribution/revoke", "POST", token = token)
            .optString("note", "")

    /** Open, unaccepted alarms on this account's site beacons. */
    suspend fun incidents(uid: String, token: String): List<String> {
        val arr = getArray("/users/$uid/incidents", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            "${o.optString("kind", "")} \u00b7 ${o.optString("at", "")}"
        }
    }

    /** Escalations and whether each reached anyone. */
    suspend fun pages(uid: String, token: String): List<PageRowK> {
        val arr = getArray("/users/$uid/pages", token)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            PageRowK(o.optString("to", ""), o.optBoolean("delivered", false),
                o.optString("sent_at", ""))
        }
    }

    /** Used only to find local rooms and events through the community door. */
    suspend fun setLocality(uid: String, token: String, locality: String): String =
        request("/users/$uid/locality", "PUT",
            JSONObject().put("locality", locality), token)
            .optString("locality", "")

    suspend fun plans(): List<PlanRowK> {
        val o = request("/plans")
        val out = mutableListOf<PlanRowK>()
        o.optJSONArray("plans")?.let { a ->
            for (i in 0 until a.length()) {
                val p = a.getJSONObject(i)
                out.add(PlanRowK(p.getString("plan"), p.optString("title", ""),
                    p.optInt("price_usd", 0)))
            }
        }
        return out
    }

    /** What a consented care provider sees — and so what the person can see
     *  that they see. */
    suspend fun providerSummary(uid: String, token: String): ProviderSummaryK {
        val o = request("/provider/$uid", token = token)
        val conditions = mutableListOf<String>()
        o.optJSONArray("known_conditions")?.let { a ->
            for (i in 0 until a.length()) conditions.add(a.getString(i))
        }
        return ProviderSummaryK(o.optString("display_name", ""), conditions,
            o.optInt("escalations", 0))
    }
}

data class MoneyAccount(val id: String, val kind: String,
                        val institution: String, val label: String?,
                        val last4: String?, val credentials: String,
                        val balance: Double?)

data class MoneyOrder(val assetClass: String, val amount: Double,
                      val status: String, val rationale: String?)

data class MoneyDesk(val name: String, val trade: String, val location: String)

data class MoneyWarning(val kind: String, val message: String,
                        val specialist: String?, val desks: List<MoneyDesk>)

data class Appointment(val id: String, val title: String,
                       val whenAt: String, val whereAt: String?,
                       val status: String)

data class ScheduleOverview(val appointments: List<Appointment>,
                            val emailAvailable: Boolean,
                            val labels: Map<String, String>,
                            val note: String)

data class TandemShop(val id: String, val name: String, val seller: String,
                      val tag: String?)

data class ShopReceipt(val id: String, val qrmeOrderId: String,
                       val title: String, val amount: Double,
                       val currency: String, val status: String)

data class ShoppingOverview(val shops: List<TandemShop>,
                            val receipts: List<ShopReceipt>,
                            val labels: Map<String, String>,
                            val note: String)

data class CirclePerson(val userId: String, val displayName: String?)

data class CircleThread(val otherId: String, val otherName: String?,
                        val messages: Int)

data class CircleMessage(val id: String, val senderId: String,
                         val body: String, val sentAt: String)

data class CircleLink(val label: String, val url: String)

data class CircleHomepage(val userId: String, val displayName: String?,
                          val headline: String, val about: String,
                          val bg: String, val accent: String,
                          val links: List<CircleLink>,
                          val topFriends: List<CirclePerson>,
                          val editable: Boolean)

data class CircleOverview(val features: Map<String, Boolean>,
                          val contacts: List<CirclePerson>,
                          val invitedMe: List<CirclePerson>,
                          val awaiting: List<CirclePerson>,
                          val threads: List<CircleThread>,
                          val homepage: CircleHomepage,
                          val labels: Map<String, String>,
                          val note: String)

data class MoneyOverview(val accounts: List<MoneyAccount>,
                         val savingsGoal: Double?,
                         val orders: List<MoneyOrder>,
                         val note: String,
                         val labels: Map<String, String>)

/** What the deployment can and cannot reach. */
data class OfflinePosture(val offline: Boolean,
                          val externalTransmissionPossible: Boolean,
                          val localDestinationsAllowed: String,
                          val guarantees: List<String>)

data class MemoryMoment(val kind: String, val ref: String,
                        val line: String?, val at: String?)
data class MemoryShelf(val moments: List<MemoryMoment>,
                       val readable: Boolean, val held: Int)

data class ContinuityState(val built: Boolean,
                           val carries: String,
                           val note: String?,
                           val observations: Int,
                           val conditioning: Boolean,
                           val vector: Map<String, Double>,
                           val meanings: Map<String, String>,
                           val method: String?)

data class CarePlanRow(val id: String, val goal: String, val plan: String?,
                       val sealedInQrmeVault: Boolean, val createdAt: String?)
data class CareTeamState(val linked: Boolean, val orgId: String?,
                         val departmentId: String?,
                         val latestPlan: CarePlanRow?)
/** Channel 2's current state. `capped` means a call is in progress and the
 *  agent has narrowed itself regardless of the owner's setting. */
data class MicState(val listening: Boolean, val attached: Boolean,
                    val device: String?, val micType: String?,
                    val gain: String?, val capped: Boolean,
                    val hears: String?)
data class MicEvent(val id: String, val device: String, val micType: String,
                    val gain: String, val live: Boolean,
                    val startedAt: String)
data class MicTypeChoices(val personal: List<String>,
                          val ambient: List<String>, val rule: String?)
data class MicGainLevel(val gain: String, val reachesOthers: Boolean,
                        val describes: String?)
data class MicGainChoices(val levels: List<MicGainLevel>,
                          val default: String, val rule: String?)
data class CaptureVocabulary(val kinds: Map<String, String>,
                             val sites: Map<String, String>,
                             val intimate: List<String>,
                             val vaultRequired: Boolean)
data class CaptureRecord(val id: String, val kind: String, val site: String,
                         val note: String?, val intimate: Boolean,
                         val sealed: Boolean, val createdAt: String?)

/** One dose slot of a scheduled medication:
 *  taken | skipped | upcoming | due | missed. */
data class MedSlot(val slot: String, val status: String, val note: String?)
/** A medication on today's board. Scheduled rows carry `slots`; as-needed
 *  rows carry `takenToday` and `maxPerDay` instead. */
data class MedRow(val id: String, val name: String, val dose: String,
                  val purpose: String?, val critical: Boolean,
                  val notes: String?, val archived: Boolean,
                  val kind: String, val slots: List<MedSlot>?,
                  val takenToday: Int?, val maxPerDay: Int?)
data class MissedDose(val name: String, val slot: String)
data class MedsBoard(val date: String, val medications: List<MedRow>,
                     val missedCritical: List<MissedDose>,
                     val disclaimer: String)
data class AdherenceRow(val id: String, val name: String, val expected: Int,
                        val taken: Int, val rate: Double?)
/** The vigil's answer. Until armed the route says `{"armed": false}` and
 *  nothing else, which is why everything past `armed` is nullable. */
data class VigilState(val armed: Boolean, val stewardName: String?,
                      val stewardChannel: String?, val quietDays: Double?,
                      val note: String?, val lastHeardAt: String?,
                      val silentHours: Double?, val tripped: Boolean)
/** One metric's band: the learned baseline and where the edges sit. Edges
 *  are null until the baseline stops being provisional. */
data class BandRow(val metric: String, val label: String, val unit: String,
                   val margin: Double, val watchHigh: Boolean,
                   val watchLow: Boolean, val source: String,
                   val baseline: Double?, val samples: Int,
                   val provisional: Boolean, val lowEdge: Double?,
                   val highEdge: Double?)

data class VoiceRow(val id: String, val name: String, val gender: String,
                    val note: String)
/** What the API may say about the voice — never the key itself. */
data class VoiceSettingsOut(val provider: String, val voiceId: String?,
                            val speakReplies: Boolean, val keySet: Boolean,
                            val keySource: String, val voices: List<VoiceRow>,
                            val deviceFallback: Boolean)
/**
 * What is left of the speaking allowance.
 *
 * `used` is what has been *spent* — the provider's own field is named
 * `character_count`, which reads like a balance and is not one. The backend
 * does the subtraction and floors it at zero, because a spent account
 * reports a count above its limit.
 */
/**
 * The verdict on a saved speaking key.
 *
 * `verdict` is the key, not the sentence — it travels on the wire so each
 * client renders it from its own table. `detail` is the English behind it,
 * for a verdict this shell has no row for yet.
 */
data class VoiceKeyCheckOut(val provider: String, val ok: Boolean,
                            val checked: Boolean, val verdict: String,
                            val detail: String)
data class VoiceQuotaOut(val provider: String, val tier: String?,
                         val used: Int, val limit: Int, val left: Int,
                         val exhausted: Boolean, val resetsAt: String?)
/** The mail configuration — never the password, only whether one is set. */
data class MailSettingsOut(val transport: String, val source: String,
                           val host: String?, val port: Int,
                           val username: String?, val sender: String?,
                           val publicUrl: String, val passwordSet: Boolean)

/** One lesson, text mode: `what` and `screens` are present. */
data class TutorialStep(val key: String, val chapter: String,
                        val title: String, val tryIt: String,
                        val mode: String, val what: String?,
                        val screens: List<Int>)
data class TutorialChapter(val chapter: String,
                           val steps: List<TutorialStep>)
data class TutorialOutline(val guide: String,
                           val chapters: List<TutorialChapter>)
data class TutorialProgress(val learnerId: String, val guide: String,
                            val step: TutorialStep?, val done: Int,
                            val total: Int, val finished: Boolean,
                            val note: String)
data class HelpAnswer(val answer: String, val source: String,
                      val ai: Boolean, val disclosure: String)
data class DockVocabulary(val faces: Map<String, String>,
                          val corners: Map<String, String>,
                          val states: Map<String, String>,
                          val perSurface: List<String>, val acts: Boolean)
data class DockState(val userId: String, val corner: String,
                     val state: String, val face: String?,
                     val faces: List<String>, val isSet: Boolean,
                     val wanted: String, val forced: Boolean,
                     val why: String?)
data class DockFace(val face: String, val shows: String)
data class DockWhere(val face: String, val screen: Int, val path: String,
                     val title: String)

data class WatchDeviceRow(val key: String, val name: String)
/** The setup card: drip URL, this device's recipe, arrivals so far. */
data class WatchSetup(val dripUrl: String, val phoneReachable: Boolean,
                      val lastDripAt: String?, val drips: Int,
                      val device: String, val devices: List<WatchDeviceRow>,
                      val steps: List<String>, val seedHint: String)
/** The local pairing card — the console's URL on this network. */
data class DripAckK(val received: Int, val noticed: Boolean)
data class PairInfo(val consoleUrl: String, val apiUrl: String,
                    val consoleBuilt: Boolean, val reachable: Boolean,
                    val hosted: Boolean, val qrSvg: String, val how: List<String>,
                    val note: String)
data class DeviceRow(val id: String, val name: String, val kind: String,
                     val transport: String?, val hasLlm: Boolean,
                     val paired: Boolean)

/** Signup's two shapes under one roof: `session` is filled on a local
 *  install that activates directly, `codeDelivery` when the code is out. */
data class SignupResult(val email: String, val verified: Boolean,
                        val verification: String, val codeDelivery: String?,
                        val session: EnrollResult?)
data class SignInResult(val email: String, val userId: String,
                        val displayName: String, val userToken: String)
data class OAuthDoor(val provider: String, val name: String,
                     val configured: Boolean)
data class OAuthStarted(val state: String, val url: String)
data class OAuthClaim(val ready: Boolean, val session: EnrollResult?)
data class ContinuityTurn(val role: String, val content: String)
data class SessionStarted(val id: String, val priorSessions: Int,
                          val memory: String?, val turns: List<ContinuityTurn>,
                          val continuityNote: String?)

data class CalmSessionRow(val kind: String, val title: String,
                          val minutes: Int, val what: String)
data class CalmStep(val say: String, val seconds: Int)
data class CalmStarted(val kind: String, val title: String,
                       val steps: List<CalmStep>, val note: String)
data class CalmHistoryRow(val title: String, val at: String)
data class WorkoutBlockK(val name: String, val seconds: Int, val cue: String)
data class WorkoutPlanK(val level: String, val focus: String,
                        val blocks: List<WorkoutBlockK>)
data class MealDayK(val dayNumber: Int, val meals: List<String>)
data class MealPlanK(val why: String, val kcal: Int,
                     val days: List<MealDayK>, val disclaimer: String)
data class ActivityWatchK(val proactive: Boolean, val watching: Boolean,
                          val intervention: Guidance?)
data class InsightRowK(val id: String, val message: String)
data class ReportK(val checkinCount: Int, val avgMood: Double)

data class SpecialistRowK(val condition: String, val mode: String,
                          val label: String)
data class CatalogStarterK(val profileId: String?, val displayName: String?)

/** One QRME profile the attach bracket found, beyond the curated shelf.
 *
 *  `attachable` and `standing` are two fields rather than one: an
 *  age-restricted profile *is* attachable and still carries a caveat
 *  somebody needs to read, so collapsing them would either hide the caveat
 *  or refuse a profile that works. */
data class SpecialistFoundK(val profileId: String, val displayName: String,
                            val purpose: String?, val attachable: Boolean,
                            val standing: String?)

data class SpecialistSearchK(val results: List<SpecialistFoundK>,
                             val capped: Boolean, val limit: Int)
data class ClinicianSearchK(val labels: List<String>, val reason: String?)
data class ReferralPreparedK(val prepared: Boolean, val reason: String?,
                             val note: String?)
data class ReferralRequestRowK(val id: String, val condition: String)
data class TaskStartedK(val started: Boolean, val reason: String?,
                        val id: String?)
data class SpecialistTaskRowK(val id: String, val goal: String,
                              val status: String)
data class SpecialistTaskViewK(val status: String, val nextPhase: String?,
                               val note: String?)
data class ProviderSummaryK(val displayName: String, val conditions: List<String>,
                            val escalations: Int)

data class AccessLogK(val vaulted: Boolean, val recordKept: Boolean,
                      val entries: List<String>, val note: String)

/** `GET /audit/{uid}` — what was *done*, beside the access log's record of
 *  what was *read*.
 *
 *  `intact` and `brokenAtSeq` are carried rather than dropped: a list of
 *  entries nobody can check is a list, and the chain's state is the half that
 *  makes the other half a record. `watched` is the catalogue, so an empty
 *  `entries` reads as "nothing happened" and not as "nothing is watched". */
data class AuditLogK(val entries: List<String>, val count: Int,
                     val intact: Boolean, val brokenAtSeq: Int?,
                     val watched: List<String>, val retention: String)
data class CloudStatusK(val cloud: Boolean, val model: String?,
                        val fallback: String, val contribution: String)
data class ContributionK(val optedIn: Boolean, val policy: String)
data class PageRowK(val to: String, val delivered: Boolean, val sentAt: String)
data class PlanRowK(val plan: String, val title: String, val priceUsd: Int)

data class BudgetRowK(val category: String, val monthlyLimit: Double,
                      val spent: Double, val standing: String)
data class MembershipK(val plan: String, val title: String,
                       val priceUsd: Double, val means: String,
                       val whoCanRead: List<String>)

data class BeaconRowK(val id: String, val label: String, val scans: Int,
                      val active: Boolean)
data class BeaconCardK(val beacon: String, val firstName: String,
                       val note: String, val badge: String)
data class BeaconAlarmK(val badge: String, val note: String)
data class RelayChannelK(val configured: Boolean, val envelope: String,
                         val note: String)
data class RelayRosterK(val roster: List<String>, val ceiling: String,
                        val note: String)
data class RelayRotaK(val timezone: String, val onNow: List<String>,
                      val anybodyOnShift: Boolean, val note: String)
data class BeaconPageK(val html: String, val url: String)

data class ExcursionRowK(val id: String, val topic: String, val redactions: Int,
                         val leftHost: Boolean, val findings: String?,
                         val learned: Boolean)
data class ExcursionLearnedK(val learned: Boolean, val alreadyLearned: Boolean,
                             val note: String?)
data class CommunityVisitRowK(val roomId: String, val at: String)
data class CommunityFeedItemK(val kind: String?, val title: String?,
                              val topic: String?)
data class CommunityFeedViewK(val note: String, val openInQrme: String?,
                              val items: List<CommunityFeedItemK>)

data class TranscribedK(val text: String)
data class HealthK(val status: String, val tandem: Boolean)
