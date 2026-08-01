"use client";

import { useState } from "react";
import { apiPost } from "@/lib/api";
import type { FourInsurancesResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const INDUSTRIES = ["제조업", "건설업", "도소매업", "서비스업"];

export default function TaxPage() {
  const [income, setIncome] = useState("3000000");
  const [industry, setIndustry] = useState(INDUSTRIES[0]);
  const [result, setResult] = useState<FourInsurancesResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const calculate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const data = await apiPost<FourInsurancesResult>("/tax/four-insurances", {
        monthly_base_income: Number(income),
        industry,
      });
      setResult(data);
    } catch {
      setError("계산에 실패했습니다.");
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">4대보험 계산기</h1>
      <div className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-300">
        ⚠️ 요율은 2026-08-01 웹검색으로 확인한 값입니다(출처는 백엔드 yaml 주석 참고). 산재보험료율은
        업종별 세부코드에 따라 편차가 크므로 대표 예시일 뿐입니다. 실사용 전
        국민연금공단·건강보험공단·근로복지공단 공식 고시로 재확인하세요.
      </div>

      <Card>
        <CardContent>
          <form onSubmit={calculate} className="flex flex-wrap items-end gap-3">
            <div className="flex flex-col gap-1">
              <Label>기준소득월액 (원)</Label>
              <Input
                type="number"
                min={0}
                value={income}
                onChange={(e) => setIncome(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-1">
              <Label>업종</Label>
              <Select value={industry} onValueChange={(v) => setIndustry(v as string)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {INDUSTRIES.map((i) => (
                    <SelectItem key={i} value={i}>
                      {i}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button type="submit">계산</Button>
          </form>
        </CardContent>
      </Card>

      {error && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {result && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <ResultCard label="국민연금 (근로자부담)" value={result.national_pension.premium} />
          <ResultCard
            label="건강보험+장기요양 (근로자부담)"
            value={result.health_insurance.total_premium}
          />
          <ResultCard label="고용보험 (근로자부담)" value={result.employment_insurance.premium} />
          <ResultCard
            label={`산재보험 (사업주 100% 부담, ${result.industrial_accident_insurance.industry})`}
            value={result.industrial_accident_insurance.premium}
          />
          <Card className="col-span-full bg-muted">
            <CardContent>
              <p className="text-sm text-muted-foreground">근로자 부담 합계</p>
              <p className="text-2xl font-bold">
                {result.employee_total_premium.toLocaleString()}원
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                적용 요율 기준일: {result.rate_effective_date}
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

function ResultCard({ label, value }: { label: string; value: number }) {
  return (
    <Card>
      <CardContent>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="mt-1 text-xl font-bold">{value.toLocaleString()}원</p>
      </CardContent>
    </Card>
  );
}
