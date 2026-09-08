import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { ListTree } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  Panel,
} from "@/components/vfsim/primitives";
import { TransactionTable } from "@/components/vfsim/TransactionTable";
import { TransactionDetails } from "@/components/vfsim/TransactionDetails";
import { useSelection } from "@/components/vfsim/selection";
import { api } from "@/services/api";

export const Route = createFileRoute("/transactions")({
  head: () => ({
    meta: [
      { title: "Transactions — VFSim" },
      {
        name: "description",
        content:
          "Replayed filesystem transactions with journal coverage, duration and GNN risk scores, plus a per-transaction operation log.",
      },
      { property: "og:title", content: "VFSim Transactions" },
      {
        property: "og:description",
        content: "Filesystem transactions with journal coverage and GNN risk scores.",
      },
    ],
  }),
  component: TransactionsPage,
});

function TransactionsPage() {
  const { selectedTxId, setSelectedTxId } = useSelection();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const txs = useQuery({ queryKey: ["transactions"], queryFn: () => api.getTransactions() });

  const select = (id: string) => {
    setSelectedTxId(id);
    setDrawerOpen(true);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Transactions"
        description="Every replayed transaction from the simulator, scored by the GNN. Select a row to open the full operation log and risk attribution."
        actions={
          <Button size="sm" variant="outline" onClick={() => setDrawerOpen(true)}>
            Open details for {selectedTxId}
          </Button>
        }
      />

      <Panel
        title="Transaction log"
        subtitle={`${txs.data?.length ?? 0} transactions`}
        icon={ListTree}
        bodyClassName="p-0 sm:p-2"
      >
        {txs.isPending ? (
          <div className="p-4">
            <LoadingState label="Loading transactions" rows={5} />
          </div>
        ) : txs.isError || !txs.data ? (
          <div className="p-4">
            <ErrorState onRetry={() => void txs.refetch()} />
          </div>
        ) : txs.data.length === 0 ? (
          <div className="p-4">
            <EmptyState
              title="No transactions yet"
              hint="Run a workload in the simulator to populate this log."
            />
          </div>
        ) : (
          <TransactionTable
            transactions={txs.data}
            selectedId={selectedTxId}
            onSelect={select}
          />
        )}
      </Panel>

      <TransactionDetails
        transactionId={selectedTxId}
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
      />
    </div>
  );
}
