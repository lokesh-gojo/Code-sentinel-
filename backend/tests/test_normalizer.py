from app.services.normalizer import (
    normalize_ruff,
    normalize_bandit,
    normalize_eslint,
    normalize_semgrep,
)


def test_normalize_ruff():
    raw = [
        {
            "code": "F821",
            "message": "Undefined name 'variable_xyz'",
            "location": {"row": 5, "column": 10},
        }
    ]
    findings = normalize_ruff(raw, "test.py")
    assert len(findings) == 1
    assert findings[0].tool == "ruff"
    assert findings[0].rule_id == "F821"
    assert findings[0].severity == "high"
    assert findings[0].line_number == 5


def test_normalize_bandit():
    raw = [
        {
            "test_id": "B105",
            "issue_severity": "LOW",
            "line_number": 12,
            "issue_text": "Possible hardcoded password",
        }
    ]
    findings = normalize_bandit(raw, "test.py")
    assert len(findings) == 1
    assert findings[0].tool == "bandit"
    assert findings[0].rule_id == "B105"
    assert findings[0].severity == "low"
