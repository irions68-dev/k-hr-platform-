"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/api";
import type { MorningBrief } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { WellbeingCard } from "@/components/WellbeingCard";
import { Mascot } from "@/components/Mascot";

const QUICK_LINKS = [
  { href: "/legal-qa", title: "법령 Q&A", desc: "전화 받으며 바로 물어보기" },
  { href: "/calculators", title: "퇴직금·연차·수당 계산기", desc: "즉시 계산, 저장 안 함" },
  { href: "/tax", title: "4대보험 계산기", desc: "보험료 얼마 떼는지" },
];

export default function DashboardPage() {
  const [brief, setBrief] = useState<MorningBrief | null>(null);

  useEffect(() => {
    apiGet<MorningBrief>("/brief/morning")
      .then(setBrief)
      .catch(() => setBrief(null));
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <div className="relative shrink-0 mascot-decor">
          <Mascot size={56} />
        </div>
        <div>
          <h1 className="text-2xl font-bold">K-HR Guard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            근로자 전화 문의에 빠르고 정확하게 답하기 위한 헬프데스크입니다.
          </p>
        </div>
      </div>

      <WellbeingCard />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {QUICK_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="block rounded-lg border border-border bg-card p-4 transition-colors hover:bg-accent"
          >
            <p className="font-semibold">{link.title}</p>
            <p className="mt-1 text-sm text-muted-foreground">{link.desc}</p>
          </Link>
        ))}
      </div>

      {brief && brief.due_study_count > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>오늘 복습할 수험 학습 항목 ({brief.due_study_count}개)</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col divide-y divide-border">
              {brief.due_study_items.map((item) => (
                <li key={item.id} className="py-2 text-sm">
                  {item.keyword}
                </li>
              ))}
            </ul>
            <Link
              href="/study"
              className={cn(buttonVariants({ variant: "outline", size: "sm" }), "mt-3")}
            >
              복습하러 가기
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
