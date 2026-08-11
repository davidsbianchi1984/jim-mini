package app.jim.guardian.ui

import android.content.Intent
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import app.jim.guardian.AccessReportRow
import app.jim.guardian.AppConn
import app.jim.guardian.BaselineMetric
import app.jim.guardian.CatalogApp
import app.jim.guardian.L10n
import app.jim.guardian.CheckinResult
import app.jim.guardian.CrashWatch
import app.jim.guardian.ChildCreated
import app.jim.guardian.ChildOverview
import app.jim.guardian.ChildSummary
import app.jim.guardian.GuardianFace
import app.jim.guardian.EmergencyResult
import app.jim.guardian.EscalationPolicy
import app.jim.guardian.Guidance
import app.jim.guardian.ImproveState
import app.jim.guardian.ContinuityState
import app.jim.guardian.SpecialistAnswer
import app.jim.guardian.CustodyList
import app.jim.guardian.OfflinePosture
import app.jim.guardian.CustodyProvenance
import app.jim.guardian.GuardianViewModel
import app.jim.guardian.ApiClient
import app.jim.guardian.Goal
import app.jim.guardian.Habit
import app.jim.guardian.LanguageInfo
import app.jim.guardian.AdaptationProfile
import app.jim.guardian.AnonymityPosture
import app.jim.guardian.FollowupAnswered
import app.jim.guardian.OpenFollowup
import app.jim.guardian.CommunityPlace
import app.jim.guardian.CareTeamState
import app.jim.guardian.CarePlanRow
import app.jim.guardian.MicState
import app.jim.guardian.MicEvent
import app.jim.guardian.MicTypeChoices
import app.jim.guardian.MicGainChoices
import app.jim.guardian.CaptureVocabulary
import app.jim.guardian.CaptureRecord
import app.jim.guardian.CommunityRoom
import app.jim.guardian.CommunityView
import app.jim.guardian.JournalItem
import app.jim.guardian.MedicalCard
import app.jim.guardian.MedicalCardIssued
import app.jim.guardian.MonitorResult
import app.jim.guardian.ProviderInfo
import app.jim.guardian.Robot
import app.jim.guardian.RobotSpec
import app.jim.guardian.SocialConn
import app.jim.guardian.SourceRow
import app.jim.guardian.TranslateResult
import app.jim.guardian.WaiverState
import app.jim.guardian.AlarmGuidance
import app.jim.guardian.AlarmRow
import app.jim.guardian.CircleHomepage
import app.jim.guardian.CircleMessage
import app.jim.guardian.CircleOverview
import app.jim.guardian.Finetune
import app.jim.guardian.MoneyOverview
import app.jim.guardian.MoneyWarning
import app.jim.guardian.Pace
import app.jim.guardian.PresenceBaseline
import app.jim.guardian.PresenceBearingView
import app.jim.guardian.PresenceBeat
import app.jim.guardian.PresenceGrowth
import app.jim.guardian.PresenceSpoken
import app.jim.guardian.PresenceSurfaces
import app.jim.guardian.PresenceWho
import app.jim.guardian.Problems
import app.jim.guardian.ScheduleOverview
import app.jim.guardian.ShoppingOverview
import kotlin.math.roundToInt

@Composable
private fun screenScroll(content: @Composable ColumnScope.() -> Unit) =
    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        content = content,
    )

@Composable
private fun SmallAction(text: String, enabled: Boolean = true, onClick: () -> Unit) {
    // A compact, inline sibling of BrandButton: sized to its label rather than
    // filling the row, for actions that sit beside a field instead of closing
    // out a card.
    Box(
        // Jim.Brand is a Brush and Jim.Card a Color, so they cannot share one
        // background() call — a ternary over the two unifies to Any and no
        // overload matches. Layer them the way BrandButton does instead.
        Modifier.clip(RoundedCornerShape(10.dp))
            .background(Jim.Card.copy(alpha = 0.4f))
            .then(if (enabled) Modifier.background(Jim.Brand) else Modifier)
            .clickable(enabled = enabled) { onClick() }
            .padding(horizontal = 14.dp, vertical = 8.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(text, color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
private fun BrandButton(text: String, enabled: Boolean = true, busy: Boolean = false, onClick: () -> Unit) {
    Box(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(13.dp))
            .background(Jim.Card.copy(alpha = 0.4f))            // muted base when disabled
            .then(if (enabled) Modifier.background(Jim.Brand) else Modifier)
            .clickable(enabled = enabled && !busy) { onClick() }
            .padding(vertical = 14.dp),
        contentAlignment = Alignment.Center,
    ) {
        if (busy) CircularProgressIndicator(color = Color.White, strokeWidth = 2.dp, modifier = Modifier.size(20.dp))
        else Text(text, color = Color.White, fontWeight = FontWeight.Bold)
    }
}

@Composable
private fun Modifier.clickableNoRipple(onClick: () -> Unit): Modifier =
    this.clickable(
        interactionSource = remember { MutableInteractionSource() },
        indication = null, onClick = onClick,
    )

// ---- Welcome / enroll ----

@Composable
fun WelcomeScreen(vm: GuardianViewModel) {
    var name by remember { mutableStateOf("") }
    var birthdate by remember { mutableStateOf("1984-01-01") }
    var consent by remember { mutableStateOf(false) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var languages by remember { mutableStateOf<List<LanguageInfo>>(emptyList()) }
    var language by remember { mutableStateOf(L10n.deviceLanguage()) }
    LaunchedEffect(Unit) {
        runCatching { ApiClient.languages() }.onSuccess { languages = it }
    }

    Box(Modifier.fillMaxSize().background(Jim.Bg)) {
        screenScroll {
            Spacer(Modifier.height(28.dp))
            Box(Modifier.align(Alignment.CenterHorizontally).size(84.dp).clip(CircleShape).background(Jim.Brand),
                contentAlignment = Alignment.Center) {
                Text("🛡", fontSize = 34.sp)
            }
            Text("Your Guardian, always here", color = Jim.Txt, fontSize = 22.sp,
                fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.CenterHorizontally))
            Text("Monitor, predict, guide, escalate — grounded in your baseline, on your device.",
                color = Jim.T2, fontSize = 13.sp, modifier = Modifier.align(Alignment.CenterHorizontally))

            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                labeledField(L10n.t("nw.name", language), name, L10n.t("res.name", language)) { name = it }
                labeledField(L10n.t("nw.birthdate", language), birthdate, L10n.t("nw.birthdate.ph", language)) { birthdate = it }
                if (languages.isNotEmpty()) {
                    Text(L10n.t("ov.language", language), color = Jim.T2, fontSize = 12.sp)
                    languages.chunked(3).forEach { row ->
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            row.forEach { l ->
                                FilterChip(
                                    selected = language == l.code,
                                    onClick = { language = l.code },
                                    label = { Text(l.label, fontSize = 11.sp) },
                                    colors = FilterChipDefaults.filterChipColors(
                                        selectedContainerColor = Jim.BrandA,
                                        selectedLabelColor = Color.White, labelColor = Jim.T2,
                                    ),
                                )
                            }
                        }
                    }
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(checked = consent, onCheckedChange = { consent = it },
                        colors = CheckboxDefaults.colors(checkedColor = Jim.Green))
                    Text("I consent to the terms of use", color = Jim.Txt, fontSize = 13.sp)
                }
            }
            error?.let { Text(it, color = Jim.Red, fontSize = 13.sp) }
            BrandButton(L10n.t("nw.start", language), enabled = consent && name.isNotBlank(), busy = busy) {
                error = null
                vm.enroll(name, birthdate, language,
                    onError = { error = it }, onBusy = { busy = it })
            }
            Text("By enrolling you agree to the Terms of Service — JIM-mini is a wellness tool, " +
             "not a medical device; in an emergency call 911 first. You assume the risks of " +
             "AI guidance and monitoring. Full terms: GET /terms · docs/terms.md",
            color = Jim.T3, fontSize = 9.sp)
        Text("Start the backend:  JIM_CORS_ORIGINS=* uvicorn jim.api:app",
                color = Jim.T3, fontSize = 10.sp)
        }
    }
}

@Composable
private fun labeledField(label: String, value: String, placeholder: String, onChange: (String) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(label, color = Jim.T2, fontSize = 12.sp)
        OutlinedTextField(
            value = value, onValueChange = onChange, singleLine = true,
            placeholder = { Text(placeholder, color = Jim.T3) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = Jim.Txt, unfocusedTextColor = Jim.Txt,
                focusedBorderColor = Jim.BrandA, unfocusedBorderColor = Jim.Line,
                focusedContainerColor = Jim.ScrBot, unfocusedContainerColor = Jim.ScrBot,
            ),
        )
    }
}

// ---- Overview ----

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OverviewScreen(vm: GuardianViewModel) {
    var metrics by remember { mutableStateOf<List<BaselineMetric>?>(null) }
    var refreshing by remember { mutableStateOf(false) }
    fun reload() {
        vm.call({ ApiClient.baseline(vm.uid!!, vm.token!!) }) { r ->
            metrics = r.getOrDefault(emptyList()); refreshing = false
        }
    }
    LaunchedEffect(Unit) { reload() }
    PullToRefreshBox(isRefreshing = refreshing,
        onRefresh = { refreshing = true; reload() }) {
    screenScroll {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Box(Modifier.size(8.dp).clip(CircleShape).background(Jim.Green))
            Text(L10n.t("ov.watching", vm.language), color = Jim.Green, fontSize = 12.sp, fontWeight = FontWeight.Bold)
        }
        Text(L10n.t("ov.hi", vm.language).replace("{name}", vm.displayName),
            color = Jim.Txt, fontSize = 28.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("ov.watching.sub", vm.language), color = Jim.T2, fontSize = 14.sp)

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(L10n.t("ov.baseline", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            when {
                metrics == null -> CircularProgressIndicator(color = Jim.BrandA, modifier = Modifier.size(22.dp))
                metrics!!.isEmpty() -> Text(L10n.t("ov.baseline.none", vm.language)
                    .replace("{screen}", L10n.t("tab.monitor", vm.language)),
                    color = Jim.T2, fontSize = 13.sp)
                else -> metrics!!.forEach { m ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(m.metric.replaceFirstChar { it.uppercase() }, color = Jim.Txt, fontSize = 14.sp)
                        Text(m.value?.roundToInt()?.toString() ?: (m.state ?: "—"), color = Jim.T2, fontSize = 14.sp)
                    }
                }
            }
        }
        ModelCard(vm)
        LanguageCard(vm)
        AdaptationCard(vm)
        TrainedModelCard(vm)
        AnonymityCard(vm)
        ImproveCard(vm)
        AccessCard(vm)
        OutlinedButton(onClick = { vm.signOut() }, modifier = Modifier.fillMaxWidth(),
            border = androidx.compose.foundation.BorderStroke(1.dp, Jim.Line)) {
            Text(L10n.t("action.sign_out", vm.language), color = Jim.T2)
        }
    }
    }
}

// ---- Monitor ----

@Composable
fun MonitorScreen(vm: GuardianViewModel) {
    var hr by remember { mutableFloatStateOf(72f) }
    var stress by remember { mutableFloatStateOf(0.2f) }
    var busy by remember { mutableStateOf(false) }
    var result by remember { mutableStateOf<MonitorResult?>(null) }
    // Spec [0039]: guidance that went out gets asked about. Read from
    // /followup rather than the monitor reply, so a question opened in an
    // earlier session is still asked instead of being silently dropped.
    var open by remember { mutableStateOf<List<OpenFollowup>>(emptyList()) }
    var answered by remember { mutableStateOf<FollowupAnswered?>(null) }
    var note by remember { mutableStateOf("") }

    fun reloadFollowups() {
        val uid = vm.uid ?: return
        val token = vm.token ?: return
        vm.call({ ApiClient.openFollowups(uid, token) }) { r ->
            open = r.getOrDefault(emptyList())
        }
    }
    LaunchedEffect(Unit) { reloadFollowups() }

    screenScroll {
        Text(L10n.t("mon", vm.language), color = Jim.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text("Send a sample. The Guardian compares it to your baseline.", color = Jim.T2, fontSize = 13.sp)
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            sliderRow(L10n.t("ci.hr", vm.language), "${hr.roundToInt()} bpm", Jim.Red, hr, 40f..180f) { hr = it }
            sliderRow(L10n.t("ci.stress", vm.language), "${(stress * 100).roundToInt()}%", Jim.Amber, stress, 0f..1f) { stress = it }
        }
        BrandButton(L10n.t("mon.send", vm.language), busy = busy) {
            busy = true
            vm.call({ ApiClient.monitor(vm.uid!!, vm.token!!, hr.roundToInt(), stress.toDouble()) }) {
                result = it.getOrNull(); busy = false
            }
        }
        result?.let { r ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Box(Modifier.size(9.dp).clip(CircleShape).background(if (r.detected) Jim.Red else Jim.Green))
                    Text(if (r.detected) (r.condition ?: "Detected").replaceFirstChar { it.uppercase() } else "All clear",
                        color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                }
                r.reason?.takeIf { it.isNotBlank() }?.let { Text(it, color = Jim.T2, fontSize = 13.sp) }
                r.guidance?.let {
                    HorizontalDivider(color = Jim.Line)
                    Text(it.content, color = Jim.Txt, fontSize = 14.sp)
                    GuidanceExtras(it)
                }
            }
        }

        // ---- [0039]: did that help? ----
        open.firstOrNull()?.let { f ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(f.question, color = Jim.Txt, fontSize = 16.sp,
                    fontWeight = FontWeight.Bold)
                Text("About the guidance for ${f.condition}.",
                    color = Jim.T2, fontSize = 12.sp)
                labeledField("", note, L10n.t("mon.add", vm.language)) { note = it }
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    listOf("It helped" to true, "It did not" to false).forEach { (label, helped) ->
                        SmallAction(label, enabled = !busy) {
                            val uid = vm.uid ?: return@SmallAction
                            val token = vm.token ?: return@SmallAction
                            busy = true
                            vm.call({ ApiClient.answerFollowup(uid, token, helped, note) }) { r ->
                                busy = false
                                answered = r.getOrNull()
                                note = ""
                                reloadFollowups()
                            }
                        }
                    }
                }
            }
        }

        answered?.let { a ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t(if (a.helped == true) "mon.resumes" else "mon.person", vm.language),
                    color = if (a.helped == true) Jim.Green else Jim.Amber,
                    fontSize = 16.sp, fontWeight = FontWeight.Bold)
                a.next?.let { Text(it, color = Jim.T2, fontSize = 12.sp) }
                // The spec's second door: not a tier, a list of people.
                a.options.forEach { op ->
                    Column(verticalArrangement = Arrangement.spacedBy(1.dp)) {
                        Text(op.name ?: op.kind.replace('_', ' '),
                            color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        op.channel?.takeIf { it.isNotBlank() }?.let {
                            Text(it, color = Jim.BrandA, fontSize = 12.sp)
                        }
                        op.note?.let { Text(it, color = Jim.T3, fontSize = 11.sp) }
                    }
                }
                a.liveNote?.let { Text(it, color = Jim.T3, fontSize = 11.sp) }
                a.reason?.let { Text(it, color = Jim.T3, fontSize = 12.sp) }
            }
        }

        // Clinical captures live with monitoring: what the body shows,
        // sealed beside what the body reports.
        CapturesPanel(vm)
    }
}

@Composable
private fun sliderRow(label: String, value: String, tint: Color, v: Float, range: ClosedFloatingPointRange<Float>, onChange: (Float) -> Unit) {
    Column {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(label, color = Jim.Txt, fontSize = 14.sp)
            Text(value, color = tint, fontSize = 14.sp, fontWeight = FontWeight.Bold)
        }
        Slider(value = v, onValueChange = onChange, valueRange = range,
            colors = SliderDefaults.colors(thumbColor = tint, activeTrackColor = tint))
    }
}

// ---- Check-in ----

@Composable
fun CheckinScreen(vm: GuardianViewModel) {
    var mood by remember { mutableIntStateOf(3) }
    var energy by remember { mutableIntStateOf(3) }
    var note by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var result by remember { mutableStateOf<CheckinResult?>(null) }

    screenScroll {
        Text(L10n.t("tab.checkin", vm.language), color = Jim.Txt, fontSize = 22.sp,
             fontWeight = FontWeight.Bold)
        Text("A quick pulse on how you're doing.", color = Jim.T2, fontSize = 13.sp)
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            ratingRow(L10n.t("ci.mood", vm.language), mood) { mood = it }
            ratingRow(L10n.t("ci.energy", vm.language), energy) { energy = it }
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text("Note", color = Jim.Txt, fontSize = 14.sp)
                OutlinedTextField(value = note, onValueChange = { note = it },
                    placeholder = { Text("Anything on your mind?", color = Jim.T3) },
                    modifier = Modifier.fillMaxWidth(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Text),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = Jim.Txt, unfocusedTextColor = Jim.Txt,
                        focusedBorderColor = Jim.BrandA, unfocusedBorderColor = Jim.Line,
                        focusedContainerColor = Jim.ScrBot, unfocusedContainerColor = Jim.ScrBot))
            }
        }
        BrandButton(L10n.t("ci.log", vm.language), busy = busy) {
            busy = true
            vm.call({ ApiClient.checkin(vm.uid!!, vm.token!!, mood, energy, note) }) {
                result = it.getOrNull(); busy = false
            }
        }
        result?.guidance?.let { g ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("Guidance", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(g.content, color = Jim.Txt, fontSize = 14.sp)
                GuidanceExtras(g)
            }
        }
    }
}

