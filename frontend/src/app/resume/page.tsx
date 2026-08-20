"use client";

import { useState } from "react";
import { apiPostFile, ApiError } from "@/lib/api";
import type { ResumeExtractResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";

function buildSummaryText(r: ResumeExtractResult): string {
  const lines: string[] = [];
  lines.push(`[이력서 요약] ${r.name || "이름 미확인"}`);
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

export default function ResumePage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ResumeExtractResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleExtract = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await apiPostFile<ResumeExtractResult>("/resume/extract", file);
      setResult(data);
    } catch (e) {
      if (e instanceof ApiError && e.status === 429) {
        setError("오늘 AI 처리 한도를 다 썼어요. 내일 다시 시도해주세요.");
      } else if (e instanceof ApiError && e.status === 415) {
        setError("지원하지 않는 파일 형식이에요. 사진(JPG/PNG) 또는 PDF로 올려주세요.");
      } else {
        setError("추출에 실패했어요. 다시 시도해주세요.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!result) return;
    await navigator.clipboard.writeText(buildSummaryText(result));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold">이력서 즉시 추출</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          이력서 사진이나 스캔본을 올리면 이름·연락처·경력·학력 등을 읽어서 정리해드려요.
          별도로 저장하지 않으니, 필요하면 결과를 복사해서 사용하세요.
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-3">
          <Input
            type="file"
            accept="image/jpeg,image/png,image/webp,application/pdf"
            onChange={(e) => {
              setFile(e.target.files?.[0] ?? null);
              setResult(null);
              setError(null);
            }}
          />
          <div className="flex items-center gap-3">
            <Button onClick={handleExtract} disabled={!file || loading}>
              {loading ? "읽는 중..." : "추출하기"}
            </Button>
            {file && (
              <span className="text-sm text-muted-foreground">{file.name}</span>
            )}
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardContent className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">{result.name || "이름 미확인"}</h2>
              <Button variant="outline" size="sm" onClick={handleCopy}>
                {copied ? "복사됨!" : "전체 복사"}
              </Button>
            </div>

            <dl className="grid grid-cols-1 gap-x-6 gap-y-1 text-sm sm:grid-cols-2">
              {result.birth_date && (
                <Field label="생년월일" value={result.birth_date} />
              )}
              {result.phone && <Field label="연락처" value={result.phone} />}
              {result.email && <Field label="이메일" value={result.email} />}
              {result.address && <Field label="거주지" value={result.address} />}
              <Field label="총 경력" value={`약 ${result.total_years_experience}년`} />
              {result.military_service && (
                <Field label="병역" value={result.military_service} />
              )}
            </dl>

            {result.career.length > 0 && (
              <Section title="경력">
                <ul className="flex flex-col gap-1 text-sm">
                  {result.career.map((c, i) => (
                    <li key={i}>
                      <span className="font-medium">{c.company}</span>
                      {c.period && <span className="text-muted-foreground"> ({c.period})</span>}
                      {c.role && <span> — {c.role}</span>}
                    </li>
                  ))}
                </ul>
              </Section>
            )}

            {result.education.length > 0 && (
              <Section title="학력">
                <ul className="flex flex-col gap-1 text-sm">
                  {result.education.map((e, i) => (
                    <li key={i}>
                      {e.school} {e.major} {e.degree && `(${e.degree})`} {e.status}
                    </li>
                  ))}
                </ul>
              </Section>
            )}

            {(result.certifications.length > 0 || result.languages.length > 0) && (
              <Section title="자격증 / 어학">
                <p className="text-sm">
                  {[...result.certifications, ...result.languages].join(", ") || "-"}
                </p>
              </Section>
            )}

            {(result.desired_position || result.desired_salary || result.desired_location) && (
              <Section title="희망사항">
                <p className="text-sm">
                  {[result.desired_position, result.desired_salary, result.desired_location]
                    .filter(Boolean)
                    .join(" / ")}
                </p>
              </Section>
            )}

            {result.notes && <Section title="비고"><p className="text-sm">{result.notes}</p></Section>}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-2">
      <dt className="w-16 shrink-0 text-muted-foreground">{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground">{title}</p>
      <div className="mt-1">{children}</div>
    </div>
  );
}
