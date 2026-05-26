import Foundation

public struct CompanyHealth: Codable, Hashable {
    public let sentiment: Double
    public let layoffRisk: Double
    public let leadershipConfidence: Double

    enum CodingKeys: String, CodingKey {
        case sentiment
        case layoffRisk = "layoff_risk"
        case leadershipConfidence = "leadership_confidence"
    }
}

public struct Company: Codable, Hashable, Identifiable {
    public let id: String
    public let name: String
    public let slug: String
    public let trustScore: Double
    public let reviewCount: Int
    public let health: CompanyHealth
    public let aiSummary: String?

    enum CodingKeys: String, CodingKey {
        case id, name, slug, health
        case trustScore = "trust_score"
        case reviewCount = "review_count"
        case aiSummary = "ai_summary"
    }
}

public enum VerificationTier: String, Codable {
    case none, t1Email = "t1_email", t2LinkedIn = "t2_linkedin",
         t3Document = "t3_document", t4Payroll = "t4_payroll"
}