@Composable
private fun ratingRow(label: String, value: Int, onPick: (Int) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(label, color = Jim.Txt, fontSize = 14.sp)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            (1..5).forEach { i ->
                Box(Modifier.size(34.dp).clip(CircleShape)
                    .background(if (i <= value) Jim.BrandA else Jim.Card)
                    .clickableNoRipple { onPick(i) }, contentAlignment = Alignment.Center) {
                    Text("$i", color = if (i <= value) Color.White else Jim.T2, fontSize = 13.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

private val LIFE_AREAS = listOf("mental_health", "health_fitness", "career",
    "finance", "relationships", "personal_growth")

private fun pretty(s: String) = s.replace('_', ' ').replaceFirstChar { it.uppercase() }

// ---- Coach ----

@Composable
fun CoachScreen(vm: GuardianViewModel) {
    var area by remember { mutableStateOf("mental_health") }
    var message by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var reply by remember { mutableStateOf<Guidance?>(null) }
    var fromSpecialist by remember { mutableStateOf<SpecialistAnswer?>(null) }

    screenScroll {
        Text("Life Coach", color = Jim.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text("Talk something through. Your coach knows your baseline and goals.",
            color = Jim.T2, fontSize = 13.sp)
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            areaChips(area) { area = it }
            labeledField(L10n.t("coach.msg", vm.language), message, L10n.t("coach.msg.ph", vm.language)) { message = it }
        }
        BrandButton(L10n.t("coach.ask", vm.language), enabled = message.isNotBlank(), busy = busy) {
            busy = true
            fromSpecialist = null
            vm.call({ ApiClient.coach(vm.uid!!, vm.token!!, area, message) }) {
                reply = it.getOrNull(); busy = false
            }
        }
        reply?.let { g ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("Coach", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(g.content, color = Jim.Txt, fontSize = 14.sp)
                GuidanceExtras(g)

                // A specialist covers this area. An offer, not a send: what
                // would cross the tandem is what this person just wrote, so
                // the button is theirs and the note says so before they press.
                val offer = g.specialistOffer
                if (offer != null && offer.available && fromSpecialist == null) {
                    Text(offer.label, color = Jim.Txt, fontSize = 14.sp,
                        fontWeight = FontWeight.Bold)
                    Text(offer.note, color = Jim.T2, fontSize = 11.sp)
                    TextButton(enabled = !busy, onClick = {
                        busy = true
                        vm.call({ ApiClient.coachSpecialist(
                            vm.uid!!, vm.token!!, area, message) }) {
                            fromSpecialist = it.getOrNull(); busy = false
                        }
                    }) { Text(L10n.t("spec.ask", vm.language), color = Jim.BrandA, fontSize = 12.sp) }
                }
            }
        }
        fromSpecialist?.let { a ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text((a.label ?: L10n.t("spec.fallback", vm.language))
                     + " \u00b7 " + L10n.t("spec.via", vm.language),
                    color = Jim.Txt, fontSize = 16.sp,
                    fontWeight = FontWeight.Bold)
                when {
                    a.delivered && a.content != null ->
                        Text(a.content, color = Jim.Txt, fontSize = 14.sp)
                    a.heldForOwnerApproval ->
                        Text(L10n.t("spec.held", vm.language),
                            color = Jim.Amber, fontSize = 12.sp)
                    else ->
                        Text((a.reason ?: "") + (a.note?.let { " \u2014 $it" } ?: ""),
                            color = Jim.Amber, fontSize = 12.sp)
                }
                a.method?.let { Text(it, color = Jim.T2, fontSize = 11.sp) }
                a.shared?.let { Text(L10n.t("spec.shared", vm.language) + ": $it", color = Jim.T2, fontSize = 11.sp) }
            }
        }
    }
}

@Composable
private fun areaChips(selected: String, onPick: (String) -> Unit) {
    Text("Area", color = Jim.T2, fontSize = 12.sp)
    FlowRowChips(LIFE_AREAS, selected, onPick)
}

@Composable
private fun FlowRowChips(items: List<String>, selected: String, onPick: (String) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        items.chunked(2).forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                row.forEach { a ->
                    FilterChip(
                        selected = selected == a, onClick = { onPick(a) },
                        label = { Text(pretty(a), fontSize = 12.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Jim.BrandA,
                            selectedLabelColor = Color.White, labelColor = Jim.T2,
                        ),
                    )
                }
            }
        }
    }
}

// ---- Life: goals / habits / journal ----

@Composable
fun LifeScreen(vm: GuardianViewModel) {
    var tab by remember { mutableIntStateOf(0) }
    val tabs = listOf(
        L10n.t("life.goals", vm.language),
        L10n.t("life.habits", vm.language),
        L10n.t("life.journal", vm.language),
        L10n.t("life.money", vm.language),
        L10n.t("life.schedule", vm.language),
        L10n.t("life.shops", vm.language),
        L10n.t("life.circle", vm.language),
    )
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)) {
        TabRow(selectedTabIndex = tab, containerColor = Jim.Card, contentColor = Jim.BrandA) {
            tabs.forEachIndexed { i, t ->
                Tab(selected = tab == i, onClick = { tab = i },
                    text = { Text(t, fontSize = 13.sp) })
            }
        }
        when (tab) {
            0 -> GoalsPanel(vm)
            1 -> HabitsPanel(vm)
            2 -> JournalPanel(vm)
            3 -> MoneyPanel(vm)
            4 -> SchedulePanel(vm)
            5 -> TandemShopPanel(vm)
            else -> CirclePanel(vm)
        }
    }
}

@Composable
private fun GoalsPanel(vm: GuardianViewModel) {
    var goals by remember { mutableStateOf<List<Goal>>(emptyList()) }
    var area by remember { mutableStateOf("personal_growth") }
    var title by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    fun reload() { vm.call({ ApiClient.goals(vm.uid!!, vm.token!!) }) { r -> goals = r.getOrDefault(emptyList()) } }
    LaunchedEffect(Unit) { reload() }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("New goal", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            areaChips(area) { area = it }
            labeledField(L10n.t("goal.title", vm.language), title, L10n.t("goal.title.ph", vm.language)) { title = it }
            BrandButton(L10n.t("goal.add", vm.language), enabled = title.isNotBlank(), busy = busy) {
                busy = true
                vm.call({ ApiClient.addGoal(vm.uid!!, vm.token!!, area, title, null) }) {
                    title = ""; busy = false; reload()
                }
            }
        }
        goals.forEach { g ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(g.title, color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(pretty(g.area), color = Jim.T2, fontSize = 12.sp)
                    Text(pretty(g.status ?: "active"), color = Jim.T3, fontSize = 12.sp)
                }
            }
        }
    }
}

@Composable
private fun HabitsPanel(vm: GuardianViewModel) {
    var habits by remember { mutableStateOf<List<Habit>>(emptyList()) }
    var name by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    fun reload() { vm.call({ ApiClient.habits(vm.uid!!, vm.token!!) }) { r -> habits = r.getOrDefault(emptyList()) } }
    LaunchedEffect(Unit) { reload() }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("New habit", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            labeledField(L10n.t("habit.name", vm.language), name, L10n.t("habit.name.ph", vm.language)) { name = it }
            BrandButton(L10n.t("habit.add", vm.language), enabled = name.isNotBlank(), busy = busy) {
                busy = true
                vm.call({ ApiClient.addHabit(vm.uid!!, vm.token!!, name) }) {
                    name = ""; busy = false; reload()
                }
            }
        }
        habits.forEach { h ->
            Row(Modifier.card(), verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text(h.name, color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Text("🔥 ${h.streak ?: 0} day streak", color = Jim.Amber, fontSize = 12.sp)
                }
                TextButton(onClick = {
                    vm.call({ ApiClient.logHabit(vm.uid!!, vm.token!!, h.id) }) { reload() }
                }) { Text("Log", color = Jim.BrandA, fontSize = 13.sp, fontWeight = FontWeight.Bold) }
            }
        }
    }
}

@Composable
private fun JournalPanel(vm: GuardianViewModel) {
    var entries by remember { mutableStateOf<List<JournalItem>>(emptyList()) }
    var text by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    fun reload() { vm.call({ ApiClient.journal(vm.uid!!, vm.token!!) }) { r -> entries = r.getOrDefault(emptyList()) } }
    LaunchedEffect(Unit) { reload() }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("New entry", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            labeledField(L10n.t("jrn.entry", vm.language), text, L10n.t("jrn.entry.ph", vm.language)) { text = it }
            BrandButton(L10n.t("jrn.save", vm.language), enabled = text.isNotBlank(), busy = busy) {
                busy = true
                vm.call({ ApiClient.addJournal(vm.uid!!, vm.token!!, text) }) {
                    text = ""; busy = false; reload()
                }
            }
        }
        entries.asReversed().forEach { e ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(e.text ?: "—", color = Jim.Txt, fontSize = 14.sp)
                e.createdAt?.let { Text(it, color = Jim.T3, fontSize = 11.sp) }
            }
        }
    }
}

// The money guardian's phone door. Every visible string comes from the
// overview's own `labels` — composed server-side in the reader's language,
// exactly as the desktop Money card renders them — because the English count
// behind this shell's tabs is a ratchet and this panel must not feed it.
// Until the overview loads there is nothing to say, so nothing is said.
@Composable
private fun MoneyPanel(vm: GuardianViewModel) {
    var view by remember { mutableStateOf<MoneyOverview?>(null) }
    var institution by remember { mutableStateOf("") }
    var accountNumber by remember { mutableStateOf("") }
    var routingNumber by remember { mutableStateOf("") }
    var balanceText by remember { mutableStateOf("") }
    var goalText by remember { mutableStateOf("") }
    var scope by remember { mutableStateOf("") }
    var warnings by remember { mutableStateOf<List<MoneyWarning>>(emptyList()) }
    var note by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }

    fun reload() { vm.call({ ApiClient.moneyOverview(vm.uid!!, vm.token!!) }) { r -> view = r.getOrNull() } }
    LaunchedEffect(Unit) { reload() }
    fun act(block: suspend () -> Unit) {
        busy = true; note = null
        vm.call({ block() }) { r ->
            busy = false
            r.exceptionOrNull()?.let { note = it.message }
            reload()
        }
    }

    val v = view ?: return
    val labels = v.labels
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(labels["title"] ?: "", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(v.note, color = Jim.T2, fontSize = 12.sp)
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(labels["accounts"] ?: "", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            v.accounts.forEach { acc ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("${acc.label ?: acc.institution} · ${acc.kind}" +
                             (acc.last4?.let { " ····$it" } ?: ""),
                         color = Jim.Txt, fontSize = 12.sp)
                    acc.balance?.let {
                        val shown = (labels["balance"] ?: "") + ": " + "%.0f".format(it)
                        Text(shown, color = Jim.T2, fontSize = 12.sp)
                    }
                }
            }
            labeledField(labels["institution"] ?: "", institution, "") { institution = it }
            labeledField(labels["account_number"] ?: "", accountNumber, "") { accountNumber = it }
            labeledField(labels["routing_number"] ?: "", routingNumber, "") { routingNumber = it }
            BrandButton(labels["add_account"] ?: "", enabled = institution.isNotBlank(), busy = busy) {
                act {
                    ApiClient.moneyAddAccount(vm.uid!!, vm.token!!, "checking",
                                              institution, accountNumber, routingNumber)
                    institution = ""; accountNumber = ""; routingNumber = ""
                }
            }
        }

        v.accounts.firstOrNull()?.let { first ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(labels["record_balance"] ?: "", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                labeledField(labels["balance"] ?: "", balanceText, "") { balanceText = it }
                BrandButton(labels["record_balance"] ?: "",
                            enabled = balanceText.toDoubleOrNull() != null, busy = busy) {
                    act {
                        warnings = ApiClient.moneyObserve(vm.uid!!, vm.token!!,
                                                          first.id, balanceText.toDouble())
                    }
                }
                warnings.forEach { w ->
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text(w.message, color = Jim.Amber, fontSize = 12.sp)
                        if (w.specialist != null || w.desks.isNotEmpty()) {
                            Text(labels["doors"] ?: "", color = Jim.T2, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        }
                        w.specialist?.let { Text("· $it", color = Jim.T2, fontSize = 11.sp) }
                        w.desks.forEach { d ->
                            Text("· ${d.name} — ${d.trade} ${d.location}", color = Jim.T2, fontSize = 11.sp)
                        }
                    }
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(labels["savings_goal"] ?: "", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            v.savingsGoal?.let { val g = "%.0f".format(it); Text(g, color = Jim.T2, fontSize = 12.sp) }
            labeledField(labels["savings_goal"] ?: "", goalText, "") { goalText = it }
            BrandButton(labels["set_goal"] ?: "", enabled = goalText.toDoubleOrNull() != null, busy = busy) {
                act { ApiClient.moneySetSavings(vm.uid!!, vm.token!!, goalText.toDouble()) }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(labels["mandate"] ?: "", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            labeledField(labels["scope"] ?: "", scope, "") { scope = it }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                BrandButton(labels["mandate_save"] ?: "", enabled = scope.isNotBlank(), busy = busy) {
                    act { ApiClient.moneySetMandate(vm.uid!!, vm.token!!, true, 500.0, 1000.0, scope) }
                }
                // Never gated by plan or emptiness: taking your hands back
                // has no price and no preconditions beyond not mid-flight.
                BrandButton(labels["mandate_revoke"] ?: "", busy = busy) {
                    act { ApiClient.moneySetMandate(vm.uid!!, vm.token!!, false, 0.0, 0.0, "") }
                }
            }
            if (v.orders.isNotEmpty()) {
                Text(labels["orders"] ?: "", color = Jim.T2, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                v.orders.forEach { o ->
                    val line = o.assetClass + " " + "%.0f".format(o.amount) + " · " + o.status
                    Text(line, color = Jim.T3, fontSize = 11.sp)
                }
            }
        }

        note?.let { Text(it, color = Jim.T2, fontSize = 12.sp) }
    }
}

// The Guardian's calendar. Every visible string comes from the view's
// own labels — server-composed in the reader's language — because the
// English count behind this shell's tabs is a ratchet.
@Composable
private fun SchedulePanel(vm: GuardianViewModel) {
    var view by remember { mutableStateOf<ScheduleOverview?>(null) }
    var title by remember { mutableStateOf("") }
    var whenAt by remember { mutableStateOf("") }
    var whereAt by remember { mutableStateOf("") }
    var emailMe by remember { mutableStateOf(false) }
    var note by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }

    fun reload() { vm.call({ ApiClient.scheduleView(vm.uid!!, vm.token!!) }) { r -> view = r.getOrNull() } }
    LaunchedEffect(Unit) { reload() }

    val v = view ?: return
    val labels = v.labels
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(labels["title"] ?: "", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(v.note, color = Jim.T2, fontSize = 11.sp)
            labeledField(labels["what"] ?: "", title, "") { title = it }
            labeledField(labels["when"] ?: "", whenAt, "") { whenAt = it }
            labeledField(labels["where"] ?: "", whereAt, "") { whereAt = it }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Switch(checked = emailMe, onCheckedChange = { emailMe = it },
                       enabled = v.emailAvailable)
                val emailLabel = if (v.emailAvailable) labels["email_me"] ?: ""
                                 else labels["no_email"] ?: ""
                Text(emailLabel, color = Jim.T2, fontSize = 12.sp)
            }
            BrandButton(labels["book"] ?: "",
                        enabled = title.isNotBlank() && whenAt.isNotBlank(),
                        busy = busy) {
                busy = true
                vm.call({ ApiClient.scheduleBook(vm.uid!!, vm.token!!, title,
                                                 whenAt, whereAt, emailMe) }) { r ->
                    busy = false
                    r.exceptionOrNull()?.let { note = it.message }
                    title = ""; whenAt = ""; whereAt = ""
                    reload()
                }
            }
        }
        if (v.appointments.isNotEmpty()) {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(labels["upcoming"] ?: "", color = Jim.Txt, fontSize = 14.sp,
                    fontWeight = FontWeight.Bold)
                v.appointments.forEach { a ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        val line = a.title + " · " +
                            a.whenAt.take(16).replace("T", " ") +
                            (a.whereAt?.let { " · " + it } ?: "")
                        Text(line, color = Jim.T2, fontSize = 12.sp)
                        TextButton(onClick = {
                            vm.call({ ApiClient.scheduleCancel(vm.uid!!, vm.token!!, a.id) }) { reload() }
                        }) { Text(labels["cancel"] ?: "", color = Jim.Red, fontSize = 11.sp) }
                    }
                }
            }
        }
        note?.let { Text(it, color = Jim.T2, fontSize = 12.sp) }
    }
}

// The tandem shops shelf: QRME's storefronts, ordered as this user's own
// interactor, with the receipts kept in JIM. Same label discipline.
@Composable
private fun TandemShopPanel(vm: GuardianViewModel) {
    var view by remember { mutableStateOf<ShoppingOverview?>(null) }
    var shopId by remember { mutableStateOf("") }
    var offeringId by remember { mutableStateOf("") }
    var note by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }

    fun reload() { vm.call({ ApiClient.shoppingView(vm.uid!!, vm.token!!) }) { r -> view = r.getOrNull() } }
    LaunchedEffect(Unit) { reload() }

    val v = view ?: return
    val labels = v.labels
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(labels["title"] ?: "", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(v.note, color = Jim.T2, fontSize = 11.sp)
            v.shops.forEach { s ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    val line = s.name + " · " + s.seller + (s.tag?.let { " · " + it } ?: "")
                    Text(line, color = Jim.Txt, fontSize = 12.sp)
                    TextButton(onClick = { shopId = s.id }) {
                        Text(labels["browse"] ?: "", color = Jim.BrandA, fontSize = 12.sp)
                    }
                }
            }
            labeledField(labels["title"] ?: "", shopId, "") { shopId = it }
            labeledField(labels["offerings"] ?: "", offeringId, "") { offeringId = it }
            BrandButton(labels["order"] ?: "",
                        enabled = shopId.isNotBlank() && offeringId.isNotBlank(),
                        busy = busy) {
                busy = true
                vm.call({ ApiClient.shoppingOrder(vm.uid!!, vm.token!!, shopId,
                                                  offeringId, 1) }) { r ->
                    busy = false
                    r.exceptionOrNull()?.let { note = it.message }
                    offeringId = ""
                    reload()
                }
            }
        }
        if (v.receipts.isNotEmpty()) {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(labels["receipts"] ?: "", color = Jim.Txt, fontSize = 14.sp,
                    fontWeight = FontWeight.Bold)
                v.receipts.forEach { r ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        val line = r.title + " · " + "%.2f".format(r.amount) +
                            " " + r.currency + " · " + r.status
                        Text(line, color = Jim.T3, fontSize = 11.sp)
                        if (r.status == "placed") {
                            TextButton(onClick = {
                                vm.call({ ApiClient.shoppingCancel(vm.uid!!, vm.token!!,
                                    r.qrmeOrderId) }) { reload() }
                            }) { Text(labels["cancel"] ?: "", color = Jim.Red, fontSize = 11.sp) }
                        }
                    }
                }
            }
        }
        note?.let { Text(it, color = Jim.T2, fontSize = 12.sp) }
    }
}

