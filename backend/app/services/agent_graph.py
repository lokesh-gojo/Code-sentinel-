from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from app.models.schemas import Finding
from app.services.analyzer import analyzer_service
from app.services.ai_reviewer import ai_reviewer_service
from app.services.sandbox import sandbox_service


class MultiAgentReviewState(TypedDict):
    """Shared state orchestrating specialized LangGraph agents."""
    filename: str
    original_code: str
    language: str
    repo_context: Optional[str]

    # Specialist Agent Outputs
    analysis_meta: Dict[str, Any]
    functional_bugs: List[Dict[str, Any]]
    security_vulnerabilities: List[Dict[str, Any]]
    performance_issues: List[Dict[str, Any]]
    all_findings: List[Dict[str, Any]]

    # Fix & Test Engineering
    proposed_patch: str
    regression_test: str
    root_cause_analysis: str
    explanation: str

    # Verification Agent
    test_passed: bool
    test_output: str
    retry_count: int
    max_retries: int
    confidence_score: float

    # Review Manager & Approval Gate
    approved: Optional[bool]
    feedback: Optional[str]
    published: bool
    final_report: Dict[str, Any]


# -------------------------------------------------------------
# Agent 1: Code Analyst Agent
# -------------------------------------------------------------
def code_analyst_agent(state: MultiAgentReviewState) -> Dict[str, Any]:
    lines = len(state["original_code"].splitlines())
    return {
        "analysis_meta": {
            "target": state["filename"],
            "language": state.get("language", "python"),
            "lines": lines,
            "complexity_level": "medium" if lines > 50 else "low",
        }
    }


# -------------------------------------------------------------
# Agent 2: Bug Hunter Agent
# -------------------------------------------------------------
def bug_hunter_agent(state: MultiAgentReviewState) -> Dict[str, Any]:
    # AST and lint analysis
    findings = analyzer_service.analyze_snippet(
        code=state["original_code"],
        filename=state["filename"],
        language=state.get("language", "python"),
    )
    # Filter functional bugs vs security
    functional = [f.model_dump() for f in findings if f.category in ("Potential Runtime Bug", "Code Quality & Bug Risk", "Syntax Bug")]
    return {"functional_bugs": functional}


# -------------------------------------------------------------
# Agent 3: Security Auditor Agent
# -------------------------------------------------------------
def security_agent(state: MultiAgentReviewState) -> Dict[str, Any]:
    findings = analyzer_service.analyze_snippet(
        code=state["original_code"],
        filename=state["filename"],
        language=state.get("language", "python"),
    )
    security = [f.model_dump() for f in findings if f.category in ("Security Vulnerability", "Pattern & Security Policy")]
    # Consolidate all findings
    all_f = state.get("functional_bugs", []) + security
    return {
        "security_vulnerabilities": security,
        "all_findings": all_f,
    }


# -------------------------------------------------------------
# Agent 4: Performance Optimization Agent
# -------------------------------------------------------------
def performance_agent(state: MultiAgentReviewState) -> Dict[str, Any]:
    code = state["original_code"]
    perf_findings = []
    # Heuristic for nested loops (O(n^2))
    if code.count("for ") >= 2 and ("for " in code and "\n    for " in code or "for " in code and "\n        for " in code):
        perf_findings.append({
            "tool": "perf-analyzer",
            "rule_id": "NESTED_LOOP_COMPLEXITY",
            "severity": "medium",
            "category": "Performance Bottleneck",
            "file_path": state["filename"],
            "line_number": 1,
            "message": "Nested loop detected: potential O(n^2) algorithmic complexity bottleneck.",
        })
    return {"performance_issues": perf_findings}


# -------------------------------------------------------------
# Agent 5 & 6: Fix Engineer & Test Engineer Agents
# -------------------------------------------------------------
def fix_and_test_engineers(state: MultiAgentReviewState) -> Dict[str, Any]:
    all_findings_objs = [Finding(**f) for f in state.get("all_findings", [])]
    last_error = state.get("test_output") if not state.get("test_passed", True) else None

    patch_output = ai_reviewer_service.generate_fix_and_test(
        code=state.get("proposed_patch") or state["original_code"],
        filename=state["filename"],
        findings=all_findings_objs,
        previous_error=last_error,
        project_context=state.get("repo_context"),
    )

    return {
        "proposed_patch": patch_output.suggested_patch,
        "regression_test": patch_output.regression_test,
        "root_cause_analysis": patch_output.root_cause,
        "explanation": patch_output.explanation,
        "confidence_score": patch_output.confidence,
    }


