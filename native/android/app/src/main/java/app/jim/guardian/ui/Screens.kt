package app.jim.guardian.ui

import android.content.Intent
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
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
import app.jim.guardian.CommunityFeedItemK
import app.jim.guardian.CommunityFeedViewK
import app.jim.guardian.CommunityVisitRowK
import app.jim.guardian.ExcursionLearnedK
import app.jim.guardian.ExcursionRowK
import app.jim.guardian.HealthK
import app.jim.guardian.TranscribedK
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
import app.jim.guardian.MedsBoard
import app.jim.guardian.AdherenceRow
import app.jim.guardian.VigilState
import app.jim.guardian.BandRow
import app.jim.guardian.VoiceSettingsOut
import app.jim.guardian.MailSettingsOut
import app.jim.guardian.TutorialOutline
import app.jim.guardian.TutorialStep
import app.jim.guardian.TutorialProgress
import app.jim.guardian.HelpAnswer
import app.jim.guardian.DockVocabulary
import app.jim.guardian.DockState
import app.jim.guardian.DockFace
import app.jim.guardian.DockWhere
import app.jim.guardian.WatchSetup
import app.jim.guardian.PairInfo
import app.jim.guardian.DeviceRow
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
import app.jim.guardian.EnrollResult
import app.jim.guardian.OAuthDoor
import app.jim.guardian.SessionStarted
import app.jim.guardian.ActivityWatchK
import app.jim.guardian.CalmHistoryRow
import app.jim.guardian.CalmSessionRow
import app.jim.guardian.CalmStarted
import app.jim.guardian.InsightRowK
import app.jim.guardian.MealPlanK
import app.jim.guardian.ReportK
import app.jim.guardian.WorkoutPlanK
import app.jim.guardian.CatalogStarterK
import app.jim.guardian.ClinicianSearchK
import app.jim.guardian.ProviderSummaryK
import app.jim.guardian.ReferralPreparedK
import app.jim.guardian.ReferralRequestRowK
import app.jim.guardian.SpecialistRowK
import app.jim.guardian.SpecialistTaskRowK
import app.jim.guardian.SpecialistTaskViewK
import app.jim.guardian.TaskStartedK
import app.jim.guardian.AccessLogK
import app.jim.guardian.CloudStatusK
import app.jim.guardian.ContributionK
import app.jim.guardian.PageRowK
import app.jim.guardian.PlanRowK
import app.jim.guardian.BudgetRowK
import app.jim.guardian.MembershipK
import app.jim.guardian.BeaconAlarmK
import app.jim.guardian.BeaconCardK
import app.jim.guardian.BeaconRowK
import app.jim.guardian.RelayChannelK
import app.jim.guardian.RelayRosterK
import app.jim.guardian.RelayRotaK
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
            Text(L10n.t("nw.hero", language), color = Jim.Txt, fontSize = 22.sp,
                fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.CenterHorizontally))
            Text(L10n.t("nw.pitch", language),
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
                    Text(L10n.t("onb.consent", language), color = Jim.Txt, fontSize = 13.sp)
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
            // Or a real account: email-verified, recoverable, and the same
            // one the console and the other devices share.
            AccountPanel(vm, language)
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


/** The account the phones never had: the shells enrolled anonymously while
 *  the console signed up with an email, verified the inbox, recovered lost
 *  passwords and opened the "Sign in with ..." doors. Same routes, this
 *  screen. */
@Composable
private fun AccountPanel(vm: GuardianViewModel, language: String) {
    var mode by remember { mutableStateOf("up") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var name by remember { mutableStateOf("") }
    var code by remember { mutableStateOf("") }
    var consent by remember { mutableStateOf(false) }
    var pending by remember { mutableStateOf(false) }
    var doors by remember { mutableStateOf<List<OAuthDoor>>(emptyList()) }
    var notice by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    LaunchedEffect(Unit) {
        runCatching { ApiClient.oauthProviders() }.onSuccess { doors = it }
    }
    fun act(block: suspend () -> Unit) {
        busy = true; error = null; notice = null
        scope.launch {
            runCatching { block() }.onFailure { error = it.message }
            busy = false
        }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            listOf("up" to L10n.t("onb.create", language),
                   "in" to L10n.t("onb.signin", language),
                   "reset" to L10n.t("onb.forgot", language)).forEach { (value, label) ->
                FilterChip(selected = mode == value,
                    onClick = { mode = value; error = null; notice = null },
                    label = { Text(label, fontSize = 11.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = Jim.BrandA,
                        selectedLabelColor = Color.White, labelColor = Jim.T2))
            }
        }
        labeledField(L10n.t("onb.email", language), email,
            L10n.t("onb.email.ph", language)) { email = it }

        if (mode == "up" && !pending) {
            labeledField(L10n.t("onb.yourname", language), name, "") { name = it }
            labeledField(L10n.t("onb.password.min", language), password, "") { password = it }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Checkbox(checked = consent, onCheckedChange = { consent = it },
                    colors = CheckboxDefaults.colors(checkedColor = Jim.Green))
                Text(L10n.t("onb.consent", language), color = Jim.Txt, fontSize = 12.sp)
            }
            BrandButton(L10n.t("onb.create", language),
                enabled = !busy && consent && email.isNotBlank()
                        && password.isNotBlank() && name.isNotBlank(), busy = busy) {
                act {
                    val r = ApiClient.signup(email.trim(), password, name, language)
                    if (r.verified && r.session != null) vm.signIn(r.session)
                    else { pending = true; notice = r.codeDelivery }
                }
            }
        }

        if (mode == "up" && pending) {
            Text("${L10n.t("onb.verify.sent", language)} $email",
                color = Jim.T2, fontSize = 12.sp)
            Text(L10n.t("onb.verify.type", language), color = Jim.T3, fontSize = 11.sp)
            labeledField(L10n.t("onb.code", language), code, "123456") { code = it }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically) {
                BrandButton(L10n.t("onb.signin", language),
                    enabled = !busy && code.isNotBlank(), busy = busy) {
                    act { vm.signIn(ApiClient.verifyEmail(email.trim(), code.trim())) }
                }
                SmallAction(L10n.t("onb.code.resend", language)) {
                    act { notice = ApiClient.resendCode(email.trim()) }
                }
            }
        }

        if (mode == "in") {
            labeledField(L10n.t("onb.password.min", language), password, "") { password = it }
            BrandButton(L10n.t("onb.signin", language),
                enabled = !busy && email.isNotBlank() && password.isNotBlank(),
                busy = busy) {
                act {
                    val r = ApiClient.signin(email.trim(), password)
                    vm.signIn(EnrollResult(r.userId, r.displayName, r.userToken))
                }
            }
        }

        if (mode == "reset") {
            Text(L10n.t("onb.reset.hint", language), color = Jim.T2, fontSize = 12.sp)
            SmallAction(L10n.t("onb.reset.send", language)) {
                act { notice = ApiClient.requestPasswordReset(email.trim()) }
            }
            labeledField(L10n.t("onb.reset.code", language), code, "123456") { code = it }
            labeledField(L10n.t("onb.password.min", language), password, "") { password = it }
            BrandButton(L10n.t("onb.reset.send", language),
                enabled = !busy && email.isNotBlank() && code.isNotBlank()
                        && password.isNotBlank(), busy = busy) {
                act {
                    // Every old session died with the old password; sign in
                    // fresh with the new one.
                    ApiClient.resetPassword(email.trim(), code.trim(), password)
                    code = ""; mode = "in"
                    notice = L10n.t("onb.signin", language)
                }
            }
        }

        if (doors.isNotEmpty() && mode != "reset") {
            doors.forEach { door ->
                val label = L10n.t("onb.signwith", language)
                    .replace("{mode}", L10n.t(
                        if (mode == "up") "onb.mode.up" else "onb.mode.in", language))
                    .replace("{provider}", door.name)
                SmallAction(if (door.configured) label
                            else label + L10n.t("onb.oauth.absent", language)) {
                    // Open the provider's page in the system browser, then
                    // poll the claim: the phone never sees the provider
                    // conversation — only whether its state was honoured.
                    if (door.configured && !busy) act {
                        val started = ApiClient.oauthStart(door.provider)
                        context.startActivity(
                            Intent(Intent.ACTION_VIEW, Uri.parse(started.url)))
                        for (i in 0 until 40) {
                            delay(3000)
                            val claim = ApiClient.oauthClaim(started.state)
                            if (claim.ready) {
                                claim.session?.let { vm.signIn(it) }
                                break
                            }
                        }
                    }
                }
            }
        }

        notice?.let { Text(it, color = Jim.T2, fontSize = 12.sp) }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
    }
}

/** This sitting: a named login session, so any device that starts one
 *  resumes the same conversational thread — including one begun with a
 *  QRME specialist from another product. */
