using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

/// Vault Custody: the user's sealed tandem exchanges, with PDI's audit-chain
/// status; selecting a record reads its provenance trail through JIM.
public sealed partial class CustodyPage : Page
{
    public CustodyPage()
    {
        InitializeComponent();
        Title.Text = L10n.T("cust");
        Sub.Text = L10n.T("cust.sub");
        EmptyNote.Text = L10n.T("cust.none");
        RefreshButton.Content = L10n.T("cust.refresh");
        BreaksHead.Text = L10n.T("cust.breaks");
        ProblemsYes.Content = L10n.T("ns.pr.send");
        ProblemsNo.Content = L10n.T("ns.pr.dont");
        ProblemsSwitch.Header = L10n.T("ns.pr.toggle");
        ProblemsPreviewButton.Content = L10n.T("ns.pr.show");
        TakeItHead.Text = L10n.T("hld.take");
        TakeItPitch.Text = L10n.T("hld.take.pitch");
        TakeItButton.Content = L10n.T("hld.take.go");
        EndItHead.Text = L10n.T("hld.end");
        EndItPitch.Text = L10n.T("hld.end.pitch");
        EndItBox.PlaceholderText = L10n.T("hld.end.ph");
        EndItButton.Content = L10n.T("hld.end.go");

        // The card reads three stored choices, so it has to be told when
        // the page appears rather than only when a button is pressed.
        Loaded += (_, _) => RefreshProblemsCard();
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        base.OnNavigatedTo(e);
        await Load();
    }

    private async void OnRefresh(object sender, RoutedEventArgs e) => await Load();

    /// The posture the deployment can show an auditor. Its own try/catch:
    /// a vault that cannot answer must not blank the offline card, which is
    /// about a different question entirely.
    private async Task LoadOfflinePosture()
    {
        try
        {
            var p = await ApiClient.Shared.OfflineStatus();
            OfflineTitle.Text = L10n.T("offline.title");
            OfflineState.Text = p.Offline ? L10n.T("offline.on") : L10n.T("offline.off");
            OfflineLocal.Text = p.LocalDestinationsAllowed;
            OfflineGuarantees.Text = string.Join("\n", Array.ConvertAll(
                p.Guarantees ?? Array.Empty<string>(), g => "\u2022 " + g));
            OfflineCard.Visibility = Visibility.Visible;
        }
        catch (Exception)
        {
            OfflineCard.Visibility = Visibility.Collapsed;
        }
    }

    private async Task Load()
    {
        await LoadOfflinePosture();
        var s = AppState.Current;
        try
        {
            var c = await ApiClient.Shared.Custody(s.Uid!, s.Token!);
            ChainText.Text = c.ChainIntact == true
                ? "🔗 Audit chain intact"
                : "⚠️ Audit chain status unknown";
            ChainText.Visibility = Visibility.Visible;
            RecordsList.ItemsSource = c.Records;
            EmptyNote.Visibility = c.Records.Length == 0
                ? Visibility.Visible : Visibility.Collapsed;
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;   // e.g. "no PDI vault configured"
            ErrorText.Visibility = Visibility.Visible;
            ChainText.Visibility = Visibility.Collapsed;
            EmptyNote.Visibility = Visibility.Collapsed;
        }
    }

