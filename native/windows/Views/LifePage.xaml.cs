using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using System.Collections.Generic;

namespace JimGuardian.Views;

public sealed partial class LifePage : Page
{
    public sealed class GoalRow
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string Meta { get; init; } = "";
        public bool Active { get; init; }
        public string DoneLabel => L10n.T("aim.goals.done");
        public string RemoveLabel => L10n.T("aim.goals.remove");
        public Visibility DoneVisibility =>
            Active ? Visibility.Visible : Visibility.Collapsed;
    }
    public record HabitRow(string Id, string Name, string Streak)
    {
        public string LogLabel => L10n.T("habit.log");
        public string UntickLabel => L10n.T("aim.habits.undid");
        public string DropLabel => L10n.T("aim.habits.drop");
    }
    // `Id` arrived with the delete door: the row rendered text and a date and
    // had nothing to delete *by*.
    public record JournalRow(string Id, string Text, string Date)
    {
        public string RemoveLabel => L10n.T("jrn.remove");
    }

    // The wire word is the tag; the shown label derives from it the same
    // way the iOS and Android pickers spell it — never a second English.
    private static readonly string[] GoalAreas =
        { "mental_health", "health_fitness", "career", "finance",
          "relationships", "personal_growth" };

    public LifePage()
    {
        InitializeComponent();
        // Money, Schedule, Shops and Circle take their headers from the
        // backend's own label sets. These three had nothing to take them
        // from and were English in every language.
        GoalsPivot.Header = L10n.T("life.goals");
        HabitsPivot.Header = L10n.T("life.habits");
        JournalPivot.Header = L10n.T("life.journal");
        GoalNewHead.Text = L10n.T("goal.new");
        GoalArea.Header = L10n.T("coach.area");
        GoalArea.ItemsSource = GoalAreas.Select(a => a.Replace('_', ' ')).ToList();
        GoalTitle.Header = L10n.T("goal.title");
        GoalTitle.PlaceholderText = L10n.T("goal.title.ph");
        AddGoalButton.Content = L10n.T("goal.add");
        HabitNewHead.Text = L10n.T("habit.new");
        HabitName.Header = L10n.T("habit.name");
        HabitName.PlaceholderText = L10n.T("habit.name.ph");
        AddHabitButton.Content = L10n.T("habit.add");
        BesideHead.Text = L10n.T("bes.head");
        BesidePitch.Text = L10n.T("bes.pitch");
        BesideDraft.PlaceholderText = L10n.T("bes.ph");
        BesideGo.Content = L10n.T("bes.go");
        JournalNewHead.Text = L10n.T("jrn.new");
        JournalText.Header = L10n.T("jrn.entry");
        JournalText.PlaceholderText = L10n.T("jrn.entry.ph");
        SaveEntryButton.Content = L10n.T("jrn.save");
        MealHead.Text = L10n.T("mea.title");
        MealNote.PlaceholderText = L10n.T("mea.ph");
        LogMealButton.Content = L10n.T("mea.log");
        LetterHead.Text = L10n.T("let.title");
        WriteLetterButton.Content = L10n.T("let.write");
        DrillHead.Text = L10n.T("drl.title");
        DealDrillButton.Content = L10n.T("drl.deal");
        DrillAnswerBox.PlaceholderText = L10n.T("drl.answer.ph");
        ReadDrillButton.Content = L10n.T("drl.read");
        LocalizeMeds();
        ActHead.Text = L10n.T("aim.activity");
        ActPitch.Text = L10n.T("aim.activity.pitch");
        ActWhat.PlaceholderText = L10n.T("aim.activity.ph");
        ActNote.PlaceholderText = L10n.T("brg.told.note.ph");
        ActLogButton.Content = L10n.T("aim.activity.log");
        BudHead.Text = L10n.T("aim.budget");
        BudNone.Text = L10n.T("aim.budget.none");
        BudCategory.PlaceholderText = L10n.T("aim.budget.cat.ph");
        BudSetButton.Content = L10n.T("aim.budget.set");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        await LoadGoals();
        await LoadHabits();
        await LoadJournal();
        await LoadMeals();
        await LoadLetters();
        await LoadDrills();
        await LoadMoney();
        await LoadBudgets();
        await LoadSchedule();
        await LoadTandemShops();
        await LoadCircle();
        await LoadMeds();
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
                new GoalRow
                {
                    Id = g.Id,
                    Title = g.Title,
                    Meta = $"{Pretty(g.Area)} · {Pretty(g.Status ?? "active")}",
                    Active = (g.Status ?? "active") == "active",
                }).ToList();
        }
        catch { /* leave as-is */ }
    }


    // The ways back an undo trail needed, and doors a person should always
    // have had: until an engaged session needed to take a check-in back,
    // nothing in this product could delete one.
    private async void OnGoalRemove(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string goalId) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.RemoveGoal(s.Uid!, s.Token!, goalId);
            await LoadGoals();
        }
        catch { /* the row keeps its state */ }
    }

    private async void OnUntickHabit(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string habitId) return;
        var s = AppState.Current;
        try
        {
            // Composed rather than formatted: a `"yyyy-MM-dd"` literal is a
            // string this shell's own table happens to carry, so the
            // English-in-the-screen guard reads it as prose. The date is the
            // same either way.
            var today = DateTime.UtcNow;
            await ApiClient.Shared.UnlogHabit(s.Uid!, s.Token!, habitId,
                $"{today.Year:D4}-{today.Month:D2}-{today.Day:D2}");
            await LoadHabits();
        }
        catch { /* the row keeps its state */ }
    }

    private async void OnDropHabit(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string habitId) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.RemoveHabit(s.Uid!, s.Token!, habitId);
            await LoadHabits();
        }
        catch { /* the row keeps its state */ }
    }

    private async void OnJournalRemove(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string entryId) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.RemoveJournal(s.Uid!, s.Token!, entryId);
            await LoadJournal();
        }
        catch { /* the row keeps its state */ }
    }

    private async void OnGoalDone(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string goalId) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.UpdateGoal(s.Uid!, s.Token!, goalId, 1.0,
                                              "completed");
            await LoadGoals();
        }
        catch { /* the row keeps its state */ }
    }

    // Tell it what you did: an ordinary activity is context, not a reading.
    private async void OnActivityLog(object sender, RoutedEventArgs e)
    {
        var what = ActWhat.Text.Trim();
        if (what.Length == 0) return;
        var s = AppState.Current;
        ActError.Visibility = Visibility.Collapsed;
        ActIntervention.Visibility = Visibility.Collapsed;
        try
        {
            var watch = await ApiClient.Shared.ObserveActivity(
                s.Uid!, s.Token!, what, ActNote.Text.Trim());
            ActWhat.Text = ""; ActNote.Text = "";
            if (watch.Intervention is { } spoke)
            {
                // The proactive voice: it noticed a struggle building and
                // spoke before being asked.
                ActIntervention.Text = spoke.Content;
                ActIntervention.Visibility = Visibility.Visible;
            }
        }
        catch (Exception ex)
        {
            ActError.Text = ex.Message;
            ActError.Visibility = Visibility.Visible;
        }
    }

    private async void OnAddGoal(object sender, RoutedEventArgs e)
    {
        var title = GoalTitle.Text.Trim();
        if (title.Length == 0) return;
        var area = GoalAreas[GoalArea.SelectedIndex >= 0 ? GoalArea.SelectedIndex : 5];
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
                new HabitRow(h.Id, h.Name,
                    L10n.T("habit.streak")
                        .Replace("{n}", $"{h.Streak ?? 0}"))).ToList();
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
            // Enumerable.Reverse by name: `entries` is a JournalItem[], and an
            // array converts to Span<T>, so plain .Reverse() binds to
            // MemoryExtensions' in-place void overload and the .Select below
            // then has nothing to attach to.
            JournalList.ItemsSource = Enumerable.Reverse(entries)
                .Select(j => new JournalRow(j.Id, j.Text ?? "—", j.CreatedAt ?? "")).ToList();
        }
        catch { /* leave as-is */ }
    }

    /// <summary>Read the draft on this device and say what is worth saying.
    /// Nothing is stored and nothing is edited — applying a remark is the
    /// writer's own act.</summary>
    private async void OnReadAlongside(object sender, RoutedEventArgs e)
    {
        var st = AppState.Current;
        var draft = BesideDraft.Text.Trim();
        if (st.Uid is null || st.Token is null || draft.Length == 0) return;
        var txt = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources["JimTxtBrush"];
        var t2 = (Microsoft.UI.Xaml.Media.Brush)
            Application.Current.Resources["JimT2Brush"];
        BesideGo.IsEnabled = false;
        try
        {
            var read = await ApiClient.Shared.Alongside(st.Uid!, st.Token!,
                                                        draft);
            BesidePanel.Children.Clear();
            BesideQuiet.Text = read.QuietBecause ?? "";
            BesideQuiet.Visibility = read.Remarks.Length == 0
                && read.QuietBecause is not null
                ? Visibility.Visible : Visibility.Collapsed;
            foreach (var m in read.Remarks)
            {
                var row = new StackPanel { Spacing = 2 };
                row.Children.Add(new TextBlock
                {
                    Text = L10n.T($"bes.kind.{m.Kind}") + " " + m.Says,
                    FontSize = 13, TextWrapping = TextWrapping.Wrap,
                    Foreground = txt,
                });
                // The evidence travels with the remark.
                row.Children.Add(new TextBlock
                {
                    Text = string.Join(" · ", m.Because), FontSize = 11,
                    TextWrapping = TextWrapping.Wrap, Foreground = t2,
                });
                BesidePanel.Children.Add(row);
            }
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { BesideGo.IsEnabled = true; }
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

    // -- Meals: the note is the log; a sealed receipt shows as a lock --

    private async System.Threading.Tasks.Task LoadMeals()
    {
        var s = AppState.Current;
        try
        {
            var meals = await ApiClient.Shared.Meals(s.Uid!, s.Token!);
            MealsList.ItemsSource = meals
                .Select(m => new JournalRow(
                    m.PhotoSealed ? m.Logged + " · 🔒" : m.Logged,
                    m.CreatedAt ?? "")).ToList();
        }
        catch { /* leave as-is */ }
    }

    // -- Interview drills: the bank is local; the reading names who
    // made it -- the coach, or the probe checklist standing in honestly --

    private string _drillId = "";
    private string _drillProbes = "";

    private async System.Threading.Tasks.Task LoadDrills()
    {
        var s = AppState.Current;
        try
        {
            var rows = await ApiClient.Shared.Drills(s.Uid!, s.Token!);
            DrillLog.ItemsSource = rows.Take(3)
                .Select(d => new JournalRow(d.Question, d.AnsweredAt ?? ""))
                .ToList();
        }
        catch { /* leave as-is */ }
    }

    private async void OnDealDrill(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            var d = await ApiClient.Shared.StartDrill(s.Uid!, s.Token!);
            _drillId = d.Id;
            _drillProbes = string.Join(" · ", d.Probes ?? System.Array.Empty<string>());
            DrillQuestion.Text = d.Question;
            DrillProbes.Text = _drillProbes;
            DrillLine.Text = "";
        }
        catch { /* ignore */ }
    }

    private async void OnReadDrill(object sender, RoutedEventArgs e)
    {
        var answer = DrillAnswerBox.Text.Trim();
        if (answer.Length == 0 || _drillId.Length == 0) return;
        var s = AppState.Current;
        try
        {
            var read = await ApiClient.Shared.AnswerDrill(
                s.Uid!, _drillId, answer, s.Token!);
            DrillLine.Text = read.Critique ?? _drillProbes;
            DrillAnswerBox.Text = ""; _drillId = "";
            DrillQuestion.Text = ""; DrillProbes.Text = "";
            await LoadDrills();
        }
        catch { /* ignore */ }
    }

    // -- The weekly letter: composed only from what was logged --

    private async System.Threading.Tasks.Task LoadLetters()
    {
        var s = AppState.Current;
        try
        {
            var letters = await ApiClient.Shared.Letters(s.Uid!, s.Token!);
            LettersList.ItemsSource = letters
                .Select(l => new JournalRow(l.Body, l.WeekStart)).ToList();
        }
        catch { /* leave as-is */ }
    }

    private async void OnWriteLetter(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.WriteLetter(s.Uid!, s.Token!);
            await LoadLetters();
        }
        catch { /* ignore */ }
    }

    private async void OnLogMeal(object sender, RoutedEventArgs e)
    {
        var note = MealNote.Text.Trim();
        if (note.Length == 0) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.LogMeal(s.Uid!, note, s.Token!);
            MealNote.Text = "";
            await LoadMeals();
        }
        catch { /* ignore */ }
    }

    // -- Money --
    //
    // Every visible string on this pivot comes from the overview's own
    // `labels` — composed server-side in the reader's language, exactly as
    // the desktop Money card renders them — because the English count behind
    // this shell's tabs is a ratchet and this pivot must not feed it. Until
    // the overview loads, the controls carry no words at all.

    public record AccountRow(string Line, string Balance);
    public record LinkRow(string Id, string Text, string SyncLabel,
                          string UnlinkLabel);

    private System.Collections.Generic.Dictionary<string, string> _moneyLabels = new();

    private async System.Threading.Tasks.Task LoadMoney()
    {
        var s = AppState.Current;
        try
        {
            var v = await ApiClient.Shared.MoneyOverview(s.Uid!, s.Token!);
            _moneyLabels = v.Labels;
            string L(string key) => v.Labels.TryGetValue(key, out var t) ? t : "";
            MoneyPivot.Header = L("title");
            MoneyTitle.Text = L("accounts");
            MoneyNote.Text = v.Note;
            MoneyAccounts.ItemsSource = v.Accounts.Select(a => new AccountRow(
                $"{a.Label ?? a.Institution} · {a.Kind}" +
                    (a.Last4 is null ? "" : $" ····{a.Last4}"),
                a.Balance is null ? "" : $"{L("balance")}: {a.Balance:F0}")).ToList();
            MoneyInstitution.Header = L("institution");
            MoneyAccountNumber.Header = L("account_number");
            MoneyRoutingNumber.Header = L("routing_number");
            MoneyAddButton.Content = L("add_account");
            MoneyObserveTitle.Text = L("record_balance");
            MoneyBalance.Header = L("balance");
            MoneyObserveButton.Content = L("record_balance");
            MoneySavingsTitle.Text = L("savings_goal");
            MoneySavingsCurrent.Text = v.Savings is null ? "" : $"{v.Savings.Goal:F0}";
            MoneyGoal.Header = L("savings_goal");
            MoneyGoalButton.Content = L("set_goal");
            MoneyFloorTitle.Text = L("low_floor");
            MoneyFloorBox.Header = L("low_floor");
            MoneyFloorButton.Content = L("set_floor");
            MoneyMandateTitle.Text = L("mandate");
            MoneyScope.Header = L("scope");
            MoneyMandateButton.Content = L("mandate_save");
            MoneyRevokeButton.Content = L("mandate_revoke");
            MoneyOrdersText.Text = v.Orders.Length == 0 ? "" :
                L("orders") + "\n" + string.Join("\n",
                    v.Orders.Select(o => $"{o.AssetClass} {o.Amount:F0} · {o.Status}"));
            MoneyStatementsTitle.Text = L("statements");
            MoneyStatementButton.Content = L("drop_statement");
            MoneyLinksTitle.Text = L("links");
            MoneyLinkInstitution.Header = L("institution");
            MoneyLinkButton.Content = L("link_bank");
            var readings = await ApiClient.Shared.MoneyStatements(s.Uid!, s.Token!);
            MoneyStatementsList.ItemsSource = readings.Select(r => new Row(
                $"{r.Filename} · {r.LineCount} · +{r.TotalIn:F2} −{r.TotalOut:F2}"))
                .ToList();
            var links = await ApiClient.Shared.MoneyLinks(s.Uid!, s.Token!);
            MoneyLinksList.ItemsSource = links.Select(l => new LinkRow(
                l.Id, $"{l.Institution} · {l.Aggregator} · {l.Status}",
                L("sync"), L("revoke_link"))).ToList();
        }
        catch { /* leave as-is */ }
    }

    // -- Statements and bank links: the file to the vault, the consent
    // written down, and a sync that only ever tells the truth --

    private async void OnMoneyDropStatement(object sender, RoutedEventArgs e)
    {
        var text = MoneyStatementBox.Text.Trim();
        if (text.Length == 0) return;
        var s = AppState.Current;
        try
        {
            var v = await ApiClient.Shared.MoneyOverview(s.Uid!, s.Token!);
            var first = v.Accounts.FirstOrDefault();
            if (first is null) return;
            var b64 = System.Convert.ToBase64String(
                System.Text.Encoding.UTF8.GetBytes(text));
            await ApiClient.Shared.MoneyDropStatement(
                s.Uid!, s.Token!, first.Id, b64);
            MoneyStatementBox.Text = "";
            await LoadMoney();
        }
        catch (Exception ex) { MoneyStatus.Text = ex.Message; }
    }

    private async void OnMoneyLinkBank(object sender, RoutedEventArgs e)
    {
        var institution = MoneyLinkInstitution.Text.Trim();
        if (institution.Length == 0) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.MoneyLinkBank(
                s.Uid!, s.Token!, institution, "plaid");
            MoneyLinkInstitution.Text = "";
            await LoadMoney();
        }
        catch (Exception ex) { MoneyStatus.Text = ex.Message; }
    }

    private async void OnMoneySyncBank(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string linkId) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.MoneySyncBank(s.Uid!, s.Token!, linkId);
            await LoadMoney();
        }
        catch (Exception ex) { MoneyStatus.Text = ex.Message; }
    }

    private async void OnMoneyRevokeLink(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string linkId) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.MoneyRevokeLink(s.Uid!, s.Token!, linkId);
            await LoadMoney();
        }
        catch (Exception ex) { MoneyStatus.Text = ex.Message; }
    }

    private async void OnMoneyAdd(object sender, RoutedEventArgs e)
    {
        var institution = MoneyInstitution.Text.Trim();
        if (institution.Length == 0) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.MoneyAddAccount(s.Uid!, s.Token!, "checking",
                institution, MoneyAccountNumber.Password, MoneyRoutingNumber.Password);
            MoneyInstitution.Text = "";
            MoneyAccountNumber.Password = "";
            MoneyRoutingNumber.Password = "";
            MoneyStatus.Text = "";
            await LoadMoney();
        }
        catch (Exception ex) { MoneyStatus.Text = ex.Message; }
    }

    private async void OnMoneyObserve(object sender, RoutedEventArgs e)
    {
        if (!double.TryParse(MoneyBalance.Text.Trim(), out var balance)) return;
        var s = AppState.Current;
        try
        {
            var v = await ApiClient.Shared.MoneyOverview(s.Uid!, s.Token!);
            var first = v.Accounts.FirstOrDefault();
            if (first is null) return;
            var seen = await ApiClient.Shared.MoneyObserve(s.Uid!, s.Token!, first.Id, balance);
            MoneyWarningsText.Text = string.Join("\n", seen.Warnings.Select(w => w.Message));
            string doorsLabel = _moneyLabels.TryGetValue("doors", out var dl) ? dl : "";
            var doorLines = seen.Warnings
                .Where(w => w.Doors is not null)
                .SelectMany(w =>
                    (w.Doors!.Specialist?.Label is string sp ? new[] { $"· {sp}" } : Array.Empty<string>())
                    .Concat(w.Doors!.Desks.Select(d => $"· {d.Name} — {d.Trade} {d.Location}")))
                .ToArray();
            MoneyDoorsText.Text = doorLines.Length == 0 ? "" : doorsLabel + "\n" + string.Join("\n", doorLines);
            await LoadMoney();
        }
        catch (Exception ex) { MoneyStatus.Text = ex.Message; }
    }

    private async void OnMoneySetGoal(object sender, RoutedEventArgs e)
    {
        if (!double.TryParse(MoneyGoal.Text.Trim(), out var goal)) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.MoneySetSavings(s.Uid!, s.Token!, goal);
            MoneyStatus.Text = "";
            await LoadMoney();
        }
        catch (Exception ex) { MoneyStatus.Text = ex.Message; }
    }

    private async void OnMoneySetFloor(object sender, RoutedEventArgs e)
    {
        if (!double.TryParse(MoneyFloorBox.Text.Trim(), out var floor)) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.MoneySetFloor(s.Uid!, s.Token!, floor);
            MoneyStatus.Text = "";
            await LoadMoney();
        }
        catch (Exception ex) { MoneyStatus.Text = ex.Message; }
    }

    private async void OnMoneyMandate(object sender, RoutedEventArgs e)
    {
        var scope = MoneyScope.Text.Trim();
        if (scope.Length == 0) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.MoneySetMandate(s.Uid!, s.Token!, true, 500, 1000, scope);
            MoneyStatus.Text = "";
            await LoadMoney();
        }
        // The refusal that matters here is the 402: its message names the
        // plan that buys the handover, in the reader's language. Show it.
        catch (Exception ex) { MoneyStatus.Text = ex.Message; }
    }

    private async void OnMoneyRevoke(object sender, RoutedEventArgs e)
    {
        // Never gated and never preconditioned: taking your hands back has
        // no price, so this button works whatever state the form is in.
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.MoneySetMandate(s.Uid!, s.Token!, false, 0, 0, "");
            MoneyStatus.Text = "";
            await LoadMoney();
        }
        catch (Exception ex) { MoneyStatus.Text = ex.Message; }
    }

    // -- Schedule + the tandem shops shelf --
    // As with Money: every visible string comes from the views' own labels.

    private async System.Threading.Tasks.Task LoadSchedule()
    {
        var s = AppState.Current;
        try
        {
            var v = await ApiClient.Shared.ScheduleView(s.Uid!, s.Token!);
            string L(string key) => v.Labels.TryGetValue(key, out var t) ? t : "";
            SchedulePivot.Header = L("title");
            ScheduleNote.Text = v.Note;
            ApptTitle.Header = L("what");
            ApptWhen.Header = L("when");
            ApptWhere.Header = L("where");
            ApptEmail.Content = v.EmailAvailable ? L("email_me") : L("no_email");
            ApptEmail.IsEnabled = v.EmailAvailable;
            BookButton.Content = L("book");
            CancelApptId.Header = L("upcoming");
            CancelApptButton.Content = L("cancel");
            ApptList.ItemsSource = v.Appointments.Select(a => new Row(
                $"{a.Id} · {a.Title} · {a.WhenAt[..16].Replace("T", " ")}" +
                (a.WhereAt is null ? "" : $" · {a.WhereAt}"))).ToList();
        }
        catch { /* leave as-is */ }
    }

    public record Row(string Line);

    private async void OnBook(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var title = ApptTitle.Text.Trim();
        var when = ApptWhen.Text.Trim();
        if (title.Length == 0 || when.Length == 0) return;
        try
        {
            await ApiClient.Shared.ScheduleBook(s.Uid!, s.Token!, title, when,
                ApptWhere.Text.Trim(), ApptEmail.IsChecked == true);
            ApptTitle.Text = ""; ApptWhen.Text = ""; ApptWhere.Text = "";
            ScheduleStatus.Text = "";
            await LoadSchedule();
        }
        catch (Exception ex) { ScheduleStatus.Text = ex.Message; }
    }

    private async void OnCancelAppt(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var id = CancelApptId.Text.Trim();
        if (id.Length == 0) return;
        try
        {
            await ApiClient.Shared.ScheduleCancel(s.Uid!, s.Token!, id);
            CancelApptId.Text = "";
            ScheduleStatus.Text = "";
            await LoadSchedule();
        }
        catch (Exception ex) { ScheduleStatus.Text = ex.Message; }
    }

    private async System.Threading.Tasks.Task LoadTandemShops()
    {
        var s = AppState.Current;
        try
        {
            var v = await ApiClient.Shared.ShoppingView(s.Uid!, s.Token!);
            string L(string key) => v.Labels.TryGetValue(key, out var t) ? t : "";
            ShopPivot.Header = L("title");
            ShopNote.Text = v.Note;
            OrderShopId.Header = L("title");
            OrderOffering.Header = L("offerings");
            TandemOrderButton.Content = L("order");
            CancelOrderId.Header = L("receipts");
            TandemCancelButton.Content = L("cancel");
            TandemShopList.ItemsSource = v.Shops.Select(x => new Row(
                $"{x.Id} · {x.Name} · {x.Seller}" +
                (x.Tag is null ? "" : $" · {x.Tag}"))).ToList();
            ReceiptList.ItemsSource = v.Receipts.Select(r => new Row(
                $"{r.QrmeOrderId} · {r.Title} · {r.Amount:F2} {r.Currency} · {r.Status}"))
                .ToList();
        }
        catch { /* leave as-is */ }
    }

    private async void OnTandemOrder(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var shop = OrderShopId.Text.Trim();
        var offering = OrderOffering.Text.Trim();
        if (shop.Length == 0 || offering.Length == 0) return;
        try
        {
            await ApiClient.Shared.ShoppingOrder(s.Uid!, s.Token!, shop,
                                                 offering, 1);
            OrderOffering.Text = "";
            ShopStatus.Text = "";
            await LoadTandemShops();
        }
        catch (Exception ex) { ShopStatus.Text = ex.Message; }
    }

    private async void OnTandemCancel(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var id = CancelOrderId.Text.Trim();
        if (id.Length == 0) return;
        try
        {
            await ApiClient.Shared.ShoppingCancel(s.Uid!, s.Token!, id);
            CancelOrderId.Text = "";
            ShopStatus.Text = "";
            await LoadTandemShops();
        }
        catch (Exception ex) { ShopStatus.Text = ex.Message; }
    }
    // -- Your circle --
    // As with Money and Schedule: every visible string comes from the
    // view's own labels; the switches only reflect the server after load.

    private bool _circleLoading;

    private async System.Threading.Tasks.Task LoadCircle()
    {
        var s = AppState.Current;
        try
        {
            var v = await ApiClient.Shared.CircleView(s.Uid!, s.Token!);
            string L(string key) => v.Labels.TryGetValue(key, out var t) ? t : "";
            _circleLoading = true;
            CirclePivot.Header = L("title");
            CircleNote.Text = v.Note;
            InviteId.Header = L("invite");
            InviteButton.Content = L("invite");
            LeaveButton.Content = L("leave");
            DmWith.Header = L("to");
            OpenThreadButton.Content = L("open");
            DmDraft.Header = L("send");
            DmSendButton.Content = L("send");
            MessagingSwitch.Header = L("sw_messaging");
            HomepageSwitch.Header = L("sw_homepage");
            MessagingSwitch.IsOn = v.Features.TryGetValue("messaging", out var m) && m;
            HomepageSwitch.IsOn = v.Features.TryGetValue("homepage", out var h) && h;
            PageHeadline.Header = L("headline");
            PageAbout.Header = L("about");
            PageBg.Header = L("background");
            PageAccent.Header = L("accent");
            PageSaveButton.Content = L("save");
            VisitId.Header = L("visit_id");
            VisitButton.Content = L("visit");
            PageHeadline.Text = v.Homepage.Headline;
            PageAbout.Text = v.Homepage.About;
            PageBg.Text = v.Homepage.Theme.Bg;
            PageAccent.Text = v.Homepage.Theme.Accent;
            var people = v.Circle.Contacts.Select(p => new Row(
                    $"{p.UserId} · {p.DisplayName ?? ""} · {L("contacts")}"))
                .Concat(v.Circle.InvitedMe.Select(p => new Row(
                    $"{p.UserId} · {p.DisplayName ?? ""} · {L("invited_me")}")))
                .Concat(v.Circle.Awaiting.Select(p => new Row(
                    $"{p.UserId} · {p.DisplayName ?? ""} · {L("awaiting")}")))
                .ToList();
            CirclePeople.ItemsSource = people;
            CircleThreads.ItemsSource = v.Threads.Select(t => new Row(
                $"{t.OtherId} · {t.OtherName ?? ""} · {t.MessagesCount}")).ToList();
            _circleLoading = false;
        }
        catch { _circleLoading = false; /* leave as-is */ }
    }

    private async void OnCircleInvite(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var other = InviteId.Text.Trim();
        if (other.Length == 0) return;
        try
        {
            await ApiClient.Shared.CircleInvite(s.Uid!, s.Token!, other);
            InviteId.Text = "";
            CircleStatus.Text = "";
            await LoadCircle();
        }
        catch (Exception ex) { CircleStatus.Text = ex.Message; }
    }

    private async void OnCircleLeave(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var other = InviteId.Text.Trim();
        if (other.Length == 0) return;
        try
        {
            await ApiClient.Shared.CircleLeave(s.Uid!, s.Token!, other);
            InviteId.Text = "";
            CircleStatus.Text = "";
            await LoadCircle();
        }
        catch (Exception ex) { CircleStatus.Text = ex.Message; }
    }

    private async void OnCircleOpenThread(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var other = DmWith.Text.Trim();
        if (other.Length == 0) return;
        try
        {
            var box = await ApiClient.Shared.CircleThread(s.Uid!, s.Token!, other);
            CircleThreadList.ItemsSource = box.Messages.Select(m => new Row(
                (m.SenderId == s.Uid ? "→ " : "← ") + m.Body)).ToList();
            CircleStatus.Text = "";
        }
        catch (Exception ex) { CircleStatus.Text = ex.Message; }
    }

    private async void OnCircleSend(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var other = DmWith.Text.Trim();
        var words = DmDraft.Text.Trim();
        if (other.Length == 0 || words.Length == 0) return;
        try
        {
            await ApiClient.Shared.CircleSend(s.Uid!, s.Token!, other, words);
            DmDraft.Text = "";
            CircleStatus.Text = "";
            OnCircleOpenThread(sender, e);
            await LoadCircle();
        }
        catch (Exception ex) { CircleStatus.Text = ex.Message; }
    }

    private async void OnMessagingSwitch(object sender, RoutedEventArgs e)
    {
        if (_circleLoading) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.CircleSetFeature(s.Uid!, s.Token!,
                "messaging", MessagingSwitch.IsOn);
            CircleStatus.Text = "";
        }
        catch (Exception ex) { CircleStatus.Text = ex.Message; }
    }

    private async void OnHomepageSwitch(object sender, RoutedEventArgs e)
    {
        if (_circleLoading) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.CircleSetFeature(s.Uid!, s.Token!,
                "homepage", HomepageSwitch.IsOn);
            CircleStatus.Text = "";
        }
        catch (Exception ex) { CircleStatus.Text = ex.Message; }
    }

    private async void OnCircleSavePage(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.CircleEditHomepage(s.Uid!, s.Token!,
                PageHeadline.Text.Trim(), PageAbout.Text.Trim(),
                PageBg.Text.Trim(), PageAccent.Text.Trim());
            CircleStatus.Text = "";
            await LoadCircle();
        }
        catch (Exception ex) { CircleStatus.Text = ex.Message; }
    }

    private async void OnCircleVisit(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var other = VisitId.Text.Trim();
        if (other.Length == 0) return;
        try
        {
            var page = await ApiClient.Shared.CircleHomepage(s.Uid!, s.Token!, other);
            var tops = string.Join(" · ",
                page.TopFriends.Select(t => t.DisplayName ?? t.UserId));
            var links = string.Join("\n",
                page.Links.Select(l => $"{l.Label} · {l.Url}"));
            VisitedPage.Text = $"{page.DisplayName ?? page.UserId} — " +
                $"{page.Headline}\n{page.About}\n{links}" +
                (tops.Length > 0 ? $"\n{tops}" : "");
            CircleStatus.Text = "";
        }
        catch (Exception ex) { CircleStatus.Text = ex.Message; }
    }

    // -- The medicine cabinet (console door since 0.9.0; this is the
    //    desktop's). The board is rebuilt in code because a med row nests
    //    slot rows with their own buttons, which an ItemsControl template
    //    cannot express without a view-model layer this page doesn't have.

    private void LocalizeMeds()
    {
        MedHead.Text = L10n.T("ns.med.title");
        MedToday.Text = L10n.T("ns.med.today");
        MedNone.Text = L10n.T("ns.med.none");
        MedAdherenceButton.Content =
            L10n.T("ns.med.last").Replace("{n}", "7");
        MedAddToggle.Content = L10n.T("ns.med.add");
        MedAddPitch.Text = L10n.T("ns.med.add.pitch");
        MedName.Header = L10n.T("ns.med.name");
        MedName.PlaceholderText = L10n.T("ns.med.name.ph");
        MedDose.Header = L10n.T("ns.med.dose");
        MedDose.PlaceholderText = L10n.T("ns.med.dose.ph");
        MedPurpose.Header = L10n.T("ns.med.purpose");
        MedPurpose.PlaceholderText = L10n.T("ns.med.purpose.ph");
        MedAsNeeded.Content = L10n.T("ns.med.asneeded");
        MedTimes.Header = L10n.T("ns.med.times") + L10n.T("ns.med.times.note");
        MedCeiling.Header = L10n.T("ns.med.ceiling") + " "
            + L10n.T("ns.med.ceiling.note");
        MedCritical.Content = L10n.T("ns.med.critical");
        MedAddButton.Content = L10n.T("ns.med.add");
    }

    private async System.Threading.Tasks.Task LoadMeds()
    {
        var s = AppState.Current;
        try
        {
            RenderMeds(await ApiClient.Shared.MedsBoard(s.Uid!, s.Token!));
        }
        catch { /* leave as-is */ }
    }

    private void RenderMeds(MedsBoard board)
    {
        MedError.Visibility = Visibility.Collapsed;
        MedMissed.Visibility = board.MissedCritical.Length > 0
            ? Visibility.Visible : Visibility.Collapsed;
        if (board.MissedCritical.Length > 0)
            MedMissed.Text = L10n.T("ns.med.missed").Replace("{list}",
                string.Join(", ", board.MissedCritical.Select(
                    m => $"{m.Name} ({m.Slot})")));
        MedNone.Visibility = board.Medications.Length == 0
            ? Visibility.Visible : Visibility.Collapsed;
        MedDisclaimer.Text = board.Disclaimer;

        MedRows.Children.Clear();
        foreach (var med in board.Medications)
        {
            var row = new StackPanel { Spacing = 2 };
            var head = new StackPanel
            { Orientation = Orientation.Horizontal, Spacing = 8 };
            head.Children.Add(new TextBlock
            {
                Text = $"{med.Name} · {med.Dose}",
                FontWeight = Microsoft.UI.Text.FontWeights.Bold,
                FontSize = 12,
                Foreground = (Microsoft.UI.Xaml.Media.Brush)
                    Application.Current.Resources["JimTxtBrush"],
            });
            var stop = new Button
            { Content = L10n.T("ns.med.stop"), FontSize = 11 };
            var medId = med.Id;
            stop.Click += async (_, _) =>
            {
                var st = AppState.Current;
                try
                {
                    await ApiClient.Shared.StopMed(st.Uid!, st.Token!, medId);
                    await LoadMeds();
                }
                catch (Exception ex) { ShowMedError(ex); }
            };
            head.Children.Add(stop);
            row.Children.Add(head);
            if (med.Purpose is { Length: > 0 })
                row.Children.Add(SmallText(med.Purpose, "JimT2Brush", 11));
            // The console's "worth a check-in" checkbox, as a toggle.
            var critical = new Microsoft.UI.Xaml.Controls.Primitives.ToggleButton
            {
                Content = L10n.T("ns.med.critical"),
                FontSize = 10,
                IsChecked = med.Critical,
            };
            var wasCritical = med.Critical;
            critical.Click += async (_, _) =>
            {
                var st = AppState.Current;
                try
                {
                    await ApiClient.Shared.SetMedCritical(st.Uid!, st.Token!,
                                                          medId, !wasCritical);
                    await LoadMeds();
                }
                catch (Exception ex) { ShowMedError(ex); }
            };
            row.Children.Add(critical);
            if (med.Kind == "as_needed")
            {
                var line = new StackPanel
                { Orientation = Orientation.Horizontal, Spacing = 8 };
                line.Children.Add(SmallText(
                    L10n.T("ns.med.asneeded.line")
                        .Replace("{n}", (med.TakenToday ?? 0).ToString())
                        .Replace("{max}", med.MaxPerDay is { } max
                            ? L10n.T("ns.med.asneeded.max")
                                .Replace("{max}", max.ToString())
                            : ""),
                    "JimT2Brush", 11));
                var take = new Button
                { Content = L10n.T("ns.med.tookone"), FontSize = 11 };
                take.Click += (_, _) => LogDose(medId, "taken", null);
                line.Children.Add(take);
                row.Children.Add(line);
            }
            else foreach (var slot in med.Slots ?? Array.Empty<MedSlot>())
            {
                var line = new StackPanel
                { Orientation = Orientation.Horizontal, Spacing = 8 };
                line.Children.Add(SmallText($"{slot.Slot} · {slot.Status}",
                    slot.Status == "missed" ? "JimAmberBrush" : "JimT2Brush",
                    11));
                if (slot.Status is "due" or "missed")
                {
                    var slotName = slot.Slot;
                    var take = new Button
                    { Content = L10n.T("ns.med.take"), FontSize = 11 };
                    take.Click += (_, _) => LogDose(medId, "taken", slotName);
                    var skip = new Button
                    { Content = L10n.T("ns.med.skip"), FontSize = 11 };
                    skip.Click += (_, _) => LogDose(medId, "skipped", slotName);
                    line.Children.Add(take);
                    line.Children.Add(skip);
                }
                row.Children.Add(line);
            }
            MedRows.Children.Add(row);
        }
    }

    private static TextBlock SmallText(string text, string brush, int size) =>
        new()
        {
            Text = text,
            FontSize = size,
            TextWrapping = TextWrapping.Wrap,
            Foreground = (Microsoft.UI.Xaml.Media.Brush)
                Application.Current.Resources[brush],
        };

    private void ShowMedError(Exception ex)
    {
        MedError.Text = ex.Message;
        MedError.Visibility = Visibility.Visible;
    }

    private async void LogDose(string medId, string action, string? slot)
    {
        var s = AppState.Current;
        try
        {
            // The log answers with the refreshed board — one round trip.
            RenderMeds(await ApiClient.Shared.LogDose(s.Uid!, s.Token!,
                                                      medId, action, slot));
        }
        catch (Exception ex) { ShowMedError(ex); }
    }

    private async void OnMedAdherence(object sender, RoutedEventArgs e)
    {
        if (MedAdherenceRows.Visibility == Visibility.Visible)
        {
            MedAdherenceRows.Visibility = Visibility.Collapsed;
            return;
        }
        var s = AppState.Current;
        try
        {
            var adherence = await ApiClient.Shared.MedAdherence(s.Uid!,
                                                                s.Token!);
            MedAdherenceRows.Children.Clear();
            foreach (var row in adherence.Medications)
                MedAdherenceRows.Children.Add(SmallText(
                    $"{row.Name} — " + L10n.T("ns.med.of")
                        .Replace("{taken}", row.Taken.ToString())
                        .Replace("{expected}", row.Expected.ToString()),
                    "JimT2Brush", 11));
            MedAdherenceRows.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowMedError(ex); }
    }

    private void OnMedAddToggle(object sender, RoutedEventArgs e) =>
        MedAddForm.Visibility = MedAddForm.Visibility == Visibility.Visible
            ? Visibility.Collapsed : Visibility.Visible;

    private void OnMedAsNeededToggle(object sender, RoutedEventArgs e)
    {
        var asNeeded = MedAsNeeded.IsChecked == true;
        MedTimes.Visibility = asNeeded ? Visibility.Collapsed
                                       : Visibility.Visible;
        MedCeiling.Visibility = asNeeded ? Visibility.Visible
                                         : Visibility.Collapsed;
    }

    private async void OnMedAdd(object sender, RoutedEventArgs e)
    {
        var name = MedName.Text.Trim();
        var dose = MedDose.Text.Trim();
        if (name.Length == 0 || dose.Length == 0) return;
        object schedule;
        if (MedAsNeeded.IsChecked == true)
            schedule = int.TryParse(MedCeiling.Text.Trim(), out var max)
                       && max > 0
                ? new { as_needed = true, max_per_day = max }
                : (object)new { as_needed = true };
        else
        {
            var times = MedTimes.Text.Split(',')
                .Select(t => t.Trim()).Where(t => t.Length > 0).ToArray();
            if (times.Length == 0) return;
            schedule = new { times };
        }
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.AddMed(s.Uid!, s.Token!, name, dose,
                schedule, MedPurpose.Text.Trim(),
                MedCritical.IsChecked == true);
            MedName.Text = ""; MedDose.Text = ""; MedPurpose.Text = "";
            MedTimes.Text = ""; MedCeiling.Text = "";
            MedAsNeeded.IsChecked = false; MedCritical.IsChecked = false;
            MedAddForm.Visibility = Visibility.Collapsed;
            await LoadMeds();
        }
        catch (Exception ex) { ShowMedError(ex); }
    }

    // ---- budgets: this much per month for this category ----

    private async System.Threading.Tasks.Task LoadBudgets()
    {
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            var sheet = await ApiClient.Shared.Budgets(s.Uid, s.Token);
            BudRows.Children.Clear();
            BudNone.Visibility = sheet.Rows.Length == 0
                ? Visibility.Visible : Visibility.Collapsed;
            foreach (var row in sheet.Rows)
            {
                var line = new StackPanel
                { Orientation = Orientation.Horizontal, Spacing = 8 };
                line.Children.Add(new TextBlock
                {
                    Text = row.Category + " " + L10n.T("aim.budget.line")
                        .Replace("{spent}", $"${(int)row.Spent}")
                        .Replace("{limit}", $"${(int)row.MonthlyLimit}")
                        .Replace("{standing}", row.Standing),
                    FontSize = 11,
                    TextWrapping = TextWrapping.Wrap,
                    Foreground = (Microsoft.UI.Xaml.Media.Brush)
                        Application.Current.Resources["JimT2Brush"],
                });
                var remove = new Button
                {
                    Content = L10n.T("aim.budget.remove"), FontSize = 11,
                    Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
                        Microsoft.UI.Colors.Transparent),
                };
                var category = row.Category;
                remove.Click += async (_, _) =>
                {
                    try
                    {
                        await ApiClient.Shared.ClearBudget(s.Uid, s.Token,
                                                           category);
                        await LoadBudgets();
                    }
                    catch (Exception ex) { ShowBudgetError(ex.Message); }
                };
                line.Children.Add(remove);
                BudRows.Children.Add(line);
            }
        }
        catch { /* backend offline */ }
    }

    private async void OnSetBudget(object sender, RoutedEventArgs e)
    {
        var category = BudCategory.Text.Trim();
        if (category.Length == 0) return;
        var s = AppState.Current;
        if (s.Uid is null || s.Token is null) return;
        try
        {
            await ApiClient.Shared.SetBudget(s.Uid, s.Token, category,
                                             BudLimit.Value);
            BudCategory.Text = "";
            await LoadBudgets();
        }
        catch (Exception ex) { ShowBudgetError(ex.Message); }
    }

    private void ShowBudgetError(string message)
    {
        BudError.Text = message;
        BudError.Visibility = Visibility.Visible;
    }
}
