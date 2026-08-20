"use client";

import { useState } from "react";
import { apiPost, ApiError } from "@/lib/api";
import type { ClientNegotiationResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { CopyableCard } from "@/components/CopyableCard";

function errorMessageFor(e: unknown): string {
  if (e instanceof ApiError && e.status === 429) {
    return "오늘 AI 처리 한도를 다 썼어요. 내일 다시 시도해주세요.";
  }
  return "생성에 실패했어요. 다시 시도해주세요.";
}

export default function ClientNegotiationPage() {
  const [contextNotes, setContextNotes] = useState("");
  const [purpose, setPurpose] = useState("");
  const [result, setResult] = useState<ClientNegotiationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = contextNotes.trim() && purpose.trim();

  const handleGenerate = async () => {
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await apiPost<ClientNegotiationResult>("/client-negotiation/draft", {
        context_notes: contextNotes,
        purpose,
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
        <h1 className="text-2xl font-bold">고객사 메일 도우미</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          고객사 담당자와 나눴던 대화나 메모해 둔 특징(선호하는 소통 방식, 과거 이슈 등)을
          적으면, 그 메모에 근거해서만 접근 방식을 제안하고 메일 초안을 만들어드려요.
          메모에 없는 성향은 함부로 단정하지 않아요.
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-col gap-1">
            <Label>고객사 담당자 관련 메모</Label>
            <Textarea
              placeholder="예: 숫자와 데이터 중심으로 판단하는 편, 과거 지연 이슈로 예민함, 말투가 짧고 직관적인 것을 선호"
              value={contextNotes}
              onChange={(e) => setContextNotes(e.target.value)}
              rows={4}
            />
          </div>
          <div className="flex flex-col gap-1">
            <Label>이번 메일의 목적</Label>
            <Input
              placeholder="예: 계약 연장 제안, 단가 조율, 지연 이슈 해명"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
            />
          </div>
          <div>
            <Button onClick={handleGenerate} disabled={!canSubmit || loading}>
              {loading ? "생성 중..." : "메일 초안 생성"}
            </Button>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>

      {result && (
        <>
          <Card>
            <CardContent>
              <p className="text-xs font-medium text-muted-foreground">접근 방식 제안</p>
              <p className="mt-1 whitespace-pre-wrap text-sm">{result.approach_notes}</p>
            </CardContent>
          </Card>

          {result.email_draft && (
            <CopyableCard title="메일 초안" text={result.email_draft} />
          )}

          {result.key_points.length > 0 && (
            <Card>
              <CardContent>
                <p className="text-xs font-medium text-muted-foreground">핵심 포인트</p>
                <ul className="mt-1 flex flex-col gap-0.5 text-sm">
                  {result.key_points.map((point) => (
                    <li key={point}>· {point}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
