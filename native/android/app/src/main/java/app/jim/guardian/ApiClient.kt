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
}
