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
                nvi.Content = L10n.T($"tab.{tag}");
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
            case "life": ContentFrame.Navigate(typeof(LifePage)); break;
            case "safety": ContentFrame.Navigate(typeof(SafetyPage)); break;
            case "connect": ContentFrame.Navigate(typeof(ConnectPage)); break;
            case "custody": ContentFrame.Navigate(typeof(CustodyPage)); break;
            case "family": ContentFrame.Navigate(typeof(FamilyPage)); break;
        }
    }

    private void OnSignOut(object sender, RoutedEventArgs e)
    {
        AppState.Current.SignOut();
        Frame.Navigate(typeof(WelcomePage));
    }
}
