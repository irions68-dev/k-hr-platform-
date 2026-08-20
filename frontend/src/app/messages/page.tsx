"use client";

import { useState } from "react";
import { apiPost, ApiError } from "@/lib/api";
import type { MessageDraftResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { CopyableCard } from "@/components/CopyableCard";

const SITUATION_TYPES = ["면접 확정", "계약 갱신", "출근 안내", "기타"];

function errorMessageFor(e: unknown): string {
  if (e instanceof ApiError && e.status === 429) {
    return "오늘 AI 처리 한도를 다 썼어요. 내일 다시 시도해주세요.";
  }
  return "초안 생성에 실패했어요. 다시 시도해주세요.";
}

export default function MessagesPage() {
  const [situation, setSituation] = useState("");
  const [situationType, setSituationType] = useState("");
  const [result, setResult] = useState<MessageDraftResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!situation.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await apiPost<MessageDraftResult>("/messages/draft", {
        situation,
        situation_type: situationType,
      });
      setResult(data);
    } catch (e) {
      setError(errorMessageFor(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold">클라이언트 맞춤형 멘트 메이커</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          상황을 짧게 적으면 고객사용 이메일·근로자용 안내 메시지·면접관용 요약 메모, 3가지
          초안을 한 번에 만들어드려요. 초안일 뿐이니 발송 전에 꼭 검토해서 사용하세요(자동
          발송은 하지 않아요).
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-wrap gap-2">
            {SITUATION_TYPES.map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setSituationType(situationType === t ? "" : t)}
                className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                  situationType === t
                    ? "border-primary bg-primary/10 font-medium"
                    : "border-border bg-background hover:bg-accent"
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <div className="flex flex-col gap-1">
            <Label>상황 설명</Label>
            <Textarea
              placeholder="예: SK하이닉스 프로젝트 면접 일정 안내, 대상자 3명, 날짜는 내일 오후 2시"
              value={situation}
              onChange={(e) => setSituation(e.target.value)}
              rows={3}
            />
          </div>

          <div>
            <Button onClick={handleGenerate} disabled={!situation.trim() || loading}>
              {loading ? "작성 중..." : "초안 만들기"}
            </Button>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>

      {result && (
        <>
          <CopyableCard title="고객사용 이메일" text={result.client_email} />
          <CopyableCard title="근로자용 안내 메시지" text={result.worker_message} />
          <CopyableCard title="면접관용 요약 메모" text={result.interviewer_memo} />
        </>
      )}
    </div>
  );
}
