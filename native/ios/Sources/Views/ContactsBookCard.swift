import Contacts
import SwiftUI

/// The synced address book (jim/contacts.py) — the shell's own road.
///
/// The console carries a picker-based sync where a browser offers one and
/// says honestly that most do not; a phone is where the contacts live.
/// The grant is the "contacts" source on the card above — this card asks
/// for it on the first sync so the decision is on the record before any
/// name moves. The sync REPLACES the book (the device's book is the
/// truth, not an accretion), names come back and numbers never do, and
/// withdrawing the source drops the book server-side.
struct ContactsBookCard: View {
    @EnvironmentObject var state: AppState
    @State private var book: [ApiClient.BookRow] = []
    @State private var held = 0
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        if let uid = state.uid, let token = state.token {
            VStack(alignment: .leading, spacing: 10) {
                Text(L10n.t("book.title", state.language))
                    .font(.headline).foregroundStyle(Theme.txt)
                Text(L10n.t("book.lead", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)
                Button {
                    Task { await sync(uid: uid, token: token) }
                } label: {
                    Text(busy ? "…" : L10n.t("book.sync", state.language))
                }
                .disabled(busy)
                if held > 0 {
                    Text(L10n.t("book.held", state.language)
                        .replacingOccurrences(of: "{n}", with: String(held)))
                        .font(.footnote).foregroundStyle(Theme.t2)
                    ForEach(book.prefix(30), id: \.id) { row in
                        HStack {
                            Text(row.name).font(.subheadline)
                                .foregroundStyle(Theme.txt)
                            if row.has_guardian == true {
                                Text(L10n.t("book.guardian", state.language))
                                    .font(.caption2)
                                    .foregroundStyle(Theme.brandA)
                            }
                            Spacer()
                        }
                    }
                }
                if let note {
                    Text(note).font(.footnote).foregroundStyle(Theme.t2)
                }
            }
            .task { await load(uid: uid, token: token) }
        }
    }

    private func load(uid: String, token: String) async {
        guard let got = try? await ApiClient.shared.contactsBook(
            uid: uid, token: token) else { return }
        book = got.book
        held = got.held
    }

    private func sync(uid: String, token: String) async {
        busy = true
        defer { busy = false }
        note = nil
        let store = CNContactStore()
        let allowed = (try? await store.requestAccess(for: .contacts)) ?? false
        guard allowed else {
            note = L10n.t("book.denied", state.language)
            return
        }
        var entries: [[String: String]] = []
        let keys = [CNContactGivenNameKey, CNContactFamilyNameKey,
                    CNContactPhoneNumbersKey] as [CNKeyDescriptor]
        let ask = CNContactFetchRequest(keysToFetch: keys)
        try? store.enumerateContacts(with: ask) { person, _ in
            let name = [person.givenName, person.familyName]
                .filter { !$0.isEmpty }.joined(separator: " ")
            guard let number = person.phoneNumbers.first?.value.stringValue,
                  !name.isEmpty else { return }
            entries.append(["name": name, "number": number])
        }
        do {
            // The grant first, its own door: the decision on the record
            // before any name moves.
            try await ApiClient.shared.setSource(
                uid: uid, token: token, source: "contacts", consented: true)
            _ = try await ApiClient.shared.syncContacts(
                uid: uid, entries: entries, token: token)
            await load(uid: uid, token: token)
        } catch {
            note = error.localizedDescription
        }
    }
}
