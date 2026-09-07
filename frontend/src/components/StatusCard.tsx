interface StatusCardProps {
  title: string;
  ok: boolean | null; // null = still loading
  detail: string;
}

export function StatusCard({ title, ok, detail }: StatusCardProps) {
  const color =
    ok === null ? "bg-zinc-400" : ok ? "bg-emerald-500" : "bg-rose-500";
  const label = ok === null ? "checking" : ok ? "healthy" : "unavailable";

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-zinc-900">{title}</h2>
        <span className="flex items-center gap-2 text-sm text-zinc-600">
          <span className={`inline-block h-2.5 w-2.5 rounded-full ${color}`} />
          {label}
        </span>
      </div>
      <p className="mt-2 text-sm text-zinc-600">{detail}</p>
    </div>
  );
}
