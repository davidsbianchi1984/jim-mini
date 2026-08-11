import PhotosUI
import SwiftUI

/// Clinical captures: a photograph of the body, sealed in the vault. The
/// bytes go straight to the deployment; the phone keeps no copy and the
/// listing never carries pixels — the image is its own call, on purpose.
/// PhotosPicker runs out of process, which is why no photo-library usage
/// string appears in the plist: the app never touches the library, only
/// the one image the person hands it. Console door since task #106.
struct CapturesCard: View {
    @EnvironmentObject var state: AppState
    @State private var vocabulary: CaptureVocabularyRow?
    @State private var rows: [CaptureRecord] = []
    @State private var site = ""
    @State private var note = ""
    @State private var intimateConsent = false
    @State private var picked: PhotosPickerItem?
    @State private var openImage: CaptureImageRow?
    @State private var busy = false
    @State private var error: String?

    private var siteIsIntimate: Bool {
        vocabulary?.intimate.contains(site) ?? false
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.ch.cam", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.ch.cam.for", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)

            if let vocabulary {
                Picker(L10n.t("ns.ch.cam.site", state.language),
                       selection: $site) {
                    ForEach(vocabulary.sites.keys.sorted(), id: \.self) { key in
                        Text(vocabulary.sites[key] ?? key).tag(key)
                    }
                }.pickerStyle(.menu)
                TextField(L10n.t("ns.ch.cam.note", state.language), text: $note)
                    .padding(8).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 9))
                if siteIsIntimate {
                    // An intimate site is never swept in silently: the tick
                    // is the consent the backend demands, stated plainly.
                    Toggle(L10n.t("ns.ch.cam.consent", state.language),
                           isOn: $intimateConsent)
                        .font(.caption2).tint(Theme.brandA)
                }
                PhotosPicker(selection: $picked, matching: .images) {
                    Text(L10n.t("ns.ch.cam.attach", state.language))
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 8)
                        .background(Theme.brandA).clipShape(Capsule())
                }
                .disabled(busy || site.isEmpty
                          || (siteIsIntimate && !intimateConsent))
                .onChange(of: picked) { item in
                    guard let item else { return }
                    send(item)
                }
            }

            ForEach(rows.prefix(6)) { row in
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(vocabulary?.sites[row.site] ?? row.site)
                            .font(.caption.bold()).foregroundStyle(Theme.txt)
                        if row.intimate == true {
                            Text(L10n.t("ns.ch.cam.intimate", state.language))
                                .font(.caption2.bold())
                                .foregroundStyle(Theme.amber)
                        }
                        if let note = row.note, !note.isEmpty {
                            Text(note).font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }
                    Spacer()
                    Button(L10n.t("ns.ch.cam.where", state.language)) { show(row) }
                        .font(.caption2).foregroundStyle(Theme.brandA)
                    // A referral releases only what is chosen by name, and
                    // this button is the choosing — never done silently.
                    Button(L10n.t("ns.ch.cam.tick", state.language)) {
                        attach(row)
                    }.font(.caption2).foregroundStyle(Theme.amber)
                    Button(L10n.t("ns.ch.cam.withdraw", state.language)) {
                        withdraw(row)
                    }.font(.caption2).foregroundStyle(Theme.red)
                }
            }
            if let openImage,
               let data = Data(base64Encoded: openImage.content),
               let image = UIImage(data: data) {
                Image(uiImage: image)
                    .resizable().scaledToFit().frame(maxHeight: 180)
                    .clipShape(RoundedRectangle(cornerRadius: 11))
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task {
            vocabulary = try? await ApiClient.shared.captureVocabulary()
            if site.isEmpty, let first = vocabulary?.sites.keys.sorted().first {
                site = first
            }
            await load()
        }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        rows = (try? await ApiClient.shared.captures(uid: uid,
                                                     token: token)) ?? []
    }

    private func send(_ item: PhotosPickerItem) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            defer { busy = false; picked = nil }
            guard let data = try? await item.loadTransferable(type: Data.self)
            else { return }
            do {
                _ = try await ApiClient.shared.takeCapture(
                    uid: uid, token: token, kind: "photo", site: site,
                    contentBase64: data.base64EncodedString(),
                    note: note.trimmingCharacters(in: .whitespaces),
                    intimateConsent: intimateConsent)
                note = ""
                await load()
            } catch { self.error = error.localizedDescription }
        }
    }

    private func show(_ row: CaptureRecord) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            do { openImage = try await ApiClient.shared.captureImage(
                uid: uid, token: token, captureId: row.id) }
            catch { self.error = error.localizedDescription }
        }
    }

    private func attach(_ row: CaptureRecord) {
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            do { _ = try await ApiClient.shared.attachCaptures(
                uid: uid, token: token, captureIds: [row.id]) }
            catch { self.error = error.localizedDescription }
        }
    }

    private func withdraw(_ row: CaptureRecord) {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do { try await ApiClient.shared.withdrawCapture(
                uid: uid, token: token, captureId: row.id) }
            catch { self.error = error.localizedDescription }
            busy = false
            await load()
        }
    }
}
