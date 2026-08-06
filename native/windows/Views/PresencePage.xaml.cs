using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

/// <summary>
/// The presence — the coach that speaks first.
///
/// A companion in the parts worth having: it starts things, it notices
/// without being asked, it reports its own change, and it keeps handing the
/// reader people who are not it.
///
/// Nothing on this page decides anything. Whether it speaks, about what, and
/// why, are the backend's, read from six areas of this person's own history
/// with no model and no second call out — so a machine with no connection
/// still gets its day.
/// </summary>
public sealed partial class PresencePage : Page
{
    private string _slot = "morning";

    public PresencePage()
    {
        InitializeComponent();
        // In code rather than XAML: a XAML literal cannot be re-read when the
        // language changes.
        Title.Text = L10n.T("presence.tab");
        Sub.Text = L10n.T("presence.sub");
        WhatHead.Text = L10n.T("presence.what");
        WillNotHead.Text = L10n.T("presence.will.not");
        TodayHead.Text = L10n.T("presence.today");
        OfflineNote.Text = L10n.T("presence.offline");
        BaselineHead.Text = L10n.T("presence.baseline");
        BearingHead.Text = L10n.T("presence.bearing");
        BearingSameHead.Text = L10n.T("presence.bearing.same");
        // Spelled out rather than "presence.bearing." + choice: a key built
        // from a variable is invisible to the guard that checks every
        // translated row is asked for by something.
        CompanionButton.Content = L10n.T("presence.bearing.companion");
        ProfessionalButton.Content = L10n.T("presence.bearing.professional");
        SurfacesHead.Text = L10n.T("presence.surfaces");
        ReachHead.Text = L10n.T("presence.reach");
        GrowthHead.Text = L10n.T("presence.growth");
        HearButton.Content = L10n.T("presence.tab");
        DeepenButton.Content = L10n.T("presence.deepen");
        ChooseButton.Content = L10n.T("presence.surfaces");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            var who = await ApiClient.Shared.PresenceWho(s.Token!);
            Says.Text = who.Says;
            Boundaries.Text = string.Join("\n",
                (who.Boundaries ?? new()).OrderBy(b => b.Key)
                    .Select(b => b.Value.Says)) + "\n" + who.Note;

            var day = await ApiClient.Shared.PresenceDay(s.Uid!, s.Token!);
            Beats.Text = string.Join("\n\n", (day.Beats ?? Array.Empty<PresenceBeat>())
                .Select(b => b.Slot + " · " + (b.Spoken ?? b.English)
                             // Why it said this. A presence that cannot show
                             // its reason is one nobody can argue with.
                             + "\n" + string.Join("; ", b.Because ?? Array.Empty<string>())));

            var bl = await ApiClient.Shared.PresenceBaseline(s.Uid!, s.Token!);
            Areas.Text = bl.KnownAreas + " / " + bl.Of + "\n" + string.Join("\n",
                (bl.Areas ?? new()).OrderBy(a => a.Key)
                    .Select(a => a.Value.Area + " · " + a.Value.Standing));

            var sf = await ApiClient.Shared.PresenceSurfaces(s.Uid!, s.Token!);
            SurfaceRule.Text = sf.Rule;
            SurfaceRows.Text = string.Join("\n",
                (sf.Surfaces ?? Array.Empty<PresenceSurfaceRow>()).Select(r =>
                    r.Surface + " · " + (r.ReadsHealthAloud
                        ? L10n.T("presence.aloud") : L10n.T("presence.shown"))));

            ShowBearing(await ApiClient.Shared.PresenceBearing(s.Uid!, s.Token!));

            var g = await ApiClient.Shared.PresenceGrowth(s.Uid!, s.Token!);
            Growth.Text = g.BeatsSpoken + " · " + g.AreasSeen + " / " + g.Of
                          + "\n" + g.AboutMyself;
        }
        catch { }

        // A missing tandem is not an error: 409 means the people live in QRME,
        // and an empty shelf says that better than a red banner would.
        try
        {
            var r = await ApiClient.Shared.PresenceReach(s.Uid!, s.Token!);
            Offers.Text = string.Join("\n", (r.Offers ?? Array.Empty<PresenceOffer>())
                .Select(o => o.Who ?? o.Topic ?? o.Kind)) + "\n" + r.Note;
        }
        catch { Offers.Text = ""; }
    }

    /// <summary>`/day` is the plan; asking for a beat is what counts as
    /// having been told, and the backend records it so the same line does not
    /// return tomorrow.</summary>
    private async void OnHear(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            var b = await ApiClient.Shared.PresenceBeat(s.Uid!, s.Token!, _slot);
            Beats.Text = b.Slot + " · " + (b.Spoken ?? b.English);
        }
        catch { }
    }

    private async void OnDeepen(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            var b = await ApiClient.Shared.PresenceDeepen(s.Uid!, s.Token!, _slot);
            Beats.Text = b.Slot + " · " + (b.Spoken ?? b.English);
        }
        catch { }
    }

    /// <summary>The dial. A register, never a capability — so this renders
    /// what stays the same in both bearings next to the buttons that change
    /// it.</summary>
    private void ShowBearing(PresenceBearingView b)
    {
        BearingSays.Text = b.Effect?.Says ?? "";
        BearingSame.Text = string.Join("\n",
            (b.Unchanged ?? new()).OrderBy(kv => kv.Key).Select(kv => kv.Value));
    }

    private async void OnCarryCompanion(object sender, RoutedEventArgs e)
        => await Carry("companion");

    private async void OnCarryProfessional(object sender, RoutedEventArgs e)
        => await Carry("professional");

    private async System.Threading.Tasks.Task Carry(string bearing)
    {
        var s = AppState.Current;
        try
        {
            ShowBearing(await ApiClient.Shared.PresenceSetBearing(
                s.Uid!, s.Token!, bearing));
        }
        catch { }
    }

    private async void OnChooseSurface(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            var sf = await ApiClient.Shared.PresenceChooseSurface(
                s.Uid!, s.Token!, SurfaceName.Text.Trim());
            SurfaceRows.Text = string.Join("\n",
                (sf.Surfaces ?? Array.Empty<PresenceSurfaceRow>()).Select(r =>
                    r.Surface + " · " + (r.ReadsHealthAloud
                        ? L10n.T("presence.aloud") : L10n.T("presence.shown"))));
        }
        catch { }
    }
}
