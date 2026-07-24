package app.jim.guardian.ui

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
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import app.jim.guardian.AppConn
import app.jim.guardian.BaselineMetric
import app.jim.guardian.CatalogApp
import app.jim.guardian.CheckinResult
import app.jim.guardian.EmergencyResult
import app.jim.guardian.EscalationPolicy
import app.jim.guardian.Guidance
import app.jim.guardian.GuardianViewModel
import app.jim.guardian.ApiClient
import app.jim.guardian.Goal
import app.jim.guardian.Habit
import app.jim.guardian.LanguageInfo
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

@Composable
fun OverviewScreen(vm: GuardianViewModel) {
    var metrics by remember { mutableStateOf<List<BaselineMetric>?>(null) }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.baseline(vm.uid!!, vm.token!!) }) { r -> metrics = r.getOrDefault(emptyList()) }
    }
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
        OutlinedButton(onClick = { vm.signOut() }, modifier = Modifier.fillMaxWidth(),
            border = androidx.compose.foundation.BorderStroke(1.dp, Jim.Line)) {
            Text("Sign out", color = Jim.T2)
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
            vm.call({ ApiClient.coach(vm.uid!!, vm.token!!, area, message) }) {
                reply = it.getOrNull(); busy = false
            }
        }
        reply?.let { g ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("Coach", color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(g.content, color = Jim.Txt, fontSize = 14.sp)
                GuidanceExtras(g)
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
    val tabs = listOf("Goals", "Habits", "Journal")
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
            else -> JournalPanel(vm)
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

// ---- Safety: Emergency (SOS), escalation policy, robot helpers ----

@Composable
fun SafetyScreen(vm: GuardianViewModel) {
    var tab by remember { mutableIntStateOf(0) }
    val tabs = listOf("SOS", "Med ID", "Policy", "Robots")
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)) {
        TabRow(selectedTabIndex = tab, containerColor = Jim.Card, contentColor = Jim.BrandA) {
            tabs.forEachIndexed { i, t ->
                Tab(selected = tab == i, onClick = { tab = i },
                    text = { Text(t, fontSize = 13.sp) })
            }
        }
        when (tab) {
            0 -> SOSPanel(vm)
            1 -> MedicalPanel(vm)
            2 -> PolicyPanel(vm)
            else -> RobotsPanel(vm)
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
    val tabs = listOf("Monitor", "Check-in", "Coach")
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
            else -> CoachScreen(vm)
        }
    }
}

// ---- Connect: data sources, social platforms, connected apps ----

@Composable
fun ConnectScreen(vm: GuardianViewModel) {
    var tab by remember { mutableIntStateOf(0) }
    val tabs = listOf("Sources", "Social", "Apps")
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
            else -> AppsPanel(vm)
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
