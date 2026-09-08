import { useMutation, useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { CheckCircle2, CircleDot, Play, RotateCcw, Zap } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  Panel,
  RiskBadge,
} from "@/components/vfsim/primitives";
import { TransactionPicker } from "@/components/vfsim/TransactionPicker";
import { useSelection } from "@/components/vfsim/selection";
import { api } from "@/services/api";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/simulation")({
  head: () => ({
    meta: [
      { title: "Crash Lab — VFSim" },
      {
        name: "description",
        content:
          "Interactive transaction, crash injection and journal recovery walkthrough for the VFSim filesystem simulator.",
      },
      { property: "og:title", content: "VFSim Crash Lab" },
      {
        property: "og:description",
        content: "Run a transaction, inject a crash, and watch journal recovery step through.",
      },
    ],
  }),
  component: SimulationPage,
});

type Phase = "idle" | "running" | "crashed" | "recovering" | "recovered";

function SimulationPage() {
  const { selectedTxId } = useSelection();
  const [phase, setPhase] = useState<Phase>("idle");
  const [cursor, setCursor] = useState(0);
  const [scenarioId, setScenarioId] = useState("crash-power");
  const [recoveryStep, setRecoveryStep] = useState(0);

  const tx = useQuery({
    queryKey: ["transaction", selectedTxId],
    queryFn: () => api.getTransaction(selectedTxId),
  });
  const scenarios = useQuery({
    queryKey: ["crash-scenarios"],
    queryFn: () => api.getCrashScenarios(),
  });

  const crash = useMutation({
    mutationFn: () => api.simulateCrash(selectedTxId, scenarioId),
    onSuccess: (res) => {
      setPhase("crashed");
      setCursor(res.survivedOps);
      toast.error(`Crash injected — ${res.lostOps} operation(s) lost`);
    },
    onError: () => toast.error("Crash simulation failed"),
  });

  const reset = () => {
    setPhase("idle");
    setCursor(0);
    setRecoveryStep(0);
    crash.reset();
  };

  const runTransaction = async () => {
    if (!tx.data) return;
    setPhase("running");
    setRecoveryStep(0);
    for (let i = 1; i <= tx.data.operations.length; i++) {
      await new Promise((r) => setTimeout(r, 420));
      setCursor(i);
    }
    setPhase("recovered");
    toast.success("Transaction committed cleanly");
  };

  const recover = async () => {
    const steps = crash.data?.recoverySteps ?? [];
    setPhase("recovering");
    for (let i = 1; i <= steps.length; i++) {
      await new Promise((r) => setTimeout(r, 520));
      setRecoveryStep(i);
    }
    setPhase("recovered");
    toast.success("Journal replay complete — filesystem consistent");
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Crash lab"
        description="Step a transaction through the simulator, inject a crash at a chosen point, then replay the journal and watch the recovery sequence."
        actions={<TransactionPicker />}
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <Panel title="Transaction timeline" subtitle={selectedTxId} icon={Play}>
          {tx.isPending ? (
            <LoadingState label="Loading transaction" rows={4} />
          ) : tx.isError || !tx.data ? (
            <ErrorState onRetry={() => void tx.refetch()} />
          ) : (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-2">
                <Button
                  size="sm"
                  onClick={() => void runTransaction()}
                  disabled={phase === "running" || phase === "recovering"}
                >
                  <Play className="size-4" aria-hidden /> Run transaction
                </Button>
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={() => crash.mutate()}
                  disabled={crash.isPending || phase === "recovering"}
                >
                  <Zap className="size-4" aria-hidden />
                  {crash.isPending ? "Injecting…" : "Inject crash"}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => void recover()}
                  disabled={phase !== "crashed"}
                >
                  <RotateCcw className="size-4" aria-hidden /> Recover
                </Button>
                <Button size="sm" variant="ghost" onClick={reset}>
                  Reset
                </Button>
                <RiskBadge level={tx.data.riskLevel} score={tx.data.riskScore} />
              </div>

              <ol className="space-y-2">
                {tx.data.operations.map((op) => {
                  const done = op.seq <= cursor;
                  const lost = phase === "crashed" && op.seq > cursor;
                  return (
                    <li
                      key={op.id}
                      className={cn(
                        "flex items-start gap-3 rounded-md border px-3 py-2 transition-colors",
                        lost
                          ? "border-critical/50 bg-critical/10"
                          : done
                            ? "border-safe/40 bg-safe/5"
                            : "border-border",
                      )}
                    >
                      {done && !lost ? (
                        <CheckCircle2 className="mt-0.5 size-4 text-safe" aria-hidden />
                      ) : (
                        <CircleDot
                          className={cn(
                            "mt-0.5 size-4",
                            lost ? "text-critical" : "text-muted-foreground",
                          )}
                          aria-hidden
                        />
                      )}
                      <div className="min-w-0">
                        <p className="tabular text-xs text-foreground">
                          #{op.seq} {op.op} · {op.journaled ? "journaled" : "unjournaled"}
                        </p>
                        <p className="tabular truncate text-[11px] text-muted-foreground">
                          {op.target}
                        </p>
                      </div>
                      {lost ? (
                        <span className="ml-auto rounded-sm bg-critical px-1.5 py-0.5 text-[10px] font-bold uppercase text-destructive-foreground">
                          lost
                        </span>
                      ) : null}
                    </li>
                  );
                })}
              </ol>
            </div>
          )}
        </Panel>

        <div className="space-y-4">
          <Panel title="Crash scenario" icon={Zap}>
            {scenarios.isPending ? (
              <LoadingState label="Loading scenarios" rows={3} />
            ) : scenarios.isError || !scenarios.data ? (
              <ErrorState onRetry={() => void scenarios.refetch()} />
            ) : (
              <ul className="space-y-2">
                {scenarios.data.map((s) => (
                  <li key={s.id}>
                    <button
                      type="button"
                      onClick={() => setScenarioId(s.id)}
                      className={cn(
                        "w-full rounded-md border px-3 py-2 text-left transition-colors",
                        s.id === scenarioId
                          ? "border-primary/60 bg-primary/10"
                          : "border-border hover:bg-surface-2",
                      )}
                    >
                      <p className="text-sm text-foreground">{s.name}</p>
                      <p className="text-[11px] text-muted-foreground">{s.description}</p>
                      <p className="mt-1 text-[11px] text-critical">{s.expectedLoss}</p>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </Panel>

          <Panel title="Recovery log" subtitle="journal replay">
            {!crash.data ? (
              <EmptyState
                title="No crash injected"
                hint="Inject a crash to generate a recovery plan from the journal."
              />
            ) : (
              <>
                <ol className="space-y-2">
                  {crash.data.recoverySteps.map((step, i) => (
                    <li
                      key={step}
                      className={cn(
                        "tabular rounded-md border px-3 py-2 text-[11px] transition-colors",
                        i < recoveryStep
                          ? "border-safe/40 bg-safe/10 text-safe"
                          : "border-border text-muted-foreground",
                      )}
                    >
                      {i + 1}. {step}
                    </li>
                  ))}
                </ol>
                <p className="mt-3 text-xs text-muted-foreground">
                  Post-recovery risk:{" "}
                  <span className="tabular text-safe">
                    {crash.data.postRecoveryRisk.toFixed(2)}
                  </span>{" "}
                  · {crash.data.survivedOps} durable / {crash.data.lostOps} lost
                </p>
              </>
            )}
          </Panel>
        </div>
      </div>
    </div>
  );
}
