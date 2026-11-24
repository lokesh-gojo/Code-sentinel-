import pytest
from app.services.analyzer import analyzer_service
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_analyzer_detects_zero_division():
    code = (FIXTURES_DIR / "buggy_math.py").read_text(encoding="utf-8")
    findings = analyzer_service.analyze_snippet(code, filename="buggy_math.py", language="python")

    assert len(findings) > 0
    tools = [f.tool for f in findings]
    # Either ast-hunter, ruff, or bandit should catch issues
    messages = [f.message.lower() for f in findings]
    has_zero_div = any("zero" in m or "division" in m for m in messages)
    assert has_zero_div, "Analyzer should identify zero division risk"


def test_analyzer_detects_security_risks():
    code = (FIXTURES_DIR / "vulnerable_creds.py").read_text(encoding="utf-8")
    findings = analyzer_service.analyze_snippet(code, filename="vulnerable_creds.py", language="python")

    assert len(findings) > 0
    # Check severity
    severities = [f.severity for f in findings]
    assert "high" in severities or "medium" in severities or "low" in severities


def test_analyzer_sanitizes_bad_filenames():
    code = "x = 10\n"
    safe_name = analyzer_service.sanitize_filename("../../etc/passwd", "python")
    assert safe_name == "passwd" or "passwd" in safe_name
    assert not safe_name.startswith("/")
    assert not safe_name.startswith("..")
