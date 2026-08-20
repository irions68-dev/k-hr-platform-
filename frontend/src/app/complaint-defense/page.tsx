"use client";

import { useState } from "react";
import { apiPost, ApiError } from "@/lib/api";
import type { ComplaintDefenseResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { CopyableCard } from "@/components/CopyableCard";

function errorMessageFor(e: unknown): string {
  if (e instanceof ApiError && e.status === 429) {
    return "오늘 AI 처리 한도를 다 썼어요. 내일 다시 시도해주세요.";
  }
  return "생성에 실패했어요. 다시 시도해주세요.";
}

export default function ComplaintDefensePage() {
  const [complaintText, setComplaintText] = useState("");
  const [result, setResult] = useState<ComplaintDefenseResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!complaintText.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await apiPost<ComplaintDefenseResult>("/complaint-defense/generate", {
        complaint_text: complaintText,
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
        <h1 className="text-2xl font-bold">민원 방어</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          근로자가 보낸 감정적이거나 억지스러운 카톡·문자를 그대로 붙여넣으면, 감정을
          배제한 사무적인 답변 초안과 근거 조항, 대응 시 유의사항을 만들어드려요. 실제
          법적 자문이 아니니 상황이 심각하면 노무사 확인을 꼭 거치세요.
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-col gap-1">
            <Label>근로자 민원 원문</Label>
            <Textarea
              placeholder="예: 오늘 갑자기 무단결근해놓고 왜 월차 차감하냐고 항의하는 카톡을 그대로 붙여넣으세요"
              value={complaintText}
              onChange={(e) => setComplaintText(e.target.value)}
              rows={5}
            />
          </div>
          <div>
            <Button onClick={handleGenerate} disabled={!complaintText.trim() || loading}>
              {loading ? "생성 중..." : "방어 답변 생성"}
            </Button>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>

      {result && (
        <>
          {result.defense_response && (
            <CopyableCard title="근로자에게 보낼 답변 (초안)" text={result.defense_response} />
          )}

          <Card>
            <CardContent className="flex flex-col gap-3">
              <p className="whitespace-pre-wrap text-sm">{result.legal_basis_explanation}</p>
              {result.legal_basis.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground">근거</p>
                  <ul className="mt-1 flex flex-col gap-0.5 text-sm">
                    {result.legal_basis.map((ref) => (
                      <li key={ref}>· {ref}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>

          {result.caution_note && (
            <Card>
              <CardContent>
                <p className="text-xs font-medium text-muted-foreground">
                  매니저 내부 유의사항
                </p>
                <p className="mt-1 whitespace-pre-wrap text-sm">{result.caution_note}</p>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
