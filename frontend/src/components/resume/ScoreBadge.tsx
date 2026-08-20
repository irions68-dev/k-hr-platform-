export function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 80
      ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
      : score >= 50
        ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
        : "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300";
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-sm font-semibold ${color}`}>
      {score}점
    </span>
  );
}
