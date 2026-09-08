import { useQuery } from "@tanstack/react-query";
import { FlaskConical, Radio } from "lucide-react";

import { API_BASE_URL, BACKEND_MODE, api } from "@/services/api";
import { cn } from "@/lib/utils";

export function BackendStatusBadge({ className }: { className?: string }) {
  const { data, isError } = useQuery({
    queryKey: ["health"],
    queryFn: () => api.getHealth(),
    refetchInterval: 30_000,
  });

  const isDemo = BACKEND_MODE === "DEMO";
  const Icon = isDemo ? FlaskConical : Radio;

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-md border px-2.5 py-1.5 text-xs font-semibold uppercase tracking-wider",
        isDemo
          ? "border-demo/50 bg-demo/15 text-demo"
          : isError
            ? "border-critical/50 bg-critical/15 text-critical"
            : "border-live/50 bg-live/15 text-live",
        className,
      )}
      title={isDemo ? "No backend configured — data is mocked" : `Connected to ${API_BASE_URL}`}
    >
      <Icon className="size-3.5" aria-hidden />
      {isDemo ? "Demo data" : isError ? "Backend offline" : "Live backend"}
      <span className="hidden font-normal normal-case tracking-normal text-muted-foreground sm:inline">
        {isDemo ? "mock API" : (data?.version ?? "connecting…")}
      </span>
    </div>
  );
}

export function DemoBanner() {
  if (BACKEND_MODE !== "DEMO") return null;
  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-demo/30 bg-demo/10 px-4 py-2 text-xs text-demo">
      <FlaskConical className="size-3.5" aria-hidden />
      <span className="font-semibold uppercase tracking-wider">Demo mode</span>
      <span className="text-muted-foreground">
        Every number on screen comes from bundled fixtures. Set VITE_API_BASE_URL to attach the
        FastAPI simulator and switch to live results.
      </span>
    </div>
  );
}
