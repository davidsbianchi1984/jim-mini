using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Navigation;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Runtime.InteropServices.WindowsRuntime;

namespace JimGuardian.Views;

public sealed partial class MonitorPage : Page
{
    public sealed class LiveOptionVm
    {
        public string Who { get; init; } = "";
        public string Channel { get; init; } = "";
        public string Note { get; init; } = "";
    }

    public MonitorPage()
    {
        InitializeComponent();
        Title.Text = L10n.T("mon");
        Sub.Text = L10n.T("mon.sub");
        HeartRate.Header = L10n.T("mon.hr");
        Stress.Header = L10n.T("mon.stress");
        SendButton.Content = L10n.T("mon.send");
        FollowupNote.PlaceholderText = L10n.T("mon.add");
        HelpedButton.Content = L10n.T("mon.helped");
        DidNotButton.Content = L10n.T("mon.didnot");
        CapHead.Text = L10n.T("ns.ch.cam");
        CapFor.Text = L10n.T("ns.ch.cam.for");
        CapSite.Header = L10n.T("ns.ch.cam.site");
        CapNote.PlaceholderText = L10n.T("ns.ch.cam.note");
        CapConsent.Header = L10n.T("ns.ch.cam.consent");
        CapPickButton.Content = L10n.T("ns.ch.cam.attach");
        BandHead.Text = L10n.T("ns.bas.title");
        BandSub.Text = L10n.T("ns.bas.sub");
        BandNone.Text = L10n.T("ns.bas.none");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        await LoadFollowups();
        await LoadCaptures();
        await LoadBands();
    }

    // MARK: [0039] — the effectiveness loop

