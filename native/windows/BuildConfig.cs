namespace JimGuardian;

/// <summary>
/// Values a release build stamps in, and a development build leaves empty.
///
/// The console's equivalent is the <c>define</c> block in
/// <c>app/vite.config.ts</c>, which bakes <c>PROBLEM_COLLECTOR</c> and
/// <c>PROBLEM_TOKEN</c> into the bundle at build time. This is the same idea
/// for the Windows shell, and it exists for the same reason: an install with
/// no address has <em>nowhere</em> to send, which is a stronger default than a
/// flag. A flag can be switched on by a later mistake. A missing address
/// cannot — there is nothing to switch on.
///
/// Stamped by the release workflow with
/// <c>-p:ProblemCollector=… -p:ProblemToken=…</c>, which land here as
/// <c>AssemblyMetadata</c> attributes. Read through <see cref="Value"/> rather
/// than as constants so a build that did not stamp them reads as empty instead
/// of failing to compile — a shell that will not build is a worse outcome than
/// one that quietly reports nothing.
/// </summary>
public static class BuildConfig
{
    private static string Value(string key)
    {
        var assembly = typeof(BuildConfig).Assembly;
        foreach (var attribute in assembly.GetCustomAttributes(
                     typeof(System.Reflection.AssemblyMetadataAttribute), false))
        {
            if (attribute is System.Reflection.AssemblyMetadataAttribute meta
                && meta.Key == key)
            {
                return meta.Value ?? "";
            }
        }
        return "";
    }

    /// <summary>Base URL of the gateway, or "" for an install that reports nowhere.</summary>
    public static string ProblemCollector => Value("ProblemCollector");

    /// <summary>Bearer token for the collector, or "" when none was stamped.</summary>
    public static string ProblemToken => Value("ProblemToken");
}
