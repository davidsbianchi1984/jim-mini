using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

public sealed partial class SafetyPage : Page
{
    public record FlowRow(string Label, string Detail);
    public record PolicyRow(string Severity, string Tier);

    public sealed class RobotRow
    {
        public string Id { get; init; } = "";
        public string Name { get; init; } = "";
        public string Status { get; init; } = "";
        public string Directive { get; init; } = "";
        public string Rating { get; init; } = "";
        public bool Assist { get; init; }
        public bool Perform { get; init; }
        public bool PerformingCpr { get; init; }
        public bool Waived { get; init; }
        public string UnbindLabel => L10n.T("rch.body.unbind");
        public Visibility AssistVisibility =>
            Assist ? Visibility.Visible : Visibility.Collapsed;
        public Visibility PerformVisibility =>
            Perform ? Visibility.Visible : Visibility.Collapsed;
        // A template is stamped once per robot, so there is no named control
        // to assign to; the row is where the lookup goes. These are the
        // buttons that put a machine's hands on somebody's chest.
        public string AedLabel => L10n.T("fa.aed");
        public string CoachLabel => L10n.T("fa.coach");
        public string EmsLabel => L10n.T("fa.ems");
        public string PerformLabel => L10n.T("fa.perform");
        public string StartLabel => L10n.T("fa.start");
        public string AutoLabel => L10n.T("res.auto");
        public string StopLabel => L10n.T("fa.stop");
        public Visibility StopVisibility =>
            PerformingCpr ? Visibility.Visible : Visibility.Collapsed;
        public Visibility WaivedVisibility =>
            Waived && !PerformingCpr ? Visibility.Visible : Visibility.Collapsed;
        public Visibility ConfirmGateVisibility =>
            !Waived && !PerformingCpr ? Visibility.Visible : Visibility.Collapsed;
    }

    private RobotSpec[] _catalog = Array.Empty<RobotSpec>();
    private bool _loading;   // suppress SelectionChanged while populating
    private string? _pendingCprRobot;
    private bool _waiverSigned;

    public SafetyPage()
    {
        InitializeComponent();
        LocalizeTheRest();
    }

    /// The rest of the same screen.
    ///
    /// `LocalizeAlarmSurface` below covers what the alarm *says* once it is
    /// going. It does not cover what arms it, fires it, or signs away the
    /// confirmation before a machine starts compressions — because the count
    /// those strings were chosen from could not see a string picked by a
    /// ternary, and `Click for emergency` is one.
    ///
    ///     asked     is the alarm's own wording localized
    ///     mattered  is the control that starts it
    private void LocalizeTheRest()
    {
        AlarmsPivot.Header = L10n.T("alarm.lead.short");
        SosPivot.Header = L10n.T("sos");
        CrashPivot.Header = L10n.T("cw.short");
        MedPivot.Header = L10n.T("mid.short");
        PolicyPivot.Header = L10n.T("cw.policy");
        RobotsPivot.Header = L10n.T("rob.short");

        ResponderBox.Header = L10n.T("res.name");
        AlarmQuestionBox.Header = L10n.T("sos.whatdo");
        AlarmAskButton.Content = L10n.T("sos.ask");

        SosLabel.Text = L10n.T("sos");
        SosHint.Text = L10n.T("sos.click");
        SituationBox.Header = L10n.T("sos.what");
        LocationBox.Header = L10n.T("sos.where");

        CrashHead.Text = L10n.T("cw");
        CrashSub.Text = L10n.T("cw.sub");
        CrashName.Header = L10n.T("cw.trusted");
        CrashName.PlaceholderText = "Rosa";
        CrashChannel.Header = L10n.T("cw.reach");
        CrashChannel.PlaceholderText = "rosa@example.com";
        CrashAttempts.Header = L10n.T("cw.attempts");
        CrashWindow.Header = L10n.T("cw.minutes");
        CrashArmButton.Content = L10n.T("cw.arm");
        CrashDisarmButton.Content = L10n.T("cw.disarm");

        MedHead.Text = L10n.T("mid");
        MedSub.Text = L10n.T("mid.sub");
        IssueButton.Content = L10n.T("mid.issue");
        IssuedHead.Text = L10n.T("mid.issued");
        PrintHint.Text = L10n.T("mid.print");
        RevokeCardButton.Content = L10n.T("mid.revoke");

        SensitivityBox.Header = L10n.T("cw.sensitivity");
        SensCautious.Content = L10n.T("cw.cautious");
        SensBalanced.Content = L10n.T("cw.balanced");
        SensAssertive.Content = L10n.T("cw.assertive");
        SensSub.Text = L10n.T("cw.sensitivity.sub");

        RobotModelBox.Header = L10n.T("rob.bind");
        BindButton.Content = L10n.T("rob.bind.go");
        RobotsSub.Text = L10n.T("rob.sub");
        WaiverHead.Text = L10n.T("res.waiver");
        WaiverBadge.Text = L10n.T("res.signed");
        SignatureBox.Header = L10n.T("res.sign.ph");
        SignWaiverButton.Content = L10n.T("res.sign");
        RevokeWaiverButton.Content = L10n.T("res.revoke");
        ConfirmCprButton.Content = L10n.T("fa.confirm");
    }

