using System;
using System.Globalization;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

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
        ImproveCategory.ItemsSource = ImproveCategories
            .Select(c => char.ToUpper(c[0]) + c[1..]).ToList();
        ImproveCategory.SelectedIndex = 0;
        ImproveRating.ItemsSource = new[] { "—", "1", "2", "3", "4", "5" };
        ImproveRating.SelectedIndex = 0;
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
            AdaptationVaulted.Visibility = Visibility.Collapsed;
            return;
        }
        AdaptationSummary.Text =
            $"Confidence {(int)Math.Round(p.Confidence * 100)}% — earned from "
          + $"{p.EvidenceItems} things already on your record.";

        var helps = p.Profile?.WhatHelps ?? new System.Collections.Generic.Dictionary<string, HelpTally>();
        AdaptationHelps.ItemsSource = helps
            .Where(kv => kv.Value.Answered > 0)
            .OrderBy(kv => kv.Key)
            .Select(kv => new HelpVm
            {
                Condition = kv.Key.Replace('_', ' '),
                Tally = $"helped {kv.Value.Helped} of {kv.Value.Answered}",
            }).ToList();

        var dials = new System.Collections.Generic.List<string>();
        if (p.Profile?.Tone is { Length: > 0 } tone) dials.Add($"Tone you asked for: {tone}");
        if (p.Profile?.Occupation is { Length: > 0 } job) dials.Add($"Work you named: {job}");
        AdaptationDials.Text = string.Join(" · ", dials);
        AdaptationMethod.Text = p.Profile?.Method ?? "";
        AdaptationVaulted.Visibility = p.Vaulted ? Visibility.Visible : Visibility.Collapsed;
    }

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
                ? $"You are known here as {p.KnownAs ?? "a pseudonym"}."
                : "You are enrolled under your own name.";
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
        Greeting.Text = $"Hi, {s.DisplayName}";
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
            Empty.Text = "Couldn't load the baseline — is the backend running?";
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
                ImproveTally.Text = "So far: " + string.Join(" · ", parts);
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
            ImproveThanks.Text = "Thank you — sent.";
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
}