    /// <summary>
    /// Ask about guidance that is still waiting on an answer, whether it went
    /// out in this session or an earlier one — a question the app drops is a
    /// question nobody ever answers.
    /// </summary>
    private async System.Threading.Tasks.Task LoadFollowups()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var state = await ApiClient.Shared.Followups(s.Uid, s.Token);
            var open = state.Open.FirstOrDefault();
            if (open is null)
            {
                FollowupCard.Visibility = Visibility.Collapsed;
                return;
            }
            FollowupQuestion.Text = open.Question;
            FollowupAbout.Text = $"About the guidance for {open.Condition}.";
            FollowupCard.Visibility = Visibility.Visible;
        }
        catch (Exception) { FollowupCard.Visibility = Visibility.Collapsed; }
    }

    private async void OnFollowupHelped(object sender, RoutedEventArgs e) =>
        await Answer(true);

    private async void OnFollowupDidNot(object sender, RoutedEventArgs e) =>
        await Answer(false);

    /// "It did not" is not a complaint filed away: the ladder runs again and the
    /// people who can help are named.
    private async System.Threading.Tasks.Task Answer(bool helped)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var a = await ApiClient.Shared.AnswerFollowup(
                s.Uid, s.Token, helped, FollowupNote.Text);
            FollowupNote.Text = "";

            AnsweredTitle.Text = a.Helped == true
                ? "Monitoring resumes" : "Bringing in a person";
            AnsweredTitle.Foreground = new SolidColorBrush(a.Helped == true
                ? Microsoft.UI.Colors.MediumSpringGreen
                : Microsoft.UI.Colors.Orange);
            AnsweredNext.Text = a.Next ?? a.Reason ?? "";

            LiveOptions.ItemsSource = (a.Live?.Options ?? Array.Empty<LiveOption>())
                .Select(o => new LiveOptionVm
                {
                    Who = string.IsNullOrEmpty(o.Name)
                        ? o.Kind.Replace('_', ' ') : o.Name!,
                    Channel = o.Channel ?? "",
                    Note = o.Note ?? "",
                }).ToList();
            LiveNote.Text = a.Live?.Note ?? "";
            AnsweredCard.Visibility = Visibility.Visible;

            await LoadFollowups();
        }
        catch (Exception) { /* the send path already surfaces errors */ }
    }

    private async void OnSend(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        SendButton.IsEnabled = false;
        try
        {
            var r = await ApiClient.Shared.Monitor(s.Uid!, s.Token!,
                (int)HeartRate.Value, Stress.Value / 100.0);

            ResultTitle.Text = r.Detected
                ? Cap(r.Condition ?? "Detected")
                : "All clear";
            ResultTitle.Foreground = new SolidColorBrush(
                r.Detected ? Microsoft.UI.Colors.OrangeRed : Microsoft.UI.Colors.MediumSpringGreen);

            ResultReason.Text = r.Reason ?? "";
            ResultReason.Visibility = string.IsNullOrEmpty(r.Reason) ? Visibility.Collapsed : Visibility.Visible;

            ResultGuidance.Text = r.Guidance?.Content ?? "";
            ResultGuidance.Visibility = r.Guidance is null ? Visibility.Collapsed : Visibility.Visible;

            ResultSpecialist.Text = FormatSpecialist(r.Guidance);
            ResultSpecialist.Visibility = ResultSpecialist.Text.Length > 0
                ? Visibility.Visible : Visibility.Collapsed;

            var aid = r.Guidance?.FirstAidPlaybook;
            if (aid is not null)
            {
                var header = $"First aid — {aid.Kind.ToUpper()}" +
                             (aid.CallEmergencyServices == true
                                  ? "  ·  📞 call emergency services now" : "");
                var steps = string.Join("\n", aid.Steps.Select(
                    (step, i) => $"{i + 1}. {step}"));
                ResultFirstAid.Text = $"{header}\n{steps}";
                ResultFirstAid.Visibility = Visibility.Visible;
                if (aid.Pace is { } pace)
                {
                    ResultPace.Text =
                        $"Pace: {pace.CompressionsPerMinute}/min · " +
                        $"{pace.CompressionToBreathRatio}" +
                        (pace.Cue is { } cue
                             ? $"\n💡 {cue.Light}\n🔊 {cue.Audio}" : "");
                    ResultPace.Visibility = Visibility.Visible;
                }
                else ResultPace.Visibility = Visibility.Collapsed;
            }
            else
            {
                ResultFirstAid.Visibility = Visibility.Collapsed;
                ResultPace.Visibility = Visibility.Collapsed;
            }

            var refs = r.Guidance?.References;
            if (refs is { Length: > 0 })
            {
                ResultRefs.Text = string.Join("\n", refs.Select(x => $"→ {x}"));
                ResultRefs.Visibility = Visibility.Visible;
            }
            else ResultRefs.Visibility = Visibility.Collapsed;

            ResultProvenance.Text = FormatProvenance(r.Guidance);
            ResultProvenance.Visibility = ResultProvenance.Text.Length > 0
                ? Visibility.Visible : Visibility.Collapsed;

            ResultCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ResultTitle.Text = L10n.T("mon.error");
            ResultReason.Text = ex.Message;
            ResultReason.Visibility = Visibility.Visible;
            ResultGuidance.Visibility = Visibility.Collapsed;
            ResultCard.Visibility = Visibility.Visible;
        }
        finally
        {
            SendButton.IsEnabled = true;
        }
    }

    /// The named expert standing behind this condition, plus a live badge
    /// when guidance was routed in tandem through a QRME synthetic persona.
    internal static string FormatSpecialist(Guidance? g)
    {
        if (g?.Specialist is not { } who) return "";
        return g.Source == "tandem" ? $"{who}  ·  LIVE VIA QRME" : who;
    }

    /// The verifiable basis of the advice: publishers, documents, URLs, and
    /// how/by what the text was produced — shared by Monitor and Coach.
    internal static string FormatProvenance(Guidance? g)
    {
        if (g is null) return "";
        var lines = new System.Collections.Generic.List<string>();
        if (g.TranslationNote is { } tn) lines.Add($"🌐 {tn}");
        if (g.ProvenanceInfo is { } p)
        {
            lines.Add("Derived from:");
            foreach (var e in p.EvidenceList)
            {
                lines.Add($"  {e.Publisher} — {e.Title}" +
                          (e.Supports is { } sup ? $" (supports: {sup})" : ""));
                lines.Add($"  {e.Url}");
            }
            lines.Add($"{p.Method} · generated by {p.GeneratedBy}");
            lines.Add(p.Disclaimer);
        }
        if (g.CustodyInfo is { } c)
            lines.Add(c.Vaulted && c.PdiKey is { } key
                ? $"🔒 Sealed in the PDI vault — {key}"
                : $"⚠️ {c.Note}");
        return string.Join("\n", lines);
    }

    private static string Cap(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..];
    // -- clinical captures ------------------------------------------------

    public sealed class CaptureVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string Note { get; init; } = "";
        public string ShowLabel { get; init; } = "";
        public string AttachLabel { get; init; } = "";
        public string WithdrawLabel { get; init; } = "";
    }

    private CaptureVocabulary? _vocabulary;
    private Dictionary<string, string> _siteByLabel = new();

    private async Task LoadCaptures()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            _vocabulary ??= await ApiClient.Shared.CaptureVocabulary();
            if (CapSite.Items.Count == 0)
            {
                _siteByLabel = _vocabulary.Sites
                    .ToDictionary(kv => kv.Value, kv => kv.Key);
                CapSite.ItemsSource = _vocabulary.Sites.Values
                    .OrderBy(v => v).ToList();
                CapSite.SelectedIndex = 0;
                CapSite.SelectionChanged += (_, _) => RefreshConsentVisibility();
                RefreshConsentVisibility();
            }
            var rows = await ApiClient.Shared.Captures(s.Uid, s.Token);
            // An intimate site is marked in words on the row itself.
            CapRows.ItemsSource = rows.Take(6).Select(r => new CaptureVm
            {
                Id = r.Id,
                Title = (_vocabulary.Sites.TryGetValue(r.Site, out var label)
                            ? label : r.Site)
                        + (r.Intimate ? " · " + L10n.T("ns.ch.cam.intimate") : ""),
                Note = r.Note ?? "",
                ShowLabel = L10n.T("ns.ch.cam.where"),
                // A referral releases only what is chosen by name, and this
                // button is the choosing — never done silently.
                AttachLabel = L10n.T("ns.ch.cam.tick"),
                WithdrawLabel = L10n.T("ns.ch.cam.withdraw"),
            }).ToList();
        }
        catch (Exception e) { CaptureError(e); }
    }

    private string? SelectedSite() =>
        CapSite.SelectedItem is string label
        && _siteByLabel.TryGetValue(label, out var site) ? site : null;

    private void RefreshConsentVisibility()
    {
        var site = SelectedSite();
        CapConsent.Visibility =
            site is not null && _vocabulary?.Intimate.Contains(site) == true
                ? Visibility.Visible : Visibility.Collapsed;
    }

    private void CaptureError(Exception e)
    {
        CapError.Text = e.Message;
        CapError.Visibility = Visibility.Visible;
    }

    private async void OnPickCapture(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var site = SelectedSite();
        if (s.Uid is null || s.Token is null || site is null) return;
        if (CapConsent.Visibility == Visibility.Visible && !CapConsent.IsOn) return;
        CapError.Visibility = Visibility.Collapsed;
        try
        {
            var picker = new Windows.Storage.Pickers.FileOpenPicker();
            picker.FileTypeFilter.Add(".jpg");
            picker.FileTypeFilter.Add(".jpeg");
            picker.FileTypeFilter.Add(".png");
            // WinUI 3 desktop: the picker has no window of its own.
            var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainAppWindow);
            WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);
            var file = await picker.PickSingleFileAsync();
            if (file is null) return;
            var buffer = await Windows.Storage.FileIO.ReadBufferAsync(file);
            var bytes = new byte[buffer.Length];
            using (var reader = Windows.Storage.Streams.DataReader.FromBuffer(buffer))
                reader.ReadBytes(bytes);
            await ApiClient.Shared.TakeCapture(s.Uid, s.Token, site,
                Convert.ToBase64String(bytes), CapNote.Text.Trim(),
                CapConsent.IsOn);
            CapNote.Text = "";
            await LoadCaptures();
        }
        catch (Exception ex) { CaptureError(ex); }
    }

    private async void OnShowCapture(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        if ((sender as FrameworkElement)?.Tag is not string id) return;
        try
        {
            var image = await ApiClient.Shared.CaptureImage(s.Uid, s.Token, id);
            var bytes = Convert.FromBase64String(image.Content);
            var bmp = new Microsoft.UI.Xaml.Media.Imaging.BitmapImage();
            using (var stream = new Windows.Storage.Streams.InMemoryRandomAccessStream())
            {
                await stream.WriteAsync(bytes.AsBuffer());
                stream.Seek(0);
                await bmp.SetSourceAsync(stream);
            }
            CapImage.Source = bmp;
            CapImage.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { CaptureError(ex); }
    }

    private async void OnAttachCapture(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        if ((sender as FrameworkElement)?.Tag is not string id) return;
        try { await ApiClient.Shared.AttachCaptures(s.Uid, s.Token, new[] { id }); }
        catch (Exception ex) { CaptureError(ex); }
    }

    private async void OnWithdrawCapture(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        if ((sender as FrameworkElement)?.Tag is not string id) return;
        try
        {
            await ApiClient.Shared.WithdrawCapture(s.Uid, s.Token, id);
            await LoadCaptures();
        }
        catch (Exception ex) { CaptureError(ex); }
    }
    // -- baseline bands (console door since 0.6.0; this is the desktop's) --
    //
    // Your normal, and how far from it counts. Crossing a band is a
    // check-in, never an escalation; the alarm layer lives elsewhere.

    private async Task LoadBands()
    {
        var s = AppState.Current;
        try { RenderBands((await ApiClient.Shared.Bands(s.Uid!, s.Token!)).Bands); }
        catch { /* leave as-is */ }
    }

    private void RenderBands(BandRow[] bands)
    {
        BandError.Visibility = Visibility.Collapsed;
        BandNone.Visibility = bands.Length == 0 ? Visibility.Visible
                                                : Visibility.Collapsed;
        BandRows.Children.Clear();
        foreach (var band in bands)
        {
            var metric = band.Metric;
            var step = band.Unit == "\u00b0C" ? 0.1 : 0.5;
            var row = new StackPanel { Spacing = 2 };
            var head = new StackPanel
            { Orientation = Orientation.Horizontal, Spacing = 8 };
            head.Children.Add(new TextBlock
            {
                Text = band.Label,
                FontWeight = Microsoft.UI.Text.FontWeights.Bold,
                FontSize = 12,
                Foreground = (Brush)Application.Current.Resources["JimTxtBrush"],
            });
            head.Children.Add(BandText(
                $"\u00b1{band.Margin}{band.Unit}", "JimT2Brush"));
            row.Children.Add(head);
            row.Children.Add(BandText(band.Provisional
                ? L10n.T("ns.bas.learning")
                    .Replace("{n}", band.Samples.ToString())
                : L10n.T("ns.bas.usual")
                    .Replace("{v}", $"{band.Baseline}{band.Unit}")
                    .Replace("{lo}", $"{band.LowEdge}{band.Unit}")
                    .Replace("{hi}", $"{band.HighEdge}{band.Unit}"),
                band.Provisional ? "JimT3Brush" : "JimT2Brush"));

            var actions = new StackPanel
            { Orientation = Orientation.Horizontal, Spacing = 6 };
            // Narrower is told sooner; wider tolerates a wanderer.
            var narrow = new Button { Content = "\u2212", FontSize = 11 };
            narrow.Click += (_, _) =>
            {
                if (band.Margin - step > 0)
                    ChangeBand(metric, band.Margin - step, null, null);
            };
            var widen = new Button { Content = "+", FontSize = 11 };
            widen.Click += (_, _) =>
                ChangeBand(metric, band.Margin + step, null, null);
            actions.Children.Add(narrow);
            actions.Children.Add(widen);
            var drop = new Microsoft.UI.Xaml.Controls.Primitives.ToggleButton
            {
                Content = L10n.T("ns.bas.drop"),
                FontSize = 11,
                IsChecked = band.WatchLow,
            };
            drop.Click += (_, _) =>
                ChangeBand(metric, null, null, !band.WatchLow);
            var climb = new Microsoft.UI.Xaml.Controls.Primitives.ToggleButton
            {
                Content = L10n.T("ns.bas.climb"),
                FontSize = 11,
                IsChecked = band.WatchHigh,
            };
            climb.Click += (_, _) =>
                ChangeBand(metric, null, !band.WatchHigh, null);
            actions.Children.Add(drop);
            actions.Children.Add(climb);
            if (band.Source == "user")
            {
                var reset = new Button
                { Content = L10n.T("ns.bas.reset"), FontSize = 11 };
                reset.Click += async (_, _) =>
                {
                    var st = AppState.Current;
                    try
                    {
                        await ApiClient.Shared.ResetBand(st.Uid!, st.Token!,
                                                         metric);
                        await LoadBands();
                    }
                    catch (Exception ex) { ShowBandError(ex); }
                };
                actions.Children.Add(reset);
            }
            row.Children.Add(actions);
            BandRows.Children.Add(row);
        }
    }

    private static TextBlock BandText(string text, string brush) => new()
    {
        Text = text,
        FontSize = 11,
        TextWrapping = TextWrapping.Wrap,
        Foreground = (Brush)Application.Current.Resources[brush],
    };

    private void ShowBandError(Exception ex)
    {
        BandError.Text = ex.Message;
        BandError.Visibility = Visibility.Visible;
    }

    private async void ChangeBand(string metric, double? margin,
                                  bool? watchHigh, bool? watchLow)
    {
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.SetBand(s.Uid!, s.Token!, metric, margin,
                                           watchHigh, watchLow);
            await LoadBands();
        }
        catch (Exception ex) { ShowBandError(ex); }
    }
}
