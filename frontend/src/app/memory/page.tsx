"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MemoryRecord } from "@/lib/types";
import { Database, Plus, CheckCircle2, BookOpen, ShieldCheck } from "lucide-react";

export default function MemoryPage() {
  const [records, setRecords] = useState<MemoryRecord[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [memoryType, setMemoryType] = useState<"convention" | "decision" | "framework_pattern">("convention");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getMemory("default").then(setRecords).catch(console.error);
  }, []);

  const handleAddMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !description) return;
    setLoading(true);
    try {
      const newRec = await api.addMemory("default", memoryType, title, description);
      setRecords((prev) => [newRec, ...prev]);
      setTitle("");
      setDescription("");
    } catch (err: any) {
      alert(`Failed to save memory: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Database className="w-6 h-6 text-amber-400" />
          Project Memory & Architectural Knowledge Base
        </h1>
        <p className="text-xs text-gray-400 mt-1">
          Stores approved coding conventions, architectural decisions, and verified patch patterns that guide future multi-agent reviews.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Memory Records List */}
        <div className="lg:col-span-8 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-indigo-400" />
            Active Repository Conventions ({records.length})
          </h2>

          <div className="space-y-3">
            {records.map((rec) => (
              <div key={rec.id} className="p-5 rounded-2xl bg-gray-900 border border-gray-800">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-bold text-white">{rec.title}</span>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                    {rec.memory_type}
                  </span>
                </div>
                <p className="text-xs text-gray-300 leading-relaxed">{rec.description}</p>
                <span className="block mt-3 text-[10px] text-gray-500 font-mono">
                  Recorded: {new Date(rec.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Add Convention Form */}
        <div className="lg:col-span-4">
          <form onSubmit={handleAddMemory} className="p-6 rounded-2xl bg-gray-900 border border-gray-800 shadow-xl">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <Plus className="w-4 h-4 text-indigo-400" />
              Add Project Convention
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Type</label>
                <select
                  value={memoryType}
                  onChange={(e: any) => setMemoryType(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-700 text-gray-200 text-xs rounded-xl p-2.5 font-mono"
                >
                  <option value="convention">Coding Convention</option>
                  <option value="decision">Architecture Decision Record (ADR)</option>
                  <option value="framework_pattern">Framework Pattern</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Rule Title</label>
                <input
                  type="text"
                  placeholder="e.g. Always Validate Optional Query Params"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-700 text-gray-200 text-xs rounded-xl p-2.5"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Description</label>
                <textarea
                  rows={4}
                  placeholder="Detailed rationale and requirements for the AI to enforce during code reviews..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-700 text-gray-200 text-xs rounded-xl p-2.5"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition shadow-lg shadow-indigo-600/20 disabled:opacity-50"
              >
                {loading ? "Saving..." : "Save Convention"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
