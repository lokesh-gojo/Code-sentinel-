"use client";

import React, { useState, useRef } from "react";
import Editor, { OnMount } from "@monaco-editor/react";
import { api } from "@/lib/api";
import { Finding, ScanResponse, AgentRunStatus } from "@/lib/types";
import { FindingCard } from "@/components/FindingCard";
import { DiffViewer } from "@/components/DiffViewer";
import { Play, Sparkles, RefreshCw, Upload, ShieldCheck, CheckCircle2 } from "lucide-react";

const SAMPLE_BUGGY_PYTHON = `def divide(a, b):
    # Potential ZeroDivisionError if b is 0
    return a / b

def append_item(val, items=[]):
    # Mutable default argument bug
    items.append(val)
    return items

# Calling divide with zero
print(divide(10, 0))
`;

const SAMPLE_SECURITY_CODE = `import sqlite3

# Security Risk: Hardcoded API secret
API_SECRET_KEY = "SUPER_SECRET_PRODUCTION_KEY_12345"

def query_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # SQL Injection pattern
    query = f"SELECT * FROM users WHERE name = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()
`;

export default function ScanPage() {
  const [code, setCode] = useState(SAMPLE_BUGGY_PYTHON);
  const [filename, setFilename] = useState("main.py");
  const [language, setLanguage] = useState<"python" | "javascript" | "typescript">("python");
  const [loading, setLoading] = useState(false);
  const [agentRunning, setAgentRunning] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const [agentStatus, setAgentStatus] = useState<AgentRunStatus | null>(null);
  const [selectedLine, setSelectedLine] = useState<number | null>(null);
  const [appliedSuccess, setAppliedSuccess] = useState(false);

  const editorRef = useRef<any>(null);

  const handleEditorDidMount: OnMount = (editor) => {
    editorRef.current = editor;
  };

  const jumpToLine = (lineNumber: number) => {
    setSelectedLine(lineNumber);
    if (editorRef.current) {
      editorRef.current.revealLineInCenter(lineNumber);
      editorRef.current.setPosition({ lineNumber, column: 1 });
      editorRef.current.focus();
    }
  };

  const handleRunStaticScan = async () => {
    setLoading(true);
    setScanResult(null);
    setAppliedSuccess(false);
    try {
      const res = await api.scanSnippet(code, filename, language, true);
      setScanResult(res);
      if (res.findings.length > 0) {
        jumpToLine(res.findings[0].line_number);
      }
    } catch (err: any) {
      alert(`Scan failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAgentLoop = async () => {
    setAgentRunning(true);
    setAgentStatus(null);
    setAppliedSuccess(false);
    try {
      const res = await api.startAgent(code, filename, language);
      setAgentStatus(res);
      if (res.findings.length > 0) {
        setScanResult({
          id: res.thread_id,
          filename,
          language,
          total_findings: res.findings.length,
          summary: {
            high: res.findings.filter((f) => f.severity === "high").length,
            medium: res.findings.filter((f) => f.severity === "medium").length,
            low: res.findings.filter((f) => f.severity === "low").length,
            info: res.findings.filter((f) => f.severity === "info").length,
          },
          findings: res.findings,
          created_at: new Date().toISOString(),
        });
      }
    } catch (err: any) {
      alert(`Agent run failed: ${err.message}`);
    } finally {
      setAgentRunning(false);
    }
  };

  const handleApprovePatch = async () => {
    if (!agentStatus?.thread_id) return;
    setLoading(true);
    try {
      const res = await api.resumeAgent(agentStatus.thread_id, true);
      if (res.final_code) {
        setCode(res.final_code);
        setAppliedSuccess(true);
      }
      setAgentStatus(null);
      // Refresh scan on the corrected code
      const updatedScan = await api.scanSnippet(res.final_code || code, filename, language, false);
      setScanResult(updatedScan);
    } catch (err: any) {
      alert(`Approval error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRejectPatch = async () => {
    if (!agentStatus?.thread_id) return;
    setLoading(true);
    try {
      await api.resumeAgent(agentStatus.thread_id, false, "Patch rejected by developer.");
      setAgentStatus(null);
    } catch (err: any) {
      alert(`Rejection error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-indigo-400" />
            Code Review Workbench
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Run multi-engine static scanning or initiate self-correcting LangGraph agent remediation.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <select
            value={filename}
            onChange={(e) => {
              const val = e.target.value;
              setFilename(val);
              if (val === "math_utils.py") {
                setCode(SAMPLE_BUGGY_PYTHON);
                setLanguage("python");
              } else if (val === "security_db.py") {
                setCode(SAMPLE_SECURITY_CODE);
                setLanguage("python");
              }
            }}
            className="bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg px-3 py-2 font-mono"
          >
            <option value="math_utils.py">Preset: Buggy Math (ZeroDivision)</option>
            <option value="security_db.py">Preset: Security Vulnerability (SQL/Creds)</option>
          </select>

          <button
            onClick={handleRunStaticScan}
            disabled={loading || agentRunning}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold border border-gray-700 transition disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            Run Static Review
          </button>

          <button
            onClick={handleRunAgentLoop}
            disabled={loading || agentRunning}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
          >
            {agentRunning ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            Launch AI Agent Loop
          </button>
        </div>
      </div>

      {/* Applied Patch Banner */}
      {appliedSuccess && (
        <div className="mb-6 p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/40 flex items-center gap-3 text-emerald-300 text-sm">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <span>
            <strong>Patch Approved & Applied!</strong> The corrected code has been loaded into Monaco Editor and validated.
          </span>
        </div>
      )}

      {/* Agent Human Approval Modal / Diff Viewer */}
      {agentStatus?.status === "awaiting_approval" && agentStatus.proposal && (
        <div className="mb-8">
          <DiffViewer
            originalCode={code}
            patchedCode={agentStatus.proposal.proposed_patch || code}
            regressionTest={agentStatus.proposal.regression_test}
            explanation={agentStatus.proposal.explanation}
            onApprove={handleApprovePatch}
            onReject={handleRejectPatch}
            isSubmitting={loading}
          />
        </div>
      )}

      {/* Editor & Findings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Monaco Code Editor */}
        <div className="lg:col-span-7 bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="px-4 py-2.5 bg-gray-950/80 border-b border-gray-800 flex items-center justify-between">
            <span className="text-xs font-mono text-gray-400">{filename}</span>
            <span className="text-xs font-mono text-indigo-400 uppercase">{language}</span>
          </div>
          <div className="h-[580px]">
            <Editor
              height="100%"
              theme="vs-dark"
              language={language}
              value={code}
              onChange={(val) => setCode(val || "")}
              onMount={handleEditorDidMount}
              options={{
                fontSize: 13,
                minimap: { enabled: false },
                lineNumbers: "on",
                scrollBeyondLastLine: false,
                wordWrap: "on",
              }}
            />
          </div>
        </div>

        {/* Right: Findings & Diagnostics Panel */}
        <div className="lg:col-span-5 flex flex-col h-[620px]">
          <div className="bg-gray-900 border border-gray-800 rounded-2xl flex-1 flex flex-col overflow-hidden shadow-xl">
            <div className="px-5 py-3.5 bg-gray-950/80 border-b border-gray-800 flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>Diagnostics & Findings</span>
                {scanResult && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-mono">
                    {scanResult.total_findings}
                  </span>
                )}
              </h3>
              {scanResult && (
                <div className="flex items-center gap-2 text-xs font-mono">
                  <span className="text-red-400 font-semibold">{scanResult.summary.high} High</span>
                  <span className="text-amber-400 font-semibold">{scanResult.summary.medium} Med</span>
                  <span className="text-blue-400 font-semibold">{scanResult.summary.low} Low</span>
                </div>
              )}
            </div>

            <div className="flex-1 p-4 overflow-y-auto space-y-3">
              {!scanResult ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-6 text-gray-500">
                  <Play className="w-8 h-8 mb-2 text-gray-600" />
                  <p className="text-sm">Click &quot;Run Static Review&quot; or &quot;Launch AI Agent Loop&quot; to inspect code.</p>
                </div>
              ) : scanResult.findings.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-6 text-emerald-400">
                  <CheckCircle2 className="w-10 h-10 mb-2" />
                  <p className="font-semibold text-sm">No issues detected!</p>
                  <p className="text-xs text-gray-400 mt-1">Code conforms to static analysis rules and security constraints.</p>
                </div>
              ) : (
                scanResult.findings.map((f) => (
                  <FindingCard
                    key={f.id}
                    finding={f}
                    onSelectLine={jumpToLine}
                    isSelected={selectedLine === f.line_number}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
