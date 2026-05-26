import SwiftUI

/// Pure SwiftUI animated beach backdrop.
/// - No external assets (copyright-free).
/// - Vector-based: crisp on any device.
/// - Continuously moves: sky gradient drifts, sun pulses, four wave layers flow.
/// - Respects Reduce Motion via `accessibilityReduceMotion`.
struct BeachBackground: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var animate = false

    var body: some View {
        GeometryReader { geo in
            ZStack {
                LinearGradient(
                    colors: [
                        Color(red: 1.0,  green: 0.85, blue: 0.69),
                        Color(red: 1.0,  green: 0.7,  blue: 0.54),
                        Color(red: 0.61, green: 0.85, blue: 0.82),
                        Color(red: 0.23, green: 0.56, blue: 0.64),
                        Color(red: 0.96, green: 0.85, blue: 0.69)
                    ],
                    startPoint: animate ? .top : .topLeading,
                    endPoint: animate ? .bottom : .bottomTrailing
                )
                .animation(
                    reduceMotion ? nil : .easeInOut(duration: 16).repeatForever(autoreverses: true),
                    value: animate
                )

                Circle()
                    .fill(
                        RadialGradient(
                            colors: [
                                Color(red: 1.0, green: 0.95, blue: 0.77),
                                Color(red: 1.0, green: 0.82, blue: 0.54).opacity(0)
                            ],
                            center: .center,
                            startRadius: 4,
                            endRadius: geo.size.width * 0.45
                        )
                    )
                    .frame(width: geo.size.width * 0.9, height: geo.size.width * 0.9)
                    .position(
                        x: geo.size.width * 0.7,
                        y: geo.size.height * (animate ? 0.22 : 0.28)
                    )
                    .blendMode(.screen)
                    .animation(
                        reduceMotion ? nil : .easeInOut(duration: 9).repeatForever(autoreverses: true),
                        value: animate
                    )

                WaveLayer(amplitude: 12, frequency: 1.0, phaseSpeed: 11, yOffset: 0.62,
                          color: Color(red: 0.12, green: 0.36, blue: 0.43).opacity(0.85))
                WaveLayer(amplitude: 14, frequency: 1.3, phaseSpeed: 7,  yOffset: 0.70,
                          color: Color(red: 0.23, green: 0.56, blue: 0.64))
                WaveLayer(amplitude: 18, frequency: 1.8, phaseSpeed: 5,  yOffset: 0.79,
                          color: Color(red: 0.42, green: 0.71, blue: 0.72))
                WaveLayer(amplitude: 10, frequency: 2.6, phaseSpeed: 3,  yOffset: 0.86,
                          color: Color(red: 0.75, green: 0.90, blue: 0.89))

                Rectangle()
                    .fill(
                        LinearGradient(
                            colors: [
                                Color(red: 0.96, green: 0.85, blue: 0.69),
                                Color(red: 0.91, green: 0.77, blue: 0.56)
                            ],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    .frame(height: geo.size.height * 0.16)
                    .position(x: geo.size.width / 2, y: geo.size.height - geo.size.height * 0.08)
            }
            .onAppear { if !reduceMotion { animate = true } }
        }
    }
}

private struct WaveLayer: View {
    let amplitude: CGFloat
    let frequency: CGFloat
    let phaseSpeed: Double
    let yOffset: CGFloat
    let color: Color

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        TimelineView(.animation) { context in
            let t = context.date.timeIntervalSinceReferenceDate
            let phase = reduceMotion ? 0 : t / phaseSpeed
            Wave(amplitude: amplitude, frequency: frequency, phase: phase, yOffset: yOffset)
                .fill(color)
        }
    }
}

private struct Wave: Shape {
    var amplitude: CGFloat
    var frequency: CGFloat
    var phase: Double
    var yOffset: CGFloat

    func path(in rect: CGRect) -> Path {
        var path = Path()
        let midY = rect.height * yOffset
        path.move(to: CGPoint(x: 0, y: midY))
        let step: CGFloat = 4
        var x: CGFloat = 0
        while x <= rect.width {
            let rel = x / rect.width
            let y = midY + sin((rel * .pi * 2 * frequency) + phase) * amplitude
            path.addLine(to: CGPoint(x: x, y: y))
            x += step
        }
        path.addLine(to: CGPoint(x: rect.width, y: rect.height))
        path.addLine(to: CGPoint(x: 0, y: rect.height))
        path.closeSubpath()
        return path
    }
}

struct GlassCard: View {
    var body: some View {
        RoundedRectangle(cornerRadius: 24, style: .continuous)
            .fill(.ultraThinMaterial)
            .overlay(
                RoundedRectangle(cornerRadius: 24, style: .continuous)
                    .strokeBorder(Color.white.opacity(0.5), lineWidth: 1)
            )
            .shadow(color: TR.oceanDeep.opacity(0.18), radius: 18, y: 10)
    }
}

#Preview {
    BeachBackground()
        .ignoresSafeArea()
}
