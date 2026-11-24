"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { CycloneDXSBOMReport } from "@/lib/types";
import { Boxes, ShieldCheck, AlertTriangle, Download, RefreshCw, FileText } from "lucide-react";

export default function SupplyChainPage() {
  const [sbom, setSbom] = useState<CycloneDXSBOMReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSBOM().then(setSbom).catch(console.error).finally(() => setLoading(false));
  }, []);

  const exportJSON = () => {
    if (!sbom) return;
    const blob = new Blob([JSON.stringify(sbom, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `cyclonedx-sbom-${Date.now()}.json`;
    a.click();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Boxes className="w-6 h-6 text-purple-400" />
            Software Supply Chain Security & SBOM
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Feature 16: Software Bill of Materials in CycloneDX v1.5 standard format, license compliance auditing, and package CVE tracking.
          </p>
        </div>

        <button
          onClick={exportJSON}
          disabled={!sbom}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-lg shadow-purple-600/20 transition disabled:opacity-50"
        >
          <Download className="w-3.5 h-3.5" />
          Export CycloneDX v1.5 JSON
        </button>
      </div>

      {loading ? (
        <div className="py-24 text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-purple-400 mx-auto mb-3" />
          <p className="text-sm text-gray-400">Parsing dependency manifests and resolving license taxonomy...</p>
        </div>
      ) : !sbom ? (
        <div className="py-12 text-center text-gray-500">Failed to load Software Bill of Materials.</div>
      ) : (
        <div className="space-y-6">
          {/* Metrics Overview */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-5">
            <div className="p-5 rounded-2xl bg-gray-900 border border-gray-800">
              <span className="text-xs font-semibold text-gray-400 uppercase">Total Components</span>
              <div className="text-2xl font-bold text-white mt-1">{sbom.total_components}</div>
            </div>

            <div className="p-5 rounded-2xl bg-gray-900 border border-gray-800">
              <span className="text-xs font-semibold text-gray-400 uppercase">Vulnerable Packages</span>
              <div className={`text-2xl font-bold mt-1 ${sbom.vulnerable_components > 0 ? "text-red-400" : "text-emerald-400"}`}>
                {sbom.vulnerable_components}
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-gray-900 border border-gray-800">
              <span className="text-xs font-semibold text-gray-400 uppercase">License Diversity</span>
              <div className="text-2xl font-bold text-indigo-400 mt-1">
                {Object.keys(sbom.licenses_summary).length} Types
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-gray-900 border border-gray-800">
              <span className="text-xs font-semibold text-gray-400 uppercase">Standard Specification</span>
              <div className="text-2xl font-bold text-purple-400 mt-1">CycloneDX v1.5</div>
            </div>
          </div>

          {/* Component Inventory Table */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="p-5 border-b border-gray-800 flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <FileText className="w-4 h-4 text-purple-400" />
                Component Inventory ({sbom.components.length})
              </h3>
              <span className="text-xs font-mono text-gray-500">PURL Package Uniform Resource Identifiers</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-gray-950/80 text-gray-400 uppercase font-mono">
                  <tr>
                    <th className="px-5 py-3">Package Component</th>
                    <th className="px-5 py-3">Version</th>
                    <th className="px-5 py-3">License</th>
                    <th className="px-5 py-3">Security Advisory</th>
                    <th className="px-5 py-3">Audit Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800 text-gray-300">
                  {sbom.components.map((comp, idx) => (
                    <tr key={idx} className="hover:bg-gray-800/40">
                      <td className="px-5 py-3.5 font-mono text-white font-medium">{comp.name}</td>
                      <td className="px-5 py-3.5 font-mono text-gray-400">{comp.version}</td>
                      <td className="px-5 py-3.5">
                        <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono text-[10px]">
                          {comp.license}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 font-mono text-xs">
                        {comp.is_vulnerable ? (
                          <span className="text-red-400 font-semibold">{comp.cve_id}</span>
                        ) : (
                          <span className="text-emerald-400">Zero CVEs</span>
                        )}
                      </td>
                      <td className="px-5 py-3.5 text-gray-400">{comp.recommendation}</td>
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
