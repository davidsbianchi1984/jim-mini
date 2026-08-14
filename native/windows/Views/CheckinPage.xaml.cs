using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using System.Linq;

namespace JimGuardian.Views;

public sealed partial class CheckinPage : Page
{
    private static readonly string[] Levels =
        { "beginner", "intermediate", "advanced" };
    private static readonly string[] MealGoals =
        { "lose_weight", "gain_muscle", "eat_healthier" };

    public CheckinPage()
    {
        InitializeComponent();
        // In code rather than XAML: a XAML literal cannot be re-read when the
        // language changes, and this heading was the English one.
        TitleText.Text = L10n.T("tab.checkin");
        PitchText.Text = L10n.T("ci.pitch");
        TakeBackButton.Content = L10n.T("chk.remove");
        Mood.Header = L10n.T("ci.mood");
        Energy.Header = L10n.T("ci.energy");
        NoteBox.Header = L10n.T("ci.note");
        NoteBox.PlaceholderText = L10n.T("ci.note.ph");
        LogButton.Content = L10n.T("ci.log");
        GuidanceHead.Text = L10n.T("ci.guidance");
        CalmHead.Text = L10n.T("wel.calm");
        CalmPitch.Text = L10n.T("wel.calm.pitch").Replace("{spoken}", "");
        WorkHead.Text = L10n.T("wel.work");
        WorkMinutes.Header = L10n.T("wel.work.minutes");
        WorkLevel.Header = L10n.T("wel.work.level");
        WorkLevel.ItemsSource = Levels.ToList();
        WorkFocus.Header = L10n.T("wel.work.focus");
        WorkFocus.Text = "mobility";
        WorkBuildButton.Content = L10n.T("wel.work.build");
        MealHead.Text = L10n.T("wel.meals");
        MealGoal.Header = L10n.T("wel.meals.goal");
        MealGoal.ItemsSource = new[] { L10n.T("wel.meals.lose"),
            L10n.T("wel.meals.gain"), L10n.T("wel.meals.healthier") }.ToList();
        MealDays.Header = L10n.T("wel.meals.days");
        MealPlanButton.Content = L10n.T("wel.meals.plan");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        try { RenderCalmTiles((await ApiClient.Shared.CalmCatalog()).Sessions); }
        catch { /* backend offline */ }
        await ReloadCalmHistory();
    }

