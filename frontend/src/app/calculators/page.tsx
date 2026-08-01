"use client";

import { useState } from "react";
import { apiPost } from "@/lib/api";
import type {
  AnnualLeaveResult,
  DispatchExpirationResult,
  MonthlyHourExemptionResult,
  OvertimePremiumResult,
  ProratedInsuranceResult,
  RiskScoreResult,
  SeverancePayResult,
} from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import StatusBadge from "@/components/StatusBadge";

const INDUSTRIES = ["제조업", "건설업", "도소매업", "서비스업"];

export default function CalculatorsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold">빠른 계산기</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          저장하지 않고 그 자리에서 계산만 합니다 - 파견근로자 명단 관리는 회사
          기존 프로그램을 이용하세요.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <SeveranceCalculator />
        <AnnualLeaveCalculator />
        <OvertimeCalculator />
        <ProratedInsuranceCalculator />
        <DispatchExpirationCalculator />
        <MonthlyHourExemptionCalculator />
        <DisguisedContractingCalculator />
        <FreelancerRiskCalculator />
      </div>
    </div>
  );
}

function ToolCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">{children}</CardContent>
    </Card>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <Label className="text-xs">{label}</Label>
      {children}
    </div>
  );
}

function ResultBox({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-md bg-muted p-3 text-sm">{children}</div>
  );
}

function SeveranceCalculator() {
  const [hireDate, setHireDate] = useState("");
  const [wage, setWage] = useState("100000");
  const [result, setResult] = useState<SeverancePayResult | null>(null);

  const calculate = async () => {
    if (!hireDate) return;
    const data = await apiPost<SeverancePayResult>("/calculators/severance-pay", {
      hire_date: hireDate,
      average_daily_wage: Number(wage),
    });
    setResult(data);
  };

  return (
    <ToolCard title="퇴직금 계산">
      <div className="flex gap-2">
        <Field label="입사일">
          <Input type="date" value={hireDate} onChange={(e) => setHireDate(e.target.value)} />
        </Field>
        <Field label="평균임금(1일분)">
          <Input type="number" value={wage} onChange={(e) => setWage(e.target.value)} />
        </Field>
      </div>
      <Button size="sm" onClick={calculate}>계산</Button>
      {result && (
        <ResultBox>
          <p>{result.reason}</p>
          {result.eligible && (
            <p className="mt-1 text-lg font-bold">
              {result.severance_pay.toLocaleString()}원
            </p>
          )}
        </ResultBox>
      )}
    </ToolCard>
  );
}

function AnnualLeaveCalculator() {
  const [hireDate, setHireDate] = useState("");
  const [result, setResult] = useState<AnnualLeaveResult | null>(null);

  const calculate = async () => {
    if (!hireDate) return;
    const data = await apiPost<AnnualLeaveResult>("/calculators/annual-leave", {
      hire_date: hireDate,
    });
    setResult(data);
  };

  return (
    <ToolCard title="연차휴가 계산">
      <Field label="입사일">
        <Input type="date" value={hireDate} onChange={(e) => setHireDate(e.target.value)} />
      </Field>
      <Button size="sm" onClick={calculate}>계산</Button>
      {result && (
        <ResultBox>
          <p className="text-lg font-bold">{result.granted_days}일</p>
          <p className="mt-1 text-xs text-muted-foreground">{result.basis}</p>
        </ResultBox>
      )}
    </ToolCard>
  );
}

