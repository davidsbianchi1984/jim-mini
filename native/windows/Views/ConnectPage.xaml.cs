using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

public sealed partial class ConnectPage : Page
{
    public sealed class SourceVm
    {
        public string Source { get; init; } = "";
        public string Label { get; init; } = "";
        public bool Consented { get; init; }
    }

    public sealed class SocialVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string Handle { get; init; } = "";
        public bool Collect { get; init; }
        public Visibility CollectVisibility =>
            Collect ? Visibility.Visible : Visibility.Collapsed;
        public Visibility PublishVisibility =>
            Collect ? Visibility.Collapsed : Visibility.Visible;
    }

    public sealed class CatalogVm
    {
        public string Provider { get; init; } = "";
        public string App { get; init; } = "";
        public string Label { get; init; } = "";
        public string Key => $"{Provider}|{App}";
    }

    public sealed class AppConnVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string App { get; init; } = "";
    }

    private static readonly string[] Platforms =
    {
        "instagram", "x", "tiktok", "facebook", "linkedin", "youtube",
        "whatsapp", "discord", "twitch", "pinterest", "snapchat", "mastodon",
    };

    private SocialConn[] _social = Array.Empty<SocialConn>();
    private AppConn[] _appConns = Array.Empty<AppConn>();
    private bool _loadingSources;

    public ConnectPage() => InitializeComponent();

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        PlatformBox.ItemsSource = Platforms.ToList();
        PlatformBox.SelectedIndex = 0;
        await ReloadSources();
        await ReloadSocial();
        await ReloadApps();
    }

    // -- Sources --

    private async System.Threading.Tasks.Task ReloadSources()
    {
        var s = AppState.Current;
        try
        {
            _loadingSources = true;
            var rows = await ApiClient.Shared.Sources(s.Uid!, s.Token!);
            SourcesList.ItemsSource = rows.Select(r => new SourceVm
            {
                Source = r.Source,
                Label = Pretty(r.Source),
                Consented = r.Consented,
            }).ToList();
        }
        catch { /* backend offline: leave the list empty */ }
        finally { _loadingSources = false; }
    }

    private async void OnSourceToggled(object sender, RoutedEventArgs e)
    {
        if (_loadingSources) return;
        if (sender is not ToggleSwitch sw || sw.Tag is not string source) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.SetSource(s.Uid!, s.Token!, source, sw.IsOn);
        }
        catch { await ReloadSources(); }
    }

    // -- Social --

    private async System.Threading.Tasks.Task ReloadSocial()
    {
        var s = AppState.Current;
        try
        {
            _social = await ApiClient.Shared.SocialConnections(s.Uid!, s.Token!);
            SocialList.ItemsSource = _social.Select(c => new SocialVm
            {
                Id = c.Id,
                Title = $"{Pretty(c.Platform)} · {c.Direction}",
                Handle = c.Handle is { } h ? $"@{h}" : "",
                Collect = c.Direction == "collect",
            }).ToList();
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    private void OnConnectCollect(object sender, RoutedEventArgs e) => Connect("collect");

    private void OnConnectPublish(object sender, RoutedEventArgs e) => Connect("publish");

    private async void Connect(string direction)
    {
        if (PlatformBox.SelectedItem is not string platform) return;
        var s = AppState.Current;
        SocialError.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.SocialConnect(
                s.Uid!, s.Token!, platform, direction, HandleBox.Text.Trim());
            HandleBox.Text = "";
            await ReloadSocial();
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    private async void OnCollect(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var conn = _social.FirstOrDefault(c => c.Id == cid);
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.SocialCollect(
                cid, s.Token!, $"sample post from {conn?.Platform}");
            ShowSocialStatus($"collected one item from {conn?.Platform}");
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    private async void OnPublish(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var conn = _social.FirstOrDefault(c => c.Id == cid);
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.SocialPublish(
                cid, s.Token!, "A check-in from my Guardian.");
            ShowSocialStatus($"published to {conn?.Platform}");
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    // -- Apps --

    private async System.Threading.Tasks.Task ReloadApps()
    {
        var s = AppState.Current;
        try
        {
            var cat = await ApiClient.Shared.ConnectorCatalog();
            CatalogList.ItemsSource = cat.Providers
                .SelectMany(p => p.Apps.Select(a => new CatalogVm
                {
                    Provider = p.Provider,
                    App = a.App,
                    Label = a.Label,
                }))
                .Take(10).ToList();
            _appConns = await ApiClient.Shared.AppConnections(s.Uid!, s.Token!);
            AppConnList.ItemsSource = _appConns.Select(c => new AppConnVm
            {
                Id = c.Id,
                Title = $"{c.Provider} · {c.App}",
                App = c.App,
            }).ToList();
        }
        catch (Exception ex) { ShowAppsError(ex.Message); }
    }

    private async void OnAppConnect(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string key) return;
        var parts = key.Split('|', 2);
        if (parts.Length != 2) return;
        var s = AppState.Current;
        AppsError.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.AppConnect(s.Uid!, s.Token!, parts[0], parts[1]);
            ShowAppsStatus($"connected {parts[0]}/{parts[1]}");
            await ReloadApps();
        }
        catch (Exception ex) { ShowAppsError(ex.Message); }
    }

    private async void OnAppCollect(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var conn = _appConns.FirstOrDefault(c => c.Id == cid);
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.AppCollect(
                cid, s.Token!, $"sample context from {conn?.App}");
            ShowAppsStatus($"collected from {conn?.App}");
        }
        catch (Exception ex) { ShowAppsError(ex.Message); }
    }

    // -- helpers --

    private void ShowSocialStatus(string message)
    {
        SocialStatus.Text = message;
        SocialStatus.Visibility = Visibility.Visible;
    }

    private void ShowSocialError(string message)
    {
        SocialError.Text = message;
        SocialError.Visibility = Visibility.Visible;
    }

    private void ShowAppsStatus(string message)
    {
        AppsStatus.Text = message;
        AppsStatus.Visibility = Visibility.Visible;
    }

    private void ShowAppsError(string message)
    {
        AppsError.Text = message;
        AppsError.Visibility = Visibility.Visible;
    }

    private static string Pretty(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..].Replace('_', ' ');
}
