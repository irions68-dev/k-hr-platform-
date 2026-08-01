"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const LINKS = [
  { href: "/", label: "대시보드" },
  { href: "/dispatch-workers", label: "파견근로자" },
  { href: "/legal-qa", label: "법령 Q&A" },
  { href: "/cases", label: "사례노트" },
  { href: "/study", label: "수험학습" },
  { href: "/tax", label: "4대보험 계산" },
];

export default function NavBar() {
  const pathname = usePathname();

  return (
    <nav className="border-b bg-background">
      <div className="mx-auto flex max-w-5xl items-center gap-1 overflow-x-auto px-4 py-3">
        <span className="mr-4 shrink-0 font-semibold text-foreground">K-HR Guard</span>
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
    </nav>
  );
}