    private async void OnSelect(object sender, SelectionChangedEventArgs e)
    {
        if (RecordsList.SelectedItem is not string key) return;
        var s = AppState.Current;
        try
        {
            var p = await ApiClient.Shared.CustodyProvenance(s.Uid!, s.Token!, key);
            ProvTitle.Text = $"🔒 {key}";
            var lines = new List<string> { $"Origin: {p.Origin}" };
            if (p.Sealed?.Cipher is { } cipher) lines.Add($"Seal: {cipher}");
            if (p.Audit is { } audit) lines.Add($"Audit events: {audit.Count}");
            lines.Add(p.Chain?.Intact == true
                ? "Hash chain: intact" : "Hash chain: unknown");
            ProvText.Text = string.Join("\n", lines);
            ProvCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
    }

    // ---- When something breaks ------------------------------------------
    //
    // The notice that has to be answered before anything leaves this machine.
    // The sending half landed last round and answered AwaitingNotice on every
    // launch because there was no surface to answer it on — safe to be wrong
    // in that direction, and still wrong: a mechanism nobody can reach is a
    // mechanism nobody chose.
    //
    // The preview is built by Problems.Report, the same call the sender posts,
    // so what is on screen is the payload rather than a description of it. A
    // preview that could drift from the message would be worse than none,
    // because it would look like a promise.

    private void RefreshProblemsCard()
    {
        var hasCollector = Problems.CollectorUrl().Length > 0;
        var answered = Problems.NoticeAnswered();

        if (!hasCollector)
        {
            // Not a failure and not a thing to hide: this build has no address
            // compiled in, so there is nothing to consent to.
            ProblemsExplain.Text = L10n.T("prb.nowhere");
            ProblemsAsk.Visibility = Visibility.Collapsed;
            ProblemsSwitch.Visibility = Visibility.Collapsed;
            return;
        }
        if (!answered)
        {
            ProblemsExplain.Text = L10n.T("prb.can");
            ProblemsAsk.Visibility = Visibility.Visible;
            ProblemsSwitch.Visibility = Visibility.Collapsed;
            return;
        }
        ProblemsExplain.Text = L10n.T("prb.never");
        ProblemsAsk.Visibility = Visibility.Collapsed;
        ProblemsSwitch.Visibility = Visibility.Visible;
        ProblemsSwitch.IsOn = Problems.SendingEnabled();
    }

    private async void OnProblemsYes(object sender, RoutedEventArgs e)
    {
        Problems.AnswerNotice(true);
        RefreshProblemsCard();
        // The first moment a send is permitted. Doing it now rather than at
        // the next launch means the person who just agreed watches the buffer
        // drain, instead of being told something happened later.
        await Problems.Send();
    }

    private void OnProblemsNo(object sender, RoutedEventArgs e)
    {
        Problems.AnswerNotice(false);
        RefreshProblemsCard();
    }

    private void OnProblemsToggled(object sender, RoutedEventArgs e) =>
        Problems.SetSending(ProblemsSwitch.IsOn);

    private void OnProblemsPreview(object sender, RoutedEventArgs e)
    {
        if (ProblemsPreview.Visibility == Visibility.Visible)
        {
            ProblemsPreview.Visibility = Visibility.Collapsed;
            ProblemsPreviewButton.Content = L10n.T("ns.pr.show");
            return;
        }
        var owed = Problems.Report()["problems"]
            as List<Dictionary<string, object>> ?? new();
        ProblemsPreview.Text = owed.Count == 0
            ? "Nothing is owed. Either nothing has failed, or everything that "
              + "has was already reported."
            : string.Join("\n", owed.Select(r =>
                $"{r["op"]} → {r["status"]}  ×{r["count"]}  {r["day"]}"));
        ProblemsPreview.Visibility = Visibility.Visible;
        ProblemsPreviewButton.Content = L10n.T("ns.pr.hide");
    }

    private async void OnTakeItWithYou(object sender, RoutedEventArgs e)
    {
        var st = AppState.Current;
        if (st.Uid is null || st.Token is null) return;
        try
        {
            var all = await ApiClient.Shared.ExportEverything(st.Uid, st.Token);
            var rows = 0;
            foreach (var t in all.Tables.Values) rows += t.Count;
            TakeItButton.Content = L10n.T("hld.take.held")
                .Replace("{t}", all.Tables.Count.ToString())
                .Replace("{r}", rows.ToString());
        }
        catch (Exception ex) { TakeItButton.Content = ex.Message; }
    }

    // The exit, beside the portability door on purpose: *take it* and *end
    // it* are the two halves of the same claim, and this shell carried only
    // the first one.
    private void OnEndItTyped(object sender, TextChangedEventArgs e) =>
        EndItButton.IsEnabled = EndItBox.Text == "erase";

    private async void OnEndIt(object sender, RoutedEventArgs e)
    {
        var st = AppState.Current;
        if (st.Uid is null || st.Token is null) return;
        try
        {
            await ApiClient.Shared.EraseEverything(st.Uid, st.Token);
            EndItButton.Content = L10n.T("hld.end.gone");
            EndItButton.IsEnabled = false;
            st.SignOut();
        }
        catch (Exception ex) { EndItButton.Content = ex.Message; }
    }
}
