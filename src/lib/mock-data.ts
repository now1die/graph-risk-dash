// Static mock dataset for VFSim. No filesystem or GNN logic runs here —
// these are pre-computed fixtures shaped like future FastAPI responses.

export type RiskLevel = "safe" | "watch" | "elevated" | "critical";

export interface FsNode {
  id: string;
  name: string;
  path: string;
  kind: "directory" | "file" | "inode" | "journal" | "superblock";
  sizeKb: number;
  riskScore: number;
  riskLevel: RiskLevel;
  lastWrite: string;
  dirty: boolean;
  embedding: number[];
}

export interface FsEdge {
  id: string;
  source: string;
  target: string;
  relation: "contains" | "points-to" | "journals" | "hardlink";
  weight: number;
}

export interface TxOperation {
  id: string;
  seq: number;
  op: "create" | "write" | "rename" | "unlink" | "fsync" | "truncate";
  target: string;
  bytes: number;
  journaled: boolean;
  riskDelta: number;
}

export interface Transaction {
  id: string;
  label: string;
  status: "committed" | "in-flight" | "aborted" | "recovered";
  startedAt: string;
  durationMs: number;
  operations: TxOperation[];
  riskScore: number;
  riskLevel: RiskLevel;
}

export interface RiskPoint {
  t: string;
  predicted: number;
  observed: number;
  writeAmp: number;
}

export interface ModelInfo {
  name: string;
  architecture: string;
  version: string;
  layers: { name: string; type: string; units: number }[];
  metrics: { auc: number; precision: number; recall: number; f1: number };
  training: { epoch: number; loss: number; valLoss: number }[];
  featureImportance: { feature: string; weight: number }[];
  lastTrained: string;
  params: number;
}

export interface CrashScenario {
  id: string;
  name: string;
  description: string;
  injectAfterSeq: number;
  expectedLoss: string;
  recoverySteps: string[];
}

export const riskLevelFor = (score: number): RiskLevel =>
  score >= 0.75 ? "critical" : score >= 0.5 ? "elevated" : score >= 0.25 ? "watch" : "safe";

export const fsNodes: FsNode[] = [
  ["sb-0", "superblock", "/", "superblock", 4, 0.12],
  ["dir-root", "/", "/", "directory", 4, 0.08],
  ["dir-var", "var", "/var", "directory", 4, 0.31],
  ["dir-log", "log", "/var/log", "directory", 4, 0.58],
  ["dir-db", "db", "/var/db", "directory", 4, 0.81],
  ["dir-home", "home", "/home", "directory", 4, 0.18],
  ["dir-user", "nachiket", "/home/nachiket", "directory", 4, 0.22],
  ["file-syslog", "syslog", "/var/log/syslog", "file", 15320, 0.63],
  ["file-audit", "audit.log", "/var/log/audit.log", "file", 8104, 0.44],
  ["file-ledger", "ledger.sqlite", "/var/db/ledger.sqlite", "file", 204800, 0.88],
  ["file-wal", "ledger.sqlite-wal", "/var/db/ledger.sqlite-wal", "file", 51200, 0.92],
  ["file-notes", "notes.md", "/home/nachiket/notes.md", "file", 32, 0.05],
  ["file-thesis", "thesis.tex", "/home/nachiket/thesis.tex", "file", 890, 0.27],
  ["inode-402", "inode:402", "/var/db/ledger.sqlite", "inode", 1, 0.74],
  ["inode-511", "inode:511", "/var/log/syslog", "inode", 1, 0.39],
  ["journal-0", "journal", "/.journal", "journal", 65536, 0.69],
].map(([id, name, path, kind, sizeKb, riskScore], i) => ({
  id: id as string,
  name: name as string,
  path: path as string,
  kind: kind as FsNode["kind"],
  sizeKb: sizeKb as number,
  riskScore: riskScore as number,
  riskLevel: riskLevelFor(riskScore as number),
  lastWrite: new Date(Date.UTC(2026, 8, 8, 1, 12 + i * 3)).toISOString(),
  dirty: (riskScore as number) > 0.6,
  embedding: Array.from({ length: 8 }, (_, k) =>
    Number((Math.sin((i + 1) * (k + 1) * 0.7) * 0.5 + 0.5).toFixed(3)),
  ),
}));

