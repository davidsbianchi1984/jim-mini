using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

public sealed partial class WelcomePage : Page
{
    private LanguageInfo[] _languages = Array.Empty<LanguageInfo>();

    public WelcomePage() => InitializeComponent();

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        try
        {
            _languages = (await ApiClient.Shared.Languages()).Languages;
            LanguageBox.ItemsSource = _languages.Select(l => l.Label).ToList();
            LanguageBox.SelectedIndex = 0;   // English
        }
        catch { /* backend offline — enroll will surface the error */ }
    }

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
            var language = LanguageBox.SelectedIndex >= 0
                           && LanguageBox.SelectedIndex < _languages.Length
                ? _languages[LanguageBox.SelectedIndex].Code
                : null;
            var result = await ApiClient.Shared.Enroll(name, BirthBox.Text.Trim(),
                                                       language);
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
