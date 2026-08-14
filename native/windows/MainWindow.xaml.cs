using Microsoft.UI.Xaml;
using JimGuardian.Views;

namespace JimGuardian;

public sealed partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        Title = "JIM Guardian";
        RootFrame.Navigate(AppState.Current.IsEnrolled ? typeof(ShellPage) : typeof(WelcomePage));
        _ = CheckVersion();
    }

    /// <summary>
    /// The version handshake, made visible on the desktop shell.
    ///
    /// A stale backend from an older install answers <c>/health</c> perfectly
    /// well and then serves an older API, so the app looks alive while every
    /// newer screen answers "Not Found" with no explanation. The console has
    /// said so since the mismatch first cost somebody an evening; this shell
    /// can be pointed at the same stale address — <c>SetBase</c> exists for
    /// exactly that — and said nothing at all.
    ///
    ///     asked     is the backend reachable
    ///     mattered  is it the backend this build was written against
    ///
    /// Reachability was the only question any shell asked. <c>/health</c> has
    /// carried the answer to the second one the whole time, and this shell
    /// decoded it away.
    /// </summary>
    private async System.Threading.Tasks.Task CheckVersion()
    {
        HealthOut? h;
        try { h = await ApiClient.Shared.Health(); }
        // An unreachable backend is the connection panel's story, not this
        // one: a version guard that also complained about being offline
        // would cry wolf every time the machine changed network.
        catch { return; }

        var lang = AppState.Current.Language;
        // A backend too old to carry the field is the loudest case there is,
        // so it gets a name rather than reading as agreement.
        var backend = string.IsNullOrEmpty(h?.Version)
            ? L10n.T("vg.ancient", lang) : h!.Version!;
        var mine = Problems.AppVersion;
        if (backend == mine) return;

        VgTitle.Text = L10n.T("vg.title", lang);
        VgBody.Text = string.Format(L10n.T("vg.body", lang),
                                    mine, ApiClient.Shared.Base, backend);
        VgFix.Text = L10n.T("vg.fix", lang);
        VgDismiss.Content = L10n.T("vg.dismiss", lang);
        VersionGuard.Visibility = Visibility.Visible;
    }

    // Dismissible, because somebody who knows and is working anyway should
    // not read it on every screen; and per-launch rather than remembered,
    // because the condition holds until the address or the backend changes,
    // and a permanently silenced warning about a broken deployment is worse
    // than none.
    private void VgDismiss_Click(object sender, RoutedEventArgs e)
        => VersionGuard.Visibility = Visibility.Collapsed;
}
