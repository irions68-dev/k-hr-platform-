"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import type { Mood, TodayWellbeing } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const MOOD_OPTIONS: { value: Mood; emoji: string; label: string }[] = [
  { value: "great", emoji: "😊", label: "최고예요" },
  { value: "good", emoji: "🙂", label: "좋아요" },
  { value: "okay", emoji: "😐", label: "그냥그래요" },
  { value: "tired", emoji: "😴", label: "피곤해요" },
  { value: "stressed", emoji: "😣", label: "힘들어요" },
];

export function WellbeingCard() {
  const [data, setData] = useState<TodayWellbeing | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    apiGet<TodayWellbeing>("/wellbeing/today")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  async function pickMood(mood: Mood) {
    setSubmitting(true);
    try {
      const result = await apiPost<TodayWellbeing>("/wellbeing/mood", { mood });
      setData(result);
    } catch {
      // 조용히 무시 - 힐링 기능이 업무 흐름을 막으면 안 됨
    } finally {
      setSubmitting(false);
    }
  }

  if (!data) return null;

  const achievements = [
    data.cases_today > 0 ? `상담 케이스 ${data.cases_today}건 정리` : null,
    data.exam_new_today > 0 ? `기출문제 ${data.exam_new_today}개 새로 학습` : null,
    data.streak_days > 1 ? `기분 기록 ${data.streak_days}일 연속` : null,
  ].filter((v): v is string => Boolean(v));

  return (
    <Card className="bg-gradient-to-br from-rose-50 to-violet-50 dark:from-rose-950/20 dark:to-violet-950/20">
      <CardHeader>
        <CardTitle>오늘 하루, 어떠셨어요?</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="flex flex-wrap gap-2">
          {MOOD_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              disabled={submitting}
              onClick={() => pickMood(opt.value)}
              className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm transition-colors disabled:opacity-50 ${
                data.mood_today === opt.value
                  ? "border-primary bg-primary/10 font-medium"
                  : "border-border bg-background hover:bg-accent"
              }`}
            >
              <span>{opt.emoji}</span>
              <span>{opt.label}</span>
            </button>
          ))}
        </div>

        {data.mood_response && (
          <p className="text-sm text-muted-foreground">{data.mood_response}</p>
        )}

        <p className="text-sm italic text-muted-foreground">“{data.quote}”</p>

        {achievements.length > 0 && (
          <div>
            <p className="text-xs font-medium text-muted-foreground">오늘의 작은 성취</p>
            <ul className="mt-1 flex flex-col gap-0.5">
              {achievements.map((a) => (
                <li key={a} className="text-sm">
                  ✓ {a}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
