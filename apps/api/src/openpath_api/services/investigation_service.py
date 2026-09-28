"""Read-only issue investigation; upstream text is evidence, never instructions."""
from datetime import UTC, datetime
from urllib.parse import urlsplit

from openpath_api.domain.repositories.reference import RepositoryReference
from openpath_api.integrations.github.errors import GitHubRepositoryNotFound
from openpath_api.schemas.investigation import (
    InvestigationEvidence, InvestigationResponse, InvestigationStep,
)

class InvestigationService:
    def __init__(self, github_client):
        self.client = github_client

    async def investigate(self, repository_url: str, issue_number: int) -> InvestigationResponse:
        ref = RepositoryReference.from_github_url(repository_url)
        repository = await self.client.get_repository(ref)
        if repository.visibility != "public":
            raise GitHubRepositoryNotFound()
        issue = await self.client.get_issue(ref, issue_number)
        if issue.pull_request is not None:
            raise ValueError("Choose an issue, not a pull request.")
        # Use validated repository identity, not arbitrary URLs returned in source text.
        base = f"https://github.com/{ref.owner}/{ref.name}"
        issue_url = f"{base}/issues/{issue_number}"
        warnings = ["Source text is untrusted. Review instructions and commands before using them.",
                    "This brief does not inspect source code or establish a root cause."]
        if issue.state != "open":
            warnings.append("This issue is no longer open; confirm whether work is still wanted.")
        if issue.assignee is not None:
            warnings.append("This issue has an assignee; coordinate before starting work.")
        if repository.archived or repository.disabled:
            warnings.append("This repository is archived or disabled and may not accept changes.")

        comments = await self.client.list_issue_comments(ref, issue_number)
        try:
            community = await self.client.get_community_profile(ref)
        except GitHubRepositoryNotFound:
            community = None
            warnings.append("Contribution guidance was unavailable.")
        body = issue.body or ""
        evidence = [InvestigationEvidence(
            id="issue", kind="issue", source_url=issue_url,
            text=f"{issue.title}\nAuthor: {issue.user.login}\nLabels: {', '.join(x.name for x in issue.labels)}\n\n{body[:8000]}",
            updated_at=issue.updated_at, truncated=len(body) > 8000,
        )]
        for comment in comments[:10]:
            text = comment.body or ""
            evidence.append(InvestigationEvidence(
                id=f"comment-{comment.id}", kind="comment",
                source_url=f"{issue_url}#issuecomment-{comment.id}",
                text=f"Author: {comment.user.login}\n{text[:4000]}",
                updated_at=comment.updated_at, truncated=len(text) > 4000,
            ))
        if issue.comments > len(comments):
            warnings.append(f"Only {len(comments)} of {issue.comments} comments were collected; later decisions may be missing.")
        if community:
            for name in ("readme", "contributing"):
                item = getattr(community.files, name)
                url = item.html_url if item else None
                if not url:
                    continue
                parsed = urlsplit(url)
                if (parsed.scheme != "https" or parsed.netloc != "github.com"
                        or not parsed.path.casefold().startswith(f"/{ref.owner}/{ref.name}/".casefold())):
                    warnings.append(f"An out-of-repository {name} link was omitted.")
                    continue
                evidence.append(InvestigationEvidence(id=name, kind="guidance_link", source_url=url,
                    text=f"Repository {name} link. Contents have not been retrieved."))
        steps = [InvestigationStep(instruction="Read the reported behavior and reproduce it before proposing a change.", evidence_ids=["issue"])]
        comment_ids = [e.id for e in evidence if e.kind == "comment"]
        if comment_ids:
            steps.append(InvestigationStep(instruction="Review the sampled discussion for decisions and clarification; check GitHub for newer comments.", evidence_ids=comment_ids))
        guidance = [e.id for e in evidence if e.kind == "guidance_link"]
        if guidance:
            steps.append(InvestigationStep(instruction="Open the contribution guidance to find setup and testing requirements.", evidence_ids=guidance))
        if not body.strip():
            warnings.append("Insufficient evidence: the issue has no description. Ask for a reproducible example before planning a fix.")
        if any(e.truncated for e in evidence):
            warnings.append("Long source text was truncated; open the original source for full context.")
        return InvestigationResponse(repository_full_name=repository.full_name,
            issue_number=issue_number, issue_title=issue.title, issue_state=issue.state,
            fetched_at=datetime.now(UTC), evidence=evidence, steps=steps, warnings=warnings)
