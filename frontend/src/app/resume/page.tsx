"use client";

import { useState } from "react";
import { apiPostFile, ApiError } from "@/lib/api";
import type { ResumeExtractResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";

const MAX_FILES = 5;

function buildSummaryText(r: ResumeExtractResult, scored: boolean): string {
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

type ItemStatus = "idle" | "loading" | "done" | "error" | "skipped";

interface ResumeItem {
  id: string;
  file: File;
  status: ItemStatus;
  data?: ResumeExtractResult;
  errorMessage?: string;
  scored: boolean;
}

function errorMessageFor(e: unknown): string {
  if (e instanceof ApiError && e.status === 429) {
    return "오늘 AI 처리 한도를 다 썼어요. 내일 다시 시도해주세요.";
  }
  if (e instanceof ApiError && e.status === 415) {
    return "지원하지 않는 파일 형식이에요. 사진(JPG/PNG) 또는 PDF로 올려주세요.";
  }
  return "추출에 실패했어요.";
}

export default function ResumePage() {
  const [items, setItems] = useState<ResumeItem[]>([]);
  const [jobDescription, setJobDescription] = useState("");
  const [processing, setProcessing] = useState(false);
  const [selectWarning, setSelectWarning] = useState<string | null>(null);

  const handleSelectFiles = (fileList: FileList | null) => {
    setSelectWarning(null);
    if (!fileList || fileList.length === 0) {
      setItems([]);
      return;
    }
    const files = Array.from(fileList);
    const capped = files.slice(0, MAX_FILES);
    if (files.length > MAX_FILES) {
      setSelectWarning(
        `한 번에 최대 ${MAX_FILES}장까지만 처리할 수 있어요. 앞 ${MAX_FILES}장만 선택했어요.`
      );
    }
    setItems(
      capped.map((file, i) => ({
        id: `${file.name}-${i}-${file.size}`,
        file,
        status: "idle",
        scored: false,
      }))
    );
  };

  const handleExtract = async () => {
    if (items.length === 0) return;
    setProcessing(true);

    const trimmedJd = jobDescription.trim();
    const scored = trimmedJd.length > 0;

    let quotaExhausted = false;
    for (let i = 0; i < items.length; i++) {
      if (quotaExhausted) {
        setItems((prev) =>
          prev.map((it, idx) =>
            idx === i ? { ...it, status: "skipped", errorMessage: "한도 초과로 건너뜀" } : it
          )
        );
        continue;
      }

      setItems((prev) => prev.map((it, idx) => (idx === i ? { ...it, status: "loading" } : it)));
      try {
        const data = await apiPostFile<ResumeExtractResult>("/resume/extract", items[i].file, {
          job_description: trimmedJd,
        });
        setItems((prev) =>
          prev.map((it, idx) => (idx === i ? { ...it, status: "done", data, scored } : it))
        );
      } catch (e) {
        if (e instanceof ApiError && e.status === 429) {
          quotaExhausted = true;
        }
        setItems((prev) =>
          prev.map((it, idx) =>
            idx === i ? { ...it, status: "error", errorMessage: errorMessageFor(e) } : it
          )
        );
      }
    }

    setProcessing(false);
  };

  const displayItems = processing
    ? items
    : [...items].sort((a, b) => {
        if (!a.scored && !b.scored) return 0;
        return (b.data?.match_score ?? -1) - (a.data?.match_score ?? -1);
      });

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold">이력서 즉시 추출</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          이력서 사진이나 스캔본을 올리면 이름·연락처·경력·학력 등을 읽어서 정리해드려요.
          고객사 직무조건을 함께 입력하면 이력서마다 매칭점수를 매겨 높은 순으로 정렬해드려요.
          한 번에 최대 {MAX_FILES}장까지 올릴 수 있고, 별도로 저장하지 않으니 필요하면 결과를
          복사해서 사용하세요.
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-col gap-1">
            <Label>고객사 직무조건 (선택 — 채워두면 이력서마다 매칭점수를 매겨요)</Label>
            <Textarea
              placeholder="예: 물류센터 근무 경험 우대, 지게차운전기능사 필수, 서울/경기 근무 가능자"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={3}
            />
          </div>
          <Input
            type="file"
            multiple
            accept="image/jpeg,image/png,image/webp,application/pdf"
            onChange={(e) => handleSelectFiles(e.target.files)}
          />
          {selectWarning && <p className="text-sm text-amber-600">{selectWarning}</p>}
          <div className="flex items-center gap-3">
            <Button onClick={handleExtract} disabled={items.length === 0 || processing}>
              {processing ? "읽는 중..." : `추출하기 (${items.length}장)`}
            </Button>
            {items.length > 0 && (
              <span className="text-sm text-muted-foreground">
                {items.map((it) => it.file.name).join(", ")}
              </span>
            )}
          </div>
        </CardContent>
      </Card>

      {displayItems.map((item) => (
        <ResumeResultCard key={item.id} item={item} />
      ))}
    </div>
  );
}

function ResumeResultCard({ item }: { item: ResumeItem }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!item.data) return;
    await navigator.clipboard.writeText(buildSummaryText(item.data, item.scored));
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

function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 80
      ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
      : score >= 50
        ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
        : "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300";
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-sm font-semibold ${color}`}>
      {score}점
    </span>
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
