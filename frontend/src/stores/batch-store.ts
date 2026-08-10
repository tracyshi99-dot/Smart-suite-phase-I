import { create } from "zustand";
import { persist } from "zustand/middleware";

interface BatchState {
  activeBatch: string;
  batches: string[];
  setActiveBatch: (id: string) => void;
  setBatches: (batches: string[]) => void;
  fetchBatches: () => Promise<void>;
}

export const useBatchStore = create<BatchState>()(
  persist(
    (set) => ({
      activeBatch: "batch_001",
      batches: ["batch_001"],

      setActiveBatch: (id: string) => {
        set({ activeBatch: id });
      },

      setBatches: (batches: string[]) => {
        set({ batches });
      },

      fetchBatches: async () => {
        // In the future, fetch from /api/batches endpoint
        // For now, use default
        set({ batches: ["batch_001"] });
      },
    }),
    {
      name: "batch-store",
      partialize: (state) => ({
        activeBatch: state.activeBatch,
      }),
    }
  )
);
