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
        Loaded += async (_, _) => await Refresh();
    }

    private async System.Threading.Tasks.Task Refresh()
    {
        var s = AppState.Current;
        if (s.UserId is null || s.UserToken is null) return;
        try
        {
            _status = await s.Api.SelfProfile(s.UserId, s.UserToken);
            _preview = await s.Api.PreviewSelfProfile(s.UserId, s.UserToken);
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
        if (s.UserId is null || s.UserToken is null) return;
        try
        {
            await s.Api.LinkSelfProfile(s.UserId, s.UserToken,
                ProfileIdBox.Text.Trim(), OwnerTokenBox.Password.Trim());
            Say(L10n.T("self.linked_note"));
        }
        catch (Exception ex) { Say(ex.Message); }
        await Refresh();
    }

    private async System.Threading.Tasks.Task SetConsent(string key, bool on)
    {
        var s = AppState.Current;
        if (s.UserId is null || s.UserToken is null) return;
        var next = (_status?.Consented ?? Array.Empty<string>()).ToList();
        if (on) { if (!next.Contains(key)) next.Add(key); } else next.Remove(key);
        try
        {
            await s.Api.ConsentSelfProfile(s.UserId, s.UserToken, next.ToArray());
            Say(L10n.T("self.saved"));
        }
        catch (Exception ex) { Say(ex.Message); }
        await Refresh();
    }

    private async void OnBrief(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.UserId is null || s.UserToken is null) return;
        try
        {
            await s.Api.BriefSelfProfile(s.UserId, s.UserToken);
            Say(L10n.T("self.sent"));
        }
        catch (Exception ex) { Say(ex.Message); }
        await Refresh();
    }

    private async void OnUnlink(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.UserId is null || s.UserToken is null) return;
        try
        {
            await s.Api.UnlinkSelfProfile(s.UserId, s.UserToken);
            Say(L10n.T("self.unlinked"));
        }
        catch (Exception ex) { Say(ex.Message); }
        await Refresh();
    }
}
