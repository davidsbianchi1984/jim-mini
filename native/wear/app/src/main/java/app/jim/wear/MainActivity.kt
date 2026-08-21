package app.jim.wear

import android.Manifest
import android.app.RemoteInput
import android.os.Bundle
import androidx.annotation.StringRes
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.wear.compose.material.Chip
import androidx.wear.compose.material.ChipDefaults
import androidx.wear.compose.material.MaterialTheme
import androidx.wear.compose.material.Scaffold
import androidx.wear.compose.material.Text
import androidx.wear.compose.material.TimeText
import androidx.wear.input.RemoteInputIntentHelper
import kotlinx.coroutines.launch

/**
 * The watch app: a way in, and four things.
 *
 * The console has 36 watch faces at wrist size. They are drawings — a
 * field report put it plainly, and it was right: nothing on a wrist could
 * reach the Guardian, because there was no watch target at all. This is
 * the target.
 *
 *     asked     do the watch screens look right
 *     mattered  is there a watch
 *
 * Deliberately small. Everything here is something a person would do
 * standing up with one hand: say how they are, say something to the coach,
 * see whether the wrist is actually being read, and call for help.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                val state: WatchState = viewModel()
                Scaffold(timeText = { TimeText() }) {
                    if (!state.signedIn) Pairing(state)
                    else Home(state)
                }
            }
        }
    }
}

/**
 * Getting in.
 *
 * A watch cannot enroll somebody — a birthdate typed on four millimetres of
 * glass is a birthdate somebody gave up on — so this is a sign-in, not a
 * sign-up, and it uses the same email and password as every other surface.
 * Three fields is three too many for a wrist and it is still the right
 * first version: it works on every watch, with no camera, no companion app
 * and no new door on the server.
 *
 * Each field opens Wear's own input screen, which takes **dictation** as
 * well as typing. That is the difference between this being awkward and
 * being impossible: nobody types an email address on a watch, and everybody
 * can say one.
 */
@Composable
private fun Pairing(state: WatchState) {
    var deployment by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }

    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState())
            .padding(horizontal = 8.dp, vertical = 26.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text(stringResource(R.string.app_name),
             style = MaterialTheme.typography.title3)

        DictatedField(R.string.deployment, deployment) { deployment = it }
        DictatedField(R.string.your_email, email) { email = it }
        // Wear's input screen does not mask what it is shown, so the
        // password is visible on the wrist while it is being entered. Said
        // out loud here rather than hidden: it is the person's own wrist,
        // and a caveat somebody knows about is one they can wait to be
        // alone for.
        DictatedField(R.string.your_password, password, masked = true) {
            password = it
        }

        Chip(
            onClick = {
                busy = true
                state.signInWith(deployment, email, password) { busy = false }
            },
            enabled = !busy && deployment.isNotBlank() &&
                email.isNotBlank() && password.isNotBlank(),
            label = { Text(stringResource(R.string.sign_in)) },
            modifier = Modifier.fillMaxWidth(),
            colors = ChipDefaults.primaryChipColors(),
        )

        if (state.trouble.isNotEmpty()) {
            Text(state.trouble, style = MaterialTheme.typography.caption2,
                 textAlign = TextAlign.Center)
        }
    }
}

/**
 * One field, filled by Wear's own input screen.
 *
 * `RemoteInput` is the platform's answer to "how does text get onto a
 * watch": it offers the keyboard, handwriting and dictation together and
 * lets the person choose. Rolling a `TextField` here instead would offer
 * only the worst of those three.
 */
@Composable
private fun DictatedField(
    @StringRes label: Int,
    value: String,
    masked: Boolean = false,
    onValue: (String) -> Unit,
) {
    val text = stringResource(label)
    val input = rememberLauncherForActivityResult(
        ActivityResultContracts.StartActivityForResult()) { result ->
        RemoteInput.getResultsFromIntent(result.data)
            ?.getCharSequence(FIELD)?.toString()?.let(onValue)
    }
    Chip(
        onClick = {
            val intent = RemoteInputIntentHelper.putRemoteInputsExtra(
                RemoteInputIntentHelper.createActionRemoteInputIntent(),
                listOf(RemoteInput.Builder(FIELD).setLabel(text).build()))
            input.launch(intent)
        },
        label = { Text(text) },
        secondaryLabel = {
            Text(when {
                value.isEmpty() -> ""
                masked -> "•".repeat(value.length.coerceAtMost(12))
                else -> value
            })
        },
        modifier = Modifier.fillMaxWidth(),
    )
}

