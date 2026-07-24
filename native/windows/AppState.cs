using System;
using System.IO;
using System.Text.Json;

namespace JimGuardian;

/// <summary>
/// The enrolled identity + token, persisted to a small JSON file under
/// LocalApplicationData so the app resumes signed-in (unpackaged-safe).
/// </summary>
public sealed class AppState
{
    public static AppState Current { get; } = Load();

    public string? Uid { get; set; }
    public string? Token { get; set; }
    public string DisplayName { get; set; } = "";
    // The user's chosen language also drives the app chrome via L10n.
    public string Language { get; set; } = "en";

    public void RememberLanguage(string code)
    {
        Language = code;
        Save();
    }

    public bool IsEnrolled => !string.IsNullOrEmpty(Uid) && !string.IsNullOrEmpty(Token);

    private static string PathOnDisk =>
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                     "JimGuardian", "session.json");

    public void SignIn(EnrollResult r)
    {
        Uid = r.Id; Token = r.UserToken; DisplayName = r.DisplayName;
        Save();
    }

    public void SignOut()
    {
        Uid = null; Token = null; DisplayName = "";
        try { File.Delete(PathOnDisk); } catch { /* ignore */ }
    }

    private void Save()
    {
        Directory.CreateDirectory(Path.GetDirectoryName(PathOnDisk)!);
        File.WriteAllText(PathOnDisk, JsonSerializer.Serialize(this));
    }

    private static AppState Load()
    {
        try
        {
            if (File.Exists(PathOnDisk))
                return JsonSerializer.Deserialize<AppState>(File.ReadAllText(PathOnDisk)) ?? new AppState();
        }
        catch { /* fall through to fresh state */ }
        return new AppState();
    }
}
