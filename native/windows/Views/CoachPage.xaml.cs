using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace JimGuardian.Views;

public sealed partial class CoachPage : Page
{
    public CoachPage() => InitializeComponent();

    private async void OnAsk(object sender, RoutedEventArgs e)
    {
        var message = MessageBox.Text.Trim();
        if (message.Length == 0) { ShowError("Type a message to your coach."); return; }
        var area = (AreaBox.SelectedItem as ComboBoxItem)?.Content as string ?? "mental_health";

        var s = AppState.Current;
        AskButton.IsEnabled = false;
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            var reply = await ApiClient.Shared.Coach(s.Uid!, s.Token!, area, message);
            ReplyText.Text = reply.Content;
            var who = MonitorPage.FormatSpecialist(reply);
            var prov = MonitorPage.FormatProvenance(reply);
            ReplyProvenance.Text = who.Length > 0 && prov.Length > 0
                ? $"{who}\n{prov}" : who + prov;
            ReplyProvenance.Visibility = ReplyProvenance.Text.Length > 0
                ? Visibility.Visible : Visibility.Collapsed;
            ReplyCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { AskButton.IsEnabled = true; }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
