"use client";

import { Input } from "@/components/ui/input";

function formatWithCommas(raw: string): string {
  const digits = raw.replace(/[^\d]/g, "");
  if (!digits) return "";
  return Number(digits).toLocaleString("ko-KR");
}

interface CurrencyInputProps {
  value: string;
  onChange: (rawDigits: string) => void;
  className?: string;
  placeholder?: string;
}

/** 금액 입력란. 화면엔 천단위 콤마로 보여주고, onChange엔 숫자만 전달한다. */
export default function CurrencyInput({
  value,
  onChange,
  className,
  placeholder,
}: CurrencyInputProps) {
  return (
    <Input
      type="text"
      inputMode="numeric"
      value={formatWithCommas(value)}
      onChange={(e) => onChange(e.target.value.replace(/[^\d]/g, ""))}
      className={className}
      placeholder={placeholder}
    />
  );
}
