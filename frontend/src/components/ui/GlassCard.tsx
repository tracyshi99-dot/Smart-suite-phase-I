"use client";

import { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  glow?: boolean;
  padding?: "sm" | "md" | "lg";
}

const paddingMap = {
  sm: "p-3",
  md: "p-5",
  lg: "p-7",
};

export function GlassCard({
  children,
  className = "",
  glow = false,
  padding = "md",
}: GlassCardProps) {
  return (
    <div
      className={`
        glass ${paddingMap[padding]}
        ${glow ? "glass-glow" : ""}
        ${className}
      `.trim()}
    >
      {children}
    </div>
  );
}