// Your circle: contacts by mutual invitation, messages that never leave
// this deployment, the switches that govern both, and the homepage
// sandbox. Every visible string arrives from the view's `labels`, in the
// reader's language — same discipline as the shelf above.
@Composable
private fun CirclePanel(vm: GuardianViewModel) {
    var view by remember { mutableStateOf<CircleOverview?>(null) }
    var inviteId by remember { mutableStateOf("") }
    var withId by remember { mutableStateOf("") }
    var thread by remember { mutableStateOf<List<CircleMessage>>(emptyList()) }
    var draft by remember { mutableStateOf("") }
    var headline by remember { mutableStateOf("") }
    var about by remember { mutableStateOf("") }
    var bg by remember { mutableStateOf("#10251c") }
    var accent by remember { mutableStateOf("#2fbf8f") }
    var lookId by remember { mutableStateOf("") }
    var looking by remember { mutableStateOf<CircleHomepage?>(null) }
    var note by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }

    fun reload() {
        vm.call({ ApiClient.circleView(vm.uid!!, vm.token!!) }) { r ->
            r.getOrNull()?.let { v ->
                view = v
                headline = v.homepage.headline; about = v.homepage.about
                bg = v.homepage.bg; accent = v.homepage.accent
            }
        }
    }
    LaunchedEffect(Unit) { reload() }

    val v = view ?: return
    val labels = v.labels

    fun act(op: suspend () -> Unit) {
        busy = true; note = null
        vm.call({ op() }) { r ->
            busy = false
            r.exceptionOrNull()?.let { note = it.message }
            reload()
        }
    }

    fun open(other: String) {
        withId = other
        vm.call({ ApiClient.circleThread(vm.uid!!, vm.token!!, other) }) { r ->
            r.getOrNull()?.let { thread = it }
            r.exceptionOrNull()?.let { note = it.message }
        }
    }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(labels["title"] ?: "", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(v.note, color = Jim.T2, fontSize = 11.sp)
            v.contacts.forEach { p ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(p.displayName ?: p.userId, color = Jim.Txt, fontSize = 12.sp)
                    Row {
                        TextButton(onClick = { open(p.userId) }) {
                            Text(labels["open"] ?: "", color = Jim.BrandA, fontSize = 11.sp)
                        }
                        TextButton(onClick = { act { ApiClient.circleLeave(vm.uid!!, vm.token!!, p.userId) } }) {
                            Text(labels["leave"] ?: "", color = Jim.Red, fontSize = 11.sp)
                        }
                    }
                }
            }
            v.invitedMe.forEach { p ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    val line = (p.displayName ?: p.userId) + " · " + (labels["invited_me"] ?: "")
                    Text(line, color = Jim.T2, fontSize = 12.sp)
                    TextButton(onClick = { act { ApiClient.circleInvite(vm.uid!!, vm.token!!, p.userId) } }) {
                        Text(labels["invite"] ?: "", color = Jim.BrandA, fontSize = 11.sp)
                    }
                }
            }
            v.awaiting.forEach { p ->
                val line = (p.displayName ?: p.userId) + " · " + (labels["awaiting"] ?: "")
                Text(line, color = Jim.T3, fontSize = 11.sp)
            }
            labeledField(labels["invite"] ?: "", inviteId, "") { inviteId = it }
            BrandButton(labels["invite"] ?: "", enabled = inviteId.isNotBlank(), busy = busy) {
                val other = inviteId.trim(); inviteId = ""
                act { ApiClient.circleInvite(vm.uid!!, vm.token!!, other) }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(labels["messages"] ?: "", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            v.threads.forEach { t ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(t.otherName ?: t.otherId, color = Jim.Txt, fontSize = 12.sp)
                    TextButton(onClick = { open(t.otherId) }) {
                        Text(labels["open"] ?: "", color = Jim.BrandA, fontSize = 11.sp)
                    }
                }
            }
            labeledField(labels["to"] ?: "", withId, "") { withId = it }
            thread.forEach { m ->
                val line = (if (m.senderId == vm.uid) "→ " else "← ") + m.body
                Text(line, color = Jim.T2, fontSize = 11.sp)
            }
            labeledField(labels["send"] ?: "", draft, "") { draft = it }
            BrandButton(labels["send"] ?: "",
                        enabled = draft.isNotBlank() && withId.isNotBlank(),
                        busy = busy) {
                val words = draft; draft = ""
                busy = true
                vm.call({ ApiClient.circleSend(vm.uid!!, vm.token!!, withId, words) }) { r ->
                    busy = false
                    r.exceptionOrNull()?.let { note = it.message }
                    open(withId)
                    reload()
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(labels["switches"] ?: "", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            v.features.toSortedMap().forEach { (feature, on) ->
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Switch(checked = on, enabled = !busy, onCheckedChange = { want ->
                        act { ApiClient.circleSetFeature(vm.uid!!, vm.token!!, feature, want) }
                    })
                    val name = if (feature == "messaging") labels["sw_messaging"]
                               else labels["sw_homepage"]
                    Text(name ?: "", color = Jim.T2, fontSize = 12.sp)
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(labels["page"] ?: "", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            labeledField(labels["headline"] ?: "", headline, "") { headline = it }
            labeledField(labels["about"] ?: "", about, "") { about = it }
            labeledField(labels["background"] ?: "", bg, "") { bg = it }
            labeledField(labels["accent"] ?: "", accent, "") { accent = it }
            BrandButton(labels["save"] ?: "", enabled = true, busy = busy) {
                act { ApiClient.circleEditHomepage(vm.uid!!, vm.token!!,
                    headline, about, bg, accent) }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(labels["visit"] ?: "", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            labeledField(labels["visit_id"] ?: "", lookId, "") { lookId = it }
            BrandButton(labels["open"] ?: "", enabled = lookId.isNotBlank(), busy = busy) {
                vm.call({ ApiClient.circleHomepage(vm.uid!!, vm.token!!, lookId.trim()) }) { r ->
                    r.getOrNull()?.let { looking = it }
                    r.exceptionOrNull()?.let { note = it.message }
                }
            }
            looking?.let { page ->
                val head = (page.displayName ?: page.userId) + " — " + page.headline
                Text(head, color = Jim.Txt, fontSize = 13.sp, fontWeight = FontWeight.Bold)
                Text(page.about, color = Jim.T2, fontSize = 11.sp)
                page.links.forEach { l ->
                    Text(l.label + " · " + l.url, color = Jim.T3, fontSize = 11.sp)
                }
                if (page.topFriends.isNotEmpty()) {
                    val tops = (labels["top"] ?: "") + ": " +
                        page.topFriends.joinToString(" · ") { it.displayName ?: it.userId }
                    Text(tops, color = Jim.T3, fontSize = 11.sp)
                }
            }
        }

        note?.let { Text(it, color = Jim.T2, fontSize = 12.sp) }
    }
}

// ---- Safety: Emergency (SOS), escalation policy, robot helpers ----

// The crash watch: the vigil's acute sibling, armed here in advance. The
// Alarms — somebody scanned a care code, and somebody has to answer.
//
// The gap this closes: this shell could raise an emergency and command a bound
// robot to perform CPR, and could not answer the alarm about it. There was no
// occurrence of the word "alarm" anywhere in it.
//
// An alarm is raised when a stranger scans the care code on somebody's door,
// and the household relay pages a responder — a neighbour, an on-call carer.
// They are paged on their phone. Accepting is the act that stops the ladder
// climbing to emergency services, so a responder who cannot accept on the
// device they were paged on leaves only the path that ends in an ambulance.
@Composable
private fun AlarmsPanel(vm: GuardianViewModel) {
    var rows by remember { mutableStateOf<List<AlarmRow>>(emptyList()) }
    var responder by remember { mutableStateOf("") }
    var question by remember { mutableStateOf("") }
    var guidance by remember { mutableStateOf<AlarmGuidance?>(null) }
    var said by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    fun load() {
        vm.call({ ApiClient.alarms(vm.uid!!, vm.token!!) }) { rows = it.getOrNull() ?: emptyList() }
    }
    LaunchedEffect(Unit) { load() }

    val open = rows.filter { it.state == "open" }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        if (open.isEmpty()) {
            Text(L10n.t("alarm.none", vm.language), color = Jim.T2, fontSize = 14.sp)
            Text(L10n.t("alarm.lead", vm.language), color = Jim.T2, fontSize = 12.sp)
        }
        open.forEach { a ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(L10n.t("alarm.raised", vm.language), color = Jim.Red,
                    fontSize = 16.sp, fontWeight = FontWeight.Bold)
                a.messages.forEach { m ->
                    Text("\u201c$m\u201d", color = Jim.Txt, fontSize = 14.sp)
                }
                if (a.acceptedBy != null) {
                    // Accepted is not cleared. The server says so in its own
                    // response and this shell repeats it rather than greying
                    // the card out.
                    Text(L10n.t("alarm.attending", vm.language)
                            .replace("{who}", a.acceptedBy),
                        color = Jim.Amber, fontSize = 12.sp)
                } else {
                    // A named responder, because the backend refuses an empty
                    // one: "someone accepted it" is the thing this relay
                    // exists to stop being enough.
                    OutlinedTextField(value = responder,
                        onValueChange = { responder = it },
                        label = { Text(L10n.t("res.name", vm.language)) })
                    Button(onClick = {
                        vm.call({ ApiClient.acceptAlarm(vm.uid!!, a.id,
                            responder, vm.token!!) }) { said = it.getOrNull()?.note; load() }
                    }, enabled = responder.isNotBlank(),
                        colors = ButtonDefaults.buttonColors(containerColor = Jim.BrandA)) {
                        Text(L10n.t("alarm.going", vm.language))
                    }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    TextButton(onClick = {
                        vm.call({ ApiClient.escalateAlarm(vm.uid!!, a.id,
                            vm.token!!) }) { said = it.getOrNull()?.note; load() }
                    }) { Text(L10n.t("alarm.cannot_go", vm.language), color = Jim.Red) }
                    TextButton(onClick = {
                        vm.call({ ApiClient.clearAlarm(vm.uid!!, a.id,
                            vm.token!!) }) { said = it.getOrNull()?.note; load() }
                    }) { Text(L10n.t("alarm.clear", vm.language), color = Jim.T2) }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(value = question,
                        onValueChange = { question = it },
                        label = { Text(L10n.t("sos.whatdo", vm.language)) },
                        modifier = Modifier.weight(1f))
                    TextButton(onClick = {
                        vm.call({ ApiClient.alarmGuidance(a.id, question,
                            vm.token!!) }) { guidance = it.getOrNull() }
                    }, enabled = question.isNotBlank()) { Text("Ask") }
                }
            }
        }
        guidance?.let { g ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(g.answer, color = Jim.Txt, fontSize = 14.sp)
                g.note?.let { Text(it, color = Jim.T2, fontSize = 11.sp) }
            }
        }
        said?.let { Text(it, color = Jim.T2, fontSize = 12.sp) }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
        Text(L10n.t("alarm.not_emergency", vm.language),
            color = Jim.T2, fontSize = 11.sp)
    }
}

// status read is also the clock, so refreshing is what re-asks the question.
@Composable
private fun CrashWatchPanel(vm: GuardianViewModel) {
    var st by remember { mutableStateOf<CrashWatch?>(null) }
    var name by remember { mutableStateOf("") }
    var channel by remember { mutableStateOf("") }
    var attempts by remember { mutableStateOf("3") }
    var window by remember { mutableStateOf("5") }
    var ems by remember { mutableStateOf(false) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    fun took(r: Result<CrashWatch>) {
        busy = false
        r.onSuccess {
            st = it
            if (it.trustedName.isNotBlank()) name = it.trustedName
            attempts = it.attempts.toString()
            window = it.windowMinutes.toInt().toString()
            ems = it.contactEms
        }.onFailure { error = it.message }
    }

    LaunchedEffect(Unit) {
        vm.call({ ApiClient.crashWatch(vm.uid!!, vm.token!!) }) { took(it) }
    }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        if (st?.asking == true) {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(L10n.t("alarm.asking", vm.language), color = Jim.Amber,
                    fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(L10n.t("alarm.concern", vm.language)
                         .replace("{concern}", st?.concern ?: "")
                         .replace("{n}", "${st?.attempt ?: 1}")
                         .replace("{total}", "${st?.attempts ?: 3}"),
                    color = Jim.T2, fontSize = 12.sp)
                Button(onClick = {
                    vm.call({ ApiClient.imOkay(vm.uid!!, vm.token!!) }) { took(it) }
                }, colors = ButtonDefaults.buttonColors(containerColor = Jim.Green)) {
                    Text(L10n.t("alarm.im_okay", vm.language))
                }
            }
        }
        if (st?.tripped == true) {
            Text(L10n.t("alarm.tripped", vm.language)
                     .replace("{name}", st?.trustedName ?: ""),
                color = Jim.Red, fontSize = 13.sp)
        }
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(L10n.t("cw", vm.language), color = Jim.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("cw.sub", vm.language),
                color = Jim.T2, fontSize = 12.sp)
            labeledField(L10n.t("cw.trusted", vm.language), name, L10n.t("res.name.ph", vm.language)) { name = it }
            labeledField(L10n.t("cw.reach", vm.language), channel, L10n.t("res.email.ph", vm.language)) { channel = it }
            labeledField(L10n.t("res.attempts", vm.language), attempts, "3") { attempts = it }
            labeledField(L10n.t("res.minutes", vm.language), window, "5") { window = it }
            Row(verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Checkbox(checked = ems, onCheckedChange = { ems = it },
                    colors = CheckboxDefaults.colors(checkedColor = Jim.Red))
                Text(L10n.t("alarm.ems", vm.language),
                    color = Jim.T2, fontSize = 12.sp)
            }
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Button(enabled = !busy, onClick = {
                    busy = true; error = null
                    vm.call({
                        ApiClient.armCrashWatch(vm.uid!!, vm.token!!, name,
                            channel, attempts.toIntOrNull() ?: 3,
                            window.toDoubleOrNull() ?: 5.0, ems)
                    }) { took(it) }
                }) { Text(L10n.t(if (st?.armed == true) "action.update" else "cw.arm", vm.language)) }
                if (st?.armed == true) {
                    Button(enabled = !busy, onClick = {
                        busy = true
                        vm.call({ ApiClient.disarmCrashWatch(vm.uid!!, vm.token!!) }) { took(it) }
                    }, colors = ButtonDefaults.buttonColors(containerColor = Jim.Card)) {
                        Text(L10n.t("cw.disarm", vm.language), color = Jim.Red)
                    }
                }
            }
            if (st?.armed == true && st?.asking != true && st?.tripped != true) {
                Text(L10n.t("alarm.armed", vm.language)
                         .replace("{name}", st?.trustedName ?: "")
                         .replace("{n}", "${st?.attempts ?: 3}"),
                    color = Jim.Green, fontSize = 12.sp)
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 13.sp) }
    }
}



@Composable
fun SafetyScreen(vm: GuardianViewModel) {
    var tab by remember { mutableIntStateOf(0) }
    // Alarms first and selected by default: somebody opening this screen has
    // usually just been paged, and the thing they were paged about should not
    // be behind a tab they have to go looking for.
    val tabs = listOf(
        L10n.t("alarm.lead.short", vm.language), L10n.t("sos", vm.language),
        L10n.t("cw.short", vm.language), L10n.t("mid.short", vm.language),
        L10n.t("cw.policy", vm.language), L10n.t("rob.short", vm.language),
        L10n.t("cust", vm.language))
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)) {
        ProblemReportingCard(vm.language)
        TabRow(selectedTabIndex = tab, containerColor = Jim.Card, contentColor = Jim.BrandA) {
            tabs.forEachIndexed { i, t ->
                Tab(selected = tab == i, onClick = { tab = i },
                    text = { Text(t, fontSize = 13.sp) })
            }
        }
        when (tab) {
            0 -> AlarmsPanel(vm)
            1 -> SOSPanel(vm)
            2 -> CrashWatchPanel(vm)
            3 -> MedicalPanel(vm)
            4 -> PolicyPanel(vm)
            5 -> RobotsPanel(vm)
            else -> CustodyPanel(vm)
        }
    }
}

@Composable
private fun SOSPanel(vm: GuardianViewModel) {
    var situation by remember { mutableStateOf("") }
    var location by remember { mutableStateOf("") }
    var result by remember { mutableStateOf<EmergencyResult?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Box(
            Modifier.fillMaxWidth().clip(RoundedCornerShape(20.dp)).background(Jim.Red)
                .clickable(enabled = !busy) {
                    busy = true; error = null
                    vm.call({ ApiClient.emergency(vm.uid!!, vm.token!!, situation, location) }) { r ->
                        busy = false
                        r.onSuccess { result = it }.onFailure { error = it.message }
                    }
                }
                .padding(vertical = 28.dp),
            contentAlignment = Alignment.Center,
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(L10n.t("sos", vm.language), color = Color.White, fontSize = 34.sp,
                     fontWeight = FontWeight.Black)
                Text(L10n.t(if (busy) "sos.coordinating" else "sos.tap", vm.language),
                    color = Color.White, fontSize = 12.sp)
            }
        }
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            labeledField(L10n.t("sos.what", vm.language), situation, "") { situation = it }
            labeledField(L10n.t("sos.where", vm.language), location, "") { location = it }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 13.sp) }
        result?.let { r ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Coordinated response", color = Jim.Txt, fontSize = 16.sp,
                    fontWeight = FontWeight.Bold)
                r.flow.forEachIndexed { i, s ->
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        Text("${i + 1}", color = Jim.Red, fontSize = 12.sp,
                            fontWeight = FontWeight.Bold)
                        Column {
                            Text(s.label, color = Jim.Txt, fontSize = 14.sp,
                                fontWeight = FontWeight.Bold)
                            Text(s.detail, color = Jim.T2, fontSize = 12.sp)
                        }
                    }
                }
                r.directives.forEach { d ->
                    Text("🤖 ${d.robot}: ${d.directive.replace('_', ' ')}",
                        color = Jim.Amber, fontSize = 12.sp)
                }
            }
        }
    }
}

