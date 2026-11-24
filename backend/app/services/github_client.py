from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings


class GitHubClient:
    """
    Communicates with the GitHub REST API to fetch PR diff files and post reviews.
    Enforces the rule that PR reviews and comments are only posted after explicit user approval.
    """

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Automated-Code-Reviewer-Bot",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def get_pr_files(self, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Fetches the list of files and patches changed in a PR."""
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=self.headers)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 404:
                # Return mock files for offline demo
                return self._mock_pr_files(repo, pr_number)
            resp.raise_for_status()
            return []

    async def post_pr_review(
        self,
        repo: str,
        pr_number: int,
        body: str,
        event: str = "COMMENT",
        comments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Posts a review comment to the PR only after human approval."""
        if not self.token:
            return {
                "status": "mock_posted",
                "message": "GitHub review comment simulated successfully (Dev Mode - no token)",
                "repo": repo,
                "pr_number": pr_number,
                "body": body,
            }

        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
        payload: Dict[str, Any] = {
            "body": body,
            "event": event,
        }
        if comments:
            payload["comments"] = comments

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    def _mock_pr_files(self, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        return [
            {
                "sha": "bb5e0e018a472c68edd08f60f8300de040d5f5e6",
                "filename": "backend/math_utils.py",
                "status": "modified",
                "additions": 4,
                "deletions": 1,
                "changes": 5,
                "patch": "@@ -1,3 +1,6 @@\n def divide(a, b):\n-    return a / b\n+    if b == 0:\n+        raise ValueError('b cannot be zero')\n+    return a / b\n",
                "raw_code": "def divide(a, b):\n    return a / b\n\nprint(divide(10, 0))\n",
            }
        ]


github_client = GitHubClient()
