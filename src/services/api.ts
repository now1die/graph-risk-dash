/**
 * Centralized VFSim API service.
 *
 * Every function maps 1:1 to a planned FastAPI endpoint. When
 * VITE_API_BASE_URL is set the client hits the real backend (LIVE);
 * otherwise it resolves the bundled fixtures (DEMO). No filesystem or
 * GNN logic is implemented on the client — mocks are static fixtures.
 */
import {
  crashScenarios,
  fsEdges,
  fsNodes,
  modelInfo,
  riskSeries,
  systemStats,
  transactions,
  type CrashScenario,
  type FsEdge,
  type FsNode,
  type ModelInfo,
  type RiskPoint,
  type Transaction,
} from "@/lib/mock-data";

export const API_BASE_URL: string = import.meta.env["VITE_API_BASE_URL"] ?? "";
export const IS_LIVE = API_BASE_URL.trim().length > 0;
export const BACKEND_MODE: "LIVE" | "DEMO" = IS_LIVE ? "LIVE" : "DEMO";

export const ENDPOINTS = {
  health: "/api/health",
  stats: "/api/stats",
  graph: "/api/graph",
  transactionGraph: (id: string) => `/api/transactions/${id}/graph`,
  transactions: "/api/transactions",
  transaction: (id: string) => `/api/transactions/${id}`,
  riskHistory: "/api/risk/history",
  riskScore: (id: string) => `/api/risk/${id}`,
  model: "/api/model",
  crashScenarios: "/api/crash/scenarios",
  simulateCrash: "/api/crash/simulate",
} as const;

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function request<T>(path: string, mock: () => T, init?: RequestInit): Promise<T> {
  if (!IS_LIVE) {
    await delay(220 + Math.random() * 350);
    return structuredClone(mock());
  }
  const res = await fetch(`${API_BASE_URL.replace(/\/$/, "")}${path}`, {
    headers: { "content-type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new ApiError(`Request to ${path} failed`, res.status);
  return (await res.json()) as T;
}

export interface GraphPayload {
  nodes: FsNode[];
  edges: FsEdge[];
  touched: string[];
  transactionId: string | null;
}

export interface RiskAssessment {
  transactionId: string;
  score: number;
  confidence: number;
  explanations: { feature: string; contribution: number; note: string }[];
}

export interface CrashResult {
  scenarioId: string;
  transactionId: string;
  survivedOps: number;
  lostOps: number;
  recoverySteps: string[];
  postRecoveryRisk: number;
}

// Maps transaction operation targets onto graph node ids.
const pathToNodeId = new Map(
  fsNodes.filter((n) => n.kind === "file" || n.kind === "journal").map((n) => [n.path, n.id]),
);

function touchedNodesFor(txId: string): string[] {
  const tx = transactions.find((t) => t.id === txId);
  if (!tx) return [];
  const ids = new Set<string>();
  for (const op of tx.operations) {
    const direct = pathToNodeId.get(op.target);
    if (direct) {
      ids.add(direct);
      // Journaled ops also touch the journal node and the owning directory.
      if (op.journaled) ids.add("journal-0");
      const parent = fsNodes.find(
        (n) => n.kind === "directory" && op.target.startsWith(`${n.path}/`),
      );
      if (parent) ids.add(parent.id);
    }
  }
  if (tx.operations.some((o) => o.target.includes("ledger"))) ids.add("inode-402");
  if (tx.operations.some((o) => o.target.includes("syslog"))) ids.add("inode-511");
  return [...ids];
}

export const api = {
  getHealth: () =>
    request(ENDPOINTS.health, () => ({
      status: "ok" as const,
      mode: BACKEND_MODE,
      version: "0.7.2",
      checkedAt: new Date().toISOString(),
    })),

  getStats: () => request(ENDPOINTS.stats, () => systemStats),

  getGraph: (transactionId?: string): Promise<GraphPayload> =>
    request(
      transactionId ? ENDPOINTS.transactionGraph(transactionId) : ENDPOINTS.graph,
      () => ({
        nodes: fsNodes,
        edges: fsEdges,
        touched: transactionId ? touchedNodesFor(transactionId) : [],
        transactionId: transactionId ?? null,
      }),
    ),

  getTransactions: (): Promise<Transaction[]> =>
    request(ENDPOINTS.transactions, () => transactions),

  getTransaction: (id: string): Promise<Transaction> =>
    request(ENDPOINTS.transaction(id), () => {
      const tx = transactions.find((t) => t.id === id);
      if (!tx) throw new ApiError(`Transaction ${id} not found`, 404);
      return tx;
    }),

  getRiskHistory: (): Promise<RiskPoint[]> => request(ENDPOINTS.riskHistory, () => riskSeries),

  getRiskAssessment: (id: string): Promise<RiskAssessment> =>
    request(ENDPOINTS.riskScore(id), () => {
      const tx = transactions.find((t) => t.id === id);
      if (!tx) throw new ApiError(`Transaction ${id} not found`, 404);
      const unjournaled = tx.operations.filter((o) => !o.journaled).length;
      const bytes = tx.operations.reduce((a, o) => a + o.bytes, 0);
      return {
        transactionId: id,
        score: tx.riskScore,
        confidence: 0.82 + (tx.riskScore > 0.7 ? 0.11 : 0),
        explanations: [
          {
            feature: "unjournaled_write_bytes",
            contribution: Number((0.27 * (unjournaled ? 1 : 0.15)).toFixed(3)),
            note: `${unjournaled} operation(s) bypass the journal`,
          },
          {
            feature: "fsync_gap_ms",
            contribution: Number((0.21 * Math.min(1, tx.durationMs / 2000)).toFixed(3)),
            note: `${tx.durationMs} ms between first write and final flush`,
          },
          {
            feature: "payload_size",
            contribution: Number((0.16 * Math.min(1, bytes / 8_388_608)).toFixed(3)),
            note: `${(bytes / 1_048_576).toFixed(2)} MiB written in this transaction`,
          },
          {
            feature: "inode_fanout",
            contribution: Number((0.14 * Math.min(1, tx.operations.length / 6)).toFixed(3)),
            note: `${tx.operations.length} operations across shared inodes`,
          },
        ],
      };
    }),

  getModel: (): Promise<ModelInfo> => request(ENDPOINTS.model, () => modelInfo),

  getCrashScenarios: (): Promise<CrashScenario[]> =>
    request(ENDPOINTS.crashScenarios, () => crashScenarios),

  simulateCrash: (transactionId: string, scenarioId: string): Promise<CrashResult> =>
    request(
      ENDPOINTS.simulateCrash,
      () => {
        const tx = transactions.find((t) => t.id === transactionId);
        const scenario = crashScenarios.find((s) => s.id === scenarioId);
        if (!tx || !scenario) throw new ApiError("Unknown transaction or scenario", 404);
        const survived = Math.min(scenario.injectAfterSeq, tx.operations.length);
        return {
          scenarioId,
          transactionId,
          survivedOps: survived,
          lostOps: tx.operations.length - survived,
          recoverySteps: scenario.recoverySteps,
          postRecoveryRisk: Number(Math.max(0.04, tx.riskScore - 0.38).toFixed(2)),
        };
      },
      { method: "POST", body: JSON.stringify({ transactionId, scenarioId }) },
    ),
};

export type { Transaction, FsNode, FsEdge, RiskPoint, ModelInfo, CrashScenario };
