import React from "react";
import { Check, X, ShieldAlert } from "lucide-react";

interface Props {
  originalCode: string;
  patchedCode: string;
  regressionTest?: string;
  explanation?: string;
  onApprove: () => void;
  onReject: () => void;
  isSubmitting?: boolean;
}

export const DiffViewer: React.FC<Props> = ({
  originalCode,
  patchedCode,
  regressionTest,
  explanation,
  onApprove,
  onReject,
  isSubmitting = false,
}) => {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between pb-4 border-b border-gray-800 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            <h3 className="text-lg font-bold text-white">Human Approval Gate</h3>
          </div>
          <p className="text-xs text-gray-400 mt-0.5">
            LangGraph Agent paused at interrupt(). Validate proposed patch and regression test before committing.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onReject}
            disabled={isSubmitting}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm font-semibold transition disabled:opacity-50"
          >
            <X className="w-4 h-4 text-red-400" />
            Reject Patch
          </button>
          <button
            onClick={onApprove}
            disabled={isSubmitting}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition shadow-lg shadow-emerald-600/20 disabled:opacity-50"
          >
            <Check className="w-4 h-4" />
            Approve & Apply
          </button>
        </div>
      </div>

      {explanation && (
        <div className="mb-4 p-4 rounded-xl bg-indigo-950/30 border border-indigo-900/50">
          <h4 className="text-xs font-semibold uppercase text-indigo-400 tracking-wider mb-1">
            Agent Reasoning & Root Cause
          </h4>
          <p className="text-sm text-indigo-200 leading-relaxed">{explanation}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <div>
          <span className="block text-xs font-mono uppercase text-red-400 mb-1.5 font-semibold">
            Original Vulnerable Code
          </span>
          <pre className="p-3 bg-black/60 rounded-xl border border-red-950 text-red-300 text-xs font-mono h-60 overflow-y-auto leading-relaxed">
            {originalCode}
          </pre>
        </div>

        <div>
          <span className="block text-xs font-mono uppercase text-emerald-400 mb-1.5 font-semibold">
            Agent Proposed Patch
          </span>
          <pre className="p-3 bg-black/60 rounded-xl border border-emerald-950 text-emerald-300 text-xs font-mono h-60 overflow-y-auto leading-relaxed">
            {patchedCode}
          </pre>
        </div>
      </div>

      {regressionTest && (
        <div>
          <span className="block text-xs font-mono uppercase text-violet-400 mb-1.5 font-semibold">
            Generated Regression Test (Validated in Sandbox)
          </span>
          <pre className="p-3 bg-black/60 rounded-xl border border-violet-950 text-violet-300 text-xs font-mono max-h-48 overflow-y-auto leading-relaxed">
            {regressionTest}
          </pre>
        </div>
      )}
    </div>
  );
};
