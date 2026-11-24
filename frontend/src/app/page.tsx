import React from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Code2,
  Cpu,
  GitPullRequest,
  ArrowRight,
  CheckCircle2,
  Network,
  Database,
  BotMessageSquare,
  Lock,
  Layers,
} from "lucide-react";

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
      {/* Hero Section */}
      <div className="text-center max-w-4xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-6">
          <Cpu className="w-3.5 h-3.5" />
          Autonomous AI Software Quality Engineer · Detect. Understand. Repair. Verify.
        </div>
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6">
          CODE SENTINEL AI <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            Autonomous Quality & Debugging Platform
          </span>
        </h1>
        <p className="text-lg text-gray-400 leading-relaxed mb-8 max-w-3xl mx-auto">
          Evolves traditional linting and chatbots into a full-scale AI Software Quality Engineer.
          Understands entire repositories with NetworkX dependency graphs, investigates root causes,
          generates surgical patches, validates fixes inside isolated microVM sandboxes, and guards production with human approval gates.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/scan"
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-3.5 rounded-xl shadow-lg shadow-indigo-600/30 transition transform hover:-translate-y-0.5"
          >
            Launch Code Workbench
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/repository"
            className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-200 font-semibold px-6 py-3.5 rounded-xl border border-gray-700 transition"
          >
            <Network className="w-4 h-4 text-cyan-400" />
            Repository Intelligence
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-2 bg-gray-900 hover:bg-gray-800 text-gray-300 font-semibold px-6 py-3.5 rounded-xl border border-gray-800 transition"
          >
            Quality Score (86/100)
          </Link>
        </div>
      </div>

      {/* 4 Core Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        <div className="p-6 rounded-2xl bg-gray-900/60 border border-gray-800 hover:border-gray-700 transition">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400 mb-4">
            <Network className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">Repo Intelligence</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            NetworkX dependency graphs map files, import paths, circular dependencies, and unused functions across the entire repository.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-gray-900/60 border border-gray-800 hover:border-gray-700 transition">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 mb-4">
            <Layers className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">Multi-Agent System</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            LangGraph orchestrates Code Analyst, Bug Hunter, Security, Performance, Test Engineer, and Fix Engineer agents in a self-healing loop.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-gray-900/60 border border-gray-800 hover:border-gray-700 transition">
          <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center text-red-400 mb-4">
            <Lock className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">Isolated Sandbox</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            Untrusted code never touches the host OS. Tests execute in isolated E2B microVMs with resource limits and zero network access.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-gray-900/60 border border-gray-800 hover:border-gray-700 transition">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400 mb-4">
            <Database className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">Project Memory</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            Stores verified architectural decisions, coding patterns, and approved conventions to maintain consistency across reviews.
          </p>
        </div>
      </div>

      {/* Multi-LLM & Acceptance Criteria Banner */}
      <div className="p-8 rounded-2xl bg-[#0f1523] border border-gray-800 max-w-4xl mx-auto shadow-2xl">
        <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-indigo-400" />
          Multi-LLM & Offline Provider Architecture
        </h3>
        <p className="text-xs text-gray-400 mb-4 leading-relaxed">
          Switch seamlessly between Google Gemini 2.5 Flash for cloud analysis and Ollama (CodeLlama, DeepSeek) for 100% offline, private air-gapped inference.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-gray-300">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Cloud: Gemini 2.5 Flash via Google GenAI SDK
          </div>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Offline: Ollama Local Server (port 11434)
          </div>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Fallback: Pure Deterministic AST Heuristics
          </div>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Approval: LangGraph interrupt() Pausing
          </div>
        </div>
      </div>
    </div>
  );
}
