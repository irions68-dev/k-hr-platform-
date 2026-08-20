"use client";

import { useState } from "react";
import { apiPost, ApiError } from "@/lib/api";
import type { AttritionSignalResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";

function errorMessageFor(e: unknown): string {
  if (e instanceof ApiError && e.status === 429) {
    return "오늘 AI 처리 한도를 다 썼어요. 내일 다시 시도해주세요.";
  }
  return "분석에 실패했어요. 다시 시도해주세요.";
}

export default function AttritionSignalPage() {
  const [notes, setNotes] = useState("");
  const [result, setResult] = useState<AttritionSignalResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!notes.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await apiPost<AttritionSignalResult>("/attrition-signal/analyze", {
        conversation_notes: notes,
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
        <h1 className="text-2xl font-bold">이탈 신호 노트</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          근로자와 최근 나눈 대화나 관찰한 내용을 적으면, 그 안에서 실제로 드러난
          신호만 정리해서 면담 준비를 도와드려요. 이탈 확률이나 점수는 계산하지
          않아요 — 근거 없는 숫자는 오히려 오판의 위험이 있기 때문이에요.
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-col gap-1">
            <Label>최근 대화/관찰 메모</Label>
            <Textarea
              placeholder="예: 요즘 카톡 답장이 눈에 띄게 짧아졌고, 급여 정산이 늦다고 두 번 물어봤어요"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={5}
            />
          </div>
          <div>
            <Button onClick={handleAnalyze} disabled={!notes.trim() || loading}>
              {loading ? "분석 중..." : "신호 정리하기"}
            </Button>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>

      {result && (
        <>
          <Card>
            <CardContent className="flex flex-col gap-3">
              <div>
                <p className="text-xs font-medium text-muted-foreground">관찰된 신호</p>
                {result.observed_signals.length > 0 ? (
                  <ul className="mt-1 flex flex-col gap-0.5 text-sm">
                    {result.observed_signals.map((signal) => (
                      <li key={signal}>· {signal}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-1 text-sm text-muted-foreground">
                    특별히 눈에 띄는 신호는 찾지 못했어요.
                  </p>
                )}
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">접근 제안</p>
                <p className="mt-1 whitespace-pre-wrap text-sm">
                  {result.suggested_approach}
                </p>
              </div>
              {result.talking_points.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground">
                    면담 대화 포인트
                  </p>
                  <ul className="mt-1 flex flex-col gap-0.5 text-sm">
                    {result.talking_points.map((point) => (
                      <li key={point}>· {point}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <p className="text-xs font-medium text-muted-foreground">유의사항</p>
              <p className="mt-1 whitespace-pre-wrap text-sm">{result.caution_note}</p>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
