import SwiftUI

/// The money guardian, on the device a person actually banks from.
///
/// Every visible string here comes from the overview's own `labels` — the
/// server composes them in the reader's language, exactly as the desktop
/// Money card does — because the count of English behind this shell's tabs
/// is a ratchet and this screen must not feed it. Until the overview loads
/// there is nothing to say, so nothing is said.
///
/// The four rules ride along unchanged: the number fields go to the vault
/// or the add is refused (the refusal sentence is the server's, shown
/// verbatim); a low balance comes back as a warning with its doors; the
/// mandate is written here and revoked here, and revoking never asks about
/// a plan.
struct MoneySection: View {
    @EnvironmentObject var state: AppState
    @State private var view: MoneyOverview?
    @State private var kind = "checking"
    @State private var institution = ""
    @State private var accountNumber = ""
    @State private var routingNumber = ""
    @State private var balanceText = ""
    @State private var goalText = ""
    @State private var floorText = ""
    @State private var capText = "500"
    @State private var monthlyText = "1000"
    @State private var scope = ""
    @State private var warnings: [MoneyWarning] = []
    @State private var note: String?
    @State private var busy = false
    @State private var statementText = ""
    @State private var statements: [ApiClient.StatementRow] = []
    @State private var links: [ApiClient.BankLinkRow] = []
    @State private var linkInstitution = ""
    @State private var linkAggregator = "plaid"

    private let kinds = ["checking", "savings", "brokerage", "crypto"]
    private let aggregators = ["plaid", "tink", "truelayer", "mx"]

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let v = view {
                let L = v.labels

                VStack(alignment: .leading, spacing: 8) {
                    Text(L["title"] ?? "").font(.headline).foregroundStyle(Theme.txt)
                    Text(v.note).font(.caption).foregroundStyle(Theme.t2)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L["accounts"] ?? "").font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    ForEach(v.accounts, id: \.id) { acc in
                        HStack {
                            VStack(alignment: .leading) {
                                Text("\(acc.label ?? acc.institution) · \(acc.kind)")
                                    .font(.caption).foregroundStyle(Theme.txt)
                                let custody = (acc.credentials ?? "none")
                                    + (acc.last4.map { " ····" + $0 } ?? "")
                                Text(custody)
                                    .font(.caption2).foregroundStyle(Theme.t2)
                            }
                            Spacer()
                            if let b = acc.balance {
                                let shown = (L["balance"] ?? "") + ": " + String(format: "%.0f", b)
                                Text(shown)
                                    .font(.caption).foregroundStyle(Theme.txt)
                            }
                        }
                    }
                    Text(L["add_account"] ?? "").font(.caption.bold())
                        .foregroundStyle(Theme.t2)
                    Picker("", selection: $kind) {
                        ForEach(kinds, id: \.self) { Text($0).tag($0) }
                    }.pickerStyle(.segmented)
                    TextField(L["institution"] ?? "", text: $institution)
                        .textFieldStyle(.roundedBorder)
                    SecureField(L["account_number"] ?? "", text: $accountNumber)
                        .textFieldStyle(.roundedBorder)
                    SecureField(L["routing_number"] ?? "", text: $routingNumber)
                        .textFieldStyle(.roundedBorder)
                    Button(L["add_account"] ?? "") { add() }
                        .disabled(busy || institution.isEmpty)
                }.card()

