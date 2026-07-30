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
}
