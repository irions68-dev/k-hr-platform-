import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { RiskStatus } from "@/lib/types";

const STYLES: Record<RiskStatus, string> = {
  normal:
    "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
  warning: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
  critical: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
};

const LABELS: Record<RiskStatus, string> = {
  normal: "정상",
  warning: "주의",
  critical: "위험",
};

export default function StatusBadge({ status }: { status: RiskStatus }) {
  return <Badge className={cn(STYLES[status])}>{LABELS[status]}</Badge>;
}
