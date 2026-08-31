"""Security tests for canonical GitHub repository URL parsing."""

import sys
import unittest
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT / "src"))

from openpath_api.domain.repositories.reference import (  # noqa: E402
    InvalidRepositoryUrl,
    RepositoryReference,
)


class RepositoryReferenceTest(unittest.TestCase):
    def test_parses_canonical_repository_url(self) -> None:
        reference = RepositoryReference.from_github_url(
            "https://github.com/angular/angular.git"
        )

        self.assertEqual(reference.owner, "angular")
        self.assertEqual(reference.name, "angular")

    def test_allows_trailing_slash(self) -> None:
        reference = RepositoryReference.from_github_url("https://github.com/fastapi/fastapi/")

        self.assertEqual(reference, RepositoryReference(owner="fastapi", name="fastapi"))

    def test_rejects_non_github_and_ambiguous_urls(self) -> None:
        invalid_urls = [
            "http://github.com/angular/angular",
            "https://github.example/angular/angular",
            "https://github.com:8443/angular/angular",
            "https://user@github.com/angular/angular",
            "https://github.com/angular/angular/issues",
            "https://github.com/angular/angular?tab=readme",
            "https://github.com/angular/angular#readme",
            "https://github.com/angular/%2e%2e",
            "https://127.0.0.1/internal/repository",
            "not-a-url",
        ]

        for invalid_url in invalid_urls:
            with self.subTest(url=invalid_url):
                with self.assertRaises(InvalidRepositoryUrl):
                    RepositoryReference.from_github_url(invalid_url)


if __name__ == "__main__":
    unittest.main()
