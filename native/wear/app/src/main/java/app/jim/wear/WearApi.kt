package app.jim.wear

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.net.HttpURLConnection
import java.net.URL

/**
 * The wrist's doors — and only the wrist's.
 *
 * The phone shells are full clients and are held to it: a guard walks every
 * route the server publishes and asks whether each phone can reach it. This
 * is not that, and should not pretend to be. A watch is a surface with about
 * four things on it, and a wrist that could reach the billing screen would
 * be a worse product, not a more complete one.
 *
 *     asked     can the watch reach the Guardian
 *     mattered  the handful of things somebody would want at their wrist
 *
 * What is here falls into three groups, and only the third is what the
 * watch does minute to minute:
 *
 *  * **pairing**, once — [register] the watch as a device, [attachMic] it as
 *    channel 2, [plugIn] the wrist monitor. Every one of those is a door
 *    `jim/mic.py` and `jim/monitors.py` already refuse without, and the
 *    watch is the first surface that has ever had to walk the whole chain
 *    for itself;
 *  * **standing**, so a face can say what is actually true rather than what
 *    is switched on — [monitors] carries the roster's `standing`, [micState]
 *    carries channel 2's;
 *  * **the four things**, [pulse] and [heard] and [checkIn] and [emergency].
 *
 * Requests are plain `HttpURLConnection` on `Dispatchers.IO`, which is what
 * the phone shell uses too — a watch is not the place to introduce a second
 * HTTP stack for the sake of elegance.
 */
object WearApi {

    /** The deployment this watch talks to. Set once, on the pairing screen. */
    @Volatile
    var base: String = ""

    /** How this watch names itself everywhere the server asks. One name, so
     *  the device row, the channel-2 lease and the delivery all agree —
     *  `mic.heard` refuses a delivery under a name the channel was not lent
     *  to, and that refusal is only useful if the watch is consistent. */
    const val DEVICE_NAME = "smart_watch"

    class Refused(val code: Int, val sentence: String) : Exception(sentence)

    private suspend fun call(
        path: String,
        method: String = "GET",
        body: JSONObject? = null,
        token: String? = null,
    ): String = withContext(Dispatchers.IO) {
        val conn = (URL(base.trimEnd('/') + path).openConnection()
                as HttpURLConnection)
        conn.requestMethod = method
        conn.connectTimeout = 15_000
        conn.readTimeout = 30_000
        token?.let { conn.setRequestProperty("authorization", "Bearer $it") }
        if (body != null) {
            conn.doOutput = true
            conn.setRequestProperty("content-type", "application/json")
            conn.outputStream.use { it.write(body.toString().toByteArray()) }
        }
        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val text = stream?.bufferedReader()?.use(BufferedReader::readText) ?: ""
        if (code !in 200..299) {
            // The server's own sentence, not a status line. Every refusal in
            // this product is written to be read by a person and translated
            // into their language; throwing away that sentence to show
            // "HTTP 403" on a watch would waste the one thing that makes a
            // refusal useful at arm's length.
            val said = runCatching {
                val o = JSONObject(text)
                o.optString("message").ifEmpty { o.optString("detail") }
            }.getOrNull().orEmpty()
            throw Refused(code, said.ifEmpty { "the Guardian said no ($code)" })
        }
        text
    }

    // -- getting in ---------------------------------------------------------

    /**
     * Sign in, with the same email and password as every other surface.
     *
     * Not a second kind of credential and deliberately not one: a watch that
     * minted its own way in would be a second thing to revoke, and the one
     * somebody forgets to revoke is the one on the wrist of a watch they
     * stopped wearing. `auth.issue` hands out a fresh token per session, so
     * signing the watch out does not sign the phone out.
     *
     * This is honest about being the awkward option. A short pairing code
     * handed over from a phone would be better and does not exist yet; what
     * makes this the right thing to ship first is that it works on every
     * watch, with no camera, no companion app, and no new door. Wear's own
     * input screen takes dictation, so the email is spoken rather than
     * typed.
     */
    suspend fun signIn(email: String, password: String): SignedIn {
        val o = JSONObject(call("/signin", "POST",
                                JSONObject().put("email", email)
                                    .put("password", password)))
        return SignedIn(
            uid = o.getString("user_id"),
            token = o.getString("user_token"),
            name = o.optString("display_name"),
        )
    }

    data class SignedIn(val uid: String, val token: String, val name: String)

    // -- pairing, once ------------------------------------------------------

    /**
     * Introduce the watch to the account.
     *
     * `mic.attach` refuses a microphone on a device that is not registered —
     * "no device called 'smart_watch' on this account" — so this is the
     * first call in the chain, not an optional nicety. `kind` is `wearable`
     * because the same function refuses anything registered as stationary:
     * a thing bolted to a room hears the room.
     */
    suspend fun register(uid: String, token: String): JSONObject =
        JSONObject(call("/devices/$uid", "POST",
                        JSONObject()
                            .put("name", DEVICE_NAME)
                            .put("kind", "wearable")
                            .put("transport", "bluetooth")
                            .put("paired", true),
                        token))

