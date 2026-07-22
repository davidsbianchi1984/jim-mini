using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace JimGuardian.Views;

public sealed partial class CheckinPage : Page
{
    public CheckinPage() => InitializeComponent();

    private async void OnLog(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        LogButton.IsEnabled = false;
        try
        {
            var r = await ApiClient.Shared.Checkin(s.Uid!, s.Token!,
                (int)Mood.Value, (int)Energy.Value, NoteBox.Text);
            var guidance = r.Guardian?.Guidance?.Content;
            if (!string.IsNullOrEmpty(guidance))
            {
                GuidanceText.Text = guidance;
                GuidanceCard.Visibility = Visibility.Visible;
            }
        }
        catch
        {
            GuidanceText.Text = "Couldn't reach your Guardian — is the backend running?";
            GuidanceCard.Visibility = Visibility.Visible;
        }
        finally
        {
            LogButton.IsEnabled = true;
        }
    }
}
