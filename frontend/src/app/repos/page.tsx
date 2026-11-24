"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { GitHubRepo, ScanResponse } from "@/lib/types";
import { FindingCard } from "@/components/FindingCard";
import { GitPullRequest, ShieldCheck, Check, Send, RefreshCw, FolderGit2 } from "lucide-react";

export default function ReposPage() {
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<string>("developer/sample-repo");
  const [prNumber, setPrNumber] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [prScanResult, setPrScanResult] = useState<ScanResponse | null>(null);
  const [publishedSuccess, setPublishedSuccess] = useState(false);

  useEffect(() => {
    api
      .listRepos()
      .then((data) => {
        setRepos(data);
        if (data.length > 0) setSelectedRepo(data[0].full_name);
      })
      .catch(() => {});
  }, []);

  const handleScanPR = async () => {
    setLoading(true);
    setPrScanResult(null);
    setPublishedSuccess(false);
    try {
      const res = await api.scanPR(selectedRepo, prNumber);
      setPrScanResult(res);
    } catch (err: any) {
      alert(`PR Scan failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handlePublishReview = async () => {
    if (!prScanResult) return;
    setLoading(true);
    try {
      const body = `### Automated Code Review Report
Found ${prScanResult.total_findings} issues (${prScanResult.summary.high} High, ${prScanResult.summary.medium} Medium).
Review verified and approved by human developer via BugHunter Bot.`;

      await api.publishPRReview(selectedRepo, prNumber, body);
      setPublishedSuccess(true);
    } catch (err: any) {
      alert(`Publish failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <GitPullRequest className="w-6 h-6 text-purple-400" />
          GitHub Pull Request Scanner
        </h1>
        <p className="text-xs text-gray-400 mt-1">
          Review modified files and patches from GitHub PRs. Hard constraint: reviews are only published after human approval.
        </p>
      </div>

      {/* PR Selection Bar */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-8 shadow-xl">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase mb-2">
              Select Repository
            </label>
            <select
              value={selectedRepo}
              onChange={(e) => setSelectedRepo(e.target.value)}
              className="w-full bg-gray-950 border border-gray-700 text-gray-200 text-sm rounded-xl px-3 py-2.5 font-mono"
            >
              {repos.map((r) => (
                <option key={r.id} value={r.full_name}>
                  {r.full_name} ({r.default_branch})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase mb-2">
              Pull Request Number
            </label>
            <input
              type="number"
              min="1"
              value={prNumber}
              onChange={(e) => setPrNumber(parseInt(e.target.value) || 1)}
              className="w-full bg-gray-950 border border-gray-700 text-gray-200 text-sm rounded-xl px-3 py-2.5 font-mono"
            />
          </div>

          <div>
            <button
              onClick={handleScanPR}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold transition shadow-lg shadow-purple-600/20 disabled:opacity-50"
            >
              {loading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <ShieldCheck className="w-4 h-4" />
              )}
              Analyze Pull Request
            </button>
          </div>
        </div>
      </div>

      {/* Published Notice */}
      {publishedSuccess && (
        <div className="mb-6 p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/40 flex items-center gap-3 text-emerald-300 text-sm">
          <Check className="w-5 h-5 text-emerald-400" />
          <span>
            <strong>Review Published Successfully!</strong> Comments and summary report have been posted to GitHub PR #{prNumber}.
          </span>
        </div>
      )}

      {/* PR Scan Results */}
      {prScanResult && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-gray-900 border border-gray-800">
            <div>
              <h3 className="text-lg font-bold text-white">
                Findings for {prScanResult.filename}
              </h3>
              <p className="text-xs text-gray-400 mt-1">
                Detected {prScanResult.total_findings} issues ({prScanResult.summary.high} High,{" "}
                {prScanResult.summary.medium} Medium, {prScanResult.summary.low} Low)
              </p>
            </div>

            <button
              onClick={handlePublishReview}
              disabled={loading || publishedSuccess}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition shadow-lg shadow-emerald-600/20 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              Approve & Publish PR Review
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {prScanResult.findings.map((f) => (
              <FindingCard key={f.id} finding={f} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
