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
        VeilLogHead.Text = L10n.T("hld.log");
        VeilVaulted.Text = L10n.T("hld.log.vaulted");
        VeilWhereHead.Text = L10n.T("hld.where");
        VeilCloudHead.Text = L10n.T("set.cloud");
        VeilStopButton.Content = L10n.T("set.cloud.stop");
        VeilPagesHead.Text = L10n.T("sfy.pages");
        VeilPagesPitch.Text = L10n.T("sfy.pages.pitch");
        VeilPagesNone.Text = L10n.T("sfy.pages.none");
        VeilHistoryHead.Text = L10n.T("sfy.history");
        VeilHistoryNone.Text = L10n.T("sfy.history.none");
        VeilLocHead.Text = L10n.T("set.loc");
        VeilLocPitch.Text = L10n.T("set.loc.pitch");
        VeilLocBox.PlaceholderText = L10n.T("set.loc.ph");
        VeilLocSave.Content = L10n.T("set.save");
        VeilPlanHead.Text = L10n.T("hld.plan");
        VeilPlanCancel.Content = L10n.T("hld.plan.cancel");
        ProblemsSwitch.Header = L10n.T("ns.pr.toggle");
        ProblemsPreviewButton.Content = L10n.T("ns.pr.show");
        ProblemsServerTitle.Text = L10n.T("prob.server");
        ProblemsKeyBox.PlaceholderText = L10n.T("prob.key.ph");
        ProblemsFetchButton.Content = L10n.T("prob.fetch");
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
        await LoadVeil();
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
                ? L10n.T("cust.chain.ok")
                : L10n.T("cust.chain.unknown");
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
            var lines = new List<string>
            {
                L10n.T("cst.origin").Replace("{x}", p.Origin),
            };
            if (p.Sealed?.Cipher is { } cipher)
                lines.Add(L10n.T("cst.seal").Replace("{x}", cipher));
            if (p.Audit is { } audit)
                lines.Add(L10n.T("cust.events").Replace("{n}", $"{audit.Count}"));
            lines.Add(p.Chain?.Intact == true
                ? L10n.T("cust.chain.ok") : L10n.T("cust.chain.unknown"));
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


    // The other end of the wire: what has reached this deployment's own
    // backend, from every client of it. Reading needs the problems key (or a
    // caller on the backend's machine); a refusal is rendered verbatim.
    private async void OnProblemsFetch(object sender, RoutedEventArgs e)
    {
        try
        {
            var r = await ApiClient.Shared.ProblemRows(ProblemsKeyBox.Password);
            ProblemsServerRows.Text = r.Rows.Length == 0
                ? L10n.T("prob.none")
                : string.Join("\n", r.Rows.Select(row =>
                    $"{row.Op}  {row.StatusCode}  ×{row.Count}  " +
                    $"{row.Source} {row.AppVersion} · {row.Platform} · {row.Day}"));
        }
        catch (Exception ex) { ProblemsServerRows.Text = ex.Message; }
        ProblemsServerRows.Visibility = Visibility.Visible;
    }

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

    // ---- the record and the veil ----

    private static TextBlock VeilLine(string text, string brush) => new()
    {
        Text = text,
        FontSize = 11,
        TextWrapping = TextWrapping.Wrap,
        Foreground = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources[brush],
    };

    private async System.Threading.Tasks.Task LoadVeil()
    {
        var s = AppState.Current;
        try
        {
            var cloud = await ApiClient.Shared.CloudStatus();
            VeilCloudLine.Text = L10n.T("hld.where.cloud")
                .Replace("{model}", cloud.Model ?? "none")
                .Replace("{fallback}", cloud.Fallback);
            VeilCloudNote.Text = cloud.Contribution;
        }
        catch { /* backend offline */ }
        try
        {
            VeilPlans.Children.Clear();
            foreach (var plan in (await ApiClient.Shared.Plans()).Plans)
            {
                var join = new Button
                {
                    Content = $"{plan.Title} · ${(int)plan.PriceUsd}",
                    FontSize = 12,
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                        Microsoft.UI.Colors.Transparent),
                };
                var name = plan.Plan;
                join.Click += async (_, _) => await Join(name);
                VeilPlans.Children.Add(join);
            }
        }
        catch { /* leave as-is */ }
        await RenderMembership(null);
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var log = await ApiClient.Shared.AccessLog(s.Uid, s.Token);
            VeilVaulted.Visibility = log.Vaulted
                ? Visibility.Visible : Visibility.Collapsed;
            VeilLogEntries.Children.Clear();
            if (log.RecordKept)
            {
                VeilLogState.Text = L10n.T("hld.log.kept");
                foreach (var entry in log.Entries.Take(5))
                    VeilLogEntries.Children.Add(VeilLine(
                        $"{entry.Action ?? ""} · {entry.At ?? ""}", "JimT3Brush"));
            }
            else VeilLogState.Text = L10n.T("hld.log.empty");
            VeilLogNote.Text = log.Note;
        }
        catch { /* leave as-is */ }
        try
        {
            var contribution = await ApiClient.Shared.CloudContribution(
                s.Uid, s.Token);
            VeilPolicy.Text = contribution.Policy;
            VeilStopButton.Visibility = contribution.OptedIn
                ? Visibility.Visible : Visibility.Collapsed;
        }
        catch { /* leave as-is */ }
        try
        {
            var pages = await ApiClient.Shared.Pages(s.Uid, s.Token);
            VeilPages.Children.Clear();
            VeilPagesNone.Visibility = pages.Length == 0
                ? Visibility.Visible : Visibility.Collapsed;
            foreach (var page in pages.Take(5))
                VeilPages.Children.Add(VeilLine(
                    $"{page.To ?? ""} · {page.SentAt ?? ""}",
                    page.Delivered == true ? "JimGreenBrush" : "JimT2Brush"));
        }
        catch { /* leave as-is */ }
        try
        {
            var incidents = await ApiClient.Shared.Incidents(s.Uid, s.Token);
            VeilIncidents.Children.Clear();
            VeilHistoryNone.Visibility = incidents.Length == 0
                ? Visibility.Visible : Visibility.Collapsed;
            foreach (var incident in incidents.Take(5))
                VeilIncidents.Children.Add(VeilLine(
                    $"{incident.Kind ?? ""} · {incident.At ?? ""}",
                    "JimAmberBrush"));
        }
        catch { /* leave as-is */ }
    }

    private async void OnStopContributing(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var revoked = await ApiClient.Shared.RevokeCloudContribution(
                s.Uid, s.Token);
            VeilRevoked.Text = revoked.Note;
            VeilRevoked.Visibility = Visibility.Visible;
            VeilStopButton.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex)
        {
            VeilError.Text = ex.Message;
            VeilError.Visibility = Visibility.Visible;
        }
    }

    private async void OnSaveLocality(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var saved = await ApiClient.Shared.SetLocality(
                s.Uid, s.Token, VeilLocBox.Text.Trim());
            VeilLocSaved.Text = saved.Locality ?? "";
            VeilLocSaved.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            VeilError.Text = ex.Message;
            VeilError.Visibility = Visibility.Visible;
        }
    }

    // ---- the membership: the plan the refusals name ----

    private async System.Threading.Tasks.Task RenderMembership(
        MembershipView? known)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var current = known
                ?? await ApiClient.Shared.Membership(s.Uid, s.Token);
            VeilPlanCurrent.Text = $"{current.Title} · ${(int)current.PriceUsd}";
            VeilPlanCurrent.Visibility = Visibility.Visible;
            VeilPlanMeans.Text = current.Storage.Means;
            VeilPlanMeans.Visibility = Visibility.Visible;
            VeilPlanReaders.Text = L10n.T("hld.plan.canread")
                .Replace("{list}", string.Join(", ",
                                               current.Storage.WhoCanRead));
            VeilPlanReaders.Visibility = Visibility.Visible;
        }
        catch { /* leave as-is */ }
    }

    /// Billing is simulated and the server's own sheet says so.
    private async System.Threading.Tasks.Task Join(string plan)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var current = await ApiClient.Shared.Subscribe(s.Uid, s.Token,
                                                           plan);
            await RenderMembership(current);
        }
        catch (Exception ex)
        {
            VeilError.Text = ex.Message;
            VeilError.Visibility = Visibility.Visible;
        }
    }

    /// The person keeps their record and every emergency path.
    private async void OnCancelMembership(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var current = await ApiClient.Shared.CancelMembership(s.Uid,
                                                                  s.Token);
            await RenderMembership(current);
        }
        catch (Exception ex)
        {
            VeilError.Text = ex.Message;
            VeilError.Visibility = Visibility.Visible;
        }
    }
}
