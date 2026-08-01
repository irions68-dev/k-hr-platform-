"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet, ApiError } from "@/lib/api";
import type { MorningBrief } from "@/lib/types";
import StatusBadge from "@/components/StatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export default function DashboardPage() {
  const [brief, setBrief] = useState<MorningBrief | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<MorningBrief>("/brief/morning")
      .then(setBrief)
      .catch((err: unknown) => {
        setError(
          err instanceof ApiError
            ? `백엔드 오류 (${err.status}): ${err.message}`
            : "백엔드에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인하세요."
        );
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-muted-foreground">불러오는 중...</p>;
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
        {error}
      </div>
    );
  }

  if (!brief) return null;

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">아침 브리핑 · {brief.brief_date}</h1>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <SummaryCard label="전체 파견근로자" value={brief.total_workers} />
        <SummaryCard
          label="만료 임박/경과"
          value={brief.at_risk_count}
          warn={brief.at_risk_count > 0}
        />
        <SummaryCard
          label="오늘 복습할 항목"
          value={brief.due_study_count}
          warn={brief.due_study_count > 0}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>파견 만료 위험 근로자</CardTitle>
        </CardHeader>
        <CardContent>
          {brief.at_risk_workers.length === 0 ? (
            <p className="text-sm text-muted-foreground">위험 대상이 없습니다.</p>
          ) : (
            <ul className="flex flex-col divide-y divide-border">
              {brief.at_risk_workers.map((w) => (
                <li key={w.id} className="flex items-center justify-between py-2 text-sm">
                  <span className="font-medium">
                    {w.name} <span className="text-muted-foreground">({w.position})</span>
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="text-muted-foreground">
                      {w.d_day >= 0 ? `D-${w.d_day}` : `D+${-w.d_day}`}
                    </span>
                    <StatusBadge status={w.status} />
                  </span>
                </li>
              ))}
            </ul>
          )}
          <Link href="/dispatch-workers" className="mt-3 inline-block text-sm text-primary hover:underline">
            전체 파견근로자 관리 →
          </Link>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>오늘 복습할 학습 항목</CardTitle>
        </CardHeader>
        <CardContent>
          {brief.due_study_items.length === 0 ? (
            <p className="text-sm text-muted-foreground">오늘 복습할 항목이 없습니다.</p>
          ) : (
            <ul className="flex flex-col divide-y divide-border">
              {brief.due_study_items.map((item) => (
                <li key={item.id} className="py-2 text-sm">
                  {item.keyword}
                </li>
              ))}
            </ul>
          )}
          <Link href="/study" className="mt-3 inline-block text-sm text-primary hover:underline">
            학습 복습하러 가기 →
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  warn = false,
}: {
  label: string;
  value: number;
  warn?: boolean;
}) {
  return (
    <Card>
      <CardContent>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p
          className={cn(
            "mt-1 text-3xl font-bold",
            warn ? "text-amber-600 dark:text-amber-400" : "text-foreground"
          )}
        >
          {value}
        </p>
      </CardContent>
    </Card>
  );
}
