using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

public sealed partial class MonitorPage : Page
{
    public sealed class LiveOptionVm
    {
        public string Who { get; init; } = "";
        public string Channel { get; init; } = "";
        public string Note { get; init; } = "";
    }

    public MonitorPage()
    {
        InitializeComponent();
        Title.Text = L10n.T("mon");
        Sub.Text = L10n.T("mon.sub");
        HeartRate.Header = L10n.T("mon.hr");
        Stress.Header = L10n.T("mon.stress");
        SendButton.Content = L10n.T("mon.send");
        FollowupNote.PlaceholderText = L10n.T("mon.add");
        HelpedButton.Content = L10n.T("mon.helped");
        DidNotButton.Content = L10n.T("mon.didnot");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e) =>
        await LoadFollowups();

    // MARK: [0039] — the effectiveness loop

    /// <summary>
    /// Ask about guidance that is still waiting on an answer, whether it went
    /// out in this session or an earlier one — a question the app drops is a
    /// question nobody ever answers.
    /// </summary>
    private async System.Threading.Tasks.Task LoadFollowups()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var state = await ApiClient.Shared.Followups(s.Uid, s.Token);
            var open = state.Open.FirstOrDefault();
            if (open is null)
            {
                FollowupCard.Visibility = Visibility.Collapsed;
                return;
            }
            FollowupQuestion.Text = open.Question;
            FollowupAbout.Text = $"About the guidance for {open.Condition}.";
            FollowupCard.Visibility = Visibility.Visible;
        }
        catch (Exception) { FollowupCard.Visibility = Visibility.Collapsed; }
    }

    private async void OnFollowupHelped(object sender, RoutedEventArgs e) =>
        await Answer(true);

    private async void OnFollowupDidNot(object sender, RoutedEventArgs e) =>
        await Answer(false);

    /// "It did not" is not a complaint filed away: the ladder runs again and the
    /// people who can help are named.
    private async System.Threading.Tasks.Task Answer(bool helped)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var a = await ApiClient.Shared.AnswerFollowup(
                s.Uid, s.Token, helped, FollowupNote.Text);
            FollowupNote.Text = "";

            AnsweredTitle.Text = a.Helped == true
                ? "Monitoring resumes" : "Bringing in a person";
            AnsweredTitle.Foreground = new SolidColorBrush(a.Helped == true
                ? Microsoft.UI.Colors.MediumSpringGreen
                : Microsoft.UI.Colors.Orange);
            AnsweredNext.Text = a.Next ?? a.Reason ?? "";

            LiveOptions.ItemsSource = (a.Live?.Options ?? Array.Empty<LiveOption>())
                .Select(o => new LiveOptionVm
                {
                    Who = string.IsNullOrEmpty(o.Name)
                        ? o.Kind.Replace('_', ' ') : o.Name!,
                    Channel = o.Channel ?? "",
                    Note = o.Note ?? "",
                }).ToList();
            LiveNote.Text = a.Live?.Note ?? "";
            AnsweredCard.Visibility = Visibility.Visible;

            await LoadFollowups();
        }
        catch (Exception) { /* the send path already surfaces errors */ }
    }

    private async void OnSend(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        SendButton.IsEnabled = false;
        try
        {
            var r = await ApiClient.Shared.Monitor(s.Uid!, s.Token!,
                (int)HeartRate.Value, Stress.Value / 100.0);

            ResultTitle.Text = r.Detected
                ? Cap(r.Condition ?? "Detected")
                : "All clear";
            ResultTitle.Foreground = new SolidColorBrush(
                r.Detected ? Microsoft.UI.Colors.OrangeRed : Microsoft.UI.Colors.MediumSpringGreen);

            ResultReason.Text = r.Reason ?? "";
            ResultReason.Visibility = string.IsNullOrEmpty(r.Reason) ? Visibility.Collapsed : Visibility.Visible;

            ResultGuidance.Text = r.Guidance?.Content ?? "";
            ResultGuidance.Visibility = r.Guidance is null ? Visibility.Collapsed : Visibility.Visible;

            ResultSpecialist.Text = FormatSpecialist(r.Guidance);
            ResultSpecialist.Visibility = ResultSpecialist.Text.Length > 0
                ? Visibility.Visible : Visibility.Collapsed;

            var aid = r.Guidance?.FirstAidPlaybook;
            if (aid is not null)
            {
                var header = $"First aid — {aid.Kind.ToUpper()}" +
                             (aid.CallEmergencyServices == true
                                  ? "  ·  📞 call emergency services now" : "");
                var steps = string.Join("\n", aid.Steps.Select(
                    (step, i) => $"{i + 1}. {step}"));
                ResultFirstAid.Text = $"{header}\n{steps}";
                ResultFirstAid.Visibility = Visibility.Visible;
                if (aid.Pace is { } pace)
                {
                    ResultPace.Text =
                        $"Pace: {pace.CompressionsPerMinute}/min · " +
                        $"{pace.CompressionToBreathRatio}" +
                        (pace.Cue is { } cue
                             ? $"\n💡 {cue.Light}\n🔊 {cue.Audio}" : "");
                    ResultPace.Visibility = Visibility.Visible;
                }
                else ResultPace.Visibility = Visibility.Collapsed;
            }
            else
            {
                ResultFirstAid.Visibility = Visibility.Collapsed;
                ResultPace.Visibility = Visibility.Collapsed;
            }

            var refs = r.Guidance?.References;
            if (refs is { Length: > 0 })
            {
                ResultRefs.Text = string.Join("\n", refs.Select(x => $"→ {x}"));
                ResultRefs.Visibility = Visibility.Visible;
            }
            else ResultRefs.Visibility = Visibility.Collapsed;

            ResultProvenance.Text = FormatProvenance(r.Guidance);
            ResultProvenance.Visibility = ResultProvenance.Text.Length > 0
                ? Visibility.Visible : Visibility.Collapsed;

            ResultCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ResultTitle.Text = L10n.T("mon.error");
            ResultReason.Text = ex.Message;
            ResultReason.Visibility = Visibility.Visible;
            ResultGuidance.Visibility = Visibility.Collapsed;
            ResultCard.Visibility = Visibility.Visible;
        }
        finally
        {
            SendButton.IsEnabled = true;
        }
    }

    /// The named expert standing behind this condition, plus a live badge
    /// when guidance was routed in tandem through a QRME synthetic persona.
    internal static string FormatSpecialist(Guidance? g)
    {
        if (g?.Specialist is not { } who) return "";
        return g.Source == "tandem" ? $"{who}  ·  LIVE VIA QRME" : who;
    }

    /// The verifiable basis of the advice: publishers, documents, URLs, and
    /// how/by what the text was produced — shared by Monitor and Coach.
    internal static string FormatProvenance(Guidance? g)
    {
        if (g is null) return "";
        var lines = new System.Collections.Generic.List<string>();
        if (g.TranslationNote is { } tn) lines.Add($"🌐 {tn}");
        if (g.ProvenanceInfo is { } p)
        {
            lines.Add("Derived from:");
            foreach (var e in p.EvidenceList)
            {
                lines.Add($"  {e.Publisher} — {e.Title}" +
                          (e.Supports is { } sup ? $" (supports: {sup})" : ""));
                lines.Add($"  {e.Url}");
            }
            lines.Add($"{p.Method} · generated by {p.GeneratedBy}");
            lines.Add(p.Disclaimer);
        }
        if (g.CustodyInfo is { } c)
            lines.Add(c.Vaulted && c.PdiKey is { } key
                ? $"🔒 Sealed in the PDI vault — {key}"
                : $"⚠️ {c.Note}");
        return string.Join("\n", lines);
    }

    private static string Cap(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..];
}
