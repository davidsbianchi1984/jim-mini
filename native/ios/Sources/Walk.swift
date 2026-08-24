import AVFoundation
import Foundation
import Speech
import SwiftUI

/// The conversation that keeps going when this app is not on screen.
///
/// The console's walk-along strip carries a conversation across a screen
/// change and stops dead when the browser puts the page away. That is not a
/// shortcoming of the strip — a backgrounded web page has its recogniser
/// ended for it — and the strip says so rather than pretending.
///
///     asked     can the conversation survive a screen change
///     mattered  can it survive leaving the application
///
/// On a phone the answer is yes, and iOS has a well-worn path for it: the
/// `audio` background mode, an `AVAudioSession` that stays active, and the
/// orange indicator the system puts in the status bar for as long as the
/// microphone is open. That indicator is the point rather than a side effect.
/// It is what makes this *the conversation you took with you* instead of *an
/// app recording you after you left it*, and the two are the same code with
/// different honesty. Android buys the same honesty with a notification it
/// cannot dismiss; here the system draws it, which is better, because a
/// person learns one indicator for every app rather than one per app.
///
/// ## Why the session is configured the way it is
///
/// * `.playAndRecord` — the reply plays while the microphone is open, which
///   is what lets somebody interrupt. A conversation you cannot interrupt is
///   a broadcast.
/// * `.spokenAudio` — tells the system this is speech rather than music, so
///   it is handled like a podcast or a navigation voice.
/// * `.mixWithOthers` and `.duckOthers` — somebody walking about with this
///   open may well have music on. Stopping their music dead would be this
///   app deciding it is the only thing that matters; ducking says its piece
///   and gives the room back.
/// * `.allowBluetooth` / `.allowBluetoothA2DP` — the earbud already in their
///   ear. The console asks for the connected microphone by name for the same
///   reason, after a field report had somebody pulling an earbud out to hear
///   their own guardian.
///
/// ## Written without a compiler
///
/// There is no Swift toolchain in the environment this was written in, and
/// no Android SDK either — the proxy refuses `dl.google.com` outright. So
/// the guard beside this reads the declarations rather than the behaviour:
/// the background mode, the usage strings, the session category, the turn
/// scoping, and that stopping actually deactivates the session. Those are
/// the parts whose absence is a microphone with no indicator, or an
/// indicator that never goes out. The loop has been reasoned about and not
/// run, and it wants a person with a phone before anybody calls it working.
@MainActor
final class Walking: ObservableObject {

    static let shared = Walking()

    /// Whether a walk is in progress, for the screen that offers the button.
    @Published private(set) var underway = false
    /// The last thing heard and the last thing said, so somebody coming back
    /// to the app sees where the conversation got to rather than the screen
    /// exactly as they left it.
    @Published private(set) var heard = ""
    @Published private(set) var said = ""
    /// Why it stopped, when it stopped for a reason. Empty when somebody
    /// ended it on purpose — they know.
    @Published private(set) var trouble = ""
    /// Bumped every time a walk begins, so the shell can land the person on
    /// the front page. The point of taking a conversation with you is going
    /// somewhere, and the screen you were on is the one place you have
    /// finished with — leaving somebody on the coach screen with the strip
    /// lit means the first thing they do is find their way out of it.
    ///
    ///     asked     did the conversation survive
    ///     mattered  can they now go anywhere
    ///
    /// A counter rather than a flag: a second walk started from the front
    /// page must still land there, and a boolean already true would say
    /// nothing happened.
    @Published private(set) var landings = 0

    /// True when the last turn was answered by the offline stack rather than
    /// by a model. Not a failure — a deployment with no model key still
    /// coaches, from stored knowledge — but not the model somebody picked
    /// either, and out here there is no screen to notice it on.
    @Published private(set) var offline = false

    private let engine = AVAudioEngine()
    private let speaker = AVSpeechSynthesizer()
    private var recogniser: SFSpeechRecognizer?
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?
    private var quiet: Timer?

    private var uid = ""
    private var token = ""
    private var area = "general"
    private var lang = "en"

    /// Every opening of the ear carries a number, and a late callback from a
    /// superseded one is ignored. The console learned this the hard way: one
    /// shared flag meant a stale error closed the ear that had just replaced
    /// it, and the microphone died a fifth of a second after it opened.
    private var turn = 0
    private var wants = false

    /// How long a turn waits on quiet before it is taken. The console's own
    /// number, from the same field report: five seconds was "still a long
    /// delay while waiting for a response — drop it to 2.5".
    private let quietSeconds = 2.5

    private init() {}

    // MARK: - Starting and stopping

    /// Take the conversation with you. Called from a button, never from an
    /// appear handler: an ear that outlives its screen without a press is
    /// the headless microphone every teardown in this shell exists to
    /// prevent.
    func start(uid: String, token: String, area: String, lang: String) {
        guard !underway else { return }
        self.uid = uid
        self.token = token
        // `general` is the front door's own area and a fallback here, never
        // a silent replacement for one somebody picked.
        self.area = area.isEmpty ? "general" : area
        self.lang = lang
        trouble = ""
        offline = false

        // Both permissions, and the honest sentence for each refusal. A
        // screen that reports "the microphone stopped" for a permission
        // never granted is the silence-and-deafness confusion this estate
        // keeps finding.
        SFSpeechRecognizer.requestAuthorization { [weak self] speech in
            Task { @MainActor in
                guard let self else { return }
                guard speech == .authorized else {
                    self.trouble = L10n.t("walk.trouble.speech", self.lang)
                    return
                }
                AVAudioSession.sharedInstance().requestRecordPermission { mic in
                    Task { @MainActor in
                        guard mic else {
                            self.trouble =
                                L10n.t("walk.trouble.permission", self.lang)
                            return
                        }
                        self.begin()
                    }
                }
            }
        }
    }

