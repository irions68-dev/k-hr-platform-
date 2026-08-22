"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL, getStoredPassword, setStoredPassword } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Status = "checking" | "authorized" | "needs-password";

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<Status>("checking");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [showSlowNotice, setShowSlowNotice] = useState(false);

  const check = async (candidatePassword: string) => {
    const res = await fetch(`${API_BASE_URL}/brief/morning`, {
      cache: "no-store",
      headers: candidatePassword ? { "X-App-Password": candidatePassword } : {},
    });
    return res.status !== 401;
  };

  useEffect(() => {
    // Render 무료플랜은 15분 미사용 시 슬립되고 재기동에 20~30초 걸린다.
    // 이 지연 중엔 아무 표시가 없으면 화면이 멈춘 것처럼 보여서(실제 신고
    // 사례), 3초 넘게 걸리면 안심 문구를 보여준다.
    const slowTimer = setTimeout(() => setShowSlowNotice(true), 3000);
    const stored = getStoredPassword();
    check(stored)
      .then((ok) => setStatus(ok ? "authorized" : "needs-password"))
      .catch(() => setStatus("needs-password"))
      .finally(() => clearTimeout(slowTimer));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const ok = await check(password);
    if (ok) {
      setStoredPassword(password);
      setStatus("authorized");
    } else {
      setError("비밀번호가 올바르지 않습니다.");
    }
  };

  if (status === "checking") {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 p-6 text-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-muted border-t-primary" />
        <p className="text-sm text-muted-foreground">확인 중...</p>
        {showSlowNotice && (
          <p className="max-w-xs text-xs text-muted-foreground">
            서버가 잠시 쉬고 있었다면 깨우는 데 최대 30초 정도 걸릴 수 있어요.
            잠시만 기다려주세요.
          </p>
        )}
      </div>
    );
  }

  if (status === "needs-password") {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <form
          onSubmit={handleSubmit}
          className="flex w-full max-w-xs flex-col gap-3 rounded-lg border border-border bg-card p-6"
        >
          <h1 className="text-lg font-semibold">K-HR Guard 로그인</h1>
          <Input
            type="password"
            placeholder="비밀번호"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoFocus
          />
          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button type="submit">입장</Button>
        </form>
      </div>
    );
  }

  return <>{children}</>;
}
