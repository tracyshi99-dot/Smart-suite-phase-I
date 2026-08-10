import { create } from "zustand";
import { PipelineStep } from "@/lib/types";

interface PipelineState {
  status: Record<string, PipelineStep[]>;
  fetchStatus: (batchId: string) => Promise<void>;
  invalidate: (batchId: string) => void;
}

const DEFAULT_STEPS: PipelineStep[] = [
  { id: "01_zhiku", label: "智库", status: "pending" },
  { id: "02_zhizao", label: "智造", status: "pending" },
  { id: "03_zhiyou", label: "智优", status: "pending" },
  { id: "04_zhibu", label: "智布", status: "pending" },
];

export const usePipelineStore = create<PipelineState>()((set, get) => ({
  status: {},

  fetchStatus: async (batchId: string) => {
    // In the future, call /api/pipeline/status?batch_id=...
    // For now, use defaults
    const current = get().status[batchId];
    if (!current) {
      set((state) => ({
        status: { ...state.status, [batchId]: [...DEFAULT_STEPS] },
      }));
    }
  },

  invalidate: (batchId: string) => {
    set((state) => {
      const newStatus = { ...state.status };
      delete newStatus[batchId];
      return { status: newStatus };
    });
  },
}));
