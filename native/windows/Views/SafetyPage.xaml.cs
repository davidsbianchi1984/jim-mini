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
        public Visibility AssistVisibility =>
            Assist ? Visibility.Visible : Visibility.Collapsed;
        public Visibility PerformVisibility =>
            Perform ? Visibility.Visible : Visibility.Collapsed;
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

    public SafetyPage() => InitializeComponent();

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        await LoadPolicy();
        await LoadRobots();
    }

    // -- SOS --

    private async void OnSos(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        SosButton.IsEnabled = false;
        SosHint.Text = "Coordinating…";
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
            SosHint.Text = "Click for emergency";
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
                ? $"Signed by {waiver.Signature} — CPR-rated robots may start compressions " +
                  "automatically and operate a fully-automatic AED. A shock still only " +
                  "follows the AED's own rhythm analysis."
                : "Unlock automatic operation: CPR that starts on detection, and a " +
                  "fully-automatic AED that shocks on its own analysis after the robot " +
                  "verifies everyone is clear. Until signed, every start needs an " +
                  "on-scene confirmation and no shock is ever delivered.";

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
            else if (r.Spoken is { Length: > 0 })
                line = "🔊 " + string.Join(" → ", r.Spoken);
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
            "Confirm the person is unresponsive and not breathing normally. " +
            "The robot never starts on its own judgement — and never delivers " +
            "a shock; the AED analyzes, a human presses.";
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
            RobotCmdResult.Text = "Waiver signed — automatic resuscitation pre-authorized.";
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
            RobotCmdResult.Text = "Waiver revoked — confirm-gated operation restored.";
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
            IssueButton.Content = "Rotate QR";
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
            IssueButton.Content = "Issue Medical ID";
        }
        catch (Exception ex)
        {
            MedError.Text = ex.Message;
            MedError.Visibility = Visibility.Visible;
        }
    }

    private static string Cap(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..];
}
