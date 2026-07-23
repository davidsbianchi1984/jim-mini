using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace JimGuardian;

// MARK: wire models (mirror jim/api.py)

public record EnrollResult(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("user_token")] string UserToken);

public record Guidance(
    [property: JsonPropertyName("delivered")] bool Delivered,
    [property: JsonPropertyName("source")] string? Source,
    [property: JsonPropertyName("content")] string Content);

public record MonitorResult(
    [property: JsonPropertyName("detected")] bool Detected,
    [property: JsonPropertyName("condition")] string? Condition,
    [property: JsonPropertyName("severity")] string? Severity,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("guidance")] Guidance? Guidance);

public record CheckinGuardian(
    [property: JsonPropertyName("guidance")] Guidance? Guidance);

public record CheckinResult(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("guardian")] CheckinGuardian Guardian);

public record BaselineMetric(
    [property: JsonPropertyName("metric")] string Metric,
    [property: JsonPropertyName("value")] double? Value,
    [property: JsonPropertyName("state")] string? State,
    [property: JsonPropertyName("samples")] int? Samples);

public record Goal(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("area")] string Area,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("target")] string? Target,
    [property: JsonPropertyName("status")] string? Status);

public record Habit(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("streak")] int? Streak);

public record JournalItem(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("text")] string? Text,
    [property: JsonPropertyName("created_at")] string? CreatedAt);

public record ProviderInfo(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("configured")] bool Configured);

public record ModelsList(
    [property: JsonPropertyName("providers")] ProviderInfo[] Providers,
    [property: JsonPropertyName("default")] string Default);

public record ModelChoice(
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("effective")] string Effective);

public record EscalationPolicy(
    [property: JsonPropertyName("sensitivity")] string Sensitivity,
    [property: JsonPropertyName("ladder")] string[] Ladder,
    [property: JsonPropertyName("by_severity")] System.Collections.Generic.Dictionary<string, string> BySeverity);

public record FlowStep(
    [property: JsonPropertyName("step")] string Step,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("detail")] string Detail);

public record RobotDirective(
    [property: JsonPropertyName("robot")] string RobotName,
    [property: JsonPropertyName("directive")] string Directive);

public record EmergencyResult(
    [property: JsonPropertyName("emergency")] bool Emergency,
    [property: JsonPropertyName("flow")] FlowStep[] Flow,
    [property: JsonPropertyName("robot_directives")] RobotDirective[]? RobotDirectives);

public record RobotSpec(
    [property: JsonPropertyName("model")] string Model,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("maker")] string Maker);

public record RoboticsCatalog(
    [property: JsonPropertyName("robots")] RobotSpec[] Robots);

public record Robot(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("model")] string Model,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("escalation_directive")] string? EscalationDirective);

/// <summary>
/// Async client for the JIM Guardian backend. Windows reaches the local dev
/// server directly on 127.0.0.1.
/// </summary>
public sealed class ApiClient
{
    public static ApiClient Shared { get; } = new();

    private readonly HttpClient _http = new() { BaseAddress = new Uri("http://127.0.0.1:8000") };

    public void SetBase(string url) => _http.BaseAddress = new Uri(url.TrimEnd('/'));

    private async Task<T> Send<T>(HttpRequestMessage req)
    {
        var res = await _http.SendAsync(req);
        var body = await res.Content.ReadAsStringAsync();
        if (!res.IsSuccessStatusCode)
        {
            string? detail = null;
            try { detail = JsonDocument.Parse(body).RootElement.GetProperty("detail").GetString(); }
            catch { /* non-JSON error body */ }
            throw new HttpRequestException(detail ?? $"HTTP {(int)res.StatusCode}");
        }
        return JsonSerializer.Deserialize<T>(body)!;
    }

    private static HttpRequestMessage Post(string path, object body, string? token = null)
    {
        var req = new HttpRequestMessage(HttpMethod.Post, path) { Content = JsonContent.Create(body) };
        if (token is not null) req.Headers.Add("authorization", $"Bearer {token}");
        return req;
    }

    public Task<EnrollResult> Enroll(string name, string birthdate) =>
        Send<EnrollResult>(Post("/enroll",
            new { display_name = name, birthdate, terms_consent = true }));

    public Task<MonitorResult> Monitor(string uid, string token, int heartRate, double stress) =>
        Send<MonitorResult>(Post($"/monitor/{uid}",
            new { heart_rate = heartRate, stress_level = stress }, token));

    public Task<CheckinResult> Checkin(string uid, string token, int mood, int energy, string note) =>
        Send<CheckinResult>(Post($"/checkin/{uid}",
            new { mood, energy, note }, token));

    public Task<Guidance> Coach(string uid, string token, string area, string message) =>
        Send<Guidance>(Post($"/coach/{uid}", new { area, message }, token));

    public async Task<BaselineMetric[]> Baseline(string uid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/baseline/{uid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return await Send<BaselineMetric[]>(req);
    }

    // -- life: goals, habits, journal --

    private HttpRequestMessage Get(string path, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, path);
        req.Headers.Add("authorization", $"Bearer {token}");
        return req;
    }

    public Task<Goal[]> Goals(string uid, string token) => Send<Goal[]>(Get($"/goals/{uid}", token));

    public Task<Goal> AddGoal(string uid, string token, string area, string title, string? target) =>
        Send<Goal>(Post($"/goals/{uid}",
            target is { Length: > 0 } ? new { area, title, target } : (object)new { area, title }, token));

    public Task<Habit[]> Habits(string uid, string token) => Send<Habit[]>(Get($"/habits/{uid}", token));

    public Task<Habit> AddHabit(string uid, string token, string name) =>
        Send<Habit>(Post($"/habits/{uid}", new { name }, token));

    public async Task LogHabit(string uid, string token, string habitId)
    {
        var req = Post($"/habits/{uid}/{habitId}/log", new { }, token);
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<JournalItem[]> Journal(string uid, string token) => Send<JournalItem[]>(Get($"/journal/{uid}", token));

    public async Task AddJournal(string uid, string token, string text)
    {
        var req = Post($"/journal/{uid}", new { text }, token);
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    // -- model selection --

    public Task<ModelsList> Models() =>
        Send<ModelsList>(new HttpRequestMessage(HttpMethod.Get, "/models"));

    public Task<ModelChoice> UserModel(string uid, string token) =>
        Send<ModelChoice>(Get($"/model/{uid}", token));

    public Task<ModelChoice> SetModel(string uid, string token, string provider)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, $"/model/{uid}")
        {
            Content = JsonContent.Create(new { provider }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ModelChoice>(req);
    }

    // -- safety: escalation policy, Emergency, robots --

    public Task<EscalationPolicy> EscalationPolicy(string uid, string token) =>
        Send<EscalationPolicy>(Get($"/escalation-policy/{uid}", token));

    public async Task SetSensitivity(string uid, string token, string level)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, $"/sensitivity/{uid}")
        {
            Content = JsonContent.Create(new { level }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<EmergencyResult> Emergency(string uid, string token,
                                           string? situation, string? location) =>
        Send<EmergencyResult>(Post($"/emergency/{uid}",
            new { situation, location }, token));

    public Task<RoboticsCatalog> Robotics() =>
        Send<RoboticsCatalog>(new HttpRequestMessage(HttpMethod.Get, "/robotics/catalog"));

    public Task<Robot[]> Robots(string uid, string token) =>
        Send<Robot[]>(Get($"/robots/{uid}", token));

    public Task<Robot> BindRobot(string uid, string token, string model) =>
        Send<Robot>(Post($"/robots/{uid}", new { model }, token));
}
