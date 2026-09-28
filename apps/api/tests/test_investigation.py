import sys
import unittest
from pathlib import Path
import httpx
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from openpath_api.main import create_app
from openpath_api.integrations.github.client import GitHubClient
from openpath_api.integrations.github.dependencies import get_github_client

class InvestigationTests(unittest.TestCase):
    def setUp(self):
        self.paths = []
        self.visibility = "public"
        self.body = "Steps to reproduce the bug"
        self.pr = None
        self.comments_status = 200
        self.guidance = "https://github.com/team/project/blob/main/CONTRIBUTING.md"
        def handler(request):
            self.assertEqual(request.url.host, "api.github.com")
            path = request.url.path
            self.paths.append(path)
            if path.endswith("/comments"):
                self.assertEqual(request.url.params["per_page"], "10")
                return httpx.Response(self.comments_status, json=[{
                    "id": 123, "body": "<script>alert(1)</script> " + "x" * 5000,
                    "updated_at": "2026-09-01T00:00:00Z", "user": {"login": "reviewer"}}])
            if path.endswith("/community/profile"):
                return httpx.Response(200, json={"health_percentage": 50,
                    "files": {"contributing": {"html_url": self.guidance}}})
            if path.endswith("/issues/1"):
                return httpx.Response(200, json={"number": 1, "title": "Example bug",
                    "html_url": "https://bad.example/ignored", "body": self.body,
                    "state": "open", "comments": 25, "user": {"login": "author"},
                    "created_at": "2026-09-01T00:00:00Z", "updated_at": "2026-09-01T00:00:00Z",
                    "pull_request": self.pr})
            return httpx.Response(200, json={"owner": {"login": "team"}, "name": "project",
                "full_name": "team/project", "html_url": "https://github.com/team/project",
                "stargazers_count": 1, "forks_count": 0, "default_branch": "main",
                "archived": False, "disabled": False, "visibility": self.visibility, "topics": []})
        self.http = httpx.AsyncClient(base_url="https://api.github.com", transport=httpx.MockTransport(handler))
        self.app = create_app()
        self.app.dependency_overrides[get_github_client] = lambda: GitHubClient(self.http)
        self.client = TestClient(self.app)

    def tearDown(self):
        import asyncio
        self.client.close()
        asyncio.run(self.http.aclose())

    def request(self, **overrides):
        data = {"repository_url": "https://github.com/team/project", "issue_number": 1}
        data.update(overrides)
        return self.client.post("/api/v1/repositories/investigation", json=data)

    def test_collects_bounded_evidence_and_resolvable_citations(self):
        response = self.request()
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["generation_mode"], "deterministic")
        ids = {e["id"] for e in result["evidence"]}
        self.assertTrue(all(set(s["evidence_ids"]) <= ids for s in result["steps"]))
        self.assertTrue(all(e["source_url"].startswith("https://github.com/team/project/") for e in result["evidence"]))
        comment = next(e for e in result["evidence"] if e["kind"] == "comment")
        self.assertTrue(comment["truncated"])
        self.assertIn("Only 1 of 25", " ".join(result["warnings"]))
        self.assertEqual(len(self.paths), 4)

    def test_rejects_invalid_input_without_upstream_requests(self):
        for data in ({"repository_url": "http://127.0.0.1"}, {"issue_number": 0},
                     {"issue_number": True}, {"issue_number": "../secrets"}):
            self.assertEqual(self.request(**data).status_code, 422)
        self.assertEqual(self.paths, [])

    def test_private_repository_does_not_fetch_issue(self):
        self.visibility = "private"
        self.assertEqual(self.request().status_code, 404)
        self.assertEqual(len(self.paths), 1)

    def test_rejects_pr_and_surfaces_rate_limits(self):
        self.pr = {"url": "ignored"}
        self.assertEqual(self.request().status_code, 422)
        self.pr = None
        self.comments_status = 429
        self.assertEqual(self.request().status_code, 429)

    def test_missing_description_and_external_guidance_do_not_become_claims(self):
        self.body = None
        self.guidance = "https://evil.example/run.sh"
        result = self.request().json()
        self.assertIn("Insufficient evidence", " ".join(result["warnings"]))
        self.assertFalse(any(e["kind"] == "guidance_link" for e in result["evidence"]))