@Composable
private fun PolicyPanel(vm: GuardianViewModel) {
    var policy by remember { mutableStateOf<EscalationPolicy?>(null) }
    fun reload() {
        vm.call({ ApiClient.escalationPolicy(vm.uid!!, vm.token!!) }) { r -> policy = r.getOrNull() }
    }
    LaunchedEffect(Unit) { reload() }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("cw.sensitivity", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                listOf("cautious", "balanced", "assertive").forEach { lvl ->
                    FilterChip(
                        selected = policy?.sensitivity == lvl,
                        onClick = {
                            vm.call({ ApiClient.setSensitivity(vm.uid!!, vm.token!!, lvl) }) { reload() }
                        },
                        // Capitalizing the API's own enum member is not a label.
                        label = { Text(sensitivityLabel(lvl, vm.language), fontSize = 12.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Jim.BrandA,
                            selectedLabelColor = Color.White, labelColor = Jim.T2,
                        ),
                    )
                }
            }
            Text(L10n.t("cw.sensitivity.sub", vm.language),
                color = Jim.T2, fontSize = 12.sp)
        }
        policy?.let { p ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("How each severity resolves", color = Jim.Txt, fontSize = 16.sp,
                    fontWeight = FontWeight.Bold)
                listOf("info", "guidance", "critical").forEach { sev ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(sev.replaceFirstChar { it.uppercase() }, color = Jim.Txt, fontSize = 14.sp)
                        Text((p.bySeverity[sev] ?: "—").replace('_', ' '),
                            color = if (sev == "critical") Jim.Red else Jim.BrandA,
                            fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
private fun GuidanceExtras(g: Guidance) {
    g.specialist?.let { who ->
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Text(who, color = Jim.Txt, fontSize = 12.sp,
                fontWeight = FontWeight.Bold)
            if (g.source == "tandem")
                Text("LIVE · QRME", color = Jim.Green, fontSize = 10.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier
                        .background(Jim.Green.copy(alpha = 0.16f),
                            RoundedCornerShape(50))
                        .padding(horizontal = 7.dp, vertical = 2.dp))
        }
    }
    g.custody?.let { c ->
        if (c.vaulted && c.pdiKey != null) {
            Column {
                Text("🔒 Sealed in the PDI vault", color = Jim.Green,
                    fontSize = 10.sp, fontWeight = FontWeight.Bold)
                Text(c.pdiKey, color = Jim.T3, fontSize = 9.sp, maxLines = 1)
            }
        } else c.note?.let {
            Text("⚠️ $it", color = Jim.Amber, fontSize = 10.sp)
        }
    }
    g.firstAid?.let { aid ->
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("First aid — ${aid.kind.uppercase()}", color = Jim.Red,
                fontSize = 13.sp, fontWeight = FontWeight.Bold)
            if (aid.callEms)
                Text("📞 Call emergency services now", color = Jim.Red,
                    fontSize = 12.sp, fontWeight = FontWeight.Bold)
            aid.steps.forEachIndexed { i, step ->
                Text("${i + 1}. $step", color = Jim.Txt, fontSize = 12.sp)
            }
            aid.pace?.let { pace ->
                Text("Pace: ${pace.perMinute}/min · ${pace.ratio}",
                    color = Jim.Amber, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                pace.lightCue?.let { Text("💡 $it", color = Jim.T2, fontSize = 11.sp) }
                pace.audioCue?.let { Text("🔊 $it", color = Jim.T2, fontSize = 11.sp) }
            }
        }
    }
    g.translationNote?.let {
        Text("🌐 $it", color = Jim.Amber, fontSize = 10.sp)
    }
    g.references.forEach { ref ->
        Text("→ $ref", fontSize = 11.sp,
            color = if ("988" in ref) Jim.Green else Jim.T2)
    }
    g.provenance?.let { p ->
        Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
            HorizontalDivider(color = Jim.Line)
            Text("Derived from", color = Jim.Txt, fontSize = 12.sp,
                fontWeight = FontWeight.Bold)
            p.evidence.forEach { e ->
                Text("${e.publisher} — ${e.title}", color = Jim.Txt, fontSize = 11.sp)
                e.supports?.let {
                    Text("supports: $it", color = Jim.T2, fontSize = 10.sp)
                }
                Text(e.url, color = Jim.BrandA, fontSize = 10.sp)
            }
            Text("${p.method} · generated by ${p.generatedBy}",
                color = Jim.T3, fontSize = 10.sp)
            Text(p.disclaimer, color = Jim.T3, fontSize = 10.sp)
        }
    }
}

/**
 * What this deployment can and cannot reach.
 *
 * Offline mode was settable and unreadable: the flag existed, the guarantee
 * was written in a docstring, and there was nowhere on a phone to see the
 * answer.
 *
 *     asked     can the guarantee be turned on
 *     mattered  can it be checked
 *
 * Read-only on purpose. The posture is set in the deployment's environment,
 * not by somebody signed into the app — a switch here would imply otherwise.
 */
@Composable
fun OfflinePostureCard(vm: GuardianViewModel) {
    var posture by remember { mutableStateOf<OfflinePosture?>(null) }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.offlineStatus() }) { r -> posture = r.getOrNull() }
    }
    posture?.let { p ->
        Card(colors = CardDefaults.cardColors(containerColor = Jim.Card)) {
            Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("offline.title", vm.language),
                     style = MaterialTheme.typography.titleSmall)
                Text(if (p.offline) L10n.t("offline.on", vm.language)
                     else L10n.t("offline.off", vm.language),
                     color = if (p.offline) Jim.Green else Jim.T2, fontSize = 12.sp,
                     fontWeight = FontWeight.Bold)
                Text(p.localDestinationsAllowed, color = Jim.T2, fontSize = 11.sp)
                p.guarantees.forEach { line ->
                    Text("\u2022 " + line, color = Jim.T2, fontSize = 11.sp)
                }
            }
        }
    }
}

@Composable
private fun CustodyPanel(vm: GuardianViewModel) {
    var list by remember { mutableStateOf<CustodyList?>(null) }
    var prov by remember { mutableStateOf<Map<String, CustodyProvenance>>(emptyMap()) }
    var open by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    var held by remember { mutableStateOf<String?>(null) }
    var typed by remember { mutableStateOf("") }
    var gone by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.custody(vm.uid!!, vm.token!!) }) { r ->
            r.onSuccess { list = it; error = null }
            r.onFailure { error = it.message }
        }
    }
    LaunchedEffect(Unit) { reload() }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(L10n.t("cust", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        OfflinePostureCard(vm)
        // The portability door. Counts and table names on the phone; the
        // document itself is what the console downloads. A person whose only
        // device is a phone is exactly the person who cannot reach a console.
        Text(L10n.t("hld.take", vm.language), color = Jim.Txt, fontSize = 14.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("hld.take.pitch", vm.language), color = Jim.T2, fontSize = 12.sp)
        BrandButton(L10n.t("hld.take.go", vm.language), enabled = true) {
            vm.call({ ApiClient.exportEverything(vm.uid ?: "", vm.token ?: "") }) { r ->
                r.onSuccess { (tables, rows) ->
                    held = L10n.t("hld.take.held", vm.language)
                        .replace("{t}", tables.toString())
                        .replace("{r}", rows.toString())
                }
                r.onFailure { error = it.message }
            }
        }
        held?.let { Text(it, color = Jim.T2, fontSize = 12.sp) }

        // The exit, beside the portability door on purpose: *take it* and
        // *end it* are the two halves of the same claim, and this shell
        // carried only the first one.
        Text(L10n.t("hld.end", vm.language), color = Jim.Red, fontSize = 14.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("hld.end.pitch", vm.language), color = Jim.T2, fontSize = 12.sp)
        OutlinedTextField(
            value = typed, onValueChange = { typed = it }, singleLine = true,
            placeholder = { Text(L10n.t("hld.end.ph", vm.language)) },
            modifier = Modifier.fillMaxWidth())
        // Armed only by the word itself. There is no undo behind this.
        BrandButton(L10n.t("hld.end.go", vm.language), enabled = typed == "erase") {
            vm.call({ ApiClient.eraseEverything(vm.uid ?: "", vm.token ?: "") }) { r ->
                r.onSuccess { gone = L10n.t("hld.end.gone", vm.language); vm.signOut() }
                r.onFailure { error = it.message }
            }
        }
        gone?.let { Text(it, color = Jim.T2, fontSize = 12.sp) }
        Text("Chats with tandem specialists are sealed into the PDI vault — " +
             "encrypted, attributed, and hash-chained. This is your copy of " +
             "the proof.", color = Jim.T2, fontSize = 12.sp)
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
        list?.let { c ->
            Text(L10n.t(if (c.chainIntact == true) "cust.chain.ok"
                        else "cust.chain.unknown", vm.language),
                color = if (c.chainIntact == true) Jim.Green else Jim.Amber,
                fontSize = 12.sp, fontWeight = FontWeight.Bold)
            if (c.records.isEmpty())
                Text("No sealed exchanges yet — they appear after a tandem " +
                     "specialist chat.", color = Jim.T2, fontSize = 12.sp)
            c.records.forEach { key ->
                Column(
                    Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp))
                        .background(Jim.Card)
                        .clickable {
                            open = if (open == key) null else key
                            if (prov[key] == null)
                                vm.call({ ApiClient.custodyProvenance(
                                    vm.uid!!, vm.token!!, key) }) { r ->
                                    r.getOrNull()?.let { prov = prov + (key to it) }
                                }
                        }
                        .padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(3.dp),
                ) {
                    Text("🔒 $key", color = Jim.Txt, fontSize = 11.sp, maxLines = 1)
                    if (open == key) prov[key]?.let { p ->
                        Text("Origin: ${p.origin}", color = Jim.Txt, fontSize = 11.sp)
                        p.cipher?.let {
                            Text("Seal: $it", color = Jim.T2, fontSize = 10.sp)
                        }
                        Text("Audit events: ${p.auditCount}", color = Jim.T2,
                            fontSize = 10.sp)
                        Text(L10n.t(if (p.chainIntact == true) "cust.hash.ok"
                                    else "cust.hash.unknown", vm.language),
                            color = if (p.chainIntact == true) Jim.Green
                                    else Jim.Amber,
                            fontSize = 10.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
private fun RobotsPanel(vm: GuardianViewModel) {
    var catalog by remember { mutableStateOf<List<RobotSpec>>(emptyList()) }
    var chosen by remember { mutableStateOf("neo") }
    var robots by remember { mutableStateOf<List<Robot>>(emptyList()) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var cmdResult by remember { mutableStateOf<String?>(null) }
    var confirmingCpr by remember { mutableStateOf<String?>(null) }
    var waiver by remember { mutableStateOf<WaiverState?>(null) }
    var signature by remember { mutableStateOf("") }

    fun reload() {
        vm.call({ ApiClient.robots(vm.uid!!, vm.token!!) }) { r -> robots = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.waiver(vm.uid!!, vm.token!!) }) { r -> waiver = r.getOrNull() }
    }

    fun command(rob: Robot, cmd: String, arg: String?) {
        error = null
        vm.call({ ApiClient.commandRobot(vm.uid!!, vm.token!!, rob.id, cmd, arg) }) { r ->
            r.onSuccess { res ->
                cmdResult = when {
                    res.sequence.isNotEmpty() -> res.sequence.joinToString(" → ")
                    res.spokenSteps.isNotEmpty() -> "🔊 " + res.spokenSteps.joinToString(" → ")
                    res.pacePerMinute != null ->
                        (res.note ?: res.status) + " · ${res.pacePerMinute}/min"
                    else -> res.note ?: res.instruction ?: res.status
                }
            }.onFailure { error = it.message }
            reload()
        }
    }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.roboticsCatalog() }) { r -> catalog = r.getOrDefault(emptyList()) }
        reload()
    }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("rob.bind", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("rob.sub", vm.language),
                color = Jim.T2, fontSize = 12.sp)
            catalog.chunked(2).forEach { row ->
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    row.forEach { s ->
                        FilterChip(
                            selected = chosen == s.model, onClick = { chosen = s.model },
                            label = { Text(s.label, fontSize = 11.sp) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = Jim.BrandA,
                                selectedLabelColor = Color.White, labelColor = Jim.T2,
                            ),
                        )
                    }
                }
            }
            BrandButton(L10n.t("rob.bind.go", vm.language), enabled = catalog.isNotEmpty(), busy = busy) {
                busy = true; error = null
                vm.call({ ApiClient.bindRobot(vm.uid!!, vm.token!!, chosen) }) { r ->
                    busy = false
                    r.onFailure { error = it.message }
                    reload()
                }
            }
        }
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(L10n.t("res.waiver", vm.language), color = Jim.Txt,
                    fontSize = 15.sp, fontWeight = FontWeight.Bold)
                if (waiver?.signed == true)
                    Text(L10n.t("res.signed", vm.language), color = Jim.Green, fontSize = 10.sp,
                        fontWeight = FontWeight.Bold)
            }
            if (waiver?.signed == true) {
                Text("Signed by ${waiver?.signature ?: ""} — CPR-rated robots may start " +
                    "compressions automatically and operate a fully-automatic AED. A shock " +
                    "still only follows the AED's own rhythm analysis.",
                    color = Jim.T2, fontSize = 12.sp)
                TextButton(onClick = {
                    vm.call({ ApiClient.revokeWaiver(vm.uid!!, vm.token!!) }) {
                        cmdResult = "Waiver revoked — confirm-gated operation restored."
                        reload()
                    }
                }) { Text(L10n.t("res.revoke", vm.language), color = Jim.Red, fontSize = 12.sp) }
            } else {
                Text("Unlock automatic operation: CPR that starts on detection, and a " +
                    "fully-automatic AED that shocks on its own analysis after the robot " +
                    "verifies everyone is clear. Until signed, every start needs an " +
                    "on-scene confirmation and no shock is ever delivered.",
                    color = Jim.T2, fontSize = 12.sp)
                waiver?.terms?.forEach { t ->
                    Text("• $t", color = Jim.T3, fontSize = 10.sp)
                }
                labeledField(L10n.t("res.sign.ph", vm.language), signature, vm.displayName) { signature = it }
                RobotAction(L10n.t("res.sign", vm.language)) {
                    if (signature.isNotBlank()) {
                        error = null
                        vm.call({ ApiClient.signWaiver(vm.uid!!, vm.token!!, signature) }) { r ->
                            r.onSuccess {
                                waiver = it; signature = ""
                                cmdResult = "Waiver signed — automatic resuscitation pre-authorized."
                            }.onFailure { error = it.message }
                        }
                    }
                }
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 13.sp) }
        cmdResult?.let { Text(it, color = Jim.Green, fontSize = 12.sp) }
        robots.forEach { rob ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically) {
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        Text(rob.name, color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        rob.firstAid?.let { rating ->
                            Text(L10n.t(if (rating == "perform") "rob.cpr_rated" else "sos.firstaid", vm.language),
                                color = Jim.Green, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                    Text((rob.status ?: "docked").replace('_', ' ')
                        .replaceFirstChar { it.uppercase() },
                        color = Jim.T2, fontSize = 12.sp)
                }
                rob.directive?.let {
                    Text("On escalation: ${it.replace('_', ' ')}", color = Jim.Amber, fontSize = 12.sp)
                }
                if ("fetch_aed" in rob.commands) {
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        RobotAction(L10n.t("fa.aed", vm.language)) { command(rob, "fetch_aed", null) }
                        RobotAction(L10n.t("fa.coach", vm.language)) { command(rob, "guide_first_aid", "cpr") }
                        RobotAction(L10n.t("fa.ems", vm.language)) { command(rob, "meet_responders", null) }
                    }
                }
                if ("perform_cpr" in rob.commands) {
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        when {
                            rob.status == "performing_cpr" ->
                                RobotAction(L10n.t("fa.stop", vm.language), Jim.Red) { command(rob, "stop_cpr", null) }
                            waiver?.signed == true -> {
                                RobotAction(L10n.t("fa.start", vm.language), Jim.Red) {
                                    command(rob, "perform_cpr", null)
                                }
                                RobotAction(L10n.t("res.auto", vm.language), Jim.Red) {
                                    command(rob, "auto_defib", null)
                                }
                            }
                            confirmingCpr == rob.id -> {
                                RobotAction(L10n.t("res.confirm", vm.language), Jim.Red) {
                                    confirmingCpr = null
                                    command(rob, "perform_cpr", "confirmed")
                                }
                                TextButton(onClick = { confirmingCpr = null }) {
                                    Text("Cancel", color = Jim.T2, fontSize = 12.sp)
                                }
                            }
                            else -> RobotAction(L10n.t("fa.perform", vm.language), Jim.Red) {
                                confirmingCpr = rob.id
                                cmdResult = "Confirm the person is unresponsive and not " +
                                    "breathing normally. The robot never starts on its own " +
                                    "judgement — and never delivers a shock; the AED " +
                                    "analyzes, a human presses."
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun RobotAction(text: String, tint: Color = Jim.BrandA, onClick: () -> Unit) {
    Box(
        Modifier.clip(RoundedCornerShape(50)).background(tint)
            .clickableNoRipple(onClick)
            .padding(horizontal = 10.dp, vertical = 7.dp),
    ) {
        Text(text, color = Color.White, fontSize = 11.sp, fontWeight = FontWeight.Bold)
    }
}

// ---- Model picker (which LLM powers coaching & guidance) ----

@Composable
fun ModelCard(vm: GuardianViewModel) {
    var providers by remember { mutableStateOf<List<ProviderInfo>>(emptyList()) }
    var current by remember { mutableStateOf("auto") }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.models() }) { r -> providers = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.userModel(vm.uid!!, vm.token!!) }) { r ->
            r.getOrNull()?.let { current = it }
        }
    }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ov.model", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("ov.model.sub", vm.language), color = Jim.T2, fontSize = 12.sp)
        providers.chunked(2).forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                row.forEach { p ->
                    FilterChip(
                        selected = current == p.name,
                        onClick = {
                            vm.call({ ApiClient.setModel(vm.uid!!, vm.token!!, p.name) }) {
                                current = p.name
                            }
                        },
                        label = { Text(p.label + if (p.configured) "" else " (no key)",
                            fontSize = 11.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Jim.BrandA,
                            selectedLabelColor = Color.White, labelColor = Jim.T2,
                        ),
                    )
                }
            }
        }
    }
}

