using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

public sealed partial class CoachPage : Page
{
    // The wire tone is the key's own last segment — no second spelling of
    // a word the table already carries.
    private static readonly string[] ToneKeys =
        { "brg.speak.direct", "brg.speak.balanced", "brg.speak.cautious" };
    // The wire word is the tag; the shown label derives from it the same
    // way the iOS and Android pickers spell it — never a second English.
    private static readonly string[] Areas =
        { "mental_health", "health_fitness", "career", "finance",
          "relationships", "personal_growth" };
    private static readonly string[] Conditions =
        { "anxiety", "depression", "stress", "phobia", "financial_stress",
          "relationship", "physical_distress", "physical_injury" };

    public CoachPage()
    {
        InitializeComponent();
        CoachTitle.Text = L10n.T("coach.title");
        CoachPitch.Text = L10n.T("coach.pitch");
        AreaBox.Header = L10n.T("coach.area");
        AreaBox.ItemsSource = Areas.Select(a => a.Replace('_', ' ')).ToList();
        MessageBox.Header = L10n.T("coach.msg");
        MessageBox.PlaceholderText = L10n.T("coach.msg.ph");
        AskButton.Content = L10n.T("coach.ask");
        ReplyHead.Text = L10n.T("tab.coach");
        // In code rather than XAML: a XAML literal cannot be re-read when the
        // language changes.
        AskSpecialistButton.Content = L10n.T("spec.ask");
        ToneHead.Text = L10n.T("brg.speak.tone");
        ToneBox.ItemsSource = ToneKeys.Select(k => L10n.T(k)).ToList();
        ToneGoButton.Content = L10n.T("brg.speak.go");
        ToldHead.Text = L10n.T("brg.told");
        ConditionBox.ItemsSource = Conditions.ToList();
        ConditionNote.PlaceholderText = L10n.T("brg.told.note.ph");
        TellButton.Content = L10n.T("brg.told.tell");
        ContextSource.PlaceholderText = L10n.T("brg.told.src.ph");
        ContextButton.Content = L10n.T("brg.told.ctx");
        SayButton.Content = L10n.T("brg.told.say");
        TellUsHead.Text = L10n.T("brg.tell");
        GoodButton.Content = L10n.T("brg.tell.good");
        BadButton.Content = L10n.T("brg.tell.bad");
        MadeHead.Text = L10n.T("brg.made");
        KnowsHead.Text = L10n.T("cch.knows");
        StudyHead.Text = L10n.T("cch.study.head");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var report = await ApiClient.Shared.ProgressReport(s.Uid, s.Token);
            // Insights are a Pro capability; a plan refusal reads as none yet.
            InsightRow[] insights;
            try { insights = await ApiClient.Shared.Insights(s.Uid, s.Token); }
            catch { insights = Array.Empty<InsightRow>(); }
            EventRow[] events;
            try { events = await ApiClient.Shared.Events(s.Uid, s.Token); }
            catch { events = Array.Empty<EventRow>(); }
            CalmHistoryRow[] calm;
            try { calm = await ApiClient.Shared.CalmHistory(s.Uid, s.Token); }
            catch { calm = Array.Empty<CalmHistoryRow>(); }
            CoachExchange[] exchanges;
            try { exchanges = await ApiClient.Shared.CoachHistory(s.Uid, s.Token); }
            catch { exchanges = Array.Empty<CoachExchange>(); }
            MadeStats.Text = L10n.T("brg.made.stats")
                .Replace("{c}", report.Checkins.Count.ToString())
                .Replace("{m}", report.Checkins.AvgMood?.ToString("0.0") ?? "—")
                .Replace("{i}", insights.Length.ToString())
                .Replace("{e}", events.Length.ToString())
                .Replace("{s}", calm.Length.ToString())
                .Replace("{x}", exchanges.Length.ToString());
            MadeStats.Visibility = Visibility.Visible;
            InsightLines.Children.Clear();
            foreach (var row in insights.Take(3))
                InsightLines.Children.Add(new TextBlock
                {
                    Text = row.Message, FontSize = 11,
                    TextWrapping = TextWrapping.Wrap,
                    Foreground = (Microsoft.UI.Xaml.Media.Brush)
                        Application.Current.Resources["JimT3Brush"],
                });
        }
        catch { /* backend offline */ }
        await LoadKnows();
    }

    /// The offline coach's store and JIM's syllabus for it
    /// (jim/pipeline.py) — and the one-press study that imports the
    /// findings into the store.
    private async System.Threading.Tasks.Task LoadKnows()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var knows = await ApiClient.Shared.CoachStore(s.Uid!, s.Token!);
            var syllabus = await ApiClient.Shared.CoachCurriculum(s.Uid!, s.Token!);
            KnowsCounts.Text =
                $"{knows.Pack} · +{knows.Excursions.Length} · +{knows.Deposits.Length}";
            StudyPanel.Children.Clear();
            foreach (var sug in syllabus.Suggested)
            {
                var row = new StackPanel { Spacing = 2 };
                row.Children.Add(new TextBlock
                {
                    Text = sug.Topic, FontSize = 13, TextWrapping = TextWrapping.Wrap,
                    Foreground = (Microsoft.UI.Xaml.Media.Brush)
                        Application.Current.Resources["JimTxtBrush"],
                });
                row.Children.Add(new TextBlock
                {
                    Text = sug.Why, FontSize = 11, TextWrapping = TextWrapping.Wrap,
                    Foreground = (Microsoft.UI.Xaml.Media.Brush)
                        Application.Current.Resources["JimT2Brush"],
                });
                var go = new Button
                {
                    Content = L10n.T("cch.study.go"),
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                        Microsoft.UI.Colors.Transparent),
                    Foreground = (Microsoft.UI.Xaml.Media.Brush)
                        Application.Current.Resources["JimBrandABrush"],
                    FontSize = 12,
                };
                var topic = sug.Topic; var area = sug.Area;
                go.Click += async (_, _) =>
                {
                    go.IsEnabled = false;
                    try
                    {
                        var r = await ApiClient.Shared.CoachStudy(
                            s.Uid!, s.Token!, topic, area);
                        var done = L10n.T("cch.study.done");
                        StudiedNote.Text = $"✓ {r.Studied} — {done}";
                        StudiedNote.Visibility = Visibility.Visible;
                        await LoadKnows();
                    }
                    catch (Exception ex) { ShowError(ex.Message); }
                    finally { go.IsEnabled = true; }
                };
                row.Children.Add(go);
                StudyPanel.Children.Add(row);
            }
            StudyHead.Visibility = syllabus.Suggested.Length > 0
                ? Visibility.Visible : Visibility.Collapsed;
            KnowsCard.Visibility = Visibility.Visible;
        }
        catch { /* the ask card stands on its own */ }
    }

    private async void OnSetTone(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var key = ToneKeys[ToneBox.SelectedIndex >= 0 ? ToneBox.SelectedIndex : 1];
        var tone = key[(key.LastIndexOf('.') + 1)..];
        try { await ApiClient.Shared.SetPersonality(s.Uid, s.Token, tone); }
        catch (Exception ex) { ShowBearingError(ex.Message); }
    }

    private async void OnTellCondition(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var condition = ConditionBox.SelectedIndex >= 0
            ? Conditions[ConditionBox.SelectedIndex] : "anxiety";
        try
        {
            var known = await ApiClient.Shared.DeclareCondition(
                s.Uid, s.Token, condition, ConditionNote.Text.Trim());
            ConditionNote.Text = "";
            KnownLine.Text = string.Join(" · ", known.KnownConditions);
            KnownLine.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowBearingError(ex.Message); }
    }

    // The server checks the consent, not this shell — a refusal is shown
    // in the server's words.
    private async void OnGiveContext(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var source = ContextSource.Text.Trim();
        if (source.Length == 0) return;
        RefusedLine.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.GiveContext(s.Uid, s.Token, source, "event");
        }
        catch (Exception ex)
        {
            RefusedLine.Text = L10n.T("brg.told.refused")
                .Replace("{err}", ex.Message);
            RefusedLine.Visibility = Visibility.Visible;
        }
    }

    private async void OnSaySomething(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var said = await ApiClient.Shared.CompanionCheckin(s.Uid, s.Token);
            SaidLine.Text = said.Content;
            SaidLine.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowBearingError(ex.Message); }
    }

    private async void OnRateGood(object sender, RoutedEventArgs e) =>
        await Rate("up");

    private async void OnRateBad(object sender, RoutedEventArgs e) =>
        await Rate("down");

    private async System.Threading.Tasks.Task Rate(string rating)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try { await ApiClient.Shared.SendGuidanceFeedback(s.Uid, s.Token, rating); }
        catch (Exception ex) { ShowBearingError(ex.Message); }
    }

    private void ShowBearingError(string message)
    {
        BearingError.Text = message;
        BearingError.Visibility = Visibility.Visible;
    }

    private async void OnAsk(object sender, RoutedEventArgs e)
    {
        var message = MessageBox.Text.Trim();
        if (message.Length == 0) { ShowError("Type a message to your coach."); return; }
        var area = Areas[AreaBox.SelectedIndex >= 0 ? AreaBox.SelectedIndex : 0];

        var s = AppState.Current;
        AskButton.IsEnabled = false;
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            var reply = await ApiClient.Shared.Coach(s.Uid!, s.Token!, area, message);
            ReplyText.Text = reply.Content;
            var who = MonitorPage.FormatSpecialist(reply);
            var prov = MonitorPage.FormatProvenance(reply);
            ReplyProvenance.Text = who.Length > 0 && prov.Length > 0
                ? $"{who}\n{prov}" : who + prov;
            ReplyProvenance.Visibility = ReplyProvenance.Text.Length > 0
                ? Visibility.Visible : Visibility.Collapsed;
            ReplyCard.Visibility = Visibility.Visible;
            SpecialistCard.Visibility = Visibility.Collapsed;

            var offer = reply.SpecialistOffer;
            if (offer is not null && offer.Available)
            {
                OfferLabel.Text = offer.Label;
                OfferNote.Text = offer.Note;
                OfferPanel.Visibility = Visibility.Visible;
            }
            else { OfferPanel.Visibility = Visibility.Collapsed; }
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { AskButton.IsEnabled = true; }
    }

    /// The door the person chooses. Nothing crosses the tandem until this is
    /// pressed, because what crosses is what they wrote.
    private async void OnAskSpecialist(object sender, RoutedEventArgs e)
    {
        var message = MessageBox.Text.Trim();
        if (message.Length == 0) return;
        var area = Areas[AreaBox.SelectedIndex >= 0 ? AreaBox.SelectedIndex : 0];
        var s = AppState.Current;
        AskSpecialistButton.IsEnabled = false;
        try
        {
            var a = await ApiClient.Shared.CoachSpecialist(
                s.Uid!, s.Token!, area, message);
            SpecialistWho.Text = (a.Specialist?.Label ?? L10n.T("spec.fallback"))
                                 + " \u00b7 " + L10n.T("spec.via");
            SpecialistText.Text = a.Delivered && a.Content is not null
                ? a.Content
                : a.HeldForOwnerApproval
                    ? L10n.T("spec.held")
                    : (a.Reason ?? "") + (a.Note is null ? "" : $" \u2014 {a.Note}");
            SpecialistProv.Text = a.Provenance is null ? ""
                : $"{a.Provenance.Method}\n{L10n.T("spec.shared")}: {a.Provenance.Shared}";
            SpecialistCard.Visibility = Visibility.Visible;
            OfferPanel.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { AskSpecialistButton.IsEnabled = true; }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
