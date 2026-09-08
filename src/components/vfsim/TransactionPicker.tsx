import { useQuery } from "@tanstack/react-query";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api } from "@/services/api";
import { useSelection } from "@/components/vfsim/selection";

export function TransactionPicker() {
  const { selectedTxId, setSelectedTxId } = useSelection();
  const { data, isPending } = useQuery({
    queryKey: ["transactions"],
    queryFn: () => api.getTransactions(),
  });

  return (
    <Select value={selectedTxId} onValueChange={setSelectedTxId} disabled={isPending}>
      <SelectTrigger className="w-[260px] bg-card" aria-label="Selected transaction">
        <SelectValue placeholder={isPending ? "Loading transactions…" : "Select transaction"} />
      </SelectTrigger>
      <SelectContent>
        {(data ?? []).map((tx) => (
          <SelectItem key={tx.id} value={tx.id}>
            <span className="tabular">{tx.id}</span> · {tx.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