@Composable
fun LanguageCard(vm: GuardianViewModel) {
    var languages by remember { mutableStateOf<List<LanguageInfo>>(emptyList()) }
    var current by remember { mutableStateOf("en") }
    var preTranslate by remember { mutableStateOf(true) }
    var translateInput by remember { mutableStateOf("") }
    var llmKey by remember { mutableStateOf(vm.llmKey) }
    var inviteKey by remember { mutableStateOf(vm.signupKey) }
    var translated by remember { mutableStateOf<TranslateResult?>(null) }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.languages() }) { r -> languages = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.userLanguage(vm.uid!!, vm.token!!) }) { r ->
            r.getOrNull()?.let { (lang, mode) ->
                current = lang; preTranslate = mode == "pre"
                vm.rememberLanguage(lang)   // chrome follows the user
            }
        }
    }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        // 0.58.0. The console has offered this since 0.4.3 and the phones
        // never did: a key set there was used there, and the deployment's key
        // used here, on the same account.
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("set.key", vm.language), color = Jim.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("set.key.pitch", vm.language), color = Jim.T2, fontSize = 12.sp)
            labeledField(L10n.t("set.key.label", vm.language), llmKey,
                L10n.t("set.key.ph", vm.language)) { llmKey = it }
            SmallAction(L10n.t("set.save", vm.language)) { vm.rememberLlmKey(llmKey) }
        }

        // The deployment invite key. A published deployment gates account
        // creation behind one; this phone talks to whichever backend the
        // connection names, so it needs the same door the console has.
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("set.invite", vm.language), color = Jim.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("set.invite.lead", vm.language), color = Jim.T2, fontSize = 12.sp)
            labeledField(L10n.t("set.invite", vm.language), inviteKey,
                L10n.t("set.invite", vm.language)) { inviteKey = it }
            SmallAction(L10n.t("set.save", vm.language)) { vm.rememberSignupKey(inviteKey) }
        }

        Text(L10n.t("ov.language", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("ov.language.sub", vm.language),
            color = Jim.T2, fontSize = 12.sp)
        languages.chunked(3).forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                row.forEach { l ->
                    FilterChip(
                        selected = current == l.code,
                        onClick = {
                            vm.call({ ApiClient.setLanguage(vm.uid!!, vm.token!!, l.code) }) {
                                current = l.code
                                vm.rememberLanguage(l.code)
                            }
                        },
                        label = { Text(l.label, fontSize = 11.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Jim.BrandA,
                            selectedLabelColor = Color.White, labelColor = Jim.T2,
                        ),
                    )
                }
            }
        }
        val chosen = languages.firstOrNull { it.code == current }
        if (chosen != null && !chosen.safetyTranslated)
            Text("Safety steps stay in English for this language (never machine-mangled).",
                color = Jim.Amber, fontSize = 10.sp)
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(L10n.t("ov.pretranslate", vm.language),
                    color = Jim.Txt, fontSize = 13.sp)
                Text(L10n.t("ov.pretranslate.sub", vm.language),
                    color = Jim.T2, fontSize = 10.sp)
            }
            Switch(
                checked = preTranslate,
                onCheckedChange = { on ->
                    preTranslate = on
                    vm.call({ ApiClient.setLanguage(vm.uid!!, vm.token!!, current,
                        if (on) "pre" else "on_demand") }) { }
                },
                colors = SwitchDefaults.colors(checkedTrackColor = Jim.Green),
            )
        }
        HorizontalDivider(color = Jim.Line)
        Text(L10n.t("ov.translate", vm.language),
            color = Jim.Txt, fontSize = 13.sp, fontWeight = FontWeight.Bold)
        labeledField("", translateInput,
            L10n.t("ov.translate.placeholder", vm.language)) { translateInput = it }
        RobotAction(L10n.t("ov.translate.go", vm.language)) {
            if (translateInput.isNotBlank() && current != "en") {
                vm.call({ ApiClient.translate(vm.uid!!, vm.token!!, translateInput) }) { r ->
                    translated = r.getOrNull()
                }
            }
        }
        translated?.let { t ->
            Text(t.translation, color = Jim.Txt, fontSize = 13.sp,
                modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(9.dp))
                    .background(Jim.ScrBot).padding(10.dp))
            Text(L10n.t("ov.engine", vm.language).replace("{engine}", t.engine)
                 + (t.note?.let { n -> " — $n" } ?: ""),
                color = Jim.T3, fontSize = 10.sp)
        }
    }
}

// ---- Help us improve — product feedback (open to anyone) ----

/**
 * The five kinds of feedback, in the reader's language.
 *
 * A `when` rather than a key built from the API value, for the reason the
 * sensitivity dial has one: a key assembled at runtime is a key no guard can
 * see being asked for, and the dead-key check would call all five rows dead.
 */
private fun feedbackCategory(kind: String, lang: String): String = when (kind) {
    "idea" -> L10n.t("ov.fb.cat.idea", lang)
    "improvement" -> L10n.t("ov.fb.cat.improvement", lang)
    "bug" -> L10n.t("ov.fb.cat.bug", lang)
    "praise" -> L10n.t("ov.fb.cat.praise", lang)
    else -> L10n.t("ov.fb.cat.other", lang)
}

/** Ability is not a gate: the accessibility report door. Three questions,
 *  none a diagnosis, sent with no token — the person this card exists for
 *  may be the person the enrollment shut out. The reviewer row reads them
 *  back with the deployment's own token, never a user's. */
@Composable
fun AccessCard(vm: GuardianViewModel) {
    var doing by remember { mutableStateOf("") }
    var wall by remember { mutableStateOf("") }
    var help by remember { mutableStateOf("") }
    var thanks by remember { mutableStateOf<String?>(null) }
    var reviewer by remember { mutableStateOf("") }
    var reports by remember { mutableStateOf<List<AccessReportRow>?>(null) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.acc", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.acc.lead", vm.language), color = Jim.T2, fontSize = 12.sp)
        // The per-need statement the console makes, not just its form.
        Text(L10n.t("ns.acc.needs.title", vm.language), color = Jim.Txt,
            fontSize = 13.sp, fontWeight = FontWeight.Bold)
        listOf("blind", "deaf", "mute", "motor", "cognitive",
            "dyslexia", "motion").forEach { need ->
            Text("• " + L10n.t("ns.acc.needs.$need", vm.language),
                color = Jim.T2, fontSize = 12.sp)
        }
        Text(L10n.t("ns.acc.needs.more", vm.language), color = Jim.T2,
            fontSize = 12.sp, fontStyle = FontStyle.Italic)
        labeledField("", doing, L10n.t("ns.acc.doing.ph", vm.language)) { doing = it }
        labeledField("", wall, L10n.t("ns.acc.wall.ph", vm.language)) { wall = it }
        labeledField("", help, L10n.t("ns.acc.help.ph", vm.language)) { help = it }
        BrandButton(L10n.t("ns.acc.send", vm.language),
            enabled = doing.isNotBlank() && wall.isNotBlank()) {
            vm.call({ ApiClient.sendAccessReport(doing.trim(), wall.trim(),
                help.trim(), vm.language) }) {
                thanks = L10n.t("ns.acc.sent", vm.language)
                doing = ""; wall = ""; help = ""
            }
        }
        thanks?.let { Text(it, color = Jim.Green, fontSize = 12.sp) }
        labeledField("", reviewer, L10n.t("ns.acc.token.ph", vm.language)) { reviewer = it }
        BrandButton(L10n.t("ns.acc.load", vm.language)) {
            vm.call({ ApiClient.accessReports(reviewer.trim()) }) { r ->
                reports = r.getOrNull()
            }
        }
        reports?.let { rs ->
            if (rs.isEmpty())
                Text(L10n.t("ns.acc.none", vm.language), color = Jim.T3, fontSize = 11.sp)
            else rs.take(6).forEach { r ->
                Text(r.doing, color = Jim.Txt, fontSize = 12.sp,
                    fontWeight = FontWeight.Bold)
                Text(r.wall, color = Jim.T2, fontSize = 11.sp)
                r.help?.let { h -> Text(h, color = Jim.T2, fontSize = 11.sp) }
                Text("${r.lang} · ${r.createdAt}", color = Jim.T3, fontSize = 10.sp)
            }
        }
    }
}

@Composable
fun ImproveCard(vm: GuardianViewModel) {
    val categories = listOf("idea", "improvement", "bug", "praise", "other")
    var category by remember { mutableStateOf("idea") }
    var message by remember { mutableStateOf("") }
    var rating by remember { mutableIntStateOf(0) }
    var state by remember { mutableStateOf<ImproveState?>(null) }
    var thanks by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.improvements(vm.token) }) { r -> state = r.getOrNull() }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ov.fb", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("ov.fb.sub", vm.language),
            color = Jim.T2, fontSize = 12.sp)
        categories.chunked(3).forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                row.forEach { c ->
                    FilterChip(
                        selected = category == c,
                        onClick = { category = c },
                        label = { Text(feedbackCategory(c, vm.language), fontSize = 11.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Jim.BrandA,
                            selectedLabelColor = Color.White, labelColor = Jim.T2,
                        ),
                    )
                }
            }
        }
        labeledField("", message, L10n.t("ov.fb.placeholder", vm.language)) { message = it }
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(L10n.t("ov.fb.rating", vm.language), color = Jim.T2, fontSize = 12.sp)
            (1..5).forEach { n ->
                Text(if (n <= rating) "★" else "☆",
                    color = if (n <= rating) Jim.Amber else Jim.T3, fontSize = 20.sp,
                    modifier = Modifier.clickable { rating = if (rating == n) 0 else n })
            }
        }
        BrandButton(L10n.t("ov.fb.send", vm.language), enabled = message.isNotBlank()) {
            vm.call({
                ApiClient.submitImprovement(vm.token, category, message.trim(),
                    if (rating == 0) null else rating)
            }) {
                thanks = L10n.t("ov.fb.thanks", vm.language)
                message = ""; rating = 0; reload()
            }
        }
        thanks?.let { Text(it, color = Jim.Green, fontSize = 12.sp) }
        state?.takeIf { it.total > 0 }?.let { st ->
            HorizontalDivider(color = Jim.Line)
            Text(L10n.t("ov.fb.sofar", vm.language) + " " + categories.mapNotNull { c ->
                st.tally[c]?.takeIf { it > 0 }?.let { "$it $c" }
            }.joinToString(" · "), color = Jim.T3, fontSize = 10.sp)
            if (st.mine.isNotEmpty()) {
                Text(L10n.t("ov.fb.yours", vm.language), color = Jim.Txt, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                st.mine.take(4).forEach { f ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("[${f.category}] ${f.message}", color = Jim.T2, fontSize = 10.sp,
                            maxLines = 1, modifier = Modifier.weight(1f))
                        Text(f.status, color = Jim.BrandA, fontSize = 10.sp)
                    }
                }
            }
        }
    }
}

// ---- Medical ID (first-responder card + QR) ----

@Composable
private fun MedicalPanel(vm: GuardianViewModel) {
    var issued by remember { mutableStateOf<MedicalCardIssued?>(null) }
    var card by remember { mutableStateOf<MedicalCard?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("mid", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("mid.sub", vm.language),
                color = Jim.T2, fontSize = 12.sp)
            BrandButton(L10n.t(if (issued == null) "mid.issue" else "mid.rotate", vm.language),
                        busy = busy) {
                busy = true; error = null
                vm.call({
                    val r = ApiClient.issueMedicalCard(vm.uid!!, vm.token!!)
                    r to ApiClient.medicalCard(r.token)
                }) { res ->
                    busy = false
                    res.onSuccess { (i, c) -> issued = i; card = c }
                       .onFailure { error = it.message }
                }
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 13.sp) }
        issued?.let { i ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("mid.issued", vm.language), color = Jim.Green, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(L10n.t("mid.print", vm.language), color = Jim.T2, fontSize = 12.sp)
                Text(i.qrSvgUrl, color = Jim.T2, fontSize = 11.sp)
                card?.let { c ->
                    HorizontalDivider(color = Jim.Line)
                    Text(L10n.t("mid.responder", vm.language), color = Jim.Txt, fontSize = 14.sp,
                        fontWeight = FontWeight.Bold)
                    medRow(L10n.t("med.name", vm.language), c.name ?: "—")
                    medRow(L10n.t("med.age", vm.language), c.age?.toString() ?: "—")
                    medRow(L10n.t("med.hr", vm.language), c.restingHr?.let { "$it bpm" } ?: "—")
                    medRow(L10n.t("med.conditions", vm.language),
                        if (c.conditions.isEmpty()) "none declared" else c.conditions.joinToString(", "))
                    if (c.contactName != null || c.contactPhone != null)
                        medRow(L10n.t("med.contact", vm.language), "${c.contactName ?: "—"} · ${c.contactPhone ?: "—"}")
                }
                TextButton(onClick = {
                    vm.call({ ApiClient.revokeMedicalCard(vm.uid!!, vm.token!!) }) {
                        issued = null; card = null
                    }
                }) { Text(L10n.t("mid.revoke", vm.language), color = Jim.Red, fontSize = 13.sp) }
            }
        }
    }
}

@Composable
private fun medRow(k: String, v: String) {
    Row(Modifier.fillMaxWidth()) {
        Text(k, color = Jim.T2, fontSize = 12.sp, modifier = Modifier.width(90.dp))
        Text(v, color = Jim.Txt, fontSize = 12.sp)
    }
}

// ---- Care: Monitor, Check-in, Coach behind one tab ----

@Composable
fun CareScreen(vm: GuardianViewModel) {
    var tab by remember { mutableIntStateOf(0) }
    val tabs = listOf(
        L10n.t("tab.monitor", vm.language),
        L10n.t("tab.checkin", vm.language),
        L10n.t("tab.coach", vm.language),
        L10n.t("presence.tab", vm.language),
        L10n.t("tab.family", vm.language),
    )
    Column(Modifier.fillMaxSize()) {
        TabRow(
            selectedTabIndex = tab, containerColor = Jim.Card, contentColor = Jim.BrandA,
            modifier = Modifier.padding(horizontal = 20.dp).padding(top = 12.dp),
        ) {
            tabs.forEachIndexed { i, t ->
                Tab(selected = tab == i, onClick = { tab = i },
                    text = { Text(t, fontSize = 13.sp) })
            }
        }
        when (tab) {
            0 -> MonitorScreen(vm)
            1 -> CheckinScreen(vm)
            2 -> CoachScreen(vm)
            // The coach answers; the presence speaks first.
            3 -> PresencePanel(vm)
            else -> FamilyPanel(vm)
        }
    }
}

// ---- the presence: the coach that speaks first ----

/**
 * What it noticed, unprompted — and, above that, what it will not be.
 *
 * The order is deliberate: the refusals are rendered before any warm line,
 * because a guardian that is charming before it is honest has the order
 * wrong, and because this product enrols children whose guardians should be
 * able to read that without scrolling for it.
 *
 * Nothing here decides anything. Whether it speaks, about what and why are
 * the backend's, read from six areas of this person's own history with no
 * model and no second call out.
 */
@Composable
private fun PresencePanel(vm: GuardianViewModel) {
    var who by remember { mutableStateOf<PresenceWho?>(null) }
    var beats by remember { mutableStateOf<List<PresenceBeat>>(emptyList()) }
    var base by remember { mutableStateOf<PresenceBaseline?>(null) }
    var surfaces by remember { mutableStateOf<PresenceSurfaces?>(null) }
    var reach by remember { mutableStateOf<List<String>>(emptyList()) }
    var grew by remember { mutableStateOf<PresenceGrowth?>(null) }
    var carry by remember { mutableStateOf<PresenceBearingView?>(null) }
    var aloud by remember { mutableStateOf<PresenceSpoken?>(null) }
    var spoken by remember { mutableStateOf<Map<String, String>>(emptyMap()) }

    LaunchedEffect(Unit) {
        vm.call({ ApiClient.presenceWho() }) { who = it.getOrNull() }
        vm.call({ ApiClient.presenceDay(vm.uid!!, vm.token!!) }) {
            beats = it.getOrDefault(emptyList())
        }
        vm.call({ ApiClient.presenceBaseline(vm.uid!!, vm.token!!) }) { base = it.getOrNull() }
        vm.call({ ApiClient.presenceSurfaces(vm.uid!!, vm.token!!) }) { surfaces = it.getOrNull() }
        vm.call({ ApiClient.presenceGrowth(vm.uid!!, vm.token!!) }) { grew = it.getOrNull() }
        vm.call({ ApiClient.presenceBearing(vm.uid!!, vm.token!!) }) { carry = it.getOrNull() }
        // A missing tandem is not an error: 409 means the people live in QRME.
        vm.call({ ApiClient.presenceReach(vm.uid!!, vm.token!!) }) {
            reach = it.getOrDefault(emptyList())
        }
    }

    screenScroll {
        Text(L10n.t("presence.tab", vm.language), color = Jim.Txt,
            fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("presence.sub", vm.language), color = Jim.T2, fontSize = 13.sp)

        who?.let { w ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("presence.what", vm.language), color = Jim.Txt,
                    fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(w.says, color = Jim.Txt, fontSize = 14.sp)
                Text(L10n.t("presence.will.not", vm.language), color = Jim.T2, fontSize = 12.sp)
                w.boundaries.toSortedMap().forEach { (_, says) ->
                    Text(says, color = Jim.T3, fontSize = 10.sp)
                }
                Text(w.note, color = Jim.T3, fontSize = 10.sp)
            }
        }

        // The dial: companion by default, professional on request. A register
        // and never a capability, so the card that changes it also shows what
        // both bearings leave alone.
        carry?.let { c ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("presence.bearing", vm.language), color = Jim.Txt,
                    fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    c.choices.forEach { pick ->
                        TextButton(onClick = {
                            vm.call({ ApiClient.presenceSetBearing(vm.uid!!, vm.token!!, pick) }) { r ->
                                carry = r.getOrNull() ?: carry
                            }
                        }) {
                            // Spelled out rather than "presence.bearing.$pick":
                            // a key built from a variable is invisible to the
                            // guard that checks every translated row is read.
                            Text(if (pick == "professional")
                                    L10n.t("presence.bearing.professional", vm.language)
                                 else L10n.t("presence.bearing.companion", vm.language),
                                color = if (pick == c.bearing) Jim.BrandA else Jim.T2,
                                fontSize = 12.sp)
                        }
                    }
                }
                Text(c.says, color = Jim.T3, fontSize = 10.sp)
                Text(L10n.t("presence.bearing.same", vm.language), color = Jim.T2, fontSize = 10.sp)
                c.unchanged.forEach { line -> Text(line, color = Jim.T3, fontSize = 10.sp) }
                Text(c.note, color = Jim.T3, fontSize = 10.sp)
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("presence.today", vm.language), color = Jim.Txt,
                fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("presence.offline", vm.language), color = Jim.T3, fontSize = 10.sp)
            beats.forEach { b ->
                Text(b.slot, color = Jim.BrandA, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                Text(spoken[b.slot] ?: b.english, color = Jim.Txt, fontSize = 14.sp)
                // Why it said this.
                b.because.forEach { why -> Text(why, color = Jim.T3, fontSize = 10.sp) }
                if (b.speak) {
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        TextButton(onClick = {
                            // `/day` is the plan; asking for the beat is what
                            // counts as having been told.
                            vm.call({ ApiClient.presenceBeat(vm.uid!!, vm.token!!, b.slot) }) { r ->
                                r.getOrNull()?.let { spoken = spoken + (b.slot to (it.deepenedLine ?: it.english)) }
                            }
                        }) { Text(L10n.t("presence.tab", vm.language), color = Jim.T2, fontSize = 12.sp) }
                        TextButton(onClick = {
                            vm.call({ ApiClient.presenceDeepen(vm.uid!!, vm.token!!, b.slot) }) { r ->
                                r.getOrNull()?.let { spoken = spoken + (b.slot to (it.deepenedLine ?: it.english)) }
                            }
                        }) { Text(L10n.t("presence.deepen", vm.language), color = Jim.BrandA, fontSize = 12.sp) }
                        // Say it — and let the room decide. The verdict is
                        // the server's: letting a client work out whether the
                        // room is safe is how the picker became a caption.
                        TextButton(onClick = {
                            vm.call({ ApiClient.presenceSay(vm.uid!!, vm.token!!, b.slot) }) { r ->
                                aloud = r.getOrNull() ?: aloud
                            }
                        }) { Text(L10n.t("presence.aloud", vm.language), color = Jim.T2, fontSize = 12.sp) }
                    }
                }
            }
        }

        // What the room did with it. Its own card: a withheld line is a
        // thing that happened, not a missing button.
        aloud?.let { a ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(a.speaksOn, color = Jim.Txt, fontSize = 16.sp,
                    fontWeight = FontWeight.Bold)
                Text(a.english, color = Jim.Txt, fontSize = 14.sp)
                Text(if (a.spoken) L10n.t("presence.aloud.said", vm.language)
                     else if (a.hasAudio) L10n.t("presence.aloud.held", vm.language)
                     else L10n.t("presence.aloud.nosound", vm.language),
                    color = Jim.T2, fontSize = 11.sp)
                a.withheld.forEach { h -> Text(h, color = Jim.T3, fontSize = 10.sp) }
                if (a.whyNotAloud.isNotBlank()) {
                    Text(a.whyNotAloud, color = Jim.T3, fontSize = 10.sp)
                }
            }
        }

        TextButton(onClick = {
            vm.call({ ApiClient.presenceDue(vm.uid!!, vm.token!!) }) { r ->
                aloud = r.getOrNull() ?: aloud
            }
        }) { Text(L10n.t("presence.hands.free", vm.language), color = Jim.BrandA, fontSize = 12.sp) }

        base?.let { bl ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("presence.baseline", vm.language), color = Jim.Txt,
                    fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text("" + bl.known + " / " + bl.of, color = Jim.T3, fontSize = 10.sp)
                bl.areas.forEach { a ->
                    Row {
                        Text(a.area, color = Jim.Txt, fontSize = 12.sp, modifier = Modifier.weight(1f))
                        Text(a.standing, color = Jim.T3, fontSize = 10.sp)
                    }
                }
            }
        }

        surfaces?.let { s ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("presence.surfaces", vm.language), color = Jim.Txt,
                    fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(s.rule, color = Jim.T3, fontSize = 10.sp)
                s.surfaces.forEach { row ->
                    Row {
                        TextButton(onClick = {
                            vm.call({ ApiClient.presenceChooseSurface(vm.uid!!, vm.token!!, row.surface) }) { r ->
                                surfaces = r.getOrNull() ?: surfaces
                            }
                        }, modifier = Modifier.weight(1f)) {
                            Text(row.surface, color = if (row.chosen) Jim.BrandA else Jim.T2, fontSize = 12.sp)
                        }
                        Text(if (row.readsHealthAloud)
                                L10n.t("presence.aloud", vm.language)
                             else L10n.t("presence.shown", vm.language),
                            color = Jim.T3, fontSize = 10.sp)
                    }
                }
            }
        }

        if (reach.isNotEmpty()) {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("presence.reach", vm.language), color = Jim.Txt,
                    fontSize = 16.sp, fontWeight = FontWeight.Bold)
                reach.forEach { name -> Text(name, color = Jim.Txt, fontSize = 12.sp) }
            }
        }

        grew?.let { g ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("presence.growth", vm.language), color = Jim.Txt,
                    fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text("" + g.beatsSpoken + " · " + g.areasSeen + " / " + g.of,
                    color = Jim.T3, fontSize = 10.sp)
                // The honest half, in its own words.
                Text(g.aboutMyself, color = Jim.T3, fontSize = 10.sp)
            }
        }
    }
}

