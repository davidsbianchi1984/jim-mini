import SwiftUI

/// The excursion and the window: study an unfamiliar topic without carrying
/// the person's PHI out — the row says how much was redacted and whether the
/// question left this host at all — plus the visits JIM noted when community
/// doors were opened, and QRME's public feed shown through the tandem.
/// Console doors (Reach, Feed); this is the phone's.
struct ExcursionsCard: View {
    @EnvironmentObject var state: AppState
    @Environment(\.openURL) private var openURL
    @State private var rows: [ExcursionRow] = []
    @State private var topic = ""
    @State private var question = ""
    @State private var entry: ExcursionRow?
    @State private var learned: ExcursionLearned?
    @State private var visits: [CommunityVisitRow] = []
    @State private var feed: CommunityFeedView?
    @State private var feedRefused: String?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("rch.ask", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            TextField(L10n.t("rch.ask.topic.ph", state.language),
                      text: $topic)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            TextField(L10n.t("rch.ask.q.ph", state.language),
                      text: $question)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            Button(L10n.t("rch.ask.go", state.language)) { ask() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 8)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy || topic.isEmpty || question.isEmpty)
            ForEach(rows, id: \.id) { row in
                HStack(spacing: 8) {
                    Text(row.topic)
                        .font(.caption2.bold()).foregroundStyle(Theme.txt)
                    // Redactions, colored by whether the question left this
                    // host — amber left, green stayed. `rch.ask.price` below
                    // is the sentence saying what these two mean.
                    Text(String(row.redactions))
                        .font(.caption2)
                        .foregroundStyle(row.left_host ? Theme.amber
                                                       : Theme.green)
                    Spacer()
                    Button(L10n.t("rch.ask.read", state.language)) {
                        read(row.id)
                    }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                    .disabled(busy)
                    Button(L10n.t("rch.ask.keep", state.language)) {
                        keep(row.id)
                    }
                    .font(.caption2)
                    .foregroundStyle(row.learned ? Theme.green : Theme.brandA)
                    .disabled(busy || row.learned)
                }
            }
            if let entry {
                Text(entry.findings ?? entry.brief ?? "")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            if let learned, let note = learned.note {
                Text(note).font(.caption2).foregroundStyle(Theme.green)
            }
            Text(L10n.t("rch.ask.price", state.language))
                .font(.caption2).foregroundStyle(Theme.t3)

            Divider().background(Theme.line)
            Text(L10n.t("rch.wrist.visits", state.language)
                    .replacingOccurrences(of: "{n}",
                                          with: String(visits.count)))
                .font(.caption2).foregroundStyle(Theme.t2)
            ForEach(Array(visits.prefix(5).enumerated()),
                    id: \.offset) { _, visit in
                let room = visit.room_id ?? ""
                let at = visit.at ?? ""
                Text("\(room) · \(at)")
                    .font(.caption2).foregroundStyle(Theme.t3)
            }

            Divider().background(Theme.line)
            Text(L10n.t("feed.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let feedRefused {
                Text(feedRefused).font(.caption2).foregroundStyle(Theme.t3)
            }
            if let feed {
                Text(feed.note).font(.caption2).foregroundStyle(Theme.t2)
                Text(L10n.t("feed.cannotpost", state.language))
                    .font(.caption2).foregroundStyle(Theme.t3)
                if feed.items.isEmpty {
                    Text(L10n.t("feed.empty", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }
                ForEach(Array(feed.items.prefix(6).enumerated()),
                        id: \.offset) { _, item in
                    let name = item.title ?? item.topic ?? item.id ?? ""
                    let kind = item.kind ?? ""
                    Text("\(name) · \(kind)")
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                if let raw = feed.open_in_qrme, let url = URL(string: raw) {
                    Button(L10n.t("feed.openinqrme", state.language)) {
                        openURL(url)
                    }
                    .font(.caption2).foregroundStyle(Theme.brandA)
                }
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        rows = (try? await ApiClient.shared.excursions(uid: uid,
                                                       token: token)) ?? []
        visits = (try? await ApiClient.shared.communityVisits(
            uid: uid, token: token)) ?? []
        do {
            feed = try await ApiClient.shared.communityFeed(uid: uid,
                                                            token: token)
        } catch { feedRefused = error.localizedDescription }
    }

    private func run(_ work: @escaping () async throws -> Void) {
        busy = true; error = nil
        Task {
            do { try await work() }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func ask() {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            _ = try await ApiClient.shared.startExcursion(
                uid: uid, token: token,
                topic: topic.trimmingCharacters(in: .whitespaces),
                question: question.trimmingCharacters(in: .whitespaces))
            topic = ""; question = ""
            rows = (try? await ApiClient.shared.excursions(
                uid: uid, token: token)) ?? []
        }
    }

    private func read(_ cid: String) {
        guard let token = state.token else { return }
        run {
            entry = try await ApiClient.shared.excursionEntry(cid: cid,
                                                              token: token)
        }
    }

    /// Fold the findings into guidance context — the local model uses them
    /// from then on, and the server says so in its own words.
    private func keep(_ cid: String) {
        guard let uid = state.uid, let token = state.token else { return }
        run {
            learned = try await ApiClient.shared.learnExcursion(cid: cid,
                                                                token: token)
            rows = (try? await ApiClient.shared.excursions(
                uid: uid, token: token)) ?? []
        }
    }
}
