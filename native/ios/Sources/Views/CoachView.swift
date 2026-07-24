import SwiftUI

/// Life coach: pick an area, send a message -> POST /coach, show the reply.
struct CoachView: View {
    @EnvironmentObject var state: AppState
    @State private var area = "mental_health"
    @State private var message = ""
    @State private var reply: Guidance?
    @State private var busy = false
    @State private var error: String?

    private let areas = ["mental_health", "health_fitness", "career",
                         "finance", "relationships", "personal_growth"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Life Coach").font(.title2.bold()).foregroundStyle(Theme.txt)
                Text("Talk something through. Your coach knows your baseline and goals.")
                    .font(.footnote).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 12) {
                    Text("Area").font(.caption).foregroundStyle(Theme.t2)
                    Picker("", selection: $area) {
                        ForEach(areas, id: \.self) {
                            Text($0.replacingOccurrences(of: "_", with: " ").capitalized).tag($0)
                        }
                    }.pickerStyle(.menu).tint(Theme.brandA)

                    Text("Message").font(.caption).foregroundStyle(Theme.t2)
                    TextField("What's on your mind?", text: $message, axis: .vertical)
                        .lineLimit(2...5).foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                }.card()

                Button(action: send) {
                    HStack { if busy { ProgressView().tint(.white) }; Text("Ask coach").bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 13))
                }.disabled(message.isEmpty || busy)

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                if let g = reply {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Coach").font(.headline).foregroundStyle(Theme.txt)
                        Text(g.content).font(.subheadline).foregroundStyle(Theme.txt)
                        GuidanceExtras(guidance: g)
                    }.card()
                }
            }.padding(20)
        }
    }

    private func send() {
        guard let uid = state.uid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do { reply = try await ApiClient.shared.coach(uid: uid, token: token, area: area, message: message) }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
