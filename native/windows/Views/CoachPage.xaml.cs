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
    private static readonly string[] Conditions =
        { "anxiety", "depression", "stress", "phobia", "financial_stress",
          "relationship", "physical_distress", "physical_injury" };

    public CoachPage()
    {
        InitializeComponent();
        MessageBox.PlaceholderText = L10n.T("ov.fb.placeholder");
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
        var area = (AreaBox.SelectedItem as ComboBoxItem)?.Content as string ?? "mental_health";

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
        var area = (AreaBox.SelectedItem as ComboBoxItem)?.Content as string
                   ?? "mental_health";
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