// ---- Family: a parent sets up and watches over a child's account ----

@Composable
private fun FamilyPanel(vm: GuardianViewModel) {
    var name by remember { mutableStateOf("") }
    var birthdate by remember { mutableStateOf("") }
    var phone by remember { mutableStateOf("") }
    var created by remember { mutableStateOf<ChildCreated?>(null) }
    var kids by remember { mutableStateOf<List<ChildSummary>>(emptyList()) }
    var overview by remember { mutableStateOf<ChildOverview?>(null) }
    var face by remember { mutableStateOf<GuardianFace?>(null) }
    var openKid by remember { mutableStateOf<String?>(null) }
    var pauseOn by remember { mutableStateOf(false) }
    var quietStart by remember { mutableStateOf("") }
    var quietEnd by remember { mutableStateOf("") }
    var controlsNote by remember { mutableStateOf<String?>(null) }
    var unlinking by remember { mutableStateOf<String?>(null) }
    var unlinkNote by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.children(vm.uid!!, vm.token!!) }) { r ->
            kids = r.getOrDefault(emptyList())
        }
        vm.call({ ApiClient.guardianWatch(vm.uid!!, vm.token!!) }) { r ->
            face = r.getOrNull()
        }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)) {
        face?.takeIf { it.children.isNotEmpty() }?.let { f ->
            Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp))
                    .background(Jim.Card).padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(L10n.t("fam", vm.language), color = Jim.Txt, fontSize = 14.sp,
                        fontWeight = FontWeight.Bold)
                    if (f.haptic == "alert")
                        Text(L10n.t("fam.tapped", vm.language), color = Jim.Red, fontSize = 11.sp,
                            fontWeight = FontWeight.Bold)
                }
                f.children.forEach { c ->
                    Row(Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically) {
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp),
                            verticalAlignment = Alignment.CenterVertically) {
                            Text("●", fontSize = 11.sp, color = when (c.light) {
                                "green" -> Jim.Green
                                "orange" -> Jim.Amber
                                "red" -> Jim.Red
                                else -> Jim.T3
                            })
                            Text(c.displayName, color = Jim.Txt, fontSize = 12.sp,
                                fontWeight = FontWeight.Bold)
                            if (c.critical24h > 0)
                                Text(L10n.t("fam.st.critical", vm.language), color = Jim.Red, fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold)
                            else if (c.escalations24h > 0)
                                Text(L10n.t("fam.st.escalated", vm.language), color = Jim.Amber, fontSize = 10.sp)
                        }
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            if (c.paused)
                                Text(L10n.t("fam.st.paused", vm.language), color = Jim.T3, fontSize = 10.sp)
                            c.quietHours?.let {
                                Text("🌙 $it", color = Jim.T3, fontSize = 10.sp)
                            }
                        }
                    }
                }
            }
        }

        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("fam.setup", vm.language), color = Jim.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("fam.enrol", vm.language), color = Jim.T2, fontSize = 12.sp)
            OutlinedTextField(value = name, onValueChange = { name = it },
                label = { Text(L10n.t("fam.child.name", vm.language)) },
                modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = birthdate, onValueChange = { birthdate = it },
                label = { Text(L10n.t("fam.child.dob", vm.language)) },
                modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = phone, onValueChange = { phone = it },
                label = { Text(L10n.t("fam.child.phone", vm.language)) },
                modifier = Modifier.fillMaxWidth())
            Button(onClick = {
                error = null
                vm.call({ ApiClient.enrollChild(vm.uid!!, vm.token!!,
                    name.trim(), birthdate.trim(), phone.trim()) }) { r ->
                    r.onSuccess { created = it; name = ""; birthdate = ""; phone = "" }
                        .onFailure { error = it.message }
                    reload()
                }
            }, enabled = name.isNotBlank() && birthdate.isNotBlank(),
                modifier = Modifier.fillMaxWidth()) {
                Text(L10n.t("fam.create", vm.language))
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
        created?.let { c ->
            Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
                Text(L10n.t("fam.created", vm.language), color = Jim.Green, fontSize = 14.sp,
                    fontWeight = FontWeight.Bold)
                Text(L10n.t("fam.oversight", vm.language)
                        .replace("{scope}",
                            if (c.oversight == "full")
                                L10n.t("fam.scope.full", vm.language)
                            else L10n.t("fam.scope.alerts", vm.language)) +
                     " · " + L10n.t("fam.sens", vm.language)
                        .replace("{level}",
                            sensitivityLabel(c.sensitivity ?: "cautious", vm.language)),
                    color = Jim.T2, fontSize = 12.sp)
                Text(L10n.t("fam.token", vm.language),
                    color = Jim.Amber, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                Text(c.childToken, color = Jim.Txt, fontSize = 10.sp)
            }
        }
        kids.forEach { kid ->
            Row(Modifier.fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp)).background(Jim.Card)
                    .clickable {
                        openKid = kid.childId
                        controlsNote = null
                        face?.children?.firstOrNull { it.childId == kid.childId }
                            ?.let { c ->
                                pauseOn = c.paused
                                val parts = (c.quietHours ?: "").split("–")
                                quietStart = parts.getOrNull(0) ?: ""
                                quietEnd = parts.getOrNull(1) ?: ""
                            }
                        vm.call({ ApiClient.childOverview(vm.uid!!,
                            kid.childId, vm.token!!) }) { r ->
                            overview = r.getOrNull()
                        }
                    }
                    .padding(12.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically) {
                Column {
                    Text("${kid.displayName} · ${kid.age}", color = Jim.Txt,
                        fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Text(when (kid.oversight) {
                        "full" -> L10n.t("fam.tier.full", vm.language)
                        "alerts_only" -> L10n.t("fam.tier.alerts", vm.language)
                        else -> L10n.t("fam.tier.ended", vm.language)
                    }, color = Jim.T2, fontSize = 11.sp)
                }
                Text("●", fontSize = 12.sp,
                    color = when (kid.oversight) {
                        "full" -> Jim.Green
                        "alerts_only" -> Jim.Amber
                        else -> Jim.T3
                    })
            }
        }
        openKid?.let { cid ->
            Column(Modifier.fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp)).background(Jim.Card)
                    .padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("fam.controls", vm.language), color = Jim.Txt, fontSize = 14.sp,
                    fontWeight = FontWeight.Bold)
                Text(L10n.t("fam.pause.sub", vm.language), color = Jim.T3, fontSize = 10.sp)
                Row(Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically) {
                    Text(L10n.t("fam.pause", vm.language), color = Jim.Txt, fontSize = 12.sp)
                    Switch(checked = pauseOn, onCheckedChange = { pauseOn = it })
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(value = quietStart,
                        onValueChange = { quietStart = it },
                        label = { Text(L10n.t("fam.quiet.start", vm.language)) },
                        modifier = Modifier.weight(1f))
                    OutlinedTextField(value = quietEnd,
                        onValueChange = { quietEnd = it },
                        label = { Text(L10n.t("fam.quiet.end", vm.language)) },
                        modifier = Modifier.weight(1f))
                }
                SmallAction(L10n.t("fam.apply", vm.language)) {
                    vm.call({ ApiClient.setFamilyControls(vm.uid!!, cid,
                        vm.token!!, pauseOn,
                        quietStart.trim().ifEmpty { null },
                        quietEnd.trim().ifEmpty { null }) }) { r ->
                        controlsNote = r.getOrNull()
                        reload()
                    }
                }
                controlsNote?.let {
                    Text(it, color = Jim.Green, fontSize = 10.sp)
                }

                // Ending the link. This screen could begin one and not end
                // one — iOS gained the control when `unlinkChild` was wired
                // there, and the route audit has listed
                // `DELETE /guardians/{guardian_id}/children/{child_id}` in
                // android_doorless.txt ever since.
                //
                // A guardian link is a standing relationship: one adult able
                // to see another person's events, light and escalations. It
                // outlives the reason for it. The surface that creates it has
                // to be able to end it, or the person who set it up has to
                // find a desktop — and until this round the desktop could not
                // do it either.
                HorizontalDivider(color = Jim.Line)
                Text(L10n.t("fam.unlink.this", vm.language), color = Jim.Red,
                    fontSize = 12.sp, fontWeight = FontWeight.Bold,
                    modifier = Modifier.clickable { unlinking = cid })
                unlinkNote?.let {
                    Text(it, color = Jim.T2, fontSize = 10.sp)
                }
            }
        }

        // Attached outside the controls card, like the iOS dialog: a dialog
        // owned by a row is dismissed with the row when the list reloads,
        // which is exactly when this one fires.
        unlinking?.let { cid ->
            AlertDialog(
                onDismissRequest = { unlinking = null },
                title = { Text(L10n.t("fam.unlink.ask", vm.language)) },
                text = { Text(L10n.t("fam.theirs", vm.language)) },
                confirmButton = {
                    TextButton(onClick = {
                        unlinking = null
                        vm.call({ ApiClient.unlinkChild(vm.uid!!, cid, vm.token!!) }) { r ->
                            r.onSuccess {
                                openKid = null
                                unlinkNote = L10n.t("fam.unlinked.note", vm.language)
                            }.onFailure { error = it.message }
                            reload()
                        }
                    }) { Text(L10n.t("fam.unlink", vm.language), color = Jim.Red) }
                },
                dismissButton = {
                    TextButton(onClick = { unlinking = null }) {
                        Text(L10n.t("fam.keep", vm.language))
                    }
                },
            )
        }
        overview?.let { o ->
            Column(Modifier.fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp)).background(Jim.Card)
                    .padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(3.dp)) {
                if (o.note != null) {
                    Text(L10n.t("fam.unlinked", vm.language), color = Jim.Txt, fontSize = 14.sp,
                        fontWeight = FontWeight.Bold)
                    Text(o.note, color = Jim.T2, fontSize = 11.sp)
                } else {
                    Text(o.displayName ?: L10n.t("fam.child.generic", vm.language), color = Jim.Txt,
                        fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    o.privacyNote?.let {
                        Text("🔒 $it", color = Jim.Amber, fontSize = 11.sp)
                    }
                    if (o.criticalEvents > 0)
                        Text(L10n.t("fam.critical", vm.language)
                                .replace("{n}", "${o.criticalEvents}"),
                            color = Jim.Red, fontSize = 12.sp,
                            fontWeight = FontWeight.Bold)
                    o.events.forEach { e ->
                        Text("${e.type}${e.condition?.let { " · $it" } ?: ""}" +
                             (e.severity?.let { " · ${it.uppercase()}" } ?: ""),
                            color = Jim.T2, fontSize = 11.sp)
                    }
                    if (o.events.isEmpty())
                        Text(L10n.t("fam.quiet", vm.language),
                            color = Jim.T2, fontSize = 11.sp)
                }
            }
        }

        // The care team: the household's coordination layer, linked from
        // the same screen that watches over its members.
        CareTeamPanel(vm)
    }
}

// ---- Connect: data sources, social platforms, connected apps ----

@Composable
fun ConnectScreen(vm: GuardianViewModel) {
    var tab by remember { mutableIntStateOf(0) }
    val tabs = listOf(
        L10n.t("jcon.tab.sources", vm.language),
        L10n.t("jcon.tab.social", vm.language),
        L10n.t("jcon.tab.apps", vm.language),
        L10n.t("jcon.community", vm.language),
        L10n.t("jcon.tab.me", vm.language),
    )
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)) {
        TabRow(selectedTabIndex = tab, containerColor = Jim.Card, contentColor = Jim.BrandA) {
            tabs.forEachIndexed { i, t ->
                Tab(selected = tab == i, onClick = { tab = i },
                    text = { Text(t, fontSize = 13.sp) })
            }
        }
        when (tab) {
            // Channel 2 sits with the sources: the lent microphone is a
            // way in for the world's sound, consented the same.
            0 -> { SourcesPanel(vm); MicPanel(vm) }
            1 -> SocialPanel(vm)
            2 -> AppsPanel(vm)
            3 -> CommunityPanel(vm)
            // The synthetic self shipped as a composable nothing called. It
            // had its strings in ten languages and a guard checking they were
            // there.
            //
            //     asked     does the screen have its wording
            //     mattered  does anything open the screen
            else -> SelfProfileScreen(ApiClient, vm.uid!!, vm.token!!, vm.language)
        }
    }
}

@Composable
private fun SourcesPanel(vm: GuardianViewModel) {
    var rows by remember { mutableStateOf<List<SourceRow>>(emptyList()) }
    fun reload() { vm.call({ ApiClient.sources(vm.uid!!, vm.token!!) }) { r -> rows = r.getOrDefault(emptyList()) } }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(L10n.t("jcon.sources", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("jcon.sources.sub", vm.language),
            color = Jim.T2, fontSize = 12.sp)
        rows.forEach { row ->
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(pretty(row.source), color = Jim.Txt, fontSize = 14.sp,
                    modifier = Modifier.weight(1f))
                Switch(
                    checked = row.consented,
                    onCheckedChange = { on ->
                        vm.call({ ApiClient.setSource(vm.uid!!, vm.token!!, row.source, on) }) { reload() }
                    },
                    colors = SwitchDefaults.colors(checkedTrackColor = Jim.Green),
                )
            }
        }
    }
}

