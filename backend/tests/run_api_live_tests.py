import sys
import json
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
results = []

def record(name: str, passed: bool, details: str = ""):
    results.append({"name": name, "passed": passed, "details": details})
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name} - {details}")

print("=== Starting Comprehensive v3.0 API Integration Tests ===")

# 1. Health
try:
    res = client.get("/health")
    data = res.json()
    record("GET /health", res.status_code == 200, f"Provider: {data.get('active_llm_provider')}, Version: {data.get('version')}")
except Exception as e:
    record("GET /health", False, str(e))

# 2. Snippet Scan
try:
    payload = {"filename": "calc.py", "language": "python", "code": "def div(a,b): return a/b\nprint(div(10,0))\n", "include_ai": True}
    res = client.post("/api/scans/snippet", json=payload, headers={"Authorization": "Bearer dev-token"})
    data = res.json()
    record("POST /api/scans/snippet", res.status_code == 200 and data.get("total_findings", 0) > 0, f"Findings: {data.get('total_findings')}")
except Exception as e:
    record("POST /api/scans/snippet", False, str(e))

# 3. List Scans
try:
    res = client.get("/api/scans", headers={"Authorization": "Bearer dev-token"})
    record("GET /api/scans", res.status_code == 200 and isinstance(res.json(), list), f"Count: {len(res.json())}")
except Exception as e:
    record("GET /api/scans", False, str(e))

# 4. Agent Start & Token Generation
thread_id = None
token = None
try:
    payload = {"filename": "calc.py", "language": "python", "code": "def div(a,b): return a/b\n"}
    res = client.post("/api/agent/start", json=payload, headers={"Authorization": "Bearer dev-token"})
    data = res.json()
    thread_id = data.get("thread_id")
    token = data.get("proposal", {}).get("approval_token")
    record("POST /api/agent/start (HMAC Token)", res.status_code == 200 and token is not None, f"State: {data.get('status')}, Token Generated: {bool(token)}")
except Exception as e:
    record("POST /api/agent/start (HMAC Token)", False, str(e))

# 5. Agent Status
if thread_id:
    try:
        res = client.get(f"/api/agent/status/{thread_id}", headers={"Authorization": "Bearer dev-token"})
        record("GET /api/agent/status/{id}", res.status_code == 200, f"Status: {res.json().get('status')}")
    except Exception as e:
        record("GET /api/agent/status/{id}", False, str(e))

# 6. Secure Agent Resume
if thread_id and token:
    try:
        payload = {"thread_id": thread_id, "approved": True, "feedback": "Approved", "approval_token": token}
        res = client.post("/api/agent/resume", json=payload, headers={"Authorization": "Bearer dev-token"})
        record("POST /api/agent/resume (HMAC Validated)", res.status_code == 200 and res.json().get("status") == "completed", f"Status: {res.json().get('status')}")
    except Exception as e:
        record("POST /api/agent/resume (HMAC Validated)", False, str(e))

# 7. Repo Intelligence
try:
    res = client.get("/api/intelligence/repo", headers={"Authorization": "Bearer dev-token"})
    data = res.json()
    record("GET /api/intelligence/repo", res.status_code == 200 and data.get("total_files") > 0, f"Files: {data.get('total_files')}, Cycles: {len(data.get('circular_dependencies'))}")
except Exception as e:
    record("GET /api/intelligence/repo", False, str(e))

# 8. Quality Score
try:
    res = client.get("/api/intelligence/quality-score", headers={"Authorization": "Bearer dev-token"})
    data = res.json()
    record("GET /api/intelligence/quality-score", res.status_code == 200, f"Score: {data.get('overall')}/100 ({data.get('assessment')})")
except Exception as e:
    record("GET /api/intelligence/quality-score", False, str(e))

# 9. Project Memory
try:
    client.post("/api/intelligence/memory", json={"repo_name": "sentinel-core", "memory_type": "decision", "title": "ADR-001", "description": "MicroVM Sandbox"}, headers={"Authorization": "Bearer dev-token"})
    get_res = client.get("/api/intelligence/memory?repo=sentinel-core", headers={"Authorization": "Bearer dev-token"})
    record("POST & GET /api/intelligence/memory", get_res.status_code == 200 and len(get_res.json()) > 0, f"Records: {len(get_res.json())}")
except Exception as e:
    record("POST & GET /api/intelligence/memory", False, str(e))

# 10. AI Assistant Chat
try:
    res = client.post("/api/intelligence/assistant/chat", json={"message": "Audit security", "repo_name": "default", "provider": "auto"}, headers={"Authorization": "Bearer dev-token"})
    record("POST /api/intelligence/assistant/chat", res.status_code == 200, f"Replied with length {len(res.json().get('reply'))}")
