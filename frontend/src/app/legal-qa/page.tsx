"use client";

import { useState } from "react";
import { apiPost, ApiError } from "@/lib/api";
import type { LegalQaResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ChatEntry {
  question: string;
  response: LegalQaResponse;
}

export default function LegalQaPage() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<ChatEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = async () => {
    const q = question.trim();
    if (!q) return;
    setLoading(true);
    setError(null);
    try {
      const response = await apiPost<LegalQaResponse>("/legal-qa/ask", { question: q });
      setHistory((prev) => [...prev, { question: q, response }]);
      setQuestion("");
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 503
          ? "GEMINI_API_KEY가 설정되어 있지 않습니다."
          : "답변 생성에 실패했습니다. 샘플 코퍼스가 적재되어 있는지 확인하세요."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col gap-4">
      <h1 className="text-2xl font-bold">법령 Q&A</h1>
      <p className="text-sm text-muted-foreground">
        샘플 법령 코퍼스(6개 조문) 기반 답변입니다. 실사용 전 반드시 원문을 대조하세요.
      </p>

      <Card className="flex-1 overflow-y-auto">
        <CardContent>
          {history.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              예: &quot;파견 근로자를 얼마나 오래 쓸 수 있어?&quot;
            </p>
          ) : (
            <div className="flex flex-col gap-6">
              {history.map((entry, i) => (
                <div key={i} className="flex flex-col gap-2">
                  <div className="self-end rounded-lg bg-primary px-3 py-2 text-sm text-primary-foreground">
                    {entry.question}
                  </div>
                  <div className="flex flex-col gap-2 rounded-lg bg-muted px-3 py-2 text-sm">
                    <p>{entry.response.answer}</p>
                    {entry.response.legal_references.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {entry.response.legal_references.map((ref, j) => (
                          <Badge key={j} variant="secondary">
                            {ref}
                          </Badge>
                        ))}
                      </div>
                    )}
                    {entry.response.study_tag && (
                      <div className="mt-1 rounded-md border border-dashed p-2 text-xs text-muted-foreground">
                        <p className="font-semibold">📚 노무사 수험 연계 포인트</p>
                        <p>과목: {entry.response.study_tag.exam_part}</p>
                        <p>키워드: {entry.response.study_tag.core_keyword}</p>
                        <p>중요도: {entry.response.study_tag.importance}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {error && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          ask();
        }}
        className="flex gap-2"
      >
        <Input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="질문을 입력하세요"
          className="flex-1"
        />
        <Button type="submit" disabled={loading}>
          {loading ? "생성 중..." : "질문"}
        </Button>
      </form>
    </div>
  );
}
