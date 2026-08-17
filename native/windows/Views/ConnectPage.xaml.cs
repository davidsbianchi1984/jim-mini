using System;
using System.Linq;
using System.Runtime.InteropServices.WindowsRuntime;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace JimGuardian.Views;

public sealed partial class ConnectPage : Page
{
    /// <summary>The assisted call being set up, if any. Held rather than
    /// re-fetched: the notice to play belongs to this one call.</summary>
    private AssistedCall? _call;

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
        public bool HasHandle { get; init; }
        public string QrLine { get; init; } = "";
        public Visibility ScrapeVisibility =>
            Collect && HasHandle ? Visibility.Visible : Visibility.Collapsed;
        public string CollectSampleLabel => L10n.T("jcon.collect.sample");
        public string ScrapeLabel => L10n.T("jcon.scrape");
        public string PublishUpdateLabel => L10n.T("jcon.publish.update");
        public string BeaconLabel => L10n.T("rch.acc.beacon");
        public string DisconnectLabel => L10n.T("rch.acc.disconnect");
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

    public sealed class ExcursionVm
    {
        public string Id { get; init; } = "";
        public string Topic { get; init; } = "";
        public int Redactions { get; init; }
        public bool LeftHost { get; init; }
        // Amber if the question left this host, green if it stayed — the
        // price line on the card says what the number and the color mean.
        public Microsoft.UI.Xaml.Media.Brush HostBrush =>
            (Microsoft.UI.Xaml.Media.Brush)Application.Current.Resources[
                LeftHost ? "JimAmberBrush" : "JimGreenBrush"];
        public bool KeepEnabled { get; init; }
        public string ReadLabel => L10n.T("rch.ask.read");
        public string KeepLabel => L10n.T("rch.ask.keep");
    }

