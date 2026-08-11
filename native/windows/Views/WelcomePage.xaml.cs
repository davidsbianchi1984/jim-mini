using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

public sealed partial class WelcomePage : Page
{
    private LanguageInfo[] _languages = Array.Empty<LanguageInfo>();

    public WelcomePage()
    {
        InitializeComponent();
        NameBox.Header = L10n.T("nw.name");
        NameBox.PlaceholderText = L10n.T("res.name");
        BirthBox.Header = L10n.T("nw.birthdate");
        BirthBox.PlaceholderText = L10n.T("nw.birthdate.ph");
        StartButton.Content = L10n.T("nw.start");
        LanguageBox.Header = L10n.T("ov.language");
        ConsentBox.Content = L10n.T("onb.consent");
        ModeUpButton.Content = L10n.T("onb.create");
        ModeInButton.Content = L10n.T("onb.signin");
        ModeResetButton.Content = L10n.T("onb.forgot");
        AccountEmailBox.Header = L10n.T("onb.email");
        AccountEmailBox.PlaceholderText = L10n.T("onb.email.ph");
        AccountNameBox.Header = L10n.T("onb.yourname");
        AccountPasswordBox.Header = L10n.T("onb.password.min");
        AccountConsentBox.Content = L10n.T("onb.consent");
        AccountCodeBox.Header = L10n.T("onb.code");
        ResendButton.Content = L10n.T("onb.code.resend");
        ResetSendButton.Content = L10n.T("onb.reset.send");
        ResetHint.Text = L10n.T("onb.reset.hint");
        VerifyHint.Text = L10n.T("onb.verify.type");
        RenderMode();
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        try
        {
            _languages = (await ApiClient.Shared.Languages()).Languages;
            LanguageBox.ItemsSource = _languages.Select(l => l.Label).ToList();
            LanguageBox.SelectedIndex = 0;   // English
        }
        catch { /* backend offline — enroll will surface the error */ }
        try { RenderDoors((await ApiClient.Shared.OauthProviders()).Providers); }
        catch { /* no doors to draw */ }
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

    // ---- the account the phones never had ----

    private string _mode = "up";     // up | in | reset
    private bool _pending;           // signed up; the code is out

    private void OnModeUp(object sender, RoutedEventArgs e) { _mode = "up"; RenderMode(); }
    private void OnModeIn(object sender, RoutedEventArgs e) { _mode = "in"; RenderMode(); }
    private void OnModeReset(object sender, RoutedEventArgs e) { _mode = "reset"; RenderMode(); }

    private void RenderMode()
    {
        AccountNotice.Visibility = Visibility.Collapsed;
        AccountError.Visibility = Visibility.Collapsed;
        var up = _mode == "up";
        AccountNameBox.Visibility = up && !_pending ? Visibility.Visible : Visibility.Collapsed;
        AccountConsentBox.Visibility = up && !_pending ? Visibility.Visible : Visibility.Collapsed;
        AccountPasswordBox.Visibility = up && _pending ? Visibility.Collapsed : Visibility.Visible;
        VerifyHint.Visibility = up && _pending ? Visibility.Visible : Visibility.Collapsed;
        ResendButton.Visibility = up && _pending ? Visibility.Visible : Visibility.Collapsed;
        AccountCodeBox.Visibility = (up && _pending) || _mode == "reset"
            ? Visibility.Visible : Visibility.Collapsed;
        AccountCodeBox.Header = _mode == "reset"
            ? L10n.T("onb.reset.code") : L10n.T("onb.code");
        ResetHint.Visibility = _mode == "reset" ? Visibility.Visible : Visibility.Collapsed;
        ResetSendButton.Visibility = _mode == "reset" ? Visibility.Visible : Visibility.Collapsed;
        AccountGoButton.Content = _mode switch
        {
            "up" => _pending ? L10n.T("onb.signin") : L10n.T("onb.create"),
            "in" => L10n.T("onb.signin"),
            _ => L10n.T("onb.reset.send"),
        };
    }

    private void RenderDoors(OauthProviderRow[] doors)
    {
        OauthDoors.Children.Clear();
        foreach (var door in doors)
        {
            var label = L10n.T("onb.signwith")
                .Replace("{mode}", L10n.T(_mode == "up" ? "onb.mode.up" : "onb.mode.in"))
                .Replace("{provider}", door.Name);
            var button = new Button
            {
                Content = door.Configured ? label : label + L10n.T("onb.oauth.absent"),
                FontSize = 12,
                Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                    Microsoft.UI.Colors.Transparent),
                IsEnabled = door.Configured,
            };
            var provider = door.Provider;
            button.Click += async (_, _) => await OpenDoor(provider);
            OauthDoors.Children.Add(button);
        }
    }

