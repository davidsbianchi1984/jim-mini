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

    public FamilyPage() => InitializeComponent();

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        base.OnNavigatedTo(e);
        await Reload();
    }

    private static string TierLabel(string oversight) => oversight switch
    {
        "full" => "full oversight (under 13)",
        "alerts_only" => "alerts only — daily life stays private",
        _ => "oversight ended — an adult now",
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
                    ? "Family watch — ⌚ TAPPED" : "Family watch";
                WatchText.Text = string.Join("\n", face.Children.Select(c =>
                {
                    var dot = c.Light switch
                    {
                        "green" => "🟢", "orange" => "🟠", "red" => "🔴",
                        _ => "⚪",
                    };
                    var extra = c.Critical24h is > 0 ? " · critical"
                        : c.Escalations24h is > 0 ? " · escalated" : "";
                    var chips = (c.Paused == true ? " · paused" : "")
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
            CreatedMeta.Text = $"Oversight: {c.Oversight} · sensitivity: {c.Sensitivity}";
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
        var s = AppState.Current;
        try
        {
            var o = await ApiClient.Shared.ChildOverviewOf(s.Uid!, cid, s.Token!);
            if (o.Note is { } note)
            {
                OverviewTitle.Text = "Oversight ended";
                OverviewText.Text = note;
            }
            else
            {
                OverviewTitle.Text = $"{o.DisplayName} — {TierLabel(o.Oversight)}";
                var lines = new List<string>();
                if (o.PrivacyNote is { } p) lines.Add($"🔒 {p}");
                if (o.CriticalEvents is > 0)
                    lines.Add($"⚠️ {o.CriticalEvents} critical event(s)");
                foreach (var ev in o.Events ?? Array.Empty<ChildEvent>())
                    lines.Add($"{ev.Type}"
                              + (ev.Condition is { } c ? $" · {c}" : "")
                              + (ev.Severity is { } sv ? $" · {sv.ToUpper()}" : ""));
                if (lines.Count == 0)
                    lines.Add("Nothing in the window — quiet is good news.");
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
            ControlsNote.Text = r.Note ?? "applied";
            ControlsNote.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
        await Reload();
    }
}
