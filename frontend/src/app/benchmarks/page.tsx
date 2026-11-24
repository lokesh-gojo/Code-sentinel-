"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";
import { EmpiricalEvaluationReport } from "@/lib/types";
import { Gauge, Play, RefreshCw, CheckCircle2, XCircle, Award, Activity } from "lucide-react";

export default function BenchmarksPage() {
  const [report, setReport] = useState<EmpiricalEvaluationReport | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRunBenchmarks = async () => {
    setLoading(true);
    try {
      const data = await api.runBenchmark();
      setReport(data);
    } catch (err: any) {
      alert(`Benchmark error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Gauge className="w-6 h-6 text-rose-400" />
            Empirical Benchmark & Evaluation Platform
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Section 5 & 9 Evaluation: Tests Code Sentinel AI against ground-truth defect fixtures to calculate precision, recall, false-positive rate, and latency.
          </p>
        </div>

        <button
          onClick={handleRunBenchmarks}
          disabled={loading}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-lg shadow-rose-600/20 transition disabled:opacity-50"
        >
          {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          Execute Ground-Truth Evaluation
        </button>
      </div>

      {!report && !loading && (
        <div className="p-12 text-center bg-gray-900 border border-gray-800 rounded-2xl">
          <Gauge className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white">No Benchmark Executed Yet</h3>
          <p className="text-xs text-gray-400 mt-1 max-w-md mx-auto">
            Click &quot;Execute Ground-Truth Evaluation&quot; to test the system against 8 standard defect and negative-control test vectors.
          </p>
        </div>
      )}

      {loading && (
        <div className="py-24 text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-rose-400 mx-auto mb-3" />
          <p className="text-sm text-gray-400">Executing benchmark suite through multi-engine analyzers and sandboxes...</p>
        </div>
      )}

      {report && (
        <div className="space-y-6">
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
            <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 text-center">
              <span className="text-[11px] text-gray-400 block mb-1">Precision</span>
              <span className="text-2xl font-extrabold text-emerald-400">{(report.precision * 100).toFixed(1)}%</span>
            </div>

            <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 text-center">
              <span className="text-[11px] text-gray-400 block mb-1">Recall</span>
              <span className="text-2xl font-extrabold text-cyan-400">{(report.recall * 100).toFixed(1)}%</span>
            </div>

            <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 text-center">
              <span className="text-[11px] text-gray-400 block mb-1">F1-Score</span>
              <span className="text-2xl font-extrabold text-indigo-400">{report.f1_score.toFixed(2)}</span>
            </div>

            <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 text-center">
              <span className="text-[11px] text-gray-400 block mb-1">False Positive Rate</span>
              <span className="text-2xl font-extrabold text-amber-400">{(report.false_positive_rate * 100).toFixed(1)}%</span>
            </div>

            <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 text-center">
              <span className="text-[11px] text-gray-400 block mb-1">Patch Pass Rate</span>
              <span className="text-2xl font-extrabold text-purple-400">{(report.patch_sandbox_pass_rate * 100).toFixed(1)}%</span>
            </div>

            <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 text-center">
              <span className="text-[11px] text-gray-400 block mb-1">Avg Latency</span>
              <span className="text-2xl font-extrabold text-white">{report.average_latency_ms} ms</span>
            </div>
          </div>

          {/* Detailed Test Cases Table */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="p-5 border-b border-gray-800">
              <h3 className="text-sm font-bold text-white">Ground-Truth Defect Test Cases ({report.total_benchmark_cases})</h3>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-gray-950 text-gray-400 uppercase font-mono">
                  <tr>
                    <th className="px-5 py-3">Case ID</th>
                    <th className="px-5 py-3">Defect Category</th>
                    <th className="px-5 py-3">Detection Status</th>
                    <th className="px-5 py-3">Expected vs Detected Rules</th>
                    <th className="px-5 py-3">Sandbox Patch</th>
                    <th className="px-5 py-3">Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800 text-gray-300">
                  {report.case_results.map((c) => (
                    <tr key={c.case_id} className="hover:bg-gray-800/40">
                      <td className="px-5 py-3.5 font-mono text-indigo-400 font-bold">{c.case_id}</td>
                      <td className="px-5 py-3.5 text-white font-medium">{c.name}</td>
                      <td className="px-5 py-3.5">
                        {c.true_positive ? (
                          <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold">
                            <CheckCircle2 className="w-3.5 h-3.5" /> True Positive
                          </span>
                        ) : c.false_negative ? (
                          <span className="inline-flex items-center gap-1 text-red-400 font-semibold">
                            <XCircle className="w-3.5 h-3.5" /> False Negative
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-cyan-400 font-semibold">
                            <CheckCircle2 className="w-3.5 h-3.5" /> True Negative (Clean)
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-3.5 font-mono text-[11px] text-gray-400">
                        {c.detected_rule_ids.join(", ") || "None"}
                      </td>
                      <td className="px-5 py-3.5 font-semibold">
                        {c.patch_verified_in_sandbox ? (
                          <span className="text-emerald-400">PASSED</span>
                        ) : (
                          <span className="text-red-400">FAILED</span>
                        )}
                      </td>
                      <td className="px-5 py-3.5 font-mono text-gray-400">{c.latency_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
