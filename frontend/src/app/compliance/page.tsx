"use client";

import { useState } from "react";
import { apiPost, ApiError } from "@/lib/api";
import type { ComplianceCheckResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { CopyableCard } from "@/components/CopyableCard";

function errorMessageFor(e: unknown): string {
  if (e instanceof ApiError && e.status === 429) {
    return "오늘 AI 처리 한도를 다 썼어요. 내일 다시 시도해주세요.";
  }
  return "진단에 실패했어요. 다시 시도해주세요.";
}

function riskBadgeClass(level: string): string {
  if (level === "높음") {
    return "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300";
  }
  if (level === "주의") {
    return "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300";
  }
  if (level === "낮음") {
    return "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300";
  }
  return "bg-muted text-muted-foreground";
}

export default function CompliancePage() {
  const [situation, setSituation] = useState("");
  const [result, setResult] = useState<ComplianceCheckResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCheck = async () => {
    if (!situation.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await apiPost<ComplianceCheckResult>("/compliance/check", { situation });
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
        <h1 className="text-2xl font-bold">컴플라이언스 진단</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          (잠재)고객사가 현재 인력을 운영하는 방식을 적으면, 위장도급·불법파견 리스크를
          법조문·판례에 비추어 진단하고 우리 회사로 전환 시 이점을 정리한 영업용 리포트를
          만들어드려요. 실제 법적 자문이 아니니 최종 판단은 노무사·변호사 확인을 꼭
          거치세요.
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-col gap-1">
            <Label>고객사 운영 방식 설명</Label>
            <Textarea
              placeholder="예: 3년째 같은 인력을 파견 형태로 계속 사용 중, 업무지시도 저희 회사가 직접 함"
              value={situation}
              onChange={(e) => setSituation(e.target.value)}
              rows={3}
            />
          </div>
          <div>
            <Button onClick={handleCheck} disabled={!situation.trim() || loading}>
              {loading ? "진단 중..." : "진단하기"}
            </Button>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>

      {result && (
        <>
          <Card>
            <CardContent className="flex flex-col gap-3">
              <div className="flex items-center gap-2">
                <span
                  className={`rounded-full px-2.5 py-0.5 text-sm font-semibold ${riskBadgeClass(result.risk_level)}`}
                >
                  리스크: {result.risk_level}
                </span>
              </div>
              <p className="whitespace-pre-wrap text-sm">{result.risk_summary}</p>
              {result.legal_references.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground">근거</p>
                  <ul className="mt-1 flex flex-col gap-0.5 text-sm">
                    {result.legal_references.map((ref) => (
                      <li key={ref}>· {ref}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>

          {result.pitch && <CopyableCard title="영업 피치 (초안)" text={result.pitch} />}
        </>
      )}
    </div>
  );
}
