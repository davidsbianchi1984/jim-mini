using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

/// <summary>
/// The Guardian you leave running.
///
/// <para><see cref="CoachPage"/> is a turn: you ask, it answers, nothing is
/// left holding. This is a session — open until sign-off, able to act on this
/// person's own records while it is open, and every act on a trail they can
/// take back.</para>
///
/// <para>Three things this page owes a person that the backend cannot: the
/// reach renders <em>above</em> Engage rather than behind a disclosure,
/// because a list of what a thing may do to you is not a detail view; an act
/// is never drawn as reversible when it is not, because "already undone" and
/// "left the app" are a real third state; and the sign-off card carries the
/// topics field before its button, because the whole promise is that leaving
/// does not mean being unwatched.</para>
/// </summary>
public sealed partial class EngagedPage : Page
{
    private EngagedSession? _session;
    private bool _busy;

    public EngagedPage()
    {
        InitializeComponent();
        // In code rather than XAML: a XAML literal cannot be re-read when the
        // language changes.
        Title.Text = L10n.T("eng.title");
        Pitch.Text = L10n.T("eng.pitch");
        ReachHead.Text = L10n.T("eng.reach");
        ReachNote.Text = L10n.T("eng.reach.note");
        EngageButton.Content = L10n.T("eng.open");
        SayBox.Header = L10n.T("eng.say");
        SayBox.PlaceholderText = L10n.T("eng.say.ph");
        SayButton.Content = L10n.T("eng.say");
        OfflineNote.Text = L10n.T("eng.offline");
        TrailHead.Text = L10n.T("eng.trail");
        TrailNote.Text = L10n.T("eng.trail.note");
        SignOffHead.Text = L10n.T("eng.off");
        SignOffNote.Text = L10n.T("eng.off.note");
        TopicsBox.PlaceholderText = L10n.T("eng.off.ph");
        SignOffButton.Content = L10n.T("eng.off");
        WatchHead.Text = L10n.T("eng.watch");
        WatchNote.Text = L10n.T("eng.watch.note");
        WatchBox.PlaceholderText = L10n.T("eng.watch.ph");
        WatchButton.Content = L10n.T("eng.open");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e) => await Load();

    private async System.Threading.Tasks.Task Load()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            var reach = await ApiClient.Shared.EngagedReach();
            ReachList.Children.Clear();
            foreach (var tool in reach.Can)
            {
                var line = tool.Acts ? L10n.T("eng.acts") : L10n.T("eng.reads");
                var row = new TextBlock
                {
                    Text = $"{line} · {tool.Says}"
                           + (tool.IrreversibleBecause is null
                              ? "" : $" — {L10n.T("eng.forever")}"),
                    FontSize = 12,
                    TextWrapping = TextWrapping.Wrap,
                };
                ReachList.Children.Add(row);
            }

            _session = await ApiClient.Shared.Engaged(s.Uid, s.Token);
            var open = _session.Engaged;
            SessionHead.Text = open ? L10n.T("eng.title") : L10n.T("eng.none");
            SessionNote.Text = open ? L10n.T("eng.pitch") : L10n.T("eng.none.note");
            EngageButton.Visibility = open ? Visibility.Collapsed : Visibility.Visible;
            SayBox.Visibility = open ? Visibility.Visible : Visibility.Collapsed;
            SayButton.Visibility = open ? Visibility.Visible : Visibility.Collapsed;
            SignOffCard.Visibility = open ? Visibility.Visible : Visibility.Collapsed;

            Transcript.Children.Clear();
            Transcript.Visibility = open ? Visibility.Visible : Visibility.Collapsed;
            foreach (var turn in _session.Turns)
            {
                Transcript.Children.Add(new TextBlock
                {
                    Text = (turn.Role == "user" ? L10n.T("eng.you") : L10n.T("eng.jim"))
                           + ": " + turn.Content,
                    FontSize = 13,
                    TextWrapping = TextWrapping.Wrap,
                });
            }

            TrailList.Children.Clear();
            var acts = await ApiClient.Shared.EngagedActs(s.Uid, s.Token);
            if (acts.Length == 0)
                TrailList.Children.Add(new TextBlock
                { Text = L10n.T("eng.trail.none"), FontSize = 12 });
            foreach (var act in acts)
            {
                var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
                row.Children.Add(new TextBlock
                { Text = act.Says, FontSize = 12, TextWrapping = TextWrapping.Wrap });
                if (act.UndoneAt is not null)
                    row.Children.Add(new TextBlock
                    { Text = L10n.T("eng.undone"), FontSize = 12 });
                else if (act.Reversible)
                {
                    var undo = new Button { Content = L10n.T("eng.undo"), Tag = act.Id };
                    undo.Click += OnUndo;
                    row.Children.Add(undo);
                }
                else
                    row.Children.Add(new TextBlock
                    { Text = L10n.T("eng.forever"), FontSize = 12 });
                TrailList.Children.Add(row);
            }