    private void RenderCalmTiles(CalmSessionRow[] sessions)
    {
        CalmTiles.Children.Clear();
        foreach (var session in sessions)
        {
            var kind = session.Kind;
            var button = new Button
            {
                Content = L10n.T("wel.calm.tile")
                    .Replace("{title}", session.Title)
                    .Replace("{n}", session.Minutes.ToString()),
                FontSize = 12,
                Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                    Microsoft.UI.Colors.Transparent),
            };
            button.Click += async (_, _) => await BeginCalm(kind);
            CalmTiles.Children.Add(button);
        }
    }

    private async System.Threading.Tasks.Task BeginCalm(string kind)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        WelError.Visibility = Visibility.Collapsed;
        try
        {
            var started = await ApiClient.Shared.StartCalm(s.Uid, s.Token, kind);
            CalmSteps.Children.Clear();
            for (var i = 0; i < started.Steps.Length; i++)
            {
                var step = started.Steps[i];
                CalmSteps.Children.Add(Line(L10n.T("wel.calm.step")
                    .Replace("{i}", (i + 1).ToString())
                    .Replace("{n}", started.Steps.Length.ToString())
                    .Replace("{sec}", step.Seconds.ToString())
                    + " — " + step.Say, "JimT2Brush"));
            }
            CalmNote.Text = started.Note;
            CalmNote.Visibility = Visibility.Visible;
            await ReloadCalmHistory();
        }
        catch (Exception ex) { ShowWelError(ex.Message); }
    }

    private async System.Threading.Tasks.Task ReloadCalmHistory()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var rows = await ApiClient.Shared.CalmHistory(s.Uid, s.Token);
            CalmHistory.Children.Clear();
            foreach (var row in rows.Take(3))
                CalmHistory.Children.Add(Line($"{row.Title} · {row.At}",
                                              "JimT3Brush"));
        }
        catch { /* leave as-is */ }
    }

    private async void OnBuildWorkout(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        WelError.Visibility = Visibility.Collapsed;
        try
        {
            var level = WorkLevel.SelectedIndex >= 0
                ? Levels[WorkLevel.SelectedIndex] : "beginner";
            var plan = await ApiClient.Shared.WorkoutPlan(
                s.Uid, s.Token, (int)WorkMinutes.Value, level,
                WorkFocus.Text.Trim());
            WorkBlocks.Children.Clear();
            foreach (var block in plan.Blocks.Take(8))
                WorkBlocks.Children.Add(Line(block.Name
                    + L10n.T("wel.work.block")
                        .Replace("{sec}", block.Seconds.ToString())
                        .Replace("{cue}", block.Cue), "JimT2Brush"));
        }
        catch (Exception ex) { ShowWelError(ex.Message); }
    }

    private async void OnPlanMeals(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        WelError.Visibility = Visibility.Collapsed;
        try
        {
            var goal = MealGoal.SelectedIndex >= 0
                ? MealGoals[MealGoal.SelectedIndex] : "eat_healthier";
            var plan = await ApiClient.Shared.MealPlan(
                s.Uid, s.Token, goal, (int)MealDays.Value);
            MealShape.Text = L10n.T("wel.meals.shape")
                .Replace("{why}", plan.Shape.Why)
                .Replace("{kcal}", plan.Shape.OrientationCalories.ToString());
            MealShape.Visibility = Visibility.Visible;
            MealDaysList.Children.Clear();
            foreach (var day in plan.Days)
            {
                MealDaysList.Children.Add(Line(L10n.T("wel.meals.day")
                    .Replace("{n}", day.DayNumber.ToString()), "JimT2Brush"));
                foreach (var meal in day.Meals)
                    MealDaysList.Children.Add(Line($"{meal.Slot}: {meal.Name}",
                                                   "JimT3Brush"));
            }
            MealDisclaimer.Text = plan.Disclaimer;
            MealDisclaimer.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowWelError(ex.Message); }
    }

    private static TextBlock Line(string text, string brush) => new()
    {
        Text = text,
        FontSize = 11,
        TextWrapping = TextWrapping.Wrap,
        Foreground = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources[brush],
    };

    private void ShowWelError(string message)
    {
        WelError.Text = message;
        WelError.Visibility = Visibility.Visible;
    }

    private async void OnLog(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        LogButton.IsEnabled = false;
        try
        {
            var r = await ApiClient.Shared.Checkin(s.Uid!, s.Token!,
                (int)Mood.Value, (int)Energy.Value, NoteBox.Text);
            _lastCheckin = r.Id;
            TakeBackButton.Visibility = Visibility.Visible;
            var guidance = r.Guardian?.Guidance?.Content;
            if (!string.IsNullOrEmpty(guidance))
            {
                GuidanceText.Text = guidance;
                var refs = r.Guardian?.Guidance?.References;
                var lines = refs is { Length: > 0 }
                    ? string.Join("\n", System.Linq.Enumerable.Select(refs, x => $"→ {x}"))
                    : "";
                var who = MonitorPage.FormatSpecialist(r.Guardian?.Guidance);
                if (who.Length > 0)
                    lines = lines.Length > 0 ? $"{who}\n{lines}" : who;
                var prov = MonitorPage.FormatProvenance(r.Guardian?.Guidance);
                if (prov.Length > 0)
                    lines = lines.Length > 0 ? $"{lines}\n{prov}" : prov;
                GuidanceRefs.Text = lines;
                GuidanceRefs.Visibility = lines.Length > 0
                    ? Visibility.Visible : Visibility.Collapsed;
                GuidanceCard.Visibility = Visibility.Visible;
            }
        }
        catch
        {
            GuidanceText.Text = L10n.T("ci.error");
            GuidanceCard.Visibility = Visibility.Visible;
        }
        finally
        {
            LogButton.IsEnabled = true;
        }
    }

    /// The id of the check-in just logged, so it can be taken back. Held
    /// rather than re-fetched: what a person means by "that one" is the one
    /// they are looking at.
    private string? _lastCheckin;

    private async void OnTakeBack(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (_lastCheckin is null || s.Uid is null || s.Token is null) return;
        try
        {
            await ApiClient.Shared.RemoveCheckin(s.Uid, s.Token, _lastCheckin);
            _lastCheckin = null;
            TakeBackButton.Visibility = Visibility.Collapsed;
            GuidanceCard.Visibility = Visibility.Collapsed;
        }
        catch { /* the card keeps its state */ }
    }

}
