import { ApiError } from "@/lib/api";
import type { ResumeExtractResult } from "@/lib/types";

export const MAX_RESUME_FILES = 5;

export type ResumeItemStatus = "idle" | "loading" | "done" | "error" | "skipped";

export interface ResumeItem {
  id: string;
  file: File;
  status: ResumeItemStatus;
  data?: ResumeExtractResult;
  errorMessage?: string;
  scored: boolean;
}

export function resumeErrorMessage(e: unknown): string {
  if (e instanceof ApiError && e.status === 429) {
    return "오늘 AI 처리 한도를 다 썼어요. 내일 다시 시도해주세요.";
  }
  if (e instanceof ApiError && e.status === 415) {
    return "지원하지 않는 파일 형식이에요. 사진(JPG/PNG) 또는 PDF로 올려주세요.";
  }
  return "추출에 실패했어요.";
}

export function buildResumeSummaryText(r: ResumeExtractResult, scored: boolean): string {
  const lines: string[] = [];
  lines.push(`[이력서 요약] ${r.name || "이름 미확인"}`);
  if (scored) {
    lines.push(`매칭점수: ${r.match_score}점`);
    if (r.match_strengths.length > 0) lines.push(`강점: ${r.match_strengths.join(" / ")}`);
    if (r.match_concerns.length > 0) lines.push(`우려사항: ${r.match_concerns.join(" / ")}`);
  }
  if (r.birth_date) lines.push(`생년월일: ${r.birth_date}`);
  if (r.phone) lines.push(`연락처: ${r.phone}`);
  if (r.email) lines.push(`이메일: ${r.email}`);
  if (r.address) lines.push(`거주지: ${r.address}`);
  lines.push(`총 경력: 약 ${r.total_years_experience}년`);

  if (r.career.length > 0) {
    lines.push("", "[경력]");
    for (const c of r.career) {
      lines.push(`- ${c.company}${c.period ? ` (${c.period})` : ""}${c.role ? ` / ${c.role}` : ""}`);
    }
  }

  if (r.education.length > 0) {
    lines.push("", "[학력]");
    for (const e of r.education) {
      lines.push(
        `- ${e.school}${e.major ? ` ${e.major}` : ""}${e.degree ? ` (${e.degree})` : ""}${e.status ? ` ${e.status}` : ""}`
      );
    }
  }

  if (r.certifications.length > 0) {
    lines.push("", `자격증: ${r.certifications.join(", ")}`);
  }
  if (r.languages.length > 0) {
    lines.push(`어학: ${r.languages.join(", ")}`);
  }
  if (r.military_service) lines.push(`병역: ${r.military_service}`);

  if (r.desired_position || r.desired_salary || r.desired_location) {
    lines.push(
      "",
      `희망사항: ${[r.desired_position, r.desired_salary, r.desired_location]
        .filter(Boolean)
        .join(" / ")}`
    );
  }
  if (r.notes) lines.push("", `비고: ${r.notes}`);

  return lines.join("\n");
}
