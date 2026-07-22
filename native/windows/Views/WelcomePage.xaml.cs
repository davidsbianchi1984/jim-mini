using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

public sealed partial class WelcomePage : Page
{
    public WelcomePage() => InitializeComponent();

    private async void OnStart(object sender, RoutedEventArgs e)
    {
        var name = NameBox.Text.Trim();
        if (name.Length == 0 || ConsentBox.IsChecked != true)
        {
            ShowError("Enter your name and accept the terms to continue.");
            return;
        }
        StartButton.IsEnabled = false;
        try
        {
            var result = await ApiClient.Shared.Enroll(name, BirthBox.Text.Trim());
            AppState.Current.SignIn(result);
            Frame.Navigate(typeof(ShellPage));
        }
        catch (Exception ex)
        {
            ShowError($"Couldn't reach your Guardian — is the backend running? ({ex.Message})");
            StartButton.IsEnabled = true;
        }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