function OvertimeCalculator() {
  const [hourlyWage, setHourlyWage] = useState("10000");
  const [overtime, setOvertime] = useState("0");
  const [night, setNight] = useState("0");
  const [holiday, setHoliday] = useState("0");
  const [result, setResult] = useState<OvertimePremiumResult | null>(null);

  const calculate = async () => {
    const data = await apiPost<OvertimePremiumResult>("/calculators/overtime-premium", {
      hourly_wage: Number(hourlyWage),
      overtime_hours: Number(overtime),
      night_hours: Number(night),
      holiday_hours: Number(holiday),
    });
    setResult(data);
  };

  return (
    <ToolCard title="연장·야간·휴일수당 계산">
      <Field label="통상시급">
        <Input type="number" value={hourlyWage} onChange={(e) => setHourlyWage(e.target.value)} />
      </Field>
      <div className="flex gap-2">
        <Field label="연장(h)">
          <Input type="number" value={overtime} onChange={(e) => setOvertime(e.target.value)} />
        </Field>
        <Field label="야간(h)">
          <Input type="number" value={night} onChange={(e) => setNight(e.target.value)} />
        </Field>
        <Field label="휴일(h)">
          <Input type="number" value={holiday} onChange={(e) => setHoliday(e.target.value)} />
        </Field>
      </div>
      <Button size="sm" onClick={calculate}>계산</Button>
      {result && (
        <ResultBox>
          <p className="text-lg font-bold">{result.total_premium_pay.toLocaleString()}원</p>
          <p className="mt-1 text-xs text-muted-foreground">
            연장 {result.overtime_pay.toLocaleString()} · 야간{" "}
            {result.night_pay.toLocaleString()} · 휴일 {result.holiday_pay.toLocaleString()}
          </p>
        </ResultBox>
      )}
    </ToolCard>
  );
}

function ProratedInsuranceCalculator() {
  const [income, setIncome] = useState("3000000");
  const [industry, setIndustry] = useState(INDUSTRIES[0]);
  const [daysWorked, setDaysWorked] = useState("15");
  const [daysInMonth, setDaysInMonth] = useState("30");
  const [result, setResult] = useState<ProratedInsuranceResult | null>(null);

  const calculate = async () => {
    const data = await apiPost<ProratedInsuranceResult>("/tax/prorated-insurance", {
      monthly_base_income: Number(income),
      industry,
      days_worked: Number(daysWorked),
      days_in_month: Number(daysInMonth),
    });
    setResult(data);
  };

  return (
    <ToolCard title="4대보험 중도정산(일할계산)">
      <div className="flex gap-2">
        <Field label="월 기준소득">
          <Input type="number" value={income} onChange={(e) => setIncome(e.target.value)} />
        </Field>
        <Field label="업종">
          <select
            className="h-8 rounded-lg border border-input bg-transparent px-2 text-sm"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
          >
            {INDUSTRIES.map((i) => (
              <option key={i} value={i}>{i}</option>
            ))}
          </select>
        </Field>
      </div>
      <div className="flex gap-2">
        <Field label="근무일수">
          <Input type="number" value={daysWorked} onChange={(e) => setDaysWorked(e.target.value)} />
        </Field>
        <Field label="해당월 총일수">
          <Input type="number" value={daysInMonth} onChange={(e) => setDaysInMonth(e.target.value)} />
        </Field>
      </div>
      <Button size="sm" onClick={calculate}>계산</Button>
      {result && (
        <ResultBox>
          <p className="text-lg font-bold">
            {result.employee_total_premium.toLocaleString()}원
          </p>
          <p className="mt-1 text-xs text-muted-foreground">{result.disclaimer}</p>
        </ResultBox>
      )}
    </ToolCard>
  );
}

function DispatchExpirationCalculator() {
  const [startDate, setStartDate] = useState("");
  const [result, setResult] = useState<DispatchExpirationResult | null>(null);

  const calculate = async () => {
    if (!startDate) return;
    const data = await apiPost<DispatchExpirationResult>("/risk/dispatch-expiration", {
      contract_start_date: startDate,
    });
    setResult(data);
  };

  return (
    <ToolCard title="파견 만료 D-Day">
      <Field label="파견 시작일">
        <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
      </Field>
      <Button size="sm" onClick={calculate}>계산</Button>
      {result && (
        <ResultBox>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold">
              {result.d_day >= 0 ? `D-${result.d_day}` : `D+${-result.d_day}`}
            </span>
            <StatusBadge status={result.status} />
          </div>
          <p className="mt-1 text-xs text-muted-foreground">만료예정일 {result.limit_date}</p>
        </ResultBox>
      )}
    </ToolCard>
  );
}

