"""Data-transfer objects matching the GitHub REST API response."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GitHubOwnerDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    login: str


class GitHubLicenseDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    spdx_id: str | None = None


class GitHubRepositoryDto(BaseModel):
    """Only fields OpenPath currently needs from GitHub's larger response."""

    model_config = ConfigDict(extra="ignore")

    owner: GitHubOwnerDto
    name: str
    full_name: str
    description: str | None = None
    html_url: str
    language: str | None = None
    stargazers_count: int
    forks_count: int
    default_branch: str
    archived: bool
    disabled: bool
    visibility: str
    topics: list[str]
    license: GitHubLicenseDto | None = None
    pushed_at: datetime | None = None


class GitHubCommunityFileDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    html_url: str | None = None


class GitHubCommunityFilesDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    code_of_conduct: GitHubCommunityFileDto | None = None
    contributing: GitHubCommunityFileDto | None = None
    issue_template: GitHubCommunityFileDto | None = None
    license: GitHubCommunityFileDto | None = None
    pull_request_template: GitHubCommunityFileDto | None = None
    readme: GitHubCommunityFileDto | None = None


class GitHubCommunityProfileDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    health_percentage: int = Field(ge=0, le=100)
    description: str | None = None
    documentation: str | None = None
    files: GitHubCommunityFilesDto


class GitHubPullRequestDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    number: int
    html_url: str
    state: str
    created_at: datetime
    closed_at: datetime | None = None
    merged_at: datetime | None = None
    user: GitHubOwnerDto


class GitHubPullRequestReviewDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    html_url: str | None = None
    state: str
    submitted_at: datetime | None = None
    user: GitHubOwnerDto | None = None


class GitHubLabelDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str


class GitHubIssueDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    number: int
    html_url: str
    title: str
    created_at: datetime
    updated_at: datetime
    assignee: GitHubOwnerDto | None = None
    labels: list[GitHubLabelDto] = Field(default_factory=list)
    pull_request: dict[str, object] | None = None

class GitHubIssueDetailDto(GitHubIssueDto):
    body: str | None = None
    state: str
    comments: int = Field(ge=0)
    user: GitHubOwnerDto

class GitHubCommentDto(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    body: str | None = None
    updated_at: datetime
    user: GitHubOwnerDto
