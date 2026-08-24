using System;
using System.Threading.Tasks;
using Windows.Media.SpeechRecognition;
using Windows.Media.SpeechSynthesis;
using Microsoft.UI.Xaml.Controls;

namespace JimGuardian;

/// <summary>
/// The conversation that keeps going while this window is not the one you
/// are looking at.
///
/// <para>
/// Windows is the odd one out of the three shells, and saying why matters
/// more than the code does. A phone suspends an app the moment it leaves the
/// screen, so Android needs a foreground service and iOS needs a background
/// audio mode — both of them permission to keep running at all. A minimised
/// desktop window is not suspended. This app is unpackaged (see
/// <c>WindowsPackageType=None</c> in the csproj), so it does not even take
/// the packaged app lifecycle: minimise it and it keeps running, exactly as
/// it did before.
/// </para>
///
/// <para>
///     asked     can the conversation survive a screen change<br/>
///     mattered  can it survive leaving the application
/// </para>
///
/// <para>
/// So there was never an operating system to satisfy here. What was missing
/// was a voice loop: this shell had none at all, and a conversation that
/// cannot hear you does not become carryable by the window staying open. That
/// is what this is.
/// </para>
///
/// <para>
/// The honesty this buys elsewhere with a notification or an orange dot is
/// bought here by Windows' own microphone indicator in the system tray, and
/// by the control that started the walk saying <em>End</em> for as long as it
/// runs. There is no supported way for a desktop app to open a microphone
/// without that tray indicator, which is the right arrangement.
/// </para>
///
/// <para>
/// <b>Written without a compiler.</b> There is no .NET SDK in the environment
/// this was written in. The guard beside it reads what can be read from the
/// source: that a loop exists, that it is scoped by turn, that quiet reopens
/// and a refusal does not, and that stopping actually disposes the recogniser
/// rather than leaving the tray indicator lit over an app that has stopped
/// listening. The loop itself has been reasoned about and not run.
/// </para>
/// </summary>
public static class Walking
{
    /// <summary>Raised whenever anything below changes, so a page can redraw
    /// without polling.</summary>
    public static event Action? Changed;

    public static bool Underway { get; private set; }
    public static string Heard { get; private set; } = "";
    public static string Said { get; private set; } = "";
    /// <summary>Why it stopped, when it stopped for a reason. Empty when
    /// somebody ended it on purpose — they know.</summary>
    public static string Trouble { get; private set; } = "";
    /// <summary>True when the last turn was answered by the offline stack
    /// rather than by a model. Not a failure — a deployment with no model key
    /// still coaches, from stored knowledge — but not the model somebody
    /// picked either.</summary>
    public static bool Offline { get; private set; }
    /// <summary>Bumped when a walk begins, so the shell can land the person on
    /// the front page. A counter rather than a flag: a second walk started
    /// from the front page must still land there.</summary>
    public static int Landings { get; private set; }

    private static SpeechRecognizer? _recogniser;
    private static SpeechSynthesizer? _speaker;
    private static MediaElement? _voice;
    private static string _uid = "", _token = "", _area = "general", _lang = "en";

    /// <summary>Every opening of the ear carries a number, and a late callback
    /// from a superseded one is ignored. The console learned this the hard
    /// way: one shared flag meant a stale error closed the ear that had just
    /// replaced it.</summary>
    private static int _turn;
    private static bool _wants;

    /// <summary>Take the conversation with you. Called from a press, never
    /// from a page loading: an ear that outlives its screen without a press is
    /// a microphone nobody asked for.</summary>
    public static async Task Start(string uid, string token, string area,
                                   string lang, MediaElement voice)
    {
        if (Underway) return;
        _uid = uid; _token = token;
        // `general` is the front door's own area, and a fallback here rather
        // than a silent replacement for one somebody picked.
        _area = string.IsNullOrWhiteSpace(area) ? "general" : area;
        _lang = lang;
        _voice = voice;
        Trouble = ""; Offline = false;

        try
        {
            _recogniser = new SpeechRecognizer();
            await _recogniser.CompileConstraintsAsync();
            _speaker = new SpeechSynthesizer();
        }
        catch (Exception)
        {
            // A refused microphone and a machine with no recogniser both land
            // here, and both get a sentence rather than silence: somebody who
            // has just pressed a button and heard nothing cannot tell the two
            // apart, and only one of them is theirs to fix.
            Trouble = L10n.T("walk.trouble.norecogniser", _lang);
            Changed?.Invoke();
            return;
        }

        _wants = true;
        Underway = true;
        Landings += 1;
        Changed?.Invoke();
        await Hear();
    }

    /// <summary>Leave: nothing in flight answers, nothing reopens, and the
    /// recogniser is disposed so the tray indicator goes out. An indicator
    /// left lit over an app that has stopped listening teaches people the
    /// indicator lies.</summary>
    public static void Stop() => Close("");

    private static async Task Hear()
    {
        if (!_wants || _recogniser is null) return;
        var mine = ++_turn;
        SpeechRecognitionResult result;
        try
        {
            result = await _recogniser.RecognizeAsync();
        }
        catch (Exception)
        {
            if (mine != _turn || !_wants) return;
            Close(L10n.T("walk.trouble.stopped", _lang));
            return;
        }
        if (mine != _turn || !_wants) return;

        // Quiet is not a failure in a standing conversation — the microphone
        // simply opens again. Everything else stops and says which failure it
        // was, because a refusal reported as quiet is a loop that reopens
        // forever with nothing to hear.
        if (result.Status != SpeechRecognitionResultStatus.Success)
        {
            if (result.Status == SpeechRecognitionResultStatus.TimeoutExceeded)
            {
                await Hear();
                return;
            }
            Close(L10n.T("walk.trouble.stopped", _lang));
            return;
        }
        var text = (result.Text ?? "").Trim();
        if (text.Length == 0) { await Hear(); return; }

        Heard = text;
        Changed?.Invoke();
        await Take(mine, text);
    }

    private static async Task Take(int mine, string message)
    {
        string reply = "";
        bool fromStore = false;
        try
        {
            var g = await ApiClient.Shared.Coach(_uid, _token, _area, message);
            reply = g.Content ?? "";
            // Who actually answered, not who was picked. That distinction is
            // the whole reason the field exists.
            fromStore = g.ProvenanceInfo?.GeneratedBy == "stub";
        }
        catch (Exception)
        {
            reply = "";
        }
        if (mine != _turn || !_wants) return;

        Offline = fromStore;
        if (reply.Length == 0)
        {
            Said = L10n.T("walk.lost", _lang);
        }
        else
        {
            Said = reply;
            Heard = "";
            try
            {
                if (_speaker is not null && _voice is not null)
                {
                    var stream = await _speaker.SynthesizeTextToStreamAsync(reply);
                    _voice.SetSource(stream, stream.ContentType);
                    _voice.Play();
                }
            }
            catch (Exception)
            {
                // A voice that will not play is not a reason to end a
                // conversation somebody is having in writing on the screen
                // behind them. The words are already in `Said`.
            }
        }
        Changed?.Invoke();
        // The next turn opens with the voice rather than after it: a person
        // may interrupt, and a conversation that cannot be interrupted is a
        // broadcast.
        await Hear();
    }

    private static void Close(string reason)
    {
        _wants = false;
        _turn += 1;
        try { _voice?.Stop(); } catch (Exception) { }
        _recogniser?.Dispose();
        _recogniser = null;
        _speaker?.Dispose();
        _speaker = null;
        Underway = false;
        Offline = false;
        Trouble = reason;
        Changed?.Invoke();
    }
}
