import React from "react";
import { Finding } from "@/lib/types";
import { SeverityBadge } from "./SeverityBadge";
import { AlertTriangle, Sparkles, ChevronRight } from "lucide-react";

interface Props {
  finding: Finding;
  onSelectLine?: (line: number) => void;
  isSelected?: boolean;
}

export const FindingCard: React.FC<Props> = ({ finding, onSelectLine, isSelected }) => {
  return (
    <div
      onClick={() => onSelectLine && onSelectLine(finding.line_number)}
      className={`p-4 rounded-xl border transition cursor-pointer ${
        isSelected
          ? "bg-indigo-950/40 border-indigo-500 shadow-lg shadow-indigo-500/10"
          : "bg-gray-900/60 border-gray-800 hover:border-gray-700 hover:bg-gray-900/90"
      }`}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          <SeverityBadge severity={finding.severity} />
          <span className="text-xs font-mono text-gray-400 bg-gray-800 px-2 py-0.5 rounded">
            Line {finding.line_number}
          </span>
          <span className="text-xs text-gray-500 uppercase tracking-wider">{finding.tool}</span>
        </div>
        <span className="text-xs font-mono text-indigo-400">{finding.rule_id}</span>
      </div>

      <p className="text-sm text-gray-200 font-medium leading-snug mb-2">{finding.message}</p>

      {finding.ai_explanation && (
        <div className="mt-3 p-3 rounded-lg bg-indigo-950/30 border border-indigo-900/40 text-xs text-indigo-200">
          <div className="flex items-center gap-1.5 font-semibold text-indigo-300 mb-1">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            AI Root Cause Analysis
          </div>
          <p className="leading-relaxed text-indigo-200/90">{finding.ai_explanation}</p>
        </div>
      )}

      {finding.suggested_fix && (
        <div className="mt-2 text-xs text-emerald-400 font-mono bg-emerald-950/20 p-2.5 rounded border border-emerald-900/30">
          <div className="font-sans font-semibold text-emerald-300 mb-1">Suggested Correction:</div>
          <pre className="overflow-x-auto whitespace-pre-wrap">{finding.suggested_fix}</pre>
        </div>
      )}
    </div>
  );
};