    /// Open the provider's page in the system browser, then poll the claim:
    /// this shell never sees the provider conversation — only whether the
    /// state it minted was honoured.
    private async System.Threading.Tasks.Task OpenDoor(string provider)
    {
        AccountError.Visibility = Visibility.Collapsed;
        try
        {
            var started = await ApiClient.Shared.OauthStart(provider);
            await Windows.System.Launcher.LaunchUriAsync(new Uri(started.Url));
            for (var i = 0; i < 40; i++)
            {
                await System.Threading.Tasks.Task.Delay(3000);
                var claim = await ApiClient.Shared.OauthClaim(started.State);
                if (!claim.Ready) continue;
                if (claim.Id is { } id && claim.UserToken is { } token)
                    Arrive(new EnrollResult(id, claim.DisplayName ?? claim.Email ?? "", token));
                return;
            }
        }
        catch (Exception ex) { ShowAccountError(ex.Message); }
    }

    private void Arrive(EnrollResult session)
    {
        AppState.Current.SignIn(session);
        Frame.Navigate(typeof(ShellPage));
    }

    private async void OnAccountGo(object sender, RoutedEventArgs e)
    {
        var email = AccountEmailBox.Text.Trim();
        var password = AccountPasswordBox.Password;
        AccountError.Visibility = Visibility.Collapsed;
        AccountNotice.Visibility = Visibility.Collapsed;
        try
        {
            if (_mode == "up" && !_pending)
            {
                var name = AccountNameBox.Text.Trim();
                if (email.Length == 0 || password.Length == 0 || name.Length == 0
                    || AccountConsentBox.IsChecked != true) return;
                var language = LanguageBox.SelectedIndex >= 0
                               && LanguageBox.SelectedIndex < _languages.Length
                    ? _languages[LanguageBox.SelectedIndex].Code
                    : null;
                var r = await ApiClient.Shared.Signup(email, password, name, language);
                if (r.Verified && r.Id is { } id && r.UserToken is { } token)
                    Arrive(new EnrollResult(id, r.DisplayName ?? name, token));
                else
                {
                    _pending = true;
                    RenderMode();
                    ShowNotice($"{L10n.T("onb.verify.sent")} {email}"
                               + (r.CodeDelivery is { } d ? $" · {d}" : ""));
                }
            }
            else if (_mode == "up")
            {
                var code = AccountCodeBox.Text.Trim();
                if (code.Length == 0) return;
                Arrive(await ApiClient.Shared.VerifyEmail(email, code));
            }
            else if (_mode == "in")
            {
                if (email.Length == 0 || password.Length == 0) return;
                var r = await ApiClient.Shared.Signin(email, password);
                Arrive(new EnrollResult(r.UserId, r.DisplayName ?? r.Email, r.UserToken));
            }
            else
            {
                // Every old session died with the old password; sign in
                // fresh with the new one.
                var code = AccountCodeBox.Text.Trim();
                if (email.Length == 0 || code.Length == 0 || password.Length == 0) return;
                await ApiClient.Shared.ResetPassword(email, code, password);
                _mode = "in";
                AccountCodeBox.Text = "";
                RenderMode();
                ShowNotice(L10n.T("onb.signin"));
            }
        }
        catch (Exception ex) { ShowAccountError(ex.Message); }
    }

    private async void OnResend(object sender, RoutedEventArgs e)
    {
        try
        {
            var r = await ApiClient.Shared.ResendCode(AccountEmailBox.Text.Trim());
            ShowNotice(r.Delivery);
        }
        catch (Exception ex) { ShowAccountError(ex.Message); }
    }

    private async void OnResetSend(object sender, RoutedEventArgs e)
    {
        try
        {
            var r = await ApiClient.Shared.RequestPasswordReset(AccountEmailBox.Text.Trim());
            ShowNotice(r.Delivery);
        }
        catch (Exception ex) { ShowAccountError(ex.Message); }
    }

    private void ShowNotice(string message)
    {
        AccountNotice.Text = message;
        AccountNotice.Visibility = Visibility.Visible;
    }

    private void ShowAccountError(string message)
    {
        AccountError.Text = message;
        AccountError.Visibility = Visibility.Visible;
    }
}