@Composable
private fun SocialPanel(vm: GuardianViewModel) {
    val platforms = listOf("instagram", "x", "tiktok", "facebook", "linkedin", "youtube",
        "whatsapp", "discord", "twitch", "pinterest", "snapchat", "mastodon")
    var platform by remember { mutableStateOf(platforms.first()) }
    var handle by remember { mutableStateOf("") }
    var conns by remember { mutableStateOf<List<SocialConn>>(emptyList()) }
    var status by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    fun reload() { vm.call({ ApiClient.socialConnections(vm.uid!!, vm.token!!) }) { r -> conns = r.getOrDefault(emptyList()) } }
    LaunchedEffect(Unit) { reload() }

    fun connect(direction: String) {
        error = null; status = null
        vm.call({ ApiClient.socialConnect(vm.uid!!, vm.token!!, platform, direction, handle) }) { r ->
            r.onSuccess { handle = ""; reload() }.onFailure { error = it.message }
        }
    }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(L10n.t("jcon.social", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            FlowRowChips(platforms, platform) { platform = it }
            labeledField(L10n.t("jcon.handle", vm.language), handle, L10n.t("care.handle.ph", vm.language)) { handle = it }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                smallAction(L10n.t("jcon.connect.collect", vm.language)) { connect("collect") }
                smallAction(L10n.t("jcon.connect.publish", vm.language)) { connect("publish") }
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 13.sp) }
        status?.let { Text(it, color = Jim.Green, fontSize = 12.sp) }
        conns.forEach { c ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("${pretty(c.platform)} · ${c.direction}", color = Jim.Txt,
                        fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    c.handle?.let { Text("@$it", color = Jim.T3, fontSize = 12.sp) }
                }
                if (c.direction == "collect") {
                    smallAction(L10n.t("jcon.collect.sample", vm.language)) {
                        vm.call({ ApiClient.socialCollect(c.id, vm.token!!,
                            "sample post from ${c.platform}") }) { r ->
                            r.onSuccess {
                                status = L10n.t("jcon.collected.one", vm.language)
                                    .replace("{platform}", pretty(c.platform))
                            }
                                .onFailure { error = it.message }
                        }
                    }
                } else {
                    smallAction(L10n.t("jcon.publish.update", vm.language)) {
                        vm.call({ ApiClient.socialPublish(c.id, vm.token!!,
                            "A check-in from my Guardian.") }) { r ->
                            r.onSuccess {
                                status = L10n.t("jcon.published", vm.language)
                                    .replace("{platform}", pretty(c.platform))
                            }
                                .onFailure { error = it.message }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun AppsPanel(vm: GuardianViewModel) {
    var catalog by remember { mutableStateOf<List<CatalogApp>>(emptyList()) }
    var conns by remember { mutableStateOf<List<AppConn>>(emptyList()) }
    var status by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    fun reload() {
        vm.call({ ApiClient.appsCatalog() }) { r -> catalog = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.appConnections(vm.uid!!, vm.token!!) }) { r -> conns = r.getOrDefault(emptyList()) }
    }
    LaunchedEffect(Unit) { reload() }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("jcon.apps", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("jcon.apps.sub", vm.language),
                color = Jim.T2, fontSize = 12.sp)
            catalog.take(10).forEach { entry ->
                Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) {
                        Text(entry.label, color = Jim.Txt, fontSize = 14.sp)
                        Text(entry.provider, color = Jim.T3, fontSize = 11.sp)
                    }
                    TextButton(onClick = {
                        error = null
                        vm.call({ ApiClient.appConnect(vm.uid!!, vm.token!!,
                            entry.provider, entry.app) }) { r ->
                            r.onSuccess {
                                status = L10n.t("jcon.connected", vm.language)
                                    .replace("{provider}", entry.provider)
                                    .replace("{app}", entry.app)
                                reload()
                            }
                                .onFailure { error = it.message }
                        }
                    }) { Text(L10n.t("jcon.connect", vm.language), color = Jim.BrandA,
                                fontSize = 13.sp, fontWeight = FontWeight.Bold) }
                }
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 13.sp) }
        status?.let { Text(it, color = Jim.Green, fontSize = 12.sp) }
        conns.forEach { c ->
            Row(Modifier.card(), verticalAlignment = Alignment.CenterVertically) {
                Text("${c.provider} · ${c.app}", color = Jim.Txt, fontSize = 14.sp,
                    fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                TextButton(onClick = {
                    vm.call({ ApiClient.appCollect(c.id, vm.token!!,
                        "sample context from ${c.app}") }) { r ->
                        r.onSuccess {
                            status = L10n.t("jcon.collected.from", vm.language)
                                .replace("{app}", c.app)
                        }
                            .onFailure { error = it.message }
                    }
                }) { Text(L10n.t("jcon.collect", vm.language), color = Jim.BrandA,
                            fontSize = 13.sp, fontWeight = FontWeight.Bold) }
            }
        }
    }
}

@Composable
private fun smallAction(text: String, onClick: () -> Unit) {
    Box(
        Modifier.clip(RoundedCornerShape(50)).background(Jim.BrandA)
            .clickable { onClick() }
            .padding(horizontal = 12.dp, vertical = 8.dp),
    ) {
        Text(text, color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
    }
}

// ---- Community: the door out, and what stays behind it ----

/**
 * FIG. 2 boxes 222-226: interact with others, moderated storage, community
 * interaction, local events and forums in every language.
 *
 * None of that is built a second time here. It exists in QRME, with the
 * moderation, the rooms and the languages already in place, so this panel is a
 * door rather than a copy and says so in the same breath as it opens. The
 * posture is rendered from the server's own booleans instead of being retyped
 * as reassurance, so the screen cannot claim more than the bridge does.
 */
@Composable
private fun CommunityPanel(vm: GuardianViewModel) {
    val context = LocalContext.current
    var view by remember { mutableStateOf<CommunityView?>(null) }
    var opened by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        val uid = vm.uid ?: return
        val token = vm.token ?: return
        vm.call({ ApiClient.community(uid, token) }) { r ->
            r.fold({ view = it }, { error = it.message })
        }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("jcon.community", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        val v = view
        if (v == null) {
            Text(L10n.t("jcon.loading", vm.language), color = Jim.T3, fontSize = 12.sp)
        } else {
            Text(v.note, color = Jim.T2, fontSize = 12.sp)
            v.language?.let {
                Text(L10n.t("jcon.rooms.lang", vm.language).replace("{lang}", it),
                    color = Jim.T3, fontSize = 11.sp)
            }
        }
    }

    view?.let { v ->
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("jcon.notdo", vm.language), color = Jim.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            PostureRow(L10n.t("jcon.posture.mirror", vm.language),
                v.posture.mirroredHere)
            PostureRow(L10n.t("jcon.posture.post", vm.language),
                v.posture.postsOnYourBehalf)
            PostureRow(L10n.t("jcon.posture.health", vm.language),
                v.posture.healthDataShared)
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("jcon.rooms", vm.language), color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            if (v.rooms.isEmpty()) {
                Text(L10n.t("jcon.rooms.none", vm.language),
                    color = Jim.T3, fontSize = 12.sp)
            }
            v.rooms.forEach { room ->
                Row(Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween) {
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text(room.topic ?: room.id, color = Jim.Txt, fontSize = 13.sp)
                        Text(roomDetail(room, vm.language), color = Jim.T3, fontSize = 10.sp)
                    }
                    room.url?.let { url ->
                        SmallAction(L10n.t("jcon.open", vm.language)) {
                            val uid = vm.uid
                            val token = vm.token
                            if (uid != null && token != null) {
                                vm.call({ ApiClient.noteCommunityVisit(uid, token, room.id) }) { r ->
                                    r.fold({ opened = room.id }, { error = it.message })
                                }
                            }
                            context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
                        }
                    }
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("jcon.near", vm.language), color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            if (v.places.isEmpty()) {
                Text(L10n.t("jcon.places.none", vm.language), color = Jim.T3, fontSize = 12.sp)
            }
            v.places.forEach { place ->
                Row(Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(placeName(place), color = Jim.Txt, fontSize = 13.sp)
                    Text("${place.listings}", color = Jim.T2, fontSize = 12.sp)
                }
            }
        }
    }

    opened?.let {
        Text(L10n.t("jcon.noted", vm.language).replace("{room}", it),
            color = Jim.Green, fontSize = 12.sp)
    }
    error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
}

@Composable
private fun PostureRow(label: String, happens: Boolean) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(if (happens) "•" else "✓",
            color = if (happens) Jim.Amber else Jim.Green, fontSize = 12.sp)
        Text(label, color = Jim.T2, fontSize = 12.sp)
    }
}

private fun roomDetail(room: CommunityRoom, lang: String): String {
    val bits = mutableListOf<String>()
    room.channel?.let { bits.add(it) }
    if (room.participants > 0)
        bits.add(L10n.t("jcon.here", lang).replace("{n}", "${room.participants}"))
    return if (bits.isEmpty()) room.id else bits.joinToString(" · ")
}

/**
 * The three settings of the sensitivity dial, in the reader's language.
 *
 * A `when` rather than one lookup on a key built by concatenating the prefix
 * with the API value, which is shorter and wrong: a key assembled at runtime
 * is a key no guard can find, and the dead-key check would then report all
 * three rows as asked for by nobody.
 */
private fun sensitivityLabel(level: String, lang: String): String = when (level) {
    "cautious" -> L10n.t("cw.cautious", lang)
    "assertive" -> L10n.t("cw.assertive", lang)
    else -> L10n.t("cw.balanced", lang)
}

private fun placeName(place: CommunityPlace): String =
    if (place.region.isNullOrBlank()) place.locality
    else "${place.locality}, ${place.region}"

// ---- What JIM has learned about you (claim 11) ----

/**
 * The user-specific adaptation profile, in plain terms: counts off this user's
 * own history rather than a score, and a statement of where it came from —
 * nothing was sent to a model vendor to build it, and the sealed copy lives in
 * their own vault.
 */
@Composable
private fun AdaptationCard(vm: GuardianViewModel) {
    var profile by remember { mutableStateOf<AdaptationProfile?>(null) }
    var busy by remember { mutableStateOf(false) }

    fun reload() {
        val uid = vm.uid ?: return
        val token = vm.token ?: return
        vm.call({ ApiClient.adaptation(uid, token) }) { r -> profile = r.getOrNull() }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ov.learned", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        val p = profile
        if (p != null && p.built) {
            Text(L10n.t("ov.confidence", vm.language)
                    .replace("{pct}", "${(p.confidence * 100).roundToInt()}")
                    .replace("{n}", "${p.evidenceItems}"),
                color = Jim.T2, fontSize = 12.sp)
            p.whatHelps.entries.sortedBy { it.key }.forEach { (condition, tally) ->
                if (tally.answered > 0) {
                    Row(Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(condition.replace('_', ' '), color = Jim.Txt, fontSize = 14.sp)
                        Text(L10n.t("ov.helped", vm.language)
                                .replace("{n}", "${tally.helped}")
                                .replace("{total}", "${tally.answered}"),
                            color = if (tally.helped * 2 >= tally.answered) Jim.Green
                                    else Jim.Amber,
                            fontSize = 12.sp)
                    }
                }
            }
            p.tone?.let {
                Text(L10n.t("ov.tone", vm.language).replace("{tone}", it),
                    color = Jim.T3, fontSize = 11.sp)
            }
            p.occupation?.let {
                Text(L10n.t("ov.work", vm.language).replace("{job}", it),
                    color = Jim.T3, fontSize = 11.sp)
            }
            if (p.vaulted) {
                Text(L10n.t("ov.sealed", vm.language), color = Jim.Green, fontSize = 11.sp)
            }
            p.method?.let { Text(it, color = Jim.T3, fontSize = 10.sp) }
        } else {
            Text(p?.note ?: L10n.t("ov.adapt.none", vm.language),
                color = Jim.T2, fontSize = 12.sp)
        }
        SmallAction(if (busy) L10n.t("ov.rebuilding", vm.language)
                    else L10n.t("ov.rebuild", vm.language),
            enabled = !busy) {
            val uid = vm.uid ?: return@SmallAction
            val token = vm.token ?: return@SmallAction
            busy = true
            vm.call({ ApiClient.rebuildAdaptation(uid, token) }) { r ->
                busy = false
                profile = r.getOrNull() ?: profile
            }
        }
    }
}

/**
 * The offline fine-tune, on this phone.
 *
 * A separate card from the adaptation profile beside it, on purpose: that one
 * is a profile that conditions a prompt, this one is weights. One card doing
 * both is how a reader ends up unable to say which of the two they have.
 */
@Composable
private fun TrainedModelCard(vm: GuardianViewModel) {
    var ft by remember { mutableStateOf<Finetune?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(vm.uid) {
        val uid = vm.uid ?: return@LaunchedEffect
        val token = vm.token ?: return@LaunchedEffect
        // A 404 until something has been trained, which is the normal state.
        vm.call({ ApiClient.finetune(uid, token) }) { r -> ft = r.getOrNull() }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ov.ft", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("ov.ft.sub", vm.language), color = Jim.T2, fontSize = 12.sp)
        ft?.let { f ->
            Text(L10n.fill("ov.ft.from", vm.language,
                           mapOf("n" to f.examples.toString())),
                color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            // The server's own sentence, shown rather than paraphrased.
            Text(f.method, color = Jim.T3, fontSize = 10.sp)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(L10n.t("ov.ft.use", vm.language), color = Jim.Txt,
                    fontSize = 13.sp, modifier = Modifier.weight(1f))
                Switch(checked = f.active, onCheckedChange = { on ->
                    val uid = vm.uid ?: return@Switch
                    val token = vm.token ?: return@Switch
                    vm.call({ ApiClient.setFinetuneActive(uid, token, on) }) { r ->
                        r.onSuccess { ft = f.copy(active = on) }
                         .onFailure { error = it.message }
                    }
                })
            }
            Text(L10n.t("ov.ft.off", vm.language), color = Jim.T3, fontSize = 10.sp)
        } ?: Text(L10n.t("ov.ft.none", vm.language), color = Jim.T2, fontSize = 12.sp)
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
        SmallAction(L10n.t(if (busy) "ov.ft.training" else "ov.ft.train",
                           vm.language), enabled = !busy) {
            val uid = vm.uid ?: return@SmallAction
            val token = vm.token ?: return@SmallAction
            busy = true; error = null
            vm.call({ ApiClient.runFinetune(uid, token) }) { r ->
                busy = false
                r.onSuccess { ft = it }.onFailure { error = it.message }
            }
        }
    }
}

// ---- Your name here (spec [0031] / box 212) ----

/**
 * The anonymity posture as a tradeoff rather than a switch: what the choice
 * keeps and what it costs, so it reads as a decision and not a surprise.
 */
@Composable
private fun AnonymityCard(vm: GuardianViewModel) {
    var posture by remember { mutableStateOf<AnonymityPosture?>(null) }

    LaunchedEffect(Unit) {
        val uid = vm.uid
        val token = vm.token
        if (uid != null && token != null) {
            vm.call({ ApiClient.anonymity(uid, token) }) { r -> posture = r.getOrNull() }
        }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(L10n.t("ov.name", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        val p = posture
        if (p == null) {
            Text(L10n.t("ov.loading", vm.language), color = Jim.T3, fontSize = 12.sp)
        } else {
            Text(
                if (p.anonymous)
                    L10n.t("ov.name.pseudonym", vm.language).replace("{name}",
                        p.knownAs ?: L10n.t("ov.name.pseudonym.fallback", vm.language))
                else L10n.t("ov.name.own", vm.language),
                color = Jim.Txt, fontSize = 14.sp)
            p.keeps.forEach { Text("✓ $it", color = Jim.Green, fontSize = 12.sp) }
            p.costs.forEach { Text("• $it", color = Jim.Amber, fontSize = 12.sp) }
            if (p.costs.isEmpty() && p.anonymous) {
                Text(L10n.t("ov.legal", vm.language),
                    color = Jim.T3, fontSize = 11.sp)
            }
        }
    }
}

/**
 * The notice that has to be answered before anything leaves the device, and
 * the switch that turns it off afterwards.
 *
 * The sending half landed last round and answers AWAITING_NOTICE on every
 * launch, because there was no surface to answer it on. Safe to be wrong in
 * that direction, and still wrong: a mechanism nobody can reach is a
 * mechanism nobody chose.
 *
 * Two rules this card keeps:
 *
 *  * **Show the report, do not describe it.** A card that says "we collect
 *    anonymous diagnostics" asks somebody to take our word for it.
 *    `Problems.report` is the same function the sender posts, so what is on
 *    screen is the payload. A preview that could drift from the message would
 *    be worse than none, because it would look like a promise.
 *  * **No pre-ticked answer.** Neither button is the emphasised one. A dialog
 *    with a bright Yes and a grey No has made the choice already.
 */
@Composable
fun ProblemReportingCard(lang: String = "en") {
    var answered by remember { mutableStateOf(Problems.noticeAnswered()) }
    var sending by remember { mutableStateOf(Problems.sendingEnabled()) }
    var showing by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val owed = remember(showing, answered, sending) {
        val arr = Problems.report().optJSONArray("problems")
        (0 until (arr?.length() ?: 0)).mapNotNull { arr?.optJSONObject(it) }
    }

    Card(colors = CardDefaults.cardColors(containerColor = Jim.Card)) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("ns.pr", lang), style = MaterialTheme.typography.titleSmall)

            if (Problems.collectorUrl().isEmpty()) {
                // Not a failure and not a thing to hide: this build has no
                // address compiled in, so there is nothing to consent to.
                Text(L10n.t("ns.pr.nowhere", lang),
                     style = MaterialTheme.typography.bodySmall)
            } else if (!answered) {
                Text(L10n.t("ns.pr.explain", lang),
                     style = MaterialTheme.typography.bodySmall)
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedButton(onClick = {
                        Problems.answerNotice(true); answered = true; sending = true
                        // The first moment a send is permitted. Doing it now
                        // rather than at the next launch means the person who
                        // just agreed watches the buffer drain, instead of
                        // being told something happened later.
                        scope.launch(Dispatchers.IO) { Problems.send() }
                    }) { Text(L10n.t("ns.pr.send", lang)) }
                    OutlinedButton(onClick = {
                        Problems.answerNotice(false); answered = true; sending = false
                    }) { Text(L10n.t("ns.pr.dont", lang)) }
                }
            } else {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(L10n.t("ns.pr.toggle", lang), Modifier.weight(1f),
                         style = MaterialTheme.typography.bodyMedium)
                    Switch(checked = sending, onCheckedChange = {
                        sending = it; Problems.setSending(it)
                    })
                }
            }

            TextButton(onClick = { showing = !showing }) {
                Text(L10n.t(if (showing) "ns.pr.hide" else "ns.pr.show", lang))
            }
            if (showing) {
                if (owed.isEmpty()) {
                    Text(L10n.t("ns.pr.owed", lang),
                         style = MaterialTheme.typography.bodySmall)
                } else {
                    owed.forEach { r ->
                        Text("${r.optString("op")} → ${r.optInt("status")}  " +
                             "×${r.optInt("count")}  ${r.optString("day")}",
                             style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
    }
}

/**
 * The one QRME profile that is this person.
 *
 * Every other tandem surface in this shell reaches somebody else's profile.
 * This reaches their own — the `self` profile that speaks *as* them, and that
 * answers strangers. Built around the preview rather than the switches,
 * because the switches are not the decision: docs/tandem.md says what may
 * cross, and this shows exactly what would before it does.
 *
 * On the phone as well as the console, because the phone is what somebody has
 * with them when they change their mind.
 */
/**
 * What the Guardian carries between sessions, on the phone.
 *
 * The console's profile is a snapshot somebody rebuilds. This is the part
 * that moves on its own — and until this release nothing moved at all,
 * because the only thing that built the derived artifact was a button in a
 * desktop console that a phone-only user never sees.
 *
 *     asked     can a user-specific model be built from the history
 *     mattered  does anything ever build it
 *
 * Read-only except for forgetting it: every derived thing here has to be
 * droppable by the person it was derived from.
 */
@Composable
fun ContinuityCard(uid: String, token: String, lang: String) {
    var carried by remember { mutableStateOf<ContinuityState?>(null) }
    val scope = rememberCoroutineScope()
    fun load() {
        scope.launch(Dispatchers.IO) {
            carried = runCatching { ApiClient.continuity(uid, token) }.getOrNull()
        }
    }
    LaunchedEffect(Unit) { load() }

    Card(colors = CardDefaults.cardColors(containerColor = Jim.Card)) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("cont.title", lang), style = MaterialTheme.typography.titleSmall)
            val c = carried
            if (c != null && c.built) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("${c.observations} " + L10n.t("cont.observations", lang),
                        Modifier.weight(1f), color = Jim.Txt, fontSize = 13.sp,
                        fontWeight = FontWeight.Bold)
                    TextButton(onClick = {
                        scope.launch(Dispatchers.IO) {
                            runCatching { ApiClient.forgetContinuity(uid, token) }
                            load()
                        }
                    }) { Text(L10n.t("cont.forget", lang), color = Jim.Red, fontSize = 12.sp) }
                }
                Text(if (c.conditioning) L10n.t("cont.shaping", lang)
                     else L10n.t("cont.not_yet", lang),
                    color = Jim.T2, fontSize = 11.sp)
                c.vector.entries.sortedBy { it.key }.forEach { (dim, value) ->
                    val meaning = c.meanings[dim]?.let { " \u2014 $it" } ?: ""
                    Text("$dim: ${(value * 100).toInt()}%$meaning",
                        color = Jim.T2, fontSize = 11.sp)
                }
                c.method?.let { Text(it, color = Jim.T2, fontSize = 11.sp) }
            } else {
                Text(c?.note ?: L10n.t("cont.nothing", lang),
                    color = Jim.T2, fontSize = 11.sp)
            }
            c?.carries?.let { Text(it, color = Jim.T2, fontSize = 11.sp) }
        }
    }
}

