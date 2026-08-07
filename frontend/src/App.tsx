import { useEffect } from "react";
import { Dashboard } from "./components/Dashboard";
import { useWebSocket } from "./hooks/useWebSocket";
import { useOrchestratorStore } from "./store/orchestratorStore";

export function App() {
  const { health, fetchHealth } = useOrchestratorStore();
  useWebSocket();

  useEffect(() => {
    fetchHealth();
    const timer = setInterval(fetchHealth, 5000);
    return () => clearInterval(timer);
  }, [fetchHealth]);

  return <Dashboard health={health} />;
}
