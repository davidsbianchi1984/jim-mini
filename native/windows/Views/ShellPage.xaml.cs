using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace JimGuardian.Views;

public sealed partial class ShellPage : Page
{
    public ShellPage()
    {
        InitializeComponent();
        LocalizeNav();
        ContentFrame.Navigate(typeof(OverviewPage));
    }

    /// Nav labels follow the user's chosen language (chrome localization);
    /// re-applied on every pane selection so a language change in Overview
    /// takes effect immediately.
    private void LocalizeNav()
    {
        foreach (var entry in Nav.MenuItems)
            if (entry is NavigationViewItem nvi && nvi.Tag is string tag)
                // `tab.{tag}` is the convention and the presence is the one
                // exception: its label already exists as `presence.tab`,
                // shared with the other two shells and the console. Adding a
                // `tab.presence` row would put the same English under two
                // keys in one table — the defect the 0.48.0 sweep spent a
                // round removing.
                //
                // `engaged` is the second exception and arrives for the same
                // reason: its label is `eng.tab`, shared byte-for-byte with
                // the other two shells, and a `tab.engaged` row would be the
                // same English under two keys again.
            {
                var label = tag switch
                {
                    "presence" => L10n.T("presence.tab"),
                    "engaged" => L10n.T("eng.tab"),
                    _ => L10n.T($"tab.{tag}"),
                };
                // The label used to be the item's whole `Content`. The icons
                // moved into `Content` to be resized (see ShellPage.xaml), so
                // it is now a `TextBlock` beside one. Assigning a string to
                // `Content` here would silently throw the icon away — which
                // would look like the drawing failing rather than like this
                // line being wrong, so it is worth the extra four lines.
                if (nvi.Content is StackPanel panel)
                    foreach (var child in panel.Children)
                        if (child is TextBlock text)
                            text.Text = label;
            }
        // Not a menu item: this one sits in the pane footer, which the loop
        // above does not walk. It said "Sign out" in every language until this
        // round — and the sibling product found and fixed exactly this two
        // releases ago, in its own copy of this file, and nobody carried the
        // check across. The row has been in this repo's table all along;
        // Android has been using it.
        SignOutButton.Content = L10n.T("action.sign_out");
    }

    private void OnSelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
    {
        LocalizeNav();
        if (args.SelectedItem is not NavigationViewItem item) return;
        switch (item.Tag as string)
        {
            case "overview": ContentFrame.Navigate(typeof(OverviewPage)); break;
            case "monitor": ContentFrame.Navigate(typeof(MonitorPage)); break;
            case "checkin": ContentFrame.Navigate(typeof(CheckinPage)); break;
            case "coach": ContentFrame.Navigate(typeof(CoachPage)); break;
            // The coach answers a turn; this one stays engaged and can act.
            case "engaged": ContentFrame.Navigate(typeof(EngagedPage)); break;
            // The coach answers; the presence speaks first.
            case "presence": ContentFrame.Navigate(typeof(PresencePage)); break;
            case "life": ContentFrame.Navigate(typeof(LifePage)); break;
            case "safety": ContentFrame.Navigate(typeof(SafetyPage)); break;
            case "connect": ContentFrame.Navigate(typeof(ConnectPage)); break;
            case "custody": ContentFrame.Navigate(typeof(CustodyPage)); break;
            case "family": ContentFrame.Navigate(typeof(FamilyPage)); break;
            // The synthetic self shipped as a page nothing navigated to. It
            // had its strings in ten languages and a guard checking they were
            // there.
            //
            //     asked     does the screen have its wording
            //     mattered  does anything open the screen
            case "self": ContentFrame.Navigate(typeof(SelfProfilePage)); break;
        }
    }

    private void OnSignOut(object sender, RoutedEventArgs e)
    {
        AppState.Current.SignOut();
        Frame.Navigate(typeof(WelcomePage));
    }
}
