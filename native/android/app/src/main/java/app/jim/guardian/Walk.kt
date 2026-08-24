package app.jim.guardian

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.Locale

/**
 * The conversation that keeps going when the app is not on screen.
 *
 * The console's walk-along strip carries a conversation across a tab change
 * and stops dead when the browser puts the page away. That is not a
 * shortcoming of the strip: a backgrounded web page has its recogniser ended
 * by the browser, and no amount of state above a tab switch changes it. The
 * console says so on screen rather than pretending otherwise.
 *
 *     asked     can the conversation survive a screen change
 *     mattered  can it survive leaving the application
 *
 * On a phone the answer can be yes, and this is the price of it: a foreground
 * service, declared as a microphone service, holding a notification that
 * cannot be swiped away and carries a Stop. That notification is not a
 * platform tax to be minimised — it is the only thing standing between "the
 * conversation you took with you" and "an app recording you after you left
 * it", and the two are the same code with different honesty.
 *
 * ## The area travels
 *
 * The coach card is the one place that offers the area picker, and a walk
 * started from *mental health* that quietly reverted to the front door's
 * `general` would be a different conversation wearing the same name. The
 * console answers this by closing over the area the screen had; a Service
 * cannot be handed a closure across a start intent, so the area rides as an
 * extra and the service asks with it.
 *
 *     asked     can the conversation be carried
 *     mattered  is it the same conversation afterwards
 *
 * ## What this is not
 *
 * It is not always-on listening. Nothing here starts without a press, the
 * notification says the microphone is open for as long as it is, and the
 * first control on that notification ends it. The standing ear that watches
 * for cue words is a different feature with its own consent, and this does
 * not borrow from it.
 *
 * ## Written without a compiler
 *
 * There is no Android toolchain in the environment this was written in, so
 * the guard beside it reads the declarations rather than the behaviour: the
 * manifest's permissions and service type, the foreground start, the
 * notification and its stop action. Those are the parts whose absence is a
 * microphone with no indicator. The conversation loop itself is checked by a
 * person with a phone, and until somebody has done that, this is code that
 * has been reasoned about and not run.
 */
object Walking {

    /** Whether a walk is in progress, for the screen that offers the button.
     *  Compose state rather than a flag, so the button can say Stop. */
    var underway by mutableStateOf(false)
        internal set

    /** The last thing heard and the last thing said, so a person who comes
     *  back to the app can see where the conversation got to. */
    var heard by mutableStateOf("")
        internal set
    var said by mutableStateOf("")
        internal set

    /** Why it stopped, when it stopped for a reason. Empty when it was
     *  ended on purpose — a person who pressed Stop does not need to be told
     *  what happened. */
    var trouble by mutableStateOf("")
        internal set

    /** Bumped every time a walk begins, so the shell can land the person on
     *  the front page. The point of taking a conversation with you is going
     *  somewhere, and the screen you were on is the one place you have
     *  finished with — leaving somebody on the coach card with the strip
     *  lit means the first thing they do is find their way out of it.
     *
     *  A counter rather than a flag: a second walk started from the front
     *  page must still land there, and a boolean that was already true
     *  would say nothing happened. */
    var landings by mutableStateOf(0)
        internal set

    /** True when the last turn was answered by the offline stack rather than
     *  by a model. Not a failure — a deployment with no model key still
     *  coaches, from stored knowledge — but not the model somebody picked
     *  either, and out here there is no screen to notice it on. */
    var offline by mutableStateOf(false)
        internal set

    fun start(context: Context, uid: String, token: String, area: String,
              lang: String) {
        val intent = Intent(context, WalkService::class.java)
            .putExtra(WalkService.EXTRA_UID, uid)
            .putExtra(WalkService.EXTRA_TOKEN, token)
            .putExtra(WalkService.EXTRA_AREA, area)
            .putExtra(WalkService.EXTRA_LANG, lang)
        // `startForegroundService` rather than `startService`: the service
        // has one window to call `startForeground` and the system kills it if
        // it does not, which is the platform enforcing the same rule this
        // file is about.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(intent)
        } else {
            context.startService(intent)
        }
    }

    fun stop(context: Context) {
        context.startService(
            Intent(context, WalkService::class.java)
                .setAction(WalkService.ACTION_STOP))
    }
}

class WalkService : Service() {

    companion object {
        const val EXTRA_UID = "uid"
        const val EXTRA_TOKEN = "token"
        /** The coaching area the walk was started in. `general` is the front
         *  door's own area — making somebody pick a category before they can
         *  speak is the menu problem the front door exists to answer — and
         *  it is a fallback here, never a silent replacement for a picked
         *  one. */
        const val EXTRA_AREA = "area"
        const val EXTRA_LANG = "lang"
        const val ACTION_STOP = "app.jim.guardian.WALK_STOP"
        private const val CHANNEL = "walk"
        private const val NOTE_ID = 4201
    }

