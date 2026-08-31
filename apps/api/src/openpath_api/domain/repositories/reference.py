"""Validated identity for a public GitHub repository."""

import re
from dataclasses import dataclass
from urllib.parse import urlsplit

_OWNER_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
_REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,100}$")


class InvalidRepositoryUrl(ValueError):
    """Raised when input is not a canonical public GitHub repository URL."""


@dataclass(frozen=True, slots=True)
class RepositoryReference:
    """Owner/name pair that is safe to place in a GitHub API path."""

    owner: str
    name: str

    @classmethod
    def from_github_url(cls, raw_url: str) -> "RepositoryReference":
        """Validate a URL without ever requesting the user-supplied host."""

        candidate = raw_url.strip()
        if not candidate or "%" in candidate:
            raise InvalidRepositoryUrl("Enter a complete, unencoded GitHub repository URL.")

        try:
            parsed = urlsplit(candidate)
            port = parsed.port
        except ValueError as exc:
            raise InvalidRepositoryUrl("The repository URL is malformed.") from exc

        if parsed.scheme != "https" or parsed.hostname != "github.com":
            raise InvalidRepositoryUrl("Only https://github.com repository URLs are supported.")
        if parsed.username or parsed.password or port is not None:
            raise InvalidRepositoryUrl("Credentials and custom ports are not allowed.")
        if parsed.query or parsed.fragment:
            raise InvalidRepositoryUrl("Query strings and fragments are not allowed.")

        segments = [segment for segment in parsed.path.split("/") if segment]
        if len(segments) != 2:
            raise InvalidRepositoryUrl("Use a repository URL in the form github.com/owner/name.")

        owner, name = segments
        if name.endswith(".git"):
            name = name[:-4]

        if not _OWNER_PATTERN.fullmatch(owner):
            raise InvalidRepositoryUrl("The repository owner is invalid.")
        if not _REPOSITORY_PATTERN.fullmatch(name) or name in {".", ".."}:
            raise InvalidRepositoryUrl("The repository name is invalid.")

        return cls(owner=owner, name=name)
