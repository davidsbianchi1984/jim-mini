package app.jim.guardian

import android.content.Context
import android.content.SharedPreferences
import org.json.JSONArray
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

/**
 * What went wrong, recorded without recording anything private.
 *
 * The console's `app/src/errors.ts` in this repository, in Kotlin. Same rules,
 * same refusals — written from that file rather than invented again, so the
 * two cannot drift into disagreeing about what a failure may say about itself.
 *
 * Every failed request passes through one place in [ApiClient], so one call
 * there catches the lot. The hard part is not the catching. The backends put
 * user input straight into their error messages — *no device called 'Pixel
 * Buds' on this account*, *unknown site 'knee'* — which are good messages for
 * the person reading them and device names and body sites to anybody else. The
 * message is shown and never written down.
 *
 * The path goes the same way: `/profiles/prf_0de08e794ed0/chat` identifies a
 * person, `POST /profiles/{id}/chat` identifies a bug, and only the second is
 * kept. Redaction happens on the way *in*, so the stored buffer never holds
 * something that would later have to be scrubbed.
 */
object Problems {
    /**
     * The application context, attached once at startup.
     *
     * `ApiClient` is an object with no context of its own, and threading one
     * through every call site would put an Android type into the signature of
     * a function whose whole job is to be identical in three languages. So the
     * recorder holds it, `record` takes the same three arguments it takes on
     * iOS and Windows, and a shell that forgot to attach records nothing
     * rather than crashing — the diagnostic must never be the reason
     * something else fails.
     */
    @Volatile private var appContext: Context? = null

    fun attach(context: Context) { appContext = context.applicationContext }

    private const val PREFS = "app.problems"
    private const val KEY = "rows"
    private const val LIMIT = 50

