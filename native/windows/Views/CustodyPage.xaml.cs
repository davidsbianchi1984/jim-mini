using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

/// Vault Custody: the user's sealed tandem exchanges, with PDI's audit-chain
/// status; selecting a record reads its provenance trail through JIM.
public sealed partial class CustodyPage : Page
{
    public CustodyPage() => InitializeComponent();

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        base.OnNavigatedTo(e);
        await Load();
    }

    private async void OnRefresh(object sender, RoutedEventArgs e) => await Load();

    private async Task Load()
    {
        var s = AppState.Current;
        try
        {
            var c = await ApiClient.Shared.Custody(s.Uid!, s.Token!);
            ChainText.Text = c.ChainIntact == true
                ? "🔗 Audit chain intact"
                : "⚠️ Audit chain status unknown";
            ChainText.Visibility = Visibility.Visible;
            RecordsList.ItemsSource = c.Records;
            EmptyText.Visibility = c.Records.Length == 0
                ? Visibility.Visible : Visibility.Collapsed;
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;   // e.g. "no PDI vault configured"
            ErrorText.Visibility = Visibility.Visible;
            ChainText.Visibility = Visibility.Collapsed;
            EmptyText.Visibility = Visibility.Collapsed;
        }
    }

    private async void OnSelect(object sender, SelectionChangedEventArgs e)
    {
        if (RecordsList.SelectedItem is not string key) return;
        var s = AppState.Current;
        try
        {
            var p = await ApiClient.Shared.CustodyProvenance(s.Uid!, s.Token!, key);
            ProvTitle.Text = $"🔒 {key}";
            var lines = new List<string> { $"Origin: {p.Origin}" };
            if (p.Sealed?.Cipher is { } cipher) lines.Add($"Seal: {cipher}");
            if (p.Audit is { } audit) lines.Add($"Audit events: {audit.Count}");
            lines.Add(p.Chain?.Intact == true
                ? "Hash chain: intact" : "Hash chain: unknown");
            ProvText.Text = string.Join("\n", lines);
            ProvCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
    }
}
