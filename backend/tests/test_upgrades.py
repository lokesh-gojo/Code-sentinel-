import pytest
from app.services.repo_intelligence import repo_intelligence_service
from app.services.security_auditor import security_auditor_service
from app.services.quality_scorer import quality_scorer_service
from app.services.project_memory import project_memory_service
from app.services.llm_provider import llm_factory, HeuristicProvider, OllamaProvider
from app.models.schemas import Finding
import os


def test_repo_intelligence_scans_workspace():
    report = repo_intelligence_service.scan_repository(os.getcwd())
    assert report.total_files > 0
    assert "python" in report.languages_detected
    assert isinstance(report.nodes, list)
    assert len(report.nodes) > 0
    assert report.architecture_summary != ""


def test_security_auditor_detects_secrets_and_injections():
    buggy_code = """import sqlite3
API_SECRET_KEY = "SUPER_SECRET_KEY_123456789"
def query(user):
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = '{user}'")
"""
    findings = security_auditor_service.audit_code(buggy_code, "test.py")
    assert len(findings) >= 2
    rule_ids = [f.rule_id for f in findings]
    assert "HARDCODED_API_KEY" in rule_ids
    assert "SQL_INJECTION_FORMAT_STRING" in rule_ids


def test_quality_scorer_calculates_calibrated_metrics():
    findings = [
        Finding(
            tool="bandit",
            rule_id="B105",
            severity="high",
            category="Security Vulnerability",
            file_path="main.py",
            line_number=5,
            message="Hardcoded password",
        )
    ]
    report = quality_scorer_service.calculate_score(findings, total_lines=50, has_tests=True)
    assert 0 <= report.overall <= 100
    assert report.security < 100  # Penalized by high security issue
    assert report.assessment in ("Good", "Action Required", "Critical Defect Risk", "Excellent")


def test_project_memory_records_and_retrieves():
    rec = project_memory_service.add_record(
        repo="test-repo",
        memory_type="convention",
        title="Type Annotations",
        description="All service methods must have explicit return type annotations.",
    )
    assert rec.id is not None
    records = project_memory_service.get_records("test-repo")
    titles = [r.title for r in records]
    assert "Type Annotations" in titles


def test_llm_provider_factory_fallback():
    provider = llm_factory.get_provider("auto")
    assert provider is not None
    patch = provider.generate_patch(
        code="def divide(a, b):\n    return a / b\n",
        filename="main.py",
        findings=[],
    )
    assert patch.suggested_patch != ""
    assert patch.regression_test != ""
