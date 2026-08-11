using Microsoft.UI.Xaml;

namespace JimGuardian;

public partial class App : Application
{
    private Window? _window;

    /// The one window, reachable by name: a FileOpenPicker on WinUI 3
    /// desktop must be initialized with a window handle, and the picker
    /// call sites have no other way to reach it.
    public static Window? MainAppWindow { get; private set; }

    public App()
    {
        InitializeComponent();
    }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        _window = new MainWindow();
        MainAppWindow = _window;
        _window.Activate();
        // What the buffer is for. Not awaited: a diagnostic must never be the
        // reason a window is slow to appear, and Send returns an outcome
        // rather than throwing, so there is nothing here to handle. It answers
        // AwaitingNotice until somebody has been told and chosen.
        _ = Problems.Send();
    }
}