@Composable
fun SelfProfileScreen(api: ApiClient, uid: String, token: String, lang: String) {
    val scope = rememberCoroutineScope()
    var status by remember { mutableStateOf<JSONObject?>(null) }
    var preview by remember { mutableStateOf<JSONObject?>(null) }
    var profileId by remember { mutableStateOf("") }
    var ownerToken by remember { mutableStateOf("") }
    var note by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }
    val categories = listOf("language", "wellbeing", "conditions",
                            "medication", "continuity")

    suspend fun refresh() {
        status = runCatching { api.selfProfile(uid, token) }.getOrNull()
        preview = runCatching { api.previewSelfProfile(uid, token) }.getOrNull()
    }
    LaunchedEffect(uid) { refresh() }

    fun consentedNow(): List<String> {
        val arr = status?.optJSONArray("consented") ?: return emptyList()
        return (0 until arr.length()).map { arr.getString(it) }
    }

    fun run(said: String, work: suspend () -> Unit) {
        busy = true
        scope.launch(Dispatchers.IO) {
            note = runCatching { work(); said }.getOrElse { it.message }
            refresh(); busy = false
        }
    }

    Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(L10n.t("self.title", lang), style = MaterialTheme.typography.titleMedium)
        ProblemReportingCard(lang)
        ContinuityCard(uid, token, lang)
        Text(L10n.t("self.lead", lang), style = MaterialTheme.typography.bodySmall)

        if (status?.optBoolean("linked") != true) {
            Card(colors = CardDefaults.cardColors(containerColor = Jim.Card)) {
                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(L10n.t("self.link", lang), style = MaterialTheme.typography.titleSmall)
                    Text(L10n.t("self.paste", lang), style = MaterialTheme.typography.bodySmall)
                    OutlinedTextField(profileId, { profileId = it },
                        label = { Text(L10n.t("self.profile_id", lang)) })
                    OutlinedTextField(ownerToken, { ownerToken = it },
                        label = { Text(L10n.t("self.owner_token", lang)) })
                    OutlinedButton(enabled = !busy && profileId.isNotBlank() && ownerToken.isNotBlank(),
                        onClick = {
                            run(L10n.t("self.linked_note", lang)) {
                                api.linkSelfProfile(uid, token, profileId.trim(), ownerToken.trim())
                            }
                        }) { Text(L10n.t("self.link_button", lang)) }
                }
            }
        } else {
            Card(colors = CardDefaults.cardColors(containerColor = Jim.Card)) {
                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(L10n.t("self.may_know", lang), style = MaterialTheme.typography.titleSmall)
                    Text(L10n.t("self.until_tick", lang), style = MaterialTheme.typography.bodySmall)
                    categories.forEach { key ->
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Switch(checked = consentedNow().contains(key), enabled = !busy,
                                onCheckedChange = { on ->
                                    val next = if (on) consentedNow() + key
                                               else consentedNow() - key
                                    run(L10n.t("self.saved", lang)) {
                                        api.consentSelfProfile(uid, token, next)
                                    }
                                })
                            Text(key, style = MaterialTheme.typography.bodySmall)
                        }
                    }
                }
            }
            Card(colors = CardDefaults.cardColors(containerColor = Jim.Card)) {
                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(L10n.t("self.exactly", lang), style = MaterialTheme.typography.titleSmall)
                    Text(
                        if (preview?.optBoolean("empty") == true) L10n.t("self.nothing_ticked", lang)
                        else preview?.optJSONObject("brief")?.toString(2) ?: "",
                        style = MaterialTheme.typography.bodySmall)
                    Text(L10n.t("self.message_itself", lang), style = MaterialTheme.typography.bodySmall)
                    OutlinedButton(enabled = !busy && preview?.optBoolean("empty") != true,
                        onClick = { run(L10n.t("self.sent", lang)) { api.briefSelfProfile(uid, token) } }
                    ) { Text(L10n.t("self.send", lang)) }
                }
            }
            Card(colors = CardDefaults.cardColors(containerColor = Jim.Card)) {
                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(L10n.t("self.stop", lang), style = MaterialTheme.typography.titleSmall)
                    Text(L10n.t("self.unlink_note", lang), style = MaterialTheme.typography.bodySmall)
                    OutlinedButton(enabled = !busy,
                        onClick = { run(L10n.t("self.unlinked", lang)) { api.unlinkSelfProfile(uid, token) } }
                    ) { Text(L10n.t("self.unlink", lang)) }
                }
            }
        }
        note?.let { Text(it, style = MaterialTheme.typography.bodySmall) }
    }
}

// ---- care team, clinical captures, and channel 2 — the console doors
// task #106 built that the phones never got ----

@Composable
private fun CareTeamPanel(vm: GuardianViewModel) {
    var team by remember { mutableStateOf<CareTeamState?>(null) }
    var plans by remember { mutableStateOf<List<CarePlanRow>>(emptyList()) }
    var orgId by remember { mutableStateOf("") }
    var departmentId by remember { mutableStateOf("") }
    var ownerToken by remember { mutableStateOf("") }
    var goal by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.careTeamState(vm.uid!!, vm.token!!) }) { r ->
            team = r.getOrNull()
            if (team?.linked == true)
                vm.call({ ApiClient.careTeamPlans(vm.uid!!, vm.token!!) }) { p ->
                    plans = p.getOrDefault(emptyList())
                }
        }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.ct.title", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.ct.sub", vm.language), color = Jim.T2, fontSize = 12.sp)
        val t = team
        if (t?.linked == true) {
            Text(L10n.t("ns.ct.linked", vm.language), color = Jim.Green,
                fontSize = 13.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("ns.ct.linked.pitch", vm.language), color = Jim.T2,
                fontSize = 11.sp)
            Text(L10n.t("ns.ct.linked.line", vm.language)
                    .replace("{org}", t.orgId ?: "")
                    .replace("{dept}", t.departmentId ?: ""),
                color = Jim.T2, fontSize = 11.sp)
            labeledField(L10n.t("ns.ct.linked.goal", vm.language), goal,
                L10n.t("ns.ct.linked.goal.ph", vm.language)) { goal = it }
            BrandButton(L10n.t("ns.ct.linked.goal", vm.language),
                enabled = goal.isNotBlank()) {
                vm.call({ ApiClient.careTeamCoordinate(vm.uid!!, vm.token!!,
                    goal.trim()) }) { r ->
                    error = r.exceptionOrNull()?.message
                    goal = ""; reload()
                }
            }
            SmallAction(L10n.t("ns.ct.linked.unlink", vm.language)) {
                vm.call({ ApiClient.careTeamUnlink(vm.uid!!, vm.token!!) }) {
                    team = null; plans = emptyList(); reload()
                }
            }
            if (plans.isEmpty())
                Text(L10n.t("ns.ct.plans.none", vm.language), color = Jim.T3,
                    fontSize = 11.sp)
            else plans.take(4).forEach { plan ->
                Text(plan.goal, color = Jim.Txt, fontSize = 12.sp,
                    fontWeight = FontWeight.Bold)
                plan.plan?.let { Text(it, color = Jim.T2, fontSize = 11.sp,
                    maxLines = 4) }
            }
        } else {
            Text(L10n.t("ns.ct.link.pitch", vm.language), color = Jim.T2,
                fontSize = 11.sp)
            labeledField(L10n.t("ns.ct.link.org", vm.language), orgId,
                L10n.t("ns.ct.link.org.ph", vm.language)) { orgId = it }
            labeledField(L10n.t("ns.ct.link.dept", vm.language), departmentId,
                L10n.t("ns.ct.link.dept.ph", vm.language)) { departmentId = it }
            labeledField(L10n.t("ns.ct.link.token", vm.language), ownerToken,
                L10n.t("ns.ct.link.token.ph", vm.language)) { ownerToken = it }
            BrandButton(L10n.t("ns.ct.link.go", vm.language),
                enabled = orgId.isNotBlank() && departmentId.isNotBlank()
                        && ownerToken.isNotBlank()) {
                vm.call({ ApiClient.careTeamLink(vm.uid!!, vm.token!!,
                    orgId.trim(), departmentId.trim(), ownerToken.trim()) }) { r ->
                    error = r.exceptionOrNull()?.message
                    ownerToken = ""; reload()
                }
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}

@Composable
private fun MicPanel(vm: GuardianViewModel) {
    var mic by remember { mutableStateOf<MicState?>(null) }
    var types by remember { mutableStateOf<MicTypeChoices?>(null) }
    var gains by remember { mutableStateOf<MicGainChoices?>(null) }
    var history by remember { mutableStateOf<List<MicEvent>>(emptyList()) }
    var showHistory by remember { mutableStateOf(false) }
    var deviceName by remember { mutableStateOf("") }
    var micType by remember { mutableStateOf("") }
    var handoverReason by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }

    fun run(work: suspend () -> MicState) {
        vm.call({ work() }) { r ->
            error = r.exceptionOrNull()?.message
            r.getOrNull()?.let { mic = it }
        }
    }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.micState(vm.uid!!, vm.token!!) }) { r -> mic = r.getOrNull() }
        vm.call({ ApiClient.micTypes() }) { r ->
            types = r.getOrNull()
            if (micType.isBlank()) micType = types?.personal?.firstOrNull() ?: ""
        }
        vm.call({ ApiClient.micGains() }) { r -> gains = r.getOrNull() }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.ch.mic", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        val m = mic
        if (m?.attached == true) {
            Text("${m.device ?: ""} · ${m.micType ?: ""}", color = Jim.Txt,
                fontSize = 13.sp, fontWeight = FontWeight.Bold)
            m.hears?.let { Text(it, color = Jim.T2, fontSize = 11.sp) }
            if (m.capped)
                Text(L10n.t("ns.ch.mic.capped", vm.language), color = Jim.Amber,
                    fontSize = 11.sp)
            gains?.let { g ->
                Text(L10n.t("ns.ch.mic.which", vm.language), color = Jim.T2,
                    fontSize = 11.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    g.levels.forEach { level ->
                        FilterChip(
                            selected = (m.gain ?: g.default) == level.gain,
                            onClick = { run { ApiClient.setMicGain(vm.uid!!,
                                vm.token!!, level.gain) } },
                            label = { Text(level.gain, fontSize = 11.sp) },
                        )
                    }
                }
            }
            labeledField("", handoverReason,
                L10n.t("ns.ch.mic.handover", vm.language)) { handoverReason = it }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SmallAction(L10n.t("ns.ch.mic.handover", vm.language)) {
                    if (handoverReason.isNotBlank()) {
                        val reason = handoverReason.trim()
                        handoverReason = ""
                        run { ApiClient.handOverMic(vm.uid!!, vm.token!!, reason) }
                    }
                }
                if (m.listening)
                    SmallAction(L10n.t("ns.ch.mic.release", vm.language)) {
                        run { ApiClient.releaseMic(vm.uid!!, vm.token!!) }
                    }
                SmallAction(L10n.t("ns.ch.mic.detach", vm.language)) {
                    run { ApiClient.detachMic(vm.uid!!, vm.token!!) }
                }
            }
        } else {
            Text(L10n.t("ns.ch.mic.none", vm.language), color = Jim.T3,
                fontSize = 11.sp)
            labeledField(L10n.t("ns.ch.mic.kind", vm.language), deviceName,
                L10n.t("ns.ch.mic.kind", vm.language)) { deviceName = it }
            types?.let { t ->
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    (t.personal + t.ambient).take(4).forEach { kind ->
                        FilterChip(selected = micType == kind,
                            onClick = { micType = kind },
                            label = { Text(kind, fontSize = 11.sp) })
                    }
                }
            }
            BrandButton(L10n.t("ns.ch.mic.attach", vm.language),
                enabled = deviceName.isNotBlank() && micType.isNotBlank()) {
                run { ApiClient.attachMic(vm.uid!!, vm.token!!,
                    deviceName.trim(), micType) }
            }
        }
        SmallAction(L10n.t("ns.ch.hist", vm.language)) {
            showHistory = !showHistory
            if (showHistory)
                vm.call({ ApiClient.micHistory(vm.uid!!, vm.token!!) }) { r ->
                    history = r.getOrDefault(emptyList())
                }
        }
        if (showHistory) history.take(6).forEach { event ->
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("${event.device} · ${event.gain}", color = Jim.T2,
                    fontSize = 11.sp)
                if (event.live)
                    Text(L10n.t("ns.ch.hist.live", vm.language),
                        color = Jim.Green, fontSize = 11.sp,
                        fontWeight = FontWeight.Bold)
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}

@Composable
private fun CapturesPanel(vm: GuardianViewModel) {
    val context = androidx.compose.ui.platform.LocalContext.current
    var vocabulary by remember { mutableStateOf<CaptureVocabulary?>(null) }
    var rows by remember { mutableStateOf<List<CaptureRecord>>(emptyList()) }
    var site by remember { mutableStateOf("") }
    var note by remember { mutableStateOf("") }
    var intimateConsent by remember { mutableStateOf(false) }
    var openImage by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.captures(vm.uid!!, vm.token!!) }) { r ->
            rows = r.getOrDefault(emptyList())
        }
    }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.captureVocabulary() }) { r ->
            vocabulary = r.getOrNull()
            if (site.isBlank())
                site = vocabulary?.sites?.keys?.sorted()?.firstOrNull() ?: ""
        }
        reload()
    }

    // The system picker hands over one image and nothing else — the app
    // never reads the photo library, only what the person chose.
    val picker = androidx.activity.compose.rememberLauncherForActivityResult(
        androidx.activity.result.contract.ActivityResultContracts.GetContent()
    ) { uri ->
        if (uri != null) {
            val bytes = context.contentResolver.openInputStream(uri)
                ?.use { it.readBytes() }
            if (bytes != null) {
                val encoded = android.util.Base64.encodeToString(
                    bytes, android.util.Base64.NO_WRAP)
                vm.call({ ApiClient.takeCapture(vm.uid!!, vm.token!!, site,
                    encoded, note.trim(), intimateConsent) }) { r ->
                    error = r.exceptionOrNull()?.message
                    note = ""; reload()
                }
            }
        }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.ch.cam", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.ch.cam.for", vm.language), color = Jim.T2,
            fontSize = 11.sp)
        vocabulary?.let { v ->
            Text(L10n.t("ns.ch.cam.site", vm.language), color = Jim.T2,
                fontSize = 11.sp)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                v.sites.keys.sorted().take(4).forEach { key ->
                    FilterChip(selected = site == key,
                        onClick = { site = key },
                        label = { Text(v.sites[key] ?: key, fontSize = 10.sp) })
                }
            }
            labeledField("", note,
                L10n.t("ns.ch.cam.note", vm.language)) { note = it }
            if (v.intimate.contains(site))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Switch(checked = intimateConsent,
                        onCheckedChange = { intimateConsent = it },
                        colors = SwitchDefaults.colors(checkedTrackColor = Jim.Amber))
                    Text(L10n.t("ns.ch.cam.consent", vm.language),
                        color = Jim.T2, fontSize = 11.sp)
                }
            BrandButton(L10n.t("ns.ch.cam.attach", vm.language),
                enabled = site.isNotBlank()
                        && (!v.intimate.contains(site) || intimateConsent)) {
                picker.launch("image/*")
            }
        }
        rows.take(6).forEach { row ->
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(vocabulary?.sites?.get(row.site) ?: row.site,
                    color = Jim.Txt, fontSize = 12.sp,
                    fontWeight = FontWeight.Bold)
                if (row.intimate)
                    Text(L10n.t("ns.ch.cam.intimate", vm.language),
                        color = Jim.Amber, fontSize = 10.sp,
                        fontWeight = FontWeight.Bold)
                row.note?.let { Text(it, color = Jim.T2, fontSize = 11.sp) }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SmallAction(L10n.t("ns.ch.cam.where", vm.language)) {
                        vm.call({ ApiClient.captureImage(vm.uid!!, vm.token!!,
                            row.id) }) { r -> openImage = r.getOrNull() }
                    }
                    // A referral releases only what is chosen by name, and
                    // this button is the choosing — never done silently.
                    SmallAction(L10n.t("ns.ch.cam.tick", vm.language)) {
                        vm.call({ ApiClient.attachCaptures(vm.uid!!, vm.token!!,
                            listOf(row.id)) }) { r ->
                            error = r.exceptionOrNull()?.message
                        }
                    }
                    SmallAction(L10n.t("ns.ch.cam.withdraw", vm.language)) {
                        vm.call({ ApiClient.withdrawCapture(vm.uid!!, vm.token!!,
                            row.id) }) { reload() }
                    }
                }
            }
        }
        openImage?.takeIf { it.isNotBlank() }?.let { b64 ->
            val bytes = android.util.Base64.decode(b64, android.util.Base64.DEFAULT)
            val bmp = android.graphics.BitmapFactory
                .decodeByteArray(bytes, 0, bytes.size)
            if (bmp != null)
                androidx.compose.foundation.Image(
                    bitmap = bmp.asImageBitmap(),
                    contentDescription = L10n.t("ns.ch.cam", vm.language),
                    modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)))
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}