    /// The alarm surface's wording, in the reader's language.
    ///
    /// These are the strings where misunderstanding changes what happens to a
    /// person — the question the crash watch asks, the three answers to an
    /// open alarm, and the line saying this screen cannot call an ambulance.
    /// They were English on all three shells while the tab above them read
    /// *Seguridad*.
    ///
    ///     asked     is the chrome localized
    ///     mattered  is the decision localized
    ///
    /// Applied here rather than in XAML because a XAML literal cannot be
    /// re-read when the language changes.
    private void LocalizeAlarmSurface()
    {
        AlarmsEmpty.Text = L10n.T("alarm.none") + " " + L10n.T("alarm.lead");
        AcceptButton.Content = L10n.T("alarm.going");
        EscalateButton.Content = L10n.T("alarm.cannot_go");
        ClearAlarmButton.Content = L10n.T("alarm.clear");
        AlarmNotEmergency.Text = L10n.T("alarm.not_emergency");
        CrashAskingTitle.Text = L10n.T("alarm.asking");
        ImOkayButton.Content = L10n.T("alarm.im_okay");
        CrashEms.Content = L10n.T("alarm.ems");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        LocalizeAlarmSurface();
        LocalizeBeacons();
        await LoadAlarms();
        await LoadBeacons();
        await LoadRelay();
        await LoadPolicy();
        await LoadRobots();
        await LoadCrashWatch();
        LocalizeVigil();
        await SweepVigil();
    }

    // -- alarms --
    //
    // The gap this closes: this shell could raise an emergency and command a
    // bound robot to perform CPR, and could not answer the alarm about it.
    // There was no occurrence of the word "alarm" anywhere in it.
    //
    // An alarm is raised when a stranger scans the care code on somebody's
    // door, and the household relay pages a responder — a neighbour, an
    // on-call carer. Accepting is the act that stops the ladder climbing to
    // emergency services, so a responder who cannot accept leaves only the
    // path that ends in an ambulance.

    private string? _openAlarmId;

    private sealed record AlarmCard(string Raised, string Said, string CannotDial,
                                    string Attending);