# -------------------------------------------------------------
# Agent 7: Verification Agent (Sandbox Execution)
# -------------------------------------------------------------
def verification_agent(state: MultiAgentReviewState) -> Dict[str, Any]:
    passed, output = sandbox_service.run_test(
        patched_code=state["proposed_patch"],
        regression_test=state["regression_test"],
        filename=state["filename"],
    )
    new_retry_count = state.get("retry_count", 0) + (0 if passed else 1)
    # Calibrate confidence based on real sandbox test execution
    calibrated_confidence = 0.98 if passed else max(0.40, state.get("confidence_score", 0.8) - 0.25)

    return {
        "test_passed": passed,
        "test_output": output,
        "retry_count": new_retry_count,
        "confidence_score": calibrated_confidence,
    }


def should_retry_or_proceed(state: MultiAgentReviewState) -> str:
    """Conditional Edge: Retry up to max_retries or proceed to approval."""
    if state["test_passed"]:
        return "review_manager"
    if state.get("retry_count", 0) < state.get("max_retries", 2):
        return "fix_and_test_engineers"
    return "review_manager"


# -------------------------------------------------------------
# Agent 8: Review Manager Agent (Human Approval Gate)
# -------------------------------------------------------------
def review_manager_agent(state: MultiAgentReviewState) -> Dict[str, Any]:
    proposal = {
        "target_file": state["filename"],
        "explanation": state.get("explanation"),
        "root_cause": state.get("root_cause_analysis"),
        "proposed_patch": state.get("proposed_patch"),
        "regression_test": state.get("regression_test"),
        "test_passed": state.get("test_passed"),
        "test_output": state.get("test_output"),
        "retry_count": state.get("retry_count"),
        "confidence": state.get("confidence_score"),
        "total_findings": len(state.get("all_findings", [])),
    }

    # PAUSE EXECUTION: Hard human-in-the-loop constraint
    decision = interrupt(proposal)

    approved = decision.get("approved", False) if isinstance(decision, dict) else bool(decision)
    feedback = decision.get("feedback") if isinstance(decision, dict) else None

    report = {
        "status": "approved" if approved else "rejected",
        "feedback": feedback,
        "verified_by_sandbox": state.get("test_passed"),
    }

    return {
        "approved": approved,
        "feedback": feedback,
        "final_report": report,
    }


def check_approval_decision(state: MultiAgentReviewState) -> str:
    if state.get("approved"):
        return "publish_verified_review"
    return END


def publish_verified_review(state: MultiAgentReviewState) -> Dict[str, Any]:
    return {"published": True}


# Construct Multi-Agent StateGraph
agent_builder = StateGraph(MultiAgentReviewState)

agent_builder.add_node("code_analyst", code_analyst_agent)
agent_builder.add_node("bug_hunter", bug_hunter_agent)
agent_builder.add_node("security_auditor", security_agent)
agent_builder.add_node("performance_agent", performance_agent)
agent_builder.add_node("fix_and_test_engineers", fix_and_test_engineers)
agent_builder.add_node("verification_agent", verification_agent)
agent_builder.add_node("review_manager", review_manager_agent)
agent_builder.add_node("publish_verified_review", publish_verified_review)

# Pipeline Flow
agent_builder.set_entry_point("code_analyst")
agent_builder.add_edge("code_analyst", "bug_hunter")
agent_builder.add_edge("bug_hunter", "security_auditor")
agent_builder.add_edge("security_auditor", "performance_agent")
agent_builder.add_edge("performance_agent", "fix_and_test_engineers")
agent_builder.add_edge("fix_and_test_engineers", "verification_agent")

agent_builder.add_conditional_edges(
    "verification_agent",
    should_retry_or_proceed,
    {
        "fix_and_test_engineers": "fix_and_test_engineers",
        "review_manager": "review_manager",
    },
)

agent_builder.add_conditional_edges(
    "review_manager",
    check_approval_decision,
    {
        "publish_verified_review": "publish_verified_review",
        END: END,
    },
)
agent_builder.add_edge("publish_verified_review", END)

# MemorySaver checkpointing for thread isolation
agent_checkpointer = MemorySaver()
code_sentinel_multi_agent = agent_builder.compile(checkpointer=agent_checkpointer)

# Backward-compatibility alias
code_review_agent = code_sentinel_multi_agent
