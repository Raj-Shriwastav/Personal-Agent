import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { DatabaseHealthResponse, HealthResponse } from "../types/health";

export type Loadable<T> =
  | { state: "loading" }
  | { state: "ready"; data: T }
  | { state: "failed"; error: string };

export interface SystemStatus {
  backend: Loadable<HealthResponse>;
  database: Loadable<DatabaseHealthResponse>;
  refresh: () => void;
}

// A custom hook: bundles the "fetch on mount + keep state" logic so the page
// component only has to render. Later hooks (useTasks, useProjects...) will
// follow the same pattern.
export function useSystemStatus(): SystemStatus {
  const [backend, setBackend] = useState<Loadable<HealthResponse>>({ state: "loading" });
  const [database, setDatabase] = useState<Loadable<DatabaseHealthResponse>>({ state: "loading" });
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setBackend({ state: "loading" });
    setDatabase({ state: "loading" });

    api
      .health()
      .then((data) => !cancelled && setBackend({ state: "ready", data }))
      .catch((e: Error) => !cancelled && setBackend({ state: "failed", error: e.message }));

    api
      .databaseHealth()
      .then((data) => !cancelled && setDatabase({ state: "ready", data }))
      .catch((e: Error) => !cancelled && setDatabase({ state: "failed", error: e.message }));

    return () => {
      cancelled = true;
    };
  }, [tick]);

  return { backend, database, refresh: () => setTick((t) => t + 1) };
}
