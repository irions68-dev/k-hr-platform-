export type RiskStatus = "normal" | "warning" | "critical";

export interface DispatchWorkerRisk {
  id: number;
  name: string;
  position: string;
  contract_start_date: string;
  created_at: string;
  limit_date: string;
  d_day: number;
  status: RiskStatus;
}

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
  at_risk_workers: DispatchWorkerRisk[];
  due_study_items: StudyReviewItem[];
  total_workers: number;
  at_risk_count: number;
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
