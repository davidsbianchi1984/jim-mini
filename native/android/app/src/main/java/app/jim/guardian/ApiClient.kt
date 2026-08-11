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
data class Finetune(val version: Int, val backend: String, val examples: Int,
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

    private suspend fun request(
        path: String, method: String = "GET",
        body: JSONObject? = null, token: String? = null,
    ): JSONObject = withContext(Dispatchers.IO) {
        val conn = (URL(base + path).openConnection() as HttpURLConnection).apply {
            requestMethod = method
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

    suspend fun coach(uid: String, token: String, area: String, message: String): Guidance {
        val o = request("/coach/$uid", "POST",
            JSONObject().put("area", area).put("message", message), token)
        return parseGuidance(o)!!
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

    private suspend fun getArray(path: String, token: String): org.json.JSONArray = withContext(Dispatchers.IO) {
        val conn = (URL("$base$path").openConnection() as HttpURLConnection).apply {
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
        o.optInt("version"), o.optString("backend"), o.optInt("examples"),
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
/** The mail configuration — never the password, only whether one is set. */
data class MailSettingsOut(val transport: String, val source: String,
                           val host: String?, val port: Int,
                           val username: String?, val sender: String?,
                           val publicUrl: String, val passwordSet: Boolean)
