from typing import List, Dict, Any
from app.models.schemas import Finding, SeverityLevel


def normalize_ruff(raw_findings: List[Dict[str, Any]], filename: str) -> List[Finding]:
    """Normalizes Ruff JSON output into unified Finding objects."""
    findings: List[Finding] = []
    for item in raw_findings:
        code = item.get("code", "RUFF")
        # Determine severity based on Ruff rule codes
        # E/W = pycodestyle, F = pyflakes, B = flake8-bugbear, S = flake8-bandit
        if code.startswith(("S", "F821", "F822", "B006", "B008")):
            severity: SeverityLevel = "high"
        elif code.startswith(("E", "F", "B")):
            severity = "medium"
        else:
            severity = "low"

        findings.append(
            Finding(
                tool="ruff",
                rule_id=code,
                severity=severity,
                category="Code Quality & Bug Risk",
                file_path=filename,
                line_number=item.get("location", {}).get("row", 1),
                message=item.get("message", "Lint warning or potential bug detected by Ruff"),
            )
        )
    return findings


def normalize_bandit(raw_results: List[Dict[str, Any]], filename: str) -> List[Finding]:
    """Normalizes Bandit JSON output into unified Finding objects."""
    findings: List[Finding] = []
    for item in raw_results:
        issue_severity = str(item.get("issue_severity", "LOW")).lower()
        if issue_severity not in ("high", "medium", "low"):
            issue_severity = "low"

        findings.append(
            Finding(
                tool="bandit",
                rule_id=item.get("test_id", "B_SEC"),
                severity=issue_severity,  # type: ignore
                category="Security Vulnerability",
                file_path=filename,
                line_number=item.get("line_number", 1),
                message=item.get("issue_text", "Security hazard detected by Bandit AST analysis"),
            )
        )
    return findings


def normalize_eslint(raw_messages: List[Dict[str, Any]], filename: str) -> List[Finding]:
    """Normalizes ESLint JSON output into unified Finding objects."""
    findings: List[Finding] = []
    for item in raw_messages:
        # ESLint severity: 1 = warning, 2 = error
        eslint_sev = item.get("severity", 1)
        rule = item.get("ruleId") or "eslint-general"
        
        severity: SeverityLevel = "high" if eslint_sev == 2 else "medium"
        if "security" in rule.lower() or "eval" in rule.lower() or "injection" in rule.lower():
            severity = "high"

        findings.append(
            Finding(
                tool="eslint",
                rule_id=rule,
                severity=severity,
                category="JavaScript/TypeScript Quality",
                file_path=filename,
                line_number=item.get("line", 1),
                message=item.get("message", "Issue detected by ESLint"),
            )
        )
    return findings


def normalize_semgrep(raw_results: List[Dict[str, Any]], filename: str) -> List[Finding]:
    """Normalizes Semgrep JSON output into unified Finding objects."""
    findings: List[Finding] = []
    for item in raw_results:
        extra = item.get("extra", {})
        semgrep_sev = str(extra.get("severity", "WARNING")).upper()
        
        if semgrep_sev == "ERROR":
            severity: SeverityLevel = "high"
        elif semgrep_sev == "WARNING":
            severity = "medium"
        else:
            severity = "low"

        findings.append(
            Finding(
                tool="semgrep",
                rule_id=item.get("check_id", "semgrep-rule"),
                severity=severity,
                category="Pattern & Security Policy",
                file_path=filename,
                line_number=item.get("start", {}).get("line", 1),
                message=extra.get("message", "Semgrep pattern match"),
            )
        )
    return findings
