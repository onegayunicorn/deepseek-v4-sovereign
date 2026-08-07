import { useEffect } from "react";
import { useOrchestratorStore } from "../store/orchestratorStore";

/** Subscribes to the orchestrator event stream and pushes events into the store. */
export function useWebSocket(): void {
  const pushEvent = useOrchestratorStore((s) => s.pushEvent);

  useEffect(() => {
    const proto = location.protocol === "https:" ? "wss://" : "ws://";
    let ws: WebSocket | null = null;
    let retry: ReturnType<typeof setTimeout>;

    const connect = () => {
      ws = new WebSocket(`${proto}${location.host}/ws/events`);
      ws.onmessage = (m) => {
        try {
          pushEvent(JSON.parse(m.data));
        } catch {
          /* ignore malformed frames */
        }
      };
      ws.onclose = () => {
        retry = setTimeout(connect, 3000); // reconnect with backoff
      };
    };
    connect();
    return () => {
      ws?.close();
      clearTimeout(retry);
    };
  }, [pushEvent]);
}
