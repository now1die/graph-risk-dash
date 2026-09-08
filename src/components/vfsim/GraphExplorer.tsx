import "@xyflow/react/dist/style.css";

import {
  Background,
  BackgroundVariant,
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import { Database, File, FileStack, Folder, HardDrive } from "lucide-react";
import { useMemo } from "react";

import { cn } from "@/lib/utils";
import type { FsEdge, FsNode } from "@/services/api";

type NodeData = {
  node: FsNode;
  touched: boolean;
  selected: boolean;
};

const kindIcon = {
  directory: Folder,
  file: File,
  inode: Database,
  journal: FileStack,
  superblock: HardDrive,
} as const;

const riskRing = {
  safe: "border-safe/50",
  watch: "border-watch/50",
  elevated: "border-elevated/60",
  critical: "border-critical/70",
} as const;

function FsFlowNode({ data }: NodeProps) {
  const { node, touched, selected } = data as unknown as NodeData;
  const Icon = kindIcon[node.kind];
  return (
    <div
      className={cn(
        "min-w-[168px] rounded-md border bg-card px-3 py-2 shadow-sm transition-colors",
        touched ? "border-critical bg-critical/15" : riskRing[node.riskLevel],
        selected && "ring-2 ring-primary",
      )}
    >
      <Handle type="target" position={Position.Top} className="!bg-border" />
      <div className="flex items-center gap-2">
        <Icon
          className={cn("size-3.5", touched ? "text-critical" : "text-primary")}
          aria-hidden
        />
        <span className="tabular truncate text-xs text-foreground">{node.name}</span>
        {touched ? (
          <span className="ml-auto rounded-sm bg-critical px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider text-destructive-foreground">
            Touched
          </span>
        ) : null}
      </div>
      <p className="mt-1 truncate text-[10px] text-muted-foreground">{node.path}</p>
      <div className="mt-1.5 flex items-center gap-1.5">
        <div className="h-1 flex-1 rounded-full bg-surface-2">
          <div
            className={cn("h-full rounded-full", touched ? "bg-critical" : "bg-primary")}
            style={{ width: `${node.riskScore * 100}%` }}
          />
        </div>
        <span className="tabular text-[10px] text-muted-foreground">
          {node.riskScore.toFixed(2)}
        </span>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-border" />
    </div>
  );
}

const nodeTypes = { fsNode: FsFlowNode };

const edgeColor: Record<FsEdge["relation"], string> = {
  contains: "var(--border)",
  "points-to": "var(--primary)",
  journals: "var(--watch)",
  hardlink: "var(--chart-4)",
};

// Deterministic layered layout derived from path depth — purely presentational.
function layout(nodes: FsNode[]) {
  const rows = new Map<number, FsNode[]>();
  for (const n of nodes) {
    const depth =
      n.kind === "superblock"
        ? 0
        : n.kind === "journal"
          ? 1
          : n.kind === "inode"
            ? 4
            : Math.min(3, n.path === "/" ? 1 : n.path.split("/").filter(Boolean).length + 1);
    rows.set(depth, [...(rows.get(depth) ?? []), n]);
  }
  const pos = new Map<string, { x: number; y: number }>();
  for (const [depth, group] of rows) {
    group.forEach((n, i) => {
      pos.set(n.id, { x: i * 230 - (group.length - 1) * 115, y: depth * 150 });
    });
  }
  return pos;
}

export function GraphExplorer({
  nodes,
  edges,
  touched,
  selectedId,
  onSelect,
}: {
  nodes: FsNode[];
  edges: FsEdge[];
  touched: string[];
  selectedId: string | null;
  onSelect: (node: FsNode) => void;
}) {
  const touchedSet = useMemo(() => new Set(touched), [touched]);

  const flowNodes: Node[] = useMemo(() => {
    const pos = layout(nodes);
    return nodes.map((n) => ({
      id: n.id,
      type: "fsNode",
      position: pos.get(n.id) ?? { x: 0, y: 0 },
      data: { node: n, touched: touchedSet.has(n.id), selected: n.id === selectedId },
    }));
  }, [nodes, touchedSet, selectedId]);

  const flowEdges: Edge[] = useMemo(
    () =>
      edges.map((e) => {
        const hot = touchedSet.has(e.source) && touchedSet.has(e.target);
        return {
          id: e.id,
          source: e.source,
          target: e.target,
          label: e.relation,
          animated: hot,
          labelStyle: { fill: "var(--muted-foreground)", fontSize: 9 },
          labelBgStyle: { fill: "var(--card)" },
          style: {
            stroke: hot ? "var(--critical)" : edgeColor[e.relation],
            strokeWidth: hot ? 2 : 1.2,
            strokeDasharray: e.relation === "hardlink" ? "4 3" : undefined,
          },
        };
      }),
    [edges, touchedSet],
  );

  return (
    <div className="h-[560px] w-full overflow-hidden rounded-md border border-border bg-background">
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        nodeTypes={nodeTypes}
        fitView
        proOptions={{ hideAttribution: true }}
        onNodeClick={(_, node) => onSelect((node.data as unknown as NodeData).node)}
        colorMode="dark"
      >
        <Background variant={BackgroundVariant.Dots} gap={22} color="var(--grid)" />
        <MiniMap
          pannable
          zoomable
          maskColor="color-mix(in oklab, var(--background) 80%, transparent)"
          nodeColor={(n) =>
            touchedSet.has(n.id) ? "var(--critical)" : "var(--primary)"
          }
          className="!bg-surface"
        />
        <Controls className="!border-border" />
      </ReactFlow>
    </div>
  );
}
