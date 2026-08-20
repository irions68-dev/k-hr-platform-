"use client";

import { useState } from "react";
import { apiPost, ApiError } from "@/lib/api";
import type { AssistantRouteResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { CopyableCard } from "@/components/CopyableCard";

function errorMessageFor(e: unknown): string {
  if (e instanceof ApiError && e.status === 429) {
    return "오늘 AI 처리 한도를 다 썼어요. 내일 다시 시도해주세요.";
  }
  return "처리에 실패했어요. 다시 시도해주세요.";
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

export default function AssistantPage() {
  const [text, setText] = useState("");
  const [data, setData] = useState<AssistantRouteResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleProcess = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await apiPost<AssistantRouteResult>("/assistant/route", { text });
      setData(res);
    } catch (e) {
      setError(errorMessageFor(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold">AI 어시스턴트</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          어떤 도구인지 고민하지 말고 그냥 붙여넣으세요 - 민원 텍스트, 고객사 운영
          방식 설명, 근로자와의 대화, 안내 메시지가 필요한 상황 등을 알아서 판단해서
          알맞은 도구로 처리해드려요. (고객사 메일 초안은 목적을 따로 입력해야 해서
          "고객사 메일 도우미" 페이지를 이용하세요.)
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-col gap-1">
            <Label>무엇이든 붙여넣기</Label>
            <Textarea
              placeholder="예: 근로자가 보낸 항의 카톡, 고객사 운영 방식 설명, 최근 대화 메모, 안내할 상황 등"
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={6}
            />
          </div>
          <div>
            <Button onClick={handleProcess} disabled={!text.trim() || loading}>
              {loading ? "판단 중..." : "처리하기"}
            </Button>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>

      {data && (
        <>
          <div>
            <span className="rounded-full bg-secondary px-2.5 py-0.5 text-sm font-semibold text-secondary-foreground">
              {data.category_label}(으)로 처리했어요
            </span>
          </div>

          {data.category === "complaint_defense" && (
            <>
              {data.result.defense_response && (
                <CopyableCard
                  title="근로자에게 보낼 답변 (초안)"
                  text={data.result.defense_response}
                />
              )}
              <Card>
                <CardContent className="flex flex-col gap-3">
                  <p className="whitespace-pre-wrap text-sm">
                    {data.result.legal_basis_explanation}
                  </p>
                  {data.result.legal_basis.length > 0 && (
                    <ul className="flex flex-col gap-0.5 text-sm">
                      {data.result.legal_basis.map((ref) => (
                        <li key={ref}>· {ref}</li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardContent>
                  <p className="text-xs font-medium text-muted-foreground">
                    매니저 내부 유의사항
                  </p>
                  <p className="mt-1 whitespace-pre-wrap text-sm">
                    {data.result.caution_note}
                  </p>
                </CardContent>
              </Card>
            </>
          )}

          {data.category === "compliance_check" && (
            <>
              <Card>
                <CardContent className="flex flex-col gap-3">
                  <span
                    className={`w-fit rounded-full px-2.5 py-0.5 text-sm font-semibold ${riskBadgeClass(data.result.risk_level)}`}
                  >
                    리스크: {data.result.risk_level}
                  </span>
                  <p className="whitespace-pre-wrap text-sm">{data.result.risk_summary}</p>
                  {data.result.legal_references.length > 0 && (
                    <ul className="flex flex-col gap-0.5 text-sm">
                      {data.result.legal_references.map((ref) => (
                        <li key={ref}>· {ref}</li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
              {data.result.pitch && (
                <CopyableCard title="영업 피치 (초안)" text={data.result.pitch} />
              )}
            </>
          )}

          {data.category === "attrition_signal" && (
            <>
              <Card>
                <CardContent className="flex flex-col gap-3">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">관찰된 신호</p>
                    <ul className="mt-1 flex flex-col gap-0.5 text-sm">
                      {data.result.observed_signals.map((s) => (
                        <li key={s}>· {s}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">접근 제안</p>
                    <p className="mt-1 whitespace-pre-wrap text-sm">
                      {data.result.suggested_approach}
                    </p>
                  </div>
                  {data.result.talking_points.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-muted-foreground">
                        면담 대화 포인트
                      </p>
                      <ul className="mt-1 flex flex-col gap-0.5 text-sm">
                        {data.result.talking_points.map((p) => (
                          <li key={p}>· {p}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardContent>
                  <p className="text-xs font-medium text-muted-foreground">유의사항</p>
                  <p className="mt-1 whitespace-pre-wrap text-sm">
                    {data.result.caution_note}
                  </p>
                </CardContent>
              </Card>
            </>
          )}

          {data.category === "message_draft" && (
            <>
              <CopyableCard title="고객사용 이메일" text={data.result.client_email} />
              <CopyableCard title="근로자용 안내 메시지" text={data.result.worker_message} />
              <CopyableCard title="면접관용 요약 메모" text={data.result.interviewer_memo} />
            </>
          )}
        </>
      )}
    </div>
  );
}
