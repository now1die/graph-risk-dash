import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { GitBranch, Info } from "lucide-react";
import { useEffect, useState } from "react";

import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  Panel,
  RiskBadge,
} from "@/components/vfsim/primitives";
import { GraphExplorer } from "@/components/vfsim/GraphExplorer";
import { TransactionPicker } from "@/components/vfsim/TransactionPicker";
import { useSelection } from "@/components/vfsim/selection";
import { api, type FsNode } from "@/services/api";

export const Route = createFileRoute("/graph")({
  head: () => ({
    meta: [
      { title: "Graph Explorer — VFSim" },
      {
        name: "description",
        content:
          "Explore the simulated filesystem as a graph: directories, inodes and journal edges, with transaction-touched nodes highlighted.",
      },
      { property: "og:title", content: "VFSim Graph Explorer" },
      {
        property: "og:description",
        content: "Interactive filesystem graph with transaction-touched nodes highlighted.",
      },
    ],
  }),
  component: GraphPage,
});

function GraphPage() {
  const { selectedTxId } = useSelection();
  const [selectedNode, setSelectedNode] = useState<FsNode | null>(null);
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const graph = useQuery({
    queryKey: ["graph", selectedTxId],
    queryFn: () => api.getGraph(selectedTxId),
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Graph explorer"
        description="The simulator represents the filesystem as a typed graph. Nodes touched by the selected transaction are outlined in red and labelled TOUCHED."
        actions={<TransactionPicker />}
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <Panel
          title="Filesystem graph"
          subtitle={`transaction ${selectedTxId}`}
          icon={GitBranch}
          bodyClassName="p-2"
        >
          {!mounted || graph.isPending ? (
            <LoadingState label="Loading graph topology" rows={5} />
          ) : graph.isError || !graph.data ? (
            <ErrorState
              message="Graph could not be loaded from the simulation service."
              onRetry={() => void graph.refetch()}
            />
          ) : graph.data.nodes.length === 0 ? (
            <EmptyState title="Graph is empty" hint="No nodes returned for this transaction." />
          ) : (
            <GraphExplorer
              nodes={graph.data.nodes}
              edges={graph.data.edges}
              touched={graph.data.touched}
              selectedId={selectedNode?.id ?? null}
              onSelect={setSelectedNode}
            />
          )}
        </Panel>

        <div className="space-y-4">
          <Panel title="Node details" subtitle="click a node in the graph" icon={Info}>
            {!selectedNode ? (
              <EmptyState
                title="No node selected"
                hint="Select any node to inspect its metadata, risk score and embedding."
              />
            ) : (
              <dl className="space-y-3 text-sm">
                <div>
                  <dt className="text-[11px] uppercase tracking-wider text-muted-foreground">
                    Path
                  </dt>
                  <dd className="tabular break-all text-foreground">{selectedNode.path}</dd>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <dt className="text-[11px] uppercase tracking-wider text-muted-foreground">
                      Kind
                    </dt>
                    <dd className="text-foreground">{selectedNode.kind}</dd>
                  </div>
                  <div>
                    <dt className="text-[11px] uppercase tracking-wider text-muted-foreground">
                      Size
                    </dt>
                    <dd className="tabular text-foreground">{selectedNode.sizeKb} KiB</dd>
                  </div>
                  <div>
                    <dt className="text-[11px] uppercase tracking-wider text-muted-foreground">
                      Dirty
                    </dt>
                    <dd className="text-foreground">{selectedNode.dirty ? "yes" : "no"}</dd>
                  </div>
                  <div>
                    <dt className="text-[11px] uppercase tracking-wider text-muted-foreground">
                      Touched
                    </dt>
                    <dd className="text-foreground">
                      {graph.data?.touched.includes(selectedNode.id) ? "yes" : "no"}
                    </dd>
                  </div>
                </div>
                <div>
                  <dt className="text-[11px] uppercase tracking-wider text-muted-foreground">
                    Risk
                  </dt>
                  <dd className="mt-1">
                    <RiskBadge level={selectedNode.riskLevel} score={selectedNode.riskScore} />
                  </dd>
                </div>
                <div>
                  <dt className="text-[11px] uppercase tracking-wider text-muted-foreground">
                    Last write
                  </dt>
                  <dd className="tabular text-xs text-foreground">
                    {new Date(selectedNode.lastWrite).toISOString().replace("T", " ").slice(0, 19)}{" "}
                    UTC
                  </dd>
                </div>
                <div>
                  <dt className="text-[11px] uppercase tracking-wider text-muted-foreground">
                    Node embedding (8d)
                  </dt>
                  <dd className="mt-1 flex gap-1">
                    {selectedNode.embedding.map((v, i) => (
                      <span
                        key={i}
                        title={v.toFixed(3)}
                        className="h-8 flex-1 rounded-sm bg-primary/70"
                        style={{ opacity: 0.25 + v * 0.75 }}
                      />
                    ))}
                  </dd>
                </div>
              </dl>
            )}
          </Panel>

          <Panel title="Legend">
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li className="flex items-center gap-2">
                <span className="inline-block size-3 rounded-sm border border-critical bg-critical/20" />
                Touched by selected transaction
              </li>
              <li className="flex items-center gap-2">
                <span className="inline-block h-0.5 w-6 bg-primary" /> points-to (inode reference)
              </li>
              <li className="flex items-center gap-2">
                <span className="inline-block h-0.5 w-6 bg-watch" /> journals
              </li>
              <li className="flex items-center gap-2">
                <span className="inline-block h-0.5 w-6 bg-border" /> contains (directory tree)
              </li>
              <li className="flex items-center gap-2">
                <span className="inline-block h-0.5 w-6 border-t border-dashed border-chart-4" />
                hardlink
              </li>
            </ul>
          </Panel>
        </div>
      </div>
    </div>
  );
}
