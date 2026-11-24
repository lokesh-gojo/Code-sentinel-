import React from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Code2,
  LayoutDashboard,
  GitPullRequest,
  Network,
  Database,
  BotMessageSquare,
  FileCheck2,
  Boxes,
  Gauge,
} from "lucide-react";

export const Navbar: React.FC = () => {
  return (
    <nav className="border-b border-gray-800 bg-[#0e1320]/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-2 text-indigo-400 font-bold text-lg hover:text-indigo-300">
              <ShieldCheck className="w-6 h-6 text-indigo-400" />
              <span className="tracking-tight text-white font-mono">CODE SENTINEL AI</span>
            </Link>
            <span className="hidden sm:inline-block text-[10px] bg-indigo-500/10 text-indigo-400 px-2.5 py-0.5 rounded-full border border-indigo-500/20 font-mono">
              v3.0 SQE
            </span>
          </div>

          <div className="flex items-center gap-1 sm:gap-1.5 overflow-x-auto">
            <Link
              href="/dashboard"
              className="flex items-center gap-1 text-xs font-medium text-gray-300 hover:text-white px-2 py-1.5 rounded-lg hover:bg-gray-800/60 transition"
            >
              <LayoutDashboard className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden md:inline">Quality Score</span>
            </Link>

            <Link
              href="/scan"
              className="flex items-center gap-1 text-xs font-medium text-gray-300 hover:text-white px-2 py-1.5 rounded-lg hover:bg-gray-800/60 transition"
            >
              <Code2 className="w-3.5 h-3.5 text-indigo-400" />
              <span>Workbench</span>
            </Link>

            <Link
              href="/repository"
              className="flex items-center gap-1 text-xs font-medium text-gray-300 hover:text-white px-2 py-1.5 rounded-lg hover:bg-gray-800/60 transition"
            >
              <Network className="w-3.5 h-3.5 text-cyan-400" />
              <span className="hidden lg:inline">Repo Graph</span>
            </Link>

            <Link
              href="/policy"
              className="flex items-center gap-1 text-xs font-medium text-gray-300 hover:text-white px-2 py-1.5 rounded-lg hover:bg-gray-800/60 transition"
            >
              <FileCheck2 className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden lg:inline">Policy</span>
            </Link>

            <Link
              href="/supply-chain"
              className="flex items-center gap-1 text-xs font-medium text-gray-300 hover:text-white px-2 py-1.5 rounded-lg hover:bg-gray-800/60 transition"
            >
              <Boxes className="w-3.5 h-3.5 text-purple-400" />
              <span className="hidden xl:inline">SBOM</span>
            </Link>

            <Link
              href="/benchmarks"
              className="flex items-center gap-1 text-xs font-medium text-gray-300 hover:text-white px-2 py-1.5 rounded-lg hover:bg-gray-800/60 transition"
            >
              <Gauge className="w-3.5 h-3.5 text-rose-400" />
              <span className="hidden xl:inline">Benchmarks</span>
            </Link>

            <Link
              href="/repos"
              className="flex items-center gap-1 text-xs font-medium text-gray-300 hover:text-white px-2 py-1.5 rounded-lg hover:bg-gray-800/60 transition"
            >
              <GitPullRequest className="w-3.5 h-3.5 text-violet-400" />
              <span className="hidden md:inline">PRs</span>
            </Link>

            <Link
              href="/memory"
              className="flex items-center gap-1 text-xs font-medium text-gray-300 hover:text-white px-2 py-1.5 rounded-lg hover:bg-gray-800/60 transition"
            >
              <Database className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden xl:inline">Memory</span>
            </Link>

            <Link
              href="/assistant"
              className="flex items-center gap-1 text-xs font-medium text-indigo-300 bg-indigo-600/20 border border-indigo-500/30 px-2 py-1.5 rounded-lg hover:bg-indigo-600/30 transition"
            >
              <BotMessageSquare className="w-3.5 h-3.5 text-indigo-400" />
              <span className="hidden sm:inline">AI Chat</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};
