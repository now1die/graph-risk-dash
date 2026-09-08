import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { Plug, Server } from "lucide-react";

import { PageHeader, Panel, ErrorState, LoadingState } from "@/components/vfsim/primitives";
import { BackendStatusBadge } from "@/components/vfsim/BackendStatus";
import { API_BASE_URL, BACKEND_MODE, ENDPOINTS, api } from "@/services/api";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Settings — VFSim" },
      {
        name: "description",
        content:
          "Backend connection status for VFSim and the FastAPI endpoint contract the frontend expects.",
      },
      { property: "og:title", content: "VFSim Settings" },
      {
        property: "og:description",
        content: "Backend connection status and the expected FastAPI endpoint contract.",
      },
    ],
  }),
  component: SettingsPage,
});

const endpointRows: [string, string][] = [
  ["GET", ENDPOINTS.health],
  ["GET", ENDPOINTS.stats],
  ["GET", ENDPOINTS.graph],
  ["GET", ENDPOINTS.transactionGraph("{tx_id}")],
  ["GET", ENDPOINTS.transactions],
  ["GET", ENDPOINTS.transaction("{tx_id}")],
  ["GET", ENDPOINTS.riskHistory],
  ["GET", ENDPOINTS.riskScore("{tx_id}")],
  ["GET", ENDPOINTS.model],
  ["GET", ENDPOINTS.crashScenarios],
  ["POST", ENDPOINTS.simulateCrash],
];

function SettingsPage() {
  const health = useQuery({ queryKey: ["health"], queryFn: () => api.getHealth() });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings"
        description="This build is frontend-only. All data flows through one API service module, so pointing it at the FastAPI simulator is a single environment variable."
        actions={<BackendStatusBadge />}
      />

      <Panel title="Backend connection" icon={Plug}>
        {health.isPending ? (
          <LoadingState label="Checking backend" rows={2} />
        ) : health.isError ? (
          <ErrorState
            message="Health check failed — the configured backend is unreachable."
            onRetry={() => void health.refetch()}
          />
        ) : (
          <dl className="grid gap-3 sm:grid-cols-3">
            <div>
              <dt className="text-[11px] uppercase tracking-wider text-muted-foreground">Mode</dt>
              <dd className="tabular text-sm text-foreground">{BACKEND_MODE}</dd>
            </div>
            <div>
              <dt className="text-[11px] uppercase tracking-wider text-muted-foreground">
                VITE_API_BASE_URL
              </dt>
              <dd className="tabular break-all text-sm text-foreground">
                {API_BASE_URL || "not set — bundled fixtures in use"}
              </dd>
            </div>
            <div>
              <dt className="text-[11px] uppercase tracking-wider text-muted-foreground">
                Checked
              </dt>
              <dd className="tabular text-sm text-foreground">
                {health.data?.checkedAt.slice(11, 19)} UTC
              </dd>
            </div>
          </dl>
        )}
      </Panel>

      <Panel title="Expected FastAPI contract" subtitle="one call site per endpoint" icon={Server}>
        <ul className="space-y-1.5">
          {endpointRows.map(([method, path]) => (
            <li
              key={path}
              className="flex items-center gap-3 rounded-md border border-border px-3 py-2 text-xs"
            >
              <span className="tabular w-12 shrink-0 text-primary">{method}</span>
              <span className="tabular break-all text-foreground">{path}</span>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-[11px] text-muted-foreground">
          Simulation, journaling and GNN inference stay server-side; the frontend never implements
          filesystem or model logic.
        </p>
      </Panel>
    </div>
  );
}
