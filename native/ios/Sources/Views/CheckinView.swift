import SwiftUI

/// Mood & energy check-in -> POST /checkin, surfacing any Guardian guidance.
struct CheckinView: View {
    @EnvironmentObject var state: AppState
    @State private var mood = 3
    @State private var energy = 3
    @State private var note = ""
    @State private var result: CheckinResult?
    @State private var busy = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Check-in").font(.title2.bold()).foregroundStyle(Theme.txt)
                Text("A quick pulse on how you're doing.").font(.footnote).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 18) {
                    rating("Mood", value: $mood)
                    rating("Energy", value: $energy)
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Note").font(.subheadline).foregroundStyle(Theme.txt)
                        TextField("Anything on your mind?", text: $note, axis: .vertical)
                            .lineLimit(2...4).foregroundStyle(Theme.txt)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 11))
                            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    }
                }.card()

                Button(action: submit) {
                    HStack { if busy { ProgressView().tint(.white) }; Text("Log check-in").bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 13))
                }.disabled(busy)

                if let g = result?.guardian.guidance {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Guidance").font(.headline).foregroundStyle(Theme.txt)
                        Text(g.content).font(.subheadline).foregroundStyle(Theme.txt)
                    }.card()
                }
            }.padding(20)
        }
    }

    private func rating(_ label: String, value: Binding<Int>) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(label).font(.subheadline).foregroundStyle(Theme.txt)
            HStack(spacing: 8) {
                ForEach(1...5, id: \.self) { i in
                    Circle()
                        .fill(i <= value.wrappedValue ? Theme.brandA : Theme.card)
                        .overlay(Circle().stroke(Theme.line, lineWidth: 1))
                        .frame(width: 34, height: 34)
                        .overlay(Text("\(i)").font(.footnote.bold())
                            .foregroundStyle(i <= value.wrappedValue ? .white : Theme.t2))
                        .onTapGesture { value.wrappedValue = i }
                }
            }
        }
    }

    private func submit() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true
        Task {
            result = try? await ApiClient.shared.checkin(uid: uid, token: token,
                                                         mood: mood, energy: energy, note: note)
            busy = false
        }
    }
}
