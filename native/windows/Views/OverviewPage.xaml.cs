using System;
using System.Globalization;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using System.Collections.Generic;

namespace JimGuardian.Views;

public sealed partial class OverviewPage : Page
{
    // View-model row so the DataTemplate can bind a preformatted value.
    public record MetricRow(string Metric, string Display);
    public record ImproveRow(string Line);

    private static readonly string[] ImproveCategories =
        { "idea", "improvement", "bug", "praise", "other" };

    private ProviderInfo[] _providers = System.Array.Empty<ProviderInfo>();
    private LanguageInfo[] _languages = System.Array.Empty<LanguageInfo>();
    private bool _loadingModel;   // suppress SelectionChanged while populating
    private bool _loadingLanguage;

    public OverviewPage()
    {
        InitializeComponent();
        Localize();
        ImproveCategory.ItemsSource = ImproveCategories
            .Select(FeedbackCategory).ToList();
        ImproveCategory.SelectedIndex = 0;
        ImproveRating.ItemsSource = new[] { "—", "1", "2", "3", "4", "5" };
        ImproveRating.SelectedIndex = 0;
    }

    /// Literal keys rather than "ov.fb.cat." + the API value: a key built
    /// at runtime is a key the dead-key guard cannot see being asked for.
    private static string FeedbackCategory(string kind) => kind switch
    {
        "idea" => L10n.T("ov.fb.cat.idea"),
        "improvement" => L10n.T("ov.fb.cat.improvement"),
        "bug" => L10n.T("ov.fb.cat.bug"),
        "praise" => L10n.T("ov.fb.cat.praise"),
        _ => L10n.T("ov.fb.cat.other"),
    };

    /// XAML carries no table lookup, so every fixed string on this page is
    /// named there and filled in here. The empty-baseline line used to say
    /// *Live Monitoring* where the phones said *Monitor*; it now takes the
    /// screen's name from the nav item itself, so the two cannot drift.
    private void Localize()
    {
        WatchingChip.Text = L10n.T("ov.watching");
        WatchingSub.Text = L10n.T("ov.watching.sub");
        BaselineTitle.Text = L10n.T("ov.baseline");
        Empty.Text = L10n.T("ov.baseline.none")
            .Replace("{screen}", L10n.T("tab.monitor"));
        ModelTitle.Text = L10n.T("ov.model");
        ModelSub.Text = L10n.T("ov.model.sub");
        LanguageTitle.Text = L10n.T("ov.language");
        KeyHead.Text = L10n.T("set.key");
        KeyLead.Text = L10n.T("set.key.pitch");
        KeyBox.Header = L10n.T("set.key.label");
        KeyBox.PlaceholderText = L10n.T("set.key.ph");
        InviteHead.Text = L10n.T("set.invite");
        InviteLead.Text = L10n.T("set.invite.lead");
        InviteBox.PlaceholderText = L10n.T("set.invite");
        SaveInviteButton.Content = L10n.T("set.save");
        InviteBox.Password = AppState.Current.SignupKey;
        SaveKeyButton.Content = L10n.T("set.save");
        KeyBox.Password = AppState.Current.LlmKey;
        LanguageSub.Text = L10n.T("ov.language.sub");
        PreTranslateToggle.Header = L10n.T("ov.pretranslate");
        PreTranslateToggle.OffContent = L10n.T("ov.pretranslate.sub");
        TranslateBox.Header = L10n.T("ov.translate");
        TranslateBox.PlaceholderText = L10n.T("ov.translate.placeholder");
        TranslateButton.Content = L10n.T("ov.translate.go");
        ImproveTitle.Text = L10n.T("ov.fb");
        ImproveSub.Text = L10n.T("ov.fb.sub");
        ImproveCategory.Header = L10n.T("ov.fb.category");
        ImproveMessage.PlaceholderText = L10n.T("ov.fb.placeholder");
        ImproveRating.Header = L10n.T("ov.fb.rating");
        SendImproveButton.Content = L10n.T("ov.fb.send");
        ImproveMineHeader.Text = L10n.T("ov.fb.yours");
        AccHead.Text = L10n.T("ns.acc");
        AccLead.Text = L10n.T("ns.acc.lead");
        AccDoing.PlaceholderText = L10n.T("ns.acc.doing.ph");
        AccWall.PlaceholderText = L10n.T("ns.acc.wall.ph");
        AccHelp.PlaceholderText = L10n.T("ns.acc.help.ph");
        AccSend.Content = L10n.T("ns.acc.send");
        AccReviewerBox.PlaceholderText = L10n.T("ns.acc.token.ph");
        AccLoad.Content = L10n.T("ns.acc.load");
        AccEmpty.Text = L10n.T("ns.acc.none");
        LearnedTitle.Text = L10n.T("ov.learned");
        SealedText.Text = L10n.T("ov.sealed");
        RebuildButton.Content = L10n.T("ov.rebuild");
        FtHead.Text = L10n.T("ov.ft");
        FtSub.Text = L10n.T("ov.ft.sub");
        FtFrom.Text = L10n.T("ov.ft.none");
        FtUse.Header = L10n.T("ov.ft.use");
        FtTrainButton.Content = L10n.T("ov.ft.train");
        LoadFinetune();
        NameTitle.Text = L10n.T("ov.name");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        RefreshButton.Content = L10n.T("action.refresh");
        await Load();
    }

