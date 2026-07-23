package app.jim.guardian

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

// MARK: wire models

data class EnrollResult(val id: String, val displayName: String, val userToken: String)
data class Guidance(val delivered: Boolean, val source: String?, val content: String)
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
data class RobotSpec(val model: String, val label: String, val maker: String)
data class Robot(val id: String, val model: String, val name: String, val status: String?, val directive: String?)
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
        return Guidance(o.optBoolean("delivered"), o.optString("source", null), o.optString("content", ""))
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

    suspend fun enroll(name: String, birthdate: String): EnrollResult {
        val o = request("/enroll", "POST", JSONObject()
            .put("display_name", name).put("birthdate", birthdate).put("terms_consent", true))
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

    suspend fun coach(uid: String, token: String, area: String, message: String): Guidance {
        val o = request("/coach/$uid", "POST",
            JSONObject().put("area", area).put("message", message), token)
        return Guidance(o.optBoolean("delivered"), o.optString("source", null), o.optString("content", ""))
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

    private fun robotOf(o: JSONObject) = Robot(
        o.getString("id"), o.optString("model", ""), o.optString("name", ""),
        o.optString("status", null), o.optString("escalation_directive", null))

    suspend fun roboticsCatalog(): List<RobotSpec> {
        val arr = request("/robotics/catalog").getJSONArray("robots")
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            RobotSpec(o.getString("model"), o.getString("label"), o.getString("maker"))
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
