using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace JimGuardian;

/// <summary>One failure, with nothing in it that belongs to anybody.</summary>
public sealed class Problem
{
    /// <summary>`POST /profiles/{id}/chat` — the operation, not the instance.</summary>
    public string Op { get; set; } = "";
    /// <summary>HTTP status, or 0 when the request never reached a server.</summary>
    public int Status { get; set; }
    public int Count { get; set; }
    /// <summary>ISO date only. A timestamp to the second is a movement record.</summary>
    public string Day { get; set; } = "";
    public string Fingerprint { get; set; } = "";
    /// <summary>
    /// How much of <see cref="Count"/> has already been reported. A number,
    /// not a flag: a row keeps accumulating after a send, and the next report
    /// owes the difference.
    /// </summary>
    public int Sent { get; set; }
}

/// <summary>
/// What went wrong, recorded without recording anything private.
///
/// The console's <c>app/src/errors.ts</c> in this repository, in C#. Same
/// rules, same refusals — written from that file rather than invented again,
/// so the two cannot drift into disagreeing about what a failure may say
/// about itself.
///
/// Every failed request passes through one place in <c>ApiClient</c>, so one
/// call there catches the lot. The hard part is not the catching. The backends
/// put user input straight into their error messages — <i>no device called
/// 'Pixel Buds' on this account</i>, <i>unknown site 'knee'</i> — good
/// messages for the person reading them, and device names and body sites to
/// anybody else. The message is shown and never written down.
///
/// The path goes the same way: <c>/profiles/prf_0de08e794ed0/chat</c>
/// identifies a person, <c>POST /profiles/{id}/chat</c> identifies a bug, and
/// only the second is kept. Redaction happens on the way <i>in</i>, so the
/// stored buffer never holds something that would later have to be scrubbed.
/// </summary>
public static class Problems
{
    private const int Limit = 50;

