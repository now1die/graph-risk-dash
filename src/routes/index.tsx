import { useQuery } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Activity,
  AlertTriangle,
  GitBranch,
  Layers,
  ShieldAlert,
  Zap,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Button } from "@/components/ui/button";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  Panel,
  RiskBadge,
  StatCard,
} from "@/components/vfsim/primitives";
import { useSelection } from "@/components/vfsim/selection";
import { api } from "@/services/api";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "VFSim Overview — Risk-Aware Filesystem Simulator" },
      {
        name: "description",
        content:
          "Live overview of simulated filesystem health: graph size, dirty nodes, open transactions and GNN-predicted risk.",
      },
      { property: "og:title", content: "VFSim Overview" },
      {
        property: "og:description",
        content: "Graph size, dirty nodes, open transactions and GNN-predicted filesystem risk.",
      },
    ],
  }),
  component: Overview,
});

const chartAxis = { stroke: "var(--muted-foreground)", fontSize: 11 };

function Overview() {
  const { setSelectedTxId } = useSelection();
  const stats = useQuery({ queryKey: ["stats"], queryFn: () => api.getStats() });
  const risk = useQuery({ queryKey: ["risk-history"], queryFn: () => api.getRiskHistory() });
  const txs = useQuery({ queryKey: ["transactions"], queryFn: () => api.getTransactions() });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Simulation overview"
        description="Graph-based, risk-aware filesystem simulation. The backend models journaling and runs GNN inference; this console renders and explores the results."
        actions={
          <>
            <Button asChild variant="outline" size="sm">
              <Link to="/graph">
                <GitBranch className="size-4" aria-hidden /> Graph explorer
              </Link>
            </Button>
            <Button asChild size="sm">
              <Link to="/simulation">
                <Zap className="size-4" aria-hidden /> Run crash test
              </Link>
            </Button>
          </>
        }
      />

      {stats.isPending ? (
        <LoadingState label="Fetching simulator stats" rows={2} />
      ) : stats.isError || !stats.data ? (
        <ErrorState onRetry={() => void stats.refetch()} />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Graph size"
            value={`${stats.data.nodes}/${stats.data.edges}`}
            hint="nodes / edges in the FS graph"
            icon={Layers}
          />
          <StatCard
            label="Dirty nodes"
            value={stats.data.dirtyNodes}
            hint="unflushed pages awaiting fsync"
            icon={AlertTriangle}
            tone="watch"
          />
          <StatCard
            label="Open transactions"
            value={stats.data.openTransactions}
            hint="in-flight, not yet committed"
            icon={Activity}
          />
          <StatCard
            label="Mean predicted risk"
            value={stats.data.meanRisk.toFixed(3)}
            hint={`journal at ${(stats.data.journalUtilization * 100).toFixed(0)}% utilization`}
            icon={ShieldAlert}
            tone="critical"
          />
        </div>
      )}

      <div className="grid gap-4 xl:grid-cols-3">
        <Panel
          title="Predicted vs observed risk"
          subtitle="last 24 simulated hours"
          icon={ShieldAlert}
          className="xl:col-span-2"
        >
          {risk.isPending ? (
            <LoadingState label="Loading risk history" rows={3} />
          ) : risk.isError || !risk.data ? (
            <ErrorState onRetry={() => void risk.refetch()} />
          ) : risk.data.length === 0 ? (
            <EmptyState title="No risk samples recorded" />
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={risk.data} margin={{ left: -20, right: 8, top: 8 }}>
                  <defs>
                    <linearGradient id="pred" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.5} />
                      <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                  <XAxis dataKey="t" {...chartAxis} tickLine={false} />
                  <YAxis domain={[0, 1]} {...chartAxis} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      background: "var(--popover)",
                      border: "1px solid var(--border)",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Area
                    type="monotone"
                    dataKey="predicted"
                    stroke="var(--chart-1)"
                    fill="url(#pred)"
                    strokeWidth={2}
                    name="GNN predicted"
                  />
                  <Area
                    type="monotone"
                    dataKey="observed"
                    stroke="var(--chart-3)"
                    fill="transparent"
                    strokeWidth={2}
                    strokeDasharray="4 3"
                    name="Observed corruption"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </Panel>

        <Panel title="Recent transactions" subtitle="click to make active" icon={Activity}>
          {txs.isPending ? (
            <LoadingState label="Loading transactions" rows={4} />
          ) : txs.isError || !txs.data ? (
            <ErrorState onRetry={() => void txs.refetch()} />
          ) : txs.data.length === 0 ? (
            <EmptyState title="No transactions replayed yet" />
          ) : (
            <ul className="space-y-2">
              {txs.data.map((tx) => (
                <li key={tx.id}>
                  <Link
                    to="/transactions"
                    onClick={() => setSelectedTxId(tx.id)}
                    className="flex items-center justify-between gap-2 rounded-md border border-border px-3 py-2 transition-colors hover:border-primary/50 hover:bg-surface-2"
                  >
                    <span>
                      <span className="tabular block text-xs text-foreground">{tx.id}</span>
                      <span className="text-[11px] text-muted-foreground">{tx.label}</span>
                    </span>
                    <RiskBadge level={tx.riskLevel} score={tx.riskScore} />
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </Panel>
      </div>
    </div>
  );
}
