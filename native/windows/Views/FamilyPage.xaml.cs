using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

/// Family: a parent sets up — and watches over — a child's account, with an
/// oversight window sized by age (full under 13, alerts-only for teens,
/// closed at 18).
public sealed partial class FamilyPage : Page
{
    private Dictionary<string, string> _kidByLabel = new();
    private string? _openKid;

    public FamilyPage()
    {
        InitializeComponent();
        Localize();
    }

    /// XAML has no table lookup, so every fixed string on this page is
    /// named above and filled in here.
    private void Localize()
    {
        PageTitle.Text = L10n.T("tab.family");
        IntroText.Text = L10n.T("fam.intro");
        SpHead.Text = L10n.T("att.spec");
        SpSeedLocal.Content = L10n.T("att.spec.local");
        SpSeedHosted.Content = L10n.T("att.spec.hosted");
        SpNone.Text = L10n.T("att.spec.none");
        SpCatalogHead.Text = L10n.T("ct.spec");
        SpCatalogChoose.Text = L10n.T("ct.spec.choose");
        SpOtherHead.Text = L10n.T("ct.spec.other");
        SpFindQuery.PlaceholderText = L10n.T("ct.spec.find.hint");
        SpFindButton.Content = L10n.T("ct.spec.find.go");
        SpHandHead.Text = L10n.T("att.hand");
        SpCondition.ItemsSource = SpConditions.ToList();
        SpGoal.PlaceholderText = L10n.T("att.hand.ph");
        SpHandButton.Content = L10n.T("att.hand.go");
        SpWhoButton.Content = L10n.T("att.hand.who");
        SpRefHead.Text = L10n.T("att.ref");
        SpRefNone.Text = L10n.T("att.ref.none");
        SpSeeButton.Content = L10n.T("att.med.see");
        RenderPrepLabel();
        ChildName.Header = L10n.T("fam.child.name");
        ChildBirthdate.Header = L10n.T("fam.child.dob");
        GuardianPhone.Header = L10n.T("fam.child.phone");
        CreateButton.Content = L10n.T("fam.create");
        CreatedTitle.Text = L10n.T("fam.created");
        TokenLabel.Text = L10n.T("fam.token");
        ControlsTitle.Text = L10n.T("fam.controls");
        ControlsSub.Text = L10n.T("fam.pause.sub");
        PauseToggle.Header = L10n.T("fam.pause");
        QuietStartBox.Header = L10n.T("fam.quiet.start");
        QuietEndBox.Header = L10n.T("fam.quiet.end");
        ApplyButton.Content = L10n.T("fam.apply");
        UnlinkButton.Content = L10n.T("fam.unlink.this");
        UnlinkAsk.Text = L10n.T("fam.unlink.ask");
        UnlinkTheirs.Text = L10n.T("fam.theirs");

        CtHead.Text = L10n.T("ns.ct.title");
        CtSub.Text = L10n.T("ns.ct.sub");
        CtPitch.Text = L10n.T("ns.ct.link.pitch");
        CtOrg.Header = L10n.T("ns.ct.link.org");
        CtOrg.PlaceholderText = L10n.T("ns.ct.link.org.ph");
        CtDept.Header = L10n.T("ns.ct.link.dept");
        CtDept.PlaceholderText = L10n.T("ns.ct.link.dept.ph");
        CtToken.Header = L10n.T("ns.ct.link.token");
        CtToken.PlaceholderText = L10n.T("ns.ct.link.token.ph");
        CtLinkButton.Content = L10n.T("ns.ct.link.go");
        CtLinkedHead.Text = L10n.T("ns.ct.linked");
        CtLinkedPitch.Text = L10n.T("ns.ct.linked.pitch");
        CtGoal.Header = L10n.T("ns.ct.linked.goal");
        CtGoal.PlaceholderText = L10n.T("ns.ct.linked.goal.ph");
        CtCoordinateButton.Content = L10n.T("ns.ct.linked.goal");
        CtUnlinkButton.Content = L10n.T("ns.ct.linked.unlink");
        CtPlansEmpty.Text = L10n.T("ns.ct.plans.none");
        UnlinkConfirmButton.Content = L10n.T("fam.unlink");
        KeepLinkButton.Content = L10n.T("fam.keep");
    }

