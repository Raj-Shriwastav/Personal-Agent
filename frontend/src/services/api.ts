// Single place that knows how to talk to the backend.
// Components never call fetch() directly; they call functions from here.

import type { DatabaseHealthResponse, HealthResponse } from "../types/health";

// Relative URL: in dev, Vite proxies /api -> FastAPI (see vite.config.ts).
// In production the same relative path works behind a reverse proxy.
const API_BASE = "/api";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`${path} failed with HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

export const api = {
  health: () => getJson<HealthResponse>("/health"),
  databaseHealth: () => getJson<DatabaseHealthResponse>("/health/db"),
};