    private async System.Threading.Tasks.Task LoadAlarms()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var rows = await ApiClient.Shared.Alarms(s.Uid, s.Token);
            var open = rows.Where(a => a.State == "open").ToList();
            _openAlarmId = open.FirstOrDefault()?.Id;
            AlarmsEmpty.Visibility = open.Count == 0
                ? Visibility.Visible : Visibility.Collapsed;
            AlarmsList.ItemsSource = open.Select(a => new AlarmCard(
                L10n.T("alarm.raised"),
                string.Join("  ", a.Messages ?? System.Array.Empty<string>()),
                // True on every row this queue holds: the beacon path is
                // ceilinged below emergency services, and a crash watch at the
                // top rung sent a dispatch request rather than placing a call.
                a.CallEmergencyServicesYourself == true
                    ? L10n.T("alarm.not_emergency") : "",
                // Accepted is not cleared — the alarm stays open and the card
                // has to say which of the two happened.
                a.AcceptedBy is null
                    ? ""
                    : L10n.T("alarm.attending").Replace("{who}", a.AcceptedBy))
            ).ToList();
            AcceptButton.IsEnabled = _openAlarmId is not null;
            EscalateButton.IsEnabled = _openAlarmId is not null;
            ClearAlarmButton.IsEnabled = _openAlarmId is not null;
        }
        catch (System.Exception ex) { AlarmSaid.Text = ex.Message; }
    }

    private async void OnAcceptAlarm(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _openAlarmId is null) return;
        // The backend refuses an empty responder, and it is right to: "someone
        // accepted it" is the thing this relay exists to stop being enough.
        if (string.IsNullOrWhiteSpace(ResponderBox.Text))
        {
            AlarmSaid.Text = L10n.T("res.needname");
            return;
        }
        try
        {
            var ack = await ApiClient.Shared.AcceptAlarm(
                s.Uid, _openAlarmId, ResponderBox.Text.Trim(), s.Token);
            AlarmSaid.Text = ack.Note ?? "";
            await LoadAlarms();
        }
        catch (System.Exception ex) { AlarmSaid.Text = ex.Message; }
    }

    private async void OnEscalateAlarm(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _openAlarmId is null) return;
        try
        {
            var ack = await ApiClient.Shared.EscalateAlarm(
                s.Uid, _openAlarmId, s.Token);
            AlarmSaid.Text = ack.Note ?? "";
            await LoadAlarms();
        }
        catch (System.Exception ex) { AlarmSaid.Text = ex.Message; }
    }

    private async void OnClearAlarm(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _openAlarmId is null) return;
        try
        {
            var ack = await ApiClient.Shared.ClearAlarm(
                s.Uid, _openAlarmId, s.Token);
            AlarmSaid.Text = ack.Note ?? "";
            await LoadAlarms();
        }
        catch (System.Exception ex) { AlarmSaid.Text = ex.Message; }
    }

    private async void OnAskAlarmGuidance(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Token is null || _openAlarmId is null) return;
        try
        {
            var g = await ApiClient.Shared.AlarmGuidance(
                _openAlarmId, AlarmQuestionBox.Text, s.Token);
            AlarmGuidanceText.Text = g.Note is null
                ? g.Answer : $"{g.Answer}\n\n{g.Note}";
        }
        catch (System.Exception ex) { AlarmSaid.Text = ex.Message; }
    }

    // -- crash watch --

    private void ShowCrashWatch(CrashWatchStatus st)
    {
        if (!string.IsNullOrEmpty(st.TrustedName)) CrashName.Text = st.TrustedName;
        if (st.Attempts is int a) CrashAttempts.Value = a;
        if (st.WindowMinutes is double w) CrashWindow.Value = w;
        CrashEms.IsChecked = st.ContactEms ?? false;
        CrashArmButton.Content = L10n.T(st.Armed ? "action.update" : "cw.arm");
        CrashDisarmButton.Visibility = st.Armed ? Visibility.Visible : Visibility.Collapsed;
        var asking = st.Asking ?? false;
        CrashAskingCard.Visibility = asking ? Visibility.Visible : Visibility.Collapsed;
        if (asking)
            CrashAskingDetail.Text = L10n.T("alarm.concern")
                .Replace("{concern}", st.Concern ?? "")
                .Replace("{n}", $"{st.Attempt ?? 1}")
                .Replace("{total}", $"{st.Attempts ?? 3}");
        var tripped = st.Tripped ?? false;
        CrashTrippedNote.Visibility = tripped ? Visibility.Visible : Visibility.Collapsed;
        if (tripped)
            CrashTrippedNote.Text = L10n.T("alarm.tripped")
                .Replace("{name}", st.TrustedName ?? "");
        var armedQuiet = st.Armed && !asking && !tripped;
        CrashArmedNote.Visibility = armedQuiet ? Visibility.Visible : Visibility.Collapsed;
        if (armedQuiet)
            CrashArmedNote.Text = L10n.T("alarm.armed")
                .Replace("{name}", st.TrustedName ?? "")
                .Replace("{n}", $"{st.Attempts ?? 3}");
    }

    private async System.Threading.Tasks.Task LoadCrashWatch()
    {
        var s = AppState.Current;
        try { ShowCrashWatch(await ApiClient.Shared.CrashWatch(s.Uid!, s.Token!)); }
        catch { /* backend offline — leave the defaults */ }
    }

    private async void OnCrashArm(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        CrashError.Visibility = Visibility.Collapsed;
        try
        {
            ShowCrashWatch(await ApiClient.Shared.ArmCrashWatch(
                s.Uid!, s.Token!, CrashName.Text, CrashChannel.Text,
                (int)CrashAttempts.Value, CrashWindow.Value,
                CrashEms.IsChecked ?? false));
        }
        catch (Exception ex)
        {
            CrashError.Text = ex.Message;
            CrashError.Visibility = Visibility.Visible;
        }
    }

    private async void OnCrashDisarm(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try { ShowCrashWatch(await ApiClient.Shared.DisarmCrashWatch(s.Uid!, s.Token!)); }
        catch { }
    }

    private async void OnImOkay(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try { ShowCrashWatch(await ApiClient.Shared.ImOkay(s.Uid!, s.Token!)); }
        catch { }
    }

    // -- SOS --

    private async void OnSos(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        SosButton.IsEnabled = false;
        SosHint.Text = L10n.T("sos.coordinating");
        SosError.Visibility = Visibility.Collapsed;
        try
        {
            var r = await ApiClient.Shared.Emergency(
                s.Uid!, s.Token!,
                SituationBox.Text.Trim(), LocationBox.Text.Trim());
            var rows = r.Flow.Select(f => new FlowRow(f.Label, f.Detail)).ToList();
            foreach (var d in r.RobotDirectives ?? Array.Empty<RobotDirective>())
                rows.Add(new FlowRow($"🤖 {d.RobotName}",
                                     d.Directive.Replace('_', ' ')));
            FlowList.ItemsSource = rows;
        }
        catch (Exception ex)
        {
            SosError.Text = ex.Message;
            SosError.Visibility = Visibility.Visible;
        }
        finally
        {
            SosButton.IsEnabled = true;
            SosHint.Text = L10n.T("sos.click");
        }
    }

    // -- Policy --

    private async System.Threading.Tasks.Task LoadPolicy()
    {
        var s = AppState.Current;
        _loading = true;
        try
        {
            var p = await ApiClient.Shared.EscalationPolicy(s.Uid!, s.Token!);
            SensitivityBox.SelectedIndex = p.Sensitivity switch
            {
                "cautious" => 0, "assertive" => 2, _ => 1,
            };
            PolicyList.ItemsSource = new[] { "info", "guidance", "critical" }
                .Select(sev => new PolicyRow(
                    char.ToUpper(sev[0]) + sev[1..],
                    (p.BySeverity.TryGetValue(sev, out var t) ? t : "—")
                        .Replace('_', ' ')))
                .ToList();
        }
        catch { /* backend offline — leave empty */ }
        finally { _loading = false; }
    }

    private async void OnSensitivityPicked(object sender, SelectionChangedEventArgs e)
    {
        if (_loading) return;
        var level = (SensitivityBox.SelectedItem as ComboBoxItem)?.Content as string;
        if (level is null) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.SetSensitivity(s.Uid!, s.Token!, level);
            await LoadPolicy();
        }
        catch { /* ignore */ }
    }

    // -- Robots --

    private async System.Threading.Tasks.Task LoadRobots()
    {
        var s = AppState.Current;
        try
        {
            if (_catalog.Length == 0)
            {
                _catalog = (await ApiClient.Shared.Robotics()).Robots;
                RobotModelBox.ItemsSource = _catalog
                    .Select(r => $"{r.Label} · {r.Maker}").ToList();
                if (_catalog.Length > 0) RobotModelBox.SelectedIndex = 0;
            }
            var waiver = await ApiClient.Shared.Waiver(s.Uid!, s.Token!);
            _waiverSigned = waiver.Signed;
            WaiverBadge.Visibility = waiver.Signed ? Visibility.Visible : Visibility.Collapsed;
            SignatureBox.Visibility = waiver.Signed ? Visibility.Collapsed : Visibility.Visible;
            SignWaiverButton.Visibility = waiver.Signed ? Visibility.Collapsed : Visibility.Visible;
            RevokeWaiverButton.Visibility = waiver.Signed ? Visibility.Visible : Visibility.Collapsed;
            WaiverTerms.Text = waiver.Signed ? "" : string.Join("\n", waiver.Terms.Select(t => $"• {t}"));
            WaiverTerms.Visibility = waiver.Signed ? Visibility.Collapsed : Visibility.Visible;
            WaiverBlurb.Text = waiver.Signed
                ? L10n.T("res.signed.by").Replace("{name}", waiver.Signature)
                : L10n.T("res.waiver.sub");

            var robots = await ApiClient.Shared.Robots(s.Uid!, s.Token!);
            RobotsList.ItemsSource = robots.Select(r => new RobotRow
            {
                Id = r.Id,
                Name = r.Name,
                Status = Cap((r.Status ?? "docked").Replace('_', ' ')),
                Directive = r.EscalationDirective is { } d
                    ? $"On escalation: {d.Replace('_', ' ')}" : "",
                Rating = r.FirstAidRating switch
                {
                    "perform" => "CPR-rated",
                    "assist" => "first-aid assist",
                    _ => "",
                },
                Assist = r.Commands?.Contains("fetch_aed") == true,
                Perform = r.Commands?.Contains("perform_cpr") == true,
                PerformingCpr = r.Status == "performing_cpr",
                Waived = _waiverSigned,
            }).ToList();
        }
        catch (Exception ex)
        {
            RobotError.Text = ex.Message;
            RobotError.Visibility = Visibility.Visible;
        }
    }

    private async void OnBind(object sender, RoutedEventArgs e)
    {
        if (RobotModelBox.SelectedIndex < 0
            || RobotModelBox.SelectedIndex >= _catalog.Length) return;
        var s = AppState.Current;
        BindButton.IsEnabled = false;
        RobotError.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.BindRobot(s.Uid!, s.Token!,
                _catalog[RobotModelBox.SelectedIndex].Model);
            await LoadRobots();
        }
        catch (Exception ex)
        {
            RobotError.Text = ex.Message;
            RobotError.Visibility = Visibility.Visible;
        }
        finally { BindButton.IsEnabled = true; }
    }

    // -- robot first-aid commands --

    private async System.Threading.Tasks.Task Command(string robotId,
                                                      string command, string? arg)
    {
        var s = AppState.Current;
        RobotError.Visibility = Visibility.Collapsed;
        try
        {
            var r = await ApiClient.Shared.CommandRobot(
                s.Uid!, s.Token!, robotId, command, arg);
            var line = r.Note ?? r.Instruction ?? r.Status;
            if (r.Sequence is { Length: > 0 })
                line = string.Join(" → ", r.Sequence);
            else if (r.SpokenSteps is { Length: > 0 })
                line = "🔊 " + string.Join(" → ", r.SpokenSteps);
            else if (r.Pace is { } pace)
                line += $" · {pace.CompressionsPerMinute}/min";
            RobotCmdResult.Text = line;
            RobotCmdResult.Visibility = Visibility.Visible;
            await LoadRobots();
        }
        catch (Exception ex)
        {
            RobotError.Text = ex.Message;
            RobotError.Visibility = Visibility.Visible;
        }
    }

    private async void OnFetchAed(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is string id) await Command(id, "fetch_aed", null);
    }

    private async void OnCoachCpr(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is string id) await Command(id, "guide_first_aid", "cpr");
    }

    private async void OnMeetEms(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is string id) await Command(id, "meet_responders", null);
    }

    private void OnPerformCpr(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string id) return;
        _pendingCprRobot = id;
        RobotCmdResult.Text =
            L10n.T("res.confirm.note");
        RobotCmdResult.Visibility = Visibility.Visible;
        ConfirmCprButton.Visibility = Visibility.Visible;
    }

    private async void OnConfirmCpr(object sender, RoutedEventArgs e)
    {
        ConfirmCprButton.Visibility = Visibility.Collapsed;
        if (_pendingCprRobot is { } id)
        {
            _pendingCprRobot = null;
            await Command(id, "perform_cpr", "confirmed");
        }
    }

    private async void OnStopCpr(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is string id) await Command(id, "stop_cpr", null);
    }

    private async void OnAutoCpr(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is string id) await Command(id, "perform_cpr", null);
    }

    private async void OnAutoDefib(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is string id) await Command(id, "auto_defib", null);
    }

    private async void OnSignWaiver(object sender, RoutedEventArgs e)
    {
        var signature = SignatureBox.Text.Trim();
        if (signature.Length == 0) return;
        var s = AppState.Current;
        RobotError.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.SignWaiver(s.Uid!, s.Token!, signature);
            SignatureBox.Text = "";
            RobotCmdResult.Text = L10n.T("res.waiver.signed");
            RobotCmdResult.Visibility = Visibility.Visible;
            await LoadRobots();
        }
        catch (Exception ex)
        {
            RobotError.Text = ex.Message;
            RobotError.Visibility = Visibility.Visible;
        }
    }

    private async void OnRevokeWaiver(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.RevokeWaiver(s.Uid!, s.Token!);
            RobotCmdResult.Text = L10n.T("res.waiver.revoked");
            RobotCmdResult.Visibility = Visibility.Visible;
            await LoadRobots();
        }
        catch (Exception ex)
        {
            RobotError.Text = ex.Message;
            RobotError.Visibility = Visibility.Visible;
        }
    }

    // -- Medical ID --

    public record MedRow(string Label, string Value);

    private async void OnIssueCard(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        IssueButton.IsEnabled = false;
        MedError.Visibility = Visibility.Collapsed;
        try
        {
            var issued = await ApiClient.Shared.IssueMedicalCard(s.Uid!, s.Token!);
            QrUrlText.Text = issued.QrSvgUrl;
            var card = await ApiClient.Shared.MedicalCardView(issued.Token);
            MedRows.ItemsSource = new[]
            {
                new MedRow("Name", card.Name ?? "—"),
                new MedRow("Age", card.Age?.ToString() ?? "—"),
                new MedRow("Resting HR",
                           card.RestingHeartRate is { } hr ? $"{hr} bpm" : "—"),
                new MedRow("Conditions",
                           card.KnownConditions is { Length: > 0 } kc
                               ? string.Join(", ", kc) : "none declared"),
                new MedRow("Contact",
                           card.EmergencyContact is { } ec
                               ? $"{ec.Name ?? "—"} · {ec.Phone ?? "—"}" : "—"),
            }.ToList();
            MedCard.Visibility = Visibility.Visible;
            IssueButton.Content = L10n.T("mid.rotate");
        }
        catch (Exception ex)
        {
            MedError.Text = ex.Message;
            MedError.Visibility = Visibility.Visible;
        }
        finally { IssueButton.IsEnabled = true; }
    }

    private async void OnRevokeCard(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.RevokeMedicalCard(s.Uid!, s.Token!);
            MedCard.Visibility = Visibility.Collapsed;
            IssueButton.Content = L10n.T("mid.issue");
        }
        catch (Exception ex)
        {
            MedError.Text = ex.Message;
            MedError.Visibility = Visibility.Visible;
        }
    }

    private static string Cap(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..];

    // -- the vigil (console door since 0.8.0; this is the desktop's) --
    //
    // The alarm that fires on the ABSENCE of readings: a steward, named and
    // worded in advance, is asked to check on the person when the signals
    // stop. It never calls emergency services — it knocks on a door.

    private void LocalizeVigil()
    {
        VgHead.Text = L10n.T("ns.vg.title");
        VgPitch.Text = L10n.T("ns.vg.pitch");
        VgOkayButton.Content = L10n.T("ns.vg.okay");
        VgName.Header = L10n.T("ns.vg.name");
        VgName.PlaceholderText = L10n.T("ns.vg.name.ph");
        VgChannel.Header = L10n.T("ns.vg.reach");
        VgChannel.PlaceholderText = L10n.T("ns.vg.reach.ph");
        VgDays.Header = L10n.T("ns.vg.days");
        VgWords.Header = L10n.T("ns.vg.words") + L10n.T("ns.vg.words.note");
        VgWords.PlaceholderText = L10n.T("ns.vg.words.ph");
        VgArmButton.Content = L10n.T("ns.vg.arm");
        VgDisarmButton.Content = L10n.T("ns.vg.disarm");
        VgCheckButton.Content = L10n.T("ns.vg.check");
    }

    private void RenderVigil(VigilState st)
    {
        VgError.Visibility = Visibility.Collapsed;
        var tripped = st.Tripped == true;
        VgTrippedNote.Visibility = tripped ? Visibility.Visible
                                           : Visibility.Collapsed;
        VgOkayButton.Visibility = tripped ? Visibility.Visible
                                          : Visibility.Collapsed;
        if (tripped)
            VgTrippedNote.Text = L10n.T("ns.vg.tripped")
                .Replace("{name}", st.StewardName ?? "")
                .Replace("{after}", L10n.T("ns.vg.after")
                    .Replace("{n}", (st.QuietDays ?? 0).ToString()));
        VgArmedNote.Visibility = !tripped && st.Armed
            ? Visibility.Visible : Visibility.Collapsed;
        if (st.Armed)
        {
            VgArmedNote.Text = L10n.T("ns.vg.armed")
                .Replace("{when}", st.SilentHours is { } h
                    ? $"{(int)h} h" : "\u2014")
                .Replace("{name}", st.StewardName ?? "");
            if (VgName.Text.Length == 0) VgName.Text = st.StewardName ?? "";
            if (VgChannel.Text.Length == 0)
                VgChannel.Text = st.StewardChannel ?? "";
            if (st.QuietDays is { } days) VgDays.Value = days;
            if (VgWords.Text.Length == 0) VgWords.Text = st.Note ?? "";
        }
        VgArmButton.Content = st.Armed ? L10n.T("ns.vg.update")
                                       : L10n.T("ns.vg.arm");
        VgDisarmButton.Visibility = st.Armed ? Visibility.Visible
                                             : Visibility.Collapsed;
    }

    private void ShowVigilError(Exception ex)
    {
        VgError.Text = ex.Message;
        VgError.Visibility = Visibility.Visible;
    }

    /// Opening the screen sweeps — idempotent, trips at most once, and
    /// opening the app is the natural moment to ask whether anybody has
    /// gone quiet. Same choice the console made.
    private async System.Threading.Tasks.Task SweepVigil()
    {
        var s = AppState.Current;
        try { RenderVigil(await ApiClient.Shared.SweepVigil(s.Uid!, s.Token!)); }
        catch { /* leave as-is */ }
    }

    private async void OnVigilArm(object sender, RoutedEventArgs e)
    {
        var name = VgName.Text.Trim();
        var channel = VgChannel.Text.Trim();
        if (name.Length == 0 || channel.Length == 0) return;
        var s = AppState.Current;
        try
        {
            RenderVigil(await ApiClient.Shared.ArmVigil(s.Uid!, s.Token!,
                name, channel, VgDays.Value, VgWords.Text.Trim()));
        }
        catch (Exception ex) { ShowVigilError(ex); }
    }

    private async void OnVigilDisarm(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            RenderVigil(await ApiClient.Shared.DisarmVigil(s.Uid!, s.Token!));
        }
        catch (Exception ex) { ShowVigilError(ex); }
    }

    /// A read, not a sweep — the way to look without acting.
    private async void OnVigilCheck(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            RenderVigil(await ApiClient.Shared.VigilStatus(s.Uid!, s.Token!));
        }
        catch (Exception ex) { ShowVigilError(ex); }
    }

    private async void OnVigilOkay(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            RenderVigil(await ApiClient.Shared.ResolveVigil(s.Uid!, s.Token!));
        }
        catch (Exception ex) { ShowVigilError(ex); }
    }


    private async void OnUnbindRobot(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string robotId)
            return;
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            await ApiClient.Shared.UnbindRobot(s.Uid, s.Token, robotId);
            await LoadRobots();
        }
        catch { /* the row keeps its state */ }
    }

    // ---- the sticker and the relay ----

    private string? _previewBeacon;

    private void LocalizeBeacons()
    {
        BcnHead.Text = L10n.T("sfy.beacons");
        BcnPitch.Text = L10n.T("sfy.beacons.pitch");
        BcnBystander.Text = L10n.T("sfy.beacons.bystander");
        BcnLabel.PlaceholderText = L10n.T("sfy.beacons.label.ph");
        BcnWhere.PlaceholderText = L10n.T("sfy.beacons.where.ph");
        BcnPlaceButton.Content = L10n.T("sfy.beacons.place");
        BcnRaiseButton.Content = L10n.T("att.alarm.raise");
        RelHead.Text = L10n.T("att.relay");
    }

    private static TextBlock BcnLine(string text, string brush) => new()
    {
        Text = text,
        FontSize = 11,
        TextWrapping = TextWrapping.Wrap,
        Foreground = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources[brush],
    };

    private async System.Threading.Tasks.Task LoadBeacons()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var rows = await ApiClient.Shared.Beacons(s.Uid, s.Token);
            BcnRows.Children.Clear();
            foreach (var row in rows)
            {
                var line = new StackPanel
                { Orientation = Orientation.Horizontal, Spacing = 8 };
                var scans = L10n.T("sfy.beacons.scans")
                    .Replace("{n}", row.Scans.ToString());
                var retired = row.Active ? "" : " · " + L10n.T("sfy.beacons.retired");
                line.Children.Add(BcnLine($"{row.Label} · {scans}{retired}",
                                          "JimT2Brush"));
                var bid = row.Id;
                var open = new Button
                {
                    Content = L10n.T("att.open"), FontSize = 11,
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                        Microsoft.UI.Colors.Transparent),
                };
                open.Click += async (_, _) =>
                {
                    try
                    {
                        // Fetched to prove the door is live; a stranger reads
                        // it in a browser, so hand it to one.
                        var page = await ApiClient.Shared.ScannedBeaconPage(bid);
                        if (page.Html.Length > 0)
                            await Windows.System.Launcher.LaunchUriAsync(page.Page);
                    }
                    catch (Exception ex) { ShowBeaconError(ex.Message); }
                };
                line.Children.Add(open);
                var preview = new Button
                {
                    Content = L10n.T("rch.acc.beacon"), FontSize = 11,
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                        Microsoft.UI.Colors.Transparent),
                };
                preview.Click += async (_, _) => await PreviewBeacon(bid);
                line.Children.Add(preview);
                var retire = new Button
                {
                    Content = L10n.T("aim.budget.remove"), FontSize = 11,
                    IsEnabled = row.Active,
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                        Microsoft.UI.Colors.Transparent),
                };
                retire.Click += async (_, _) =>
                {
                    try
                    {
                        await ApiClient.Shared.RetireBeacon(bid, s.Token);
                        await LoadBeacons();
                    }
                    catch (Exception ex) { ShowBeaconError(ex.Message); }
                };
                line.Children.Add(retire);
                BcnRows.Children.Add(line);
                // The sticker's own image: the door is the URL a browser or
                // printer fetches.
                BcnRows.Children.Add(BcnLine(
                    L10n.T("qr.addr") + " " + ApiClient.Shared.BeaconQrUrl(row.Id),
                    "JimT3Brush"));
            }
        }
        catch { /* backend offline */ }
    }

    /// What a stranger sees before deciding to raise the alarm.
    private async System.Threading.Tasks.Task PreviewBeacon(string bid)
    {
        try
        {
            var card = await ApiClient.Shared.BeaconCard(bid);
            _previewBeacon = card.Beacon;
            BcnCardName.Text = card.FirstName ?? "";
            BcnCardName.Visibility = Visibility.Visible;
            BcnCardNote.Text = card.Note ?? "";
            BcnCardNote.Visibility = Visibility.Visible;
            BcnCardBadge.Text = card.Badge ?? "";
            BcnCardBadge.Visibility = Visibility.Visible;
            BcnRaiseButton.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowBeaconError(ex.Message); }
    }

    private async void OnRaiseBeaconAlarm(object sender, RoutedEventArgs e)
    {
        if (_previewBeacon is not { } bid) return;
        try
        {
            var alarm = await ApiClient.Shared.RaiseBeaconAlarm(bid);
            BcnAlarmLine.Text = $"{alarm.Badge ?? ""} {alarm.Note ?? ""}";
            BcnAlarmLine.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowBeaconError(ex.Message); }
    }

    private async void OnPlaceBeacon(object sender, RoutedEventArgs e)
    {
        var label = BcnLabel.Text.Trim();
        if (label.Length == 0) return;
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            await ApiClient.Shared.PlaceBeacon(s.Uid, s.Token, label,
                                               BcnWhere.Text.Trim());
            BcnLabel.Text = ""; BcnWhere.Text = "";
            await LoadBeacons();
        }
        catch (Exception ex) { ShowBeaconError(ex.Message); }
    }

    private async System.Threading.Tasks.Task LoadRelay()
    {
        try
        {
            var channel = await ApiClient.Shared.RelayChannel();
            RelChannel.Text = L10n.T("att.relay.channel") + ": "
                + (channel.Envelope ?? "");
            RelChannel.Visibility = Visibility.Visible;
            RelChannelNote.Text = channel.Note;
            RelChannelNote.Visibility = Visibility.Visible;
        }
        catch { /* backend offline */ }
        try
        {
            var roster = await ApiClient.Shared.RelayRoster();
            RelRoster.Text = L10n.T("att.relay.roster")
                .Replace("{list}", string.Join(", ", roster.Roster))
                .Replace("{c}", roster.Ceiling);
            RelRoster.Visibility = Visibility.Visible;
        }
        catch { /* leave as-is */ }
        try
        {
            var rota = await ApiClient.Shared.RelayRota();
            RelRota.Text = $"{string.Join(", ", rota.OnNow)} · {rota.Timezone}"
                + $" — {rota.Note}";
            RelRota.Visibility = Visibility.Visible;
        }
        catch { /* leave as-is */ }
    }

    private void ShowBeaconError(string message)
    {
        BcnError.Text = message;
        BcnError.Visibility = Visibility.Visible;
    }
}
