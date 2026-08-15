import SwiftUI

/// The jim-mini OS lockup — the whole mark, as the ABRACADABRA menu button.
///
/// Three stacked parts in the proportions of the artwork: the neon wordmark,
/// the amulet triangle with ABRACADABRA descending eleven rows, and the OS
/// plate. The console draws the same lockup from the same numbers
/// (`app/src/JimMiniOS.tsx`, `assets/brand/jim-mini-os.svg`).
///
///     asked     is the mark on the button
///     mattered  is the whole mark on the button, big enough to read as itself
///
/// **Built from stack views and one `Path`, not from a canvas with text drawn
/// into it.** Text on a canvas means measuring glyphs by hand on three
/// platforms that measure them differently; `Text` in a `VStack` is the same
/// drawing with the layout engine doing the arithmetic, and it is the shape
/// this shell already knows how to render. The only hand-drawn thing here is
/// the triangle, which is three points.
///
/// Every dimension is a fraction of `size`, so the mark is one mark whether it
/// is 44pt on a tab strip or 200pt on a splash.
struct JimMiniOSMark: View {
    var size: CGFloat = 72

    /// The eleven rows of the descent: ABRACADABRA, then one letter shorter
    /// each line, down to a single A.
    private static let rows: [String] = (0..<11).map {
        String("ABRACADABRA".prefix(11 - $0))
    }

    var body: some View {
        ZStack {
            Color.black
            VStack(spacing: 0) {
                Text("jim-mini")
                    .font(.system(size: size * 0.15, weight: .medium,
                                  design: .serif))
                    .italic()
                    .foregroundStyle(Color(red: 0.91, green: 0.94, blue: 0.31))
                    // Two shadows rather than one: a neon tube is a bright
                    // core inside a wider halo, and a single blur reads as a
                    // smudge instead.
                    .shadow(color: Color(red: 0.91, green: 0.94, blue: 0.31)
                        .opacity(0.9), radius: size * 0.02)
                    .shadow(color: Color(red: 0.85, green: 0.90, blue: 0.20)
                        .opacity(0.6), radius: size * 0.06)
                    .frame(height: size * 0.22)

                triangle
                    .frame(width: size * 0.42, height: size * 0.37)

                Rectangle()
                    .fill(.white)
                    .frame(width: size * 0.82, height: size * 0.21)
                    .overlay(
                        Text("OS")
                            .font(.system(size: size * 0.17, weight: .black))
                            .foregroundStyle(.black)
                    )
                    .padding(.top, size * 0.01)
            }
            .padding(.vertical, size * 0.05)
        }
        .frame(width: size, height: size)
        .accessibilityLabel("ABRACADABRA")
    }

    private var triangle: some View {
        GeometryReader { geo in
            let w = geo.size.width, h = geo.size.height
            ZStack {
                Path { p in
                    p.move(to: CGPoint(x: 0, y: 0))
                    p.addLine(to: CGPoint(x: w, y: 0))
                    p.addLine(to: CGPoint(x: w / 2, y: h))
                    p.closeSubpath()
                }
                .fill(Color(red: 0.08, green: 0.07, blue: 0.04))
                .overlay(
                    Path { p in
                        p.move(to: CGPoint(x: 0, y: 0))
                        p.addLine(to: CGPoint(x: w, y: 0))
                        p.addLine(to: CGPoint(x: w / 2, y: h))
                        p.closeSubpath()
                    }
                    .stroke(
                        LinearGradient(
                            colors: [Color(red: 0.87, green: 0.91, blue: 0.29),
                                     Color(red: 0.95, green: 0.76, blue: 0.19),
                                     Color(red: 0.72, green: 0.53, blue: 0.12)],
                            startPoint: .topLeading, endPoint: .bottomTrailing),
                        lineWidth: max(1, w * 0.05))
                )
                // The letters stop above the apex, as they do on the amulet —
                // the bottom fifth of the triangle is empty on purpose.
                VStack(spacing: 0) {
                    ForEach(Self.rows, id: \.self) { row in
                        Text(row)
                            .font(.system(size: h * 0.075, design: .serif))
                            .foregroundStyle(Color(red: 0.96, green: 0.94,
                                                   blue: 0.86))
                            .lineLimit(1)
                            .minimumScaleFactor(0.4)
                            .frame(maxWidth: .infinity)
                    }
                }
                .padding(.horizontal, w * 0.08)
                .frame(height: h * 0.78, alignment: .top)
                .frame(maxHeight: .infinity, alignment: .top)
                .padding(.top, h * 0.04)
            }
        }
    }
}
