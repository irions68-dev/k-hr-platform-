"use client";

import { useState } from "react";
import { apiPostFile, ApiError } from "@/lib/api";
import type { ResumeExtractResult } from "@/lib/types";
import { MAX_RESUME_FILES, resumeErrorMessage, type ResumeItem } from "@/lib/resume";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { ResumeResultCard } from "@/components/resume/ResumeResultCard";

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
    const capped = files.slice(0, MAX_RESUME_FILES);
    if (files.length > MAX_RESUME_FILES) {
      setSelectWarning(
        `한 번에 최대 ${MAX_RESUME_FILES}장까지만 처리할 수 있어요. 앞 ${MAX_RESUME_FILES}장만 선택했어요.`
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
            idx === i ? { ...it, status: "error", errorMessage: resumeErrorMessage(e) } : it
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
          한 번에 최대 {MAX_RESUME_FILES}장까지 올릴 수 있고, 별도로 저장하지 않으니 필요하면
          결과를 복사해서 사용하세요.
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
