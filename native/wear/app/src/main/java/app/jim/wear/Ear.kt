package app.jim.wear

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer

/**
 * Channel 2, at the wrist.
 *
 * `jim/mic.py` has said since it was written that capture happens on the
 * device and nothing in that module touches a sample. That was a true
 * description of a division and, for a long time, of a channel with no
 * device on the other end: it could be attached, handed over, gained and
 * audited, and nothing could hand anything in.
 *
 *     asked     may the agent listen on this device
 *     mattered  is there a device
 *
 * This is the device. It recognises the speech on the watch and sends
 * **words**, never audio — so nothing but text ever leaves the wrist, and
 * it works on a deployment with no transcription key at all. That is not a
 * shortcut around the server's ears; it is the better half of the choice
 * `mic.heard` offers, and the reason the wear target was worth building
 * before an audio one.
 *
 * ## Why the recognizer and not a recorder
 *
 * A watch that records and uploads needs a microphone permission, a codec,
 * a buffer, an upload, and a story about what happens to the file. A watch
 * that recognises needs a microphone permission. The second story is the
 * one that can be told in a sentence on a 45mm screen, and a privacy
 * promise nobody can read is a privacy promise nobody has.
 */
class Ear(private val context: Context) {

    private var recognizer: SpeechRecognizer? = null

    val available: Boolean get() = SpeechRecognizer.isRecognitionAvailable(context)

    /**
     * Listen for one turn.
     *
     * One turn, not a standing ear: the console holds an open microphone
     * because it sits on a desk with mains power, and a watch doing the
     * same is a watch that is flat by lunchtime. The person presses, says
     * the thing, and the recognizer closes itself.
     *
     * `onWords` fires with what was recognised. `onNothing` fires when the
     * recognizer heard no speech — reported rather than swallowed, because
     * `mic.heard` refuses an empty delivery on purpose ("an empty delivery
     * is not something the microphone heard") and a face that sent one
     * anyway would show that refusal to somebody who did nothing wrong.
     */
    fun listenOnce(language: String, onWords: (String) -> Unit,
                   onNothing: (String) -> Unit) {
        stop()
        if (!available) {
            onNothing("this watch has no speech recogniser")
            return
        }
        val r = SpeechRecognizer.createSpeechRecognizer(context)
        recognizer = r
        r.setRecognitionListener(object : RecognitionListener {
            override fun onResults(results: Bundle) {
                val said = results.getStringArrayList(
                    SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
                    .orEmpty().trim()
                if (said.isEmpty()) onNothing("nothing was heard in that")
                else onWords(said)
                stop()
            }

            override fun onError(error: Int) {
                onNothing(
                    when (error) {
                        SpeechRecognizer.ERROR_NO_MATCH,
                        SpeechRecognizer.ERROR_SPEECH_TIMEOUT ->
                            "nothing was heard in that"
                        SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS ->
                            "the watch has not been allowed to listen"
                        else -> "the watch could not listen just then"
                    })
                stop()
            }

            override fun onReadyForSpeech(params: Bundle?) {}
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onPartialResults(partialResults: Bundle?) {}
            override fun onEvent(eventType: Int, params: Bundle?) {}
        })
        r.startListening(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                     RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, language)
            // On device where the watch can. The point of sending words is
            // that the sound stays on the wrist; a recogniser that ships the
            // audio to a cloud transcriber to produce them would keep the
            // wire promise and break the actual one.
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
        })
    }

    /** Let the microphone go. Called from the screen's teardown as well as
     *  from every terminal callback above — a recogniser left running by a
     *  screen nobody is on is the wrist listening to a room. */
    fun stop() {
        recognizer?.run { runCatching { cancel() }; runCatching { destroy() } }
        recognizer = null
    }
}
