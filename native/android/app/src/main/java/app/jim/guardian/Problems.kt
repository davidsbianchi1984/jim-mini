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
}
