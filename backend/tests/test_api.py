import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_snippet_scan_api():
    payload = {
        "filename": "math_helper.py",
        "language": "python",
        "code": "def divide(a, b):\n    return a / b\n\nprint(divide(10, 0))\n",
        "include_ai": True,
    }
    resp = client.post("/api/scans/snippet", json=payload, headers={"Authorization": "Bearer dev-token"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_findings"] > 0
    assert "summary" in data
    assert len(data["findings"]) > 0


def test_agent_start_and_resume_api():
    start_payload = {
        "filename": "main.py",
        "language": "python",
        "code": "def divide(a, b):\n    return a / b\n",
    }
    resp = client.post("/api/agent/start", json=start_payload, headers={"Authorization": "Bearer dev-token"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "awaiting_approval"
    thread_id = data["thread_id"]
    assert thread_id is not None
    assert data["proposal"] is not None

    # Resume with approval
    resume_payload = {
        "thread_id": thread_id,
        "approved": True,
        "feedback": "LGTM",
    }
    resume_resp = client.post("/api/agent/resume", json=resume_payload, headers={"Authorization": "Bearer dev-token"})
    assert resume_resp.status_code == 200
    res_data = resume_resp.json()
    assert res_data["status"] == "completed"


def test_github_repos_api():
    resp = client.get("/api/github/repos", headers={"Authorization": "Bearer dev-token"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