    private void OnUnlinkAsked(object sender, RoutedEventArgs e)
    {
        UnlinkConfirmPanel.Visibility = Visibility.Visible;
        UnlinkButton.Visibility = Visibility.Collapsed;
    }

    private void OnKeepLink(object sender, RoutedEventArgs e)
    {
        UnlinkConfirmPanel.Visibility = Visibility.Collapsed;
        UnlinkButton.Visibility = Visibility.Visible;
    }

    private async void OnUnlinkConfirmed(object sender, RoutedEventArgs e)
    {
        if (_openKid is not { } cid) return;
        var s = AppState.Current;
        UnlinkConfirmPanel.Visibility = Visibility.Collapsed;
        UnlinkButton.Visibility = Visibility.Visible;
        try
        {
            await ApiClient.Shared.UnlinkChild(s.Uid!, cid, s.Token!);
            _openKid = null;
            ControlsCard.Visibility = Visibility.Collapsed;
            OverviewCard.Visibility = Visibility.Collapsed;
            UnlinkNote.Text = L10n.T("fam.unlinked.note");
            UnlinkNote.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
        await Reload();
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        base.OnNavigatedTo(e);
        await Reload();
        await LoadCareTeam();
        await ReloadSpecialists();
        await LoadCatalog();
        await ReloadTasks();
        await ReloadRequests();
    }

    /// Each branch resolves on its own line, rather than picking a key and
    /// handing it to one lookup: a key that is not a literal argument is a
    /// key the dead-key guard cannot see being asked for.
    private static string TierLabel(string oversight) => oversight switch
    {
        "full" => L10n.T("fam.tier.full"),
        "alerts_only" => L10n.T("fam.tier.alerts"),
        _ => L10n.T("fam.tier.ended"),
    };

    /// Literal keys rather than "cw." + the API value, so the dead-key
    /// guard can see that these three rows are asked for.
    private static string SensitivityLabel(string? level) => level switch
    {
        "cautious" => L10n.T("cw.cautious"),
        "assertive" => L10n.T("cw.assertive"),
        _ => L10n.T("cw.balanced"),
    };

    private async Task Reload()
    {
        var s = AppState.Current;
        try
        {
            var kids = await ApiClient.Shared.Children(s.Uid!, s.Token!);
            _kidByLabel = kids.ToDictionary(
                k => $"{k.DisplayName} · {k.Age} — {TierLabel(k.Oversight)}",
                k => k.ChildId);
            KidsList.ItemsSource = _kidByLabel.Keys.ToList();

            var face = await ApiClient.Shared.GuardianWatch(s.Uid!, s.Token!);
            if (face.Children.Length > 0)
            {
                WatchTitle.Text = face.Haptic == "alert"
                    ? $"{L10n.T("fam")} — {L10n.T("fam.tapped")}"
                    : L10n.T("fam");
                WatchText.Text = string.Join("\n", face.Children.Select(c =>
                {
                    var dot = c.Light switch
                    {
                        "green" => "🟢", "orange" => "🟠", "red" => "🔴",
                        _ => "⚪",
                    };
                    var extra = c.Critical24h is > 0
                        ? $" · {L10n.T("fam.st.critical")}"
                        : c.Escalations24h is > 0
                        ? $" · {L10n.T("fam.st.escalated")}" : "";
                    var chips = (c.Paused == true
                                 ? $" · {L10n.T("fam.st.paused")}" : "")
                        + (c.QuietHours is { } q ? $" · 🌙 {q}" : "");
                    return $"{dot} {c.DisplayName}{extra}{chips}";
                }));
                WatchCard.Visibility = Visibility.Visible;
            }
            else WatchCard.Visibility = Visibility.Collapsed;
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
    }

    private async void OnCreate(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        CreateButton.IsEnabled = false;
        try
        {
            var c = await ApiClient.Shared.EnrollChild(
                s.Uid!, s.Token!, ChildName.Text.Trim(),
                ChildBirthdate.Text.Trim(), GuardianPhone.Text.Trim());
            CreatedMeta.Text =
                L10n.T("fam.oversight").Replace("{scope}",
                    c.Oversight == "full"
                        ? L10n.T("fam.scope.full") : L10n.T("fam.scope.alerts"))
                + " · " + L10n.T("fam.sens")
                    .Replace("{level}", SensitivityLabel(c.Sensitivity));
            CreatedToken.Text = c.ChildToken;
            CreatedCard.Visibility = Visibility.Visible;
            ChildName.Text = ""; ChildBirthdate.Text = ""; GuardianPhone.Text = "";
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;   // e.g. minors can't be guardians
            ErrorText.Visibility = Visibility.Visible;
        }
        finally
        {
            CreateButton.IsEnabled = true;
        }
        await Reload();
    }

    private async void OnSelect(object sender, SelectionChangedEventArgs e)
    {
        if (KidsList.SelectedItem is not string label ||
            !_kidByLabel.TryGetValue(label, out var cid)) return;
        _openKid = cid;
        ControlsCard.Visibility = Visibility.Visible;
        ControlsNote.Visibility = Visibility.Collapsed;
        UnlinkNote.Visibility = Visibility.Collapsed;
        UnlinkConfirmPanel.Visibility = Visibility.Collapsed;
        UnlinkButton.Visibility = Visibility.Visible;
        var s = AppState.Current;
        try
        {
            var o = await ApiClient.Shared.ChildOverviewOf(s.Uid!, cid, s.Token!);
            if (o.Note is { } note)
            {
                OverviewTitle.Text = L10n.T("fam.unlinked");
                OverviewText.Text = note;
            }
            else
            {
                OverviewTitle.Text =
                    $"{o.DisplayName ?? L10n.T("fam.child.generic")}"
                    + $" — {TierLabel(o.Oversight)}";
                var lines = new List<string>();
                if (o.PrivacyNote is { } p) lines.Add($"🔒 {p}");
                if (o.CriticalEvents is > 0)
                    lines.Add(L10n.T("fam.critical")
                        .Replace("{n}", $"{o.CriticalEvents}"));
                foreach (var ev in o.Events ?? Array.Empty<ChildEvent>())
                    lines.Add($"{ev.Type}"
                              + (ev.Condition is { } c ? $" · {c}" : "")
                              + (ev.Severity is { } sv ? $" · {sv.ToUpper()}" : ""));
                if (lines.Count == 0)
                    lines.Add(L10n.T("fam.quiet"));
                OverviewText.Text = string.Join("\n", lines);
            }
            OverviewCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
    }

    private async void OnApplyControls(object sender, RoutedEventArgs e)
    {
        if (_openKid is not { } cid) return;
        var s = AppState.Current;
        try
        {
            var r = await ApiClient.Shared.SetFamilyControls(
                s.Uid!, cid, s.Token!, PauseToggle.IsOn,
                QuietStartBox.Text.Trim(), QuietEndBox.Text.Trim());
            ControlsNote.Text = r.Note ?? L10n.T("fam.applied");
            ControlsNote.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
        await Reload();
    }
    // -- the care team ----------------------------------------------------

    private async Task LoadCareTeam()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var team = await ApiClient.Shared.CareTeamState(s.Uid, s.Token);
            CtLinked.Visibility = team.Linked ? Visibility.Visible : Visibility.Collapsed;
            CtLinkForm.Visibility = team.Linked ? Visibility.Collapsed : Visibility.Visible;
            if (team.Linked)
            {
                CtLinkedLine.Text = L10n.T("ns.ct.linked.line")
                    .Replace("{org}", team.OrgId ?? "")
                    .Replace("{dept}", team.DepartmentId ?? "");
                var plans = await ApiClient.Shared.CareTeamPlans(s.Uid, s.Token);
                CtPlans.ItemsSource = plans.Take(4).ToList();
                CtPlansEmpty.Visibility = plans.Length == 0
                    ? Visibility.Visible : Visibility.Collapsed;
            }
        }
        catch (Exception e) { CareTeamError(e); }
    }

    private void CareTeamError(Exception e)
    {
        CtError.Text = e.Message;
        CtError.Visibility = Visibility.Visible;
    }

    private async void OnCareTeamLink(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        CtError.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.CareTeamLink(s.Uid, s.Token,
                CtOrg.Text.Trim(), CtDept.Text.Trim(), CtToken.Password.Trim());
            CtToken.Password = "";
            await LoadCareTeam();
        }
        catch (Exception ex) { CareTeamError(ex); }
    }

    private async void OnCareTeamUnlink(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        CtError.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.CareTeamUnlink(s.Uid, s.Token);
            await LoadCareTeam();
        }
        catch (Exception ex) { CareTeamError(ex); }
    }

