package app.jim.guardian

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
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
                    val custody: Custody? = null)
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
data class RobotSpec(val model: String, val label: String, val maker: String,
                     val firstAid: String?)
data class Robot(val id: String, val model: String, val name: String, val status: String?,
                 val directive: String?, val firstAid: String?, val commands: List<String>)
data class RobotCmdResult(val status: String, val note: String?, val instruction: String?,
                          val spoken: List<String>, val sequence: List<String>,
                          val pacePerMinute: Int?)
data class WaiverState(val signed: Boolean, val signature: String?, val terms: List<String>)
data class MedicalCardIssued(val token: String, val qrSvgUrl: String)
data class SourceRow(val source: String, val consented: Boolean)
data class SocialConn(val id: String, val platform: String, val direction: String, val handle: String?)
data class CatalogApp(val provider: String, val app: String, val label: String)
data class AppConn(val id: String, val provider: String, val app: String)
data class MedicalCard(val name: String?, val age: Int?, val conditions: List<String>,
                       val restingHr: Int?, val contactName: String?, val contactPhone: String?)

class ApiException(message: String) : Exception(message)

/**
 * Coroutine client for the JIM Guardian backend.
 *
 * The Android emulator reaches the host machine at 10.0.2.2, so that is the
 * default. On a physical device, set your machine's LAN IP via [base].
 */
object ApiClient {
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
            })
    }

    private suspend fun request(
        path: String, method: String = "GET",
        body: JSONObject? = null, token: String? = null,
    ): JSONObject = withContext(Dispatchers.IO) {
        val conn = (URL(base + path).openConnection() as HttpURLConnection).apply {
            requestMethod = method
            setRequestProperty("content-type", "application/json")
            token?.let { setRequestProperty("authorization", "Bearer $it") }
            connectTimeout = 8000; readTimeout = 8000
            if (body != null) {
                doOutput = true
                outputStream.use { it.write(body.toString().toByteArray()) }
            }
        }
        val code = conn.responseCode
        val text = (if (code in 200..299) conn.inputStream else conn.errorStream)
            ?.bufferedReader()?.use { it.readText() } ?: ""
        conn.disconnect()
        if (code !in 200..299) {
            val detail = runCatching { JSONObject(text).optString("detail") }.getOrNull()
            throw ApiException(if (detail.isNullOrBlank()) "HTTP $code" else detail)
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

    private suspend fun getArray(path: String, token: String): org.json.JSONArray = withContext(Dispatchers.IO) {
        val conn = (URL("$base$path").openConnection() as HttpURLConnection).apply {
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
        val spoken = o.optJSONArray("spoken")
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
}
