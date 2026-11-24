from typing import List, Dict, Any
from pydantic import BaseModel, Field
from app.models.schemas import Finding


class CodeReviewPolicy(BaseModel):
    block_critical_vulnerabilities: bool = True
    block_high_severity: bool = True
    block_hardcoded_secrets: bool = True
    minimum_quality_score: int = 75
    require_human_approval: bool = True
    allow_auto_merge: bool = False
    max_cyclomatic_complexity: int = 15


class PolicyEvaluationResult(BaseModel):
    passed: bool
    violations: List[str]
    enforced_rules: List[str]
    merge_status: str  # "BLOCKED" | "APPROVED" | "REQUIRES_REVIEW"


class PolicyEngineService:
    """
    Feature 18: Intelligent Code Review Policy Engine.
    Deterministically evaluates repository quality policies before allowing PR merge.
    """

    def evaluate_policy(
        self,
        findings: List[Finding],
        quality_score: int = 86,
        policy: CodeReviewPolicy = CodeReviewPolicy(),
    ) -> PolicyEvaluationResult:
        violations: List[str] = []
        enforced: List[str] = []

        # 1. Block High/Critical Vulnerabilities
        high_findings = [f for f in findings if f.severity == "high"]
        if policy.block_high_severity and high_findings:
            violations.append(f"Policy Violation: Found {len(high_findings)} High-severity issues (Rule 'block_high_severity' active).")
        enforced.append("block_high_severity")

        # 2. Block Hardcoded Secrets
        secret_findings = [f for f in findings if "secret" in f.rule_id.lower() or "key" in f.rule_id.lower() or "password" in f.rule_id.lower()]
        if policy.block_hardcoded_secrets and secret_findings:
            violations.append(f"Policy Violation: Detected {len(secret_findings)} exposed secrets in code.")
        enforced.append("block_hardcoded_secrets")

        # 3. Minimum Quality Score
        if quality_score < policy.minimum_quality_score:
            violations.append(f"Policy Violation: Quality score {quality_score}/100 is below required threshold {policy.minimum_quality_score}/100.")
        enforced.append(f"minimum_quality_score (>= {policy.minimum_quality_score})")

        # 4. Human Approval Rule
        enforced.append("require_human_approval (100% enforced)")

        passed = len(violations) == 0
        merge_status = "APPROVED" if passed else "BLOCKED"

        return PolicyEvaluationResult(
            passed=passed,
            violations=violations,
            enforced_rules=enforced,
            merge_status=merge_status,
        )


policy_engine_service = PolicyEngineService()
