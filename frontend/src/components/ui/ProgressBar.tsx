"use client";

interface ProgressBarProps {
  percent: number; // 0-100
  label?: string;
  className?: string;
}

export function ProgressBar({ percent, label, className = "" }: ProgressBarProps) {
  const clampedPercent = Math.min(100, Math.max(0, percent));

  return (
    <div className={`w-full ${className}`}>
      {label && (
        <div className="flex justify-between text-xs text-[var(--text-secondary)] mb-1">
          <span>{label}</span>
          <span>{clampedPercent.toFixed(0)}%</span>
        </div>
      )}
      <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
        <div
          className="h-full bg-[var(--accent)] rounded-full transition-all duration-300 ease-out"
          style={{ width: `${clampedPercent}%` }}
        />
      </div>
    </div>
  );
}
