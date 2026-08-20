"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Mascot } from "@/components/Mascot";

const STYLE_STORAGE_KEY = "khr-visual-style";
type VisualStyle = "playful" | "normal";

function applyVisualStyle(style: VisualStyle) {
  document.documentElement.classList.toggle("normal-style", style === "normal");
}

const LINKS = [
  { href: "/", label: "홈" },
  { href: "/assistant", label: "AI 어시스턴트" },
  { href: "/legal-qa", label: "법령 Q&A" },
  { href: "/calculators", label: "빠른 계산기" },
  { href: "/tax", label: "4대보험 계산" },
  { href: "/cases", label: "사례노트" },
  { href: "/study", label: "수험학습" },
  { href: "/exam", label: "오늘의 기출" },
  { href: "/resume", label: "이력서 추출" },
  { href: "/messages", label: "멘트 메이커" },
  { href: "/worklog", label: "업무 로그" },
  { href: "/compliance", label: "컴플라이언스 진단" },
  { href: "/complaint-defense", label: "민원 방어" },
  { href: "/client-negotiation", label: "고객사 메일 도우미" },
  { href: "/attrition-signal", label: "이탈 신호 노트" },
];

export default function NavBar() {
  const pathname = usePathname();
  const [style, setStyle] = useState<VisualStyle>("playful");

  useEffect(() => {
    const stored = window.localStorage.getItem(STYLE_STORAGE_KEY);
    const initial: VisualStyle = stored === "normal" ? "normal" : "playful";
    setStyle(initial);
    applyVisualStyle(initial);
  }, []);

  const toggleStyle = () => {
    const next: VisualStyle = style === "playful" ? "normal" : "playful";
    setStyle(next);
    applyVisualStyle(next);
    window.localStorage.setItem(STYLE_STORAGE_KEY, next);
  };

  return (
    <nav className="border-b bg-background">
      <div className="mx-auto flex max-w-5xl items-center gap-2 px-4 py-3">
        <span className="mr-2 flex shrink-0 items-center gap-1.5 font-semibold text-foreground">
          <Mascot size={26} className="mascot-decor" />
          K-HR Guard
        </span>
        <div className="flex flex-1 items-center gap-1 overflow-x-auto">
          {LINKS.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  buttonVariants({ variant: active ? "default" : "ghost", size: "sm" }),
                  "shrink-0"
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
        <button
          type="button"
          onClick={toggleStyle}
          className="shrink-0 rounded-full border border-border px-3 py-1 text-xs text-muted-foreground transition-colors hover:bg-accent"
        >
          {style === "playful" ? "심플하게 보기" : "꾸밈 보기"}
        </button>
      </div>
    </nav>
  );
}
