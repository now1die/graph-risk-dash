import { Link } from "@tanstack/react-router";
import {
  Activity,
  BrainCircuit,
  GitBranch,
  LayoutDashboard,
  ListTree,
  Settings,
  ShieldAlert,
  Zap,
} from "lucide-react";
import type { ReactNode } from "react";

import { BackendStatusBadge, DemoBanner } from "@/components/vfsim/BackendStatus";
import { useSelection } from "@/components/vfsim/selection";

const nav = [
  { to: "/", label: "Overview", icon: LayoutDashboard, exact: true },
  { to: "/graph", label: "Graph Explorer", icon: GitBranch },
  { to: "/transactions", label: "Transactions", icon: ListTree },
  { to: "/risk", label: "Risk Analysis", icon: ShieldAlert },
  { to: "/simulation", label: "Crash Lab", icon: Zap },
  { to: "/model", label: "GNN Model", icon: BrainCircuit },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  const { selectedTxId } = useSelection();

  return (
    <div className="min-h-screen bg-background">
      <div className="flex min-h-screen">
        <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-sidebar-border bg-sidebar lg:flex">
          <div className="flex items-center gap-2.5 border-b border-sidebar-border px-4 py-4">
            <span className="grid size-8 place-items-center rounded-md bg-primary/15 text-primary">
              <Activity className="size-4" aria-hidden />
            </span>
            <div>
              <p className="text-sm font-semibold text-sidebar-foreground">VFSim</p>
              <p className="text-[11px] text-muted-foreground">Risk-aware FS simulator</p>
            </div>
          </div>
          <nav className="flex-1 space-y-1 p-3">
            {nav.map(({ to, label, icon: Icon, ...rest }) => (
              <Link
                key={to}
                to={to}
                activeOptions={{ exact: "exact" in rest ? rest.exact : false }}
                className="flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground data-[status=active]:bg-sidebar-accent data-[status=active]:text-sidebar-primary"
              >
                <Icon className="size-4" aria-hidden />
                {label}
              </Link>
            ))}
          </nav>
          <div className="border-t border-sidebar-border p-3 text-[11px] text-muted-foreground">
            <p className="uppercase tracking-wider">Active transaction</p>
            <p className="tabular mt-1 text-sm text-primary">{selectedTxId}</p>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-20 border-b border-border bg-background/85 backdrop-blur">
            <div className="flex items-center justify-between gap-4 px-4 py-3">
              <div className="flex items-center gap-2 overflow-x-auto lg:hidden">
                {nav.map(({ to, label, icon: Icon }) => (
                  <Link
                    key={to}
                    to={to}
                    className="flex items-center gap-1.5 whitespace-nowrap rounded-md border border-border px-2 py-1 text-xs text-muted-foreground data-[status=active]:border-primary/50 data-[status=active]:text-primary"
                  >
                    <Icon className="size-3.5" aria-hidden />
                    {label}
                  </Link>
                ))}
              </div>
              <p className="hidden text-xs text-muted-foreground lg:block">
                Graph-based risk-aware filesystem simulator · frontend research console
              </p>
              <BackendStatusBadge />
            </div>
            <DemoBanner />
          </header>
          <main className="flex-1 space-y-6 p-4 md:p-6">{children}</main>
          <footer className="border-t border-border px-4 py-3 text-[11px] text-muted-foreground md:px-6">
            VFSim frontend · all simulation, journaling and GNN inference run in the Python
            backend; this UI only renders results.
          </footer>
        </div>
      </div>
    </div>
  );
}