    private async void OnCareTeamCoordinate(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var goal = CtGoal.Text.Trim();
        if (goal.Length == 0) return;
        CtError.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.CareTeamCoordinate(s.Uid, s.Token, goal);
            CtGoal.Text = "";
            await LoadCareTeam();
        }
        catch (Exception ex) { CareTeamError(ex); }
    }

    // ---- the specialist economy ----

    private static readonly string[] SpConditions =
        { "anxiety", "depression", "stress", "phobia", "financial_stress",
          "relationship", "physical_distress", "physical_injury" };

    private string SpPicked => SpConditions[
        SpCondition.SelectedIndex >= 0 ? SpCondition.SelectedIndex : 0];

    private void RenderPrepLabel() =>
        SpPrepButton.Content = L10n.T("att.ref.prep").Replace("{c}", SpPicked);

    private static TextBlock SpLine(string text, string brush) => new()
    {
        Text = text,
        FontSize = 11,
        TextWrapping = TextWrapping.Wrap,
        Foreground = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources[brush],
    };

    private async Task ReloadSpecialists()
    {
        try
        {
            var roster = await ApiClient.Shared.Specialists();
            SpRoster.Children.Clear();
            foreach (var row in roster)
                SpRoster.Children.Add(SpLine(
                    $"{row.Condition} — {row.Label} · {row.Mode}", "JimT2Brush"));
            SpNone.Visibility = roster.Length == 0
                ? Visibility.Visible : Visibility.Collapsed;
        }
        catch { /* backend offline */ }
    }

    private async Task LoadCatalog()
    {
        try
        {
            var catalog = await ApiClient.Shared.SpecialistsCatalog();
            SpStarters.Children.Clear();
            var starters = catalog.Starters ?? Array.Empty<CatalogStarter>();
            if (starters.Length == 0)
            {
                SpCatalogNote.Text = L10n.T("ct.spec.empty");
                SpCatalogNote.Visibility = Visibility.Visible;
                return;
            }
            foreach (var starter in starters.Take(6))
            {
                if (starter.ProfileId is not { } pid) continue;
                var button = new Button
                {
                    Content = $"{starter.DisplayName ?? pid} — "
                              + L10n.T("ct.spec.attach"),
                    FontSize = 12,
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                        Microsoft.UI.Colors.Transparent),
                };
                var label = starter.DisplayName ?? pid;
                button.Click += async (_, _) =>
                {
                    try
                    {
                        await ApiClient.Shared.AttachSpecialist(SpPicked, pid,
                                                                label);
                        await ReloadSpecialists();
                    }
                    catch (Exception ex) { ShowSpError(ex.Message); }
                };
                SpStarters.Children.Add(button);
            }
        }
        catch (Exception ex)
        {
            // No QRME endpoint is a posture, not a fault — shown in the
            // server's words.
            SpCatalogNote.Text = ex.Message;
            SpCatalogNote.Visibility = Visibility.Visible;
        }
    }

    /// <summary>The standing caveat beside a found profile, or null when
    /// there is nothing to say.</summary>
    ///
    /// Written as a switch over literal keys rather than a dictionary
    /// lookup, because the guard that finds strings translated and never
    /// read follows literal arguments — a key reached only through a table
    /// reads to it as dead.
    private static string? StandingLine(string? standing) => standing switch
    {
        "specialist.departed" => L10n.T("ct.spec.stand.departed"),
        "specialist.not_active" => L10n.T("ct.spec.stand.not_active"),
        "specialist.adults_only" => L10n.T("ct.spec.stand.adults_only"),
        "specialist.unreachable" => L10n.T("ct.spec.stand.unreachable"),
        _ => null,
    };

    private async void OnFindSpecialist(object sender, RoutedEventArgs e)
    {
        var q = SpFindQuery.Text?.Trim() ?? "";
        if (q.Length == 0) return;
        SpFound.Children.Clear();
        SpFindNote.Visibility = Visibility.Collapsed;
        try
        {
            var out_ = await ApiClient.Shared.SearchSpecialists(q);
            var rows = out_.Results ?? Array.Empty<SpecialistFound>();
            if (rows.Length == 0)
            {
                SpFindNote.Text = L10n.T("ct.spec.find.none");
                SpFindNote.Visibility = Visibility.Visible;
                return;
            }
            if (out_.Capped)
            {
                SpFindNote.Text = L10n.T("ct.spec.find.capped")
                    .Replace("{n}", out_.Limit.ToString());
                SpFindNote.Visibility = Visibility.Visible;
            }
            foreach (var row in rows)
            {
                var caveat = StandingLine(row.Standing);
                var button = new Button
                {
                    Content = row.DisplayName
                              + (caveat is null ? "" : $" — {caveat}")
                              + " — " + L10n.T("ct.spec.attach"),
                    FontSize = 12,
                    // Refused here as well as at the door, so a profile that
                    // could only ever fall back is not a button somebody
                    // presses and then has to wonder about.
                    IsEnabled = row.Attachable,
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                        Microsoft.UI.Colors.Transparent),
                };
                var pid = row.ProfileId;
                var label = row.DisplayName;
                button.Click += async (_, _) =>
                {
                    try
                    {
                        await ApiClient.Shared.AttachSpecialist(SpPicked, pid,
                                                                label);
                        await ReloadSpecialists();
                    }
                    catch (Exception ex) { ShowSpError(ex.Message); }
                };
                SpFound.Children.Add(button);
            }
        }
        catch (Exception ex) { ShowSpError(ex.Message); }
    }

    private async void OnSeedLocal(object sender, RoutedEventArgs e)
    {
        try { await ApiClient.Shared.SeedSpecialists(); await ReloadSpecialists(); }
        catch (Exception ex) { ShowSpError(ex.Message); }
    }

    private async void OnSeedHosted(object sender, RoutedEventArgs e)
    {
        try { await ApiClient.Shared.SeedTandemSpecialists(); await ReloadSpecialists(); }
        catch (Exception ex) { ShowSpError(ex.Message); }
    }

    private async void OnHandOver(object sender, RoutedEventArgs e)
    {
        var goal = SpGoal.Text.Trim();
        if (goal.Length == 0) return;
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var started = await ApiClient.Shared.StartSpecialistTask(
                s.Uid, s.Token, SpPicked, goal);
            SpGoal.Text = "";
            SpStarted.Text = started.Started
                ? started.Id ?? "" : started.Reason ?? "";
            SpStarted.Visibility = Visibility.Visible;
            await ReloadTasks();
        }
        catch (Exception ex) { ShowSpError(ex.Message); }
    }

    private async void OnWho(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        RenderPrepLabel();
        try
        {
            var found = await ApiClient.Shared.ReferralClinicians(
                s.Uid, s.Token, SpPicked);
            SpClinicians.Children.Clear();
            foreach (var clinician in found.Clinicians.Take(4))
                SpClinicians.Children.Add(SpLine(
                    clinician.Label ?? clinician.DisplayName ?? "", "JimT2Brush"));
            if (found.Clinicians.Length == 0 && found.Reason is { } why)
                SpClinicians.Children.Add(SpLine(why, "JimT3Brush"));
        }
        catch (Exception ex) { ShowSpError(ex.Message); }
    }

    private async Task ReloadTasks()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var tasks = await ApiClient.Shared.SpecialistTasks(s.Uid, s.Token);
            SpTasks.Children.Clear();
            foreach (var task in tasks)
            {
                var row = new StackPanel
                { Orientation = Orientation.Horizontal, Spacing = 8 };
                row.Children.Add(SpLine($"{task.Goal} · {task.Status}",
                                        "JimT2Brush"));
                var open = new Button
                {
                    Content = L10n.T("att.open"), FontSize = 11,
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                        Microsoft.UI.Colors.Transparent),
                };
                var taskId = task.Id;
                open.Click += async (_, _) => await OpenTask(taskId, false);
                row.Children.Add(open);
                var advance = new Button
                {
                    Content = L10n.T("att.advance"), FontSize = 11,
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                        Microsoft.UI.Colors.Transparent),
                };
                advance.Click += async (_, _) => await OpenTask(taskId, true);
                row.Children.Add(advance);
                SpTasks.Children.Add(row);
            }
        }
        catch { /* leave as-is */ }
    }

    private async Task OpenTask(string taskId, bool advance)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var view = advance
                ? await ApiClient.Shared.AdvanceSpecialistTask(s.Uid, s.Token,
                                                               taskId)
                : await ApiClient.Shared.SpecialistTask(s.Uid, s.Token, taskId);
            SpOpened.Text = $"{view.Status} · {view.NextPhase ?? ""}"
                + (view.Note is { } note ? $" — {note}" : "");
            SpOpened.Visibility = Visibility.Visible;
            if (advance) await ReloadTasks();
        }
        catch (Exception ex) { ShowSpError(ex.Message); }
    }

    private async void OnPrepare(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            // The console's own placeholder clinician on a deployment with
            // no QRME directory.
            var prepared = await ApiClient.Shared.PrepareReferral(
                s.Uid, s.Token, SpPicked, "prv_local");
            SpPrepared.Text = prepared.Prepared
                ? prepared.Note ?? "" : prepared.Reason ?? "";
            SpPrepared.Visibility = Visibility.Visible;
            await ReloadRequests();
        }
        catch (Exception ex) { ShowSpError(ex.Message); }
    }

    private async Task ReloadRequests()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var requests = await ApiClient.Shared.ReferralRequests(s.Uid,
                                                                   s.Token);
            SpRequests.Children.Clear();
            SpRefNone.Visibility = requests.Length == 0
                ? Visibility.Visible : Visibility.Collapsed;
            foreach (var request in requests)
            {
                var row = new StackPanel
                { Orientation = Orientation.Horizontal, Spacing = 8 };
                row.Children.Add(SpLine(request.Condition, "JimT2Brush"));
                var released = new Button
                {
                    Content = L10n.T("att.ref.released"), FontSize = 11,
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                        Microsoft.UI.Colors.Transparent),
                };
                var requestId = request.Id;
                released.Click += async (_, _) =>
                {
                    try
                    {
                        await ApiClient.Shared.MarkReferralReleased(
                            s.Uid, s.Token, requestId);
                    }
                    catch (Exception ex) { ShowSpError(ex.Message); }
                };
                row.Children.Add(released);
                SpRequests.Children.Add(row);
            }
        }
        catch { /* leave as-is */ }
    }

    private async void OnSeeProvider(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var summary = await ApiClient.Shared.ProviderSummary(s.Uid,
                                                                 s.Token);
            SpProvider.Text = $"{summary.DisplayName ?? ""} · "
                + string.Join(", ", summary.KnownConditions)
                + $" · {summary.Escalations}";
        }
        catch (Exception ex)
        {
            // Not consented is the usual answer, in the server's words.
            SpProvider.Text = ex.Message;
        }
        SpProvider.Visibility = Visibility.Visible;
    }

    private void ShowSpError(string message)
    {
        SpError.Text = message;
        SpError.Visibility = Visibility.Visible;
    }
}
