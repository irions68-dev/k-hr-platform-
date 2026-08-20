"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { buildResumeSummaryText, type ResumeItem } from "@/lib/resume";
import { ScoreBadge } from "@/components/resume/ScoreBadge";

export function ResumeResultCard({ item }: { item: ResumeItem }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!item.data) return;
    await navigator.clipboard.writeText(buildResumeSummaryText(item.data, item.scored));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (item.status === "idle" || item.status === "loading") {
    return (
      <Card>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {item.file.name} — {item.status === "loading" ? "읽는 중..." : "대기 중"}
          </p>
        </CardContent>
      </Card>
    );
  }

  if (item.status === "error" || item.status === "skipped") {
    return (
      <Card>
        <CardContent>
          <p className="text-sm text-destructive">
            {item.file.name} — {item.errorMessage}
          </p>
        </CardContent>
      </Card>
    );
  }

  const result = item.data;
  if (!result) return null;

  return (
    <Card>
      <CardContent className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold">{result.name || "이름 미확인"}</h2>
            {item.scored && <ScoreBadge score={result.match_score} />}
          </div>
          <Button variant="outline" size="sm" onClick={handleCopy}>
            {copied ? "복사됨!" : "전체 복사"}
          </Button>
        </div>
        <p className="-mt-2 text-xs text-muted-foreground">{item.file.name}</p>

        {item.scored && (result.match_strengths.length > 0 || result.match_concerns.length > 0) && (
          <div className="rounded-lg border border-border bg-muted/30 p-3 text-sm">
            {result.match_strengths.length > 0 && (
              <p>
                <span className="font-medium text-emerald-600 dark:text-emerald-400">강점 </span>
                {result.match_strengths.join(" / ")}
              </p>
            )}
            {result.match_concerns.length > 0 && (
              <p className="mt-1">
                <span className="font-medium text-amber-600 dark:text-amber-400">우려 </span>
                {result.match_concerns.join(" / ")}
              </p>
            )}
          </div>
        )}

        <dl className="grid grid-cols-1 gap-x-6 gap-y-1 text-sm sm:grid-cols-2">
          {result.birth_date && <Field label="생년월일" value={result.birth_date} />}
          {result.phone && <Field label="연락처" value={result.phone} />}
          {result.email && <Field label="이메일" value={result.email} />}
          {result.address && <Field label="거주지" value={result.address} />}
          <Field label="총 경력" value={`약 ${result.total_years_experience}년`} />
          {result.military_service && <Field label="병역" value={result.military_service} />}
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

        {result.notes && (
          <Section title="비고">
            <p className="text-sm">{result.notes}</p>
          </Section>
        )}
      </CardContent>
    </Card>
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