    private val main = Handler(Looper.getMainLooper())
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var recogniser: SpeechRecognizer? = null
    private var speaker: TextToSpeech? = null
    private var uid: String = ""
    private var token: String = ""
    private var area: String = "general"
    private var lang: String = "en"
    /** Every opening of the ear carries a number, and a late callback from a
     *  superseded one is ignored. The console learned this the hard way: one
     *  shared flag meant a stale `onError` closed the ear that had replaced
     *  it, and the microphone died a fifth of a second after it opened. */
    private var turn = 0
    private var wants = false

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            close(reason = "")
            return START_NOT_STICKY
        }
        uid = intent?.getStringExtra(EXTRA_UID).orEmpty()
        token = intent?.getStringExtra(EXTRA_TOKEN).orEmpty()
        area = intent?.getStringExtra(EXTRA_AREA)?.ifBlank { null } ?: "general"
        lang = intent?.getStringExtra(EXTRA_LANG) ?: "en"
        if (uid.isEmpty() || token.isEmpty()) {
            stopSelf()
            return START_NOT_STICKY
        }
        goForeground()
        Walking.underway = true
        Walking.trouble = ""
        Walking.landings += 1
        speaker = TextToSpeech(this) { }.also {
            it.language = Locale.forLanguageTag(lang)
        }
        wants = true
        main.post { hear() }
        // NOT sticky. A service the system restarts after killing it is a
        // microphone that reopens without anybody pressing anything, which
        // is the one thing this must never be.
        return START_NOT_STICKY
    }

    override fun onDestroy() {
        close(reason = "")
        scope.cancel()
        super.onDestroy()
    }

    // -- the notification ----------------------------------------------------

    private fun goForeground() {
        val manager = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            manager.createNotificationChannel(
                NotificationChannel(CHANNEL,
                    L10n.t("walk.note.channel", lang),
                    // Low, not minimum: it must be visible in the shade for
                    // as long as the microphone is open, and it must not
                    // make a sound every time a turn ends.
                    NotificationManager.IMPORTANCE_LOW))
        }
        val stop = PendingIntent.getService(
            this, 0,
            Intent(this, WalkService::class.java).setAction(ACTION_STOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
        val note: Notification = Notification.Builder(this, CHANNEL)
            .setContentTitle(L10n.t("walk.note.title", lang))
            .setContentText(
                if (Walking.offline)
                    L10n.t("walk.note.body", lang) + " "
                        + L10n.t("walk.offline", lang)
                else L10n.t("walk.note.body", lang))
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setOngoing(true)
            .addAction(Notification.Action.Builder(
                null, L10n.t("walk.end", lang), stop).build())
            .build()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(NOTE_ID, note,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
        } else {
            startForeground(NOTE_ID, note)
        }
    }

    // -- one turn ------------------------------------------------------------

    private fun hear() {
        if (!wants) return
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            close(reason = L10n.t("walk.trouble.norecogniser", lang))
            return
        }
        val mine = ++turn
        fun live() = mine == turn && wants
        val rec = SpeechRecognizer.createSpeechRecognizer(this)
        recogniser = rec
        rec.setRecognitionListener(object : RecognitionListener {
            override fun onResults(results: android.os.Bundle?) {
                if (!live()) return
                val text = results
                    ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    ?.firstOrNull()
                    .orEmpty()
                    .trim()
                if (text.isEmpty()) { main.post { hear() }; return }
                Walking.heard = text
                take(mine, text)
            }

            override fun onError(code: Int) {
                if (!live()) return
                // Quiet is not a failure in a standing conversation — the
                // microphone simply opens again, the same rule the console
                // holds. Everything else stops and says which failure it was,
                // because a refused microphone reported as quiet is a loop
                // that reopens forever with nothing to hear.
                when (code) {
                    SpeechRecognizer.ERROR_NO_MATCH,
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT ->
                        main.post { hear() }
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS ->
                        close(reason = L10n.t("walk.trouble.permission", lang))
                    SpeechRecognizer.ERROR_NETWORK,
                    SpeechRecognizer.ERROR_NETWORK_TIMEOUT ->
                        close(reason = L10n.t("walk.trouble.network", lang))
                    else ->
                        close(reason = L10n.t("walk.trouble.stopped", lang))
                }
            }

            override fun onReadyForSpeech(params: android.os.Bundle?) {}
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rms: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onPartialResults(partial: android.os.Bundle?) {}
            override fun onEvent(type: Int, params: android.os.Bundle?) {}
        })
        rec.startListening(
            Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                          RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang))
    }

    private fun take(mine: Int, message: String) {
        scope.launch {
            val reply = runCatching {
                ApiClient.coach(uid, token, area, message)
            }.getOrNull()
            if (mine != turn || !wants) return@launch
            val text = reply?.content.orEmpty()
            // Who answered — `generated_by` is who actually did, not who was
            // picked, which is the whole reason the field exists.
            val fromStore = reply?.provenance?.generatedBy == "stub"
            withContext(Dispatchers.Main) {
                if (mine != turn || !wants) return@withContext
                if (text.isEmpty()) {
                    Walking.said = L10n.t("walk.lost", lang)
                } else {
                    Walking.said = text
                    speaker?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "walk")
                }
                // The notification is the only surface a person walking
                // about has, so it is where this has to be said. Rewritten
                // rather than re-posted from scratch: the same id keeps one
                // notification rather than stacking a new one per turn.
                if (fromStore != Walking.offline) {
                    Walking.offline = fromStore
                    goForeground()
                }
                // The next turn opens after the answer is handed to the
                // speaker rather than after it finishes: a person may
                // interrupt, and a conversation where interrupting is
                // impossible is a broadcast.
                hear()
            }
        }
    }

    private fun close(reason: String) {
        wants = false
        turn += 1
        recogniser?.destroy()
        recogniser = null
        speaker?.stop()
        speaker?.shutdown()
        speaker = null
        Walking.underway = false
        Walking.offline = false
        Walking.trouble = reason
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }
}
