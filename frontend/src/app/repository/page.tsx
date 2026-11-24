"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { RepositoryArchitectureReport } from "@/lib/types";
import { Network, RefreshCw, AlertTriangle, Layers, FileCode, GitFork, CheckCircle2 } from "lucide-react";

export default function RepositoryPage() {
  const [report, setReport] = useState<RepositoryArchitectureReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getRepoIntelligence()
      .then((data) => setReport(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Network className="w-6 h-6 text-cyan-400" />
            Repository Intelligence Engine
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            NetworkX-powered AST dependency graph, circular import analysis, framework detection, and dead code discovery.
          </p>
        </div>

        <button
          onClick={() => {
            setLoading(true);
            api.getRepoIntelligence().then(setReport).finally(() => setLoading(false));
          }}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold border border-gray-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Re-index Repository
        </button>
      </div>

      {loading ? (
        <div className="py-24 text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-cyan-400 mx-auto mb-3" />
          <p className="text-sm text-gray-400">Analyzing repository AST and generating NetworkX dependency model...</p>
        </div>
      ) : !report ? (
        <div className="py-12 text-center text-gray-500">Failed to load repository model.</div>
      ) : (
        <div className="space-y-6">
          {/* Summary Box */}
          <div className="p-6 rounded-2xl bg-gray-900 border border-gray-800">
            <h3 className="text-sm font-bold text-white mb-2">Architecture Summary</h3>
            <p className="text-xs text-gray-300 leading-relaxed font-mono">{report.architecture_summary}</p>

            <div className="mt-4 flex flex-wrap gap-2">
              {report.frameworks_detected.map((fw, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-lg bg-cyan-950/40 text-cyan-300 border border-cyan-800/50 text-xs font-mono"
                >
                  {fw}
                </span>
              ))}
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div className="p-5 rounded-2xl bg-gray-900/60 border border-gray-800">
              <span className="text-xs font-semibold text-gray-400 uppercase">Tracked Source Files</span>
              <div className="text-2xl font-bold text-white mt-1">{report.total_files}</div>
            </div>

            <div className="p-5 rounded-2xl bg-gray-900/60 border border-gray-800">
              <span className="text-xs font-semibold text-gray-400 uppercase">Circular Dependency Cycles</span>
              <div className={`text-2xl font-bold mt-1 ${report.circular_dependencies.length > 0 ? "text-amber-400" : "text-emerald-400"}`}>
                {report.circular_dependencies.length}
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-gray-900/60 border border-gray-800">
              <span className="text-xs font-semibold text-gray-400 uppercase">Unreferenced Functions</span>
              <div className="text-2xl font-bold text-purple-400 mt-1">{report.unused_functions.length}</div>
            </div>
          </div>

          {/* Circular Dependencies & Unused Functions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-gray-900 border border-gray-800">
              <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                <GitFork className="w-4 h-4 text-amber-400" />
                Circular Import Hazards
              </h3>
              {report.circular_dependencies.length === 0 ? (
                <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-900/30 text-emerald-400 text-xs flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  Zero circular dependency cycles detected across modules.
                </div>
              ) : (
                <div className="space-y-2">
                  {report.circular_dependencies.map((cycle, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-amber-950/30 border border-amber-900/40 text-xs font-mono text-amber-200">
                      Cycle #{idx + 1}: {cycle.join(" ➔ ")} ➔ {cycle[0]}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-6 rounded-2xl bg-gray-900 border border-gray-800">
              <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                <FileCode className="w-4 h-4 text-purple-400" />
                Potentially Dead Code & Uncalled Functions
              </h3>
              {report.unused_functions.length === 0 ? (
                <p className="text-xs text-gray-400">All scanned functions have active references.</p>
              ) : (
                <ul className="space-y-2 max-h-48 overflow-y-auto">
                  {report.unused_functions.map((fn, idx) => (
                    <li key={idx} className="text-xs font-mono text-gray-300 p-2 bg-gray-950 rounded border border-gray-800">
                      {fn}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Dependency Graph Nodes Explorer */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
            <div className="p-5 border-b border-gray-800 flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-400" />
                Source File Topology & AST Nodes ({report.nodes.length})
              </h3>
            </div>
            <div className="divide-y divide-gray-800 max-h-96 overflow-y-auto text-xs">
              {report.nodes.map((node) => (
                <div key={node.id} className="p-4 flex items-center justify-between hover:bg-gray-800/40">
                  <div>
                    <span className="font-mono text-white font-medium">{node.id}</span>
                    <div className="flex items-center gap-2 mt-1 text-[11px] text-gray-400">
                      <span className="uppercase text-cyan-400 font-mono">{node.language}</span>
                      <span>·</span>
                      <span>{node.lines_of_code} lines</span>
                      <span>·</span>
                      <span>{node.functions.length} functions</span>
                    </div>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono text-[10px] uppercase">
                    {node.type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
