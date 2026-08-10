"use client";

import { useBatchStore } from "@/stores/batch-store";

interface BatchSelectorProps {
  className?: string;
}

export function BatchSelector({ className = "" }: BatchSelectorProps) {
  const { activeBatch, batches, setActiveBatch } = useBatchStore();

  return (
    <select
      value={activeBatch}
      onChange={(e) => setActiveBatch(e.target.value)}
      className={`
        bg-white/5 border border-[var(--border-glass)] rounded-lg
        px-3 py-1.5 text-sm text-[var(--text-primary)]
        focus:outline-none focus:border-[var(--accent)]
        ${className}
      `.trim()}
      aria-label="Select batch"
    >
      {batches.map((b) => (
        <option key={b} value={b} className="bg-[var(--bg-secondary)]">
          {b}
        </option>
      ))}
    </select>
  );
}
