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
        var s = AppState.Current;
        Greeting.Text = $"Hi, {s.DisplayName}";
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
        try { await ApiClient.Shared.SetLanguage(s.Uid!, s.Token!, _languages[idx].Code, CurrentMode); }
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
