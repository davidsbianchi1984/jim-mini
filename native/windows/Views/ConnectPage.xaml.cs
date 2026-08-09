using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using System.Collections.Generic;

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
        public string CollectSampleLabel => L10n.T("jcon.collect.sample");
        public string PublishUpdateLabel => L10n.T("jcon.publish.update");
    }

    public sealed class PostureVm
    {
        public string Line { get; init; } = "";
    }

    public sealed class RoomVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string Detail { get; init; } = "";
        public string? Url { get; init; }
        public Visibility OpenVisibility =>
            string.IsNullOrEmpty(Url) ? Visibility.Collapsed : Visibility.Visible;
        public string OpenLabel => L10n.T("jcon.open");
    }

    public sealed class PlaceVm
    {
        public string Name { get; init; } = "";
        public int Listings { get; init; }
    }

    public sealed class CatalogVm
    {
        public string Provider { get; init; } = "";
        public string App { get; init; } = "";
        public string Label { get; init; } = "";
        public string Key => $"{Provider}|{App}";
        public string ConnectLabel => L10n.T("jcon.connect");
    }

    public sealed class AppConnVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string App { get; init; } = "";
        public string CollectLabel => L10n.T("jcon.collect");
    }

    private static readonly string[] Platforms =
    {
        "instagram", "x", "tiktok", "facebook", "linkedin", "youtube",
        "whatsapp", "discord", "twitch", "pinterest", "snapchat", "mastodon",
    };

    private SocialConn[] _social = Array.Empty<SocialConn>();
    private AppConn[] _appConns = Array.Empty<AppConn>();
    private bool _loadingSources;

    public ConnectPage()
    {
        InitializeComponent();
        Localize();
    }

    /// The fixed strings on this page. Row-level labels are not here —
    /// they are properties on the view models above, because a template
    /// is stamped once per row and a name addresses only one of them.
    private void Localize()
    {
        SourcesPivot.Header = L10n.T("jcon.tab.sources");
        SocialPivot.Header = L10n.T("jcon.tab.social");
        AppsPivot.Header = L10n.T("jcon.tab.apps");
        CommunityPivot.Header = L10n.T("jcon.community");
        SourcesTitle.Text = L10n.T("jcon.sources");
        SourcesSub.Text = L10n.T("jcon.sources.sub");
        SocialTitle.Text = L10n.T("jcon.social");
        PlatformBox.Header = L10n.T("jcon.platform");
        HandleBox.Header = L10n.T("jcon.handle");
        ConnectCollectButton.Content = L10n.T("jcon.connect.collect");
        ConnectPublishButton.Content = L10n.T("jcon.connect.publish");
        AppsTitle.Text = L10n.T("jcon.apps");
        AppsSub.Text = L10n.T("jcon.apps.sub");
        CommunityTitle.Text = L10n.T("jcon.community");
        CommunityNote.Text = L10n.T("jcon.loading");
        PostureTitle.Text = L10n.T("jcon.notdo");
        RoomsTitle.Text = L10n.T("jcon.rooms");
        RoomsEmpty.Text = L10n.T("jcon.rooms.none");
        NearTitle.Text = L10n.T("jcon.near");
        PlacesEmpty.Text = L10n.T("jcon.places.none");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        PlatformBox.ItemsSource = Platforms.ToList();
        PlatformBox.SelectedIndex = 0;
        await ReloadSources();
        await ReloadSocial();
        await ReloadApps();
        await ReloadCommunity();
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
            ShowSocialStatus(L10n.T("jcon.collected.one")
                .Replace("{platform}", Pretty(conn?.Platform ?? "")));
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
            ShowSocialStatus(L10n.T("jcon.published")
                .Replace("{platform}", Pretty(conn?.Platform ?? "")));
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
            ShowAppsStatus(L10n.T("jcon.connected")
                .Replace("{provider}", parts[0]).Replace("{app}", parts[1]));
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
            ShowAppsStatus(L10n.T("jcon.collected.from")
                .Replace("{app}", conn?.App ?? ""));
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

    // -- Community: the door into QRME, and the visit note --

    /// <summary>
    /// FIG. 2 boxes 222-226 — interact with others, moderated storage,
    /// community interaction, local events and forums in every language.
    ///
    /// None of it is rebuilt here. It lives in QRME, where the moderation, the
    /// rooms and the languages already are, so this pivot is a door rather than
    /// a copy. The posture list is generated from the server's own booleans
    /// instead of being typed out as reassurance, so the page cannot claim more
    /// than the bridge actually does.
    /// </summary>
    private async System.Threading.Tasks.Task ReloadCommunity()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var v = await ApiClient.Shared.Community(s.Uid, s.Token);
            CommunityNote.Text = v.Note;
            CommunityLanguage.Text = v.Language is { Length: > 0 } lang
                ? L10n.T("jcon.rooms.lang").Replace("{lang}", lang)
                : "";

            PostureList.ItemsSource = new[]
            {
                Posture(L10n.T("jcon.posture.mirror"), v.Posture.MirroredHere),
                Posture(L10n.T("jcon.posture.post"), v.Posture.PostsOnYourBehalf),
                Posture(L10n.T("jcon.posture.health"), v.Posture.HealthDataShared),
            };

            var rooms = v.Rooms.Select(r => new RoomVm
            {
                Id = r.Id,
                Title = string.IsNullOrEmpty(r.Topic) ? r.Id : r.Topic!,
                Detail = RoomDetail(r),
                Url = r.Url,
            }).ToList();
            RoomList.ItemsSource = rooms;
            RoomsEmpty.Visibility = rooms.Count == 0 ? Visibility.Visible : Visibility.Collapsed;

            var places = v.Places.Select(pl => new PlaceVm
            {
                Name = string.IsNullOrEmpty(pl.Region)
                    ? pl.Locality : $"{pl.Locality}, {pl.Region}",
                Listings = pl.Listings,
            }).ToList();
            PlaceList.ItemsSource = places;
            PlacesEmpty.Visibility = places.Count == 0 ? Visibility.Visible : Visibility.Collapsed;
        }
        catch (Exception ex) { ShowCommunityError(ex.Message); }
    }

    private static PostureVm Posture(string label, bool happens) =>
        new() { Line = (happens ? "• " : "\u2713 ") + label };

    private static string RoomDetail(CommunityRoom room)
    {
        var bits = new System.Collections.Generic.List<string>();
        if (!string.IsNullOrEmpty(room.Channel)) bits.Add(room.Channel!);
        if (room.Participants > 0)
            bits.Add(L10n.T("jcon.here").Replace("{n}", $"{room.Participants}"));
        return bits.Count == 0 ? room.Id : string.Join(" · ", bits);
    }

    /// The visit is noted first, then the browser opens — the note is the part
    /// that belongs to JIM, and it should not depend on the launch succeeding.
    private async void OnOpenRoom(object sender, RoutedEventArgs e)
    {
        if (sender is not Button b || b.Tag is not string roomId) return;
        if (RoomList.ItemsSource is not System.Collections.Generic.List<RoomVm> rooms) return;
        var room = rooms.FirstOrDefault(r => r.Id == roomId);
        if (room?.Url is null) return;

        var s = AppState.Current;
        if (s.Uid is not null && s.Token is not null)
        {
            try
            {
                await ApiClient.Shared.NoteCommunityVisit(s.Uid, s.Token, roomId);
                VisitStatus.Text = L10n.T("jcon.noted").Replace("{room}", roomId);
                VisitStatus.Visibility = Visibility.Visible;
            }
            catch (Exception ex) { ShowCommunityError(ex.Message); }
        }
        if (Uri.TryCreate(room.Url, UriKind.Absolute, out var uri))
            await Windows.System.Launcher.LaunchUriAsync(uri);
    }

    private void ShowCommunityError(string message)
    {
        CommunityError.Text = message;
        CommunityError.Visibility = Visibility.Visible;
    }

}
