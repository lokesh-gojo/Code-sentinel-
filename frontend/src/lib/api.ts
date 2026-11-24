import {
  ScanResponse,
  AgentRunStatus,
  GitHubRepo,
  RepositoryArchitectureReport,
  QualityScoreReport,
  MemoryRecord,
  CycloneDXSBOMReport,
  CodeReviewPolicy,
  PolicyEvaluationResult,
  EmpiricalEvaluationReport,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const headers = {
    "Content-Type": "application/json",
    Authorization: "Bearer dev-token",
    ...(options.headers || {}),
  };

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error [${res.status}]: ${errorText}`);
  }

  return res.json();
}

export const api = {
  checkHealth: async () => {
    return fetchWithAuth("/health");
  },

  scanSnippet: async (
    code: string,
    filename: string = "main.py",
    language: string = "python",
    includeAi: boolean = false
  ): Promise<ScanResponse> => {
    return fetchWithAuth("/api/scans/snippet", {
      method: "POST",
      body: JSON.stringify({ code, filename, language, include_ai: includeAi }),
    });
  },

  startAgent: async (code: string, filename: string = "main.py", language: string = "python"): Promise<AgentRunStatus> => {
    return fetchWithAuth("/api/agent/start", {
      method: "POST",
      body: JSON.stringify({ code, filename, language }),
    });
  },

  resumeAgent: async (
    threadId: string,
    approved: boolean,
    feedback?: string,
    approvalToken?: string
  ): Promise<AgentRunStatus> => {
    return fetchWithAuth("/api/agent/resume", {
      method: "POST",
      body: JSON.stringify({
        thread_id: threadId,
        approved,
        feedback,
        approval_token: approvalToken,
      }),
    });
  },

  listScans: async (): Promise<ScanResponse[]> => {
    return fetchWithAuth("/api/scans");
  },

  listRepos: async (): Promise<GitHubRepo[]> => {
    return fetchWithAuth("/api/github/repos");
  },

  scanPR: async (repo: string, prNumber: number): Promise<ScanResponse> => {
    return fetchWithAuth("/api/github/pr/scan", {
      method: "POST",
      body: JSON.stringify({ repo, pr_number: prNumber }),
    });
  },

  publishPRReview: async (repo: string, prNumber: number, body: string) => {
    return fetchWithAuth("/api/github/pr/publish", {
      method: "POST",
      body: JSON.stringify({ repo, pr_number: prNumber, body }),
    });
  },

  getRepoIntelligence: async (path?: string): Promise<RepositoryArchitectureReport> => {
    const query = path ? `?path=${encodeURIComponent(path)}` : "";
    return fetchWithAuth(`/api/intelligence/repo${query}`);
  },

  getQualityScore: async (code?: string, filename?: string): Promise<QualityScoreReport> => {
    const params = new URLSearchParams();
    if (code) params.set("code", code);
    if (filename) params.set("filename", filename);
    return fetchWithAuth(`/api/intelligence/quality-score?${params.toString()}`);
  },

  getMemory: async (repo: string = "default"): Promise<MemoryRecord[]> => {
    return fetchWithAuth(`/api/intelligence/memory?repo=${encodeURIComponent(repo)}`);
  },

  addMemory: async (repo: string, memoryType: string, title: string, description: string): Promise<MemoryRecord> => {
    return fetchWithAuth("/api/intelligence/memory", {
      method: "POST",
      body: JSON.stringify({ repo_name: repo, memory_type: memoryType, title, description }),
    });
  },

  chatAssistant: async (message: string, repoName: string = "default", provider: string = "auto") => {
    return fetchWithAuth("/api/intelligence/assistant/chat", {
      method: "POST",
      body: JSON.stringify({ message, repo_name: repoName, provider }),
    });
  },

  getSBOM: async (): Promise<CycloneDXSBOMReport> => {
    return fetchWithAuth("/api/intelligence/sbom");
  },

  evaluatePolicy: async (policy: CodeReviewPolicy): Promise<PolicyEvaluationResult> => {
    return fetchWithAuth("/api/intelligence/policy-evaluate", {
      method: "POST",
      body: JSON.stringify(policy),
    });
  },

  runBenchmark: async (): Promise<EmpiricalEvaluationReport> => {
    return fetchWithAuth("/api/intelligence/benchmark");
  },
};
