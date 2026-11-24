import json
import subprocess
import tempfile
import re
from pathlib import Path
from typing import List
from app.models.schemas import Finding, ScanLanguage, SeverityLevel
from app.services.normalizer import (
    normalize_ruff,
    normalize_bandit,
    normalize_eslint,
    normalize_semgrep,
)
from app.services.security_auditor import security_auditor_service

SUBPROCESS_TIMEOUT_SECONDS = 15


class AnalyzerService:
    """
    Orchestrates multi-language static analysis with strict security controls:
    - Never executes untrusted user code; runs AST & static scanners only.
    - Always invokes subprocesses with list arguments and shell=False.
    - Uses strict 15s timeouts and sanitizes input filenames.
    - Ephemeral temp directories.
    """

    def sanitize_filename(self, filename: str, language: ScanLanguage) -> str:
        safe_name = Path(filename).name
        safe_name = re.sub(r"[^\w\-.]", "_", safe_name)
        if not safe_name or safe_name.startswith("."):
            safe_name = f"source.{'py' if language == 'python' else 'js' if language == 'javascript' else 'ts'}"
        return safe_name

    def analyze_python_ast_heuristics(self, code: str, filename: str) -> List[Finding]:
        import ast
        findings: List[Finding] = []
        try:
            tree = ast.parse(code, filename=filename)

            for node in ast.walk(tree):
                # 1. Direct division/modulo by literal 0
                if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                    if isinstance(node.right, ast.Constant) and node.right.value == 0:
                        findings.append(
                            Finding(
                                tool="ast-hunter",
                                rule_id="ZERO_DIVISION",
                                severity="high",
                                category="Potential Runtime Bug",
                                file_path=filename,
                                line_number=node.lineno,
                                message="Potential ZeroDivisionError: dividing or modulo by literal zero",
                            )
                        )

                # 2. Function-level inspection: unvalidated divisor parameters & mutable defaults
                elif isinstance(node, ast.FunctionDef):
                    arg_names = {arg.arg for arg in node.args.args}

                    # Check mutable default arguments: def fn(items=[])
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            findings.append(
                                Finding(
                                    tool="ast-hunter",
                                    rule_id="MUTABLE_DEFAULT_ARG",
                                    severity="medium",
                                    category="Code Quality & Bug Risk",
                                    file_path=filename,
                                    line_number=node.lineno,
                                    message=f"Function '{node.name}' uses mutable default argument; instances are shared across calls",
                                )
                            )

                    # Check unvalidated division by parameter
                    for sub in ast.walk(node):
                        if isinstance(sub, ast.BinOp) and isinstance(sub.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                            if isinstance(sub.right, ast.Name) and sub.right.id in arg_names:
                                has_guard = False
                                for stmt in node.body:
                                    if isinstance(stmt, (ast.If, ast.Assert)):
                                        if sub.right.id in ast.dump(stmt.test):
                                            has_guard = True
                                if not has_guard:
                                    findings.append(
                                        Finding(
                                            tool="ast-hunter",
                                            rule_id="POTENTIAL_ZERO_DIVISION",
                                            severity="high",
                                            category="Potential Runtime Bug",
                                            file_path=filename,
                                            line_number=sub.lineno,
                                            message=f"Function '{node.name}' does not check whether parameter '{sub.right.id}' is zero before division, which may raise ZeroDivisionError",
                                        )
                                    )

                # 3. Call-site zero division
                elif isinstance(node, ast.Call):
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and arg.value == 0:
                            func_name = getattr(node.func, "id", None)
                            if func_name and "div" in func_name.lower():
                                findings.append(
                                    Finding(
                                        tool="ast-hunter",
                                        rule_id="ZERO_ARG_PASSED",
                                        severity="high",
                                        category="Potential Runtime Bug",
                                        file_path=filename,
                                        line_number=node.lineno,
                                        message=f"Call to '{func_name}' passes 0 as argument which may cause division by zero runtime error",
                                    )
                                )

        except SyntaxError as e:
            findings.append(
                Finding(
                    tool="python-compiler",
                    rule_id="SYNTAX_ERROR",
                    severity="high",
                    category="Syntax Bug",
                    file_path=filename,
                    line_number=e.lineno or 1,
                    message=f"SyntaxError: {e.msg}",
                )
            )
        except Exception:
            pass

        return findings

    def run_ruff(self, temp_dir: Path, target_file: Path) -> List[Finding]:
        try:
            proc = subprocess.run(
                ["ruff", "check", "--output-format", "json", str(target_file.name)],
                cwd=str(temp_dir),
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
                shell=False,
            )
            raw = proc.stdout.strip()
            if raw:
                try:
                    data = json.loads(raw)
                    return normalize_ruff(data, target_file.name)
                except Exception:
                    pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return []

    def run_bandit(self, temp_dir: Path, target_file: Path) -> List[Finding]:
        try:
            proc = subprocess.run(
                ["bandit", "-f", "json", "-q", str(target_file.name)],
                cwd=str(temp_dir),
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
                shell=False,
            )
            raw = proc.stdout.strip()
            if raw:
                try:
                    data = json.loads(raw)
                    return normalize_bandit(data.get("results", []), target_file.name)
                except Exception:
                    pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return []

    def run_eslint(self, temp_dir: Path, target_file: Path) -> List[Finding]:
        try:
            proc = subprocess.run(
                ["npx", "eslint", "--format", "json", str(target_file.name)],
                cwd=str(temp_dir),
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
                shell=False,
            )
            raw = proc.stdout.strip()
            if raw:
                try:
                    data = json.loads(raw)
                    if isinstance(data, list) and len(data) > 0:
                        messages = data[0].get("messages", [])
                        return normalize_eslint(messages, target_file.name)
                except Exception:
                    pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return []

    def run_semgrep(self, temp_dir: Path, target_file: Path) -> List[Finding]:
        try:
            proc = subprocess.run(
                ["semgrep", "--config", "auto", "--json", str(target_file.name)],
                cwd=str(temp_dir),
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
                shell=False,
            )
            raw = proc.stdout.strip()
            if raw:
                try:
                    data = json.loads(raw)
                    return normalize_semgrep(data.get("results", []), target_file.name)
                except Exception:
                    pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return []

    def analyze_snippet(
        self,
        code: str,
        filename: str = "main.py",
        language: ScanLanguage = "python"
    ) -> List[Finding]:
        safe_filename = self.sanitize_filename(filename, language)
        all_findings: List[Finding] = []

        # 1. Advanced Security Auditor (Secrets, Injections, Configs)
        all_findings.extend(security_auditor_service.audit_code(code, safe_filename))

        # 2. Ephemeral Sandbox Tool Scans
        with tempfile.TemporaryDirectory() as tmp_str:
            temp_dir = Path(tmp_str)
            target_file = temp_dir / safe_filename
            target_file.write_text(code, encoding="utf-8")

            if language == "python":
                # AST Heuristics
                all_findings.extend(self.analyze_python_ast_heuristics(code, safe_filename))
                # Ruff Linter
                all_findings.extend(self.run_ruff(temp_dir, target_file))
                # Bandit Security
                all_findings.extend(self.run_bandit(temp_dir, target_file))
                # Semgrep Community Rules
                all_findings.extend(self.run_semgrep(temp_dir, target_file))
            elif language in ("javascript", "typescript"):
                all_findings.extend(self.run_eslint(temp_dir, target_file))
                all_findings.extend(self.run_semgrep(temp_dir, target_file))

        # Deduplicate findings
        seen = set()
        deduped: List[Finding] = []
        for f in all_findings:
            key = (f.tool, f.rule_id, f.line_number, f.message)
            if key not in seen:
                seen.add(key)
                deduped.append(f)

        severity_rank = {"high": 0, "medium": 1, "low": 2, "info": 3}
        deduped.sort(key=lambda x: (x.line_number, severity_rank.get(x.severity, 4)))
        return deduped


analyzer_service = AnalyzerService()
