import SwiftUI

/// The guide and the help box: the Guardian showing you around, and the
/// written map of where everything lives. Console doors since 0.19.x; this
/// is the phone's. The help box calls no model and says so on its face.
struct GuideCard: View {
    @EnvironmentObject var state: AppState
    @State private var outline: TutorialOutline?
    @State private var progress: TutorialProgress?
    @State private var stepDetail: TutorialStep?
    @State private var screenNumber = ""
    @State private var question = ""
    @State private var answer: HelpAnswer?
    @State private var topics: HelpTopics?
    @State private var showTopics = false
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.gd.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let outline {
                Text(outline.guide).font(.caption2).foregroundStyle(Theme.t2)
            }
            if let progress {
                Text(L10n.t("ns.gd.progress", state.language)
                        .replacingOccurrences(of: "{d}",
                                              with: String(progress.done))
                        .replacingOccurrences(of: "{t}",
                                              with: String(progress.total))
                     + " · " + progress.note)
                    .font(.caption2).foregroundStyle(Theme.t2)
                if let step = progress.step {
                    stepView(step)
                    HStack {
                        Button(L10n.t("ns.gd.done", state.language)) {
                            mark(step.key)
                        }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 8)
                        .background(Theme.brandA).clipShape(Capsule())
                        .disabled(busy)
                        // The canonical lesson, re-read from its own route.
                        Button(L10n.t("ns.gd.step", state.language)) {
                            readStep(step.key)
                        }
                        .font(.caption2).foregroundStyle(Theme.brandA)
                        .disabled(busy)
                    }
                }
            } else {
                Button(L10n.t("ns.gd.start", state.language)) { start() }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(busy)
            }
            if let stepDetail {
                stepView(stepDetail)
            }

            // A screen can explain itself: the gallery number is enough.
            Text(L10n.t("ns.gd.screen", state.language))
                .font(.caption2.bold()).foregroundStyle(Theme.t2)
            HStack {
                TextField("61", text: $screenNumber)
                    .keyboardType(.numberPad)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                    .frame(width: 80)
                Button(L10n.t("ns.gd.screen", state.language)) { forScreen() }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy || Int(screenNumber) == nil)
            }

            TextField(L10n.t("ns.gd.ask.ph", state.language), text: $question)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
                .onSubmit { ask() }
            if let answer {
                Text(answer.answer).font(.caption2).foregroundStyle(Theme.txt)
                Text(answer.disclosure).font(.caption2)
                    .foregroundStyle(Theme.t3)
            }
            Button(L10n.t("ns.gd.topics", state.language)) {
                showTopics.toggle()
                if showTopics { loadTopics() }
            }
            .font(.caption2).foregroundStyle(Theme.brandA)
            if showTopics, let topics {
                ForEach(topics.topics.prefix(8), id: \.self) { topic in
                    Text(topic).font(.caption2).foregroundStyle(Theme.t2)
                }
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    @ViewBuilder
    private func stepView(_ step: TutorialStep) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text("\(step.chapter) · \(step.title)")
                .font(.caption.bold()).foregroundStyle(Theme.txt)
            if let what = step.what {
                Text(what).font(.caption2).foregroundStyle(Theme.t2)
            }
            Text(step.try_it).font(.caption2.italic())
                .foregroundStyle(Theme.t2)
        }
    }

    private func load() async {
        outline = try? await ApiClient.shared.tutorialOutline()
        if let uid = state.uid {
            progress = try? await ApiClient.shared.tutorialProgress(
                learnerId: uid)
        }
    }

    private func start() {
        guard let uid = state.uid else { return }
        busy = true; error = nil
        Task {
            do {
                progress = try await ApiClient.shared.startTutorial(
                    learnerId: uid)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func mark(_ key: String) {
        guard let uid = state.uid else { return }
        busy = true; error = nil
        Task {
            do {
                progress = try await ApiClient.shared.markTutorialDone(
                    learnerId: uid, lesson: key)
                stepDetail = nil
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func readStep(_ key: String) {
        busy = true; error = nil
        Task {
            do {
                stepDetail = try await ApiClient.shared.tutorialStep(key: key)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func forScreen() {
        guard let number = Int(screenNumber) else { return }
        busy = true; error = nil
        Task {
            do {
                stepDetail = try await ApiClient.shared.tutorialForScreen(
                    number: number)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func ask() {
        let q = question.trimmingCharacters(in: .whitespaces)
        guard !q.isEmpty else { return }
        busy = true; error = nil
        Task {
            do { answer = try await ApiClient.shared.askHelp(question: q) }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func loadTopics() {
        Task { topics = try? await ApiClient.shared.helpTopics() }
    }
}
