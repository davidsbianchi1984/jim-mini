import SwiftUI

/// First-run: name + birthdate + consent -> POST /enroll.
struct WelcomeView: View {
    @EnvironmentObject var state: AppState
    @State private var name = ""
    @State private var birthdate = Date(timeIntervalSince1970: 441_763_200) // 1984-01-01
    @State private var consent = false
    @State private var languages: [LanguageInfo] = []
    @State private var language = "en"
    @State private var busy = false
    @State private var error: String?

    private var iso: String {
        let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"; return f.string(from: birthdate)
    }

    var body: some View {
        ScrollView {
            VStack(spacing: 22) {
                Circle()
                    .fill(Theme.brand)
                    .frame(width: 84, height: 84)
                    .overlay(Image(systemName: "shield.lefthalf.filled").font(.system(size: 34)).foregroundStyle(.white))
                    .shadow(color: Theme.brandA.opacity(0.5), radius: 24, y: 8)
                    .padding(.top, 40)

                VStack(spacing: 6) {
                    Text("Your Guardian, always here").font(.title2.bold()).foregroundStyle(Theme.txt)
                    Text("Monitor, predict, guide, escalate — grounded in your baseline, on your device.")
                        .font(.footnote).foregroundStyle(Theme.t2)
                        .multilineTextAlignment(.center)
                }

                VStack(alignment: .leading, spacing: 14) {
                    field("Name") {
                        TextField("Your name", text: $name).textFieldStyle(.plain).foregroundStyle(Theme.txt)
                    }
                    field("Birthdate") {
                        DatePicker("", selection: $birthdate, displayedComponents: .date)
                            .labelsHidden().colorScheme(.dark)
                    }
                    field("Language") {
                        Picker("", selection: $language) {
                            Text("English").tag("en")
                            ForEach(languages.filter { $0.code != "en" }, id: \.code) { l in
                                Text(l.label).tag(l.code)
                            }
                        }.pickerStyle(.menu).tint(Theme.brandA)
                    }
                    Toggle(isOn: $consent) {
                        Text("I consent to the terms of use").font(.footnote).foregroundStyle(Theme.txt)
                    }.tint(Theme.green)
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                Button(action: enroll) {
                    HStack { if busy { ProgressView().tint(.white) }; Text("Get Started").bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 13))
                }
                .disabled(!consent || name.isEmpty || busy)
                .opacity(!consent || name.isEmpty ? 0.5 : 1)

                Text("Start the backend:  JIM_CORS_ORIGINS=* uvicorn jim.api:app")
                    .font(.system(size: 10, design: .monospaced)).foregroundStyle(Theme.t3)
            }.padding(20)
        }
        .task {
            languages = (try? await ApiClient.shared.languages())?.languages ?? []
        }
    }

    private func field<Content: View>(_ label: String, @ViewBuilder _ content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(label).font(.caption).foregroundStyle(Theme.t2)
            content()
                .padding(.horizontal, 12).padding(.vertical, 10)
                .background(Theme.scrBot).clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
        }
    }

    private func enroll() {
        busy = true; error = nil
        Task {
            do {
                let r = try await ApiClient.shared.enroll(name: name, birthdate: iso,
                                                          language: language)
                state.signIn(r)
            } catch {
                self.error = "Couldn't reach your Guardian — is the backend running? (\(error.localizedDescription))"
            }
            busy = false
        }
    }
}
