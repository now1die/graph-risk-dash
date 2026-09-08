import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

interface SelectionValue {
  selectedTxId: string;
  setSelectedTxId: (id: string) => void;
  riskThreshold: number;
  setRiskThreshold: (v: number) => void;
}

const SelectionContext = createContext<SelectionValue | null>(null);

export function SelectionProvider({ children }: { children: ReactNode }) {
  const [selectedTxId, setSelectedTxId] = useState("tx-9f21");
  const [riskThreshold, setRiskThreshold] = useState(0.6);
  const value = useMemo(
    () => ({ selectedTxId, setSelectedTxId, riskThreshold, setRiskThreshold }),
    [selectedTxId, riskThreshold],
  );
  return <SelectionContext.Provider value={value}>{children}</SelectionContext.Provider>;
}

export function useSelection() {
  const ctx = useContext(SelectionContext);
  if (!ctx) throw new Error("useSelection must be used inside SelectionProvider");
  return ctx;
}
