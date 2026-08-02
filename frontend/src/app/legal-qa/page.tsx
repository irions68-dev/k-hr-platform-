"use client";

import { useEffect, useState } from "react";
import { apiPost, ApiError } from "@/lib/api";
import type { LegalQaResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ChatEntry {
  id: string;
  question: string;
  response: LegalQaResponse;
  savedToCases: boolean;
}

const FAQ_QUESTIONS = [
  "퇴직금은 얼마나 받나요?",
  "연차는 며칠 생기나요?",
  "야근수당은 어떻게 계산하나요?",
  "파견 기간은 최대 몇 년인가요?",
  "해고 통보는 며칠 전에 해야 하나요?",
  "퇴직금 중간정산이 가능한가요?",
  "휴일에 일하면 수당이 얼마나 붙나요?",
  "4대보험은 왜 이렇게 떼나요?",
  "주휴수당은 언제 받을 수 있나요?",
  "감시단속적 근로자도 야간수당 받나요?",
  "고객이 폭언하면 어떻게 보호받나요?",
  "계약만료로 그만두면 실업급여 받을 수 있나요?",
  "실업급여는 언제까지 신청해야 하나요?",
];

const HISTORY_STORAGE_KEY = "khr-legal-qa-history";
const MAX_HISTORY_ENTRIES = 50;

function loadHistory(): ChatEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(HISTORY_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as ChatEntry[]) : [];
  } catch {
    return [];
  }
}

export default function LegalQaPage() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<ChatEntry[]>([]);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 새로고침·페이지 이동 후에도 대화가 남아있도록 이 브라우저에 저장해둔 걸 불러온다
  useEffect(() => {
    setHistory(loadHistory());
    setHistoryLoaded(true);
  }, []);

  useEffect(() => {
    if (!historyLoaded) return;
    window.localStorage.setItem(
      HISTORY_STORAGE_KEY,
      JSON.stringify(history.slice(-MAX_HISTORY_ENTRIES))
    );
  }, [history, historyLoaded]);

  const ask = async (overrideQuestion?: string) => {
    const q = (overrideQuestion ?? question).trim();
    if (!q) return;
    setLoading(true);
    setError(null);
    try {
      const response = await apiPost<LegalQaResponse>("/legal-qa/ask", { question: q });
      const entry: ChatEntry = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        question: q,
        response,
        savedToCases: false,
      };
      setHistory((prev) => [...prev, entry]);
      setQuestion("");
    } catch (err) {
      if (err instanceof ApiError && err.status === 503) {
        setError("GEMINI_API_KEY가 설정되어 있지 않습니다.");
      } else if (err instanceof ApiError && err.status === 429) {
        setError(
          "Gemini API 사용 한도를 초과했습니다(무료 티어는 하루 요청 수가 제한되어 있습니다). 잠시 후 다시 시도하거나 내일 다시 시도하세요."
        );
      } else {
        setError("답변 생성에 실패했습니다. 샘플 코퍼스가 적재되어 있는지 확인하세요.");
      }
    } finally {
      setLoading(false);
    }
  };

  const saveToCases = async (entry: ChatEntry) => {
    await apiPost("/cases", {
      question: entry.question,
      answer: entry.response.answer,
      legal_references: entry.response.legal_references,
      exam_part: entry.response.study_tag?.exam_part ?? "",
      core_keyword: entry.response.study_tag?.core_keyword ?? "",
      importance: entry.response.study_tag?.importance ?? "Medium",
    });
    setHistory((prev) =>
      prev.map((h) => (h.id === entry.id ? { ...h, savedToCases: true } : h))
    );
  };

  const clearHistory = () => {
    if (!window.confirm("대화 기록을 전부 지울까요?")) return;
    setHistory([]);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">법령 Q&A · 전화응대 헬프데스크</h1>
        {history.length > 0 && (
          <Button variant="outline" size="sm" onClick={clearHistory}>
            대화 지우기
          </Button>
        )}
      </div>
      <p className="text-sm text-muted-foreground">
        샘플 법령·판례 코퍼스(법조문 16개 + 대법원/고등법원 판례 6개 + 세법 1개) 기반
        답변입니다. 실사용 전 반드시 원문을 대조하세요. 대화는 이 브라우저에 자동
        저장되어 새로고침해도 남아있습니다.
      </p>

      {history.length === 0 && (
        <div className="flex flex-wrap gap-2">
          {FAQ_QUESTIONS.map((q) => (
            <button
              key={q}
              type="button"
              disabled={loading}
              onClick={() => ask(q)}
              className="rounded-full border border-border bg-muted px-3 py-1.5 text-xs font-medium hover:bg-accent disabled:opacity-50"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      <Card className="flex-1 overflow-y-auto">
        <CardContent>
          {history.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              위 자주 묻는 질문을 클릭하거나 직접 질문을 입력하세요.
            </p>
          ) : (
            <div className="flex flex-col gap-6">
              {history.map((entry) => (
                <div key={entry.id} className="flex flex-col gap-2">
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
                    <Button
                      variant="outline"
                      size="sm"
                      className="self-start"
                      disabled={entry.savedToCases}
                      onClick={() => saveToCases(entry)}
                    >
                      {entry.savedToCases ? "사례노트에 저장됨" : "사례노트에 저장"}
                    </Button>
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