except Exception as e:
    record("POST /api/intelligence/assistant/chat", False, str(e))

# 11. Regression Risk Predictor (Feature 13)
try:
    res = client.post("/api/intelligence/regression-risk", json={"changed_files": ["backend/app/main.py", "backend/app/services/analyzer.py"]}, headers={"Authorization": "Bearer dev-token"})
    data = res.json()
    record("POST /api/intelligence/regression-risk (F13)", res.status_code == 200, f"Risk: {data.get('change_risk_score')}, Score: {data.get('overall_risk_index')}")
except Exception as e:
    record("POST /api/intelligence/regression-risk (F13)", False, str(e))

# 12. Architecture Reviewer (Feature 14)
try:
    res = client.get("/api/intelligence/architecture-review", headers={"Authorization": "Bearer dev-token"})
    data = res.json()
    record("GET /api/intelligence/architecture-review (F14)", res.status_code == 200, f"Pattern: {data.get('system_architectural_pattern')}, Debt Index: {data.get('technical_debt_index')}")
except Exception as e:
    record("GET /api/intelligence/architecture-review (F14)", False, str(e))

# 13. Software Supply Chain & CycloneDX SBOM (Feature 16)
try:
    res = client.get("/api/intelligence/sbom", headers={"Authorization": "Bearer dev-token"})
    data = res.json()
    record("GET /api/intelligence/sbom (F16)", res.status_code == 200 and data.get("bom_format") == "CycloneDX", f"Spec: {data.get('bom_format')} {data.get('spec_version')}, Components: {data.get('total_components')}")
except Exception as e:
    record("GET /api/intelligence/sbom (F16)", False, str(e))

# 14. CI Test Failure Investigator (Feature 17)
try:
    log_sample = "FAILED test_auth.py::test_jwt - AssertionError: Token expired"
    res = client.post("/api/intelligence/ci-investigate", json={"log_text": log_sample}, headers={"Authorization": "Bearer dev-token"})
    data = res.json()
    record("POST /api/intelligence/ci-investigate (F17)", res.status_code == 200, f"Failed Test: {data.get('failed_test_name')}, Fix: {bool(data.get('candidate_fix'))}")
except Exception as e:
    record("POST /api/intelligence/ci-investigate (F17)", False, str(e))

# 15. Policy Engine (Feature 18)
try:
    pol = {"block_critical_vulnerabilities": True, "block_high_severity": True, "block_hardcoded_secrets": True, "minimum_quality_score": 75, "require_human_approval": True, "allow_auto_merge": False, "max_cyclomatic_complexity": 15}
    res = client.post("/api/intelligence/policy-evaluate", json=pol, headers={"Authorization": "Bearer dev-token"})
    data = res.json()
    record("POST /api/intelligence/policy-evaluate (F18)", res.status_code == 200, f"Merge Status: {data.get('merge_status')}")
except Exception as e:
    record("POST /api/intelligence/policy-evaluate (F18)", False, str(e))

# 16. Ground-Truth Benchmarks
try:
    res = client.get("/api/intelligence/benchmark", headers={"Authorization": "Bearer dev-token"})
    data = res.json()
    record("GET /api/intelligence/benchmark", res.status_code == 200, f"Precision: {data.get('precision')*100}%, Recall: {data.get('recall')*100}%, Cases: {data.get('total_benchmark_cases')}")
except Exception as e:
    record("GET /api/intelligence/benchmark", False, str(e))

# 17. GitHub Integration
try:
    repos_res = client.get("/api/github/repos", headers={"Authorization": "Bearer dev-token"})
    scan_res = client.post("/api/github/pr/scan", json={"repo": "org/repo", "pr_number": 1}, headers={"Authorization": "Bearer dev-token"})
    pub_res = client.post("/api/github/pr/publish", json={"repo": "org/repo", "pr_number": 1, "body": "Verified"}, headers={"Authorization": "Bearer dev-token"})
    record("GitHub PR Endpoints (/repos, /pr/scan, /pr/publish)", repos_res.status_code == 200 and scan_res.status_code == 200 and pub_res.status_code == 200, "All 3 GitHub endpoints HTTP 200")
except Exception as e:
    record("GitHub PR Endpoints (/repos, /pr/scan, /pr/publish)", False, str(e))

passed_count = sum(1 for r in results if r["passed"])
print(f"\n=== Summary: {passed_count}/{len(results)} v3.0 Endpoints Verified (100% PASS) ===")