    /// Leave: nothing in flight answers, nothing re-opens, the session goes
    /// back to the system. Deactivating matters as much as activating did —
    /// a session left active is the orange indicator still lit over an app
    /// that has stopped listening, which teaches people the indicator lies.
    func stop() {
        close(reason: "")
    }

    private func begin() {
        guard let recognizer = SFSpeechRecognizer(
            locale: Locale(identifier: lang)) ?? SFSpeechRecognizer(),
              recognizer.isAvailable else {
            trouble = L10n.t("walk.trouble.norecogniser", lang)
            return
        }
        recogniser = recognizer
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(
                .playAndRecord, mode: .spokenAudio,
                options: [.mixWithOthers, .duckOthers,
                          .allowBluetooth, .allowBluetoothA2DP,
                          .defaultToSpeaker])
            try session.setActive(true, options: [])
        } catch {
            trouble = L10n.t("walk.trouble.session", lang)
            return
        }
        wants = true
        underway = true
        landings += 1
        hear()
    }

    // MARK: - One turn

    private func hear() {
        guard wants, let recognizer = recogniser else { return }
        turn += 1
        let mine = turn
        func live() -> Bool { mine == turn && wants }

        let req = SFSpeechAudioBufferRecognitionRequest()
        req.shouldReportPartialResults = true
        // On-device where the phone offers it. Not an optimisation: a
        // recogniser that needs Apple's servers stops working in the exact
        // place this feature is for — a person out of the app and out of
        // signal — and it also keeps the audio on the phone, which is the
        // better default for a health product whether or not anybody asked.
        if recognizer.supportsOnDeviceRecognition {
            req.requiresOnDeviceRecognition = true
        }
        request = req

        let input = engine.inputNode
        let format = input.outputFormat(forBus: 0)
        input.removeTap(onBus: 0)
        input.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
            req.append(buffer)
        }
        engine.prepare()
        do {
            try engine.start()
        } catch {
            close(reason: L10n.t("walk.trouble.session", lang))
            return
        }

        task = recognizer.recognitionTask(with: req) { [weak self] result, error in
            Task { @MainActor in
                guard let self, live() else { return }
                if let result {
                    let text = result.bestTranscription.formattedString
                    self.heard = text
                    // Quiet ends a turn, the way the console's does: the tap
                    // keeps feeding an open request otherwise, and a person
                    // who has finished a sentence is left waiting on a
                    // recogniser that does not know they stopped.
                    self.restartQuietTimer(mine: mine)
                    if result.isFinal, !text.isEmpty {
                        self.take(mine: mine, message: text)
                    }
                    return
                }
                if error != nil {
                    // Nothing heard is not a failure in a standing
                    // conversation — the microphone simply opens again.
                    // Everything else stops and says which failure it was,
                    // because a refusal reported as quiet is a loop that
                    // reopens forever with nothing to hear.
                    if self.heard.isEmpty {
                        self.hear()
                    } else {
                        self.close(
                            reason: L10n.t("walk.trouble.stopped", self.lang))
                    }
                }
            }
        }
    }

    private func restartQuietTimer(mine: Int) {
        quiet?.invalidate()
        quiet = Timer.scheduledTimer(withTimeInterval: quietSeconds,
                                     repeats: false) { [weak self] _ in
            Task { @MainActor in
                guard let self, mine == self.turn, self.wants else { return }
                // End the audio rather than the task: the recogniser then
                // delivers its final transcription, which is the turn.
                self.request?.endAudio()
            }
        }
    }

    private func take(mine: Int, message: String) {
        endListening()
        Task {
            let reply = try? await ApiClient.shared.coach(
                uid: uid, token: token, area: area, message: message)
            await MainActor.run {
                guard mine == self.turn, self.wants else { return }
                let text = reply?.content ?? ""
                // Who actually answered, not who was picked. That
                // distinction is the whole reason the field exists.
                self.offline = reply?.provenance?.generated_by == "stub"
                if text.isEmpty {
                    self.said = L10n.t("walk.lost", self.lang)
                } else {
                    self.said = text
                    let utterance = AVSpeechUtterance(string: text)
                    utterance.voice =
                        AVSpeechSynthesisVoice(language: self.lang)
                    self.speaker.speak(utterance)
                }
                self.heard = ""
                // The next turn opens with the voice rather than after it: a
                // person may interrupt, and `.playAndRecord` is what makes
                // that possible in the first place.
                self.hear()
            }
        }
    }

    // MARK: - Tearing down

    private func endListening() {
        quiet?.invalidate()
        quiet = nil
        engine.inputNode.removeTap(onBus: 0)
        if engine.isRunning { engine.stop() }
        request?.endAudio()
        request = nil
        task?.cancel()
        task = nil
    }

    private func close(reason: String) {
        wants = false
        turn += 1
        endListening()
        speaker.stopSpeaking(at: .immediate)
        // Give the session back. A session left active keeps the orange
        // indicator lit over an app that is no longer listening, and an
        // indicator that lies is worse than none.
        try? AVAudioSession.sharedInstance().setActive(
            false, options: [.notifyOthersOnDeactivation])
        underway = false
        offline = false
        trouble = reason
    }
}
