using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace JimGuardian.Views;

public sealed partial class CoachPage : Page
{
    public CoachPage()
    {
        InitializeComponent();
        // In code rather than XAML: a XAML literal cannot be re-read when the
        // language changes.
        AskSpecialistButton.Content = L10n.T("spec.ask");
    }

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
            SpecialistCard.Visibility = Visibility.Collapsed;

            var offer = reply.SpecialistOffer;
            if (offer is not null && offer.Available)
            {
                OfferLabel.Text = offer.Label;
                OfferNote.Text = offer.Note;
                OfferPanel.Visibility = Visibility.Visible;
            }
            else { OfferPanel.Visibility = Visibility.Collapsed; }
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { AskButton.IsEnabled = true; }
    }

    /// The door the person chooses. Nothing crosses the tandem until this is
    /// pressed, because what crosses is what they wrote.
    private async void OnAskSpecialist(object sender, RoutedEventArgs e)
    {
        var message = MessageBox.Text.Trim();
        if (message.Length == 0) return;
        var area = (AreaBox.SelectedItem as ComboBoxItem)?.Content as string
                   ?? "mental_health";
        var s = AppState.Current;
        AskSpecialistButton.IsEnabled = false;
        try
        {
            var a = await ApiClient.Shared.CoachSpecialist(
                s.Uid!, s.Token!, area, message);
            SpecialistWho.Text = (a.Specialist?.Label ?? L10n.T("spec.fallback"))
                                 + " \u00b7 " + L10n.T("spec.via");
            SpecialistText.Text = a.Delivered && a.Content is not null
                ? a.Content
                : a.HeldForOwnerApproval
                    ? L10n.T("spec.held")
                    : (a.Reason ?? "") + (a.Note is null ? "" : $" \u2014 {a.Note}");
            SpecialistProv.Text = a.Provenance is null ? ""
                : $"{a.Provenance.Method}\n{L10n.T("spec.shared")}: {a.Provenance.Shared}";
            SpecialistCard.Visibility = Visibility.Visible;
            OfferPanel.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { AskSpecialistButton.IsEnabled = true; }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
