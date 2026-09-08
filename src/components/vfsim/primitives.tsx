import { AlertTriangle, Inbox, Loader2, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import type { RiskLevel } from "@/lib/mock-data";

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description: string;
  actions?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">{title}</h1>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{description}</p>
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}

export function Panel({
  title,
  subtitle,
  icon: Icon,
  actions,
  className,
  bodyClassName,
  children,
}: {
  title?: string;
  subtitle?: string;
  icon?: LucideIcon;
  actions?: ReactNode;
  className?: string;
  bodyClassName?: string;
  children: ReactNode;
}) {
  return (
    <section
      className={cn(
        "rounded-lg border border-border bg-card shadow-[0_1px_0_0_color-mix(in_oklab,var(--foreground)_6%,transparent)_inset]",
        className,
      )}
    >
      {title ? (
        <header className="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
          <div className="flex items-center gap-2">
            {Icon ? <Icon className="size-4 text-primary" aria-hidden /> : null}
            <div>
              <h2 className="text-sm font-semibold text-foreground">{title}</h2>
              {subtitle ? (
                <p className="text-xs text-muted-foreground">{subtitle}</p>
              ) : null}
            </div>
          </div>
          {actions}
        </header>
      ) : null}
      <div className={cn("p-4", bodyClassName)}>{children}</div>
    </section>
  );
}

const riskStyles: Record<RiskLevel, string> = {
  safe: "border-safe/40 bg-safe/10 text-safe",
  watch: "border-watch/40 bg-watch/10 text-watch",
  elevated: "border-elevated/40 bg-elevated/10 text-elevated",
  critical: "border-critical/50 bg-critical/15 text-critical",
};

export function RiskBadge({ level, score }: { level: RiskLevel; score?: number }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide",
        riskStyles[level],
      )}
    >
      <span className="size-1.5 rounded-full bg-current" />
      {level}
      {score !== undefined ? <span className="tabular">{score.toFixed(2)}</span> : null}
    </span>
  );
}

export function LoadingState({ label = "Loading data", rows = 3 }: { label?: string; rows?: number }) {
  return (
    <div className="space-y-3" role="status" aria-live="polite">
      <p className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="size-4 animate-spin" aria-hidden />
        {label}…
      </p>
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-10 w-full bg-surface-2" />
      ))}
    </div>
  );
}

export function ErrorState({
  message = "Could not reach the simulation service.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="flex flex-col items-start gap-3 rounded-md border border-destructive/40 bg-destructive/10 p-4"
    >
      <p className="flex items-center gap-2 text-sm font-medium text-destructive">
        <AlertTriangle className="size-4" aria-hidden />
        {message}
      </p>
      {onRetry ? (
        <Button size="sm" variant="outline" onClick={onRetry}>
          Retry request
        </Button>
      ) : null}
    </div>
  );
}

export function EmptyState({
  title = "Nothing to show yet",
  hint,
}: {
  title?: string;
  hint?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-md border border-dashed border-border px-6 py-10 text-center">
      <Inbox className="size-5 text-muted-foreground" aria-hidden />
      <p className="text-sm font-medium text-foreground">{title}</p>
      {hint ? <p className="max-w-sm text-xs text-muted-foreground">{hint}</p> : null}
    </div>
  );
}

export function StatCard({
  label,
  value,
  unit,
  hint,
  icon: Icon,
  tone = "default",
}: {
  label: string;
  value: string | number;
  unit?: string;
  hint?: string;
  icon?: LucideIcon;
  tone?: "default" | "critical" | "safe" | "watch";
}) {
  const tones = {
    default: "text-foreground",
    critical: "text-critical",
    safe: "text-safe",
    watch: "text-watch",
  } as const;
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between">
        <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
        {Icon ? <Icon className="size-4 text-muted-foreground" aria-hidden /> : null}
      </div>
      <p className={cn("mt-2 text-2xl font-semibold tabular", tones[tone])}>
        {value}
        {unit ? <span className="ml-1 text-sm text-muted-foreground">{unit}</span> : null}
      </p>
      {hint ? <p className="mt-1 text-xs text-muted-foreground">{hint}</p> : null}
    </div>
  );
}