    /**
     * A segment that identifies a *thing* rather than naming a route.
     *
     * Deliberately wide: over-redacting costs a little precision in a bug
     * report, under-redacting costs somebody their privacy, and only one of
     * those is recoverable. The suffix length is unbounded because an id
     * minted short is still an id — requiring six hex characters let
     * `cap_9f2`, `req_77aa` and `usr_1` through when the console's version of
     * this was first written.
     */
    private val idLike = listOf(
        Regex("^[a-z]{2,8}_[0-9a-z]+$", RegexOption.IGNORE_CASE),
        Regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
              RegexOption.IGNORE_CASE),
        Regex("^[0-9]+$"),
        Regex("^[A-Za-z0-9_-]{24,}$"),
    )

    /** A path with every identifying segment replaced by `{id}`. */
    fun redact(path: String): String =
        path.substringBefore('?')
            .split('/')
            .joinToString("/") { seg ->
                if (seg.isNotEmpty() && idLike.any { it.matches(seg) }) "{id}" else seg
            }

    /**
     * Non-reversible by construction — its input already carries nothing
     * private. FNV-1a, matching the console so the same failure fingerprints
     * the same on a phone and on a desktop.
     */
    private fun fingerprint(op: String, status: Int): String {
        var h = 2166136261u
        for (b in "$op|$status".toByteArray()) {
            h = h xor (b.toInt() and 0xff).toUInt()
            h *= 16777619u
        }
        return h.toString(16).padStart(8, '0')
    }

    private fun prefs(): SharedPreferences? =
        appContext?.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    private fun read(): MutableList<JSONObject> {
        val raw = prefs()?.getString(KEY, null) ?: return mutableListOf()
        return try {
            val arr = JSONArray(raw)
            (0 until arr.length()).map { arr.getJSONObject(it) }.toMutableList()
        } catch (_: Exception) {
            mutableListOf()
        }
    }

    private fun write(rows: List<JSONObject>) {
        // A full or unavailable store is not worth an error of its own. The
        // diagnostic is the least important thing in the app; it must never be
        // the reason something else fails.
        try {
            val arr = JSONArray()
            rows.take(LIMIT).forEach { arr.put(it) }
            prefs()?.edit()?.putString(KEY, arr.toString())?.apply()
        } catch (_: Exception) {
        }
    }

    /**
     * Record a failure. Takes the method and raw path, never the message.
     *
     * The signature is the safeguard: there is no parameter a detail string
     * could arrive through, so a future caller cannot pass one in a hurry.
     */
    fun record(method: String, path: String, status: Int) {
        val op = "${method.uppercase()} ${redact(path)}"
        val print = fingerprint(op, status)
        val fmt = SimpleDateFormat("yyyy-MM-dd", Locale.US)
        fmt.timeZone = TimeZone.getTimeZone("UTC")
        val day = fmt.format(Date())

        val rows = read()
        val i = rows.indexOfFirst { it.optString("fingerprint") == print }
        if (i >= 0) {
            val hit = rows.removeAt(i)
            hit.put("count", hit.optInt("count") + 1).put("day", day)
            rows.add(0, hit)
        } else {
            rows.add(0, JSONObject()
                .put("op", op).put("status", status).put("count", 1)
                .put("day", day).put("fingerprint", print).put("sent", 0))
        }
        write(rows)
    }

    /** The whole local history, which is the person's own. */
    fun all(): List<JSONObject> = read()

    fun clear() { prefs()?.edit()?.remove(KEY)?.apply() }

    // ---- Reporting ------------------------------------------------------
    //
    // Everything above this existed for four releases and did half a job.
    // `record` redacts on the way in, and `sent` was documented as "how much
    // of `count` has already been reported" — describing a send that was
    // never written. The buffer filled, capped at fifty, and rolled over.
    // Nothing ever read `sent`, because nothing ever reported.
    //
    //     asked     is the failure recorded without recording anything private
    //     mattered  does the failure reach anybody
    //
    // The console's `app/src/errors.ts` had both halves the whole time.

    /**
     * Which product this is.
     *
     * Not defaulted: `"unknown"` is a source the gateway refuses, so a shell
     * that forgot to set it finds out on the first report rather than filing
     * one app's bugs under another app's name.
     */
    const val SOURCE = "jim-mini"

    private const val COLLECTOR_KEY = "app.problems.collector"
    private const val SEND_KEY = "app.problems.send"
    private const val NOTICE_KEY = "app.problems.notice"

    /** Stamped by gradle at build time — see `buildConfigField` in build.gradle.kts. */
    private val builtCollector: String get() = BuildConfig.PROBLEM_COLLECTOR
    private val builtToken: String get() = BuildConfig.PROBLEM_TOKEN

    /**
     * Where reports go, or "" for nowhere.
     *
     * The built-in address comes from `BuildConfig`, stamped at build time the
     * way the console's vite `define` stamps its bundle. Absent means an
     * install with nowhere to send — a stronger default than a flag, because
     * there is no address for a later mistake to switch on. A stored value
     * wins, so a self-hoster can point at their own gateway and anyone can
     * point at nothing by storing an empty string.
     */
    fun collectorUrl(): String {
        val stored = prefs()?.getString(COLLECTOR_KEY, null)
        return (stored ?: builtCollector).trim().trimEnd('/')
    }

    fun setCollectorUrl(url: String?) {
        val editor = prefs()?.edit() ?: return
        if (url == null) editor.remove(COLLECTOR_KEY)
        else editor.putString(COLLECTOR_KEY, url)
        editor.apply()
    }

    /** On where a collector exists, off the moment anyone says so. */
    fun sendingEnabled(): Boolean =
        prefs()?.getString(SEND_KEY, null) != "off"

    fun setSending(on: Boolean) {
        prefs()?.edit()?.putString(SEND_KEY, if (on) "on" else "off")?.apply()
    }

    /**
     * Nothing leaves this device before somebody has been told and answered.
     * The gate is the notice, not the switch: a switch that defaults to on is
     * a decision made on the person's behalf.
     */
    fun noticeAnswered(): Boolean = prefs()?.getString(NOTICE_KEY, null) != null

    fun answerNotice(send: Boolean) {
        prefs()?.edit()?.putString(NOTICE_KEY, if (send) "yes" else "no")?.apply()
        setSending(send)
    }

    /**
     * Exactly what a report contains — shown on screen and posted, both from
     * here, so a preview cannot drift from the payload.
     *
     * `count` is the *unreported remainder*, and rows with nothing left owing
     * are absent. This is not a view of the log; it is the message, and after
     * a successful send it is legitimately empty.
     */
    fun report(appVersion: String = BuildConfig.VERSION_NAME): JSONObject {
        val owed = JSONArray()
        for (row in read()) {
            val remainder = row.optInt("count") - row.optInt("sent")
            if (remainder <= 0) continue
            owed.put(JSONObject()
                .put("op", row.optString("op"))
                .put("status", row.optInt("status"))
                .put("count", remainder)
                .put("day", row.optString("day"))
                .put("fingerprint", row.optString("fingerprint")))
        }
        return JSONObject()
            .put("source", SOURCE)
            .put("app_version", appVersion)
            .put("platform", "android")
            .put("language", Locale.getDefault().language.ifEmpty { "en" })
            .put("problems", owed)
    }

    /**
     * Advance each row's watermark by what was actually reported — by amount,
     * never by flag. A row goes on counting while the request is in flight and
     * that growth is still owed; a flag would drop it silently.
     */
    fun markReported(report: JSONObject) {
        val sent = report.optJSONArray("problems") ?: return
        val owed = HashMap<String, Int>()
        for (i in 0 until sent.length()) {
            val row = sent.optJSONObject(i) ?: continue
            owed[row.optString("fingerprint")] = row.optInt("count")
        }
        val rows = read()
        for (row in rows) {
            val n = owed[row.optString("fingerprint")] ?: continue
            row.put("sent", row.optInt("sent") + n)
        }
        write(rows)
    }

    enum class SendOutcome {
        SENT, NOTHING_TO_SEND, TURNED_OFF, NO_COLLECTOR, AWAITING_NOTICE, FAILED
    }

    /**
     * Post what is owed. Never throws, never blocks anything.
     *
     * The gateway answers 422 when a report is not the shape it expects, which
     * would mean this build's redaction has stopped working. That is a refusal
     * and not a retry: the watermark stays put, nothing is marked sent, and the
     * next launch tries again with whatever the fix ships.
     *
     * Its own connection rather than [ApiClient]'s: `ApiClient` records a
     * problem on every failure, so a failing collector would write a new row
     * each launch — a log that fills with the story of its own delivery.
     *
     * Blocking, and must be called off the main thread.
     */
    fun send(appVersion: String): SendOutcome {
        val base = collectorUrl()
        if (base.isEmpty()) return SendOutcome.NO_COLLECTOR
        if (!noticeAnswered()) return SendOutcome.AWAITING_NOTICE
        if (!sendingEnabled()) return SendOutcome.TURNED_OFF
        val payload = report(appVersion)
        if ((payload.optJSONArray("problems")?.length() ?: 0) == 0) {
            return SendOutcome.NOTHING_TO_SEND
        }
        try {
            val conn = java.net.URL("$base/v1/problems").openConnection()
                    as java.net.HttpURLConnection
            conn.requestMethod = "POST"
            conn.connectTimeout = 10_000
            conn.readTimeout = 10_000
            conn.setRequestProperty("content-type", "application/json")
            if (builtToken.isNotEmpty()) {
                conn.setRequestProperty("Authorization", "Bearer $builtToken")
            }
            conn.doOutput = true
            conn.outputStream.use { it.write(payload.toString().toByteArray()) }
            val code = conn.responseCode
            conn.disconnect()
            if (code !in 200..299) return SendOutcome.FAILED
        } catch (_: Exception) {
            return SendOutcome.FAILED
        }
        markReported(payload)
        return SendOutcome.SENT
    }
}
