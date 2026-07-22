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
    }
}
