package app.jim.guardian.ui

import android.content.Intent
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
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
    var language by remember { mutableStateOf("en") }
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
                labeledField("Name", name, "Your name") { name = it }
                labeledField("Birthdate", birthdate, "yyyy-MM-dd") { birthdate = it }
                if (languages.isNotEmpty()) {
                    Text("Language", color = Jim.T2, fontSize = 12.sp)
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
            BrandButton("Get Started", enabled = consent && name.isNotBlank(), busy = busy) {
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
            Text("Guardian on · watching", color = Jim.Green, fontSize = 12.sp, fontWeight = FontWeight.Bold)
        }
        Text("Hi, ${vm.displayName}", color = Jim.Txt, fontSize = 28.sp, fontWeight = FontWeight.Bold)
        Text("Your Guardian is watching — the rules are transparent.", color = Jim.T2, fontSize = 14.sp)

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("Learned baseline", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            when {
                metrics == null -> CircularProgressIndicator(color = Jim.BrandA, modifier = Modifier.size(22.dp))
                metrics!!.isEmpty() -> Text("No baseline yet — it builds from calm samples in Monitor.",
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
        AnonymityCard(vm)
        ImproveCard(vm)
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
        Text("Live Monitoring", color = Jim.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text("Send a sample. The Guardian compares it to your baseline.", color = Jim.T2, fontSize = 13.sp)
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            sliderRow("Heart rate", "${hr.roundToInt()} bpm", Jim.Red, hr, 40f..180f) { hr = it }
            sliderRow("Stress", "${(stress * 100).roundToInt()}%", Jim.Amber, stress, 0f..1f) { stress = it }
        }
        BrandButton("Send sample", busy = busy) {
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
                labeledField("", note, "Anything you want to add (optional)") { note = it }
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
                Text(if (a.helped == true) "Monitoring resumes" else "Bringing in a person",
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
        Text("Check-in", color = Jim.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text("A quick pulse on how you're doing.", color = Jim.T2, fontSize = 13.sp)
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            ratingRow("Mood", mood) { mood = it }
            ratingRow("Energy", energy) { energy = it }
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
        BrandButton("Log check-in", busy = busy) {
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
            labeledField("Message", message, "What's on your mind?") { message = it }
        }
        BrandButton("Ask coach", enabled = message.isNotBlank(), busy = busy) {
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
    val tabs = listOf("Goals", "Habits", "Journal", "Money", "Schedule", "Shop", "Circle")
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
            labeledField("Title", title, "What do you want to achieve?") { title = it }
            BrandButton("Add goal", enabled = title.isNotBlank(), busy = busy) {
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
            labeledField("Name", name, "e.g. Walk 20 minutes") { name = it }
            BrandButton("Add habit", enabled = name.isNotBlank(), busy = busy) {
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
            labeledField("Entry", text, "How was today?") { text = it }
            BrandButton("Save entry", enabled = text.isNotBlank(), busy = busy) {
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
        vm.call({ ApiClient.alarms(vm.uid!!, vm.token!!) }) { rows = it }
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
                        label = { Text("Your name") })
                    Button(onClick = {
                        vm.call({ ApiClient.acceptAlarm(vm.uid!!, a.id,
                            responder, vm.token!!) }) { said = it.note; load() }
                    }, enabled = responder.isNotBlank(),
                        colors = ButtonDefaults.buttonColors(containerColor = Jim.BrandA)) {
                        Text(L10n.t("alarm.going", vm.language))
                    }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    TextButton(onClick = {
                        vm.call({ ApiClient.escalateAlarm(vm.uid!!, a.id,
                            vm.token!!) }) { said = it.note; load() }
                    }) { Text(L10n.t("alarm.cannot_go", vm.language), color = Jim.Red) }
                    TextButton(onClick = {
                        vm.call({ ApiClient.clearAlarm(vm.uid!!, a.id,
                            vm.token!!) }) { said = it.note; load() }
                    }) { Text(L10n.t("alarm.clear", vm.language), color = Jim.T2) }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(value = question,
                        onValueChange = { question = it },
                        label = { Text("What do I do?") },
                        modifier = Modifier.weight(1f))
                    TextButton(onClick = {
                        vm.call({ ApiClient.alarmGuidance(a.id, question,
                            vm.token!!) }) { guidance = it }
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
            Text("Crash watch", color = Jim.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text("Off by default, programmed by you: a critical reading (a fall the watch felt, a collapsing pulse) opens " +
                 "\"are you okay?\" — unanswered attempts contact your trusted " +
                 "person, and emergency services only if you tick the box. " +
                 "Gentle drift check-ins can never trigger it.",
                color = Jim.T2, fontSize = 12.sp)
            labeledField("Trusted person", name, "Rosa") { name = it }
            labeledField("How to reach them", channel, "rosa@example.com") { channel = it }
            labeledField("Attempts (1\u201310)", attempts, "3") { attempts = it }
            labeledField("Minutes per attempt", window, "5") { window = it }
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
                }) { Text(if (st?.armed == true) "Update" else "Arm the crash watch") }
                if (st?.armed == true) {
                    Button(enabled = !busy, onClick = {
                        busy = true
                        vm.call({ ApiClient.disarmCrashWatch(vm.uid!!, vm.token!!) }) { took(it) }
                    }, colors = ButtonDefaults.buttonColors(containerColor = Jim.Card)) {
                        Text("Disarm", color = Jim.Red)
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
    val tabs = listOf("Alarms", "SOS", "Crash", "Med ID", "Policy", "Robots", "Vault")
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)) {
        ProblemReportingCard()
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
                Text("SOS", color = Color.White, fontSize = 34.sp, fontWeight = FontWeight.Black)
                Text(if (busy) "Coordinating…" else "Tap for emergency",
                    color = Color.White, fontSize = 12.sp)
            }
        }
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            labeledField("What's happening? (optional)", situation, "") { situation = it }
            labeledField("Where are you? (optional)", location, "") { location = it }
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
            Text("Sensitivity", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                listOf("cautious", "balanced", "assertive").forEach { lvl ->
                    FilterChip(
                        selected = policy?.sensitivity == lvl,
                        onClick = {
                            vm.call({ ApiClient.setSensitivity(vm.uid!!, vm.token!!, lvl) }) { reload() }
                        },
                        label = { Text(lvl.replaceFirstChar { it.uppercase() }, fontSize = 12.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Jim.BrandA,
                            selectedLabelColor = Color.White, labelColor = Jim.T2,
                        ),
                    )
                }
            }
            Text("Cautious escalates a rung earlier; assertive a rung later. Crisis and critical events have floors no dial can lower.",
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

    fun reload() {
        vm.call({ ApiClient.custody(vm.uid!!, vm.token!!) }) { r ->
            r.onSuccess { list = it; error = null }
            r.onFailure { error = it.message }
        }
    }
    LaunchedEffect(Unit) { reload() }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("Vault custody", color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        OfflinePostureCard(vm)
        Text("Chats with tandem specialists are sealed into the PDI vault — " +
             "encrypted, attributed, and hash-chained. This is your copy of " +
             "the proof.", color = Jim.T2, fontSize = 12.sp)
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
        list?.let { c ->
            Text(if (c.chainIntact == true) "🔗 Audit chain intact"
                 else "⚠️ Audit chain status unknown",
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
                        Text(if (p.chainIntact == true) "Hash chain: intact"
                             else "Hash chain: unknown",
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
                    res.spoken.isNotEmpty() -> "🔊 " + res.spoken.joinToString(" → ")
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
            Text("Bind a robot", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("Bound robots respond to escalations: mobile bodies come to you; vacuums dock and clear the floor.",
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
            BrandButton("Bind", enabled = catalog.isNotEmpty(), busy = busy) {
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
                Text("Autonomous-resuscitation waiver", color = Jim.Txt,
                    fontSize = 15.sp, fontWeight = FontWeight.Bold)
                if (waiver?.signed == true)
                    Text("SIGNED", color = Jim.Green, fontSize = 10.sp,
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
                }) { Text("Revoke — restore confirm-gated operation", color = Jim.Red, fontSize = 12.sp) }
            } else {
                Text("Unlock automatic operation: CPR that starts on detection, and a " +
                    "fully-automatic AED that shocks on its own analysis after the robot " +
                    "verifies everyone is clear. Until signed, every start needs an " +
                    "on-scene confirmation and no shock is ever delivered.",
                    color = Jim.T2, fontSize = 12.sp)
                waiver?.terms?.forEach { t ->
                    Text("• $t", color = Jim.T3, fontSize = 10.sp)
                }
                labeledField("Type your legal name to sign", signature, vm.displayName) { signature = it }
                RobotAction("Sign & submit waiver") {
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
                            Text(if (rating == "perform") "CPR-rated" else "first-aid assist",
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
                        RobotAction("Fetch AED") { command(rob, "fetch_aed", null) }
                        RobotAction("Coach CPR") { command(rob, "guide_first_aid", "cpr") }
                        RobotAction("Meet EMS") { command(rob, "meet_responders", null) }
                    }
                }
                if ("perform_cpr" in rob.commands) {
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        when {
                            rob.status == "performing_cpr" ->
                                RobotAction("Stop CPR", Jim.Red) { command(rob, "stop_cpr", null) }
                            waiver?.signed == true -> {
                                RobotAction("Start CPR (pre-authorized)", Jim.Red) {
                                    command(rob, "perform_cpr", null)
                                }
                                RobotAction("Auto-resuscitate", Jim.Red) {
                                    command(rob, "auto_defib", null)
                                }
                            }
                            confirmingCpr == rob.id -> {
                                RobotAction("Confirm: unresponsive, not breathing", Jim.Red) {
                                    confirmingCpr = null
                                    command(rob, "perform_cpr", "confirmed")
                                }
                                TextButton(onClick = { confirmingCpr = null }) {
                                    Text("Cancel", color = Jim.T2, fontSize = 12.sp)
                                }
                            }
                            else -> RobotAction("Perform CPR…", Jim.Red) {
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
        Text("Model", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text("Which LLM powers your coaching and guidance.", color = Jim.T2, fontSize = 12.sp)
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
        Text("Language", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text("Everything drafted for you — guidance, coaching, first-aid steps, waiver terms — is delivered in this language.",
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
                Text("Pre-translate everything", color = Jim.Txt, fontSize = 13.sp)
                Text("Off keeps originals — translate selectively below.",
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
        Text("Translate anything", color = Jim.Txt, fontSize = 13.sp, fontWeight = FontWeight.Bold)
        labeledField("", translateInput, "Paste or type text…") { translateInput = it }
        RobotAction("Translate") {
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
            Text("engine: ${t.engine}" + (t.note?.let { " — $it" } ?: ""),
                color = Jim.T3, fontSize = 10.sp)
        }
    }
}

// ---- Help us improve — product feedback (open to anyone) ----

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
        Text("Help us improve", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text("Tell us how to make the app better — an idea, a rough edge, a bug, or what you love. It goes straight to the team.",
            color = Jim.T2, fontSize = 12.sp)
        categories.chunked(3).forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                row.forEach { c ->
                    FilterChip(
                        selected = category == c,
                        onClick = { category = c },
                        label = { Text(c.replaceFirstChar { it.uppercase() }, fontSize = 11.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Jim.BrandA,
                            selectedLabelColor = Color.White, labelColor = Jim.T2,
                        ),
                    )
                }
            }
        }
        labeledField("", message, "What's on your mind?") { message = it }
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("Rating", color = Jim.T2, fontSize = 12.sp)
            (1..5).forEach { n ->
                Text(if (n <= rating) "★" else "☆",
                    color = if (n <= rating) Jim.Amber else Jim.T3, fontSize = 20.sp,
                    modifier = Modifier.clickable { rating = if (rating == n) 0 else n })
            }
        }
        BrandButton("Send feedback", enabled = message.isNotBlank()) {
            vm.call({
                ApiClient.submitImprovement(vm.token, category, message.trim(),
                    if (rating == 0) null else rating)
            }) {
                thanks = "Thank you — sent."; message = ""; rating = 0; reload()
            }
        }
        thanks?.let { Text(it, color = Jim.Green, fontSize = 12.sp) }
        state?.takeIf { it.total > 0 }?.let { st ->
            HorizontalDivider(color = Jim.Line)
            Text("So far: " + categories.mapNotNull { c ->
                st.tally[c]?.takeIf { it > 0 }?.let { "$it $c" }
            }.joinToString(" · "), color = Jim.T3, fontSize = 10.sp)
            if (st.mine.isNotEmpty()) {
                Text("Yours", color = Jim.Txt, fontSize = 12.sp, fontWeight = FontWeight.Bold)
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
            Text("Medical ID", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("A shareable card for first responders: condition-level facts only, readable from a locked phone. Re-issuing rotates the QR and kills the old one.",
                color = Jim.T2, fontSize = 12.sp)
            BrandButton(if (issued == null) "Issue Medical ID" else "Rotate QR", busy = busy) {
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
                Text("Card issued", color = Jim.Green, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text("Print or lock-screen the QR at:", color = Jim.T2, fontSize = 12.sp)
                Text(i.qrSvgUrl, color = Jim.T2, fontSize = 11.sp)
                card?.let { c ->
                    HorizontalDivider(color = Jim.Line)
                    Text("What a responder sees", color = Jim.Txt, fontSize = 14.sp,
                        fontWeight = FontWeight.Bold)
                    medRow("Name", c.name ?: "—")
                    medRow("Age", c.age?.toString() ?: "—")
                    medRow("Resting HR", c.restingHr?.let { "$it bpm" } ?: "—")
                    medRow("Conditions",
                        if (c.conditions.isEmpty()) "none declared" else c.conditions.joinToString(", "))
                    if (c.contactName != null || c.contactPhone != null)
                        medRow("Contact", "${c.contactName ?: "—"} · ${c.contactPhone ?: "—"}")
                }
                TextButton(onClick = {
                    vm.call({ ApiClient.revokeMedicalCard(vm.uid!!, vm.token!!) }) {
                        issued = null; card = null
                    }
                }) { Text("Revoke card", color = Jim.Red, fontSize = 13.sp) }
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
    val tabs = listOf("Monitor", "Check-in", "Coach", "Family")
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
            else -> FamilyPanel(vm)
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
                    Text("Family watch", color = Jim.Txt, fontSize = 14.sp,
                        fontWeight = FontWeight.Bold)
                    if (f.haptic == "alert")
                        Text("⌚ TAPPED", color = Jim.Red, fontSize = 11.sp,
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
                                Text("critical", color = Jim.Red, fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold)
                            else if (c.escalations24h > 0)
                                Text("escalated", color = Jim.Amber, fontSize = 10.sp)
                        }
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            if (c.paused)
                                Text("paused", color = Jim.T3, fontSize = 10.sp)
                            c.quietHours?.let {
                                Text("🌙 $it", color = Jim.T3, fontSize = 10.sp)
                            }
                        }
                    }
                }
            }
        }

        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Set up my child", color = Jim.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text("You enroll as the recorded parent/guardian. The account " +
                 "starts cautious, with you as the emergency contact; cloud " +
                 "sharing stays off. The auto-defib waiver can never be " +
                 "signed for a minor.", color = Jim.T2, fontSize = 12.sp)
            OutlinedTextField(value = name, onValueChange = { name = it },
                label = { Text("Child's name") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = birthdate, onValueChange = { birthdate = it },
                label = { Text("Birthdate (YYYY-MM-DD)") },
                modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = phone, onValueChange = { phone = it },
                label = { Text("Your phone (emergency line, optional)") },
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
                Text("Create child account")
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
        created?.let { c ->
            Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
                Text("Child account created", color = Jim.Green, fontSize = 14.sp,
                    fontWeight = FontWeight.Bold)
                Text("Oversight: ${c.oversight} · sensitivity: ${c.sensitivity}",
                    color = Jim.T2, fontSize = 12.sp)
                Text("Device token — shown once, put it on their watch or phone:",
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
                        "full" -> "full oversight (under 13)"
                        "alerts_only" -> "alerts only — daily life stays private"
                        else -> "oversight ended — an adult now"
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
                Text("Device controls", color = Jim.Txt, fontSize = 14.sp,
                    fontWeight = FontWeight.Bold)
                Text("Pause and quiet hours hold everyday guidance only — " +
                     "monitoring, crisis escalation, and the emergency path " +
                     "never pause.", color = Jim.T3, fontSize = 10.sp)
                Row(Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically) {
                    Text("Pause guidance", color = Jim.Txt, fontSize = 12.sp)
                    Switch(checked = pauseOn, onCheckedChange = { pauseOn = it })
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(value = quietStart,
                        onValueChange = { quietStart = it },
                        label = { Text("Quiet start") },
                        modifier = Modifier.weight(1f))
                    OutlinedTextField(value = quietEnd,
                        onValueChange = { quietEnd = it },
                        label = { Text("Quiet end") },
                        modifier = Modifier.weight(1f))
                }
                SmallAction("Apply") {
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
            }
        }
        overview?.let { o ->
            Column(Modifier.fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp)).background(Jim.Card)
                    .padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(3.dp)) {
                if (o.note != null) {
                    Text("Oversight ended", color = Jim.Txt, fontSize = 14.sp,
                        fontWeight = FontWeight.Bold)
                    Text(o.note, color = Jim.T2, fontSize = 11.sp)
                } else {
                    Text(o.displayName ?: "Child", color = Jim.Txt,
                        fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    o.privacyNote?.let {
                        Text("🔒 $it", color = Jim.Amber, fontSize = 11.sp)
                    }
                    if (o.criticalEvents > 0)
                        Text("⚠️ ${o.criticalEvents} critical event(s)",
                            color = Jim.Red, fontSize = 12.sp,
                            fontWeight = FontWeight.Bold)
                    o.events.forEach { e ->
                        Text("${e.type}${e.condition?.let { " · $it" } ?: ""}" +
                             (e.severity?.let { " · ${it.uppercase()}" } ?: ""),
                            color = Jim.T2, fontSize = 11.sp)
                    }
                    if (o.events.isEmpty())
                        Text("Nothing in the window — quiet is good news.",
                            color = Jim.T2, fontSize = 11.sp)
                }
            }
        }
    }
}

// ---- Connect: data sources, social platforms, connected apps ----

@Composable
fun ConnectScreen(vm: GuardianViewModel) {
    var tab by remember { mutableIntStateOf(0) }
    val tabs = listOf("Sources", "Social", "Apps", "Community", "Me")
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)) {
        TabRow(selectedTabIndex = tab, containerColor = Jim.Card, contentColor = Jim.BrandA) {
            tabs.forEachIndexed { i, t ->
                Tab(selected = tab == i, onClick = { tab = i },
                    text = { Text(t, fontSize = 13.sp) })
            }
        }
        when (tab) {
            0 -> SourcesPanel(vm)
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
        Text("Data sources", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text("JIM sees what you allow — flip a source off and it stops being read, immediately.",
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
            Text("Social platforms", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            FlowRowChips(platforms, platform) { platform = it }
            labeledField("Handle (optional)", handle, "@you") { handle = it }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                smallAction("Connect to collect") { connect("collect") }
                smallAction("Connect to publish") { connect("publish") }
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
                    smallAction("Collect sample") {
                        vm.call({ ApiClient.socialCollect(c.id, vm.token!!,
                            "sample post from ${c.platform}") }) { r ->
                            r.onSuccess { status = "collected one item from ${c.platform}" }
                                .onFailure { error = it.message }
                        }
                    }
                } else {
                    smallAction("Publish update") {
                        vm.call({ ApiClient.socialPublish(c.id, vm.token!!,
                            "A check-in from my Guardian.") }) { r ->
                            r.onSuccess { status = "published to ${c.platform}" }
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
            Text("Connected apps", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("Apple, Google, Microsoft, and Canva apps the Guardian can collect from and act through.",
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
                            r.onSuccess { status = "connected ${entry.provider}/${entry.app}"; reload() }
                                .onFailure { error = it.message }
                        }
                    }) { Text("Connect", color = Jim.BrandA, fontSize = 13.sp, fontWeight = FontWeight.Bold) }
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
                        r.onSuccess { status = "collected from ${c.app}" }
                            .onFailure { error = it.message }
                    }
                }) { Text("Collect", color = Jim.BrandA, fontSize = 13.sp, fontWeight = FontWeight.Bold) }
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
        Text("Community", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        val v = view
        if (v == null) {
            Text("Loading the door…", color = Jim.T3, fontSize = 12.sp)
        } else {
            Text(v.note, color = Jim.T2, fontSize = 12.sp)
            v.language?.let {
                Text("Rooms are listed as QRME serves them; you read $it.",
                    color = Jim.T3, fontSize = 11.sp)
            }
        }
    }

    view?.let { v ->
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text("What JIM does not do", color = Jim.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            PostureRow("Mirror the conversation here", v.posture.mirroredHere)
            PostureRow("Post on your behalf", v.posture.postsOnYourBehalf)
            PostureRow("Share your health data", v.posture.healthDataShared)
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Rooms", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            if (v.rooms.isEmpty()) {
                Text("No rooms open right now. A community shelf that cannot " +
                     "load is a quiet screen, not an error.",
                    color = Jim.T3, fontSize = 12.sp)
            }
            v.rooms.forEach { room ->
                Row(Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween) {
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text(room.topic ?: room.id, color = Jim.Txt, fontSize = 13.sp)
                        Text(roomDetail(room), color = Jim.T3, fontSize = 10.sp)
                    }
                    room.url?.let { url ->
                        SmallAction("Open") {
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
            Text("Near you", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            if (v.places.isEmpty()) {
                Text("No places claimed yet.", color = Jim.T3, fontSize = 12.sp)
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
        Text("Noted that you opened $it — the visit, and nothing from inside it.",
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

private fun roomDetail(room: CommunityRoom): String {
    val bits = mutableListOf<String>()
    room.channel?.let { bits.add(it) }
    if (room.participants > 0) bits.add("${room.participants} here")
    return if (bits.isEmpty()) room.id else bits.joinToString(" · ")
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
        Text("What JIM has learned about you", color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        val p = profile
        if (p != null && p.built) {
            Text("Confidence ${(p.confidence * 100).roundToInt()}% — earned from " +
                 "${p.evidenceItems} things already on your record.",
                color = Jim.T2, fontSize = 12.sp)
            p.whatHelps.entries.sortedBy { it.key }.forEach { (condition, tally) ->
                if (tally.answered > 0) {
                    Row(Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(condition.replace('_', ' '), color = Jim.Txt, fontSize = 14.sp)
                        Text("helped ${tally.helped} of ${tally.answered}",
                            color = if (tally.helped * 2 >= tally.answered) Jim.Green
                                    else Jim.Amber,
                            fontSize = 12.sp)
                    }
                }
            }
            p.tone?.let { Text("Tone you asked for: $it", color = Jim.T3, fontSize = 11.sp) }
            p.occupation?.let { Text("Work you named: $it", color = Jim.T3, fontSize = 11.sp) }
            if (p.vaulted) {
                Text("Sealed in your own vault.", color = Jim.Green, fontSize = 11.sp)
            }
            p.method?.let { Text(it, color = Jim.T3, fontSize = 10.sp) }
        } else {
            Text(p?.note ?: "No profile yet — it is built from the history already " +
                 "on record, here on your own device's backend.",
                color = Jim.T2, fontSize = 12.sp)
        }
        SmallAction(if (busy) "Rebuilding…" else "Rebuild from my history",
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
        Text("Your name here", color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        val p = posture
        if (p == null) {
            Text("Loading…", color = Jim.T3, fontSize = 12.sp)
        } else {
            Text(if (p.anonymous) "You are known here as ${p.knownAs ?: "a pseudonym"}."
                 else "You are enrolled under your own name.",
                color = Jim.Txt, fontSize = 14.sp)
            p.keeps.forEach { Text("✓ $it", color = Jim.Green, fontSize = 12.sp) }
            p.costs.forEach { Text("• $it", color = Jim.Amber, fontSize = 12.sp) }
            if (p.costs.isEmpty() && p.anonymous) {
                Text("A legal name is on record for responders.",
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
fun ProblemReportingCard() {
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
            Text("When something breaks", style = MaterialTheme.typography.titleSmall)

            if (Problems.collectorUrl().isEmpty()) {
                // Not a failure and not a thing to hide: this build has no
                // address compiled in, so there is nothing to consent to.
                Text("This build reports nowhere. Failures are counted on this " +
                     "device and never leave it.",
                     style = MaterialTheme.typography.bodySmall)
            } else if (!answered) {
                Text("This app can send a count of what failed — the operation " +
                     "and the HTTP status, the day, and how many times. Not " +
                     "what you typed, not who you are, not which profile. " +
                     "Nothing that identifies you or anyone else.",
                     style = MaterialTheme.typography.bodySmall)
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedButton(onClick = {
                        Problems.answerNotice(true); answered = true; sending = true
                        // The first moment a send is permitted. Doing it now
                        // rather than at the next launch means the person who
                        // just agreed watches the buffer drain, instead of
                        // being told something happened later.
                        scope.launch(Dispatchers.IO) { Problems.send() }
                    }) { Text("Send counts") }
                    OutlinedButton(onClick = {
                        Problems.answerNotice(false); answered = true; sending = false
                    }) { Text("Do not send") }
                }
            } else {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("Send failure counts", Modifier.weight(1f),
                         style = MaterialTheme.typography.bodyMedium)
                    Switch(checked = sending, onCheckedChange = {
                        sending = it; Problems.setSending(it)
                    })
                }
            }

            TextButton(onClick = { showing = !showing }) {
                Text(if (showing) "Hide what would be sent"
                     else "Show what would be sent")
            }
            if (showing) {
                if (owed.isEmpty()) {
                    Text("Nothing is owed. Either nothing has failed, or " +
                         "everything that has was already reported.",
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
        ProblemReportingCard()
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
