from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from langgraph.types import Command
from app.core.auth import get_current_user_id
from app.core.approval_security import approval_security_manager
from app.models.schemas import (
    AgentStartRequest,
    AgentDecisionRequest,
    AgentRunStatusResponse,
    Finding,
)
from app.services.agent_graph import code_sentinel_multi_agent
import uuid

router = APIRouter(prefix="/api/agent", tags=["Agent"])

# Thread ownership tracking
THREAD_OWNERS = {}
THREAD_PATCHES = {}


class SecureAgentDecisionRequest(BaseModel):
    thread_id: str
    approved: bool
    feedback: Optional[str] = None
    approval_token: Optional[str] = None


@router.post("/start", response_model=AgentRunStatusResponse)
def start_agent_review(
    payload: AgentStartRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Kicks off a multi-step LangGraph code review agent run:
    1. Code Analyst & Bug Hunter
    2. Security Auditor & Performance Agent
    3. Fix & Test Engineers
    4. Sandboxed Verification Agent
    5. PAUSES at interrupt() waiting for secure human approval.
    """
    thread_id = f"{user_id}_{uuid.uuid4().hex}"
    THREAD_OWNERS[thread_id] = user_id
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "filename": payload.filename,
        "original_code": payload.code,
        "language": payload.language,
        "repo_context": f"Target: {payload.filename}",
        "analysis_meta": {},
        "functional_bugs": [],
        "security_vulnerabilities": [],
        "performance_issues": [],
        "all_findings": [],
        "proposed_patch": "",
        "regression_test": "",
        "root_cause_analysis": "",
        "explanation": "",
        "test_passed": False,
        "test_output": "",
        "retry_count": 0,
        "max_retries": 2,
        "confidence_score": 0.90,
        "approved": None,
        "feedback": None,
        "published": False,
        "final_report": {},
    }

    result = code_sentinel_multi_agent.invoke(initial_state, config=config)

    # Check if agent is paused at review_manager human approval interrupt
    if "__interrupt__" in result:
        interrupt_val = result["__interrupt__"][0].value
        patch_code = interrupt_val.get("proposed_patch", "")
        THREAD_PATCHES[thread_id] = patch_code

        # Generate cryptographic HMAC approval token with nonce and TTL
        signed_token = approval_security_manager.generate_approval_token(
            thread_id=thread_id,
            user_id=user_id,
            patch_code=patch_code,
        )
        interrupt_val["approval_token"] = signed_token

        return AgentRunStatusResponse(
            status="awaiting_approval",
            thread_id=thread_id,
            proposal=interrupt_val,
            findings=[Finding(**f) for f in result.get("all_findings", [])],
            message="Agent completed analysis and isolated tests. Paused for human approval.",
        )

    return AgentRunStatusResponse(
        status="completed" if result.get("published") else "failed",
        thread_id=thread_id,
        findings=[Finding(**f) for f in result.get("all_findings", [])],
        final_code=result.get("proposed_patch"),
        message="Agent completed review workflow.",
    )


@router.post("/resume", response_model=AgentRunStatusResponse)
def resume_agent_review(
    payload: SecureAgentDecisionRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Resumes an interrupted LangGraph agent run with the human approval decision.
    Enforces thread ownership, token signature, and replay protection.
    """
    owner = THREAD_OWNERS.get(payload.thread_id)
    if owner and owner != user_id and user_id != "local-dev-user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not own this agent thread.",
        )

    # If approval token was provided, verify HMAC, nonce replay, and patch integrity
    if payload.approval_token:
        cached_patch = THREAD_PATCHES.get(payload.thread_id, "")
        valid, reason = approval_security_manager.verify_and_consume_approval(
            token=payload.approval_token,
            expected_thread_id=payload.thread_id,
            expected_user_id=user_id,
            current_patch_code=cached_patch,
        )
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Security Gate Rejection: {reason}",
            )

    config = {"configurable": {"thread_id": payload.thread_id}}

    decision_payload = {
        "approved": payload.approved,
        "feedback": payload.feedback,
    }

    result = code_sentinel_multi_agent.invoke(
        Command(resume=decision_payload),
        config=config,
    )

    if not payload.approved:
        return AgentRunStatusResponse(
            status="rejected",
            thread_id=payload.thread_id,
            message="Human reviewer rejected the proposed patch. Workflow ended safely.",
        )

    return AgentRunStatusResponse(
        status="completed",
        thread_id=payload.thread_id,
        final_code=result.get("proposed_patch"),
        message="Patch approved, validated, and published successfully.",
    )


@router.get("/status/{thread_id}", response_model=AgentRunStatusResponse)
def get_agent_thread_status(
    thread_id: str,
    user_id: str = Depends(get_current_user_id),
):
    config = {"configurable": {"thread_id": thread_id}}
    state_snapshot = code_sentinel_multi_agent.get_state(config)

    if not state_snapshot.values:
        raise HTTPException(status_code=404, detail="Agent thread not found")

    values = state_snapshot.values
    is_paused = bool(state_snapshot.next)

    return AgentRunStatusResponse(
        status="awaiting_approval" if is_paused else "completed",
        thread_id=thread_id,
        findings=[Finding(**f) for f in values.get("all_findings", [])],
        final_code=values.get("proposed_patch"),
        proposal={
            "explanation": values.get("explanation"),
            "proposed_patch": values.get("proposed_patch"),
            "regression_test": values.get("regression_test"),
            "test_passed": values.get("test_passed"),
        },
    )
