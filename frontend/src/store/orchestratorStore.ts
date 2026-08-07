import { create } from "zustand";

type Event = { id?: string; type?: string; payload?: unknown };

type OrchestratorState = {
  health: { status?: string; tasks?: number; active_tasks?: number; agents?: number; uptime_seconds?: number } | null;
  events: Event[];
  fetchHealth: () => Promise<void>;
  pushEvent: (event: Event) => void;
};

export const useOrchestratorStore = create<OrchestratorState>((set) => ({
  health: null,
  events: [],
  fetchHealth: async () => {
    try {
      const res = await fetch("/health");
      set({ health: await res.json() });
    } catch {
      set({ health: { status: "offline" } });
    }
  },
  pushEvent: (event) =>
    set((s) => ({ events: [event, ...s.events].slice(0, 100) })),
}));