export const fsEdges: FsEdge[] = [
  ["sb-0", "dir-root", "points-to", 1],
  ["dir-root", "dir-var", "contains", 0.9],
  ["dir-root", "dir-home", "contains", 0.9],
  ["dir-var", "dir-log", "contains", 0.8],
  ["dir-var", "dir-db", "contains", 0.95],
  ["dir-home", "dir-user", "contains", 0.6],
  ["dir-log", "file-syslog", "contains", 0.85],
  ["dir-log", "file-audit", "contains", 0.7],
  ["dir-db", "file-ledger", "contains", 0.99],
  ["dir-db", "file-wal", "contains", 0.97],
  ["dir-user", "file-notes", "contains", 0.3],
  ["dir-user", "file-thesis", "contains", 0.4],
  ["file-ledger", "inode-402", "points-to", 1],
  ["file-syslog", "inode-511", "points-to", 1],
  ["journal-0", "file-wal", "journals", 0.93],
  ["journal-0", "file-ledger", "journals", 0.88],
  ["file-wal", "file-ledger", "hardlink", 0.5],
].map(([source, target, relation, weight]) => ({
  id: `${source}->${target}`,
  source: source as string,
  target: target as string,
  relation: relation as FsEdge["relation"],
  weight: weight as number,
}));

const ops = (
  list: [TxOperation["op"], string, number, boolean, number][],
): TxOperation[] =>
  list.map(([op, target, bytes, journaled, riskDelta], i) => ({
    id: `op-${i}-${target}`,
    seq: i + 1,
    op,
    target,
    bytes,
    journaled,
    riskDelta,
  }));

export const transactions: Transaction[] = [
  {
    id: "tx-9f21",
    label: "ledger checkpoint",
    status: "in-flight",
    startedAt: "2026-09-08T02:04:11Z",
    durationMs: 1840,
    riskScore: 0.86,
    riskLevel: "critical",
    operations: ops([
      ["create", "/var/db/ledger.sqlite-wal", 0, true, 0.04],
      ["write", "/var/db/ledger.sqlite-wal", 4194304, true, 0.21],
      ["fsync", "/var/db/ledger.sqlite-wal", 0, true, -0.08],
      ["write", "/var/db/ledger.sqlite", 8388608, false, 0.42],
      ["rename", "/var/db/ledger.sqlite-wal", 0, true, 0.15],
      ["fsync", "/var/db/ledger.sqlite", 0, true, -0.12],
    ]),
  },
  {
    id: "tx-8c04",
    label: "log rotation",
    status: "committed",
    startedAt: "2026-09-08T01:58:02Z",
    durationMs: 420,
    riskScore: 0.31,
    riskLevel: "watch",
    operations: ops([
      ["rename", "/var/log/syslog", 0, true, 0.11],
      ["create", "/var/log/syslog", 0, true, 0.03],
      ["truncate", "/var/log/audit.log", 0, false, 0.17],
    ]),
  },
  {
    id: "tx-7b55",
    label: "thesis autosave",
    status: "committed",
    startedAt: "2026-09-08T01:44:37Z",
    durationMs: 96,
    riskScore: 0.09,
    riskLevel: "safe",
    operations: ops([
      ["write", "/home/nachiket/thesis.tex", 24576, true, 0.05],
      ["fsync", "/home/nachiket/thesis.tex", 0, true, -0.02],
    ]),
  },
  {
    id: "tx-6a12",
    label: "orphan cleanup",
    status: "aborted",
    startedAt: "2026-09-08T01:31:09Z",
    durationMs: 2110,
    riskScore: 0.67,
    riskLevel: "elevated",
    operations: ops([
      ["unlink", "/var/db/stale-000.tmp", 0, false, 0.33],
      ["unlink", "/var/db/stale-001.tmp", 0, false, 0.28],
    ]),
  },
  {
    id: "tx-5d80",
    label: "journal replay",
    status: "recovered",
    startedAt: "2026-09-08T01:12:55Z",
    durationMs: 3390,
    riskScore: 0.52,
    riskLevel: "elevated",
    operations: ops([
      ["write", "/.journal", 1048576, true, 0.19],
      ["fsync", "/.journal", 0, true, -0.06],
      ["write", "/var/db/ledger.sqlite", 2097152, true, 0.24],
    ]),
  },
];

