import type { ReactElement } from "react";

type Health = {
  status?: string;
  tasks?: number;
  active_tasks?: number;
  agents?: number;
  uptime_seconds?: number;
};

export function Dashboard({ health }: { health: Health | null }): ReactElement {
  const h = health ?? {};
  return (
    <main className="dash">
      <header className="dash-header">
        <h1>◈ SOVEREIGN <span>ORCHESTRATOR</span></h1>
        <span className={`pill ${h.status === "ok" ? "ok" : ""}`}>
          {h.status ?? "connecting…"}
        </span>
      </header>

      <section className="grid">
        <MetricCard label="Status" value={(h.status ?? "—").toUpperCase()} />
        <MetricCard label="Tasks" value={String(h.tasks ?? 0)} />
        <MetricCard label="Active" value={String(h.active_tasks ?? 0)} />
        <MetricCard label="Agents" value={String(h.agents ?? 0)} />
      </section>

      <p className="note">
        uptime {Math.round((h.uptime_seconds ?? 0) / 60)} min · event stream on /ws/events
      </p>
    </main>
  );
}

function MetricCard({ label, value }: { label: string; value: string }): ReactElement {
  return (
    <div className="card">
      <h3>{label}</h3>
      <div className="metric">{value}</div>
    </div>
  );
}
