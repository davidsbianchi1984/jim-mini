using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace JimGuardian.Views;

/// The one QRME profile that is this person.
///
/// Every other tandem surface in this shell reaches somebody else's profile.
/// This reaches their own — the `self` profile that speaks *as* them, and that
/// answers strangers. Built around the preview rather than the switches,
/// because the switches are not the decision: docs/tandem.md says what may
/// cross, and this shows exactly what would before it does.
public sealed partial class SelfProfilePage : Page
{
    private static readonly string[] Categories =
        { "language", "wellbeing", "conditions", "medication", "continuity" };

    private SelfProfileStatus? _status;
    private SelfProfilePreview? _preview;

    public SelfProfilePage()
    {
        InitializeComponent();
        TitleText.Text = L10n.T("self.title");
        LeadText.Text = L10n.T("self.lead");
        LinkHeading.Text = L10n.T("self.link");
        PasteText.Text = L10n.T("self.paste");
        ProfileIdBox.PlaceholderText = L10n.T("self.profile_id");
        OwnerTokenBox.PlaceholderText = L10n.T("self.owner_token");
        LinkButton.Content = L10n.T("self.link_button");
        MayKnowHeading.Text = L10n.T("self.may_know");
        UntilTickText.Text = L10n.T("self.until_tick");
        ExactlyHeading.Text = L10n.T("self.exactly");
        MessageItselfText.Text = L10n.T("self.message_itself");
        SendButton.Content = L10n.T("self.send");
        StopHeading.Text = L10n.T("self.stop");
        UnlinkNoteText.Text = L10n.T("self.unlink_note");
        UnlinkButton.Content = L10n.T("self.unlink");
        ContTitle.Text = L10n.T("cont.title");
        ContForget.Content = L10n.T("cont.forget");
        Loaded += async (_, _) => { await LoadContinuity(); await Refresh(); };
    }

    /// What the Guardian carries between sessions.
    ///
    /// Its own try/catch and its own load: the vector answers a different
    /// question from the tandem link above it, and a QRME profile that cannot
    /// be reached must not blank this card.
    private async System.Threading.Tasks.Task LoadContinuity()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var c = await ApiClient.Shared.Continuity(s.Uid, s.Token);
            ContCarries.Text = c.Carries;
            if (!c.Built || c.Vector is null)
            {
                ContCount.Text = "";
                ContForget.Visibility = Visibility.Collapsed;
                ContState.Text = c.Note ?? L10n.T("cont.nothing");
                ContDims.Text = "";
                return;
            }
            ContCount.Text = $"{c.Observations} " + L10n.T("cont.observations");
            ContForget.Visibility = Visibility.Visible;
            ContState.Text = c.Conditioning
                ? L10n.T("cont.shaping") : L10n.T("cont.not_yet");
            ContDims.Text = string.Join("\n", c.Vector.OrderBy(kv => kv.Key)
                .Select(kv => $"{kv.Key}: {(int)(kv.Value * 100)}%"
                              + (c.Meanings is not null
                                 && c.Meanings.TryGetValue(kv.Key, out var m)
                                 ? $" \u2014 {m}" : "")));
        }
        catch (Exception) { ContState.Text = L10n.T("cont.nothing"); }
    }

    private async void OnForgetContinuity(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try { await ApiClient.Shared.ForgetContinuity(s.Uid, s.Token); }
        catch (Exception) { }
        await LoadContinuity();
    }

    private async System.Threading.Tasks.Task Refresh()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            _status = await ApiClient.Shared.SelfProfile(s.Uid, s.Token);
            _preview = await ApiClient.Shared.PreviewSelfProfile(s.Uid, s.Token);
        }
        catch (Exception e) { Say(e.Message); return; }

        var linked = _status?.Linked == true;
        LinkPanel.Visibility = linked ? Visibility.Collapsed : Visibility.Visible;
        ConsentPanel.Visibility = linked ? Visibility.Visible : Visibility.Collapsed;
        if (!linked) return;

        CategoryList.Children.Clear();
        foreach (var key in Categories)
        {
            var box = new CheckBox
            {
                Content = key,
                IsChecked = _status?.Consented?.Contains(key) == true,
            };
            var captured = key;
            box.Click += async (_, _) => await SetConsent(captured, box.IsChecked == true);
            CategoryList.Children.Add(box);
        }
        BriefText.Text = _preview?.Empty == true
            ? L10n.T("self.nothing_ticked")
            : string.Join(" · ", _preview?.Consented ?? Array.Empty<string>());
        SendButton.IsEnabled = _preview?.Empty != true;
    }

    private void Say(string message)
    {
        NoteText.Text = message;
        NoteText.Visibility = Visibility.Visible;
    }

    private async void OnLink(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            await ApiClient.Shared.LinkSelfProfile(s.Uid, s.Token,
                ProfileIdBox.Text.Trim(), OwnerTokenBox.Password.Trim());
            Say(L10n.T("self.linked_note"));
        }
        catch (Exception ex) { Say(ex.Message); }
        await Refresh();
    }

    private async System.Threading.Tasks.Task SetConsent(string key, bool on)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        var next = (_status?.Consented ?? Array.Empty<string>()).ToList();
        if (on) { if (!next.Contains(key)) next.Add(key); } else next.Remove(key);
        try
        {
            await ApiClient.Shared.ConsentSelfProfile(s.Uid, s.Token, next.ToArray());
            Say(L10n.T("self.saved"));
        }
        catch (Exception ex) { Say(ex.Message); }
        await Refresh();
    }

    private async void OnBrief(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            await ApiClient.Shared.BriefSelfProfile(s.Uid, s.Token);
            Say(L10n.T("self.sent"));
        }
        catch (Exception ex) { Say(ex.Message); }
        await Refresh();
    }

    private async void OnUnlink(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            await ApiClient.Shared.UnlinkSelfProfile(s.Uid, s.Token);
            Say(L10n.T("self.unlinked"));
        }
        catch (Exception ex) { Say(ex.Message); }
        await Refresh();
    }
}
