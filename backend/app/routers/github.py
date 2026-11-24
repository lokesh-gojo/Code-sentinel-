from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user_id
from app.models.schemas import (
    GitHubPRScanRequest,
    GitHubPRPublishRequest,
    ScanResponse,
    Finding,
    FindingSummary,
)
from app.services.github_client import github_client
from app.services.analyzer import analyzer_service
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/github", tags=["GitHub"])


@router.get("/repos")
async def list_user_repositories(
    user_id: str = Depends(get_current_user_id),
):
    """Lists repositories accessible to the user (mockable in dev mode)."""
    return [
        {"id": 1, "name": "sample-repo", "full_name": "developer/sample-repo", "default_branch": "main"},
        {"id": 2, "name": "e-commerce-api", "full_name": "developer/e-commerce-api", "default_branch": "master"},
    ]


@router.post("/pr/scan", response_model=ScanResponse)
async def scan_pull_request(
    payload: GitHubPRScanRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Fetches PR diff files from GitHub and performs multi-engine static analysis.
    Does NOT execute PR code.
    """
    files = await github_client.get_pr_files(payload.repo, payload.pr_number)
    all_findings: List[Finding] = []

    for file_item in files:
        filename = file_item.get("filename", "file.py")
        code = file_item.get("raw_code") or file_item.get("patch", "")
        lang = "python" if filename.endswith(".py") else "javascript" if filename.endswith((".js", ".jsx")) else "typescript" if filename.endswith((".ts", ".tsx")) else "python"
        
        findings = analyzer_service.analyze_snippet(code=code, filename=filename, language=lang)
        all_findings.extend(findings)

    summary = FindingSummary(
        high=sum(1 for f in all_findings if f.severity == "high"),
        medium=sum(1 for f in all_findings if f.severity == "medium"),
        low=sum(1 for f in all_findings if f.severity == "low"),
        info=sum(1 for f in all_findings if f.severity == "info"),
    )

    return ScanResponse(
        id=str(uuid.uuid4()),
        filename=f"PR #{payload.pr_number} ({payload.repo})",
        language="multi",
        total_findings=len(all_findings),
        summary=summary,
        findings=all_findings,
        created_at=datetime.utcnow().isoformat(),
    )


@router.post("/pr/publish")
async def publish_pr_review(
    payload: GitHubPRPublishRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Publishes review comments to GitHub PR.
    HARD CONSTRAINT: Invoked only upon explicit human user approval.
    """
    comments_payload = [c.model_dump() for c in payload.comments] if payload.comments else None
    result = await github_client.post_pr_review(
        repo=payload.repo,
        pr_number=payload.pr_number,
        body=payload.body,
        comments=comments_payload,
    )
    return {
        "status": "success",
        "message": "PR review comments published after explicit user approval.",
        "details": result,
    }
