"use client";

import { PipelineStep } from "@/lib/types";

interface PipelineFlowProps {
  steps: PipelineStep[];
  activeStep?: string;
}

export function PipelineFlow({ steps, activeStep }: PipelineFlowProps) {
  return (
    <div className="flex items-center gap-1 overflow-x-auto py-2" role="list" aria-label="Pipeline steps">
      {steps.map((step, idx) => {
        const isActive = step.id === activeStep || step.status === "active";
        const isComplete = step.status === "complete";

        return (
          <div key={step.id} className="flex items-center" role="listitem">
            {/* Step indicator */}
            <div
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                ${
                  isActive
                    ? "bg-[var(--accent)]/15 text-[var(--accent)] border border-[var(--accent)]/40"
                    : isComplete
                    ? "bg-[var(--success)]/10 text-[var(--success)] border border-[var(--success)]/20"
                    : "bg-white/5 text-[var(--text-muted)] border border-[var(--border-glass)]"
                }
              `}
            >
              <span>
                {isComplete ? "✓" : idx + 1}
              </span>
              <span>{step.label}</span>
              {step.fileCount !== undefined && (
                <span className="text-[10px] opacity-60">({step.fileCount})</span>
              )}
            </div>

            {/* Connector */}
            {idx < steps.length - 1 && (
              <div
                className={`w-6 h-px mx-1 ${
                  isComplete ? "bg-[var(--success)]/40" : "bg-[var(--border-glass)]"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