            // From the watch list rather than the session's copy of it: this
            // card shows what is being watched for whether or not anybody is
            // engaged — that is what makes a watch *standing* — and taking it
            // from the session would go stale the moment one closed.
            WatchList.Children.Clear();
            var watching = await ApiClient.Shared.EngagedWatches(s.Uid, s.Token);
            if (watching.Length == 0)
                WatchList.Children.Add(new TextBlock
                { Text = L10n.T("eng.watch.none"), FontSize = 12 });
            foreach (var w in watching)
            {
                var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
                row.Children.Add(new TextBlock
                { Text = w.Topic, FontSize = 12, TextWrapping = TextWrapping.Wrap });
                var stop = new Button { Content = L10n.T("eng.watch.stop"), Tag = w.Id };
                stop.Click += OnStopWatching;
                row.Children.Add(stop);
                WatchList.Children.Add(row);
            }
        }
        catch (Exception ex) { Fail(ex); }
    }

    private void Fail(Exception ex)
    {
        ErrorText.Text = ex.Message;
        ErrorText.Visibility = Visibility.Visible;
    }

    private async void OnEngage(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _busy) return;
        _busy = true;
        try { await ApiClient.Shared.Engage(s.Uid, s.Token); await Load(); }
        catch (Exception ex) { Fail(ex); }
        finally { _busy = false; }
    }

    private async void OnSay(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var message = SayBox.Text.Trim();
        if (s.Uid is null || s.Token is null || _busy || message.Length == 0) return;
        _busy = true;
        try
        {
            var turn = await ApiClient.Shared.EngagedTurn(s.Uid, s.Token, message);
            Steps.Children.Clear();
            Steps.Visibility = turn.Did.Length > 0
                ? Visibility.Visible : Visibility.Collapsed;
            foreach (var step in turn.Did)
            {
                Steps.Children.Add(new TextBlock
                {
                    Text = step.Refused ?? (step.Says ?? step.Tool ?? "")
                           + (step.Acts && !step.Reversible
                              ? $" — {L10n.T("eng.forever")}" : ""),
                    FontSize = 12,
                    TextWrapping = TextWrapping.Wrap,
                });
            }
            // The one stop this page has that the coach does not: the offline
            // model can answer but cannot act, so a turn it served says so
            // rather than handing over canned prose from a surface that acts.
            OfflineNote.Visibility =
                turn.Stopped == "engaged.needs_the_online_model"
                || turn.Provenance.Degraded
                    ? Visibility.Visible : Visibility.Collapsed;
            SayBox.Text = "";
            await Load();
        }
        catch (Exception ex) { Fail(ex); }
        finally { _busy = false; }
    }

    private async void OnUndo(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _busy) return;
        if (sender is not Button b || b.Tag is not string actId) return;
        _busy = true;
        try { await ApiClient.Shared.EngagedUndo(s.Uid, s.Token, actId); await Load(); }
        catch (Exception ex) { Fail(ex); }
        finally { _busy = false; }
    }

    private async void OnSignOff(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _busy) return;
        _busy = true;
        try
        {
            var topics = TopicsBox.Text
                .Split('\n').Select(t => t.Trim())
                .Where(t => t.Length > 0).ToArray();
            await ApiClient.Shared.EngagedSignOff(s.Uid, s.Token, topics);
            TopicsBox.Text = "";
            Steps.Children.Clear();
            OfflineNote.Visibility = Visibility.Collapsed;
            await Load();
        }
        catch (Exception ex) { Fail(ex); }
        finally { _busy = false; }
    }

    private async void OnWatch(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var topic = WatchBox.Text.Trim();
        if (s.Uid is null || s.Token is null || _busy || topic.Length == 0) return;
        _busy = true;
        try
        {
            await ApiClient.Shared.EngagedWatch(s.Uid, s.Token, topic);
            WatchBox.Text = "";
            await Load();
        }
        catch (Exception ex) { Fail(ex); }
        finally { _busy = false; }
    }

    private async void OnStopWatching(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null || _busy) return;
        if (sender is not Button b || b.Tag is not string watchId) return;
        _busy = true;
        try { await ApiClient.Shared.EngagedClearWatch(s.Uid, s.Token, watchId); await Load(); }
        catch (Exception ex) { Fail(ex); }
        finally { _busy = false; }
    }
}
