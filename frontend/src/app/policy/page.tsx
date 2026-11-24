"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";
import { CodeReviewPolicy, PolicyEvaluationResult } from "@/lib/types";
import { FileCheck2, ShieldAlert, CheckCircle2, XCircle, RefreshCw } from "lucide-react";

export default function PolicyPage() {
  const [policy, setPolicy] = useState<CodeReviewPolicy>({
    block_critical_vulnerabilities: true,
    block_high_severity: true,
    block_hardcoded_secrets: true,
    minimum_quality_score: 75,
    require_human_approval: true,
    allow_auto_merge: false,
    max_cyclomatic_complexity: 15,
  });

  const [result, setResult] = useState<PolicyEvaluationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleEvaluate = async () => {
    setLoading(true);
    try {
      const res = await api.evaluatePolicy(policy);
      setResult(res);
    } catch (err: any) {
      alert(`Evaluation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <FileCheck2 className="w-6 h-6 text-amber-400" />
          Intelligent Code Review Policy Engine
        </h1>
        <p className="text-xs text-gray-400 mt-1">
          Feature 18: Deterministic quality gating. Enforces customizable compliance and security policies independently of the LLM before merge.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Policy Configuration Form */}
        <div className="lg:col-span-6 bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
          <h2 className="text-sm font-bold text-white mb-4">Repository Merge Policy Configuration</h2>

          <div className="space-y-4 text-xs">
            <label className="flex items-center justify-between p-3 rounded-xl bg-gray-950 border border-gray-800 cursor-pointer">
              <span>Block High & Critical Vulnerabilities</span>
              <input
                type="checkbox"
                checked={policy.block_high_severity}
                onChange={(e) => setPolicy({ ...policy, block_high_severity: e.target.checked })}
                className="w-4 h-4 rounded text-indigo-600"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl bg-gray-950 border border-gray-800 cursor-pointer">
              <span>Block Hardcoded Secrets & API Keys</span>
              <input
                type="checkbox"
                checked={policy.block_hardcoded_secrets}
                onChange={(e) => setPolicy({ ...policy, block_hardcoded_secrets: e.target.checked })}
                className="w-4 h-4 rounded text-indigo-600"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl bg-gray-950 border border-gray-800 cursor-pointer">
              <span>Require Human Approval Gate (100% Zero Auto-Merge)</span>
              <input
                type="checkbox"
                checked={policy.require_human_approval}
                onChange={(e) => setPolicy({ ...policy, require_human_approval: e.target.checked })}
                className="w-4 h-4 rounded text-indigo-600"
              />
            </label>

            <div className="p-3 rounded-xl bg-gray-950 border border-gray-800">
              <div className="flex justify-between mb-1">
                <span>Minimum Quality Score Required:</span>
                <span className="font-mono text-indigo-400 font-bold">{policy.minimum_quality_score}/100</span>
              </div>
              <input
                type="range"
                min="50"
                max="95"
                value={policy.minimum_quality_score}
                onChange={(e) => setPolicy({ ...policy, minimum_quality_score: parseInt(e.target.value) })}
                className="w-full accent-indigo-500"
              />
            </div>

            <button
              onClick={handleEvaluate}
              disabled={loading}
              className="w-full mt-2 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldAlert className="w-4 h-4" />}
              Evaluate Compliance Against Repository
            </button>
          </div>
        </div>

        {/* Evaluation Output */}
        <div className="lg:col-span-6 bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl flex flex-col">
          <h2 className="text-sm font-bold text-white mb-4">Deterministic Policy Decision</h2>

          {!result ? (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500 text-center py-16">
              <FileCheck2 className="w-10 h-10 mb-2 text-gray-600" />
              <p className="text-xs">Adjust configuration and click &quot;Evaluate Compliance&quot; to test policy enforcement.</p>
            </div>
          ) : (
            <div className="space-y-4 flex-1">
              <div
                className={`p-4 rounded-xl border flex items-center gap-3 ${
                  result.passed
                    ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300"
                    : "bg-red-950/40 border-red-500/40 text-red-300"
                }`}
              >
                {result.passed ? <CheckCircle2 className="w-6 h-6" /> : <XCircle className="w-6 h-6" />}
                <div>
                  <div className="font-bold text-sm">Merge Status: {result.merge_status}</div>
                  <p className="text-xs opacity-90">
                    {result.passed ? "All policy rules satisfied. Code is eligible for merge." : "Pull Request merge is blocked by deterministic quality policy."}
                  </p>
                </div>
              </div>

              {result.violations.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold uppercase text-red-400 mb-2">Active Policy Violations:</h3>
                  <ul className="space-y-2">
                    {result.violations.map((v, idx) => (
                      <li key={idx} className="p-3 bg-red-950/20 border border-red-900/40 rounded-xl text-xs text-red-200">
                        {v}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div>
                <h3 className="text-xs font-semibold uppercase text-gray-400 mb-2">Enforced Policy Rules:</h3>
                <div className="flex flex-wrap gap-2">
                  {result.enforced_rules.map((rule, idx) => (
                    <span key={idx} className="px-2.5 py-1 bg-gray-950 border border-gray-800 text-gray-300 rounded-lg text-[11px] font-mono">
                      {rule}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
