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

  const check = async (candidatePassword: string) => {
    const res = await fetch(`${API_BASE_URL}/brief/morning`, {
      cache: "no-store",
      headers: candidatePassword ? { "X-App-Password": candidatePassword } : {},
    });
    return res.status !== 401;
  };

  useEffect(() => {
    const stored = getStoredPassword();
    check(stored)
      .then((ok) => setStatus(ok ? "authorized" : "needs-password"))
      .catch(() => setStatus("needs-password"));
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
    return <div className="p-6 text-sm text-muted-foreground">확인 중...</div>;
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
