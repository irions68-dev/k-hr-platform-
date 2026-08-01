"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import type { StudyReviewItem } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";

export default function StudyPage() {
  const [dueItems, setDueItems] = useState<StudyReviewItem[]>([]);
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    apiGet<StudyReviewItem[]>("/study/due")
      .then(setDueItems)
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const addKeyword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim()) return;
    await apiPost("/study/review-items", { keyword: keyword.trim() });
    setKeyword("");
    load();
  };

  const review = async (id: number, quality: number) => {
    await apiPost(`/study/review-items/${id}/review`, { quality });
    load();
  };

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">수험 학습 복습</h1>

      <form onSubmit={addKeyword} className="flex gap-2">
        <Input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="새 복습 키워드 추가 (예: 위장도급 판단기준)"
          className="flex-1"
        />
        <Button type="submit">추가</Button>
      </form>

      <div className="flex flex-col gap-3">
        {loading ? (
          <p className="text-sm text-muted-foreground">불러오는 중...</p>
        ) : dueItems.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            오늘 복습할 항목이 없습니다. 잘하고 계세요!
          </p>
        ) : (
          dueItems.map((item) => (
            <Card key={item.id}>
              <CardContent className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-medium">{item.keyword}</p>
                  <p className="text-xs text-muted-foreground">
                    복습 {item.repetitions}회차 · 다음 복습일 {item.next_review_date}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button variant="destructive" size="sm" onClick={() => review(item.id, 1)}>
                    기억 안 남
                  </Button>
                  <Button
                    size="sm"
                    className="bg-amber-100 text-amber-700 hover:bg-amber-200 dark:bg-amber-900/40 dark:text-amber-300"
                    onClick={() => review(item.id, 3)}
                  >
                    애매함
                  </Button>
                  <Button
                    size="sm"
                    className="bg-emerald-100 text-emerald-700 hover:bg-emerald-200 dark:bg-emerald-900/40 dark:text-emerald-300"
                    onClick={() => review(item.id, 5)}
                  >
                    잘 기억함
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
