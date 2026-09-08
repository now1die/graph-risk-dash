import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { Gauge, LineChart as LineChartIcon, ShieldAlert, ShieldCheck } from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Slider } from "@/components/ui/slider";
import {
  ErrorState,
  LoadingState,
  PageHeader,
  Panel,
  RiskBadge,
} from "@/components/vfsim/primitives";
import { RiskGauge } from "@/components/vfsim/RiskGauge";
import { TransactionPicker } from "@/components/vfsim/TransactionPicker";
import { useSelection } from "@/components/vfsim/selection";
import { api } from "@/services/api";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/risk")({
  head: () => ({
    meta: [
      { title: "Risk Analysis — VFSim" },
      {
        name: "description",
        content:
          "GNN risk gauge, feature attribution and journaling decision for the selected filesystem transaction, tuned by a risk threshold.",
      },
      { property: "og:title", content: "VFSim Risk Analysis" },
      {
        property: "og:description",
        content: "Risk gauge, attribution and journaling decision per transaction.",
      },
    ],
  }),
  component: RiskPage,
});

function RiskPage() {
  const { selectedTxId, riskThreshold, setRiskThreshold } = useSelection();
  const history = useQuery({ queryKey: ["risk-history"], queryFn: () => api.getRiskHistory() });
  const tx = useQuery({
    queryKey: ["transaction", selectedTxId],
    queryFn: () => api.getTransaction(selectedTxId),
  });
  const assessment = useQuery({
    queryKey: ["risk", selectedTxId],
    queryFn: () => api.getRiskAssessment(selectedTxId),
  });

  const score = assessment.data?.score ?? 0;
  const shouldJournal = score >= riskThreshold;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Risk analysis"
        description="The GNN scores each transaction before it commits. Above the threshold, the simulator forces full journaling and an extra flush; below it, the fast path is taken."
        actions={<TransactionPicker />}
      />

      <div className="grid gap-4 xl:grid-cols-[320px_minmax(0,1fr)]">
        <div className="space-y-4">
          <Panel title="Risk gauge" subtitle={selectedTxId} icon={Gauge}>
            {assessment.isPending ? (
              <LoadingState label="Scoring transaction" rows={2} />
            ) : assessment.isError ? (
              <ErrorState onRetry={() => void assessment.refetch()} />
            ) : (
              <div className="space-y-4">
                <RiskGauge score={score} threshold={riskThreshold} />
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>model confidence</span>
                  <span className="tabular text-foreground">
                    {((assessment.data?.confidence ?? 0) * 100).toFixed(1)}%
                  </span>
                </div>
                {tx.data ? (
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{tx.data.label}</span>
                    <RiskBadge level={tx.data.riskLevel} />
                  </div>
                ) : null}
              </div>
            )}
          </Panel>

          <Panel title="Risk threshold" subtitle="journaling policy control">
            <Slider
              value={[riskThreshold]}
              min={0}
              max={1}
              step={0.01}
              onValueChange={([v]) => setRiskThreshold(v ?? 0)}
              aria-label="Risk threshold"
            />
            <div className="mt-2 flex justify-between text-[11px] text-muted-foreground">
              <span>0.00 fast path</span>
              <span className="tabular text-primary">{riskThreshold.toFixed(2)}</span>
              <span>1.00 always journal</span>
            </div>

            <div
              className={cn(
                "mt-4 rounded-md border p-3",
                shouldJournal
                  ? "border-critical/50 bg-critical/10"
                  : "border-safe/40 bg-safe/10",
              )}
            >
              <p
                className={cn(
                  "flex items-center gap-2 text-sm font-semibold",
                  shouldJournal ? "text-critical" : "text-safe",
                )}
              >
                {shouldJournal ? (
                  <ShieldAlert className="size-4" aria-hidden />
                ) : (
                  <ShieldCheck className="size-4" aria-hidden />
                )}
                {shouldJournal ? "Force full journaling" : "Fast path allowed"}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                {shouldJournal
                  ? `Risk ${score.toFixed(2)} ≥ threshold ${riskThreshold.toFixed(2)} — every write is journaled and an fsync barrier is inserted before commit.`
                  : `Risk ${score.toFixed(2)} < threshold ${riskThreshold.toFixed(2)} — metadata-only journaling; data writes may be reordered by the device.`}
              </p>
            </div>
          </Panel>
        </div>

        <div className="space-y-4">
          <Panel title="Risk history" subtitle="predicted vs observed, 24h" icon={LineChartIcon}>
            {history.isPending ? (
              <LoadingState label="Loading risk history" rows={3} />
            ) : history.isError || !history.data ? (
              <ErrorState onRetry={() => void history.refetch()} />
            ) : (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={history.data} margin={{ left: -20, right: 8, top: 8 }}>
                    <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                    <XAxis
                      dataKey="t"
                      stroke="var(--muted-foreground)"
                      fontSize={11}
                      tickLine={false}
                    />
                    <YAxis
                      domain={[0, 1]}
                      stroke="var(--muted-foreground)"
                      fontSize={11}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        background: "var(--popover)",
                        border: "1px solid var(--border)",
                        borderRadius: 8,
                        fontSize: 12,
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                    <ReferenceLine
                      y={riskThreshold}
                      stroke="var(--critical)"
                      strokeDasharray="5 4"
                      label={{
                        value: `threshold ${riskThreshold.toFixed(2)}`,
                        fill: "var(--critical)",
                        fontSize: 10,
                        position: "insideTopRight",
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="predicted"
                      stroke="var(--chart-1)"
                      strokeWidth={2}
                      dot={false}
                      name="GNN predicted"
                    />
                    <Line
                      type="monotone"
                      dataKey="observed"
                      stroke="var(--chart-3)"
                      strokeWidth={2}
                      strokeDasharray="4 3"
                      dot={false}
                      name="Observed"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </Panel>

          <Panel title="Why this score?" subtitle={`attribution for ${selectedTxId}`}>
            {assessment.isPending ? (
              <LoadingState label="Loading attribution" rows={3} />
            ) : assessment.isError || !assessment.data ? (
              <ErrorState onRetry={() => void assessment.refetch()} />
            ) : (
              <ul className="space-y-3">
                {assessment.data.explanations.map((ex) => (
                  <li key={ex.feature}>
                    <div className="flex items-center justify-between text-xs">
                      <span className="tabular text-foreground">{ex.feature}</span>
                      <span className="tabular text-muted-foreground">
                        +{ex.contribution.toFixed(3)}
                      </span>
                    </div>
                    <div className="mt-1 h-2 rounded-full bg-surface-2">
                      <div
                        className="h-full rounded-full bg-primary transition-all"
                        style={{ width: `${Math.min(100, ex.contribution * 300)}%` }}
                      />
                    </div>
                    <p className="mt-1 text-[11px] text-muted-foreground">{ex.note}</p>
                  </li>
                ))}
              </ul>
            )}
          </Panel>
        </div>
      </div>
    </div>
  );
}
