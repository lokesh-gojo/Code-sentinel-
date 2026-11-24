from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.core.auth import get_current_user_id
from app.models.schemas import (
    SnippetScanRequest,
    ScanResponse,
    FindingSummary,
    Finding,
)
from app.services.analyzer import analyzer_service
from app.services.ai_reviewer import ai_reviewer_service
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/api/scans", tags=["Scans"])

# In-memory storage cache for local development / testing fallback
IN_MEMORY_SCANS = {}


@router.post("/snippet", response_model=ScanResponse)
def scan_code_snippet(
    payload: SnippetScanRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Analyzes submitted code snippet via Ruff, Bandit, ESLint, and Semgrep.
    Strictly isolated: runs only static AST analysis and never executes code.
    """
    findings = analyzer_service.analyze_snippet(
        code=payload.code,
        filename=payload.filename,
        language=payload.language,
    )

    # If AI explanation is requested, generate plain-English insights
    if payload.include_ai and findings:
        patch_info = ai_reviewer_service.generate_fix_and_test(
            code=payload.code,
            filename=payload.filename,
            findings=findings,
        )
        for f in findings:
            f.ai_explanation = patch_info.explanation
            f.suggested_fix = patch_info.suggested_patch
            f.regression_test = patch_info.regression_test

    summary = FindingSummary(
        high=sum(1 for f in findings if f.severity == "high"),
        medium=sum(1 for f in findings if f.severity == "medium"),
        low=sum(1 for f in findings if f.severity == "low"),
        info=sum(1 for f in findings if f.severity == "info"),
    )

    scan_id = str(uuid.uuid4())
    resp = ScanResponse(
        id=scan_id,
        filename=payload.filename,
        language=payload.language,
        total_findings=len(findings),
        summary=summary,
        findings=findings,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    IN_MEMORY_SCANS[scan_id] = resp
    return resp


@router.post("/upload", response_model=ScanResponse)
async def scan_file_upload(
    file: UploadFile = File(...),
    language: str = Form("python"),
    include_ai: bool = Form(False),
    user_id: str = Depends(get_current_user_id),
):
    """Scans an uploaded single code file."""
    content = await file.read()
    code = content.decode("utf-8", errors="ignore")

    payload = SnippetScanRequest(
        filename=file.filename or "uploaded_file.py",
        language=language if language in ("python", "javascript", "typescript") else "python",  # type: ignore
        code=code,
        include_ai=include_ai,
    )
    return scan_code_snippet(payload, user_id=user_id)


@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan_by_id(
    scan_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Retrieves an existing scan and findings."""
    scan = IN_MEMORY_SCANS.get(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("", response_model=List[ScanResponse])
def list_scans(
    user_id: str = Depends(get_current_user_id),
):
    """Lists all scans recorded in the system."""
    return list(IN_MEMORY_SCANS.values())
