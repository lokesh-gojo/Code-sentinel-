from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


SeverityLevel = Literal["high", "medium", "low", "info"]
ScanLanguage = Literal["python", "javascript", "typescript"]
SourceType = Literal["snippet", "upload", "github_pr", "agent_run"]
FindingStatus = Literal["open", "fixed", "dismissed", "applied"]


class SnippetScanRequest(BaseModel):
    filename: str = Field(default="main.py", max_length=100)
    language: ScanLanguage = "python"
    code: str = Field(..., min_length=1, max_length=500_000)
    include_ai: bool = False
    run_agent: bool = False


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool: str
    rule_id: str
    severity: SeverityLevel
    category: str
    file_path: str
    line_number: int
    message: str
    ai_explanation: Optional[str] = None
    suggested_fix: Optional[str] = None
    regression_test: Optional[str] = None
    status: FindingStatus = "open"


class FindingSummary(BaseModel):
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class ScanResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = "main.py"
    language: str
    total_findings: int
    summary: FindingSummary
    findings: List[Finding]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AgentStartRequest(BaseModel):
    filename: str = Field(default="main.py", max_length=100)
    language: ScanLanguage = "python"
    code: str = Field(..., min_length=1, max_length=500_000)
    repo_full_name: Optional[str] = None
    pr_number: Optional[int] = None


class AgentDecisionRequest(BaseModel):
    thread_id: str
    approved: bool
    feedback: Optional[str] = None


class AgentStepProposal(BaseModel):
    tool: str
    reason: str
    proposed_patch: str
    regression_test: str
    test_passed: bool
    retry_count: int
    findings_addressed: List[str]


class AgentRunStatusResponse(BaseModel):
    status: Literal["active", "awaiting_approval", "completed", "failed", "rejected"]
    thread_id: str
    proposal: Optional[Dict[str, Any]] = None
    findings: List[Finding] = []
    final_code: Optional[str] = None
    message: Optional[str] = None


class GitHubPRScanRequest(BaseModel):
    repo: str = Field(..., description="owner/repo_name format")
    pr_number: int


class PRComment(BaseModel):
    path: str
    line: int
    body: str


class GitHubPRPublishRequest(BaseModel):
    repo: str
    pr_number: int
    body: str
    comments: List[PRComment] = []


class MetricsOverview(BaseModel):
    total_scans: int
    total_findings: int
    fixed_findings: int
    high_severity: int
    medium_severity: int
    low_severity: int
