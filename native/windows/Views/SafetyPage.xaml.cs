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
    public record RobotRow(string Name, string Status, string Directive);

    private RobotSpec[] _catalog = Array.Empty<RobotSpec>();
    private bool _loading;   // suppress SelectionChanged while populating

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
            var robots = await ApiClient.Shared.Robots(s.Uid!, s.Token!);
            RobotsList.ItemsSource = robots.Select(r => new RobotRow(
                r.Name, Cap(r.Status ?? "docked"),
                r.EscalationDirective is { } d
                    ? $"On escalation: {d.Replace('_', ' ')}" : "")).ToList();
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
