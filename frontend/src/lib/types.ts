export type RiskStatus = "normal" | "warning" | "critical";

export interface StudyReviewItem {
  id: number;
  case_note_id: number | null;
  keyword: string;
  next_review_date: string;
  interval_days: number;
  ease_factor: number;
  repetitions: number;
  created_at: string;
}

export interface MorningBrief {
  brief_date: string;
  due_study_items: StudyReviewItem[];
  due_study_count: number;
}

export interface CaseNote {
  id: number;
  question: string;
  answer: string;
  legal_references: string[];
  exam_part: string;
  core_keyword: string;
  importance: string;
  created_at: string;
}

export interface LegalQaStudyTag {
  exam_part: string;
  core_keyword: string;
  importance: string;
}

export interface LegalQaResponse {
  answer: string;
  legal_references: string[];
  rejected_references: string[];
  study_tag: LegalQaStudyTag | null;
  retrieved_citations: string[];
}

export interface FourInsurancesResult {
  rate_effective_date: string;
  national_pension: { base_income: number; employee_rate: number; premium: number };
  health_insurance: {
    health_premium: number;
    long_term_care_premium: number;
    total_premium: number;
  };
  employment_insurance: { premium: number };
  industrial_accident_insurance: {
    industry: string;
    rate: number;
    premium: number;
    employer_only: boolean;
  };
  employee_total_premium: number;
}

export interface DispatchExpirationResult {
  limit_date: string;
  d_day: number;
  status: RiskStatus;
}

export interface SeverancePayResult {
  eligible: boolean;
  tenure_days: number;
  severance_pay: number;
  reason: string;
}

export interface AnnualLeaveResult {
  tenure_days: number;
  years_of_service: number | null;
  granted_days: number;
  basis: string;
}

export interface OvertimePremiumResult {
  overtime_pay: number;
  night_pay: number;
  holiday_pay: number;
  total_premium_pay: number;
}

export interface ProratedInsuranceResult {
  days_worked: number;
  days_in_month: number;
  proration_ratio: number;
  national_pension_premium: number;
  health_insurance_premium: number;
  employment_insurance_premium: number;
  employee_total_premium: number;
  disclaimer: string;
}

export interface RiskScoreResult {
  score: number;
  max_score: number;
  status: RiskStatus;
  disclaimer: string;
}

export interface MonthlyHourExemptionResult {
  monthly_hours: number;
  threshold_hours: number;
  exempt_from_pension_and_health_insurance: boolean;
  reason: string;
}

export interface WeeklyHolidayPayResult {
  eligible: boolean;
  pay: number;
  reason: string;
}

export interface ComprehensiveWageAdequacyResult {
  required_overtime_pay: number;
  included_overtime_pay: number;
  shortfall: number;
  adequate: boolean;
  status: RiskStatus;
  disclaimer: string;
}

export interface SupervisoryStatusResult {
  status: RiskStatus;
  reason: string;
  night_premium_note: string;
}