export const riskSeries: RiskPoint[] = Array.from({ length: 24 }, (_, i) => {
  const predicted = Number((0.35 + 0.28 * Math.sin(i / 3) + (i > 17 ? 0.22 : 0)).toFixed(3));
  return {
    t: `${String(i).padStart(2, "0")}:00`,
    predicted: Math.max(0.02, Math.min(0.98, predicted)),
    observed: Math.max(0.02, Math.min(0.98, Number((predicted + Math.cos(i / 2) * 0.07).toFixed(3)))),
    writeAmp: Number((1.2 + Math.abs(Math.sin(i / 4)) * 2.4).toFixed(2)),
  };
});

export const modelInfo: ModelInfo = {
  name: "VFSim-GNN",
  architecture: "3-layer GraphSAGE + attention readout",
  version: "v0.7.2",
  params: 1_284_736,
  lastTrained: "2026-09-07T19:40:00Z",
  layers: [
    { name: "input", type: "NodeFeatureEncoder", units: 32 },
    { name: "sage_1", type: "SAGEConv", units: 128 },
    { name: "sage_2", type: "SAGEConv", units: 128 },
    { name: "sage_3", type: "SAGEConv", units: 64 },
    { name: "readout", type: "AttentionPool", units: 64 },
    { name: "head", type: "MLP → risk", units: 1 },
  ],
  metrics: { auc: 0.938, precision: 0.891, recall: 0.864, f1: 0.877 },
  training: Array.from({ length: 30 }, (_, i) => ({
    epoch: i + 1,
    loss: Number((0.92 * Math.exp(-i / 7) + 0.06).toFixed(4)),
    valLoss: Number((0.95 * Math.exp(-i / 6.2) + 0.09 + (i > 22 ? (i - 22) * 0.004 : 0)).toFixed(4)),
  })),
  featureImportance: [
    { feature: "unjournaled_write_bytes", weight: 0.27 },
    { feature: "fsync_gap_ms", weight: 0.21 },
    { feature: "inode_fanout", weight: 0.16 },
    { feature: "dirty_page_age", weight: 0.14 },
    { feature: "rename_depth", weight: 0.12 },
    { feature: "subtree_size", weight: 0.1 },
  ],
};

export const crashScenarios: CrashScenario[] = [
  {
    id: "crash-power",
    name: "Power loss",
    description: "Host loses power mid-transaction; page cache is discarded.",
    injectAfterSeq: 4,
    expectedLoss: "Unjournaled 8 MiB write to ledger.sqlite",
    recoverySteps: [
      "Mount detects unclean shutdown flag in superblock",
      "Scan /.journal for the last valid commit record",
      "Replay journaled ops up to tx-9f21 seq 3",
      "Roll back the unjournaled data write",
      "Rebuild inode:402 block map and clear dirty bits",
    ],
  },
  {
    id: "crash-kernel",
    name: "Kernel panic",
    description: "Kernel halts after rename but before the final fsync.",
    injectAfterSeq: 5,
    expectedLoss: "WAL rename visible without a durable data flush",
    recoverySteps: [
      "Detect dangling rename in journal tail",
      "Re-apply rename target metadata",
      "Force fsync of ledger.sqlite",
      "Verify checksum against journal commit record",
    ],
  },
  {
    id: "crash-disk",
    name: "Disk write error",
    description: "Storage device returns EIO on the WAL flush.",
    injectAfterSeq: 2,
    expectedLoss: "Entire transaction aborted, no partial state",
    recoverySteps: [
      "Abort transaction and mark WAL segment invalid",
      "Drop dirty pages for the failing extent",
      "Remount read-only pending fsck",
    ],
  },
];

export const systemStats = {
  nodes: fsNodes.length,
  edges: fsEdges.length,
  dirtyNodes: fsNodes.filter((n) => n.dirty).length,
  openTransactions: transactions.filter((t) => t.status === "in-flight").length,
  meanRisk: Number(
    (fsNodes.reduce((a, n) => a + n.riskScore, 0) / fsNodes.length).toFixed(3),
  ),
  journalUtilization: 0.62,
  simulatedUptimeHrs: 41.6,
  crashesSurvived: 12,
};
