import SwiftUI

/// Connect: what feeds the Guardian — consented data sources, social-platform
/// connections, the connected-apps catalog, and the door out to QRME's
/// community — behind one tab.
struct ConnectView: View {
    enum Tab: String, CaseIterable {
        case sources, social, apps, community, me

        func label(_ lang: String) -> String {
            switch self {
            case .sources: return L10n.t("jcon.tab.sources", lang)
            case .social: return L10n.t("jcon.tab.social", lang)
            case .apps: return L10n.t("jcon.tab.apps", lang)
            case .community: return L10n.t("jcon.community", lang)
            case .me: return L10n.t("jcon.tab.me", lang)
            }
        }
    }
    @EnvironmentObject var state: AppState
    @State private var tab: Tab = .sources

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Picker("", selection: $tab) {
                    ForEach(Tab.allCases, id: \.self) {
                        Text($0.label(state.language)).tag($0)
                    }
                }.pickerStyle(.segmented)

                switch tab {
                case .sources:
                    SourcesSection()
                    // Channel 2 sits with the sources: the lent microphone
                    // is a way in for the world's sound, consented the same.
                    MicCard()
                    // The deployment's own plumbing: the voice it speaks in
                    // and the mail it sends through.
                    VoiceSettingsCard()
                    MailSettingsCard()
                case .social: SocialSection()
                case .apps: AppsSection()
                case .community: CommunitySection()
                // The synthetic self shipped as a section nothing switched to.
                // It had its strings in ten languages and a guard checking
                // they were there.
                //
                //     asked     does the screen have its wording
                //     mattered  does anything open the screen
                case .me: SelfProfileSection()
                }
            }.padding(20)
        }
    }
}

// MARK: Sources — "JIM sees what you allow"

private struct SourcesSection: View {
    @EnvironmentObject var state: AppState
    @State private var rows: [SourceRow] = []

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("jcon.sources", state.language)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("jcon.sources.sub", state.language))
                .font(.caption).foregroundStyle(Theme.t2)
            ForEach(rows, id: \.source) { row in
                Toggle(isOn: Binding(
                    get: { row.consented },
                    set: { newValue in set(row.source, newValue) })) {
                    Text(row.source.capitalized).font(.subheadline).foregroundStyle(Theme.txt)
                }.tint(Theme.green)
            }
        }.card()
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        rows = (try? await ApiClient.shared.sources(uid: uid, token: token)) ?? []
    }

    private func set(_ source: String, _ consented: Bool) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            try? await ApiClient.shared.setSource(uid: uid, token: token,
                                                  source: source, consented: consented)
            await load()
        }
    }
}

// MARK: Social — platform connections

private struct SocialSection: View {
    @EnvironmentObject var state: AppState
    @State private var platform = "instagram"
    @State private var handle = ""
    @State private var conns: [SocialConn] = []
    @State private var status: String?
    @State private var error: String?

