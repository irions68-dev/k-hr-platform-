"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import type { DailyQuestion, ExamAttemptResult, ExamStats } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const CHOICE_MARKS = ["①", "②", "③", "④", "⑤"];

export default function ExamPage() {
  const [questions, setQuestions] = useState<DailyQuestion[]>([]);
  const [index, setIndex] = useState(0);
  const [result, setResult] = useState<ExamAttemptResult | null>(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [stats, setStats] = useState<ExamStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadStats = () => apiGet<ExamStats>("/exam/stats").then(setStats);

  useEffect(() => {
    setLoading(true);
    Promise.all([apiGet<DailyQuestion[]>("/exam/daily"), loadStats()])
      .then(([daily]) => setQuestions(daily))
      .catch(() => setError("오늘의 기출문제를 불러오지 못했습니다."))
      .finally(() => setLoading(false));
  }, []);

  const current = questions[index];
  const done = questions.length > 0 && index >= questions.length;

  const selectAnswer = async (choiceNumber: number) => {
    if (!current || submitting || result) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await apiPost<ExamAttemptResult>("/exam/attempts", {
        question_id: current.id,
        selected_index: choiceNumber,
      });
      setResult(res);
      if (res.correct) setCorrectCount((c) => c + 1);
      loadStats();
    } catch {
      setError("채점에 실패했습니다.");
    } finally {
      setSubmitting(false);
    }
  };

  const nextQuestion = () => {
    setResult(null);
    setIndex((i) => i + 1);
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">오늘의 기출문제</h1>
        {stats && (
          <p className="text-xs text-muted-foreground">
            누적 {stats.total_attempts}문제 풀이 ·{" "}
            {stats.accuracy !== null ? `정답률 ${Math.round(stats.accuracy * 100)}%` : "정답률 -"}
          </p>
        )}
      </div>
      <p className="text-sm text-muted-foreground">
        2025년 제34회 공인노무사 1차시험 기출(Q-net 공식 문제·정답 기반). 매일
        3문제씩 SM-2 간격반복으로 출제되며, 틀린 문제는 금방 다시 나옵니다.
      </p>

      {loading ? (
        <p className="text-sm text-muted-foreground">불러오는 중...</p>
      ) : error && questions.length === 0 ? (
        <p className="text-sm text-destructive">{error}</p>
      ) : done ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-2 py-8 text-center">
            <p className="text-lg font-semibold">
              오늘 {questions.length}문제 중 {correctCount}개 정답
            </p>
            <p className="text-sm text-muted-foreground">
              내일 또 3문제가 새로 나옵니다. 틀린 문제는 더 빨리 재출제됩니다.
            </p>
          </CardContent>
        </Card>
      ) : current ? (
        <Card>
          <CardContent className="flex flex-col gap-4">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{current.subject}</Badge>
              <span className="text-xs text-muted-foreground">
                {index + 1} / {questions.length}
              </span>
            </div>
            <p className="font-medium leading-relaxed">{current.question}</p>
            <div className="flex flex-col gap-2">
              {current.choices.map((choice, i) => {
                const choiceNumber = i + 1;
                const isAnswer = result && choiceNumber === result.answer_index;
                return (
                  <button
                    key={i}
                    type="button"
                    disabled={submitting || result !== null}
                    onClick={() => selectAnswer(choiceNumber)}
                    className={`rounded-lg border px-3 py-2 text-left text-sm transition-colors disabled:cursor-default ${
                      result
                        ? isAnswer
                          ? "border-emerald-500 bg-emerald-50 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300"
                          : "border-border opacity-60"
                        : "border-border hover:bg-accent"
                    }`}
                  >
                    <span className="mr-2 font-semibold">{CHOICE_MARKS[i]}</span>
                    {choice}
                  </button>
                );
              })}
            </div>

            {result && (
              <div
                className={`flex flex-col gap-2 rounded-lg border p-3 text-sm ${
                  result.correct
                    ? "border-emerald-500/40 bg-emerald-50 dark:bg-emerald-900/20"
                    : "border-destructive/40 bg-destructive/10"
                }`}
              >
                <p className="font-semibold">
                  {result.correct ? "정답입니다" : `오답입니다 (정답: ${CHOICE_MARKS[result.answer_index - 1]})`}
                </p>
                {result.explanation ? (
                  <p className="text-muted-foreground">{result.explanation}</p>
                ) : (
                  <p className="text-muted-foreground">
                    해설은 아직 준비 중입니다. 정답만 참고하세요.
                  </p>
                )}
                <Button size="sm" className="self-start" onClick={nextQuestion}>
                  다음 문제
                </Button>
              </div>
            )}
            {error && <p className="text-sm text-destructive">{error}</p>}
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