    private static string Store => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "jim-mini", "problems.json");

    /// <summary>
    /// A segment that identifies a <i>thing</i> rather than naming a route.
    ///
    /// Deliberately wide: over-redacting costs a little precision in a bug
    /// report, under-redacting costs somebody their privacy, and only one of
    /// those is recoverable. The suffix length is unbounded because an id
    /// minted short is still an id — requiring six hex characters let
    /// <c>cap_9f2</c>, <c>req_77aa</c> and <c>usr_1</c> through when the
    /// console's version of this was first written.
    /// </summary>
    private static readonly Regex[] IdLike =
    {
        new(@"^[a-z]{2,8}_[0-9a-z]+$", RegexOptions.IgnoreCase),
        new(@"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            RegexOptions.IgnoreCase),
        new(@"^[0-9]+$"),
        new(@"^[A-Za-z0-9_-]{24,}$"),
    };

    /// <summary>A path with every identifying segment replaced by {id}.</summary>
    public static string Redact(string path)
    {
        var noQuery = path.Split('?')[0];
        return string.Join("/", noQuery.Split('/').Select(seg =>
            seg.Length > 0 && IdLike.Any(re => re.IsMatch(seg)) ? "{id}" : seg));
    }

    /// <summary>
    /// Non-reversible by construction — its input already carries nothing
    /// private. FNV-1a, matching the console so the same failure fingerprints
    /// the same on a desktop and on a phone.
    /// </summary>
    private static string Fingerprint(string op, int status)
    {
        uint h = 2166136261;
        foreach (var b in Encoding.UTF8.GetBytes($"{op}|{status}"))
        {
            h ^= b;
            h *= 16777619;
        }
        return h.ToString("x8", CultureInfo.InvariantCulture);
    }

    private static List<Problem> Read()
    {
        try
        {
            if (!File.Exists(Store)) return new List<Problem>();
            return JsonSerializer.Deserialize<List<Problem>>(File.ReadAllText(Store))
                   ?? new List<Problem>();
        }
        catch
        {
            return new List<Problem>();
        }
    }

    private static void Write(List<Problem> rows)
    {
        // A full or unavailable store is not worth an error of its own. The
        // diagnostic is the least important thing in the app; it must never be
        // the reason something else fails.
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(Store)!);
            File.WriteAllText(Store,
                JsonSerializer.Serialize(rows.Take(Limit).ToList()));
        }
        catch
        {
        }
    }

    /// <summary>
    /// Record a failure. Takes the method and raw path, never the message.
    ///
    /// The signature is the safeguard: there is no parameter a detail string
    /// could arrive through, so a future caller cannot pass one in a hurry.
    /// </summary>
    public static void Record(string method, string path, int status)
    {
        var op = $"{method.ToUpperInvariant()} {Redact(path)}";
        var print = Fingerprint(op, status);
        var day = DateTime.UtcNow.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);

        var rows = Read();
        var hit = rows.FirstOrDefault(r => r.Fingerprint == print);
        if (hit is not null)
        {
            hit.Count += 1;
            hit.Day = day;
            rows.Remove(hit);
            rows.Insert(0, hit);
        }
        else
        {
            rows.Insert(0, new Problem
            {
                Op = op, Status = status, Count = 1,
                Day = day, Fingerprint = print, Sent = 0,
            });
        }
        Write(rows);
    }

    /// <summary>The whole local history, which is the person's own.</summary>
    public static IReadOnlyList<Problem> All() => Read();

    public static void Clear()
    {
        try { if (File.Exists(Store)) File.Delete(Store); } catch { }
    }

    // ---- Reporting -------------------------------------------------------
    //
    // Everything above this line existed for four releases and did half a job.
    // Record redacts on the way in, and Sent was documented as "how much of
    // Count has already been reported" — describing a send that was never
    // written. The buffer filled, capped at fifty, and rolled over. Nothing
    // ever read Sent, because nothing ever reported.
    //
    //     asked     is the failure recorded without recording anything private
    //     mattered  does the failure reach anybody
    //
    // The console's app/src/errors.ts had both halves the whole time.

    /// <summary>
    /// Which product this is. Not defaulted: "unknown" is a source the gateway
    /// refuses, so a shell that forgot to set it finds out on the first report
    /// rather than filing one app's bugs under another's name.
    /// </summary>
    public const string Source = "jim-mini";

    private const string CollectorSetting = "problems.collector";
    private const string SendSetting = "problems.send";
    private const string NoticeSetting = "problems.notice";

    /// <summary>
    /// The three choices above, beside the buffer they govern.
    ///
    /// Deliberately not in <c>AppState</c>: that file is emptied when somebody
    /// signs out, and "I turned reporting off" is not a fact about a session.
    /// An answered notice that unanswers itself would ask again forever.
    /// </summary>
    private static string SettingsStore => Path.Combine(
        Path.GetDirectoryName(Store)!, "problems-settings.json");

    private static Dictionary<string, string> ReadSettings()
    {
        try
        {
            if (!File.Exists(SettingsStore)) return new Dictionary<string, string>();
            return JsonSerializer.Deserialize<Dictionary<string, string>>(
                File.ReadAllText(SettingsStore)) ?? new Dictionary<string, string>();
        }
        catch { return new Dictionary<string, string>(); }
    }

    private static string? Get(string name) =>
        ReadSettings().TryGetValue(name, out var v) ? v : null;

    private static void Set(string name, string? value)
    {
        try
        {
            var all = ReadSettings();
            if (value is null) all.Remove(name); else all[name] = value;
            Directory.CreateDirectory(Path.GetDirectoryName(SettingsStore)!);
            File.WriteAllText(SettingsStore, JsonSerializer.Serialize(all));
        }
        catch { /* the choice still holds for this session */ }
    }

    /// <summary>
    /// Where reports go, or "" for nowhere. A stored value wins over the
    /// built-in address so a self-hoster can point at their own gateway, and
    /// so anyone can point at nothing by storing an empty string.
    /// </summary>
    public static string CollectorUrl()
    {
        var stored = Get(CollectorSetting);
        var raw = stored ?? BuildConfig.ProblemCollector;
        return raw.Trim().TrimEnd('/');
    }

    public static void SetCollectorUrl(string? url) => Set(CollectorSetting, url);

    /// <summary>On where a collector exists, off the moment anyone says so.</summary>
    public static bool SendingEnabled() => Get(SendSetting) != "off";

    public static void SetSending(bool on) => Set(SendSetting, on ? "on" : "off");

    /// <summary>
    /// Nothing leaves this machine before somebody has been told and answered.
    /// The gate is the notice, not the switch: a switch defaulting to on is a
    /// decision made on the person's behalf.
    /// </summary>
    public static bool NoticeAnswered() => Get(NoticeSetting) is not null;

    public static void AnswerNotice(bool send)
    {
        Set(NoticeSetting, send ? "yes" : "no");
        SetSending(send);
    }

    /// <summary>
    /// Exactly what a report contains — shown on screen and posted, both from
    /// here, so a preview cannot drift from the payload.
    ///
    /// Count is the <em>unreported remainder</em>, and rows with nothing left
    /// owing are absent. This is not a view of the log; it is the message, and
    /// after a successful send it is legitimately empty.
    /// </summary>
    public static Dictionary<string, object> Report(string appVersion) => new()
    {
        ["source"] = Source,
        ["app_version"] = appVersion,
        ["platform"] = "windows",
        ["language"] = CultureInfo.CurrentUICulture.TwoLetterISOLanguageName,
        ["problems"] = Read()
            .Where(r => r.Count - r.Sent > 0)
            .Select(r => new Dictionary<string, object>
            {
                ["op"] = r.Op, ["status"] = r.Status,
                ["count"] = r.Count - r.Sent,
                ["day"] = r.Day, ["fingerprint"] = r.Fingerprint,
            })
            .ToList(),
    };

    /// <summary>
    /// Advance each row's watermark by what was actually reported — by amount,
    /// never by flag. A row goes on counting while the request is in flight,
    /// and that growth is still owed; a flag would drop it silently.
    /// </summary>
    public static void MarkReported(Dictionary<string, object> report)
    {
        if (report["problems"] is not List<Dictionary<string, object>> sent) return;
        var owed = sent.ToDictionary(r => (string)r["fingerprint"],
                                     r => (int)r["count"]);
        var rows = Read();
        foreach (var row in rows)
        {
            if (owed.TryGetValue(row.Fingerprint, out var n)) row.Sent += n;
        }
        Write(rows);
    }

    /// <summary>
    /// This build's version, from the assembly that shipped it. Not a constant
    /// in the source: a version written down twice disagrees with itself by
    /// the second release.
    /// </summary>
    public static string AppVersion =>
        typeof(Problems).Assembly.GetName().Version?.ToString(3) ?? "0.0.0";

    public enum SendOutcome
    {
        Sent, NothingToSend, TurnedOff, NoCollector, AwaitingNotice, Failed,
    }

    /// <summary>
    /// Post what is owed. Never throws, never blocks anything.
    ///
    /// The gateway answers 422 when a report is not the shape it expects,
    /// which would mean this build's redaction has stopped working. That is a
    /// refusal and not a retry: the watermark stays put, nothing is marked
    /// sent, and the next launch tries again with whatever the fix ships.
    ///
    /// Its own HttpClient rather than ApiClient's: ApiClient records a problem
    /// on every failure, so a failing collector would write a new row each
    /// launch — a log that fills with the story of its own delivery.
    /// </summary>
    public static async System.Threading.Tasks.Task<SendOutcome> Send(string? appVersion = null)
    {
        var baseUrl = CollectorUrl();
        if (baseUrl.Length == 0) return SendOutcome.NoCollector;
        if (!NoticeAnswered()) return SendOutcome.AwaitingNotice;
        if (!SendingEnabled()) return SendOutcome.TurnedOff;

        var payload = Report(appVersion ?? AppVersion);
        if (payload["problems"] is not List<Dictionary<string, object>> rows
            || rows.Count == 0) return SendOutcome.NothingToSend;

        try
        {
            using var http = new System.Net.Http.HttpClient
            {
                Timeout = TimeSpan.FromSeconds(10),
            };
            var token = BuildConfig.ProblemToken;
            if (token.Length > 0)
            {
                http.DefaultRequestHeaders.Authorization =
                    new System.Net.Http.Headers.AuthenticationHeaderValue(
                        "Bearer", token);
            }
            var content = new System.Net.Http.StringContent(
                JsonSerializer.Serialize(payload), Encoding.UTF8,
                "application/json");
            var res = await http.PostAsync($"{baseUrl}/v1/problems", content);
            if (!res.IsSuccessStatusCode) return SendOutcome.Failed;
        }
        catch { return SendOutcome.Failed; }

        MarkReported(payload);
        return SendOutcome.Sent;
    }
}
