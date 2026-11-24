import re
from typing import List, Dict, Any
from app.models.schemas import Finding, SeverityLevel


class SecurityAuditorService:
    """
    Enterprise-grade security auditor scanning for:
    - Secret exposure (API keys, JWT secrets, passwords)
    - Injection flaws (SQLi, Command Injection, XSS)
    - Insecure configurations (CORS, debug flags)
    - Vulnerable dependency manifests (OSV/CVE mapping)
    """

    SECRET_PATTERNS = [
        (r"(?i)(?:api_key|apikey|secret_key|secret)\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]", "HARDCODED_API_KEY", "high", "Hardcoded API key or private secret detected in source."),
        (r"(?i)(?:password|passwd|pwd)\s*=\s*['\"][^'\"]{6,}['\"]", "HARDCODED_PASSWORD", "high", "Plaintext password constant found in source."),
        (r"ghp_[a-zA-Z0-9]{36}", "GITHUB_PERSONAL_ACCESS_TOKEN", "high", "Live GitHub Personal Access Token pattern detected."),
        (r"eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}", "HARDCODED_JWT_TOKEN", "high", "Hardcoded JSON Web Token detected."),
    ]

    INJECTION_PATTERNS = [
        (r"(?i)execute\s*\(\s*f[\"'].*?\{[a-zA-Z0-9_]+\}", "SQL_INJECTION_FORMAT_STRING", "high", "Unsanitized f-string formatting in SQL execute call (SQL Injection risk)."),
        (r"(?i)cursor\.execute\s*\([^,]+\s*%\s*[a-zA-Z0-9_]+", "SQL_INJECTION_PERCENT_FORMAT", "high", "Python % string interpolation in SQL query (SQL Injection risk)."),
        (r"(?i)subprocess\.(?:Popen|run|call)\s*\([^)]*shell\s*=\s*True", "COMMAND_INJECTION_SHELL_TRUE", "high", "Subprocess invoked with shell=True exposing host to command injection."),
    ]

    INSECURE_CONFIG_PATTERNS = [
        (r"(?i)allow_origins\s*=\s*\[\s*['\"]\*['\"]\s*\]\s*,\s*allow_credentials\s*=\s*True", "INSECURE_CORS_WILDCARD_CREDENTIALS", "medium", "CORS configured with wildcard origin '*' and allow_credentials=True."),
        (r"(?i)debug\s*=\s*True", "DEBUG_MODE_ENABLED", "low", "Debug mode flag enabled; ensure this is disabled in production."),
    ]

    KNOWN_VULNERABLE_PACKAGES = {
        "requests": ("<2.31.0", "CVE-2023-32681", "Leaking Proxy-Authorization headers on redirect to different port."),
        "urllib3": ("<2.0.7", "CVE-2023-45803", "Request body strip on redirect missing for specific HTTP verbs."),
        "cryptography": ("<41.0.6", "CVE-2023-49083", "NULL-pointer dereference in PKCS7 verification."),
        "express": ("<4.19.2", "CVE-2024-29041", "Open redirect in malformed URL handling."),
    }

    def audit_code(self, code: str, filename: str) -> List[Finding]:
        findings: List[Finding] = []
        lines = code.splitlines()

        # 1. Secret Scanning
        for pattern, rule_id, sev, msg in self.SECRET_PATTERNS:
            for idx, line in enumerate(lines, start=1):
                if re.search(pattern, line):
                    findings.append(
                        Finding(
                            tool="security-auditor",
                            rule_id=rule_id,
                            severity=sev,  # type: ignore
                            category="Security Vulnerability",
                            file_path=filename,
                            line_number=idx,
                            message=msg,
                        )
                    )

        # 2. Injection Flaws
        for pattern, rule_id, sev, msg in self.INJECTION_PATTERNS:
            for idx, line in enumerate(lines, start=1):
                if re.search(pattern, line):
                    findings.append(
                        Finding(
                            tool="security-auditor",
                            rule_id=rule_id,
                            severity=sev,  # type: ignore
                            category="Security Vulnerability",
                            file_path=filename,
                            line_number=idx,
                            message=msg,
                        )
                    )

        # 3. Insecure Configs
        for pattern, rule_id, sev, msg in self.INSECURE_CONFIG_PATTERNS:
            for idx, line in enumerate(lines, start=1):
                if re.search(pattern, line):
                    findings.append(
                        Finding(
                            tool="security-auditor",
                            rule_id=rule_id,
                            severity=sev,  # type: ignore
                            category="Security Configuration",
                            file_path=filename,
                            line_number=idx,
                            message=msg,
                        )
                    )

        return findings

    def audit_dependencies(self, manifest_text: str, filename: str = "requirements.txt") -> List[Finding]:
        findings: List[Finding] = []
        for line_no, raw_line in enumerate(manifest_text.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            for pkg_name, (vuln_range, cve_id, description) in self.KNOWN_VULNERABLE_PACKAGES.items():
                if pkg_name in line.lower():
                    findings.append(
                        Finding(
                            tool="dependency-scanner",
                            rule_id=cve_id,
                            severity="high",
                            category="Vulnerable Dependency",
                            file_path=filename,
                            line_number=line_no,
                            message=f"Dependency '{pkg_name}' may be vulnerable ({cve_id}: {description}). Recommended: upgrade package.",
                        )
                    )
        return findings


security_auditor_service = SecurityAuditorService()
