import { StatusCard } from "../components/StatusCard";
import { useSystemStatus } from "../hooks/useSystemStatus";

export function SystemStatusPage() {
  const { backend, database, refresh } = useSystemStatus();

  const backendOk = backend.state === "loading" ? null : backend.state === "ready";
  const backendDetail =
    backend.state === "ready"
      ? `${backend.data.app} · ${backend.data.environment}`
      : backend.state === "failed"
        ? backend.error
        : "Contacting FastAPI...";

  const databaseOk =
    database.state === "loading"
      ? null
      : database.state === "ready" && database.data.status === "ok";
  const databaseDetail =
    database.state === "ready"
      ? database.data.detail
      : database.state === "failed"
        ? database.error
        : "Asking backend to ping PostgreSQL...";

  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <header className="mb-8">
        <p className="text-sm font-medium uppercase tracking-wide text-zinc-500">
          Personal AI Agent
        </p>
        <h1 className="mt-1 text-3xl font-bold text-zinc-900">System status</h1>
        <p className="mt-2 text-zinc-600">
          Phase 1 check: React → FastAPI → PostgreSQL.
        </p>
      </header>

      <div className="grid gap-4">
        <StatusCard title="Backend (FastAPI)" ok={backendOk} detail={backendDetail} />
        <StatusCard title="Database (PostgreSQL)" ok={databaseOk} detail={databaseDetail} />
      </div>

      <button
        onClick={refresh}
        className="mt-6 rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700"
      >
        Re-check
      </button>
    </main>
  );
}
