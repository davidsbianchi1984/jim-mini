using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using System.Collections.Generic;
using System.Threading.Tasks;

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
        MicHead.Text = L10n.T("ns.ch.mic");
        MicNone.Text = L10n.T("ns.ch.mic.none");
        MicDevice.Header = L10n.T("ns.ch.mic.kind");
        MicKind.Header = L10n.T("ns.ch.mic.which");
        MicAttachButton.Content = L10n.T("ns.ch.mic.attach");
        MicCapped.Text = L10n.T("ns.ch.mic.capped");
        MicGain.Header = L10n.T("ns.ch.mic.which");
        MicHandoverReason.PlaceholderText = L10n.T("ns.ch.mic.handover");
        MicHandoverButton.Content = L10n.T("ns.ch.mic.handover");
        MicReleaseButton.Content = L10n.T("ns.ch.mic.release");
        MicDetachButton.Content = L10n.T("ns.ch.mic.detach");
        MicHistoryButton.Content = L10n.T("ns.ch.hist");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        PlatformBox.ItemsSource = Platforms.ToList();
        PlatformBox.SelectedIndex = 0;
        await ReloadSources();
        await ReloadSocial();
        await ReloadApps();
        await ReloadCommunity();
        await ReloadMic();
        LocalizeSettingsCards();
        await LoadVoiceSettings();
        await LoadMailSettings();
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

    // -- channel 2, the lent microphone ----------------------------------

    public sealed class MicHistoryVm { public string Line { get; init; } = ""; }

    private bool _micGainLoading;

    private async Task ReloadMic()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            if (MicKind.Items.Count == 0)
            {
                var types = await ApiClient.Shared.MicTypes();
                MicKind.ItemsSource = types.Personal.Concat(types.Ambient).ToList();
                MicKind.SelectedIndex = 0;
            }
            var mic = await ApiClient.Shared.MicState(s.Uid, s.Token);
            Render(mic);
        }
        catch (Exception e) { MicFailed(e); }
    }

    private async void Render(MicState mic)
    {
        MicAttached.Visibility = mic.Attached ? Visibility.Visible : Visibility.Collapsed;
        MicAttachForm.Visibility = mic.Attached ? Visibility.Collapsed : Visibility.Visible;
        if (!mic.Attached) return;
        MicLine.Text = $"{mic.Device} · {mic.MicType}";
        MicHears.Text = mic.Hears ?? "";
        MicCapped.Visibility = mic.Capped ? Visibility.Visible : Visibility.Collapsed;
        MicReleaseButton.Visibility = mic.Listening ? Visibility.Visible : Visibility.Collapsed;
        try
        {
            if (MicGain.Items.Count == 0)
            {
                var gains = await ApiClient.Shared.MicGains();
                _micGainLoading = true;
                MicGain.ItemsSource = gains.Levels.Select(l => l.Gain).ToList();
                _micGainLoading = false;
            }
            _micGainLoading = true;
            MicGain.SelectedItem = mic.Gain;
            _micGainLoading = false;
        }
        catch (Exception e) { MicFailed(e); }
    }

    private void MicFailed(Exception e)
    {
        MicError.Text = e.Message;
        MicError.Visibility = Visibility.Visible;
    }

    private async void OnAttachMic(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        if (MicKind.SelectedItem is not string kind) return;
        MicError.Visibility = Visibility.Collapsed;
        try { Render(await ApiClient.Shared.AttachMic(s.Uid, s.Token,
                  MicDevice.Text.Trim(), kind)); }
        catch (Exception ex) { MicFailed(ex); }
    }

    private async void OnDetachMic(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        MicError.Visibility = Visibility.Collapsed;
        try { Render(await ApiClient.Shared.DetachMic(s.Uid, s.Token)); }
        catch (Exception ex) { MicFailed(ex); }
    }

    private async void OnMicGainPicked(object sender, SelectionChangedEventArgs e)
    {
        if (_micGainLoading) return;
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        if (MicGain.SelectedItem is not string gain) return;
        try { Render(await ApiClient.Shared.SetMicGain(s.Uid, s.Token, gain)); }
        catch (Exception ex) { MicFailed(ex); }
    }

    private async void OnHandOverMic(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var reason = MicHandoverReason.Text.Trim();
        if (reason.Length == 0) return;
        MicError.Visibility = Visibility.Collapsed;
        try
        {
            Render(await ApiClient.Shared.HandOverMic(s.Uid, s.Token, reason));
            MicHandoverReason.Text = "";
        }
        catch (Exception ex) { MicFailed(ex); }
    }

    private async void OnReleaseMic(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try { Render(await ApiClient.Shared.ReleaseMic(s.Uid, s.Token)); }
        catch (Exception ex) { MicFailed(ex); }
    }

    private async void OnMicHistory(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var rows = await ApiClient.Shared.MicHistory(s.Uid, s.Token);
            MicHistoryList.ItemsSource = rows.Take(6).Select(r => new MicHistoryVm
            {
                Line = $"{r.Device} · {r.Gain}"
                       + (r.Live ? " · " + L10n.T("ns.ch.hist.live") : ""),
            }).ToList();
        }
        catch (Exception ex) { MicFailed(ex); }
    }
    // -- deployment settings: the voice and the mail desk --------------------
    // Console doors since 0.6.0 / 0.4.x; these are the desktop's. Keys and
    // the password are write-only: the routes say whether one is set and
    // never say it back.

    private string _vsProvider = "";
    private string _vsVoiceId = "";

    private void LocalizeSettingsCards()
    {
        VsHead.Text = L10n.T("ns.vs.title");
        VsHear.Content = L10n.T("ns.vs.hear");
        VsSaveButton.Content = L10n.T("ns.set.save");
        VsResetButton.Content = L10n.T("ns.bas.reset");
        MlHead.Text = L10n.T("ns.ml.title");
        MlHost.Header = L10n.T("ns.ml.host");
        MlHost.PlaceholderText = L10n.T("ns.ml.host.ph");
        MlPort.Header = L10n.T("ns.ml.port");
        MlUser.Header = L10n.T("ns.ml.user");
        MlUser.PlaceholderText = L10n.T("ns.ml.user.ph");
        MlPass.Header = L10n.T("ns.ml.pass");
        MlFrom.Header = L10n.T("ns.ml.from");
        MlFrom.PlaceholderText = L10n.T("ns.ml.user.ph");
        MlLink.Header = L10n.T("ns.ml.link") + L10n.T("ns.ml.link.note");
        MlLink.PlaceholderText = L10n.T("ns.ml.link.ph");
        MlSaveButton.Content = L10n.T("ns.set.save");
        MlResetButton.Content = L10n.T("ns.bas.reset");
        MlTestTo.Header = L10n.T("ns.ml.test");
        MlTestTo.PlaceholderText = L10n.T("ns.ml.test.ph");
        MlTestButton.Content = L10n.T("ns.ml.test");
    }

    private async Task LoadVoiceSettings()
    {
        try { RenderVoiceSettings(await ApiClient.Shared.VoiceSettings()); }
        catch { /* leave as-is */ }
    }

    private void RenderVoiceSettings(VoiceSettingsOut s)
    {
        VsError.Visibility = Visibility.Collapsed;
        if (_vsProvider.Length == 0) _vsProvider = s.Provider;
        if (_vsVoiceId.Length == 0) _vsVoiceId = s.VoiceId ?? "";
        VsHear.IsChecked = s.SpeakReplies;
        VsStatus.Text = s.Provider == "device"
            ? L10n.T("ns.vs.pitch")
            : L10n.T("ns.vs.through").Replace("{provider}", s.Provider)
                .Replace("{env}", s.KeySource == "environment" ? " (env)" : "");
        VsKey.PlaceholderText = s.KeySet ? L10n.T("ns.ml.saved") : "sk-\u2026";

        // The provider vocabulary is the backend's PROVIDERS tuple; the
        // describe route answers the current one but does not enumerate.
        VsProviders.Children.Clear();
        foreach (var name in new[] { "elevenlabs", "openai", "device" })
        {
            var chosen = name;
            var chip = new Microsoft.UI.Xaml.Controls.Primitives.ToggleButton
            { Content = chosen, FontSize = 11, IsChecked = _vsProvider == chosen };
            chip.Click += (_, _) =>
            { _vsProvider = chosen; RenderVoiceSettings(s); };
            VsProviders.Children.Add(chip);
        }
        VsVoices.Children.Clear();
        if (_vsProvider != "device")
            foreach (var voice in s.Voices)
            {
                var id = voice.Id;
                var chip = new Microsoft.UI.Xaml.Controls.Primitives.ToggleButton
                {
                    Content = $"{voice.Name} \u00b7 {voice.Note}",
                    FontSize = 11,
                    IsChecked = _vsVoiceId == id,
                };
                chip.Click += (_, _) =>
                { _vsVoiceId = id; RenderVoiceSettings(s); };
                VsVoices.Children.Add(chip);
            }
        VsKey.Visibility = _vsProvider == "device" ? Visibility.Collapsed
                                                   : Visibility.Visible;
    }

    private void ShowVoiceError(Exception ex)
    {
        VsError.Text = ex.Message;
        VsError.Visibility = Visibility.Visible;
    }

    private async void OnVoiceSave(object sender, RoutedEventArgs e)
    {
        if (_vsProvider.Length == 0) return;
        try
        {
            RenderVoiceSettings(await ApiClient.Shared.SaveVoiceSettings(
                _vsProvider, VsKey.Password.Trim(), _vsVoiceId,
                VsHear.IsChecked == true));
            VsKey.Password = "";
        }
        catch (Exception ex) { ShowVoiceError(ex); }
    }

    private async void OnVoiceReset(object sender, RoutedEventArgs e)
    {
        try
        {
            var s = await ApiClient.Shared.ClearVoiceSettings();
            _vsProvider = s.Provider; _vsVoiceId = "";
            RenderVoiceSettings(s);
        }
        catch (Exception ex) { ShowVoiceError(ex); }
    }

    private async Task LoadMailSettings()
    {
        try { RenderMailSettings(await ApiClient.Shared.MailSettings()); }
        catch { /* leave as-is */ }
    }

    private void RenderMailSettings(MailSettingsOut s)
    {
        MlError.Visibility = Visibility.Collapsed;
        MlStatus.Text = s.Transport == "smtp"
            ? L10n.T("ns.ml.smtp").Replace("{host}", s.Host ?? "")
                .Replace("{env}", s.Source == "environment" ? " (env)" : "")
            : L10n.T("ns.ml.none");
        if (MlHost.Text.Length == 0) MlHost.Text = s.Host ?? "";
        MlPort.Value = s.Port;
        if (MlUser.Text.Length == 0) MlUser.Text = s.Username ?? "";
        if (MlFrom.Text.Length == 0) MlFrom.Text = s.Sender ?? "";
        if (MlLink.Text.Length == 0) MlLink.Text = s.PublicUrl;
        MlPass.Header = L10n.T("ns.ml.pass")
            + (s.PasswordSet ? " " + L10n.T("ns.ml.saved") : "");
        MlPass.PlaceholderText = L10n.T("ns.ml.pass.ph");
    }

    private void ShowMailError(Exception ex)
    {
        MlError.Text = ex.Message;
        MlError.Visibility = Visibility.Visible;
    }

    private async void OnMailSave(object sender, RoutedEventArgs e)
    {
        var host = MlHost.Text.Trim();
        if (host.Length == 0) return;
        try
        {
            RenderMailSettings(await ApiClient.Shared.SaveMailSettings(
                host, (int)MlPort.Value, MlUser.Text.Trim(),
                MlPass.Password, MlFrom.Text.Trim(), MlLink.Text.Trim()));
            MlPass.Password = "";
        }
        catch (Exception ex) { ShowMailError(ex); }
    }

    private async void OnMailReset(object sender, RoutedEventArgs e)
    {
        try
        {
            MlHost.Text = ""; MlUser.Text = ""; MlPass.Password = "";
            MlFrom.Text = "";
            RenderMailSettings(await ApiClient.Shared.ClearMailSettings());
        }
        catch (Exception ex) { ShowMailError(ex); }
    }

    private async void OnMailTest(object sender, RoutedEventArgs e)
    {
        var to = MlTestTo.Text.Trim();
        if (to.Length == 0) return;
        try
        {
            var outcome = await ApiClient.Shared.TestMail(to);
            MlTestNote.Text = "\u2713 " + outcome.To;
            MlTestNote.Visibility = outcome.Sent ? Visibility.Visible
                                                 : Visibility.Collapsed;
        }
        catch (Exception ex) { ShowMailError(ex); }
    }
}
