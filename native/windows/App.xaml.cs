using Microsoft.UI.Xaml;

namespace JimGuardian;

public partial class App : Application
{
    private Window? _window;

    public App()
    {
        InitializeComponent();
    }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        _window = new MainWindow();
        _window.Activate();
        // What the buffer is for. Not awaited: a diagnostic must never be the
        // reason a window is slow to appear, and Send returns an outcome
        // rather than throwing, so there is nothing here to handle. It answers
        // AwaitingNotice until somebody has been told and chosen.
        _ = Problems.Send();
    }
}