@Composable
private fun SittingPanel(vm: GuardianViewModel) {
    var session by remember { mutableStateOf<SessionStarted?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(L10n.t("att.sit", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically) {
            BrandButton(L10n.t("att.sit.start", vm.language),
                enabled = !busy, busy = busy) {
                busy = true; error = null
                vm.call({ ApiClient.startSession(vm.uid!!, vm.token!!, "android") }) { r ->
                    r.onSuccess { session = it }.onFailure { error = it.message }
                    busy = false
                }
            }
            SmallAction(L10n.t("att.sit.end", vm.language)) {
                session?.let { sitting ->
                    if (!busy) {
                        busy = true; error = null
                        vm.call({ ApiClient.endSession(vm.uid!!, vm.token!!, sitting.id) }) { r ->
                            r.onSuccess { session = null }.onFailure { error = it.message }
                            busy = false
                        }
                    }
                }
            }
        }
        session?.let { s ->
            Text(L10n.t("att.sit.prior", vm.language)
                    .replace("{id}", s.id).replace("{n}", s.priorSessions.toString()),
                color = Jim.T2, fontSize = 12.sp)
            s.memory?.let { Text(it, color = Jim.T3, fontSize = 11.sp) }
            s.turns.forEach { turn ->
                Text("${turn.role}: ${turn.content}", color = Jim.T2,
                    fontSize = 11.sp, maxLines = 2)
            }
            s.continuityNote?.let { Text(it, color = Jim.T3, fontSize = 11.sp) }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
    }
}


/** Tell it what you did: an ordinary activity is context, not a reading —
 *  the why behind a moved heart rate before it has to guess one. */
@Composable
private fun ActivityPanel(vm: GuardianViewModel) {
    var activity by remember { mutableStateOf("") }
    var note by remember { mutableStateOf("") }
    var watch by remember { mutableStateOf<ActivityWatchK?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(L10n.t("aim.activity", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("aim.activity.pitch", vm.language), color = Jim.T2, fontSize = 12.sp)
        labeledField(L10n.t("aim.activity", vm.language), activity,
            L10n.t("aim.activity.ph", vm.language)) { activity = it }
        labeledField(L10n.t("brg.told.note.ph", vm.language), note, "") { note = it }
        BrandButton(L10n.t("aim.activity.log", vm.language),
            enabled = !busy && activity.isNotBlank(), busy = busy) {
            busy = true; error = null
            vm.call({ ApiClient.observeActivity(vm.uid!!, vm.token!!,
                activity.trim(), note) }) { r ->
                r.onSuccess { watch = it; activity = ""; note = "" }
                    .onFailure { error = it.message }
                busy = false
            }
        }
        watch?.intervention?.let { g ->
            // The proactive voice: it noticed a struggle building and spoke
            // before being asked.
            Text(g.content, color = Jim.Amber, fontSize = 12.sp)
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
    }
}

/** Guided calm, a workout for the time you have, and a day of meals that
 *  fits: protocols and templates, not generations. */
@Composable
private fun WellnessPanel(vm: GuardianViewModel) {
    var catalog by remember { mutableStateOf<List<CalmSessionRow>>(emptyList()) }
    var started by remember { mutableStateOf<CalmStarted?>(null) }
    var history by remember { mutableStateOf<List<CalmHistoryRow>>(emptyList()) }
    var minutes by remember { mutableIntStateOf(20) }
    var level by remember { mutableStateOf("beginner") }
    var focus by remember { mutableStateOf("mobility") }
    var workout by remember { mutableStateOf<WorkoutPlanK?>(null) }
    var goal by remember { mutableStateOf("eat_healthier") }
    var days by remember { mutableIntStateOf(2) }
    var meals by remember { mutableStateOf<MealPlanK?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    fun reloadHistory() {
        vm.call({ ApiClient.calmHistory(vm.uid!!, vm.token!!) }) { r ->
            history = r.getOrDefault(emptyList())
        }
    }
    LaunchedEffect(Unit) {
        runCatching { ApiClient.calmCatalog() }.onSuccess { catalog = it }
        reloadHistory()
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(L10n.t("wel.calm", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("wel.calm.pitch", vm.language).replace("{spoken}", ""),
            color = Jim.T2, fontSize = 12.sp)
        catalog.chunked(2).forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                row.forEach { session ->
                    FilterChip(selected = started?.kind == session.kind,
                        onClick = {
                            busy = true; error = null
                            vm.call({ ApiClient.startCalm(vm.uid!!, vm.token!!,
                                session.kind) }) { r ->
                                r.onSuccess { started = it; reloadHistory() }
                                    .onFailure { error = it.message }
                                busy = false
                            }
                        },
                        label = { Text(L10n.t("wel.calm.tile", vm.language)
                            .replace("{title}", session.title)
                            .replace("{n}", session.minutes.toString()),
                            fontSize = 11.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Jim.BrandA,
                            selectedLabelColor = Color.White, labelColor = Jim.T2))
                }
            }
        }
        started?.let { s ->
            s.steps.forEachIndexed { index, step ->
                Text(L10n.t("wel.calm.step", vm.language)
                    .replace("{i}", (index + 1).toString())
                    .replace("{n}", s.steps.size.toString())
                    .replace("{sec}", step.seconds.toString())
                    + " \u2014 " + step.say, color = Jim.T2, fontSize = 11.sp)
            }
            Text(s.note, color = Jim.T3, fontSize = 11.sp)
        }
        history.take(3).forEach { row ->
            Text("${row.title} \u00b7 ${row.at}", color = Jim.T3, fontSize = 11.sp)
        }

        Text(L10n.t("wel.work", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Text(L10n.t("wel.work.minutes", vm.language), color = Jim.T2, fontSize = 12.sp)
            listOf(10, 20, 40).forEach { m ->
                FilterChip(selected = minutes == m, onClick = { minutes = m },
                    label = { Text("$m", fontSize = 11.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = Jim.BrandA,
                        selectedLabelColor = Color.White, labelColor = Jim.T2))
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Text(L10n.t("wel.work.level", vm.language), color = Jim.T2, fontSize = 12.sp)
            listOf("beginner", "intermediate", "advanced").forEach { l ->
                FilterChip(selected = level == l, onClick = { level = l },
                    label = { Text(l, fontSize = 11.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = Jim.BrandA,
                        selectedLabelColor = Color.White, labelColor = Jim.T2))
            }
        }
        labeledField(L10n.t("wel.work.focus", vm.language), focus, "") { focus = it }
        BrandButton(L10n.t("wel.work.build", vm.language), enabled = !busy, busy = busy) {
            busy = true; error = null
            vm.call({ ApiClient.workoutPlan(vm.uid!!, vm.token!!, minutes,
                level, focus.trim()) }) { r ->
                r.onSuccess { workout = it }.onFailure { error = it.message }
                busy = false
            }
        }
        workout?.blocks?.take(8)?.forEach { block ->
            Text(block.name + L10n.t("wel.work.block", vm.language)
                .replace("{sec}", block.seconds.toString())
                .replace("{cue}", block.cue), color = Jim.T2, fontSize = 11.sp)
        }

        Text(L10n.t("wel.meals", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Text(L10n.t("wel.meals.goal", vm.language), color = Jim.T2, fontSize = 12.sp)
        }
        listOf("lose_weight" to "wel.meals.lose", "gain_muscle" to "wel.meals.gain",
               "eat_healthier" to "wel.meals.healthier").chunked(2).forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                row.forEach { (value, key) ->
                    FilterChip(selected = goal == value, onClick = { goal = value },
                        label = { Text(L10n.t(key, vm.language), fontSize = 11.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Jim.BrandA,
                            selectedLabelColor = Color.White, labelColor = Jim.T2))
                }
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Text(L10n.t("wel.meals.days", vm.language), color = Jim.T2, fontSize = 12.sp)
            listOf(1, 2, 3, 7).forEach { d ->
                FilterChip(selected = days == d, onClick = { days = d },
                    label = { Text("$d", fontSize = 11.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = Jim.BrandA,
                        selectedLabelColor = Color.White, labelColor = Jim.T2))
            }
        }
        BrandButton(L10n.t("wel.meals.plan", vm.language), enabled = !busy, busy = busy) {
            busy = true; error = null
            vm.call({ ApiClient.mealPlan(vm.uid!!, vm.token!!, goal, days) }) { r ->
                r.onSuccess { meals = it }.onFailure { error = it.message }
                busy = false
            }
        }
        meals?.let { m ->
            Text(L10n.t("wel.meals.shape", vm.language)
                .replace("{why}", m.why).replace("{kcal}", m.kcal.toString()),
                color = Jim.T2, fontSize = 11.sp)
            m.days.forEach { day ->
                Text(L10n.t("wel.meals.day", vm.language)
                    .replace("{n}", day.day.toString()),
                    color = Jim.T2, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                day.meals.forEach { Text(it, color = Jim.T3, fontSize = 11.sp) }
            }
            Text(m.disclaimer, color = Jim.T3, fontSize = 10.sp)
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
    }
}

/** The Guardian's bearing: the tone it speaks in, what it was told, whether
 *  its answers landed, and what it made of all that. */
@Composable
private fun BearingPanel(vm: GuardianViewModel) {
    var tone by remember { mutableStateOf("balanced") }
    var condition by remember { mutableStateOf("anxiety") }
    var conditionNote by remember { mutableStateOf("") }
    var known by remember { mutableStateOf<List<String>>(emptyList()) }
    var source by remember { mutableStateOf("") }
    var refused by remember { mutableStateOf<String?>(null) }
    var said by remember { mutableStateOf<String?>(null) }
    var report by remember { mutableStateOf<ReportK?>(null) }
    var insightRows by remember { mutableStateOf<List<InsightRowK>>(emptyList()) }
    var eventCount by remember { mutableIntStateOf(0) }
    var calmCount by remember { mutableIntStateOf(0) }
    var exchangeCount by remember { mutableIntStateOf(0) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(Unit) {
        runCatching { ApiClient.progressReport(vm.uid!!, vm.token!!) }
            .onSuccess { report = it }
        // Insights are a Pro capability; a plan refusal reads as none yet.
        runCatching { ApiClient.insights(vm.uid!!, vm.token!!) }
            .onSuccess { insightRows = it }
        runCatching { ApiClient.eventsCount(vm.uid!!, vm.token!!) }
            .onSuccess { eventCount = it }
        runCatching { ApiClient.calmHistory(vm.uid!!, vm.token!!) }
            .onSuccess { calmCount = it.size }
        runCatching { ApiClient.coachExchangeCount(vm.uid!!, vm.token!!) }
            .onSuccess { exchangeCount = it }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(L10n.t("brg.speak.tone", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp),
            verticalAlignment = Alignment.CenterVertically) {
            listOf("direct" to "brg.speak.direct", "balanced" to "brg.speak.balanced",
                   "cautious" to "brg.speak.cautious").forEach { (t, key) ->
                FilterChip(selected = tone == t, onClick = { tone = t },
                    label = { Text(L10n.t(key, vm.language), fontSize = 11.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = Jim.BrandA,
                        selectedLabelColor = Color.White, labelColor = Jim.T2))
            }
            SmallAction(L10n.t("brg.speak.go", vm.language), enabled = !busy) {
                busy = true; error = null
                vm.call({ ApiClient.setPersonality(vm.uid!!, vm.token!!, tone) }) {
                    busy = false
                }
            }
        }

        Text(L10n.t("brg.told", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        listOf("anxiety", "depression", "stress", "phobia", "financial_stress",
               "relationship", "physical_distress", "physical_injury")
            .chunked(3).forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                row.forEach { c ->
                    FilterChip(selected = condition == c, onClick = { condition = c },
                        label = { Text(c, fontSize = 10.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Jim.BrandA,
                            selectedLabelColor = Color.White, labelColor = Jim.T2))
                }
            }
        }
        labeledField(L10n.t("brg.told", vm.language), conditionNote,
            L10n.t("brg.told.note.ph", vm.language)) { conditionNote = it }
        BrandButton(L10n.t("brg.told.tell", vm.language), enabled = !busy, busy = busy) {
            busy = true; error = null
            vm.call({ ApiClient.declareCondition(vm.uid!!, vm.token!!,
                condition, conditionNote) }) { r ->
                r.onSuccess { known = it; conditionNote = "" }
                    .onFailure { error = it.message }
                busy = false
            }
        }
        if (known.isNotEmpty()) {
            Text(known.joinToString(" \u00b7 "), color = Jim.T2, fontSize = 12.sp)
        }
        labeledField(L10n.t("brg.told.ctx", vm.language), source,
            L10n.t("brg.told.src.ph", vm.language)) { source = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically) {
            SmallAction(L10n.t("brg.told.ctx", vm.language),
                enabled = !busy && source.isNotBlank()) {
                busy = true; refused = null
                vm.call({ ApiClient.giveContext(vm.uid!!, vm.token!!,
                    source.trim(), "event",
                    org.json.JSONObject().put("title", "something on the calendar")) }) { r ->
                    r.onFailure { refused = it.message }
                    busy = false
                }
            }
            SmallAction(L10n.t("brg.told.say", vm.language), enabled = !busy) {
                busy = true; error = null
                vm.call({ ApiClient.companionCheckin(vm.uid!!, vm.token!!) }) { r ->
                    r.onSuccess { said = it }.onFailure { error = it.message }
                    busy = false
                }
            }
        }
        refused?.let {
            Text(L10n.t("brg.told.refused", vm.language).replace("{err}", it),
                color = Jim.Amber, fontSize = 11.sp)
        }
        said?.let { Text(it, color = Jim.T2, fontSize = 12.sp) }

        Text(L10n.t("brg.tell", vm.language), color = Jim.T2, fontSize = 12.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            SmallAction(L10n.t("brg.tell.good", vm.language), enabled = !busy) {
                busy = true
                vm.call({ ApiClient.sendGuidanceFeedback(vm.uid!!, vm.token!!, "up") }) {
                    busy = false
                }
            }
            SmallAction(L10n.t("brg.tell.bad", vm.language), enabled = !busy) {
                busy = true
                vm.call({ ApiClient.sendGuidanceFeedback(vm.uid!!, vm.token!!, "down") }) {
                    busy = false
                }
            }
        }

        Text(L10n.t("brg.made", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        report?.let { r ->
            Text(L10n.t("brg.made.stats", vm.language)
                .replace("{c}", r.checkinCount.toString())
                .replace("{m}", if (r.avgMood.isNaN()) "\u2014"
                                else String.format("%.1f", r.avgMood))
                .replace("{i}", insightRows.size.toString())
                .replace("{e}", eventCount.toString())
                .replace("{s}", calmCount.toString())
                .replace("{x}", exchangeCount.toString()),
                color = Jim.T2, fontSize = 12.sp)
        }
        insightRows.take(3).forEach { Text(it.message, color = Jim.T3, fontSize = 11.sp) }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
    }
}


/** The specialist economy: who stands behind each condition, the QRME
 *  attach bracket, handing over multi-step work, preparing a referral
 *  (nothing releases without QRME's signing ceremony), and the consented
 *  provider's view of you. */
@Composable
private fun SpecialistsPanel(vm: GuardianViewModel) {
    var roster by remember { mutableStateOf<List<SpecialistRowK>>(emptyList()) }
    var starters by remember { mutableStateOf<List<CatalogStarterK>?>(null) }
    var catalogRefused by remember { mutableStateOf<String?>(null) }
    var condition by remember { mutableStateOf("anxiety") }
    var goal by remember { mutableStateOf("") }
    var started by remember { mutableStateOf<TaskStartedK?>(null) }
    var tasks by remember { mutableStateOf<List<SpecialistTaskRowK>>(emptyList()) }
    var opened by remember { mutableStateOf<SpecialistTaskViewK?>(null) }
    var clinicians by remember { mutableStateOf<ClinicianSearchK?>(null) }
    var prepared by remember { mutableStateOf<ReferralPreparedK?>(null) }
    var requests by remember { mutableStateOf<List<ReferralRequestRowK>>(emptyList()) }
    var provider by remember { mutableStateOf<ProviderSummaryK?>(null) }
    var providerRefused by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    fun reloadRoster() {
        vm.call({ ApiClient.specialists() }) { r -> roster = r.getOrDefault(emptyList()) }
    }
    fun reloadTasks() {
        vm.call({ ApiClient.specialistTasks(vm.uid!!, vm.token!!) }) { r ->
            tasks = r.getOrDefault(emptyList())
        }
    }
    fun reloadRequests() {
        vm.call({ ApiClient.referralRequests(vm.uid!!, vm.token!!) }) { r ->
            requests = r.getOrDefault(emptyList())
        }
    }
    LaunchedEffect(Unit) {
        reloadRoster()
        vm.call({ ApiClient.specialistsCatalog() }) { r ->
            r.onSuccess { starters = it }.onFailure { catalogRefused = it.message }
        }
        reloadTasks(); reloadRequests()
    }
    fun act(block: suspend () -> Unit, then: () -> Unit = {}) {
        busy = true; error = null
        vm.call({ block() }) { r ->
            r.onFailure { error = it.message }
            busy = false; then()
        }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(L10n.t("att.spec", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            SmallAction(L10n.t("att.spec.local", vm.language), enabled = !busy) {
                act({ ApiClient.seedSpecialists() }) { reloadRoster() }
            }
            SmallAction(L10n.t("att.spec.hosted", vm.language), enabled = !busy) {
                act({ ApiClient.seedTandemSpecialists() }) { reloadRoster() }
            }
        }
        if (roster.isEmpty()) {
            Text(L10n.t("att.spec.none", vm.language), color = Jim.T3, fontSize = 11.sp)
        }
        roster.forEach { row ->
            Text("${row.condition} \u2014 ${row.label} \u00b7 ${row.mode}",
                color = Jim.T2, fontSize = 11.sp)
        }

        Text(L10n.t("ct.spec", vm.language), color = Jim.T2, fontSize = 12.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("ct.spec.choose", vm.language), color = Jim.T3, fontSize = 11.sp)
        catalogRefused?.let { Text(it, color = Jim.T3, fontSize = 11.sp) }
        starters?.let { rows ->
            if (rows.isEmpty()) {
                Text(L10n.t("ct.spec.empty", vm.language), color = Jim.T3, fontSize = 11.sp)
            }
            rows.take(6).forEach { starter ->
                Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    Text(starter.displayName ?: starter.profileId ?: "",
                        color = Jim.Txt, fontSize = 12.sp, modifier = Modifier.weight(1f))
                    SmallAction(L10n.t("ct.spec.attach", vm.language),
                        enabled = !busy && starter.profileId != null) {
                        act({ ApiClient.attachSpecialist(condition,
                            starter.profileId!!, starter.displayName
                                ?: starter.profileId!!) }) { reloadRoster() }
                    }
                }
            }
        }

        Text(L10n.t("att.hand", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        listOf("anxiety", "depression", "stress", "phobia", "financial_stress",
               "relationship", "physical_distress", "physical_injury")
            .chunked(3).forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                row.forEach { c ->
                    FilterChip(selected = condition == c, onClick = { condition = c },
                        label = { Text(c, fontSize = 10.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Jim.BrandA,
                            selectedLabelColor = Color.White, labelColor = Jim.T2))
                }
            }
        }
        labeledField(L10n.t("att.hand", vm.language), goal,
            L10n.t("att.hand.ph", vm.language)) { goal = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically) {
            BrandButton(L10n.t("att.hand.go", vm.language),
                enabled = !busy && goal.isNotBlank(), busy = busy) {
                busy = true; error = null
                vm.call({ ApiClient.startSpecialistTask(vm.uid!!, vm.token!!,
                    condition, goal.trim()) }) { r ->
                    r.onSuccess { started = it; goal = "" }
                        .onFailure { error = it.message }
                    busy = false; reloadTasks()
                }
            }
            SmallAction(L10n.t("att.hand.who", vm.language), enabled = !busy) {
                busy = true; error = null
                vm.call({ ApiClient.referralClinicians(vm.uid!!, vm.token!!,
                    condition) }) { r ->
                    r.onSuccess { clinicians = it }.onFailure { error = it.message }
                    busy = false
                }
            }
        }
        started?.let { s ->
            Text(if (s.started) (s.id ?: "") else (s.reason ?: ""),
                color = if (s.started) Jim.Green else Jim.Amber, fontSize = 11.sp)
        }
        clinicians?.let { c ->
            c.labels.take(4).forEach { Text(it, color = Jim.T2, fontSize = 11.sp) }
            if (c.labels.isEmpty()) c.reason?.let {
                Text(it, color = Jim.T3, fontSize = 11.sp)
            }
        }
        tasks.forEach { task ->
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text("${task.goal} \u00b7 ${task.status}", color = Jim.T2,
                    fontSize = 11.sp, modifier = Modifier.weight(1f))
                SmallAction(L10n.t("att.open", vm.language), enabled = !busy) {
                    busy = true
                    vm.call({ ApiClient.specialistTask(vm.uid!!, vm.token!!,
                        task.id) }) { r ->
                        r.onSuccess { opened = it }.onFailure { error = it.message }
                        busy = false
                    }
                }
                SmallAction(L10n.t("att.advance", vm.language), enabled = !busy) {
                    busy = true
                    vm.call({ ApiClient.advanceSpecialistTask(vm.uid!!, vm.token!!,
                        task.id) }) { r ->
                        r.onSuccess { opened = it }.onFailure { error = it.message }
                        busy = false; reloadTasks()
                    }
                }
            }
        }
        opened?.let { o ->
            Text(o.status + (o.nextPhase?.let { " \u00b7 $it" } ?: "")
                + (o.note?.let { " \u2014 $it" } ?: ""),
                color = Jim.T3, fontSize = 11.sp)
        }

        Text(L10n.t("att.ref", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        SmallAction(L10n.t("att.ref.prep", vm.language).replace("{c}", condition),
            enabled = !busy) {
            busy = true; error = null
            vm.call({ ApiClient.prepareReferral(vm.uid!!, vm.token!!, condition,
                "prv_local") }) { r ->
                r.onSuccess { prepared = it }.onFailure { error = it.message }
                busy = false; reloadRequests()
            }
        }
        prepared?.let { p ->
            Text(if (p.prepared) (p.note ?: "") else (p.reason ?: ""),
                color = if (p.prepared) Jim.T2 else Jim.Amber, fontSize = 11.sp)
        }
        if (requests.isEmpty()) {
            Text(L10n.t("att.ref.none", vm.language), color = Jim.T3, fontSize = 11.sp)
        }
        requests.forEach { request ->
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(request.condition, color = Jim.T2, fontSize = 11.sp,
                    modifier = Modifier.weight(1f))
                SmallAction(L10n.t("att.ref.released", vm.language), enabled = !busy) {
                    act({ ApiClient.markReferralReleased(vm.uid!!, vm.token!!,
                        request.id) })
                }
            }
        }

        SmallAction(L10n.t("att.med.see", vm.language), enabled = !busy) {
            busy = true; providerRefused = null
            vm.call({ ApiClient.providerSummary(vm.uid!!, vm.token!!) }) { r ->
                r.onSuccess { provider = it }
                    .onFailure { providerRefused = it.message }
                busy = false
            }
        }
        provider?.let { p ->
            val joined = p.conditions.joinToString(", ")
            Text("${p.displayName} \u00b7 $joined \u00b7 ${p.escalations}",
                color = Jim.T2, fontSize = 11.sp)
        }
        providerRefused?.let { Text(it, color = Jim.T3, fontSize = 11.sp) }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
    }
}


/** The record and the veil: who has read your record, where the answers
 *  come from, what you contribute and how to stop, what went out in your
 *  name, and the plans this deployment offers. */
@Composable
private fun VeilPanel(vm: GuardianViewModel) {
    var log by remember { mutableStateOf<AccessLogK?>(null) }
    var cloud by remember { mutableStateOf<CloudStatusK?>(null) }
    var contribution by remember { mutableStateOf<ContributionK?>(null) }
    var revokedNote by remember { mutableStateOf<String?>(null) }
    var incidentLines by remember { mutableStateOf<List<String>>(emptyList()) }
    var pageRows by remember { mutableStateOf<List<PageRowK>>(emptyList()) }
    var locality by remember { mutableStateOf("") }
    var savedLocality by remember { mutableStateOf<String?>(null) }
    var planRows by remember { mutableStateOf<List<PlanRowK>>(emptyList()) }
    var current by remember { mutableStateOf<MembershipK?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(Unit) {
        runCatching { ApiClient.cloudStatus() }.onSuccess { cloud = it }
        vm.call({ ApiClient.membership(vm.uid!!, vm.token!!) }) { r ->
            r.onSuccess { current = it }
        }
        runCatching { ApiClient.plans() }.onSuccess { planRows = it }
        vm.call({ ApiClient.accessLog(vm.uid!!, vm.token!!) }) { r ->
            r.onSuccess { log = it }
        }
        vm.call({ ApiClient.cloudContribution(vm.uid!!, vm.token!!) }) { r ->
            r.onSuccess { contribution = it }
        }
        vm.call({ ApiClient.incidents(vm.uid!!, vm.token!!) }) { r ->
            r.onSuccess { incidentLines = it }
        }
        vm.call({ ApiClient.pages(vm.uid!!, vm.token!!) }) { r ->
            r.onSuccess { pageRows = it }
        }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(L10n.t("hld.log", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        log?.let { l ->
            if (l.vaulted) {
                Text(L10n.t("hld.log.vaulted", vm.language), color = Jim.Green,
                    fontSize = 11.sp)
            }
            if (l.recordKept) {
                Text(L10n.t("hld.log.kept", vm.language), color = Jim.T2, fontSize = 11.sp)
                l.entries.take(5).forEach { Text(it, color = Jim.T3, fontSize = 11.sp) }
            } else {
                Text(L10n.t("hld.log.empty", vm.language), color = Jim.T3, fontSize = 11.sp)
            }
            Text(l.note, color = Jim.T3, fontSize = 10.sp)
        }

        Text(L10n.t("hld.where", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        cloud?.let { c ->
            Text(L10n.t("hld.where.cloud", vm.language)
                .replace("{model}", c.model ?: "none")
                .replace("{fallback}", c.fallback), color = Jim.T2, fontSize = 11.sp)
            Text(c.contribution, color = Jim.T3, fontSize = 10.sp)
        }

        Text(L10n.t("set.cloud", vm.language), color = Jim.T2, fontSize = 12.sp,
            fontWeight = FontWeight.Bold)
        contribution?.let { c ->
            Text(c.policy, color = Jim.T3, fontSize = 10.sp)
            if (c.optedIn) {
                SmallAction(L10n.t("set.cloud.stop", vm.language), enabled = !busy) {
                    busy = true; error = null
                    vm.call({ ApiClient.revokeCloudContribution(vm.uid!!, vm.token!!) }) { r ->
                        r.onSuccess { revokedNote = it }
                            .onFailure { error = it.message }
                        busy = false
                        vm.call({ ApiClient.cloudContribution(vm.uid!!, vm.token!!) }) { again ->
                            again.onSuccess { contribution = it }
                        }
                    }
                }
            }
        }
        revokedNote?.let { Text(it, color = Jim.T2, fontSize = 11.sp) }

        Text(L10n.t("sfy.pages", vm.language), color = Jim.T2, fontSize = 12.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("sfy.pages.pitch", vm.language), color = Jim.T3, fontSize = 10.sp)
        if (pageRows.isEmpty()) {
            Text(L10n.t("sfy.pages.none", vm.language), color = Jim.T3, fontSize = 11.sp)
        }
        pageRows.take(5).forEach { p ->
            Text("${p.to} \u00b7 ${p.sentAt}",
                color = if (p.delivered) Jim.Green else Jim.T2, fontSize = 11.sp)
        }
        Text(L10n.t("sfy.history", vm.language), color = Jim.T2, fontSize = 12.sp,
            fontWeight = FontWeight.Bold)
        if (incidentLines.isEmpty()) {
            Text(L10n.t("sfy.history.none", vm.language), color = Jim.T3, fontSize = 11.sp)
        }
        incidentLines.take(5).forEach { Text(it, color = Jim.Amber, fontSize = 11.sp) }

        Text(L10n.t("set.loc", vm.language), color = Jim.T2, fontSize = 12.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("set.loc.pitch", vm.language), color = Jim.T3, fontSize = 10.sp)
        labeledField(L10n.t("set.loc", vm.language), locality,
            L10n.t("set.loc.ph", vm.language)) { locality = it }
        SmallAction(L10n.t("set.save", vm.language), enabled = !busy) {
            busy = true; error = null
            vm.call({ ApiClient.setLocality(vm.uid!!, vm.token!!,
                locality.trim()) }) { r ->
                r.onSuccess { savedLocality = it }.onFailure { error = it.message }
                busy = false
            }
        }
        savedLocality?.let { Text(it, color = Jim.T2, fontSize = 11.sp) }

        Text(L10n.t("hld.plan", vm.language), color = Jim.T2, fontSize = 12.sp,
            fontWeight = FontWeight.Bold)
        current?.let { m ->
            Text("${m.title} \u00b7 $${m.priceUsd.toInt()}", color = Jim.Txt,
                fontSize = 12.sp, fontWeight = FontWeight.Bold)
            Text(m.means, color = Jim.T3, fontSize = 10.sp)
            val readers = m.whoCanRead.joinToString(", ")
            Text(L10n.t("hld.plan.canread", vm.language).replace("{list}", readers),
                color = Jim.T2, fontSize = 11.sp)
        }
        planRows.forEach { p ->
            SmallAction("${p.title} \u00b7 $${p.priceUsd}",
                enabled = !busy && current?.plan != p.plan) {
                busy = true; error = null
                vm.call({ ApiClient.subscribe(vm.uid!!, vm.token!!, p.plan) }) { r ->
                    r.onSuccess { current = it }.onFailure { error = it.message }
                    busy = false
                }
            }
        }
        SmallAction(L10n.t("hld.plan.cancel", vm.language), enabled = !busy) {
            busy = true; error = null
            vm.call({ ApiClient.cancelMembership(vm.uid!!, vm.token!!) }) { r ->
                r.onSuccess { current = it }.onFailure { error = it.message }
                busy = false
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
    }
}


/** Budgets: this much per month for this category. Financial stress is one
 *  of the eight conditions the Guardian takes on, and a budget is how it
 *  learns the shape of yours. */
@Composable
private fun BudgetPanel(vm: GuardianViewModel) {
    var rows by remember { mutableStateOf<List<BudgetRowK>>(emptyList()) }
    var category by remember { mutableStateOf("") }
    var limit by remember { mutableIntStateOf(100) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    fun reload() {
        vm.call({ ApiClient.budgets(vm.uid!!, vm.token!!) }) { r ->
            rows = r.getOrDefault(emptyList())
        }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(L10n.t("aim.budget", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        if (rows.isEmpty()) {
            Text(L10n.t("aim.budget.none", vm.language), color = Jim.T3, fontSize = 11.sp)
        }
        rows.forEach { row ->
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(row.category, color = Jim.Txt, fontSize = 12.sp,
                    fontWeight = FontWeight.Bold)
                Text(" " + L10n.t("aim.budget.line", vm.language)
                    .replace("{spent}", "$" + row.spent.toInt().toString())
                    .replace("{limit}", "$" + row.monthlyLimit.toInt().toString())
                    .replace("{standing}", row.standing),
                    color = Jim.T2, fontSize = 11.sp, modifier = Modifier.weight(1f))
                SmallAction(L10n.t("aim.budget.remove", vm.language), enabled = !busy) {
                    busy = true
                    vm.call({ ApiClient.clearBudget(vm.uid!!, vm.token!!,
                        row.category) }) { busy = false; reload() }
                }
            }
        }
        labeledField(L10n.t("aim.budget", vm.language), category,
            L10n.t("aim.budget.cat.ph", vm.language)) { category = it }
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp),
            verticalAlignment = Alignment.CenterVertically) {
            listOf(50, 100, 200, 400).forEach { amount ->
                FilterChip(selected = limit == amount, onClick = { limit = amount },
                    label = { Text("$$amount", fontSize = 11.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = Jim.BrandA,
                        selectedLabelColor = Color.White, labelColor = Jim.T2))
            }
        }
        BrandButton(L10n.t("aim.budget.set", vm.language),
            enabled = !busy && category.isNotBlank(), busy = busy) {
            busy = true; error = null
            vm.call({ ApiClient.setBudget(vm.uid!!, vm.token!!, category.trim(),
                limit.toDouble()) }) { r ->
                r.onFailure { error = it.message }
                busy = false; category = ""; reload()
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
    }
}


/** The sticker and the relay: beacons a stranger can scan to reach help on
 *  your behalf, and the relay that escalates people, not sirens. */
@Composable
private fun BeaconsPanel(vm: GuardianViewModel) {
    val context = LocalContext.current
    var rows by remember { mutableStateOf<List<BeaconRowK>>(emptyList()) }
    var label by remember { mutableStateOf("") }
    var placement by remember { mutableStateOf("") }
    var card by remember { mutableStateOf<BeaconCardK?>(null) }
    var alarm by remember { mutableStateOf<BeaconAlarmK?>(null) }
    var channel by remember { mutableStateOf<RelayChannelK?>(null) }
    var roster by remember { mutableStateOf<RelayRosterK?>(null) }
    var rota by remember { mutableStateOf<RelayRotaK?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    fun reload() {
        vm.call({ ApiClient.beacons(vm.uid!!, vm.token!!) }) { r ->
            rows = r.getOrDefault(emptyList())
        }
    }
    LaunchedEffect(Unit) {
        reload()
        runCatching { ApiClient.relayChannel() }.onSuccess { channel = it }
        runCatching { ApiClient.relayRoster() }.onSuccess { roster = it }
        runCatching { ApiClient.relayRota() }.onSuccess { rota = it }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(L10n.t("sfy.beacons", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("sfy.beacons.pitch", vm.language), color = Jim.T2, fontSize = 11.sp)
        rows.forEach { row ->
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(row.label, color = Jim.Txt, fontSize = 12.sp,
                    fontWeight = FontWeight.Bold)
                Text(" " + L10n.t("sfy.beacons.scans", vm.language)
                    .replace("{n}", row.scans.toString()),
                    color = Jim.T2, fontSize = 11.sp, modifier = Modifier.weight(1f))
                if (!row.active) {
                    Text(L10n.t("sfy.beacons.retired", vm.language),
                        color = Jim.T3, fontSize = 10.sp)
                }
                SmallAction(L10n.t("att.open", vm.language), enabled = !busy) {
                    busy = true; error = null
                    vm.call({ ApiClient.scannedBeaconPage(row.id) }) { r ->
                        r.onSuccess { page ->
                            // Fetched to prove the door is live; a stranger
                            // reads it in a browser, so hand it to one.
                            context.startActivity(Intent(Intent.ACTION_VIEW,
                                Uri.parse(page.url)))
                        }.onFailure { error = it.message }
                        busy = false
                    }
                }
                SmallAction(L10n.t("rch.acc.beacon", vm.language), enabled = !busy) {
                    busy = true
                    vm.call({ ApiClient.beaconCard(row.id) }) { r ->
                        r.onSuccess { card = it }.onFailure { error = it.message }
                        busy = false
                    }
                }
                SmallAction(L10n.t("aim.budget.remove", vm.language),
                    enabled = !busy && row.active) {
                    busy = true
                    vm.call({ ApiClient.retireBeacon(row.id, vm.token!!) }) {
                        busy = false; reload()
                    }
                }
            }
        }
        card?.let { c ->
            Text(c.firstName, color = Jim.Txt, fontSize = 12.sp,
                fontWeight = FontWeight.Bold)
            Text(c.note, color = Jim.T2, fontSize = 11.sp)
            Text(c.badge, color = Jim.T3, fontSize = 10.sp)
            SmallAction(L10n.t("att.alarm.raise", vm.language), enabled = !busy) {
                busy = true
                vm.call({ ApiClient.raiseBeaconAlarm(c.beacon) }) { r ->
                    r.onSuccess { alarm = it }.onFailure { error = it.message }
                    busy = false
                }
            }
        }
        alarm?.let { Text("${it.badge} ${it.note}", color = Jim.Amber, fontSize = 11.sp) }
        labeledField(L10n.t("sfy.beacons", vm.language), label,
            L10n.t("sfy.beacons.label.ph", vm.language)) { label = it }
        labeledField(L10n.t("sfy.beacons", vm.language), placement,
            L10n.t("sfy.beacons.where.ph", vm.language)) { placement = it }
        BrandButton(L10n.t("sfy.beacons.place", vm.language),
            enabled = !busy && label.isNotBlank(), busy = busy) {
            busy = true; error = null
            vm.call({ ApiClient.placeBeacon(vm.uid!!, vm.token!!, label.trim(),
                placement) }) { r ->
                r.onFailure { error = it.message }
                busy = false; label = ""; placement = ""; reload()
            }
        }

        Text(L10n.t("att.relay", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        channel?.let { c ->
            Text(L10n.t("att.relay.channel", vm.language) + ": " + c.envelope,
                color = Jim.T2, fontSize = 11.sp)
            Text(c.note, color = Jim.T3, fontSize = 10.sp)
        }
        roster?.let { r ->
            val names = r.roster.joinToString(", ")
            Text(L10n.t("att.relay.roster", vm.language)
                .replace("{list}", names).replace("{c}", r.ceiling),
                color = Jim.T2, fontSize = 11.sp)
            Text(r.note, color = Jim.T3, fontSize = 10.sp)
        }
        rota?.let { r ->
            val onNow = r.onNow.joinToString(", ")
            Text("$onNow \u00b7 ${r.timezone}",
                color = if (r.anybodyOnShift) Jim.Green else Jim.T3, fontSize = 11.sp)
            Text(r.note, color = Jim.T3, fontSize = 10.sp)
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
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
        // The Guardian showing you around, and the pane it lives in.
        GuidePanel(vm)
        DockPanel(vm)
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
        Text(L10n.t("mon.sub", vm.language), color = Jim.T2, fontSize = 13.sp)
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
                    GuidanceExtras(it, vm.language)
                }
            }
        }

        // ---- [0039]: did that help? ----
        open.firstOrNull()?.let { f ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(f.question, color = Jim.Txt, fontSize = 16.sp,
                    fontWeight = FontWeight.Bold)
                Text(L10n.t("fu.about", vm.language).replace("{c}", f.condition),
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

        // Your normal, and where its edges sit.
        BandsPanel(vm)
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
        Text(L10n.t("ci.pitch", vm.language), color = Jim.T2, fontSize = 13.sp)
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            ratingRow(L10n.t("ci.mood", vm.language), mood) { mood = it }
            ratingRow(L10n.t("ci.energy", vm.language), energy) { energy = it }
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(L10n.t("ci.note", vm.language), color = Jim.Txt, fontSize = 14.sp)
                OutlinedTextField(value = note, onValueChange = { note = it },
                    placeholder = { Text(L10n.t("ci.note.ph", vm.language), color = Jim.T3) },
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
                Text(L10n.t("ci.guidance", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(g.content, color = Jim.Txt, fontSize = 14.sp)
                GuidanceExtras(g, vm.language)
            }
        }
        // The wellness protocols sit with the pulse they steady.
        WellnessPanel(vm)
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

    // The offline coach's store and JIM's syllabus for it (jim/pipeline.py).
    var knows by remember { mutableStateOf<CoachStore?>(null) }
    var syllabus by remember { mutableStateOf<CoachCurriculum?>(null) }
    var studied by remember { mutableStateOf<String?>(null) }
    var studying by remember { mutableStateOf(false) }
    var reloads by remember { mutableStateOf(0) }
    LaunchedEffect(reloads) {
        val uid = vm.uid ?: return@LaunchedEffect
        val token = vm.token ?: return@LaunchedEffect
        knows = runCatching { ApiClient.coachStore(uid, token) }.getOrNull()
        syllabus = runCatching { ApiClient.coachCurriculum(uid, token) }.getOrNull()
    }

    screenScroll {
        Text(L10n.t("coach.title", vm.language), color = Jim.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("coach.pitch", vm.language),
            color = Jim.T2, fontSize = 13.sp)
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            areaChips(vm, area) { area = it }
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
                Text(L10n.t("tab.coach", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(g.content, color = Jim.Txt, fontSize = 14.sp)
                GuidanceExtras(g, vm.language)

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
        knows?.let { k ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("cch.knows", vm.language), color = Jim.Txt,
                    fontSize = 16.sp, fontWeight = FontWeight.Bold)
                val counts = "${k.pack} · +${k.excursions.size} · +${k.deposits.size}"
                Text(counts, color = Jim.T2, fontSize = 12.sp)
                val s = syllabus
                if (s != null && s.suggested.isNotEmpty()) {
                    Text(L10n.t("cch.study.head", vm.language), color = Jim.Txt,
                        fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    s.suggested.forEach { sug ->
                        Text(sug.topic, color = Jim.Txt, fontSize = 13.sp)
                        Text(sug.why, color = Jim.T2, fontSize = 11.sp)
                        TextButton(enabled = !studying, onClick = {
                            studying = true
                            vm.call({ ApiClient.coachStudy(
                                vm.uid!!, vm.token!!, sug.topic, sug.area) }) {
                                studying = false
                                studied = it.getOrNull()?.studied
                                reloads += 1
                            }
                        }) { Text(L10n.t("cch.study.go", vm.language),
                                  color = Jim.BrandA, fontSize = 12.sp) }
                    }
                }
                studied?.let {
                    val done = L10n.t("cch.study.done", vm.language)
                    Text("✓ $it — $done", color = Jim.T2, fontSize = 11.sp)
                }
            }
        }
        // The Guardian's bearing: tone, what it was told, whether its
        // answers landed, and what it made of that.
        BearingPanel(vm)
    }
}

@Composable
private fun areaChips(vm: GuardianViewModel, selected: String,
                      onPick: (String) -> Unit) {
    Text(L10n.t("coach.area", vm.language), color = Jim.T2, fontSize = 12.sp)
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
            3 -> { MoneyPanel(vm); BudgetPanel(vm) }
            // The dose board is a schedule the body keeps.
            4 -> { SchedulePanel(vm); MedsPanel(vm) }
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
    var drill by remember { mutableStateOf<Triple<String, String, String>?>(null) }
    var drillAnswer by remember { mutableStateOf("") }
    var drillLine by remember { mutableStateOf<String?>(null) }
    var drillLog by remember { mutableStateOf<List<String>>(emptyList()) }
    fun reload() {
        vm.call({ ApiClient.goals(vm.uid!!, vm.token!!) }) { r -> goals = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.drills(vm.uid!!, vm.token!!) }) { r -> drillLog = r.getOrDefault(emptyList()) }
    }
    LaunchedEffect(Unit) { reload() }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(L10n.t("goal.new", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            areaChips(vm, area) { area = it }
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
                if ((g.status ?: "active") == "active") {
                    SmallAction(L10n.t("aim.goals.done", vm.language), enabled = !busy) {
                        busy = true
                        vm.call({ ApiClient.updateGoal(vm.uid!!, vm.token!!,
                            g.id, 1.0, "completed") }) { busy = false; reload() }
                    }
                }
            }
        }
        // Interview drills: deal, answer, and the reading names who made
        // it — the coach, or the probe checklist standing in honestly.
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("drl.title", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            BrandButton(L10n.t("drl.deal", vm.language), enabled = !busy) {
                drillLine = null
                vm.call({ ApiClient.startDrill(vm.uid!!, vm.token!!) }) { r ->
                    drill = r.getOrNull()
                }
            }
            drill?.let { d ->
                Text(d.second, color = Jim.Txt, fontSize = 13.sp)
                Text(d.third, color = Jim.T3, fontSize = 11.sp)
                labeledField(L10n.t("drl.title", vm.language), drillAnswer,
                    L10n.t("drl.answer.ph", vm.language)) { drillAnswer = it }
                BrandButton(L10n.t("drl.read", vm.language),
                    enabled = drillAnswer.isNotBlank()) {
                    vm.call({ ApiClient.answerDrill(vm.uid!!, d.first,
                        drillAnswer, vm.token!!) }) { r ->
                        drillLine = r.getOrNull()?.ifEmpty { d.third }
                        drill = null; drillAnswer = ""
                    }
                }
            }
            drillLine?.let { Text(it, color = Jim.T2, fontSize = 12.sp) }
            drillLog.take(3).forEach { Text(it, color = Jim.T3, fontSize = 11.sp) }
        }
        ActivityPanel(vm)
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
            Text(L10n.t("habit.new", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
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
                    Text(L10n.t("habit.streak", vm.language)
                        .replace("{n}", "${h.streak ?: 0}"),
                        color = Jim.Amber, fontSize = 12.sp)
                }
                TextButton(onClick = {
                    vm.call({ ApiClient.logHabit(vm.uid!!, vm.token!!, h.id) }) { reload() }
                }) { Text(L10n.t("habit.log", vm.language), color = Jim.BrandA, fontSize = 13.sp, fontWeight = FontWeight.Bold) }
            }
        }
    }
}

@Composable
private fun JournalPanel(vm: GuardianViewModel) {
    var entries by remember { mutableStateOf<List<JournalItem>>(emptyList()) }
    var text by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var meals by remember { mutableStateOf<List<String>>(emptyList()) }
    var mealNote by remember { mutableStateOf("") }
    var letters by remember { mutableStateOf<List<Pair<String, String>>>(emptyList()) }
    fun reload() {
        vm.call({ ApiClient.journal(vm.uid!!, vm.token!!) }) { r -> entries = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.meals(vm.uid!!, vm.token!!) }) { r -> meals = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.letters(vm.uid!!, vm.token!!) }) { r -> letters = r.getOrDefault(emptyList()) }
    }
    LaunchedEffect(Unit) { reload() }

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(L10n.t("jrn.new", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            labeledField(L10n.t("jrn.entry", vm.language), text, L10n.t("jrn.entry.ph", vm.language)) { text = it }
            BrandButton(L10n.t("jrn.save", vm.language), enabled = text.isNotBlank(), busy = busy) {
                busy = true
                vm.call({ ApiClient.addJournal(vm.uid!!, vm.token!!, text) }) {
                    text = ""; busy = false; reload()
                }
            }
        }
        // Meals: the note is the log; a photo, when the app attaches one,
        // is a sealed receipt. No pretended vision.
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("mea.title", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            labeledField(L10n.t("mea.title", vm.language), mealNote, L10n.t("mea.ph", vm.language)) { mealNote = it }
            BrandButton(L10n.t("mea.log", vm.language), enabled = mealNote.isNotBlank()) {
                vm.call({ ApiClient.logMeal(vm.uid!!, mealNote, vm.token!!) }) {
                    mealNote = ""; reload()
                }
            }
            meals.forEach { Text(it, color = Jim.T2, fontSize = 12.sp) }
        }
        // The weekly letter: composed only from what was logged.
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("let.title", vm.language), color = Jim.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            BrandButton(L10n.t("let.write", vm.language)) {
                vm.call({ ApiClient.writeLetter(vm.uid!!, vm.token!!) }) { reload() }
            }
            letters.forEach { (week, body) ->
                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(week, color = Jim.T3, fontSize = 11.sp)
                    Text(body, color = Jim.T2, fontSize = 12.sp)
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
    var statementText by remember { mutableStateOf("") }
    var statements by remember { mutableStateOf<List<String>>(emptyList()) }
    var links by remember { mutableStateOf<List<Triple<String, String, String>>>(emptyList()) }
    var linkInstitution by remember { mutableStateOf("") }

    fun reload() {
        vm.call({ ApiClient.moneyOverview(vm.uid!!, vm.token!!) }) { r -> view = r.getOrNull() }
        vm.call({ ApiClient.moneyStatements(vm.uid!!, vm.token!!) }) { r -> statements = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.moneyLinks(vm.uid!!, vm.token!!) }) { r -> links = r.getOrDefault(emptyList()) }
    }
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

        // The statement is the reading: pasted here, sealed in the vault,
        // summed locally; a closing balance walks the observe path.
        v.accounts.firstOrNull()?.let { first ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(labels["statements"] ?: "", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                labeledField(labels["statements"] ?: "", statementText,
                    labels["drop_statement"] ?: "") { statementText = it }
                BrandButton(labels["drop_statement"] ?: "",
                            enabled = statementText.isNotBlank(), busy = busy) {
                    act {
                        val b64 = android.util.Base64.encodeToString(
                            statementText.toByteArray(), android.util.Base64.NO_WRAP)
                        ApiClient.moneyDropStatement(vm.uid!!, vm.token!!, first.id, b64)
                        statementText = ""
                    }
                }
                statements.forEach { Text(it, color = Jim.T2, fontSize = 11.sp) }
            }
        }

        // A bank link is a written consent; its status never claims data.
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(labels["links"] ?: "", color = Jim.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            labeledField(labels["institution"] ?: "", linkInstitution,
                labels["aggregator"] ?: "") { linkInstitution = it }
            BrandButton(labels["link_bank"] ?: "",
                        enabled = linkInstitution.isNotBlank(), busy = busy) {
                act {
                    ApiClient.moneyLinkBank(vm.uid!!, vm.token!!,
                        linkInstitution, "plaid")
                    linkInstitution = ""
                }
            }
            links.forEach { (id, name, status) ->
                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(name + " \u00b7 " + status, color = Jim.T2, fontSize = 11.sp)
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        SmallAction(labels["sync"] ?: "", enabled = !busy) {
                            act { ApiClient.moneySyncBank(vm.uid!!, vm.token!!, id) }
                        }
                        SmallAction(labels["revoke_link"] ?: "", enabled = !busy) {
                            act { ApiClient.moneyRevokeLink(vm.uid!!, vm.token!!, id) }
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
                    }, enabled = question.isNotBlank()) { Text(L10n.t("fu.ask", vm.language)) }
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
            0 -> { AlarmsPanel(vm); BeaconsPanel(vm) }
            1 -> SOSPanel(vm)
            // The vigil is the crash watch's chronic sibling: one fires on
            // a bad reading, the other on no readings at all.
            2 -> { CrashWatchPanel(vm); VigilPanel(vm) }
            3 -> MedicalPanel(vm)
            4 -> PolicyPanel(vm)
            5 -> RobotsPanel(vm)
            else -> { CustodyPanel(vm); VeilPanel(vm) }
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
                Text(L10n.t("sos.coord", vm.language), color = Jim.Txt, fontSize = 16.sp,
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
                Text(L10n.t("sos.severity", vm.language), color = Jim.Txt, fontSize = 16.sp,
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
private fun GuidanceExtras(g: Guidance, lang: String) {
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
                Text(L10n.t("gd.sealed", lang), color = Jim.Green,
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
                Text(L10n.t("gd.pace", lang).replace("{rate}", "${pace.perMinute}")
                    .replace("{ratio}", pace.ratio),
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
            Text(L10n.t("gd.derived", lang), color = Jim.Txt, fontSize = 12.sp,
                fontWeight = FontWeight.Bold)
            p.evidence.forEach { e ->
                Text("${e.publisher} — ${e.title}", color = Jim.Txt, fontSize = 11.sp)
                e.supports?.let {
                    Text(L10n.t("gd.supports", lang).replace("{s}", it), color = Jim.T2, fontSize = 10.sp)
                }
                Text(e.url, color = Jim.BrandA, fontSize = 10.sp)
            }
            Text(L10n.t("gd.provenance", lang).replace("{method}", p.method)
                    .replace("{model}", p.generatedBy),
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
        Text(L10n.t("cst.sealedchats", vm.language) + " " +
             "encrypted, attributed, and hash-chained. This is your copy of " +
             "the proof.", color = Jim.T2, fontSize = 12.sp)
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
        list?.let { c ->
            Text(L10n.t(if (c.chainIntact == true) "cust.chain.ok"
                        else "cust.chain.unknown", vm.language),
                color = if (c.chainIntact == true) Jim.Green else Jim.Amber,
                fontSize = 12.sp, fontWeight = FontWeight.Bold)
            if (c.records.isEmpty())
                Text(L10n.t("cst.sealednone", vm.language) + " " +
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
                        Text(L10n.t("cst.origin", vm.language).replace("{x}", p.origin), color = Jim.Txt, fontSize = 11.sp)
                        p.cipher?.let {
                            Text(L10n.t("cst.seal", vm.language).replace("{x}", it), color = Jim.T2, fontSize = 10.sp)
                        }
                        Text(L10n.t("cust.events", vm.language).replace("{n}", "${p.auditCount}"), color = Jim.T2,
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
                SmallAction(L10n.t("rch.body.unbind", vm.language)) {
                    vm.call({ ApiClient.unbindRobot(vm.uid!!, vm.token!!,
                        rob.id) }) { reload() }
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
        // The specialists who stand behind the household's conditions, and
        // everything handed to them.
        SpecialistsPanel(vm)
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
            0 -> { SourcesPanel(vm); MicPanel(vm); VoiceSettingsPanel(vm); TalkPanel(vm); MailSettingsPanel(vm); WatchPanel(vm); DevicesPanel(vm); SittingPanel(vm) }
            1 -> SocialPanel(vm)
            2 -> AppsPanel(vm)
            3 -> {
                CommunityPanel(vm)
                ExcursionsPanel(vm)
            }
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
                    val h = c.handle
                    if (h != null && h.isNotEmpty()) {
                        smallAction(L10n.t("jcon.scrape", vm.language)) {
                            vm.call({ ApiClient.socialScrape(c.id, vm.token!!) }) { r ->
                                r.onSuccess {
                                    status = L10n.t("jcon.scraped.one", vm.language)
                                        .replace("{platform}", pretty(c.platform))
                                }
                                    .onFailure { error = it.message }
                            }
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
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    smallAction(L10n.t("rch.acc.beacon", vm.language)) {
                        vm.call({ ApiClient.socialBeacon(c.id, vm.token!!) }) { r ->
                            r.onSuccess { status = it }
                                .onFailure { error = it.message }
                        }
                    }
                    smallAction(L10n.t("rch.acc.disconnect", vm.language)) {
                        vm.call({ ApiClient.disconnectSocial(c.id, vm.token!!) }) {
                            reload()
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

/** The excursion and the window: study a topic without carrying PHI out,
 *  the community doors this account opened, and QRME's public feed through
 *  the tandem. Console doors (Reach, Feed); this is the phone's. */
@Composable
private fun ExcursionsPanel(vm: GuardianViewModel) {
    val context = LocalContext.current
    var rows by remember { mutableStateOf<List<ExcursionRowK>>(emptyList()) }
    var topic by remember { mutableStateOf("") }
    var question by remember { mutableStateOf("") }
    var entry by remember { mutableStateOf<ExcursionRowK?>(null) }
    var learned by remember { mutableStateOf<ExcursionLearnedK?>(null) }
    var visits by remember { mutableStateOf<List<CommunityVisitRowK>>(emptyList()) }
    var feed by remember { mutableStateOf<CommunityFeedViewK?>(null) }
    var feedRefused by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        val uid = vm.uid ?: return
        val token = vm.token ?: return
        vm.call({ ApiClient.excursions(uid, token) }) { r ->
            r.fold({ rows = it }, { error = it.message })
        }
        vm.call({ ApiClient.communityVisits(uid, token) }) { r ->
            r.fold({ visits = it }, { error = it.message })
        }
        vm.call({ ApiClient.communityFeed(uid, token) }) { r ->
            r.fold({ feed = it }, { feedRefused = it.message })
        }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("rch.ask", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("rch.ask", vm.language), topic,
            L10n.t("rch.ask.topic.ph", vm.language)) { topic = it }
        labeledField(L10n.t("rch.ask", vm.language), question,
            L10n.t("rch.ask.q.ph", vm.language)) { question = it }
        BrandButton(L10n.t("rch.ask.go", vm.language),
            enabled = topic.isNotBlank() && question.isNotBlank()) {
            val uid = vm.uid ?: return@BrandButton
            val token = vm.token ?: return@BrandButton
            vm.call({ ApiClient.startExcursion(uid, token, topic.trim(),
                question.trim()) }) { r ->
                r.fold({ topic = ""; question = ""; reload() },
                    { error = it.message })
            }
        }
        rows.forEach { row ->
            Row(Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Column(Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(row.topic, color = Jim.Txt, fontSize = 13.sp)
                    // Redactions, colored by whether the question left this
                    // host — amber left, green stayed. `rch.ask.price` below
                    // says what the two mean.
                    Text("${row.redactions}",
                        color = if (row.leftHost) Jim.Amber else Jim.Green,
                        fontSize = 11.sp)
                }
                SmallAction(L10n.t("rch.ask.read", vm.language)) {
                    val token = vm.token ?: return@SmallAction
                    vm.call({ ApiClient.excursionEntry(row.id, token) }) { r ->
                        r.fold({ entry = it }, { error = it.message })
                    }
                }
                SmallAction(L10n.t("rch.ask.keep", vm.language),
                    enabled = !row.learned) {
                    val token = vm.token ?: return@SmallAction
                    vm.call({ ApiClient.learnExcursion(row.id, token) }) { r ->
                        r.fold({ learned = it; reload() }, { error = it.message })
                    }
                }
            }
        }
        entry?.let {
            Text(it.findings ?: "", color = Jim.T2, fontSize = 12.sp)
        }
        learned?.note?.let { Text(it, color = Jim.Green, fontSize = 12.sp) }
        Text(L10n.t("rch.ask.price", vm.language), color = Jim.T3, fontSize = 11.sp)
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(L10n.t("rch.wrist.visits", vm.language)
            .replace("{n}", "${visits.size}"), color = Jim.T2, fontSize = 12.sp)
        visits.take(5).forEach { visit ->
            Text("${visit.roomId} \u00b7 ${visit.at}", color = Jim.T3,
                fontSize = 11.sp)
        }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(L10n.t("feed.title", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        feedRefused?.let { Text(it, color = Jim.T3, fontSize = 12.sp) }
        feed?.let { f ->
            Text(f.note, color = Jim.T2, fontSize = 12.sp)
            Text(L10n.t("feed.cannotpost", vm.language), color = Jim.T3,
                fontSize = 11.sp)
            if (f.items.isEmpty()) {
                Text(L10n.t("feed.empty", vm.language), color = Jim.T3,
                    fontSize = 12.sp)
            }
            f.items.take(6).forEach { item ->
                // An elvis inside the interpolation reads to the English
                // counter as a truncated literal; named vals keep it clean.
                val name = item.title ?: item.topic ?: ""
                val kind = item.kind ?: ""
                Text("$name \u00b7 $kind", color = Jim.T2, fontSize = 12.sp)
            }
            f.openInQrme?.let { url ->
                SmallAction(L10n.t("feed.openinqrme", vm.language)) {
                    context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
                }
            }
        }
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

// ---- the health core: the cabinet, the vigil, and the baseline bands ----
// Console doors since 0.9.0 / 0.8.0 / 0.6.0; these are the phone's.

@Composable
private fun MedsPanel(vm: GuardianViewModel) {
    var board by remember { mutableStateOf<MedsBoard?>(null) }
    var adherence by remember { mutableStateOf<List<AdherenceRow>>(emptyList()) }
    var showAdherence by remember { mutableStateOf(false) }
    var showAdd by remember { mutableStateOf(false) }
    var name by remember { mutableStateOf("") }
    var dose by remember { mutableStateOf("") }
    var purpose by remember { mutableStateOf("") }
    var times by remember { mutableStateOf("") }
    var asNeeded by remember { mutableStateOf(false) }
    var ceiling by remember { mutableStateOf("") }
    var critical by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.medsBoard(vm.uid!!, vm.token!!) }) { r ->
            board = r.getOrNull()
        }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.med.title", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        val b = board
        if (b != null) {
            if (b.missedCritical.isNotEmpty())
                Text(L10n.t("ns.med.missed", vm.language).replace("{list}",
                        b.missedCritical.joinToString(", ") {
                            "${it.name} (${it.slot})" }),
                    color = Jim.Amber, fontSize = 11.sp)
            Text(L10n.t("ns.med.today", vm.language), color = Jim.T2,
                fontSize = 12.sp, fontWeight = FontWeight.Bold)
            if (b.medications.isEmpty())
                Text(L10n.t("ns.med.none", vm.language), color = Jim.T3,
                    fontSize = 11.sp)
            b.medications.forEach { med ->
                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("${med.name} · ${med.dose}", color = Jim.Txt,
                            fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        SmallAction(L10n.t("ns.med.stop", vm.language)) {
                            vm.call({ ApiClient.stopMed(vm.uid!!, vm.token!!,
                                med.id) }) { reload() }
                        }
                    }
                    med.purpose?.let {
                        Text(it, color = Jim.T2, fontSize = 11.sp)
                    }
                    // The console's "worth a check-in" checkbox, as a chip.
                    FilterChip(selected = med.critical,
                        onClick = {
                            vm.call({ ApiClient.setMedCritical(vm.uid!!,
                                vm.token!!, med.id, !med.critical) }) {
                                reload()
                            }
                        },
                        label = { Text(L10n.t("ns.med.critical", vm.language),
                            fontSize = 10.sp) })
                    if (med.kind == "as_needed") {
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text(L10n.t("ns.med.asneeded.line", vm.language)
                                    .replace("{n}", (med.takenToday ?: 0).toString())
                                    .replace("{max}", med.maxPerDay?.let {
                                        L10n.t("ns.med.asneeded.max", vm.language)
                                            .replace("{max}", it.toString())
                                    } ?: ""),
                                color = Jim.T2, fontSize = 11.sp)
                            SmallAction(L10n.t("ns.med.tookone", vm.language)) {
                                vm.call({ ApiClient.logDose(vm.uid!!, vm.token!!,
                                    med.id, "taken", null) }) { r ->
                                    error = r.exceptionOrNull()?.message
                                    r.getOrNull()?.let { board = it }
                                }
                            }
                        }
                    } else med.slots?.forEach { slot ->
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("${slot.slot} · ${slot.status}",
                                color = if (slot.status == "missed") Jim.Amber
                                        else Jim.T2,
                                fontSize = 11.sp)
                            if (slot.status == "due" || slot.status == "missed") {
                                SmallAction(L10n.t("ns.med.take", vm.language)) {
                                    vm.call({ ApiClient.logDose(vm.uid!!,
                                        vm.token!!, med.id, "taken",
                                        slot.slot) }) { r ->
                                        error = r.exceptionOrNull()?.message
                                        r.getOrNull()?.let { board = it }
                                    }
                                }
                                SmallAction(L10n.t("ns.med.skip", vm.language)) {
                                    vm.call({ ApiClient.logDose(vm.uid!!,
                                        vm.token!!, med.id, "skipped",
                                        slot.slot) }) { r ->
                                        error = r.exceptionOrNull()?.message
                                        r.getOrNull()?.let { board = it }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            // The board's own honesty line, verbatim from the wire.
            Text(b.disclaimer, color = Jim.T3, fontSize = 10.sp)
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            SmallAction(L10n.t("ns.med.last", vm.language)
                    .replace("{n}", "7")) {
                showAdherence = !showAdherence
                if (showAdherence)
                    vm.call({ ApiClient.medAdherence(vm.uid!!, vm.token!!) }) { r ->
                        adherence = r.getOrDefault(emptyList())
                    }
            }
            SmallAction(L10n.t("ns.med.add", vm.language)) {
                showAdd = !showAdd
            }
        }
        if (showAdherence) adherence.forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(row.name, color = Jim.Txt, fontSize = 11.sp)
                Text(L10n.t("ns.med.of", vm.language)
                        .replace("{taken}", row.taken.toString())
                        .replace("{expected}", row.expected.toString()),
                    color = Jim.T2, fontSize = 11.sp)
            }
        }
        if (showAdd) {
            Text(L10n.t("ns.med.add.pitch", vm.language), color = Jim.T2,
                fontSize = 11.sp)
            labeledField(L10n.t("ns.med.name", vm.language), name,
                L10n.t("ns.med.name.ph", vm.language)) { name = it }
            labeledField(L10n.t("ns.med.dose", vm.language), dose,
                L10n.t("ns.med.dose.ph", vm.language)) { dose = it }
            labeledField(L10n.t("ns.med.purpose", vm.language), purpose,
                L10n.t("ns.med.purpose.ph", vm.language)) { purpose = it }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Switch(checked = asNeeded,
                    onCheckedChange = { asNeeded = it })
                Text(L10n.t("ns.med.asneeded", vm.language), color = Jim.T2,
                    fontSize = 11.sp)
            }
            if (asNeeded)
                labeledField(L10n.t("ns.med.ceiling", vm.language) + " "
                        + L10n.t("ns.med.ceiling.note", vm.language),
                    ceiling, "3") { ceiling = it }
            else
                labeledField(L10n.t("ns.med.times", vm.language)
                        + L10n.t("ns.med.times.note", vm.language),
                    times, "08:00, 20:00") { times = it }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Switch(checked = critical,
                    onCheckedChange = { critical = it })
                Text(L10n.t("ns.med.critical", vm.language), color = Jim.T2,
                    fontSize = 11.sp)
            }
            BrandButton(L10n.t("ns.med.add", vm.language),
                enabled = name.isNotBlank() && dose.isNotBlank()
                        && (asNeeded || times.isNotBlank())) {
                val schedule = org.json.JSONObject()
                if (asNeeded) {
                    schedule.put("as_needed", true)
                    ceiling.trim().toIntOrNull()?.let {
                        if (it > 0) schedule.put("max_per_day", it)
                    }
                } else {
                    val arr = org.json.JSONArray()
                    times.split(",").map { it.trim() }
                        .filter { it.isNotEmpty() }.forEach { arr.put(it) }
                    schedule.put("times", arr)
                }
                vm.call({ ApiClient.addMed(vm.uid!!, vm.token!!, name.trim(),
                    dose.trim(), schedule, purpose.trim(), critical) }) { r ->
                    error = r.exceptionOrNull()?.message
                    if (r.isSuccess) {
                        name = ""; dose = ""; purpose = ""; times = ""
                        ceiling = ""; asNeeded = false; critical = false
                        showAdd = false
                    }
                    reload()
                }
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}

@Composable
private fun VigilPanel(vm: GuardianViewModel) {
    var status by remember { mutableStateOf<VigilState?>(null) }
    var stewardName by remember { mutableStateOf("") }
    var stewardChannel by remember { mutableStateOf("") }
    var quietDays by remember { mutableStateOf("3") }
    var note by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }

    fun took(r: Result<VigilState>) {
        error = r.exceptionOrNull()?.message
        r.getOrNull()?.let { st ->
            status = st
            if (st.armed) {
                if (stewardName.isBlank()) stewardName = st.stewardName ?: ""
                if (stewardChannel.isBlank())
                    stewardChannel = st.stewardChannel ?: ""
                st.quietDays?.let { quietDays = it.toString() }
                if (note.isBlank()) note = st.note ?: ""
            }
        }
    }
    // Opening the screen sweeps — idempotent, trips at most once, and
    // opening the app is the natural moment to ask whether anybody has
    // gone quiet. Same choice the console made.
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.sweepVigil(vm.uid!!, vm.token!!) }) { took(it) }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.vg.title", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.vg.pitch", vm.language), color = Jim.T2,
            fontSize = 11.sp)
        val st = status
        if (st?.tripped == true) {
            Text(L10n.t("ns.vg.tripped", vm.language)
                    .replace("{name}", st.stewardName ?: "")
                    .replace("{after}", L10n.t("ns.vg.after", vm.language)
                        .replace("{n}", (st.quietDays ?: 0.0).toString())),
                color = Jim.Amber, fontSize = 12.sp,
                fontWeight = FontWeight.Bold)
            BrandButton(L10n.t("ns.vg.okay", vm.language)) {
                vm.call({ ApiClient.resolveVigil(vm.uid!!, vm.token!!) }) {
                    took(it)
                }
            }
        } else if (st?.armed == true) {
            Text(L10n.t("ns.vg.armed", vm.language)
                    .replace("{when}", st.silentHours?.let {
                        "${it.toInt()} h" } ?: "—")
                    .replace("{name}", st.stewardName ?: ""),
                color = Jim.Green, fontSize = 11.sp)
        }
        labeledField(L10n.t("ns.vg.name", vm.language), stewardName,
            L10n.t("ns.vg.name.ph", vm.language)) { stewardName = it }
        labeledField(L10n.t("ns.vg.reach", vm.language), stewardChannel,
            L10n.t("ns.vg.reach.ph", vm.language)) { stewardChannel = it }
        labeledField(L10n.t("ns.vg.days", vm.language), quietDays,
            "3") { quietDays = it }
        labeledField(L10n.t("ns.vg.words", vm.language)
                + L10n.t("ns.vg.words.note", vm.language), note,
            L10n.t("ns.vg.words.ph", vm.language)) { note = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t(if (st?.armed == true) "ns.vg.update"
                               else "ns.vg.arm", vm.language),
                enabled = stewardName.isNotBlank()
                        && stewardChannel.isNotBlank()) {
                vm.call({ ApiClient.armVigil(vm.uid!!, vm.token!!,
                    stewardName.trim(), stewardChannel.trim(),
                    quietDays.trim().toDoubleOrNull() ?: 3.0,
                    note.trim()) }) { took(it) }
            }
            if (st?.armed == true)
                SmallAction(L10n.t("ns.vg.disarm", vm.language)) {
                    vm.call({ ApiClient.disarmVigil(vm.uid!!, vm.token!!) }) {
                        took(it)
                    }
                }
            // A read, not a sweep — the way to look without acting.
            SmallAction(L10n.t("ns.vg.check", vm.language)) {
                vm.call({ ApiClient.vigilStatus(vm.uid!!, vm.token!!) }) {
                    took(it)
                }
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}

@Composable
private fun BandsPanel(vm: GuardianViewModel) {
    var bands by remember { mutableStateOf<List<BandRow>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.bands(vm.uid!!, vm.token!!) }) { r ->
            bands = r.getOrDefault(emptyList())
        }
    }
    fun change(band: BandRow, margin: Double?, high: Boolean?,
               low: Boolean?) {
        vm.call({ ApiClient.setBand(vm.uid!!, vm.token!!, band.metric,
            margin, high, low) }) { r ->
            error = r.exceptionOrNull()?.message
            reload()
        }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.bas.title", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.bas.sub", vm.language), color = Jim.T2,
            fontSize = 11.sp)
        if (bands.isEmpty())
            Text(L10n.t("ns.bas.none", vm.language), color = Jim.T3,
                fontSize = 11.sp)
        bands.forEach { band ->
            val step = if (band.unit == "°C") 0.1 else 0.5
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(band.label, color = Jim.Txt, fontSize = 12.sp,
                        fontWeight = FontWeight.Bold)
                    Text("±${band.margin}${band.unit}", color = Jim.T2,
                        fontSize = 11.sp)
                }
                if (band.provisional)
                    Text(L10n.t("ns.bas.learning", vm.language)
                            .replace("{n}", band.samples.toString()),
                        color = Jim.T3, fontSize = 11.sp)
                else
                    Text(L10n.t("ns.bas.usual", vm.language)
                            .replace("{v}", "${band.baseline}${band.unit}")
                            .replace("{lo}", "${band.lowEdge}${band.unit}")
                            .replace("{hi}", "${band.highEdge}${band.unit}"),
                        color = Jim.T2, fontSize = 11.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    // Narrower is told sooner; wider tolerates a wanderer.
                    SmallAction("−") {
                        if (band.margin - step > 0)
                            change(band, band.margin - step, null, null)
                    }
                    SmallAction("+") {
                        change(band, band.margin + step, null, null)
                    }
                    FilterChip(selected = band.watchLow,
                        onClick = { change(band, null, null, !band.watchLow) },
                        label = { Text(L10n.t("ns.bas.drop", vm.language),
                            fontSize = 10.sp) })
                    FilterChip(selected = band.watchHigh,
                        onClick = { change(band, null, !band.watchHigh, null) },
                        label = { Text(L10n.t("ns.bas.climb", vm.language),
                            fontSize = 10.sp) })
                    if (band.source == "user")
                        SmallAction(L10n.t("ns.bas.reset", vm.language)) {
                            vm.call({ ApiClient.resetBand(vm.uid!!, vm.token!!,
                                band.metric) }) { reload() }
                        }
                }
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}

// ---- deployment settings: the voice and the mail desk ----
// Console doors since 0.6.0 / 0.4.x; these are the phone's. The key and
// the password are write-only: the routes say whether one is set and never
// say it back.

@Composable
private fun VoiceSettingsPanel(vm: GuardianViewModel) {
    var settings by remember { mutableStateOf<VoiceSettingsOut?>(null) }
    var provider by remember { mutableStateOf("") }
    var voiceId by remember { mutableStateOf("") }
    var apiKey by remember { mutableStateOf("") }
    var speakReplies by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }

    fun took(r: Result<VoiceSettingsOut>) {
        error = r.exceptionOrNull()?.message
        r.getOrNull()?.let { s ->
            settings = s
            if (provider.isBlank()) provider = s.provider
            if (voiceId.isBlank()) voiceId = s.voiceId ?: ""
            speakReplies = s.speakReplies
        }
    }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.voiceSettings() }) { took(it) }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.vs.title", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        val s = settings
        if (s != null) {
            if (s.provider == "device")
                Text(L10n.t("ns.vs.pitch", vm.language), color = Jim.T2,
                    fontSize = 11.sp)
            else
                Text(L10n.t("ns.vs.through", vm.language)
                        .replace("{provider}", s.provider)
                        .replace("{env}", if (s.keySource == "environment")
                            " (env)" else ""),
                    color = Jim.Green, fontSize = 11.sp)
        }
        // The provider vocabulary is the backend's PROVIDERS tuple; the
        // describe route answers the current one but does not enumerate.
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            listOf("elevenlabs", "openai", "device").forEach { name ->
                FilterChip(selected = provider == name,
                    onClick = { provider = name },
                    label = { Text(name, fontSize = 10.sp) })
            }
        }
        if (provider != "device") s?.voices?.take(6)?.forEach { voice ->
            FilterChip(selected = voiceId == voice.id,
                onClick = { voiceId = voice.id },
                label = { Text("${voice.name} \u00b7 ${voice.note}",
                    fontSize = 10.sp) })
        }
        if (provider != "device")
            labeledField("", apiKey,
                if (s?.keySet == true) L10n.t("ns.ml.saved", vm.language)
                else "sk-\u2026") { apiKey = it }
        Row(verticalAlignment = Alignment.CenterVertically) {
            Switch(checked = speakReplies,
                onCheckedChange = { speakReplies = it })
            Text(L10n.t("ns.vs.hear", vm.language), color = Jim.T2,
                fontSize = 11.sp)
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("ns.set.save", vm.language),
                enabled = provider.isNotBlank()) {
                vm.call({ ApiClient.saveVoiceSettings(provider,
                    apiKey.trim(), voiceId, speakReplies) }) { r ->
                    took(r)
                    if (r.isSuccess) apiKey = ""
                }
            }
            SmallAction(L10n.t("ns.bas.reset", vm.language)) {
                vm.call({ ApiClient.clearVoiceSettings() }) { r ->
                    took(r)
                    r.getOrNull()?.let { provider = it.provider; voiceId = "" }
                }
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}

@Composable
private fun MailSettingsPanel(vm: GuardianViewModel) {
    var settings by remember { mutableStateOf<MailSettingsOut?>(null) }
    var host by remember { mutableStateOf("") }
    var port by remember { mutableStateOf("587") }
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var sender by remember { mutableStateOf("") }
    var publicUrl by remember { mutableStateOf("") }
    var testTo by remember { mutableStateOf("") }
    var testSentTo by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    fun took(r: Result<MailSettingsOut>) {
        error = r.exceptionOrNull()?.message
        r.getOrNull()?.let { s ->
            settings = s
            if (host.isBlank()) host = s.host ?: ""
            port = s.port.toString()
            if (username.isBlank()) username = s.username ?: ""
            if (sender.isBlank()) sender = s.sender ?: ""
            if (publicUrl.isBlank()) publicUrl = s.publicUrl
        }
    }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.mailSettings() }) { took(it) }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.ml.title", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        val s = settings
        if (s != null) {
            if (s.transport == "smtp")
                Text(L10n.t("ns.ml.smtp", vm.language)
                        .replace("{host}", s.host ?: "")
                        .replace("{env}", if (s.source == "environment")
                            " (env)" else ""),
                    color = Jim.Green, fontSize = 11.sp)
            else
                Text(L10n.t("ns.ml.none", vm.language), color = Jim.T2,
                    fontSize = 11.sp)
        }
        labeledField(L10n.t("ns.ml.host", vm.language), host,
            L10n.t("ns.ml.host.ph", vm.language)) { host = it }
        labeledField(L10n.t("ns.ml.port", vm.language), port,
            "587") { port = it }
        labeledField(L10n.t("ns.ml.user", vm.language), username,
            L10n.t("ns.ml.user.ph", vm.language)) { username = it }
        labeledField(L10n.t("ns.ml.pass", vm.language)
                + (if (s?.passwordSet == true)
                    " " + L10n.t("ns.ml.saved", vm.language) else ""),
            password,
            L10n.t("ns.ml.pass.ph", vm.language)) { password = it }
        labeledField(L10n.t("ns.ml.from", vm.language), sender,
            L10n.t("ns.ml.user.ph", vm.language)) { sender = it }
        labeledField(L10n.t("ns.ml.link", vm.language)
                + L10n.t("ns.ml.link.note", vm.language), publicUrl,
            L10n.t("ns.ml.link.ph", vm.language)) { publicUrl = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("ns.set.save", vm.language),
                enabled = host.isNotBlank()) {
                vm.call({ ApiClient.saveMailSettings(host.trim(),
                    port.trim().toIntOrNull() ?: 587, username.trim(),
                    password, sender.trim(), publicUrl.trim()) }) { r ->
                    took(r)
                    if (r.isSuccess) password = ""
                }
            }
            SmallAction(L10n.t("ns.bas.reset", vm.language)) {
                vm.call({ ApiClient.clearMailSettings() }) { r ->
                    took(r)
                    if (r.isSuccess) {
                        host = ""; username = ""; password = ""; sender = ""
                    }
                }
            }
        }
        labeledField(L10n.t("ns.ml.test", vm.language), testTo,
            L10n.t("ns.ml.test.ph", vm.language)) { testTo = it }
        SmallAction(L10n.t("ns.ml.test", vm.language)) {
            if (testTo.isNotBlank())
                vm.call({ ApiClient.testMail(testTo.trim()) }) { r ->
                    error = r.exceptionOrNull()?.message
                    testSentTo = r.getOrNull()
                }
        }
        testSentTo?.let {
            Text("\u2713 $it", color = Jim.Green, fontSize = 11.sp)
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}

// ---- the guide, the help box, and the dock in the corner ----
// Console doors since 0.19.x; these are the phone's. The help box calls no
// model and says so on its face; the dock never acts.

@Composable
private fun GuidePanel(vm: GuardianViewModel) {
    var outline by remember { mutableStateOf<TutorialOutline?>(null) }
    var progress by remember { mutableStateOf<TutorialProgress?>(null) }
    var stepDetail by remember { mutableStateOf<TutorialStep?>(null) }
    var screenNumber by remember { mutableStateOf("") }
    var question by remember { mutableStateOf("") }
    var answer by remember { mutableStateOf<HelpAnswer?>(null) }
    var topics by remember { mutableStateOf<List<String>>(emptyList()) }
    var showTopics by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        vm.call({ ApiClient.tutorialOutline() }) { r ->
            outline = r.getOrNull()
        }
        vm.call({ ApiClient.tutorialProgress(vm.uid!!) }) { r ->
            progress = r.getOrNull()
        }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.gd.title", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        outline?.let { Text(it.guide, color = Jim.T2, fontSize = 11.sp) }
        val p = progress
        if (p != null) {
            Text(L10n.t("ns.gd.progress", vm.language)
                    .replace("{d}", p.done.toString())
                    .replace("{t}", p.total.toString())
                    + " \u00b7 " + p.note,
                color = Jim.T2, fontSize = 11.sp)
            p.step?.let { step ->
                Text("${step.chapter} \u00b7 ${step.title}", color = Jim.Txt,
                    fontSize = 12.sp, fontWeight = FontWeight.Bold)
                step.what?.let {
                    Text(it, color = Jim.T2, fontSize = 11.sp)
                }
                Text(step.tryIt, color = Jim.T2, fontSize = 11.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    BrandButton(L10n.t("ns.gd.done", vm.language)) {
                        vm.call({ ApiClient.markTutorialDone(vm.uid!!,
                            step.key) }) { r ->
                            error = r.exceptionOrNull()?.message
                            r.getOrNull()?.let { progress = it }
                            stepDetail = null
                        }
                    }
                    // The canonical lesson, re-read from its own route.
                    SmallAction(L10n.t("ns.gd.step", vm.language)) {
                        vm.call({ ApiClient.tutorialStep(step.key) }) { r ->
                            stepDetail = r.getOrNull()
                        }
                    }
                }
            }
        } else {
            BrandButton(L10n.t("ns.gd.start", vm.language)) {
                vm.call({ ApiClient.startTutorial(vm.uid!!) }) { r ->
                    error = r.exceptionOrNull()?.message
                    r.getOrNull()?.let { progress = it }
                }
            }
        }
        stepDetail?.let { step ->
            Text("${step.chapter} \u00b7 ${step.title}", color = Jim.Txt,
                fontSize = 12.sp, fontWeight = FontWeight.Bold)
            step.what?.let { Text(it, color = Jim.T2, fontSize = 11.sp) }
            Text(step.tryIt, color = Jim.T2, fontSize = 11.sp)
        }
        // A screen can explain itself: the gallery number is enough.
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            labeledField(L10n.t("ns.gd.screen", vm.language), screenNumber,
                "61") { screenNumber = it }
        }
        SmallAction(L10n.t("ns.gd.screen", vm.language)) {
            screenNumber.trim().toIntOrNull()?.let { number ->
                vm.call({ ApiClient.tutorialForScreen(number) }) { r ->
                    error = r.exceptionOrNull()?.message
                    stepDetail = r.getOrNull()
                }
            }
        }
        labeledField("", question,
            L10n.t("ns.gd.ask.ph", vm.language)) { question = it }
        SmallAction(L10n.t("ns.gd.ask.ph", vm.language)) {
            if (question.isNotBlank())
                vm.call({ ApiClient.askHelp(question.trim()) }) { r ->
                    error = r.exceptionOrNull()?.message
                    answer = r.getOrNull()
                }
        }
        answer?.let { a ->
            Text(a.answer, color = Jim.Txt, fontSize = 11.sp)
            Text(a.disclosure, color = Jim.T3, fontSize = 10.sp)
        }
        SmallAction(L10n.t("ns.gd.topics", vm.language)) {
            showTopics = !showTopics
            if (showTopics)
                vm.call({ ApiClient.helpTopics() }) { r ->
                    topics = r.getOrDefault(emptyList())
                }
        }
        if (showTopics) topics.take(8).forEach {
            Text(it, color = Jim.T2, fontSize = 11.sp)
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}

@Composable
private fun DockPanel(vm: GuardianViewModel) {
    var vocabulary by remember { mutableStateOf<DockVocabulary?>(null) }
    var dock by remember { mutableStateOf<DockState?>(null) }
    var detail by remember { mutableStateOf<DockFace?>(null) }
    var place by remember { mutableStateOf<DockWhere?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    fun configure(corner: String? = null, state: String? = null,
                  face: String? = null) {
        vm.call({ ApiClient.configureDock(vm.uid!!, vm.token!!, corner,
            state, face) }) { r ->
            error = r.exceptionOrNull()?.message
            r.getOrNull()?.let { dock = it }
        }
    }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.dockVocabulary() }) { r ->
            vocabulary = r.getOrNull()
        }
        vm.call({ ApiClient.dockState(vm.uid!!, vm.token!!) }) { r ->
            dock = r.getOrNull()
        }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.dk.title", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        val d = dock
        if (d != null) {
            Text(L10n.t("ns.dk.line", vm.language)
                    .replace("{corner}", d.corner)
                    .replace("{state}", d.state)
                    .replace("{forced}", if (d.forced) " !" else "")
                    .replace("{face}", d.face ?: ""),
                color = Jim.T2, fontSize = 11.sp)
            d.why?.let { Text(it, color = Jim.Amber, fontSize = 11.sp) }
        }
        val v = vocabulary
        if (v != null && d != null) {
            // Per-surface faces are configured only — their detail needs a
            // particular surface to be about, which this card is not.
            v.faces.keys.sorted().chunked(3).forEach { rowNames ->
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    rowNames.forEach { name ->
                        FilterChip(selected = d.face == name,
                            onClick = {
                                configure(face = name)
                                if (name !in v.perSurface) {
                                    vm.call({ ApiClient.dockFace(vm.uid!!,
                                        vm.token!!, name) }) { r ->
                                        detail = r.getOrNull()
                                    }
                                    vm.call({ ApiClient.dockWhere(name) }) { r ->
                                        place = r.getOrNull()
                                    }
                                }
                            },
                            label = { Text(name, fontSize = 10.sp) })
                    }
                }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                v.states.keys.sorted().forEach { name ->
                    FilterChip(selected = d.wanted == name,
                        onClick = { configure(state = name) },
                        label = { Text(name, fontSize = 10.sp) })
                }
            }
            SmallAction(L10n.t("ns.dk.move", vm.language)) {
                v.corners.keys.firstOrNull { it != d.corner }?.let {
                    configure(corner = it)
                }
            }
        }
        detail?.let { f ->
            Text(f.face, color = Jim.Txt, fontSize = 12.sp,
                fontWeight = FontWeight.Bold)
            Text(f.shows, color = Jim.T2, fontSize = 11.sp)
            place?.let { w ->
                Text("\u2192 ${w.title} \u00b7 ${w.screen}", color = Jim.T3,
                    fontSize = 10.sp)
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}

// ---- the wrist and the doorway ----
// The drip channel's setup card and the paired embodiments. Console doors
// since 0.6.0 / 0.19.x; these are the phone's.

@Composable
private fun WatchPanel(vm: GuardianViewModel) {
    var setup by remember { mutableStateOf<WatchSetup?>(null) }
    var pair by remember { mutableStateOf<PairInfo?>(null) }
    var showSteps by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val context = androidx.compose.ui.platform.LocalContext.current

    val picker = androidx.activity.compose.rememberLauncherForActivityResult(
        androidx.activity.result.contract.ActivityResultContracts.OpenDocument()
    ) { uri ->
        if (uri != null) {
            val bytes = context.contentResolver.openInputStream(uri)
                ?.use { it.readBytes() }
            if (bytes != null)
                vm.call({ ApiClient.seedWatch(vm.uid!!, vm.token!!,
                    bytes) }) { r ->
                    error = r.exceptionOrNull()?.message
                }
        }
    }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.watchSetup(vm.uid!!, vm.token!!) }) { r ->
            setup = r.getOrNull()
        }
        vm.call({ ApiClient.pairInfo() }) { r -> pair = r.getOrNull() }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.wt.title", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.wt.lead", vm.language), color = Jim.T2,
            fontSize = 11.sp)
        val s = setup
        if (s != null) {
            s.devices.chunked(2).forEach { rowDevices ->
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    rowDevices.forEach { device ->
                        FilterChip(selected = s.device == device.key,
                            onClick = {
                                vm.call({ ApiClient.watchSetup(vm.uid!!,
                                    vm.token!!, device.key) }) { r ->
                                    setup = r.getOrNull() ?: setup
                                }
                            },
                            label = { Text(device.name, fontSize = 10.sp) })
                    }
                }
            }
            Text(L10n.t("ns.wt.address", vm.language), color = Jim.T2,
                fontSize = 11.sp, fontWeight = FontWeight.Bold)
            Text(s.dripUrl, color = Jim.Txt, fontSize = 11.sp)
            Text("${s.drips} \u00b7 ${s.lastDripAt ?: "\u2014"}",
                color = Jim.T3, fontSize = 10.sp)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SmallAction(L10n.t("ns.wt.setup", vm.language)) {
                    showSteps = !showSteps
                }
                // Rotating invalidates the old drip token.
                SmallAction(L10n.t("ns.bas.reset", vm.language)) {
                    vm.call({ ApiClient.rotateWatchChannel(vm.uid!!,
                        vm.token!!) }) { r ->
                        error = r.exceptionOrNull()?.message
                        setup = r.getOrNull() ?: setup
                    }
                }
                SmallAction(L10n.t("ns.wt.seed", vm.language)) {
                    picker.launch(arrayOf("application/zip", "text/xml",
                                          "application/xml"))
                }
            }
            if (showSteps) s.steps.forEachIndexed { i, step ->
                Text("${i + 1}. $step", color = Jim.T2, fontSize = 11.sp)
            }
            Text(s.seedHint, color = Jim.T3, fontSize = 10.sp)
        }
        pair?.let { p ->
            // The pairing card's own words, straight from the wire.
            p.how.forEach { line ->
                Text(line, color = Jim.T2, fontSize = 11.sp,
                    fontWeight = FontWeight.Bold)
            }
            Text(p.consoleUrl, color = Jim.Txt, fontSize = 11.sp)
            Text(p.note, color = Jim.T3, fontSize = 10.sp)
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}

@Composable
private fun DevicesPanel(vm: GuardianViewModel) {
    var rows by remember { mutableStateOf<List<DeviceRow>>(emptyList()) }
    var name by remember { mutableStateOf("") }
    var kind by remember { mutableStateOf("speaker") }
    var paired by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }
    // The server's DeviceRegister kinds, shown in its own words like the
    // mic types are.
    val kinds = listOf("wearable", "stationary", "autonomous", "speaker",
                       "phone", "glasses", "headset", "spatial", "other")

    fun reload() {
        vm.call({ ApiClient.devices(vm.uid!!, vm.token!!) }) { r ->
            rows = r.getOrDefault(emptyList())
        }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.dv.bluetooth", vm.language), color = Jim.Txt,
            fontSize = 16.sp, fontWeight = FontWeight.Bold)
        rows.forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("${row.name} \u00b7 ${row.kind}", color = Jim.Txt,
                    fontSize = 11.sp)
                if (row.paired)
                    Text(L10n.t("ns.dv.paired", vm.language),
                        color = Jim.Green, fontSize = 11.sp)
            }
        }
        labeledField("", name, "") { name = it }
        kinds.chunked(3).forEach { rowKinds ->
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                rowKinds.forEach { choice ->
                    FilterChip(selected = kind == choice,
                        onClick = { kind = choice },
                        label = { Text(choice, fontSize = 10.sp) })
                }
            }
        }
        Row(verticalAlignment = Alignment.CenterVertically) {
            Switch(checked = paired, onCheckedChange = { paired = it })
            Text(L10n.t("ns.dv.paired", vm.language), color = Jim.T2,
                fontSize = 11.sp)
        }
        BrandButton(L10n.t("ns.dv.bluetooth", vm.language),
            enabled = name.isNotBlank()) {
            vm.call({ ApiClient.registerDevice(vm.uid!!, vm.token!!,
                name.trim(), kind, paired) }) { r ->
                error = r.exceptionOrNull()?.message
                if (r.isSuccess) name = ""
                reload()
            }
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 11.sp) }
    }
}

// The voice pair, spoken and heard: text goes out through /voice/speak
// and comes back as audio — or the device's own voice reads it when no
// speaking service is configured, because silence would be the wrong
// failure. The microphone records a short clip and /voice/transcribe
// hands back the words; the audio is not stored server-side. The health
// line at the bottom is the backend's own pulse. Console door (the
// Coach's orb); this is the phone's.
//
// Line comments on purpose: the release-parse guard strips block
// comments before counting braces, and the image mime literal in
// CapturesPanel above reads to that stripper as a block-comment opener.
// A block comment anywhere after it would hand the stripper its closing
// half and swallow the thousand lines between.
@Composable
private fun TalkPanel(vm: GuardianViewModel) {
    val context = LocalContext.current
    var text by remember { mutableStateOf("") }
    var heard by remember { mutableStateOf("") }
    var deviceSpoke by remember { mutableStateOf(false) }
    var recording by remember { mutableStateOf(false) }
    var micRefused by remember { mutableStateOf(false) }
    var health by remember { mutableStateOf<HealthK?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    val recorder = remember { mutableStateOf<android.media.MediaRecorder?>(null) }
    val clip = remember { mutableStateOf<java.io.File?>(null) }
    val tts = remember { mutableStateOf<android.speech.tts.TextToSpeech?>(null) }
    DisposableEffect(Unit) {
        val engine = android.speech.tts.TextToSpeech(context) { }
        tts.value = engine
        onDispose { engine.shutdown() }
    }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.health() }) { r -> r.fold({ health = it }, { }) }
    }

    fun sendClip() {
        val file = clip.value ?: return
        val encoded = android.util.Base64.encodeToString(
            file.readBytes(), android.util.Base64.NO_WRAP)
        vm.call({ ApiClient.transcribe(encoded, "speech.m4a") }) { r ->
            r.fold({ heard = it.text }, { error = it.message })
        }
    }

    fun beginRecording() {
        val file = java.io.File(context.cacheDir, "speech.m4a")
        @Suppress("DEPRECATION") val rec = android.media.MediaRecorder()
        try {
            rec.setAudioSource(android.media.MediaRecorder.AudioSource.MIC)
            rec.setOutputFormat(android.media.MediaRecorder.OutputFormat.MPEG_4)
            rec.setAudioEncoder(android.media.MediaRecorder.AudioEncoder.AAC)
            rec.setOutputFile(file.absolutePath)
            rec.prepare(); rec.start()
            recorder.value = rec; clip.value = file; recording = true
        } catch (e: Exception) { error = e.message }
    }

    val ask = androidx.activity.compose.rememberLauncherForActivityResult(
        androidx.activity.result.contract.ActivityResultContracts.RequestPermission()
    ) { granted -> if (granted) beginRecording() else micRefused = true }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.vs.title", vm.language), color = Jim.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("ns.vs.title", vm.language), text,
            L10n.t("ns.vc.say.ph", vm.language)) { text = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("ns.vc.speak", vm.language),
                enabled = text.isNotBlank()) {
                deviceSpoke = false; error = null
                val toSay = text.trim()
                vm.call({ ApiClient.speakAloud(toSay) }) { r ->
                    r.fold({ bytes ->
                        try {
                            val out = java.io.File(context.cacheDir, "said.mp3")
                            out.writeBytes(bytes)
                            android.media.MediaPlayer().apply {
                                setDataSource(out.absolutePath)
                                setOnCompletionListener { release() }
                                prepare(); start()
                            }
                        } catch (e: Exception) { error = e.message }
                    }, {
                        // 503 and everything else: the device's own voice.
                        tts.value?.speak(toSay,
                            android.speech.tts.TextToSpeech.QUEUE_FLUSH,
                            null, "jim-say")
                        deviceSpoke = true
                    })
                }
            }
            SmallAction(L10n.t(if (recording) "ns.vc.stop" else "ns.vc.talk",
                    vm.language)) {
                if (recording) {
                    try { recorder.value?.stop() } catch (_: Exception) { }
                    recorder.value?.release(); recorder.value = null
                    recording = false
                    sendClip()
                } else {
                    micRefused = false
                    ask.launch(android.Manifest.permission.RECORD_AUDIO)
                }
            }
        }
        if (deviceSpoke) {
            Text(L10n.t("ns.vc.device", vm.language), color = Jim.Amber,
                fontSize = 11.sp)
        }
        if (micRefused) {
            Text(L10n.t("ns.vc.mic.refused", vm.language), color = Jim.Amber,
                fontSize = 11.sp)
        }
        if (heard.isNotEmpty()) {
            Text(heard, color = Jim.T2, fontSize = 12.sp)
        }
        health?.let {
            Text("${it.status} \u00b7 ${it.tandem}", color = Jim.T3,
                fontSize = 10.sp)
        }
        error?.let { Text(it, color = Jim.Red, fontSize = 12.sp) }
    }
}
