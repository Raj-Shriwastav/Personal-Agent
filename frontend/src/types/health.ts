// These mirror the Pydantic schemas in backend/app/schemas/health.py.
// Keeping both sides typed means a backend change that breaks the contract
// shows up as a TypeScript error here, not as a runtime surprise.

export interface HealthResponse {
  status: "ok";
  app: string;
  environment: string;
}

export interface DatabaseHealthResponse {
  status: "ok" | "error";
  database: "connected" | "unreachable";
  detail: string;
}
