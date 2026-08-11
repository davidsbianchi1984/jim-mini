import AVFoundation
import SwiftUI

/// The voice pair, spoken and heard: text goes out through `/voice/speak`
/// and comes back as audio — or, on a deployment with no speaking service,
/// the device's own voice reads it, because silence would be the wrong
/// failure. The microphone records a short clip and `/voice/transcribe`
/// hands back the words; the audio is not stored server-side. Console door
/// (the Coach's orb) since 0.6.0; this is the phone's.
struct TalkCard: View {
    @EnvironmentObject var state: AppState
    @State private var text = ""
    @State private var heard = ""
    @State private var deviceSpoke = false
    @State private var recording = false
    @State private var micRefused = false
    @State private var busy = false
    @State private var error: String?
    @State private var player: AVAudioPlayer?
    @State private var recorder: AVAudioRecorder?
    @State private var synthesizer = AVSpeechSynthesizer()

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.vs.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            TextField(L10n.t("ns.vc.say.ph", state.language), text: $text)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            HStack(spacing: 8) {
                Button(L10n.t("ns.vc.speak", state.language)) { speak() }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(busy || text.isEmpty)
                Button(L10n.t(recording ? "ns.vc.stop" : "ns.vc.talk",
                              state.language)) {
                    recording ? stopRecording() : startRecording()
                }
                .font(.caption.bold())
                .foregroundStyle(recording ? .white : Theme.brandA)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(recording ? Theme.red : Theme.scrBot)
                .clipShape(Capsule())
                .disabled(busy)
            }
            if deviceSpoke {
                Text(L10n.t("ns.vc.device", state.language))
                    .font(.caption2).foregroundStyle(Theme.amber)
            }
            if micRefused {
                Text(L10n.t("ns.vc.mic.refused", state.language))
                    .font(.caption2).foregroundStyle(Theme.amber)
            }
            if !heard.isEmpty {
                Text(heard).font(.caption2).foregroundStyle(Theme.t2)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
    }

    /// The configured voice when the deployment has one; the device's own
    /// otherwise — the same two layers, in the same order, as the console.
    private func speak() {
        busy = true; error = nil; deviceSpoke = false
        let toSay = text.trimmingCharacters(in: .whitespaces)
        Task {
            do {
                let audio = try await ApiClient.shared.speakAloud(text: toSay)
                player = try AVAudioPlayer(data: audio)
                player?.play()
            } catch {
                // 503 and everything else land here: read it with the
                // device's own voice and say which layer answered.
                synthesizer.speak(AVSpeechUtterance(string: toSay))
                deviceSpoke = true
            }
            busy = false
        }
    }

    private func startRecording() {
        error = nil; micRefused = false
        let session = AVAudioSession.sharedInstance()
        session.requestRecordPermission { granted in
            DispatchQueue.main.async {
                guard granted else { micRefused = true; return }
                do {
                    try session.setCategory(.playAndRecord,
                                            mode: .spokenAudio,
                                            options: [.defaultToSpeaker])
                    try session.setActive(true)
                    let url = FileManager.default.temporaryDirectory
                        .appendingPathComponent("speech.m4a")
                    recorder = try AVAudioRecorder(url: url, settings: [
                        AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
                        AVSampleRateKey: 16_000,
                        AVNumberOfChannelsKey: 1,
                    ])
                    recorder?.record()
                    recording = true
                } catch { self.error = error.localizedDescription }
            }
        }
    }

    private func stopRecording() {
        recorder?.stop()
        recording = false
        guard let url = recorder?.url,
              let data = try? Data(contentsOf: url) else { return }
        busy = true
        Task {
            do {
                let out = try await ApiClient.shared.transcribe(
                    audioBase64: data.base64EncodedString(),
                    filename: "speech.m4a")
                heard = out.text
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
