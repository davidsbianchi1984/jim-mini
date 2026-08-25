import SwiftUI

/// The Widget Studio, in the pocket: the small programs somebody writes
/// for themselves — listed, written, run and removed from the phone the
/// way the console has done since the Studio shipped. The doorless
/// record called this the debt of a console-first feature; these are the
/// doors.
///
///     asked     can a phone reach the widgets it owns
///     mattered  a feature with no door reads as a feature that does not exist
struct StudioCard: View {
    @EnvironmentObject var state: AppState
    @State private var limits: StudioLimitsOut?
    @State private var rows: [WidgetOut] = []
    @State private var widgetId = ""
    @State private var name = ""
    @State private var source = ""
    @State private var ran: String?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("nst.title", state.language))
                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
            if let limits, !limits.available {
                // The key travels; the sentence is this table's, in the
                // reader's language — the same bargain the console makes.
                Text(L10n.t("nst.limits", state.language) + " — "
                     + (limits.unavailable_because ?? ""))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            if rows.isEmpty {
                Text(L10n.t("nst.none", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            ForEach(rows, id: \.id) { w in
                Button {
                    widgetId = w.id
                    show()
                } label: {
                    Text("\(w.name) · \(w.id)")
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
            }
            TextField(L10n.t("nst.name", state.language), text: $name)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            TextField(L10n.t("nst.source", state.language), text: $source,
                      axis: .vertical)
                .lineLimit(3...8)
                .font(.system(.caption, design: .monospaced))
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            TextField(L10n.t("nst.id", state.language), text: $widgetId)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            HStack {
                Button(L10n.t("nst.save", state.language)) { save() }
                    .font(.caption.bold()).foregroundStyle(Theme.brandA)
                    .disabled(busy || name.isEmpty || source.isEmpty)
                Button(L10n.t("nst.show", state.language)) { show() }
                    .font(.caption).foregroundStyle(Theme.t2)
                    .disabled(busy || widgetId.isEmpty)
                Button(L10n.t("nst.run", state.language)) { run() }
                    .font(.caption).foregroundStyle(Theme.t2)
                    .disabled(busy || widgetId.isEmpty)
                Button(L10n.t("nst.remove", state.language)) { remove() }
                    .font(.caption).foregroundStyle(Theme.red)
                    .disabled(busy || widgetId.isEmpty)
            }
            if let ran {
                Text(ran).font(.caption2).foregroundStyle(Theme.green)
            }
            if let error {
                Text(error).font(.caption2).foregroundStyle(Theme.red)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        limits = try? await ApiClient.shared.studioLimits()
        guard let uid = state.uid, let token = state.token else { return }
        rows = (try? await ApiClient.shared.widgets(
            uid: uid, token: token).widgets) ?? []
    }

    private func save() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                // The id field decides whether this is a new widget or a
                // new revision — the same fork the console's editor takes.
                let saved = widgetId.isEmpty
                    ? try await ApiClient.shared.writeWidget(
                        uid: uid, name: name, source: source, token: token)
                    : try await ApiClient.shared.reviseWidget(
                        uid: uid, widgetId: widgetId, name: name,
                        source: source, token: token)
                widgetId = saved.id
                await load()
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func show() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                let w = try await ApiClient.shared.widget(
                    uid: uid, widgetId: widgetId, token: token)
                name = w.name; source = w.source
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func run() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil; ran = nil
        Task {
            do {
                let out = try await ApiClient.shared.runWidget(
                    uid: uid, widgetId: widgetId, token: token)
                // A failed widget is a 200 carrying its status — shown
                // beside the editor, not thrown as an error.
                ran = out.status + (out.ms.map { " · \($0)ms" } ?? "")
                    + (out.detail.map { " · \($0)" } ?? "")
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func remove() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.removeWidget(
                    uid: uid, widgetId: widgetId, token: token)
                widgetId = ""; name = ""; source = ""
                await load()
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