    private async void OnRefresh(object sender, RoutedEventArgs e) => await Load();

    // MARK: Claim 11's user-specific model, and the name

    public sealed class HelpVm
    {
        public string Condition { get; init; } = "";
        public string Tally { get; init; } = "";
    }

    public sealed class LineVm { public string Line { get; init; } = ""; }

    /// <summary>
    /// Counts off this user's own history rather than a score, plus where the
    /// profile came from: nothing was sent to a model vendor to build it.
    /// </summary>
    private async System.Threading.Tasks.Task LoadAdaptation()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try { Render(await ApiClient.Shared.Adaptation(s.Uid, s.Token)); }
        catch (Exception) { AdaptationSummary.Text = ""; }
    }

    private void Render(AdaptationProfile p)
    {
        if (!p.Built)
        {
            AdaptationSummary.Text = p.Note
                ?? "No profile yet — it is built from the history already on record.";
            AdaptationHelps.ItemsSource = null;
            AdaptationDials.Text = "";
            AdaptationMethod.Text = "";
            SealedText.Visibility = Visibility.Collapsed;
            return;
        }
        AdaptationSummary.Text = L10n.T("ov.confidence")
            .Replace("{pct}", $"{(int)Math.Round(p.Confidence * 100)}")
            .Replace("{n}", $"{p.EvidenceItems}");

        var helps = p.Profile?.WhatHelps ?? new System.Collections.Generic.Dictionary<string, HelpTally>();
        AdaptationHelps.ItemsSource = helps
            .Where(kv => kv.Value.Answered > 0)
            .OrderBy(kv => kv.Key)
            .Select(kv => new HelpVm
            {
                Condition = kv.Key.Replace('_', ' '),
                Tally = L10n.T("ov.helped")
                    .Replace("{n}", $"{kv.Value.Helped}")
                    .Replace("{total}", $"{kv.Value.Answered}"),
            }).ToList();

        var dials = new System.Collections.Generic.List<string>();
        if (p.Profile?.Tone is { Length: > 0 } tone)
            dials.Add(L10n.T("ov.tone").Replace("{tone}", tone));
        if (p.Profile?.Occupation is { Length: > 0 } job)
            dials.Add(L10n.T("ov.work").Replace("{job}", job));
        AdaptationDials.Text = string.Join(" · ", dials);
        AdaptationMethod.Text = p.Profile?.Method ?? "";
        SealedText.Visibility = p.Vaulted ? Visibility.Visible : Visibility.Collapsed;
    }

    /// <summary>The offline fine-tune. A 404 before anything is trained is
    /// the normal state, not an error worth showing.</summary>
    private async void LoadFinetune()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try { RenderFinetune(await ApiClient.Shared.Finetune(s.Uid, s.Token)); }
        catch { /* nothing trained yet */ }
    }

    private void RenderFinetune(Finetune f)
    {
        _ft = f;
        FtFrom.Text = L10n.T("ov.ft.from").Replace("{n}", f.Examples.ToString());
        // The server's own sentence, shown rather than paraphrased: it is the
        // line that says whether weights or a prompt came out of this.
        FtMethod.Text = f.Method;
        FtUse.Visibility = Visibility.Visible;
        FtUse.IsOn = f.Active ?? false;
        FtOff.Text = L10n.T("ov.ft.off");
    }

    private async void OnTrainModel(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        FtTrainButton.IsEnabled = false;
        FtTrainButton.Content = L10n.T("ov.ft.training");
        try { RenderFinetune(await ApiClient.Shared.RunFinetune(s.Uid, s.Token)); }
        catch (Exception ex) { FtMethod.Text = ex.Message; }
        finally
        {
            FtTrainButton.IsEnabled = true;
            FtTrainButton.Content = L10n.T("ov.ft.train");
        }
    }

    /// <summary>Training and using are two decisions.</summary>
    private async void OnUseTrainedModel(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _ft is null) return;
        try
        {
            await ApiClient.Shared.SetFinetuneActive(s.Uid, s.Token, FtUse.IsOn);
        }
        catch (Exception ex) { FtMethod.Text = ex.Message; }
    }

    private Finetune? _ft;

    private async void OnRebuildAdaptation(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        RebuildButton.IsEnabled = false;
        try { Render(await ApiClient.Shared.RebuildAdaptation(s.Uid, s.Token)); }
        catch (Exception) { /* leave the previous reading in place */ }
        finally { RebuildButton.IsEnabled = true; }
    }

    /// <summary>The tradeoff, not a switch: what the choice keeps and costs.</summary>
    private async System.Threading.Tasks.Task LoadAnonymity()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var p = await ApiClient.Shared.Anonymity(s.Uid, s.Token);
            AnonymityKnownAs.Text = p.Anonymous
                ? L10n.T("ov.name.pseudonym").Replace("{name}",
                    p.KnownAs ?? L10n.T("ov.name.pseudonym.fallback"))
                : L10n.T("ov.name.own");
            AnonymityLines.ItemsSource =
                p.Keeps.Select(k => new LineVm { Line = "\u2713 " + k })
                 .Concat(p.Costs.Select(c => new LineVm { Line = "• " + c }))
                 .ToList();
        }
        catch (Exception) { AnonymityKnownAs.Text = ""; }
    }

    private async System.Threading.Tasks.Task Load()
    {
        var s = AppState.Current;
        Greeting.Text = L10n.T("ov.hi").Replace("{name}", s.DisplayName);
        await LoadAdaptation();
        await LoadAnonymity();
        try
        {
            var metrics = await ApiClient.Shared.Baseline(s.Uid!, s.Token!);
            MetricsList.ItemsSource = metrics.Select(m => new MetricRow(
                Cap(m.Metric),
                m.Value is { } v ? v.ToString("0", CultureInfo.InvariantCulture) : m.State ?? "—")).ToList();
            Empty.Visibility = metrics.Length == 0 ? Visibility.Visible : Visibility.Collapsed;
        }
        catch
        {
            Empty.Text = L10n.T("ov.error");
            Empty.Visibility = Visibility.Visible;
        }
        finally
        {
            Loading.IsActive = false;
            Loading.Visibility = Visibility.Collapsed;
        }
        await LoadModel();
        await LoadLanguage();
        await LoadImprovements();
    }

    private async System.Threading.Tasks.Task LoadImprovements()
    {
        try
        {
            var st = await ApiClient.Shared.Improvements(AppState.Current.Token);
            if (st.Total > 0)
            {
                var parts = ImproveCategories
                    .Where(c => st.Tally.TryGetValue(c, out var n) && n > 0)
                    .Select(c => $"{st.Tally[c]} {c}");
                ImproveTally.Text = L10n.T("fb.sofar").Replace("{list}", string.Join(" · ", parts));
                ImproveTally.Visibility = Visibility.Visible;
            }
            else ImproveTally.Visibility = Visibility.Collapsed;

            var mine = st.Mine.Select(f => new ImproveRow(
                $"[{f.Category}] {f.Message}  ·  {f.Status}")).ToList();
            ImproveMine.ItemsSource = mine;
            ImproveMineHeader.Visibility =
                mine.Count > 0 ? Visibility.Visible : Visibility.Collapsed;
        }
        catch { /* backend offline — leave empty */ }
    }

    // The accessibility door: tokenless on purpose — the person it exists
    // for may be the person the enrollment shut out.
    private async void OnSendAccessReport(object sender, RoutedEventArgs e)
    {
        var doing = AccDoing.Text.Trim();
        var wall = AccWall.Text.Trim();
        if (doing.Length == 0 || wall.Length == 0) return;
        try
        {
            await ApiClient.Shared.SendAccessReport(
                doing, wall, AccHelp.Text.Trim(), AppState.Current.Language);
            AccDoing.Text = ""; AccWall.Text = ""; AccHelp.Text = "";
            AccThanks.Text = L10n.T("ns.acc.sent");
            AccThanks.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            AccThanks.Text = ex.Message;
            AccThanks.Visibility = Visibility.Visible;
        }
    }

    private async void OnLoadAccessReports(object sender, RoutedEventArgs e)
    {
        try
        {
            var state = await ApiClient.Shared.AccessReports(AccReviewerBox.Password.Trim());
            AccEmpty.Visibility = state.Total == 0 ? Visibility.Visible : Visibility.Collapsed;
            AccReportsList.ItemsSource = state.Reports.Take(6).Select(r => new LineVm
            {
                Line = $"{r.Doing} — {r.Wall}"
                       + (r.Help is { Length: > 0 } h ? $" ({h})" : "")
                       + $" · {r.Lang} · {r.CreatedAt}",
            }).ToList();
        }
        catch (Exception ex)
        {
            AccThanks.Text = ex.Message;
            AccThanks.Visibility = Visibility.Visible;
        }
    }

    private async void OnSendImprovement(object sender, RoutedEventArgs e)
    {
        var message = ImproveMessage.Text.Trim();
        if (message.Length == 0) return;
        var cat = ImproveCategories[System.Math.Max(0, ImproveCategory.SelectedIndex)];
        int? rating = ImproveRating.SelectedIndex >= 1 ? ImproveRating.SelectedIndex : null;
        try
        {
            await ApiClient.Shared.SubmitImprovement(AppState.Current.Token, cat, message, rating);
            ImproveMessage.Text = "";
            ImproveRating.SelectedIndex = 0;
            ImproveThanks.Text = L10n.T("ov.fb.thanks");
            ImproveThanks.Visibility = Visibility.Visible;
            await LoadImprovements();
        }
        catch (Exception ex)
        {
            ImproveThanks.Text = ex.Message;
            ImproveThanks.Visibility = Visibility.Visible;
        }
    }

    private async System.Threading.Tasks.Task LoadLanguage()
    {
        var s = AppState.Current;
        _loadingLanguage = true;
        try
        {
            _languages = (await ApiClient.Shared.Languages()).Languages;
            LanguageBox.ItemsSource = _languages.Select(l =>
                l.Label + (l.SafetyTranslated ? "" : "  (safety steps in English)")).ToList();
            var current = await ApiClient.Shared.UserLanguage(s.Uid!, s.Token!);
            var idx = System.Array.FindIndex(_languages, l => l.Code == current.Language);
            LanguageBox.SelectedIndex = idx >= 0 ? idx : 0;
            PreTranslateToggle.IsOn = (current.Mode ?? "pre") == "pre";
            s.RememberLanguage(current.Language);   // chrome follows the user
        }
        catch { /* backend offline — leave empty */ }
        finally { _loadingLanguage = false; }
    }

    private string CurrentMode => PreTranslateToggle.IsOn ? "pre" : "on_demand";

    private async void OnLanguagePicked(object sender, SelectionChangedEventArgs e)
    {
        if (_loadingLanguage) return;
        var idx = LanguageBox.SelectedIndex;
        if (idx < 0 || idx >= _languages.Length) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.SetLanguage(s.Uid!, s.Token!, _languages[idx].Code, CurrentMode);
            s.RememberLanguage(_languages[idx].Code);
        }
        catch { /* ignore */ }
    }

    private async void OnModeToggled(object sender, RoutedEventArgs e)
    {
        if (_loadingLanguage) return;
        var idx = LanguageBox.SelectedIndex;
        if (idx < 0 || idx >= _languages.Length) return;
        var s = AppState.Current;
        try { await ApiClient.Shared.SetLanguage(s.Uid!, s.Token!, _languages[idx].Code, CurrentMode); }
        catch { /* ignore */ }
    }

    private async void OnTranslate(object sender, RoutedEventArgs e)
    {
        var text = TranslateBox.Text.Trim();
        if (text.Length == 0) return;
        var s = AppState.Current;
        try
        {
            var r = await ApiClient.Shared.Translate(s.Uid!, s.Token!, text);
            TranslateOut.Text = r.Translation;
            TranslateOut.Visibility = Visibility.Visible;
            TranslateEngine.Text = $"engine: {r.Engine}" +
                (r.Note is { } n ? $" — {n}" : "");
            TranslateEngine.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            TranslateOut.Text = ex.Message;
            TranslateOut.Visibility = Visibility.Visible;
        }
    }

    private async System.Threading.Tasks.Task LoadModel()
    {
        var s = AppState.Current;
        _loadingModel = true;
        try
        {
            _providers = (await ApiClient.Shared.Models()).Providers;
            ProviderBox.ItemsSource = _providers.Select(p =>
                $"{p.Label}  ({(p.Configured ? "ready" : "no key")})").ToList();
            var current = await ApiClient.Shared.UserModel(s.Uid!, s.Token!);
            var idx = System.Array.FindIndex(_providers, p => p.Name == current.Provider);
            ProviderBox.SelectedIndex = idx >= 0 ? idx : 0;
        }
        catch { /* backend offline — leave empty */ }
        finally { _loadingModel = false; }
    }

    private async void OnProviderPicked(object sender, SelectionChangedEventArgs e)
    {
        if (_loadingModel) return;
        var idx = ProviderBox.SelectedIndex;
        if (idx < 0 || idx >= _providers.Length) return;
        var s = AppState.Current;
        try { await ApiClient.Shared.SetModel(s.Uid!, s.Token!, _providers[idx].Name); }
        catch { /* ignore */ }
    }

    private static string Cap(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..];

    /// <summary>Store or clear the person's own model key. An empty box is
    /// the clear — no key means the deployment's, and there is no flag to
    /// leave switched on by mistake.</summary>
    private void OnSaveKey(object sender, RoutedEventArgs e)
    {
        AppState.Current.RememberLlmKey(KeyBox.Password);
        KeyBox.Password = AppState.Current.LlmKey;
    }

    /// <summary>The deployment invite key, same clearing rule: empty means
    /// none, and a deployment that never gated signup never needs one.</summary>
    private void OnSaveInvite(object sender, RoutedEventArgs e)
    {
        AppState.Current.RememberSignupKey(InviteBox.Password);
        InviteBox.Password = AppState.Current.SignupKey;
    }
}