function MonthlyHourExemptionCalculator() {
  const [hours, setHours] = useState("");
  const [result, setResult] = useState<MonthlyHourExemptionResult | null>(null);

  const calculate = async () => {
    if (!hours) return;
    const data = await apiPost<MonthlyHourExemptionResult>(
      "/risk/monthly-hour-exemption",
      { monthly_hours: Number(hours) }
    );
    setResult(data);
  };

  return (
    <ToolCard title="4대보험 적용제외(월 60시간) 확인">
      <Field label="월 소정근로시간">
        <Input type="number" value={hours} onChange={(e) => setHours(e.target.value)} />
      </Field>
      <Button size="sm" onClick={calculate}>확인</Button>
      {result && (
        <ResultBox>
          <p>{result.reason}</p>
        </ResultBox>
      )}
    </ToolCard>
  );
}

function DisguisedContractingCalculator() {
  const [factors, setFactors] = useState({
    principal_directs_work: false,
    integrated_into_principal_business: false,
    lacks_independent_equipment_or_expertise: false,
    scope_of_work_not_fixed: false,
  });
  const [result, setResult] = useState<RiskScoreResult | null>(null);

  const calculate = async () => {
    const data = await apiPost<RiskScoreResult>("/risk/disguised-contracting", factors);
    setResult(data);
  };

  const labels: Record<keyof typeof factors, string> = {
    principal_directs_work: "원청이 작업을 직접 지시하는가",
    integrated_into_principal_business: "원청 사업에 실질적으로 편입됐는가",
    lacks_independent_equipment_or_expertise: "자체 설비·전문성 없이 원청에 의존하는가",
    scope_of_work_not_fixed: "계약상 업무 범위가 불명확한가",
  };

  return (
    <ToolCard title="위장도급 리스크 체크">
      {(Object.keys(factors) as (keyof typeof factors)[]).map((key) => (
        <label key={key} className="flex items-center gap-2 text-xs">
          <input
            type="checkbox"
            checked={factors[key]}
            onChange={(e) => setFactors({ ...factors, [key]: e.target.checked })}
          />
          {labels[key]}
        </label>
      ))}
      <Button size="sm" onClick={calculate}>판정</Button>
      {result && (
        <ResultBox>
          <div className="flex items-center gap-2">
            <span className="font-bold">{result.score}/{result.max_score}</span>
            <StatusBadge status={result.status} />
          </div>
          <p className="mt-1 text-xs text-muted-foreground">{result.disclaimer}</p>
        </ResultBox>
      )}
    </ToolCard>
  );
}

function FreelancerRiskCalculator() {
  const [factors, setFactors] = useState({
    fixed_working_hours_and_place: false,
    subject_to_direction_and_supervision: false,
    cannot_delegate_or_use_substitute: false,
    exclusive_and_continuous_engagement: false,
  });
  const [result, setResult] = useState<RiskScoreResult | null>(null);

  const calculate = async () => {
    const data = await apiPost<RiskScoreResult>(
      "/risk/freelancer-misclassification",
      factors
    );
    setResult(data);
  };

  const labels: Record<keyof typeof factors, string> = {
    fixed_working_hours_and_place: "근무시간·장소가 지정되어 있는가",
    subject_to_direction_and_supervision: "업무수행 과정에서 지휘·감독을 받는가",
    cannot_delegate_or_use_substitute: "제3자에게 대체 수행시킬 수 없는가",
    exclusive_and_continuous_engagement: "특정 사업장에 전속·계속 종사하는가",
  };

  return (
    <ToolCard title="위장프리랜서(3.3%) 리스크 체크">
      {(Object.keys(factors) as (keyof typeof factors)[]).map((key) => (
        <label key={key} className="flex items-center gap-2 text-xs">
          <input
            type="checkbox"
            checked={factors[key]}
            onChange={(e) => setFactors({ ...factors, [key]: e.target.checked })}
          />
          {labels[key]}
        </label>
      ))}
      <Button size="sm" onClick={calculate}>판정</Button>
      {result && (
        <ResultBox>
          <div className="flex items-center gap-2">
            <span className="font-bold">{result.score}/{result.max_score}</span>
            <StatusBadge status={result.status} />
          </div>
          <p className="mt-1 text-xs text-muted-foreground">{result.disclaimer}</p>
        </ResultBox>
      )}
    </ToolCard>
  );
}