                if let first = v.accounts.first {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(L["record_balance"] ?? "").font(.subheadline.bold())
                            .foregroundStyle(Theme.txt)
                        TextField(L["balance"] ?? "", text: $balanceText)
                            .keyboardType(.decimalPad)
                            .textFieldStyle(.roundedBorder)
                        Button(L["record_balance"] ?? "") { observe(first.id) }
                            .disabled(busy || Double(balanceText) == nil)
                        ForEach(warnings.indices, id: \.self) { ix in
                            let w = warnings[ix]
                            VStack(alignment: .leading, spacing: 4) {
                                Text(w.message).font(.caption)
                                    .foregroundStyle(Theme.txt)
                                if let doors = w.doors {
                                    Text(L["doors"] ?? "").font(.caption2.bold())
                                        .foregroundStyle(Theme.t2)
                                    if let spec = doors.specialist, let label = spec.label {
                                        Text("· \(label)").font(.caption2)
                                            .foregroundStyle(Theme.t2)
                                    }
                                    ForEach(doors.desks.indices, id: \.self) { d in
                                        let desk = doors.desks[d]
                                        let line = "· " + (desk.name ?? "") + " — "
                                            + (desk.trade ?? "") + " " + (desk.location ?? "")
                                        Text(line)
                                            .font(.caption2).foregroundStyle(Theme.t2)
                                    }
                                }
                            }
                        }
                    }.card()
                }

                // The statement is the reading: pasted here, sealed in
                // the vault, summed locally; a closing balance walks the
                // observe path.
                if let first = v.accounts.first {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(L["statements"] ?? "").font(.subheadline.bold())
                            .foregroundStyle(Theme.txt)
                        TextField(L["drop_statement"] ?? "",
                                  text: $statementText, axis: .vertical)
                            .lineLimit(2...4).textFieldStyle(.roundedBorder)
                        Button(L["drop_statement"] ?? "") { drop(first.id) }
                            .font(.caption.bold())
                            .disabled(busy || statementText.isEmpty)
                        ForEach(statements) { s in
                            let line = s.filename + " · " + String(s.line_count)
                                + " · +" + String(format: "%.2f", s.total_in)
                                + " −" + String(format: "%.2f", s.total_out)
                            Text(line).font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }.card()
                }

                // A bank link is a written consent; its status never
                // claims data that was not pulled.
                VStack(alignment: .leading, spacing: 8) {
                    Text(L["links"] ?? "").font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    TextField(L["institution"] ?? "", text: $linkInstitution)
                        .textFieldStyle(.roundedBorder)
                    Picker("", selection: $linkAggregator) {
                        ForEach(aggregators, id: \.self) { Text($0).tag($0) }
                    }.pickerStyle(.segmented)
                    Button(L["link_bank"] ?? "") { linkBank() }
                        .font(.caption.bold())
                        .disabled(busy || linkInstitution.isEmpty)
                    ForEach(links) { l in
                        HStack {
                            Text(l.institution + " · " + l.aggregator
                                 + " · " + l.status)
                                .font(.caption2).foregroundStyle(Theme.t2)
                            Spacer()
                            Button(L["sync"] ?? "") { syncBank(l.id) }
                                .font(.caption2).disabled(busy)
                            Button(L["revoke_link"] ?? "") { unlink(l.id) }
                                .font(.caption2).disabled(busy)
                        }
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L["savings_goal"] ?? "").font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    if let goal = v.savings {
                        Text(String(format: "%.0f", goal.goal))
                            .font(.caption).foregroundStyle(Theme.txt)
                    }
                    TextField(L["savings_goal"] ?? "", text: $goalText)
                        .keyboardType(.decimalPad)
                        .textFieldStyle(.roundedBorder)
                    Button(L["set_goal"] ?? "") { setGoal() }
                        .disabled(busy || Double(goalText) == nil)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L["low_floor"] ?? "").font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    TextField(L["low_floor"] ?? "", text: $floorText)
                        .keyboardType(.decimalPad)
                        .textFieldStyle(.roundedBorder)
                    Button(L["set_floor"] ?? "") { setFloor() }
                        .disabled(busy || Double(floorText) == nil)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L["mandate"] ?? "").font(.subheadline.bold())
                        .foregroundStyle(Theme.txt)
                    TextField(L["cap_per_order"] ?? "", text: $capText)
                        .keyboardType(.decimalPad).textFieldStyle(.roundedBorder)
                    TextField(L["monthly_cap"] ?? "", text: $monthlyText)
                        .keyboardType(.decimalPad).textFieldStyle(.roundedBorder)
                    TextField(L["scope"] ?? "", text: $scope)
                        .textFieldStyle(.roundedBorder)
                    HStack {
                        Button(L["mandate_save"] ?? "") { mandate(true) }
                            .disabled(busy || scope.isEmpty)
                        // Never disabled by plan, price or emptiness beyond
                        // busy-ness: taking your hands back has no gate.
                        Button(L["mandate_revoke"] ?? "") { mandate(false) }
                            .disabled(busy)
                    }
                    if !v.orders.isEmpty {
                        Text(L["orders"] ?? "").font(.caption.bold())
                            .foregroundStyle(Theme.t2)
                        ForEach(v.orders.indices, id: \.self) { ix in
                            let o = v.orders[ix]
                            let line = o.asset_class + " "
                                + String(format: "%.0f", o.amount) + " · " + o.status
                            Text(line)
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }
                }.card()
            }

            if let note {
                Text(note).font(.caption).foregroundStyle(Theme.t2)
            }
        }
        .task { await load() }
    }

    private func load() async {
        guard let uid = state.uid, let token = state.token else { return }
        view = try? await ApiClient.shared.moneyOverview(uid: uid, token: token)
        statements = (try? await ApiClient.shared.moneyStatements(
            uid: uid, token: token)) ?? []
        links = (try? await ApiClient.shared.moneyLinks(
            uid: uid, token: token)) ?? []
    }

    private func run(_ op: @escaping () async throws -> Void) {
        guard state.uid != nil, state.token != nil else { return }
        busy = true; note = nil
        Task {
            do { try await op(); await load() }
            catch { note = error.localizedDescription }
            busy = false
        }
    }

    private func add() {
        run {
            _ = try await ApiClient.shared.moneyAddAccount(
                uid: state.uid!, token: state.token!, kind: kind,
                institution: institution, label: nil,
                accountNumber: accountNumber, routingNumber: routingNumber,
                apiKey: nil)
            institution = ""; accountNumber = ""; routingNumber = ""
        }
    }

    private func observe(_ accountId: String) {
        guard let value = Double(balanceText) else { return }
        run {
            let seen = try await ApiClient.shared.moneyObserve(
                uid: state.uid!, token: state.token!,
                accountId: accountId, balance: value)
            warnings = seen.warnings
        }
    }

    private func setGoal() {
        guard let value = Double(goalText) else { return }
        run {
            _ = try await ApiClient.shared.moneySetSavings(
                uid: state.uid!, token: state.token!, goal: value)
        }
    }

    private func setFloor() {
        guard let value = Double(floorText) else { return }
        run {
            _ = try await ApiClient.shared.moneySetFloor(
                uid: state.uid!, token: state.token!, floor: value)
        }
    }

    private func drop(_ accountId: String) {
        run {
            let b64 = Data(statementText.utf8).base64EncodedString()
            _ = try await ApiClient.shared.moneyDropStatement(
                uid: state.uid!, token: state.token!, accountId: accountId,
                filename: "statement.csv", contentB64: b64)
            statementText = ""
        }
    }

    private func linkBank() {
        run {
            _ = try await ApiClient.shared.moneyLinkBank(
                uid: state.uid!, token: state.token!,
                institution: linkInstitution, aggregator: linkAggregator)
            linkInstitution = ""
        }
    }

    private func syncBank(_ linkId: String) {
        run {
            _ = try await ApiClient.shared.moneySyncBank(
                uid: state.uid!, token: state.token!, linkId: linkId)
        }
    }

    private func unlink(_ linkId: String) {
        run {
            _ = try await ApiClient.shared.moneyRevokeLink(
                uid: state.uid!, token: state.token!, linkId: linkId)
        }
    }

    private func mandate(_ enabled: Bool) {
        run {
            _ = try await ApiClient.shared.moneySetMandate(
                uid: state.uid!, token: state.token!, enabled: enabled,
                capPerOrder: Double(capText) ?? 0,
                monthlyCap: Double(monthlyText) ?? 0,
                assetClasses: ["index_funds"], scope: scope)
        }
    }
}
