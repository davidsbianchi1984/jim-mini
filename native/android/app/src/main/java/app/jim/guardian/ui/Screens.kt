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
import app.jim.guardian.BaselineMetric
import app.jim.guardian.CheckinResult
import app.jim.guardian.GuardianViewModel
import app.jim.guardian.ApiClient
import app.jim.guardian.Goal
import app.jim.guardian.Guidance
import app.jim.guardian.Habit
import app.jim.guardian.JournalItem
import app.jim.guardian.MonitorResult
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
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(checked = consent, onCheckedChange = { consent = it },
                        colors = CheckboxDefaults.colors(checkedColor = Jim.Green))
                    Text("I consent to the terms of use", color = Jim.Txt, fontSize = 13.sp)
                }
            }
            error?.let { Text(it, color = Jim.Red, fontSize = 13.sp) }
            BrandButton("Get Started", enabled = consent && name.isNotBlank(), busy = busy) {
                error = null
                vm.enroll(name, birthdate, onError = { error = it }, onBusy = { busy = it })
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
