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

    private ProviderInfo[] _providers = System.Array.Empty<ProviderInfo>();
    private bool _loadingModel;   // suppress SelectionChanged while populating

    public OverviewPage() => InitializeComponent();

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
