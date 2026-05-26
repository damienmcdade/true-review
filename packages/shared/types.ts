export type CompanyHealth = {
  sentiment: number;
  layoff_risk: number;
  leadership_confidence: number;
};

export type Company = {
  id: string;
  name: string;
  slug: string;
  trust_score: number;
  review_count: number;
  health: CompanyHealth;
  ai_summary?: string;
};

export type CompanySearchResult = {
  id: string;
  name: string;
  slug: string;
  review_count: number;
};

export type VerificationTier = 'none' | 't1_email' | 't2_linkedin' | 't3_document' | 't4_payroll';

export type ModerationAction = 'removed' | 'edited' | 'warned' | 'reinstated';

export type ModerationLogEntry = {
  id: string;
  review_id?: string;
  action: ModerationAction;
  reason: string;
  moderator_handle: string;
  created_at: string;
};
