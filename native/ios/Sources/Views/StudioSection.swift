import SwiftUI

/// The Studio's reading half. A widget is written at a desk — the console
/// holds the editor — but somebody who wrote one should be able to open it,
/// run it and read the answer from the phone in their pocket. This is that
/// half, and only that half: no editor ships here, because a phone keyboard
/// is the wrong instrument for the first draft of a program.
struct StudioSection: View {
    @EnvironmentObject var state: AppState
    @State private var box: StudioLimits?
    @State private var rows: [StudioWidget] = []
    @State private var open: StudioWidget?
    @State private var given = "{}"
    @State private var answer: WidgetAnswer?
    @State private var busy = false
    @State private var error: String?

    /// Every refusal key the Studio can send back, spelled out rather than
    /// composed — a key nothing can see is a key nobody notices going
    /// missing. The console keeps the same list.
    private static let saidKeys = [
        "widgets.no_rlimits", "widgets.no_unshare", "widgets.no_node",
        "widgets.node_too_old", "widgets.no_netns", "widgets.threw",
        "widgets.timeout", "widgets.killed", "widgets.no_answer",
    ]

    private func said(_ key: String?) -> String? {
        guard let key, Self.saidKeys.contains(key) else { return nil }
        return L10n.t(key, state.language)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(L10n.t("studio.sub", state.language))
                .font(.caption).foregroundStyle(Theme.t2)

            if let b = box, !b.available {
                Text(said(b.unavailable_because)
                     ?? L10n.t("studio.nobox", state.language))
                    .font(.caption).foregroundStyle(Theme.red)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .card()
            }
            if let error {
                Text("⚠ \(error)").font(.caption).foregroundStyle(Theme.red)
            }

            VStack(alignment: .leading, spacing: 10) {
                Text(L10n.t("studio.yours", state.language))
                    .font(.headline).foregroundStyle(Theme.txt)
                if rows.isEmpty {
                    Text(L10n.t("studio.none", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                }
                ForEach(rows, id: \.id) { w in
                    Button {
                        select(w)
                    } label: {
                        HStack {
                            Text(w.name).font(.subheadline)
                                .foregroundStyle(open?.id == w.id
                                                 ? Theme.brandA : Theme.txt)
                            Spacer()
                            Text(L10n.t("studio.revision", state.language)
                                .replacingOccurrences(of: "{n}",
                                                      with: "\(w.revision)"))
                                .font(.caption).foregroundStyle(Theme.t2)
                        }
                    }
                }
            }.card()

            if let w = open {
                VStack(alignment: .leading, spacing: 10) {
                    Text(w.name).font(.headline).foregroundStyle(Theme.txt)
                    // Read-only on purpose: the reading half shows the
                    // program, the console is where it is written.
                    Text(L10n.t("studio.source", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    ScrollView(.horizontal) {
                        Text(w.source)
                            .font(.system(.caption2, design: .monospaced))
                            .foregroundStyle(Theme.txt)
                    }.frame(maxHeight: 160)
                    Text(L10n.t("studio.tryit", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    Text(L10n.t("studio.inputs", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    TextField("{}", text: $given)
                        .textFieldStyle(.roundedBorder)
                        .font(.system(.caption, design: .monospaced))
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    // No run button at all when the box cannot be built —
                    // a control that refuses on every press is a dead
                    // control, and the banner above already said why.
                    if box?.available != false {
                        Button(L10n.t("studio.run", state.language)) { run(w) }
                            .font(.subheadline.bold())
                            .foregroundStyle(Theme.brandA)
                            .disabled(busy)
                    } else {
                        Text(L10n.t("studio.cannotrun", state.language))
                            .font(.caption).foregroundStyle(Theme.t2)
                    }
                    if let a = answer {
                        Text(L10n.t("studio.took", state.language)
                            .replacingOccurrences(of: "{ms}", with: "\(a.ms)"))
                            .font(.caption2).foregroundStyle(Theme.t2)
                        if a.status == "ok" {
                            ScrollView(.horizontal) {
                                Text(a.truncated
                                     ? L10n.t("studio.toobig", state.language)
                                     : (a.valueJSON ?? ""))
                                    .font(.system(.caption2,
                                                  design: .monospaced))
                                    .foregroundStyle(Theme.txt)
                            }.frame(maxHeight: 160)
                        } else {
                            // `message` is the widget's own error, verbatim
                            // beside its output; `detail` is a refusal key
                            // for this shell's table.
                            Text(a.message ?? said(a.detail)
                                 ?? L10n.t("studio.failed", state.language))
                                .font(.caption).foregroundStyle(Theme.red)
                        }
                    }
                }.card()
            }

            if let b = box {
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("studio.limits", state.language))
                        .font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("studio.limits.why", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    ForEach(b.allowances.sorted(by: { $0.key < $1.key }),
                            id: \.key) { k, v in
                        HStack {
                            Text(L10n.t("studio.limit.\(k)", state.language))
                                .font(.caption).foregroundStyle(Theme.txt)
                            Spacer()
                            Text("\(v)").font(.caption)
                                .foregroundStyle(Theme.t2)
                        }
                    }
                }.card()
            }
        }
        .task { await load() }
    }

    private func load() async {
        box = try? await ApiClient.shared.studioLimits()
        guard let uid = state.uid, let token = state.token else { return }
        rows = (try? await ApiClient.shared.widgets(uid: uid,
                                                    token: token)) ?? []
    }

    /// Opening re-reads the row: the desk may have saved a new revision
    /// since this list loaded, and the phone should run what is stored,
    /// not what it remembers.
    private func select(_ w: StudioWidget) {
        answer = nil
        open = w
        guard let uid = state.uid, let token = state.token else { return }
        Task {
            if let fresh = try? await ApiClient.shared.readWidget(
                uid: uid, widgetId: w.id, token: token) {
                open = fresh
            }
        }
    }

    private func run(_ w: StudioWidget) {
        guard let uid = state.uid, let token = state.token else { return }
        // Their JSON, not the server's problem: say so here rather than
        // sending something the widget will be blamed for.
        let text = given.trimmingCharacters(in: .whitespacesAndNewlines)
        var inputs: [String: Any] = [:]
        if !text.isEmpty {
            guard let data = text.data(using: .utf8),
                  let parsed = try? JSONSerialization.jsonObject(with: data)
                    as? [String: Any] else {
                error = L10n.t("studio.badinputs", state.language)
                return
            }
            inputs = parsed
        }
        busy = true; error = nil; answer = nil
        Task {
            do {
                answer = try await ApiClient.shared.runWidget(
                    uid: uid, widgetId: w.id, inputs: inputs, token: token)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
