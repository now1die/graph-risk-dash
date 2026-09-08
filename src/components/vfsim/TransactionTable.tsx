import { ChevronRight } from "lucide-react";

import { cn } from "@/lib/utils";
import { RiskBadge } from "@/components/vfsim/primitives";
import type { Transaction } from "@/services/api";

const statusStyles: Record<Transaction["status"], string> = {
  committed: "border-safe/40 bg-safe/10 text-safe",
  "in-flight": "border-primary/40 bg-primary/10 text-primary",
  aborted: "border-critical/40 bg-critical/10 text-critical",
  recovered: "border-watch/40 bg-watch/10 text-watch",
};

export function TransactionTable({
  transactions,
  selectedId,
  onSelect,
}: {
  transactions: Transaction[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[720px] text-sm">
        <thead>
          <tr className="border-b border-border text-left text-[11px] uppercase tracking-wider text-muted-foreground">
            <th className="px-3 py-2 font-medium">Transaction</th>
            <th className="px-3 py-2 font-medium">Status</th>
            <th className="px-3 py-2 font-medium">Ops</th>
            <th className="px-3 py-2 font-medium">Duration</th>
            <th className="px-3 py-2 font-medium">Started</th>
            <th className="px-3 py-2 font-medium">Risk</th>
            <th className="w-8 px-3 py-2" />
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => {
            const active = tx.id === selectedId;
            return (
              <tr
                key={tx.id}
                tabIndex={0}
                role="button"
                aria-pressed={active}
                onClick={() => onSelect(tx.id)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onSelect(tx.id);
                  }
                }}
                className={cn(
                  "cursor-pointer border-b border-border/70 transition-colors hover:bg-surface-2 focus:outline-none focus-visible:ring-1 focus-visible:ring-ring",
                  active && "bg-primary/10",
                )}
              >
                <td className="px-3 py-2.5">
                  <p className="tabular text-foreground">{tx.id}</p>
                  <p className="text-xs text-muted-foreground">{tx.label}</p>
                </td>
                <td className="px-3 py-2.5">
                  <span
                    className={cn(
                      "rounded-full border px-2 py-0.5 text-[11px] font-medium",
                      statusStyles[tx.status],
                    )}
                  >
                    {tx.status}
                  </span>
                </td>
                <td className="tabular px-3 py-2.5 text-muted-foreground">
                  {tx.operations.length}
                </td>
                <td className="tabular px-3 py-2.5 text-muted-foreground">{tx.durationMs} ms</td>
                <td className="tabular px-3 py-2.5 text-xs text-muted-foreground">
                  {new Date(tx.startedAt).toISOString().slice(11, 19)} UTC
                </td>
                <td className="px-3 py-2.5">
                  <RiskBadge level={tx.riskLevel} score={tx.riskScore} />
                </td>
                <td className="px-3 py-2.5 text-muted-foreground">
                  <ChevronRight className="size-4" aria-hidden />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
