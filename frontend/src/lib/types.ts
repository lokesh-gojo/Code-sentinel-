export type SeverityLevel = "high" | "medium" | "low" | "info";
export type ScanLanguage = "python" | "javascript" | "typescript";

export interface Finding {
  id: string;
  tool: string;
  rule_id: string;
  severity: SeverityLevel;
  category: string;
  file_path: string;
  line_number: number;
  message: string;
  root_cause?: string | null;
  confidence?: number;
  ai_explanation?: string | null;
  suggested_fix?: string | null;
  regression_test?: string | null;
  status: "open" | "fixed" | "dismissed" | "applied";
}

export interface FindingSummary {
  high: number;
  medium: number;
  low: number;
  info: number;
}

export interface ScanResponse {
  id: string;
  filename: string;
  language: string;
  total_findings: number;
  summary: FindingSummary;
  findings: Finding[];
  created_at: string;
}

export interface AgentProposal {
  target_file?: string;
  explanation?: string;
  root_cause?: string;
  proposed_patch?: string;
  regression_test?: string;
  test_passed?: boolean;
  test_output?: string;
  retry_count?: number;
  confidence?: number;
  total_findings?: number;
  approval_token?: string;
}

export interface AgentRunStatus {
  status: "active" | "awaiting_approval" | "completed" | "failed" | "rejected";
  thread_id: string;
  proposal?: AgentProposal;
  findings: Finding[];
  final_code?: string;
  message?: string;
}

export interface GitHubRepo {
  id: number;
  name: string;
  full_name: string;
  default_branch: string;
}

export interface DependencyNode {
  id: string;
  label: string;
  type: string;
  language: string;
  lines_of_code: number;
  functions: string[];
  classes: string[];
}

export interface DependencyEdge {
  source: string;
  target: string;
  relation: string;
}

export interface RepositoryArchitectureReport {
  total_files: number;
  languages_detected: Record<string, number>;
  frameworks_detected: string[];
  nodes: DependencyNode[];
  edges: DependencyEdge[];
  circular_dependencies: string[][];
  unused_functions: string[];
  duplicated_blocks_count: number;
  architecture_summary: string;
}

export interface QualityScoreReport {
  overall: number;
  code_quality: number;
  security: number;
  performance: number;
  test_coverage: number;
  maintainability: number;
  assessment: string;
}

export interface MemoryRecord {
  id: string;
  repo_full_name: string;
  memory_type: "convention" | "decision" | "approved_patch" | "framework_pattern";
  title: string;
  description: string;
  created_at: string;
}

export interface SBOMComponent {
  name: string;
  version: string;
  purl: string;
  license: string;
  is_vulnerable: boolean;
  cve_id: string;
  recommendation: string;
}

export interface CycloneDXSBOMReport {
  bom_format: string;
  spec_version: string;
  serial_number: string;
  timestamp: string;
  components: SBOMComponent[];
  total_components: number;
  vulnerable_components: number;
  licenses_summary: Record<string, number>;
}

export interface CodeReviewPolicy {
  block_critical_vulnerabilities: boolean;
  block_high_severity: boolean;
  block_hardcoded_secrets: boolean;
  minimum_quality_score: number;
  require_human_approval: boolean;
  allow_auto_merge: boolean;
  max_cyclomatic_complexity: number;
}

export interface PolicyEvaluationResult {
  passed: boolean;
  violations: string[];
  enforced_rules: string[];
  merge_status: "BLOCKED" | "APPROVED" | "REQUIRES_REVIEW";
}

export interface CaseBenchmarkResult {
  case_id: string;
  name: string;
  detected_rule_ids: string[];
  expected_rule_ids: string[];
  true_positive: boolean;
  false_positive: boolean;
  false_negative: boolean;
  patch_verified_in_sandbox: boolean;
  latency_ms: number;
}

export interface EmpiricalEvaluationReport {
  total_benchmark_cases: number;
  true_positives: number;
  false_positives: number;
  false_negatives: number;
  true_negatives: number;
  precision: number;
  recall: number;
  f1_score: number;
  false_positive_rate: number;
  patch_sandbox_pass_rate: number;
  average_latency_ms: number;
  cost_per_scan_usd: number;
  case_results: CaseBenchmarkResult[];
}