    public sealed class LineVm
    {
        public string Line { get; init; } = "";
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
        TalkTitle.Text = L10n.T("ns.vs.title");
        TalkText.PlaceholderText = L10n.T("ns.vc.say.ph");
        TalkSpeakButton.Content = L10n.T("ns.vc.speak");
        TalkMicButton.Content = L10n.T("ns.vc.talk");
        TalkDeviceSpoke.Text = L10n.T("ns.vc.device");
        TalkMicRefused.Text = L10n.T("ns.vc.mic.refused");
        AskTitle.Text = L10n.T("rch.ask");
        AskTopicBox.PlaceholderText = L10n.T("rch.ask.topic.ph");
        AskQuestionBox.PlaceholderText = L10n.T("rch.ask.q.ph");
        AskGoButton.Content = L10n.T("rch.ask.go");
        AskPrice.Text = L10n.T("rch.ask.price");
        FeedTitle.Text = L10n.T("feed.title");
        FeedCannotPost.Text = L10n.T("feed.cannotpost");
        FeedEmpty.Text = L10n.T("feed.empty");
        OpenInQrmeButton.Content = L10n.T("feed.openinqrme");
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
        await ReloadExcursions();
        await LoadHealthLine();
        await ReloadMic();
        LocalizeSettingsCards();
        await LoadVoiceSettings();
        await LoadMailSettings();
        LocalizeWristCards();
        await LoadWatch();
        await LoadDevices();
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
                HasHandle = !string.IsNullOrEmpty(c.Handle),
                Collect = c.Direction == "collect",
                QrLine = L10n.T("qr.addr") + " "
                    + ApiClient.Shared.ConnectionQrUrl(c.Id),
            }).ToList();
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    // One reading by hand, through the same door the automation uses —
    // the cheapest proof the tether is live.
    private async void OnWatchDrip(object sender, RoutedEventArgs e)
    {
        if (_watch is null || !int.TryParse(WtDripBox.Text, out var hr)) return;
        var token = _watch.DripUrl.Split('/').Last();
        try
        {
            var ack = await ApiClient.Shared.WatchDrip(token, hr);
            WtDripAck.Text = L10n.T(ack.Noticed ? "ns.wt.drip.noticed"
                                                : "ns.wt.drip.ok")
                .Replace("{n}", ack.Received.ToString());
            WtDripAck.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            WtError.Text = ex.Message;
            WtError.Visibility = Visibility.Visible;
        }
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

    private async void OnScrape(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var conn = _social.FirstOrDefault(c => c.Id == cid);
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.SocialScrape(cid, s.Token!);
            ShowSocialStatus(L10n.T("jcon.scraped.one")
                .Replace("{platform}", conn?.Platform ?? ""));
            await ReloadSocial();
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

    // -- The excursion and the window: safe knowledge excursions, the noted
    //    visits, and QRME's public feed through the tandem --

    private string? _feedUrl;

    private async Task ReloadExcursions()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var rows = await ApiClient.Shared.Excursions(s.Uid, s.Token);
            ExcursionList.ItemsSource = rows.Select(r => new ExcursionVm
            {
                Id = r.Id,
                Topic = r.Topic,
                Redactions = r.Redactions,
                LeftHost = r.LeftHost,
                KeepEnabled = !r.Learned,
            }).ToList();

            var visits = await ApiClient.Shared.CommunityVisits(s.Uid, s.Token);
            VisitsLine.Text = L10n.T("rch.wrist.visits")
                .Replace("{n}", $"{visits.Length}");
            VisitList.ItemsSource = visits.Take(5)
                .Select(v => new LineVm { Line = $"{v.RoomId} · {v.At}" })
                .ToList();
        }
        catch (Exception ex) { ShowCommunityError(ex.Message); }

        try
        {
            var feed = await ApiClient.Shared.CommunityFeed(s.Uid, s.Token);
            FeedNote.Text = feed.Note;
            FeedNote.Visibility = Visibility.Visible;
            FeedCannotPost.Visibility = Visibility.Visible;
            FeedEmpty.Visibility = feed.Items.Length == 0
                ? Visibility.Visible : Visibility.Collapsed;
            FeedList.ItemsSource = feed.Items.Take(6).Select(i => new LineVm
            {
                Line = $"{i.Title ?? i.Topic ?? ""} · {i.Kind ?? ""}",
            }).ToList();
            _feedUrl = feed.OpenInQrme;
            OpenInQrmeButton.Visibility = _feedUrl is null
                ? Visibility.Collapsed : Visibility.Visible;
        }
        catch (Exception ex)
        {
            // No QRME endpoint is a posture, not a fault: the 409 carries the
            // server's own sentence and the card shows it.
            FeedRefused.Text = ex.Message;
            FeedRefused.Visibility = Visibility.Visible;
        }
    }

    private async void OnStartExcursion(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var topic = AskTopicBox.Text.Trim();
        var question = AskQuestionBox.Text.Trim();
        if (topic.Length == 0 || question.Length == 0) return;
        try
        {
            await ApiClient.Shared.StartExcursion(s.Uid, s.Token, topic, question);
            AskTopicBox.Text = "";
            AskQuestionBox.Text = "";
            await ReloadExcursions();
        }
        catch (Exception ex) { ShowCommunityError(ex.Message); }
    }

    private async void OnReadExcursion(object sender, RoutedEventArgs e)
    {
        if (sender is not Button b || b.Tag is not string cid) return;
        var s = AppState.Current;
        if (s.Token is null) return;
        try
        {
            var row = await ApiClient.Shared.ExcursionEntry(cid, s.Token);
            ExcursionEntryText.Text = row.Findings ?? "";
            ExcursionEntryText.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowCommunityError(ex.Message); }
    }

    private async void OnKeepExcursion(object sender, RoutedEventArgs e)
    {
        if (sender is not Button b || b.Tag is not string cid) return;
        var s = AppState.Current;
        if (s.Token is null) return;
        try
        {
            var got = await ApiClient.Shared.LearnExcursion(cid, s.Token);
            if (got.Note is { Length: > 0 } note)
            {
                ExcursionLearnedText.Text = note;
                ExcursionLearnedText.Visibility = Visibility.Visible;
            }
            await ReloadExcursions();
        }
        catch (Exception ex) { ShowCommunityError(ex.Message); }
    }

    private async void OnOpenFeedInQrme(object sender, RoutedEventArgs e)
    {
        if (_feedUrl is null) return;
        if (Uri.TryCreate(_feedUrl, UriKind.Absolute, out var uri))
            await Windows.System.Launcher.LaunchUriAsync(uri);
    }

    // -- The voice pair: say it aloud, and hear what was said --

    private Windows.Media.Playback.MediaPlayer? _player;
    private Windows.Media.Capture.MediaCapture? _capture;
    private Windows.Storage.StorageFile? _clip;
    private bool _talkRecording;

    /// <summary>The backend's own pulse, shown as one small line — the
    /// route every deployment answers without an account.</summary>
    private async Task LoadHealthLine()
    {
        try
        {
            var h = await ApiClient.Shared.Health();
            TalkHealth.Text = $"{h.Status} · {h.Tandem}";
            TalkHealth.Visibility = Visibility.Visible;
        }
        catch { /* an unreachable backend already shows everywhere else */ }
    }

    private void PlayStream(Windows.Storage.Streams.IRandomAccessStream stream,
                            string contentType)
    {
        _player?.Dispose();
        _player = new Windows.Media.Playback.MediaPlayer
        {
            Source = Windows.Media.Core.MediaSource.CreateFromStream(
                stream, contentType),
        };
        _player.Play();
    }

    /// The configured voice when the deployment has one; the device's own
    /// otherwise — the same two layers, in the same order, as the console.
    private async void OnSpeakAloud(object sender, RoutedEventArgs e)
    {
        var toSay = TalkText.Text.Trim();
        if (toSay.Length == 0) return;
        TalkDeviceSpoke.Visibility = Visibility.Collapsed;
        TalkError.Visibility = Visibility.Collapsed;
        try
        {
            var bytes = await ApiClient.Shared.SpeakAloud(toSay);
            var stream = new Windows.Storage.Streams.InMemoryRandomAccessStream();
            await stream.WriteAsync(bytes.AsBuffer());
            stream.Seek(0);
            PlayStream(stream, "audio/mpeg");
        }
        catch
        {
            // 503 and everything else: the device's own voice reads it.
            try
            {
                using var synth =
                    new Windows.Media.SpeechSynthesis.SpeechSynthesizer();
                var spoken = await synth.SynthesizeTextToStreamAsync(toSay);
                PlayStream(spoken, spoken.ContentType);
                TalkDeviceSpoke.Visibility = Visibility.Visible;
            }
            catch (Exception inner) { ShowTalkError(inner.Message); }
        }
    }

    private async void OnTalkMic(object sender, RoutedEventArgs e)
    {
        if (!_talkRecording)
        {
            TalkMicRefused.Visibility = Visibility.Collapsed;
            TalkError.Visibility = Visibility.Collapsed;
            try
            {
                _capture = new Windows.Media.Capture.MediaCapture();
                await _capture.InitializeAsync(
                    new Windows.Media.Capture.MediaCaptureInitializationSettings
                    {
                        StreamingCaptureMode =
                            Windows.Media.Capture.StreamingCaptureMode.Audio,
                    });
                var folder = await Windows.Storage.StorageFolder
                    .GetFolderFromPathAsync(System.IO.Path.GetTempPath());
                _clip = await folder.CreateFileAsync("speech.m4a",
                    Windows.Storage.CreationCollisionOption.ReplaceExisting);
                await _capture.StartRecordToStorageFileAsync(
                    Windows.Media.MediaProperties.MediaEncodingProfile.CreateM4a(
                        Windows.Media.MediaProperties.AudioEncodingQuality.Auto),
                    _clip);
                _talkRecording = true;
                TalkMicButton.Content = L10n.T("ns.vc.stop");
            }
            catch
            {
                // Initialization is where a refused microphone surfaces.
                TalkMicRefused.Visibility = Visibility.Visible;
            }
            return;
        }

        try
        {
            await _capture!.StopRecordAsync();
            _capture.Dispose();
            _capture = null;
            _talkRecording = false;
            TalkMicButton.Content = L10n.T("ns.vc.talk");
            if (_clip is null) return;
            var buffer = await Windows.Storage.FileIO.ReadBufferAsync(_clip);
            var got = await ApiClient.Shared.Transcribe(
                Convert.ToBase64String(buffer.ToArray()), "speech.m4a");
            TalkHeard.Text = got.Text;
            TalkHeard.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowTalkError(ex.Message); }
    }

    private void ShowTalkError(string message)
    {
        TalkError.Text = message;
        TalkError.Visibility = Visibility.Visible;
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
            await LoadCalls();
            await LoadMonitors();
            await LoadDay();
            await LoadLiaisons();
        }
        catch (Exception e) { MicFailed(e); }
    }

    /// <summary>Which links are still going, and why. Each row's half is what
    /// this person's own guardian said — the other person's was never theirs
    /// to read.</summary>
    private async System.Threading.Tasks.Task LoadLiaisons()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var txt = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources["JimTxtBrush"];
        var t2 = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources["JimT2Brush"];
        LiaisonHead.Text = L10n.T("lia.head");
        LiaisonLead.Text = L10n.T("lia.lead");
        LiaisonOther.PlaceholderText = L10n.T("lia.who.ph");
        LiaisonOpenButton.Content = L10n.T("lia.open");
        try
        {
            var rows = await ApiClient.Shared.Liaisons(s.Uid, s.Token);
            LiaisonPanel.Children.Clear();
            foreach (var l in rows)
            {
                var box = new StackPanel { Spacing = 2 };
                box.Children.Add(new TextBlock
                {
                    Text = l.About.Length > 0 ? l.About : l.Id, FontSize = 13,
                    TextWrapping = TextWrapping.Wrap, Foreground = txt,
                });
                if (l.Task.Length > 0)
                {
                    // The task is why it is still open — once both sides have
                    // said so. Naming it is the namer's own yes and nothing
                    // more, so the row says which of the three states this
                    // link is in rather than leaving it ambiguous.
                    box.Children.Add(new TextBlock
                    {
                        Text = l.Task, FontSize = 11,
                        TextWrapping = TextWrapping.Wrap, Foreground = t2,
                    });
                    box.Children.Add(new TextBlock
                    {
                        Text = l.HoldsItOpen ? L10n.T("lia.holds")
                             : l.YouAgreed ? L10n.T("lia.waiting")
                             : L10n.T("lia.yours"),
                        FontSize = 11,
                        TextWrapping = TextWrapping.Wrap, Foreground = t2,
                    });
                }
                box.Children.Add(new TextBlock
                {
                    Text = l.Running ? L10n.T("lia.running") : L10n.T("lia.closed"),
                    FontSize = 11, Foreground = t2,
                });
                var id = l.Id;
                var mine = new Button { Content = L10n.T("lia.mine") };
                var shown = new TextBlock
                {
                    FontSize = 11, TextWrapping = TextWrapping.Wrap,
                    Foreground = t2,
                };
                mine.Click += async (_, _) =>
                {
                    try
                    {
                        var h = await ApiClient.Shared.LiaisonHalf(
                            s.Uid, s.Token, id);
                        shown.Text = L10n.T("lia.bymine") + " "
                            + string.Join(" · ", h.SaidByMine) + "\n"
                            + L10n.T("lia.tomine") + " "
                            + string.Join(" · ", h.SaidToMine);
                    }
                    catch (Exception ex) { MicFailed(ex); }
                };
                box.Children.Add(mine);
                box.Children.Add(shown);
                if (l.Running)
                {
                    var say = new Button { Content = L10n.T("lia.say") };
                    say.Click += async (_, _) =>
                    {
                        try
                        {
                            await ApiClient.Shared.LiaisonSaid(
                                s.Uid, s.Token, id, L10n.T("lia.said.example"));
                        }
                        catch (Exception ex) { MicFailed(ex); }
                    };
                    box.Children.Add(say);
                    var work = new Button { Content = L10n.T("lia.task") };
                    work.Click += async (_, _) =>
                    {
                        try
                        {
                            await ApiClient.Shared.LiaisonTask(
                                s.Uid, s.Token, id, L10n.T("lia.task.example"));
                            await LoadLiaisons();
                        }
                        catch (Exception ex) { MicFailed(ex); }
                    };
                    box.Children.Add(work);
                    // The other side's yes. Offered only where there is a
                    // task this person has not already agreed to — agreeing
                    // with yourself is not something the backend counts, so a
                    // button offering it would be a button that does nothing.
                    if (l.Task.Length > 0 && !l.YouAgreed)
                    {
                        var agree = new Button { Content = L10n.T("lia.agree") };
                        agree.Click += async (_, _) =>
                        {
                            try
                            {
                                await ApiClient.Shared.LiaisonAgreed(
                                    s.Uid, s.Token, id);
                                await LoadLiaisons();
                            }
                            catch (Exception ex) { MicFailed(ex); }
                        };
                        box.Children.Add(agree);
                    }
                    var stop = new Button { Content = L10n.T("lia.stop") };
                    stop.Click += async (_, _) =>
                    {
                        try
                        {
                            await ApiClient.Shared.CloseLiaison(
                                s.Uid, s.Token, id, "stopped");
                            await LoadLiaisons();
                        }
                        catch (Exception ex) { MicFailed(ex); }
                    };
                    box.Children.Add(stop);
                }
                LiaisonPanel.Children.Add(box);
            }
        }
        catch (Exception ex) { MicFailed(ex); }
    }

    /// <summary>Open a link to another person's guardian. Refused unless the
    /// two are already each other's contacts.</summary>
    private async void OnOpenLiaison(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var other = LiaisonOther.Text.Trim();
        if (s.Uid is null || s.Token is null || other.Length == 0) return;
        try
        {
            await ApiClient.Shared.OpenLiaison(s.Uid, s.Token, other);
            await LoadLiaisons();
        }
        catch (Exception ex) { MicFailed(ex); }
    }

    /// <summary>Everything that can be plugged in, off rows included. A
    /// roster showing only what is already on is a roster nobody can add
    /// to.</summary>
    /// <summary>What the monitors actually took in today, and what survived.
    ///
    /// The drops are in here too, each with the promise that dropped it: a
    /// record listing only what it kept would be one with its own omissions
    /// edited out.</summary>
    private async System.Threading.Tasks.Task LoadDay()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var txt = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources["JimTxtBrush"];
        var t2 = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources["JimT2Brush"];
        DayHead.Text = L10n.T("day.head");
        DayPanel.Children.Clear();
        try
        {
            var day = await ApiClient.Shared.Day(s.Uid, s.Token);
            if (day.Account.Quiet)
            {
                DayPanel.Children.Add(new TextBlock
                {
                    Text = L10n.T("day.quiet"), FontSize = 11,
                    TextWrapping = TextWrapping.Wrap, Foreground = t2,
                });
            }
            foreach (var m in day.Account.Monitors)
            {
                DayPanel.Children.Add(new TextBlock
                {
                    Text = $"{m.Monitor} — {m.Sensed} " + L10n.T("day.sensed")
                           + $" · {m.Kept} " + L10n.T("day.kept"),
                    FontSize = 13, TextWrapping = TextWrapping.Wrap,
                    Foreground = txt,
                });
                foreach (var why in m.Because)
                {
                    DayPanel.Children.Add(new TextBlock
                    {
                        Text = L10n.T($"day.why.{why}"), FontSize = 11,
                        TextWrapping = TextWrapping.Wrap, Foreground = t2,
                    });
                }
            }
            // The short list, by construction.
            foreach (var k in day.Survived)
            {
                DayPanel.Children.Add(new TextBlock
                {
                    Text = k.Content, FontSize = 11,
                    TextWrapping = TextWrapping.Wrap, Foreground = t2,
                });
                var momentId = k.Id;
                var drop = new Button { Content = L10n.T("day.forget") };
                drop.Click += async (_, _) =>
                {
                    try
                    {
                        await ApiClient.Shared.ForgetMoment(
                            s.Uid, s.Token, momentId);
                        await LoadDay();
                    }
                    catch (Exception ex) { MicFailed(ex); }
                };
                DayPanel.Children.Add(drop);
            }
            DayPanel.Children.Add(new TextBlock
            {
                Text = L10n.T("day.meet"), FontSize = 13,
                FontWeight = Microsoft.UI.Text.FontWeights.Bold,
                TextWrapping = TextWrapping.Wrap, Foreground = txt,
            });
            foreach (var st in day.Stretches)
            {
                DayPanel.Children.Add(new TextBlock
                {
                    Text = st.About.Length > 0 ? st.About : st.Monitor,
                    FontSize = 12, TextWrapping = TextWrapping.Wrap,
                    Foreground = txt,
                });
                if (st.CatchesOthers && st.OthersTold)
                {
                    DayPanel.Children.Add(new TextBlock
                    {
                        Text = L10n.T("day.meet.told"), FontSize = 11,
                        TextWrapping = TextWrapping.Wrap, Foreground = t2,
                    });
                }
                if (st.Running)
                {
                    var stretchId = st.Id;
                    var end = new Button { Content = L10n.T("day.meet.end") };
                    end.Click += async (_, _) =>
                    {
                        try
                        {
                            await ApiClient.Shared.CloseStretch(
                                s.Uid, s.Token, stretchId);
                            await LoadDay();
                        }
                        catch (Exception ex) { MicFailed(ex); }
                    };
                    DayPanel.Children.Add(end);
                }
            }
        }
        catch { /* the roster above stands on its own */ }
    }

    private async System.Threading.Tasks.Task LoadMonitors()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var txt = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources["JimTxtBrush"];
        var t2 = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources["JimT2Brush"];
        MonitorsHead.Text = L10n.T("mon.head");
        MonitorsLead.Text = L10n.T("mon.lead");
        try
        {
            var rows = await ApiClient.Shared.Monitors(s.Uid, s.Token);
            MonitorsPanel.Children.Clear();
            foreach (var m in rows)
            {
                var box = new StackPanel { Spacing = 2 };
                box.Children.Add(new TextBlock
                {
                    Text = m.Says, FontSize = 13,
                    TextWrapping = TextWrapping.Wrap, Foreground = txt,
                });
                box.Children.Add(new TextBlock
                {
                    Text = string.Join(" · ", m.Senses)
                           + (m.CatchesOthers ? " · " + L10n.T("mon.others") : ""),
                    FontSize = 11, TextWrapping = TextWrapping.Wrap,
                    Foreground = t2,
                });
                box.Children.Add(new TextBlock
                {
                    Text = L10n.T("mon.keeps") + " " + m.Holds, FontSize = 11,
                    TextWrapping = TextWrapping.Wrap, Foreground = t2,
                });
                box.Children.Add(new TextBlock
                {
                    Text = m.On ? L10n.T("mon.on") : L10n.T("mon.off"),
                    FontSize = 11, Foreground = t2,
                });
                var name = m.Name;
                if (m.On)
                {
                    // Refused with a 403 until the row is on — the one door.
                    var take = new Button { Content = L10n.T("mon.sense") };
                    take.Click += async (_, _) =>
                    {
                        try
                        {
                            await ApiClient.Shared.MonitorSensed(
                                s.Uid, s.Token, name);
                        }
                        catch (Exception ex) { MicFailed(ex); }
                    };
                    box.Children.Add(take);
                    // Begin a meeting on this one. Where it catches other
                    // people the claim that they were told is made here
                    // rather than inherited from the switch.
                    var catches = m.CatchesOthers;
                    var meet = new Button { Content = L10n.T("day.meet.open") };
                    meet.Click += async (_, _) =>
                    {
                        try
                        {
                            await ApiClient.Shared.OpenStretch(
                                s.Uid, s.Token, name, "", catches);
                            await LoadDay();
                        }
                        catch (Exception ex) { MicFailed(ex); }
                    };
                    box.Children.Add(meet);
                    var off = new Button { Content = L10n.T("mon.unplug") };
                    off.Click += async (_, _) =>
                    {
                        try
                        {
                            await ApiClient.Shared.UnplugMonitor(
                                s.Uid, s.Token, name);
                            await LoadMonitors();
                            await LoadDay();
                        }
                        catch (Exception ex) { MicFailed(ex); }
                    };
                    box.Children.Add(off);
                }
                else
                {
                    var told = m.CatchesOthers;
                    var on = new Button
                    {
                        Content = told ? L10n.T("mon.plug.told")
                                       : L10n.T("mon.plug"),
                    };
                    on.Click += async (_, _) =>
                    {
                        try
                        {
                            await ApiClient.Shared.PlugMonitor(
                                s.Uid, s.Token, name, "", told);
                            await LoadMonitors();
                            await LoadDay();
                        }
                        catch (Exception ex) { MicFailed(ex); }
                    };
                    box.Children.Add(on);
                }
                MonitorsPanel.Children.Add(box);
            }
        }
        catch (Exception ex) { MicFailed(ex); }
    }

    /// <summary>Set up the call. It is not listening: what comes back is the
    /// notice to play, in the languages the number suggests.</summary>
    private async void OnOpenCall(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var t2 = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources["JimT2Brush"];
        try
        {
            var number = CallNumber.Text.Trim();
            _call = await ApiClient.Shared.OpenCall(
                s.Uid, s.Token, "speaker", false,
                number.Length == 0 ? null : number);
            CallPlayHead.Text = L10n.T("cal.play");
            CallSay.Children.Clear();
            foreach (var part in _call.Notices)
            {
                CallSay.Children.Add(new TextBlock
                {
                    Text = part.Language + " — " + part.Words, FontSize = 12,
                    TextWrapping = TextWrapping.Wrap,
                    Foreground = (Microsoft.UI.Xaml.Media.Brush)
                        Application.Current.Resources["JimTxtBrush"],
                });
            }
            CallFrom.Text = L10n.T("cal.from") + " " + _call.LanguageFrom;
            CallNotice.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { MicFailed(ex); }
    }

    private async void OnCallAnnounced(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _call is null) return;
        try
        {
            await ApiClient.Shared.CallAnnounced(s.Uid, _call.Id, s.Token);
            await LoadCalls();
        }
        catch (Exception ex) { MicFailed(ex); }
    }

    /// <summary>Refused with a 409 until the notice has gone out. One
    /// door.</summary>
    private async void OnCallHeard(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _call is null) return;
        try { await ApiClient.Shared.CallHeard(s.Uid, _call.Id, s.Token); }
        catch (Exception ex) { MicFailed(ex); }
    }

    private async void OnEndCall(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _call is null) return;
        try
        {
            await ApiClient.Shared.EndCall(s.Uid, _call.Id, s.Token);
            _call = null;
            CallNotice.Visibility = Visibility.Collapsed;
            await LoadCalls();
        }
        catch (Exception ex) { MicFailed(ex); }
    }

    /// <summary>Assisted calls, each saying whether it announced itself. A
    /// call that never announced never listened and stays here: it is the
    /// evidence that the ordering held.</summary>
    private async System.Threading.Tasks.Task LoadCalls()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        CallHead.Text = L10n.T("cal.head");
        CallLead.Text = L10n.T("cal.lead");
        CallNumber.PlaceholderText = L10n.T("cal.number.ph");
        CallOpenButton.Content = L10n.T("cal.open");
        CallPlayedButton.Content = L10n.T("cal.played");
        CallListenButton.Content = L10n.T("cal.listen");
        CallEndButton.Content = L10n.T("cal.end");
        try
        {
            var rows = await ApiClient.Shared.Calls(s.Uid, s.Token);
            CallHistory.Children.Clear();
            foreach (var row in rows)
            {
                CallHistory.Children.Add(new TextBlock
                {
                    Text = row.Route + " · " + string.Join(" · ", row.SpokenIn)
                           + " · " + L10n.T(row.Listened ? "cal.told"
                                                         : "cal.nevertold"),
                    FontSize = 11, TextWrapping = TextWrapping.Wrap,
                    Foreground = (Microsoft.UI.Xaml.Media.Brush)
                        Application.Current.Resources["JimT2Brush"],
                });
            }
        }
        catch (Exception ex) { MicFailed(ex); }
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
        await LoadVoiceQuota();
    }

    /// The allowance, refreshed whenever the settings are — saving can
    /// change the provider, and with it whether there is a balance at all.
    /// A deployment on the device's own voice, or on a provider that
    /// publishes none, answers 503; the line is then absent rather than
    /// red, because having no allowance is not a failure to report one.
    private async Task LoadVoiceQuota()
    {
        try
        {
            var q = await ApiClient.Shared.VoiceQuota();
            VsQuota.Text = L10n.T(q.Exhausted ? "ns.vs.spent" : "ns.vs.left")
                .Replace("{left}", q.Left.ToString())
                .Replace("{limit}", q.Limit.ToString());
            VsQuota.Foreground = (Microsoft.UI.Xaml.Media.Brush)
                Application.Current.Resources[
                    q.Exhausted ? "JimAmberBrush" : "JimT2Brush"];
            VsQuota.Visibility = Visibility.Visible;
        }
        catch { VsQuota.Visibility = Visibility.Collapsed; }
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
            await LoadVoiceQuota();
            // And whether what was saved is a key at all. Saving used to
            // report only that the string had been written down; a key the
            // service refuses looked identical to one it accepts until
            // somebody asked to be spoken to.
            try
            {
                var check = await ApiClient.Shared.CheckVoiceKey();
                if (!check.Ok)
                {
                    VsError.Text = L10n.T($"ns.vs.{check.Verdict}");
                    VsError.Visibility = Visibility.Visible;
                }
            }
            catch { /* 503: nothing here to check */ }
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
    // -- the wrist and the doorway -------------------------------------------
    // The drip channel's setup card and the paired embodiments. Console
    // doors since 0.6.0 / 0.19.x; these are the desktop's.

    private WatchSetup? _watch;
    private string _deviceKind = "speaker";

    private void LocalizeWristCards()
    {
        WtHead.Text = L10n.T("ns.wt.title");
        WtLead.Text = L10n.T("ns.wt.lead");
        WtAddressLabel.Text = L10n.T("ns.wt.address");
        WtStepsButton.Content = L10n.T("ns.wt.setup");
        WtRotateButton.Content = L10n.T("ns.bas.reset");
        WtSeedButton.Content = L10n.T("ns.wt.seed");
        WtDripBox.PlaceholderText = L10n.T("ns.wt.drip.ph");
        WtDripButton.Content = L10n.T("ns.wt.drip.now");
        DvHead.Text = L10n.T("ns.dv.bluetooth");
        DvPaired.Content = L10n.T("ns.dv.paired");
        DvAddButton.Content = L10n.T("ns.dv.bluetooth");
        SitHead.Text = L10n.T("att.sit");
        SitStartButton.Content = L10n.T("att.sit.start");
        SitEndButton.Content = L10n.T("att.sit.end");
    }

    private async Task LoadWatch()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try { RenderWatch(await ApiClient.Shared.WatchSetup(s.Uid, s.Token)); }
        catch { /* leave as-is */ }
        try
        {
            var pair = await ApiClient.Shared.PairInfo();
            WtPairHow.Text = string.Join("\n", pair.How);
            WtPairUrl.Text = pair.ConsoleUrl;
            WtPairNote.Text = pair.Note;
            WtPairQr.Text = L10n.T("qr.addr") + " "
                + ApiClient.Shared.PairQrUrl();
        }
        catch { /* leave as-is */ }
    }

    private void RenderWatch(WatchSetup setup)
    {
        WtError.Visibility = Visibility.Collapsed;
        _watch = setup;
        WtAddress.Text = setup.DripUrl;
        WtDrips.Text = $"{setup.Drips} \u00b7 {setup.LastDripAt ?? "\u2014"}";
        WtSeedHint.Text = setup.SeedHint;
        WtDevices.Children.Clear();
        foreach (var device in setup.Devices)
        {
            var key = device.Key;
            var chip = new Microsoft.UI.Xaml.Controls.Primitives.ToggleButton
            {
                Content = device.Name,
                FontSize = 11,
                IsChecked = setup.Device == key,
            };
            chip.Click += async (_, _) =>
            {
                var st = AppState.Current;
                try
                {
                    RenderWatch(await ApiClient.Shared.WatchSetup(
                        st.Uid!, st.Token!, key));
                }
                catch (Exception ex) { ShowWatchError(ex); }
            };
            WtDevices.Children.Add(chip);
        }
        WtSteps.Children.Clear();
        for (var i = 0; i < setup.Steps.Length; i++)
            WtSteps.Children.Add(new TextBlock
            {
                Text = $"{i + 1}. {setup.Steps[i]}",
                FontSize = 11,
                TextWrapping = TextWrapping.Wrap,
                Foreground = (Microsoft.UI.Xaml.Media.Brush)
                    Application.Current.Resources["JimT2Brush"],
            });
    }

    private void ShowWatchError(Exception ex)
    {
        WtError.Text = ex.Message;
        WtError.Visibility = Visibility.Visible;
    }

    private void OnWatchSteps(object sender, RoutedEventArgs e) =>
        WtSteps.Visibility = WtSteps.Visibility == Visibility.Visible
            ? Visibility.Collapsed : Visibility.Visible;

    /// Rotating invalidates the old drip token.
    private async void OnWatchRotate(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            RenderWatch(await ApiClient.Shared.RotateWatchChannel(
                s.Uid, s.Token));
        }
        catch (Exception ex) { ShowWatchError(ex); }
    }

    private async void OnWatchSeed(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var picker = new Windows.Storage.Pickers.FileOpenPicker();
        WinRT.Interop.InitializeWithWindow.Initialize(picker,
            WinRT.Interop.WindowNative.GetWindowHandle(App.MainAppWindow));
        picker.FileTypeFilter.Add(".zip");
        picker.FileTypeFilter.Add(".xml");
        var file = await picker.PickSingleFileAsync();
        if (file is null) return;
        try
        {
            var buffer = await Windows.Storage.FileIO.ReadBufferAsync(file);
            await ApiClient.Shared.SeedWatch(s.Uid, s.Token,
                                             buffer.ToArray());
        }
        catch (Exception ex) { ShowWatchError(ex); }
    }

    private async Task LoadDevices()
    {
        // The server's DeviceRegister kinds, shown in its own words like
        // the mic types are.
        if (DvKinds.Children.Count == 0)
        {
            var kinds = new[] { "wearable", "stationary", "autonomous",
                                "speaker", "phone", "glasses", "headset",
                                "spatial", "other" };
            StackPanel row = NewKindRow();
            foreach (var kind in kinds)
            {
                if (row.Children.Count == 3)
                {
                    DvKinds.Children.Add(row);
                    row = NewKindRow();
                }
                var chosen = kind;
                var chip = new Microsoft.UI.Xaml.Controls.Primitives.ToggleButton
                { Content = chosen, FontSize = 11,
                  IsChecked = _deviceKind == chosen };
                chip.Click += (_, _) =>
                {
                    _deviceKind = chosen;
                    foreach (var r in DvKinds.Children)
                        foreach (var c in ((StackPanel)r).Children)
                            ((Microsoft.UI.Xaml.Controls.Primitives.ToggleButton)c)
                                .IsChecked =
                                (string)((Microsoft.UI.Xaml.Controls.Primitives.ToggleButton)c).Content
                                == chosen;
                };
                row.Children.Add(chip);
            }
            if (row.Children.Count > 0) DvKinds.Children.Add(row);
        }
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var rows = await ApiClient.Shared.Devices(s.Uid, s.Token);
            DvRows.Children.Clear();
            foreach (var row in rows)
                DvRows.Children.Add(new TextBlock
                {
                    Text = $"{row.Name} \u00b7 {row.Kind}"
                        + (row.Paired ? " \u00b7 " + L10n.T("ns.dv.paired")
                                      : ""),
                    FontSize = 11,
                    TextWrapping = TextWrapping.Wrap,
                    Foreground = (Microsoft.UI.Xaml.Media.Brush)
                        Application.Current.Resources["JimTxtBrush"],
                });
        }
        catch { /* leave as-is */ }
    }

    private static StackPanel NewKindRow() => new()
    { Orientation = Orientation.Horizontal, Spacing = 6 };

    private async void OnDeviceAdd(object sender, RoutedEventArgs e)
    {
        var name = DvName.Text.Trim();
        if (name.Length == 0) return;
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            await ApiClient.Shared.RegisterDevice(s.Uid, s.Token, name,
                _deviceKind, DvPaired.IsChecked == true);
            DvName.Text = "";
            await LoadDevices();
        }
        catch (Exception ex)
        {
            DvError.Text = ex.Message;
            DvError.Visibility = Visibility.Visible;
        }
    }


    // ---- the beacon on a social presence, and the way out of one ----

    private async void OnSocialBeacon(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string cid) return;
        var s = AppState.Current;
        if (s.Token is null) return;
        try
        {
            var beacon = await ApiClient.Shared.SocialBeacon(cid, s.Token);
            ShowSocialStatus($"{beacon.Handle} → {beacon.PresenceUrl}");
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    private async void OnSocialDisconnect(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string cid) return;
        var s = AppState.Current;
        if (s.Token is null) return;
        try
        {
            await ApiClient.Shared.DisconnectSocial(cid, s.Token);
            await ReloadSocial();
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    // ---- this sitting: a named login session ----

    private SessionStarted? _sitting;

    private async void OnSitStart(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        SitError.Visibility = Visibility.Collapsed;
        try
        {
            _sitting = await ApiClient.Shared.StartSession(s.Uid, s.Token,
                                                           "windows");
            SitEndButton.IsEnabled = true;
            SitLine.Text = L10n.T("att.sit.prior")
                .Replace("{id}", _sitting.Id)
                .Replace("{n}", _sitting.PriorSessions.ToString());
            SitLine.Visibility = Visibility.Visible;
            SitMemory.Text = _sitting.Memory ?? "";
            SitMemory.Visibility = _sitting.Memory is null
                ? Visibility.Collapsed : Visibility.Visible;
            SitTurns.Children.Clear();
            if (_sitting.Continuity is { } continuity)
            {
                foreach (var turn in continuity.RecentTurns)
                    SitTurns.Children.Add(new TextBlock
                    {
                        Text = $"{turn.Role}: {turn.Content}",
                        FontSize = 10,
                        TextWrapping = TextWrapping.Wrap,
                        Foreground = (Microsoft.UI.Xaml.Media.Brush)
                            Application.Current.Resources["JimT2Brush"],
                    });
                SitNote.Text = continuity.Note;
                SitNote.Visibility = Visibility.Visible;
            }
            else SitNote.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex)
        {
            SitError.Text = ex.Message;
            SitError.Visibility = Visibility.Visible;
        }
    }

    private async void OnSitEnd(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _sitting is null) return;
        SitError.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.EndSession(s.Uid, s.Token, _sitting.Id);
            _sitting = null;
            SitEndButton.IsEnabled = false;
            SitLine.Visibility = Visibility.Collapsed;
            SitMemory.Visibility = Visibility.Collapsed;
            SitNote.Visibility = Visibility.Collapsed;
            SitTurns.Children.Clear();
        }
        catch (Exception ex)
        {
            SitError.Text = ex.Message;
            SitError.Visibility = Visibility.Visible;
        }
    }
}
