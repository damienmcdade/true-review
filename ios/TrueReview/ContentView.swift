import SwiftUI

struct ContentView: View {
    @State private var query = ""

    var body: some View {
        ZStack {
            BeachBackground()
                .ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    header
                    hero
                    featuresGrid
                    Spacer(minLength: 60)
                }
                .padding(.horizontal, 20)
                .padding(.top, 24)
            }
        }
    }

    private var header: some View {
        HStack {
            HStack(spacing: 8) {
                Image(systemName: "sun.max.fill")
                    .foregroundStyle(TR.coral)
                Text("True Review")
                    .font(.system(size: 18, weight: .semibold))
            }
            Spacer()
            Text("Verify")
                .font(.system(size: 14, weight: .medium))
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(.white.opacity(0.6), in: Capsule())
        }
        .foregroundStyle(TR.ink)
    }

    private var hero: some View {
        VStack(alignment: .leading, spacing: 16) {
            Label("Workplace truth, verified", systemImage: "checkmark.shield.fill")
                .font(.system(size: 12, weight: .medium))
                .foregroundStyle(TR.oceanDeep)
                .padding(.horizontal, 10)
                .padding(.vertical, 5)
                .background(.white.opacity(0.65), in: Capsule())

            Text("The calmest place to read what work is really like.")
                .font(.system(size: 34, weight: .semibold, design: .serif))
                .foregroundStyle(TR.ink)
                .lineSpacing(2)

            Text("Verified employees. Transparent moderation. AI insights from the reviews — not the noise.")
                .font(.system(size: 15))
                .foregroundStyle(TR.ink.opacity(0.7))
                .lineSpacing(3)

            HStack(spacing: 8) {
                Image(systemName: "magnifyingglass")
                    .foregroundStyle(TR.ink.opacity(0.45))
                TextField("Search a company", text: $query)
                    .foregroundStyle(TR.ink)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(.white.opacity(0.7), in: Capsule())
        }
        .padding(20)
        .background(GlassCard())
    }

    private var featuresGrid: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            featureCard(icon: "checkmark.shield.fill", title: "Zero-knowledge verify", color: TR.verified)
            featureCard(icon: "eye.fill", title: "Public moderation", color: TR.ocean)
            featureCard(icon: "sparkles", title: "AI copilot", color: TR.coral)
            featureCard(icon: "chart.line.uptrend.xyaxis", title: "Real-time health", color: TR.ocean)
        }
    }

    private func featureCard(icon: String, title: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(systemName: icon).foregroundStyle(color)
            Text(title)
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(TR.ink)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(GlassCard())
    }
}

#Preview {
    ContentView()
}