    private let platforms = ["instagram", "x", "tiktok", "facebook", "linkedin",
                             "youtube", "whatsapp", "discord", "twitch",
                             "pinterest", "snapchat", "mastodon"]

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 10) {
                Text(L10n.t("jcon.social", state.language)).font(.headline).foregroundStyle(Theme.txt)
                Picker("", selection: $platform) {
                    ForEach(platforms, id: \.self) { Text($0.capitalized).tag($0) }
                }.pickerStyle(.menu).tint(Theme.brandA)
                TextField(L10n.t("jcon.handle", state.language), text: $handle)
                    .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 11))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                HStack(spacing: 8) {
                    smallButton(L10n.t("jcon.connect.collect", state.language)) { connect("collect") }
                    smallButton(L10n.t("jcon.connect.publish", state.language)) { connect("publish") }
                }
            }.card()

            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
            if let status { Text(status).font(.caption).foregroundStyle(Theme.green) }

            ForEach(conns, id: \.id) { c in
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        Text("\(c.platform.capitalized) · \(c.direction)")
                            .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                        Spacer()
                        if let h = c.handle { Text("@\(h)").font(.caption).foregroundStyle(Theme.t3) }
                    }
                    HStack(spacing: 8) {
                        if c.direction == "collect" {
                            smallButton(L10n.t("jcon.collect.sample", state.language)) { collect(c) }
                        } else {
                            smallButton(L10n.t("jcon.publish.update", state.language)) { publish(c) }
                        }
                    }
                }.card()
            }
        }
        .task { await load() }
    }

    private func smallButton(_ label: String, _ action: @escaping () -> Void) -> some View {
        Button(label, action: action)
            .font(.caption.bold()).foregroundStyle(.white)
            .padding(.horizontal, 12).padding(.vertical, 8)
            .background(Theme.brandA).clipShape(Capsule())
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        conns = (try? await ApiClient.shared.socialConnections(uid: uid, token: token)) ?? []
    }

    private func connect(_ direction: String) {
        guard let uid = state.uid, let token = state.token else { return }
        error = nil; status = nil
        Task {
            do {
                _ = try await ApiClient.shared.socialConnect(
                    uid: uid, token: token, platform: platform,
                    direction: direction, handle: handle)
                handle = ""
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func collect(_ c: SocialConn) {
        guard let token = state.token else { return }
        Task {
            do {
                try await ApiClient.shared.socialCollect(
                    cid: c.id, token: token, content: "sample post from \(c.platform)")
                status = L10n.t("jcon.collected.one", state.language)
                    .replacingOccurrences(of: "{platform}", with: c.platform.capitalized)
            } catch { self.error = error.localizedDescription }
        }
    }

    private func publish(_ c: SocialConn) {
        guard let token = state.token else { return }
        Task {
            do {
                try await ApiClient.shared.socialPublish(
                    cid: c.id, token: token, content: "A check-in from my Guardian.")
                status = L10n.t("jcon.published", state.language)
                    .replacingOccurrences(of: "{platform}", with: c.platform.capitalized)
            } catch { self.error = error.localizedDescription }
        }
    }
}

// MARK: Apps — the connected-apps catalog

private struct AppsSection: View {
    @EnvironmentObject var state: AppState
    @State private var flat: [(provider: String, app: String, label: String)] = []
    @State private var conns: [AppConn] = []
    @State private var status: String?
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 8) {
                Text(L10n.t("jcon.apps", state.language)).font(.headline).foregroundStyle(Theme.txt)
                Text(L10n.t("jcon.apps.sub", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
                ForEach(flat.prefix(10), id: \.app) { entry in
                    HStack {
                        Text(entry.label).font(.subheadline).foregroundStyle(Theme.txt)
                        Text(entry.provider).font(.caption).foregroundStyle(Theme.t3)
                        Spacer()
                        Button(L10n.t("jcon.connect", state.language)) { connect(entry.provider, entry.app) }
                            .font(.caption.bold()).foregroundStyle(Theme.brandA)
                    }
                }
            }.card()

            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
            if let status { Text(status).font(.caption).foregroundStyle(Theme.green) }

            ForEach(conns, id: \.id) { c in
                HStack {
                    Text("\(c.provider) · \(c.app)")
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    Spacer()
                    Button(L10n.t("jcon.collect", state.language)) { collect(c) }
                        .font(.caption.bold()).foregroundStyle(Theme.brandA)
                }.card()
            }
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        if let cat = try? await ApiClient.shared.appsCatalog() {
            flat = cat.providers.flatMap { p in
                p.apps.map { (provider: p.provider, app: $0.app, label: $0.label) }
            }
        }
        conns = (try? await ApiClient.shared.appConnections(uid: uid, token: token)) ?? []
    }

    private func connect(_ provider: String, _ app: String) {
        guard let uid = state.uid, let token = state.token else { return }
        error = nil
        Task {
            do {
                _ = try await ApiClient.shared.appConnect(
                    uid: uid, token: token, provider: provider, app: app)
                status = L10n.t("jcon.connected", state.language)
                    .replacingOccurrences(of: "{provider}", with: provider)
                    .replacingOccurrences(of: "{app}", with: app)
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func collect(_ c: AppConn) {
        guard let token = state.token else { return }
        Task {
            do {
                try await ApiClient.shared.appCollect(
                    cid: c.id, token: token, content: "sample context from \(c.app)")
                status = L10n.t("jcon.collected.from", state.language)
                    .replacingOccurrences(of: "{app}", with: c.app)
            } catch { self.error = error.localizedDescription }
        }
    }
}

// MARK: Community — the door out, and what stays behind it

/// FIG. 2 boxes 222–226: interact with others, moderated storage, community
/// interaction, local events and forums in every language.
///
/// None of that is built a second time here. It exists in QRME — with the
/// moderation, the rooms and the languages already in place — so this screen
/// is a door rather than a copy, and it says so in the same breath as it
/// opens. The posture is rendered from the server's own booleans instead of
/// being retyped as reassurance, so the screen cannot claim more than the
/// bridge actually does.
private struct CommunitySection: View {
    @EnvironmentObject var state: AppState
    @State private var view: CommunityView?
    @State private var opened: String?
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 8) {
                Text(L10n.t("jcon.community", state.language)).font(.headline).foregroundStyle(Theme.txt)
                if let v = view {
                    Text(v.note).font(.caption).foregroundStyle(Theme.t2)
                    if let lang = v.language {
                        Text(L10n.t("jcon.rooms.lang", state.language)
                            .replacingOccurrences(of: "{lang}", with: lang))
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                } else {
                    Text(L10n.t("jcon.loading", state.language)).font(.caption).foregroundStyle(Theme.t3)
                }
            }.card()

            if let v = view {
                // The posture, from the server's booleans rather than prose.
                VStack(alignment: .leading, spacing: 6) {
                    Text(L10n.t("jcon.notdo", state.language)).font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    postureRow(L10n.t("jcon.posture.mirror", state.language),
                               v.posture.mirrored_here)
                    postureRow(L10n.t("jcon.posture.post", state.language),
                               v.posture.posts_on_your_behalf)
                    postureRow(L10n.t("jcon.posture.health", state.language),
                               v.posture.health_data_shared)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("jcon.rooms", state.language)).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    if v.rooms.isEmpty {
                        Text(L10n.t("jcon.rooms.none", state.language))
                            .font(.caption).foregroundStyle(Theme.t3)
                    }
                    ForEach(v.rooms) { room in
                        HStack(alignment: .top) {
                            VStack(alignment: .leading, spacing: 2) {
                                Text(room.topic ?? room.id)
                                    .font(.subheadline).foregroundStyle(Theme.txt)
                                Text(roomDetail(room)).font(.caption2)
                                    .foregroundStyle(Theme.t3)
                            }
                            Spacer()
                            if let raw = room.url, let url = URL(string: raw) {
                                Link(L10n.t("jcon.open", state.language), destination: url)
                                    .font(.caption.bold()).foregroundStyle(Theme.brandA)
                                    .simultaneousGesture(TapGesture().onEnded {
                                        note(room.id)
                                    })
                            }
                        }
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("jcon.near", state.language)).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    if v.places.isEmpty {
                        Text(L10n.t("jcon.places.none", state.language)).font(.caption)
                            .foregroundStyle(Theme.t3)
                    }
                    ForEach(v.places) { place in
                        HStack {
                            Text(placeName(place)).font(.subheadline)
                                .foregroundStyle(Theme.txt)
                            Spacer()
                            if let n = place.listings {
                                Text("\(n)").font(.caption).monospacedDigit()
                                    .foregroundStyle(Theme.t2)
                            }
                        }
                    }
                }.card()
            }

            if let opened {
                Text(L10n.t("jcon.noted", state.language)
                        .replacingOccurrences(of: "{room}", with: opened))
                    .font(.caption).foregroundStyle(Theme.green)
            }
            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
        }
        .task { await load() }
    }

    private func postureRow(_ label: String, _ happens: Bool) -> some View {
        HStack(spacing: 8) {
            Text(happens ? "•" : "✓")
                .foregroundStyle(happens ? Theme.amber : Theme.green)
            Text(label).font(.caption).foregroundStyle(Theme.t2)
        }
    }

    private func roomDetail(_ room: CommunityRoom) -> String {
        var bits: [String] = []
        if let channel = room.channel { bits.append(channel) }
        if let heads = room.participants {
            bits.append(L10n.t("jcon.here", state.language)
                .replacingOccurrences(of: "{n}", with: "\(heads)"))
        }
        return bits.isEmpty ? room.id : bits.joined(separator: " · ")
    }

    private func placeName(_ place: CommunityPlace) -> String {
        guard let region = place.region, !region.isEmpty else { return place.locality }
        return "\(place.locality), \(region)"
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        do { view = try await ApiClient.shared.community(uid: uid, token: token) }
        catch { self.error = error.localizedDescription }
    }

    private func note(_ roomId: String) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            do {
                try await ApiClient.shared.noteCommunityVisit(
                    uid: uid, token: token, roomId: roomId)
                opened = roomId
            } catch { self.error = error.localizedDescription }
        }
    }
}
