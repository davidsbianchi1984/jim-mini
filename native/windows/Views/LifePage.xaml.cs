using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace JimGuardian.Views;

public sealed partial class LifePage : Page
{
    public record GoalRow(string Title, string Meta);
    public record HabitRow(string Id, string Name, string Streak);
    public record JournalRow(string Text, string Date);

    public LifePage() => InitializeComponent();

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        await LoadGoals();
        await LoadHabits();
        await LoadJournal();
    }

    private static string Pretty(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..].Replace('_', ' ');

    // -- Goals --

    private async System.Threading.Tasks.Task LoadGoals()
    {
        var s = AppState.Current;
        try
        {
            var goals = await ApiClient.Shared.Goals(s.Uid!, s.Token!);
            GoalsList.ItemsSource = goals.Select(g =>
                new GoalRow(g.Title, $"{Pretty(g.Area)} · {Pretty(g.Status ?? "active")}")).ToList();
        }
        catch { /* leave as-is */ }
    }

    private async void OnAddGoal(object sender, RoutedEventArgs e)
    {
        var title = GoalTitle.Text.Trim();
        if (title.Length == 0) return;
        var area = (GoalArea.SelectedItem as ComboBoxItem)?.Content as string ?? "personal_growth";
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.AddGoal(s.Uid!, s.Token!, area, title, null);
            GoalTitle.Text = "";
            await LoadGoals();
        }
        catch { /* ignore */ }
    }

    // -- Habits --

    private async System.Threading.Tasks.Task LoadHabits()
    {
        var s = AppState.Current;
        try
        {
            var habits = await ApiClient.Shared.Habits(s.Uid!, s.Token!);
            HabitsList.ItemsSource = habits.Select(h =>
                new HabitRow(h.Id, h.Name, $"🔥 {h.Streak ?? 0} day streak")).ToList();
        }
        catch { /* leave as-is */ }
    }

    private async void OnAddHabit(object sender, RoutedEventArgs e)
    {
        var name = HabitName.Text.Trim();
        if (name.Length == 0) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.AddHabit(s.Uid!, s.Token!, name);
            HabitName.Text = "";
            await LoadHabits();
        }
        catch { /* ignore */ }
    }

    private async void OnLogHabit(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string id) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.LogHabit(s.Uid!, s.Token!, id);
            await LoadHabits();
        }
        catch { /* ignore */ }
    }

    // -- Journal --

    private async System.Threading.Tasks.Task LoadJournal()
    {
        var s = AppState.Current;
        try
        {
            var entries = await ApiClient.Shared.Journal(s.Uid!, s.Token!);
            JournalList.ItemsSource = entries.Reverse()
                .Select(j => new JournalRow(j.Text ?? "—", j.CreatedAt ?? "")).ToList();
        }
        catch { /* leave as-is */ }
    }

    private async void OnAddJournal(object sender, RoutedEventArgs e)
    {
        var text = JournalText.Text.Trim();
        if (text.Length == 0) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.AddJournal(s.Uid!, s.Token!, text);
            JournalText.Text = "";
            await LoadJournal();
        }
        catch { /* ignore */ }
    }
}
