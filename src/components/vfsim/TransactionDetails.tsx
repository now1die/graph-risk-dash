import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { FileWarning, ShieldCheck } from "lucide-react";

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { ErrorState, LoadingState, EmptyState, RiskBadge } from "@/components/vfsim/primitives";
import { api } from "@/services/api";
import { cn } from "@/lib/utils";

export function TransactionDetails({
  transactionId,
  open,
  onOpenChange,
}: {
  transactionId: string | null;
  open: boolean;
  onOpenChange: (v: boolean) => void;
}) {
  const txQuery = useQuery({
    queryKey: ["transaction", transactionId],
    queryFn: () => api.getTransaction(transactionId as string),
    enabled: Boolean(transactionId) && open,
  });
  const riskQuery = useQuery({
    queryKey: ["risk", transactionId],
    queryFn: () => api.getRiskAssessment(transactionId as string),
    enabled: Boolean(transactionId) && open,
  });

  const tx = txQuery.data;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto border-border bg-card sm:max-w-lg">
        <SheetHeader>
          <SheetTitle className="tabular text-foreground">
            {transactionId ?? "No transaction"}
          </SheetTitle>
          <SheetDescription>
            Operation log, journal coverage and model risk attribution for the selected
            transaction.
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-5 px-4 pb-8">
          {!transactionId ? (
            <EmptyState
              title="Select a transaction"
              hint="Pick a row in the table to inspect its operations."
            />
          ) : txQuery.isPending ? (
            <LoadingState label="Fetching transaction" rows={4} />
          ) : txQuery.isError || !tx ? (
            <ErrorState
              message="Transaction could not be loaded."
              onRetry={() => void txQuery.refetch()}
            />
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <RiskBadge level={tx.riskLevel} score={tx.riskScore} />
                <span className="rounded-full border border-border px-2 py-0.5 text-[11px] uppercase tracking-wide text-muted-foreground">
                  {tx.status}
                </span>
                <span className="tabular text-xs text-muted-foreground">{tx.durationMs} ms</span>
              </div>

              <div>
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Operation log
                </h3>
                <ol className="space-y-1.5">
                  {tx.operations.map((op) => (
                    <li
                      key={op.id}
                      className="rounded-md border border-border bg-surface-2/60 px-3 py-2"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="tabular text-xs text-primary">
                          #{op.seq} {op.op}
                        </span>
                        <span
                          className={cn(
                            "inline-flex items-center gap-1 text-[11px]",
                            op.journaled ? "text-safe" : "text-critical",
                          )}
                        >
                          {op.journaled ? (
                            <ShieldCheck className="size-3.5" aria-hidden />
                          ) : (
                            <FileWarning className="size-3.5" aria-hidden />
                          )}
                          {op.journaled ? "journaled" : "unjournaled"}
                        </span>
                      </div>
                      <p className="tabular mt-1 break-all text-xs text-muted-foreground">
                        {op.target}
                      </p>
                      <p className="tabular mt-1 text-[11px] text-muted-foreground">
                        {op.bytes ? `${(op.bytes / 1024).toFixed(0)} KiB` : "no payload"} · risk
                        {op.riskDelta >= 0 ? " +" : " "}
                        {op.riskDelta.toFixed(2)}
                      </p>
                    </li>
                  ))}
                </ol>
              </div>

              <div>
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Model attribution
                </h3>
                {riskQuery.isPending ? (
                  <LoadingState label="Scoring transaction" rows={2} />
                ) : riskQuery.isError || !riskQuery.data ? (
                  <ErrorState
                    message="Risk assessment unavailable."
                    onRetry={() => void riskQuery.refetch()}
                  />
                ) : (
                  <ul className="space-y-2">
                    {riskQuery.data.explanations.map((ex) => (
                      <li key={ex.feature}>
                        <div className="flex items-center justify-between text-xs">
                          <span className="tabular text-foreground">{ex.feature}</span>
                          <span className="tabular text-muted-foreground">
                            {ex.contribution.toFixed(3)}
                          </span>
                        </div>
                        <div className="mt-1 h-1.5 rounded-full bg-surface-2">
                          <div
                            className="h-full rounded-full bg-primary"
                            style={{ width: `${Math.min(100, ex.contribution * 300)}%` }}
                          />
                        </div>
                        <p className="mt-1 text-[11px] text-muted-foreground">{ex.note}</p>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="flex flex-wrap gap-2">
                <Button asChild size="sm" variant="outline">
                  <Link to="/graph">View in graph</Link>
                </Button>
                <Button asChild size="sm" variant="outline">
                  <Link to="/risk">Open risk analysis</Link>
                </Button>
                <Button asChild size="sm">
                  <Link to="/simulation">Run crash test</Link>
                </Button>
              </div>
            </>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
