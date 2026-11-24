from typing import List, Dict, Any
from pydantic import BaseModel


class GroundTruthTestCase(BaseModel):
    case_id: str
    name: str
    code: str
    filename: str = "benchmark_file.py"
    language: str = "python"
    expected_rule_ids: List[str]
    expected_categories: List[str]
    is_negative_control: bool = False  # If True, expected 0 defects


BENCHMARK_CASES: List[GroundTruthTestCase] = [
    GroundTruthTestCase(
        case_id="TC-01",
        name="Division by Zero Hazard",
        code="""def calculate_rate(total, count):
    # Missing zero check on count
    return total / count

print(calculate_rate(100, 0))
""",
        expected_rule_ids=["POTENTIAL_ZERO_DIVISION", "ZERO_ARG_PASSED"],
        expected_categories=["Potential Runtime Bug"],
    ),
    GroundTruthTestCase(
        case_id="TC-02",
        name="Mutable Default Argument Trap",
        code="""def register_user(username, roles=[]):
    # Bug: roles list retained across invocations
    roles.append(username)
    return roles
""",
        expected_rule_ids=["MUTABLE_DEFAULT_ARG"],
        expected_categories=["Code Quality & Bug Risk"],
    ),
    GroundTruthTestCase(
        case_id="TC-03",
        name="Hardcoded Secret Key (Gitleaks pattern)",
        code="""import os
API_SECRET_KEY = "SUPER_SECRET_PRODUCTION_KEY_987654321"
def get_auth_header():
    return {"Authorization": f"Bearer {API_SECRET_KEY}"}
""",
        expected_rule_ids=["HARDCODED_API_KEY"],
        expected_categories=["Security Vulnerability"],
    ),
    GroundTruthTestCase(
        case_id="TC-04",
        name="SQL Injection via Format String",
        code="""import sqlite3
def fetch_account(account_id):
    conn = sqlite3.connect("bank.db")
    cur = conn.cursor()
    # SQLi format string
    cur.execute(f"SELECT * FROM accounts WHERE id = '{account_id}'")
    return cur.fetchall()
""",
        expected_rule_ids=["SQL_INJECTION_FORMAT_STRING"],
        expected_categories=["Security Vulnerability"],
    ),
    GroundTruthTestCase(
        case_id="TC-05",
        name="Subprocess Shell=True Command Injection",
        code="""import subprocess
def ping_host(host_ip):
    # Command injection risk
    return subprocess.run(f"ping -c 1 {host_ip}", shell=True, capture_output=True)
""",
        expected_rule_ids=["COMMAND_INJECTION_SHELL_TRUE"],
        expected_categories=["Security Vulnerability"],
    ),
    GroundTruthTestCase(
        case_id="TC-06",
        name="Algorithmic Nested Loop Complexity",
        code="""def find_duplicates(items):
    duplicates = []
    for i in items:
        for j in items:
            if i == j:
                duplicates.append(i)
    return duplicates
""",
        expected_rule_ids=["NESTED_LOOP_COMPLEXITY"],
        expected_categories=["Performance Bottleneck"],
    ),
    GroundTruthTestCase(
        case_id="TC-07",
        name="Clean Valid Code (Negative Control)",
        code="""def safe_divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Denominator cannot be zero")
    return a / b
""",
        expected_rule_ids=[],
        expected_categories=[],
        is_negative_control=True,
    ),
    GroundTruthTestCase(
        case_id="TC-08",
        name="Syntax Error Ingestion",
        code="""def malformed_syntax(:
    return "broken"
""",
        expected_rule_ids=["SYNTAX_ERROR"],
        expected_categories=["Syntax Bug"],
    ),
]
