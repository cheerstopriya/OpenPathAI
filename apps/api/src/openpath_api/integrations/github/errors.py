"""Safe error categories emitted by the GitHub adapter."""


class GitHubClientError(Exception):
    """Base error for failures while communicating with GitHub."""


class GitHubRepositoryNotFound(GitHubClientError):
    """The repository is absent or not publicly accessible."""


class GitHubRateLimited(GitHubClientError):
    """GitHub refused the request because the current rate budget is exhausted."""

    def __init__(self, reset_at: str | None = None) -> None:
        super().__init__("GitHub rate limit exceeded")
        self.reset_at = reset_at


class GitHubUnavailable(GitHubClientError):
    """GitHub timed out, failed, or returned an unexpected contract."""
