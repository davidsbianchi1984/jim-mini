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
        await LoadMoney();
        await LoadSchedule();
        await LoadTandemShops();
        await LoadCircle();
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
            // Enumerable.Reverse by name: `entries` is a JournalItem[], and an
            // array converts to Span<T>, so plain .Reverse() binds to
            // MemoryExtensions' in-place void overload and the .Select below
            // then has nothing to attach to.
            JournalList.ItemsSource = Enumerable.Reverse(entries)
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

    // -- Money --
    //
    // Every visible string on this pivot comes from the overview's own
    // `labels` — composed server-side in the reader's language, exactly as
    // the desktop Money card renders them — because the English count behind
    // this shell's tabs is a ratchet and this pivot must not feed it. Until
    // the overview loads, the controls carry no words at all.

    public record AccountRow(string Line, string Balance);

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
            MoneyMandateTitle.Text = L("mandate");
            MoneyScope.Header = L("scope");
            MoneyMandateButton.Content = L("mandate_save");
            MoneyRevokeButton.Content = L("mandate_revoke");
            MoneyOrdersText.Text = v.Orders.Length == 0 ? "" :
                L("orders") + "\n" + string.Join("\n",
                    v.Orders.Select(o => $"{o.AssetClass} {o.Amount:F0} · {o.Status}"));
        }
        catch { /* leave as-is */ }
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
                $"{t.OtherId} · {t.OtherName ?? ""} · {t.Messages}")).ToList();
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
}
