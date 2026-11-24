import React from "react";
import { SeverityLevel } from "@/lib/types";

interface Props {
  severity: SeverityLevel;
  className?: string;
}

export const SeverityBadge: React.FC<Props> = ({ severity, className = "" }) => {
  const styles: Record<SeverityLevel, string> = {
    high: "bg-red-500/15 text-red-400 border-red-500/30",
    medium: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    low: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    info: "bg-slate-500/15 text-slate-400 border-slate-500/30",
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border ${styles[severity]} ${className}`}
    >
      {severity}
    </span>
  );
};