    /**
     * Nominate the watch's microphone as channel 2. Attaching is not
     * listening — see [handover].
     */
    suspend fun attachMic(uid: String, token: String): JSONObject =
        JSONObject(call("/users/$uid/mic", "PUT",
                        JSONObject()
                            .put("device_name", DEVICE_NAME)
                            .put("mic_type", "watch"),
                        token))

    /**
     * Lend it, for as long as the person is talking to the Guardian.
     *
     * `route` is how the occupying call is being heard and the server will
     * refuse `speaker` — on speaker the watch picks up whoever is on the
     * other end, and they are not a user here. The watch sends `earpiece`
     * because that is what it knows to be true of itself: the person is
     * talking at their own wrist. `primary_device` is the phone, which must
     * not be this watch — one microphone cannot be both channels.
     */
    suspend fun handover(uid: String, token: String,
                         primaryDevice: String = "phone"): JSONObject =
        JSONObject(call("/users/$uid/mic/handover", "POST",
                        JSONObject()
                            .put("reason", "dictation")
                            .put("route", "earpiece")
                            .put("others_present", false)
                            .put("primary_device", primaryDevice),
                        token))

    /** Take the microphone back. Called when the talk screen closes — a
     *  handover left open is a lease nobody ended. */
    suspend fun releaseMic(uid: String, token: String): JSONObject =
        JSONObject(call("/users/$uid/mic/release", "POST", JSONObject(), token))

    /** Switch a monitor on, by name, naming this watch as the device. */
    suspend fun plugIn(uid: String, token: String, name: String): List<Monitor> =
        parseMonitors(call("/monitors/$uid/$name", "PUT",
                           JSONObject().put("device_name", DEVICE_NAME), token))

    // -- standing -----------------------------------------------------------

    /** What may sense this person, and whether the wrist is among them. */
    suspend fun monitors(uid: String, token: String): List<Monitor> =
        parseMonitors(call("/monitors/$uid", token = token))

    private fun parseMonitors(text: String): List<Monitor> {
        val arr = JSONArray(text)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            Monitor(
                name = o.getString("name"),
                says = o.optString("says"),
                on = o.optBoolean("on"),
                // `standing` is the honest word the roster learned when a
                // field report caught every switched-on row calling itself
                // sensing: off, waiting, or sensing.
                standing = o.optString("standing", if (o.optBoolean("on"))
                    "waiting" else "off"),
            )
        }
    }

    data class Monitor(
        val name: String,
        val says: String,
        val on: Boolean,
        val standing: String,
    )

    /** Channel 2's own standing: unattached, silent, or carrying. */
    suspend fun micState(uid: String, token: String): MicState {
        val o = JSONObject(call("/users/$uid/mic", token = token))
        return MicState(
            attached = o.optString("attached").ifEmpty { null },
            listening = o.optBoolean("listening"),
            standing = o.optString("standing", "unattached"),
        )
    }

    data class MicState(
        val attached: String?,
        val listening: Boolean,
        val standing: String,
    )

    // -- the four things ----------------------------------------------------

    /**
     * One reading from the wrist, on its way to the ladder and the day.
     *
     * `monitor` is what makes the wrist row say `sensing` truthfully. The
     * switch is only a permission; this is the reading that arrived. Naming
     * the row does not gate the reading — a dangerous rate is escalated
     * whether or not the roster row is on. See jim/api.py:monitor.
     */
    suspend fun pulse(uid: String, token: String, bpm: Int): JSONObject =
        JSONObject(call("/monitor/$uid", "POST",
                        JSONObject()
                            .put("heart_rate", bpm)
                            .put("source_device", DEVICE_NAME)
                            .put("monitor", "wrist"),
                        token))

    /**
     * What the watch heard, handed to the channel it was lent.
     *
     * Words, not audio, and deliberately: the watch recognises the speech
     * itself, so nothing but text ever leaves the wrist, and it works on a
     * deployment with no transcription key at all. The server refuses this
     * unless the channel is attached and handed over, and unless the name
     * matches the one it was lent to — see jim/mic.py.
     */
    suspend fun heard(uid: String, token: String, words: String): JSONObject =
        JSONObject(call("/users/$uid/mic/heard", "POST",
                        JSONObject()
                            .put("device_name", DEVICE_NAME)
                            .put("words", words),
                        token))

    /** The Guardian's own question, answered on two dials. */
    suspend fun checkIn(uid: String, token: String,
                        mood: Int, energy: Int): JSONObject =
        JSONObject(call("/checkin/$uid", "POST",
                        JSONObject().put("mood", mood).put("energy", energy),
                        token))

    /** The coach reaching out first, in one or two sentences. The wrist is
     *  the surface this was always for: nobody opens an app to be asked how
     *  they are. */
    suspend fun companion(uid: String, token: String): String =
        JSONObject(call("/companion/$uid", "POST", JSONObject(), token))
            .optString("content")

    /** The one a watch is for at three in the morning. */
    suspend fun emergency(uid: String, token: String,
                          situation: String = ""): JSONObject =
        JSONObject(call("/emergency/$uid", "POST",
                        JSONObject().apply {
                            if (situation.isNotBlank()) put("situation", situation)
                        }, token))
}
