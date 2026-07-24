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
                var refs = r.Guardian?.Guidance?.References;
                var lines = refs is { Length: > 0 }
                    ? string.Join("\n", System.Linq.Enumerable.Select(refs, x => $"→ {x}"))
                    : "";
                var prov = MonitorPage.FormatProvenance(r.Guardian?.Guidance);
                if (prov.Length > 0)
                    lines = lines.Length > 0 ? $"{lines}\n{prov}" : prov;
                GuidanceRefs.Text = lines;
                GuidanceRefs.Visibility = lines.Length > 0
                    ? Visibility.Visible : Visibility.Collapsed;
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
