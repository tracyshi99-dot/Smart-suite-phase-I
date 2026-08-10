/**
 * Format a number as percentage string
 */
export function formatPercent(value: number): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(0)}%`;
}

/**
 * Format a date string to locale display
 */
export function formatDate(dateStr: string, locale = "zh-CN"): string {
  try {
    return new Date(dateStr).toLocaleDateString(locale, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

/**
 * Truncate text to max length with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "…";
}

/**
 * Format large numbers with comma separators
 */
export function formatNumber(num: number): string {
  return num.toLocaleString();
}

/**
 * Determine trend direction from change value
 */
export function getTrend(change: number): "up" | "down" | "flat" {
  if (change > 0) return "up";
  if (change < 0) return "down";
  return "flat";
}

/**
 * Sleep utility for delays
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Generate a simple unique ID
 */
export function uid(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

/**
 * Clamp a number between min and max
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}