private const val FIELD = "field"

@Composable
private fun Home(state: WatchState) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val wrist = remember { Wrist(context) }
    val ear = remember { Ear(context) }
    var said by remember { mutableStateOf("") }
    var bpm by remember { mutableStateOf(0) }

    // The pulse permission, asked at the switch and nowhere else.
    val askBody = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) wrist.start(
            onReading = { beat ->
                bpm = beat
                state.call({ WearApi.pulse(state.uid, state.token, beat) }) {
                    // The roster's own word, straight back from the door
                    // that recorded the moment — so the face says `sensing`
                    // because something arrived, never because a switch is
                    // on. See jim/api.py:monitor.
                    it.getOrNull()?.optString("standing")
                        ?.takeIf { s -> s.isNotEmpty() }
                        ?.let { s -> said = s }
                }
            },
            onUnavailable = { bpm = 0 })
    }
    val askMic = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()) { granted ->
        if (!granted) state.trouble = context.getString(R.string.mic_refused)
    }

    LaunchedEffect(Unit) { if (!state.paired) state.pairUp() else state.refresh() }
    // Leaving ends both. The same rule every voice screen in the console
    // learned: a sensor or a microphone left open by a screen nobody is on
    // is a thing nobody switched on.
    DisposableEffect(Unit) {
        onDispose {
            ear.stop()
            scope.launch {
                wrist.stop()
                runCatching { WearApi.releaseMic(state.uid, state.token) }
            }
        }
    }

    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState())
            .padding(horizontal = 8.dp, vertical = 26.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        // What is actually true, in the roster's own three words. A face
        // that printed "connected" over a switch would be the defect this
        // whole round exists to stop repeating.
        Text(
            stringResource(R.string.wrist_is, state.wrist) +
                if (bpm > 0) "  ·  $bpm" else "",
            style = MaterialTheme.typography.caption2,
            textAlign = TextAlign.Center,
        )

        Chip(
            onClick = { askBody.launch(Manifest.permission.BODY_SENSORS) },
            label = { Text(stringResource(R.string.read_my_pulse)) },
            modifier = Modifier.fillMaxWidth(),
            colors = ChipDefaults.primaryChipColors(),
        )

        Chip(
            onClick = {
                askMic.launch(Manifest.permission.RECORD_AUDIO)
                state.call({ WearApi.handover(state.uid, state.token) }) { r ->
                    if (r.isFailure) return@call
                    ear.listenOnce(
                        language = java.util.Locale.getDefault().language,
                        onWords = { words ->
                            state.call({
                                WearApi.heard(state.uid, state.token, words)
                            }) { heard ->
                                said = heard.getOrNull()?.optString("heard")
                                    ?: said
                                state.refresh()
                            }
                        },
                        onNothing = { why -> state.trouble = why },
                    )
                }
            },
            label = { Text(stringResource(R.string.say_something)) },
            modifier = Modifier.fillMaxWidth(),
        )

        Chip(
            onClick = {
                state.call({ WearApi.companion(state.uid, state.token) }) {
                    said = it.getOrNull().orEmpty().ifEmpty { said }
                }
            },
            label = { Text(stringResource(R.string.how_am_i)) },
            modifier = Modifier.fillMaxWidth(),
        )

        Chip(
            onClick = {
                state.call({
                    WearApi.emergency(state.uid, state.token)
                })
            },
            label = { Text(stringResource(R.string.get_help_now)) },
            modifier = Modifier.fillMaxWidth(),
            colors = ChipDefaults.primaryChipColors(
                backgroundColor = MaterialTheme.colors.error),
        )

        if (said.isNotEmpty()) {
            Text(said, style = MaterialTheme.typography.body2,
                 textAlign = TextAlign.Center)
        }
        // The Guardian's own sentence, held on screen rather than flashed.
        // A watch is glanced at, and a refusal that vanishes in two seconds
        // is a refusal nobody read.
        if (state.trouble.isNotEmpty()) {
            Text(state.trouble, style = MaterialTheme.typography.caption2,
                 textAlign = TextAlign.Center)
        }
    }
}
