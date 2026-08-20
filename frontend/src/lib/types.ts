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

export interface UnemploymentBenefitResult {
  eligible: boolean;
  reason: string;
  daily_benefit: number | null;
  scheduled_benefit_days: number | null;
  total_benefit: number | null;
  disclaimer: string | null;
}

export interface SupervisoryStatusResult {
  status: RiskStatus;
  reason: string;
  night_premium_note: string;
}

export interface DailyQuestion {
  id: string;
  subject: string;
  number: number;
  question: string;
  choices: string[];
}

export interface ExamAttemptResult {
  correct: boolean;
  answer_index: number;
  explanation: string | null;
  keywords: string[];
  next_review_date: string;
}

export interface ExamStats {
  total_questions: number;
  attempted_questions: number;
  total_attempts: number;
  total_correct: number;
  accuracy: number | null;
}

export type Mood = "great" | "good" | "okay" | "tired" | "stressed";

export interface TodayWellbeing {
  mood_today: Mood | null;
  mood_note: string;
  mood_response: string | null;
  streak_days: number;
  quote: string;
  cases_today: number;
  exam_new_today: number;
}

export interface EducationItem {
  school: string;
  major: string;
  degree: string;
  status: string;
}

export interface CareerItem {
  company: string;
  period: string;
  role: string;
}

export interface ResumeExtractResult {
  name: string;
  birth_date: string;
  phone: string;
  email: string;
  address: string;
  total_years_experience: number;
  education: EducationItem[];
  career: CareerItem[];
  certifications: string[];
  languages: string[];
  military_service: string;
  desired_position: string;
  desired_salary: string;
  desired_location: string;
  notes: string;
  match_score: number;
  match_strengths: string[];
  match_concerns: string[];
}

export interface MessageDraftResult {
  client_email: string;
  worker_message: string;
  interviewer_memo: string;
}

export interface WorkLogEntry {
  id: number;
  entry_date: string;
  note: string;
  created_at: string;
}

export interface WorkLogReportResult {
  report: string;
}

export interface WorkLogExportResult {
  text: string;
}

export interface WorkLogWeeklyReport {
  id: number;
  week_start: string;
  week_end: string;
  report_text: string;
  generated_at: string;
}

export interface ComplianceCheckResult {
  risk_level: string;
  risk_summary: string;
  legal_references: string[];
  pitch: string;
}

export interface ComplaintDefenseResult {
  defense_response: string;
  legal_basis: string[];
  legal_basis_explanation: string;
  caution_note: string;
}

export interface ClientNegotiationResult {
  approach_notes: string;
  email_draft: string;
  key_points: string[];
}

export interface AttritionSignalResult {
  observed_signals: string[];
  suggested_approach: string;
  talking_points: string[];
  caution_note: string;
}

export type AssistantRouteResult =
  | { category: "complaint_defense"; category_label: string; result: ComplaintDefenseResult }
  | { category: "compliance_check"; category_label: string; result: ComplianceCheckResult }
  | { category: "attrition_signal"; category_label: string; result: AttritionSignalResult }
  | { category: "message_draft"; category_label: string; result: MessageDraftResult };
