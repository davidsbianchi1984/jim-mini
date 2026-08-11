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
}
