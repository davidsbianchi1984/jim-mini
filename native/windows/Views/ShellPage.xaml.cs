using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace JimGuardian.Views;

public sealed partial class ShellPage : Page
{
    public ShellPage()
    {
        InitializeComponent();
        ContentFrame.Navigate(typeof(OverviewPage));
    }

    private void OnSelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
    {
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
        }
    }

    private void OnSignOut(object sender, RoutedEventArgs e)
    {
        AppState.Current.SignOut();
        Frame.Navigate(typeof(WelcomePage));
    }
}
