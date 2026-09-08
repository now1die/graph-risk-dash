import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { BrainCircuit, Layers } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  ErrorState,
  LoadingState,
  PageHeader,
  Panel,
  StatCard,
} from "@/components/vfsim/primitives";
import { api } from "@/services/api";

export const Route = createFileRoute("/model")({
  head: () => ({
    meta: [
      { title: "GNN Model — VFSim" },
      {
        name: "description",
        content:
          "Architecture, training curves, metrics and feature importance for the VFSim graph neural network risk model.",
      },
      { property: "og:title", content: "VFSim GNN Model" },
      {
        property: "og:description",
        content: "Architecture, training curves and feature importance of the risk model.",
      },
    ],
  }),
  component: ModelPage,
});

function ModelPage() {
  const model = useQuery({ queryKey: ["model"], queryFn: () => api.getModel() });

  return (
    <div className="space-y-6">
      <PageHeader
        title="GNN risk model"
        description="Inference runs entirely in the Python backend. This page reports the served checkpoint's architecture and evaluation results."
      />

      {model.isPending ? (
        <LoadingState label="Loading model card" rows={4} />
      ) : model.isError || !model.data ? (
        <ErrorState onRetry={() => void model.refetch()} />
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="AUC" value={model.data.metrics.auc.toFixed(3)} tone="safe" />
            <StatCard label="Precision" value={model.data.metrics.precision.toFixed(3)} />
            <StatCard label="Recall" value={model.data.metrics.recall.toFixed(3)} />
            <StatCard label="F1" value={model.data.metrics.f1.toFixed(3)} />
          </div>

          <div className="grid gap-4 xl:grid-cols-3">
            <Panel
              title="Training curves"
              subtitle={`${model.data.version} · ${model.data.params.toLocaleString()} params`}
              icon={BrainCircuit}
              className="xl:col-span-2"
            >
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={model.data.training} margin={{ left: -20, right: 8, top: 8 }}>
                    <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                    <XAxis
                      dataKey="epoch"
                      stroke="var(--muted-foreground)"
                      fontSize={11}
                      tickLine={false}
                    />
                    <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        background: "var(--popover)",
                        border: "1px solid var(--border)",
                        borderRadius: 8,
                        fontSize: 12,
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                    <Line
                      type="monotone"
                      dataKey="loss"
                      stroke="var(--chart-1)"
                      strokeWidth={2}
                      dot={false}
                      name="train loss"
                    />
                    <Line
                      type="monotone"
                      dataKey="valLoss"
                      stroke="var(--chart-5)"
                      strokeWidth={2}
                      dot={false}
                      name="val loss"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Panel>

            <Panel title="Architecture" subtitle={model.data.architecture} icon={Layers}>
              <ol className="space-y-2">
                {model.data.layers.map((l) => (
                  <li
                    key={l.name}
                    className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-xs"
                  >
                    <span className="tabular text-foreground">{l.name}</span>
                    <span className="text-muted-foreground">{l.type}</span>
                    <span className="tabular text-primary">{l.units}</span>
                  </li>
                ))}
              </ol>
              <p className="mt-3 text-[11px] text-muted-foreground">
                Last trained{" "}
                {new Date(model.data.lastTrained).toISOString().replace("T", " ").slice(0, 16)} UTC
              </p>
            </Panel>
          </div>

          <Panel title="Feature importance" subtitle="permutation importance on the eval split">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={model.data.featureImportance}
                  layout="vertical"
                  margin={{ left: 90, right: 16 }}
                >
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" stroke="var(--muted-foreground)" fontSize={11} />
                  <YAxis
                    type="category"
                    dataKey="feature"
                    stroke="var(--muted-foreground)"
                    fontSize={10}
                    width={140}
                  />
                  <Tooltip
                    cursor={{ fill: "var(--surface-2)" }}
                    contentStyle={{
                      background: "var(--popover)",
                      border: "1px solid var(--border)",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="weight" fill="var(--chart-1)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Panel>
        </>
      )}
    </div>
  );
}
