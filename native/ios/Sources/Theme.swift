import SwiftUI

/// JIM-mini / Guardian dark-OLED palette, shared across every screen.
enum Theme {
    static let scrTop   = Color(hex: 0x0E1626)
    static let scrBot   = Color(hex: 0x0A0F1C)
    static let card     = Color(hex: 0x182238)
    static let line     = Color(hex: 0x26314E)
    static let txt      = Color(hex: 0xEEF1F7)
    static let t2       = Color(hex: 0x8A94AD)
    static let t3       = Color(hex: 0x626D88)
    static let brandA   = Color(hex: 0x7C5CFF)
    static let brandB   = Color(hex: 0x3AA0FF)
    static let green    = Color(hex: 0x43E08A)
    static let red      = Color(hex: 0xFF3B30)
    static let amber    = Color(hex: 0xF7B731)

    static let bg = LinearGradient(colors: [scrTop, scrBot],
                                   startPoint: .top, endPoint: .bottom)
    static let brand = LinearGradient(colors: [brandA, brandB],
                                      startPoint: .topLeading, endPoint: .bottomTrailing)
}

extension Color {
    init(hex: UInt32) {
        self.init(.sRGB,
                  red: Double((hex >> 16) & 0xFF) / 255,
                  green: Double((hex >> 8) & 0xFF) / 255,
                  blue: Double(hex & 0xFF) / 255,
                  opacity: 1)
    }
}

/// A rounded, hairline-bordered surface used for every card on every screen.
struct CardBackground: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(16)
            .background(Theme.card.opacity(0.9))
            .overlay(RoundedRectangle(cornerRadius: 16).stroke(Theme.line, lineWidth: 1))
            .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

extension View {
    func card() -> some View { modifier(CardBackground()) }
}
