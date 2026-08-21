package app.jim.wear

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch

/**
 * What the watch knows about itself between launches.
 *
 * The phone shell enrolls: name, birthdate, a whole welcome flow. This one
 * deliberately cannot. A watch keyboard is four millimetres of glass, and
 * asking somebody to type a birthdate on it is asking them to give up —
 * so the wrist is *paired*, not enrolled. The identity comes from a phone
 * or the console, and this holds it.
 *
 *     asked     how does the watch sign in
 *     mattered  nobody types on a watch
 *
 * `paired` is the honest third field: the identity can be here and the
 * watch still not be registered as a device, attached as channel 2, or
 * switched on as the wrist monitor — three separate doors, each of which
 * `jim/mic.py` and `jim/monitors.py` refuse without. [pairUp] walks all
 * three, and only sets this once every one of them answered.
 */
class WatchState(app: Application) : AndroidViewModel(app) {
    private val prefs = app.getSharedPreferences("jim-wear", 0)

    var base by mutableStateOf(prefs.getString("base", "") ?: "")
        private set
    var uid by mutableStateOf(prefs.getString("uid", "") ?: "")
        private set
    var token by mutableStateOf(prefs.getString("token", "") ?: "")
        private set

    /** Whether the three pairing doors have been walked on this deployment. */
    var paired by mutableStateOf(prefs.getBoolean("paired", false))
        private set

    /** The roster's word for the wrist row: off, waiting or sensing. */
    var wrist by mutableStateOf("off")
        private set

    /** Channel 2's word: unattached, silent or carrying. */
    var channelTwo by mutableStateOf("unattached")
        private set

    /** The last thing the Guardian refused, in her own sentence. Held rather
     *  than toasted: a watch face is glanced at, and a message that vanishes
     *  in two seconds is a message nobody read. */
    var trouble by mutableStateOf("")

    val signedIn get() = uid.isNotEmpty() && token.isNotEmpty() &&
            base.isNotEmpty()

    init { WearApi.base = base }

    /**
     * Sign in, with the deployment and the same email and password as every
     * other surface.
     *
     * Three fields on a 45mm screen is three too many, and this is still the
     * right first version: Wear's own input screen takes dictation, so the
     * deployment and the email are spoken rather than typed, and it works on
     * every watch — no camera, no companion app, no new door on the server.
     * A short pairing code handed over from the phone would be better; that
     * is a round, not a line, and shipping the awkward thing that works
     * beats shipping the elegant thing that does not exist.
     */
    fun signInWith(deployment: String, email: String, password: String,
                   onDone: (Boolean) -> Unit = {}) {
        base = deployment.trim().trimEnd('/')
        WearApi.base = base
        viewModelScope.launch {
            trouble = ""
            runCatching { WearApi.signIn(email.trim(), password) }
                .onSuccess { who ->
                    uid = who.uid
                    token = who.token
                    prefs.edit().putString("base", base)
                        .putString("uid", uid).putString("token", token)
                        .putBoolean("paired", false).apply()
                    paired = false
                    onDone(true)
                }
                .onFailure {
                    trouble = it.message ?: "the watch could not sign in"
                    onDone(false)
                }
        }
    }

    fun signOut() {
        base = ""; uid = ""; token = ""; paired = false
        wrist = "off"; channelTwo = "unattached"
        WearApi.base = ""
        prefs.edit().clear().apply()
    }

    /**
     * Walk the three doors, in the order the server requires them.
     *
     * Register first, because `mic.attach` refuses a microphone on a device
     * that is not on the account. Attach second. Switch the wrist monitor on
     * last — and separately, because it is a different consent about a
     * different thing: one says the Guardian may borrow this microphone
     * while your phone is busy, the other says it may read your pulse.
     *
     * Failing part-way is reported and not retried in a loop. A watch that
     * silently re-tries a refusal is a watch that hides the sentence
     * explaining why it will never work.
     */
    fun pairUp(onDone: (Boolean) -> Unit = {}) {
        viewModelScope.launch {
            trouble = ""
            val ok = runCatching {
                WearApi.register(uid, token)
                WearApi.attachMic(uid, token)
                WearApi.plugIn(uid, token, "wrist")
            }.onFailure { trouble = it.message ?: "the watch could not pair" }
                .isSuccess
            if (ok) {
                paired = true
                prefs.edit().putBoolean("paired", true).apply()
                refresh()
            }
            onDone(ok)
        }
    }

    /** What is actually true right now, from the two doors that say so. */
    fun refresh() {
        if (!signedIn) return
        viewModelScope.launch {
            runCatching { WearApi.monitors(uid, token) }
                .onSuccess { roster ->
                    wrist = roster.firstOrNull { it.name == "wrist" }
                        ?.standing ?: "off"
                }
            runCatching { WearApi.micState(uid, token) }
                .onSuccess { channelTwo = it.standing }
        }
    }

    /** Run one call, keep the Guardian's sentence if she refuses. */
    fun <T> call(block: suspend () -> T, onResult: (Result<T>) -> Unit = {}) {
        viewModelScope.launch {
            val r = runCatching { block() }
            r.exceptionOrNull()?.let { trouble = it.message ?: "no answer" }
            onResult(r)
        }
    }
}
