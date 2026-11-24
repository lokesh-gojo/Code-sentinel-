from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body
from pydantic import BaseModel
from app.core.auth import get_current_user_id
from app.services.repo_intelligence import repo_intelligence_service, RepositoryArchitectureReport
from app.services.quality_scorer import quality_scorer_service, QualityScoreReport
from app.services.project_memory import project_memory_service, MemoryRecord
from app.services.analyzer import analyzer_service
from app.services.ai_reviewer import ai_reviewer_service
from app.services.regression_risk import regression_risk_predictor, RegressionRiskReport
from app.services.supply_chain import supply_chain_service, CycloneDXSBOMReport
from app.services.policy_engine import policy_engine_service, PolicyEvaluationResult, CodeReviewPolicy
from app.services.architecture_reviewer import architecture_reviewer_service, ArchitectureReviewReport
from app.services.ci_investigator import ci_investigator_service, CIFailureDiagnosis
from benchmarks.benchmark_evaluator import benchmark_evaluator, EmpiricalEvaluationReport
import os

router = APIRouter(prefix="/api/intelligence", tags=["Intelligence"])


class ChatInquiryRequest(BaseModel):
    message: str
    repo_name: str = "default"
    provider: str = "auto"


class ChatInquiryResponse(BaseModel):
    reply: str
    provider_used: str


class AddMemoryRequest(BaseModel):
    repo_name: str = "default"
    memory_type: str = "convention"
    title: str
    description: str


class RegressionRiskRequest(BaseModel):
    changed_files: List[str]


class CIInvestigateRequest(BaseModel):
    log_text: str


@router.get("/repo", response_model=RepositoryArchitectureReport)
def get_repository_intelligence(
    path: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
):
    scan_target = path or os.getcwd()
    return repo_intelligence_service.scan_repository(scan_target)


@router.get("/quality-score", response_model=QualityScoreReport)
def get_quality_score(
    code: Optional[str] = Query(None),
    filename: str = Query("main.py"),
    user_id: str = Depends(get_current_user_id),
):
    sample_code = code or "def divide(a, b):\n    return a / b\n"
    findings = analyzer_service.analyze_snippet(sample_code, filename=filename)
    return quality_scorer_service.calculate_score(findings, total_lines=len(sample_code.splitlines()))


@router.get("/memory", response_model=List[MemoryRecord])
def get_project_memory(
    repo: str = Query("default"),
    user_id: str = Depends(get_current_user_id),
):
    return project_memory_service.get_records(repo)


@router.post("/memory", response_model=MemoryRecord)
def add_project_memory(
    payload: AddMemoryRequest,
    user_id: str = Depends(get_current_user_id),
):
    return project_memory_service.add_record(
        repo=payload.repo_name,
        memory_type=payload.memory_type,
        title=payload.title,
        description=payload.description,
    )


@router.post("/assistant/chat", response_model=ChatInquiryResponse)
def developer_assistant_chat(
    payload: ChatInquiryRequest,
    user_id: str = Depends(get_current_user_id),
):
    repo_context = project_memory_service.format_context_for_prompt(payload.repo_name)
    reply = ai_reviewer_service.chat_assist(
        prompt=payload.message,
        repo_context=repo_context,
        provider_preference=payload.provider,
    )
    return ChatInquiryResponse(
        reply=reply,
        provider_used=payload.provider,
    )


# -------------------------------------------------------------
# v3.0 New Feature Endpoints
# -------------------------------------------------------------

@router.post("/regression-risk", response_model=RegressionRiskReport)
def evaluate_regression_risk(
    payload: RegressionRiskRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Feature 13: Predicts blast-radius and regression risk of code changes."""
    return regression_risk_predictor.predict_risk(payload.changed_files)


@router.get("/architecture-review", response_model=ArchitectureReviewReport)
def get_architecture_review(
    user_id: str = Depends(get_current_user_id),
):
    """Feature 14: AI Architecture Reviewer auditing technical debt and modularity."""
    return architecture_reviewer_service.review_architecture()


@router.get("/sbom", response_model=CycloneDXSBOMReport)
def get_cyclonedx_sbom(
    user_id: str = Depends(get_current_user_id),
):
    """Feature 16: Software Supply Chain Security & CycloneDX v1.5 SBOM Generator."""
    req_path = os.path.join(os.getcwd(), "backend", "requirements.txt")
    req_content = ""
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            req_content = f.read()
    else:
        req_content = "fastapi>=0.110.0\npydantic>=2.7.0\npytest>=8.0.0\n"

    return supply_chain_service.generate_cyclonedx_sbom(req_content)


@router.post("/ci-investigate", response_model=CIFailureDiagnosis)
def investigate_ci_failure(
    payload: CIInvestigateRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Feature 17: AI Test Failure Investigator parsing CI build traces."""
    return ci_investigator_service.investigate_log(payload.log_text)


@router.post("/policy-evaluate", response_model=PolicyEvaluationResult)
def evaluate_review_policy(
    policy: CodeReviewPolicy = Body(...),
    user_id: str = Depends(get_current_user_id),
):
    """Feature 18: Intelligent Code Review Policy Engine."""
    sample_code = "def divide(a, b):\n    return a / b\n"
    findings = analyzer_service.analyze_snippet(sample_code, filename="main.py")
    quality = quality_scorer_service.calculate_score(findings).overall
    return policy_engine_service.evaluate_policy(findings=findings, quality_score=quality, policy=policy)


@router.get("/benchmark", response_model=EmpiricalEvaluationReport)
def run_ground_truth_benchmarks(
    user_id: str = Depends(get_current_user_id),
):
    """Evaluates Code Sentinel AI against ground-truth defect fixtures."""
    return benchmark_evaluator.run_benchmark()
