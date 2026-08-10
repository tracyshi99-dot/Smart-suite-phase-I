"use client";

import { GlassCard } from "./GlassCard";

interface MetricCardProps {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  trend?: "up" | "down" | "flat";
}

export function MetricCard({
  label,
  value,
  change,
  changeLabel,
  trend,
}: MetricCardProps) {
  const trendColor =
    trend === "up"
      ? "text-[var(--success)]"
      : trend === "down"
      ? "text-[var(--error)]"
      : "text-[var(--text-secondary)]";

  const trendIcon =
    trend === "up" ? "↑" : trend === "down" ? "↓" : "→";

  return (
    <GlassCard padding="md" className="flex flex-col gap-1 min-w-[140px]">
      <span className="text-xs text-[var(--text-secondary)] uppercase tracking-wide">
        {label}
      </span>
      <span className="text-2xl font-bold text-[var(--text-primary)]">
        {value}
      </span>
      {change !== undefined && (
        <span className={`text-sm flex items-center gap-1 ${trendColor}`}>
          <span>{trendIcon}</span>
          <span>
            {change > 0 ? "+" : ""}
            {change}%
          </span>
          {changeLabel && (
            <span className="text-[var(--text-muted)] ml-1">
              {changeLabel}
            </span>
          )}
        </span>
      )}
    </GlassCard>
  );
}
