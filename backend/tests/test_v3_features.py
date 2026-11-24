import pytest
import time
from app.core.approval_security import approval_security_manager
from app.services.regression_risk import regression_risk_predictor
from app.services.supply_chain import supply_chain_service
from app.services.policy_engine import policy_engine_service, CodeReviewPolicy
from app.services.architecture_reviewer import architecture_reviewer_service
from app.services.ci_investigator import ci_investigator_service
from benchmarks.benchmark_evaluator import benchmark_evaluator
from app.models.schemas import Finding


def test_approval_security_hmac_and_replay_protection():
    thread_id = "test-thread-sec-1"
    user_id = "test-user-alice"
    patch = "def divide(a, b):\n    if b == 0: raise ValueError()\n    return a / b\n"

    # 1. Generate valid signed token
    token = approval_security_manager.generate_approval_token(thread_id, user_id, patch)
    assert token is not None
    assert len(token.split(".")) == 2

    # 2. First verification: should succeed
    valid, msg = approval_security_manager.verify_and_consume_approval(token, thread_id, user_id, patch)
    assert valid is True
    assert "successfully" in msg

    # 3. Replay attack: same token used again must be rejected!
    valid_replay, msg_replay = approval_security_manager.verify_and_consume_approval(token, thread_id, user_id, patch)
    assert valid_replay is False
    assert "Replay attack detected" in msg_replay

    # 4. Tampered patch code must fail integrity check
    token2 = approval_security_manager.generate_approval_token(thread_id, user_id, patch)
    tampered_patch = patch + "\n# Tampered line"
    valid_tamper, msg_tamper = approval_security_manager.verify_and_consume_approval(token2, thread_id, user_id, tampered_patch)
    assert valid_tamper is False
    assert "integrity violation" in msg_tamper


def test_regression_risk_prediction():
    report = regression_risk_predictor.predict_risk(["backend/app/main.py", "backend/app/services/analyzer.py"])
    assert report.change_risk_score in ("HIGH", "MEDIUM", "LOW")
    assert 0 <= report.overall_risk_index <= 100
    assert len(report.impacted_modules) == 2
    assert len(report.recommended_tests) > 0


def test_supply_chain_cyclonedx_sbom():
    req = """fastapi>=0.110.0
pydantic>=2.7.0
requests==2.28.0
"""
    sbom = supply_chain_service.generate_cyclonedx_sbom(req)
    assert sbom.bom_format == "CycloneDX"
    assert sbom.spec_version == "1.5"
    assert sbom.total_components == 3
    # requests < 2.31.0 should trigger CVE alert
    vuln_names = [c.name for c in sbom.components if c.is_vulnerable]
    assert "requests" in vuln_names


def test_policy_engine_enforcement():
    high_finding = Finding(
        tool="security-auditor",
        rule_id="SQL_INJECTION",
        severity="high",
        category="Security Vulnerability",
        file_path="main.py",
        line_number=10,
        message="SQL injection",
    )
    # Default policy blocks high severity
    res = policy_engine_service.evaluate_policy(findings=[high_finding], quality_score=60)
    assert res.passed is False
    assert res.merge_status == "BLOCKED"
    assert len(res.violations) >= 1


def test_architecture_reviewer():
    report = architecture_reviewer_service.review_architecture()
    assert report.system_architectural_pattern != ""
    assert isinstance(report.architectural_issues, list)
    assert len(report.refactoring_priorities) > 0


def test_ci_investigator():
    mock_ci_log = """
=================================== FAILURES ===================================
____________________________ test_divide_by_zero ____________________________
tests/test_math.py:15: ZeroDivisionError: division by zero
E   ZeroDivisionError: division by zero
FAILED tests/test_math.py::test_divide_by_zero - ZeroDivisionError
"""
    diagnosis = ci_investigator_service.investigate_log(mock_ci_log)
    assert diagnosis.failed_test_name == "test_divide_by_zero"
    assert diagnosis.exception_type == "ZeroDivisionError"
    assert diagnosis.failing_line == 15
    assert "candidate_fix" in diagnosis.model_dump()


def test_empirical_benchmark_evaluation():
    report = benchmark_evaluator.run_benchmark()
    assert report.total_benchmark_cases == 8
    assert report.true_positives > 0
    assert 0.0 <= report.precision <= 1.0
    assert 0.0 <= report.recall <= 1.0
    assert report.patch_sandbox_pass_rate > 0.0
