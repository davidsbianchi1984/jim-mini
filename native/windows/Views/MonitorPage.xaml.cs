using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;

namespace JimGuardian.Views;

public sealed partial class MonitorPage : Page
{
    public MonitorPage() => InitializeComponent();

    private async void OnSend(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        SendButton.IsEnabled = false;
        try
        {
            var r = await ApiClient.Shared.Monitor(s.Uid!, s.Token!,
                (int)HeartRate.Value, Stress.Value / 100.0);

            ResultTitle.Text = r.Detected
                ? Cap(r.Condition ?? "Detected")
                : "All clear";
            ResultTitle.Foreground = new SolidColorBrush(
                r.Detected ? Microsoft.UI.Colors.OrangeRed : Microsoft.UI.Colors.MediumSpringGreen);

            ResultReason.Text = r.Reason ?? "";
            ResultReason.Visibility = string.IsNullOrEmpty(r.Reason) ? Visibility.Collapsed : Visibility.Visible;

            ResultGuidance.Text = r.Guidance?.Content ?? "";
            ResultGuidance.Visibility = r.Guidance is null ? Visibility.Collapsed : Visibility.Visible;

            var aid = r.Guidance?.FirstAidPlaybook;
            if (aid is not null)
            {
                var header = $"First aid — {aid.Kind.ToUpper()}" +
                             (aid.CallEmergencyServices == true
                                  ? "  ·  📞 call emergency services now" : "");
                var steps = string.Join("\n", aid.Steps.Select(
                    (step, i) => $"{i + 1}. {step}"));
                ResultFirstAid.Text = $"{header}\n{steps}";
                ResultFirstAid.Visibility = Visibility.Visible;
                if (aid.Pace is { } pace)
                {
                    ResultPace.Text =
                        $"Pace: {pace.CompressionsPerMinute}/min · " +
                        $"{pace.CompressionToBreathRatio}" +
                        (pace.Cue is { } cue
                             ? $"\n💡 {cue.Light}\n🔊 {cue.Audio}" : "");
                    ResultPace.Visibility = Visibility.Visible;
                }
                else ResultPace.Visibility = Visibility.Collapsed;
            }
            else
            {
                ResultFirstAid.Visibility = Visibility.Collapsed;
                ResultPace.Visibility = Visibility.Collapsed;
            }

            var refs = r.Guidance?.References;
            if (refs is { Length: > 0 })
            {
                ResultRefs.Text = string.Join("\n", refs.Select(x => $"→ {x}"));
                ResultRefs.Visibility = Visibility.Visible;
            }
            else ResultRefs.Visibility = Visibility.Collapsed;

            ResultCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ResultTitle.Text = "Couldn't reach your Guardian";
            ResultReason.Text = ex.Message;
            ResultReason.Visibility = Visibility.Visible;
            ResultGuidance.Visibility = Visibility.Collapsed;
            ResultCard.Visibility = Visibility.Visible;
        }
        finally
        {
            SendButton.IsEnabled = true;
        }
    }

    private static string Cap(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..];
}
