"""HTTP endpoints for repository discovery."""

from fastapi import APIRouter, Depends, HTTPException, status

from openpath_api.domain.repositories.reference import InvalidRepositoryUrl
from openpath_api.integrations.github.client import GitHubClient
from openpath_api.integrations.github.dependencies import get_github_client
from openpath_api.integrations.github.errors import (
    GitHubRateLimited,
    GitHubRepositoryNotFound,
    GitHubUnavailable,
)
from openpath_api.schemas.repository import RepositoryPreviewRequest, RepositoryPreviewResponse
from openpath_api.services.repository_preview_service import RepositoryPreviewService

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post(
    "/preview",
    response_model=RepositoryPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Preview a public GitHub repository",
)
async def preview_repository(
    request: RepositoryPreviewRequest,
    github_client: GitHubClient = Depends(get_github_client),
) -> RepositoryPreviewResponse:
    service = RepositoryPreviewService(github_client)

    try:
        return await service.preview(request.repository_url)
    except InvalidRepositoryUrl as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except GitHubRepositoryNotFound as exc:
        raise HTTPException(
            status_code=404,
            detail="The repository was not found or is not publicly accessible.",
        ) from exc
    except GitHubRateLimited as exc:
        raise HTTPException(
            status_code=429,
            detail="GitHub's request limit has been reached. Try again later.",
        ) from exc
    except GitHubUnavailable as exc:
        raise HTTPException(
            status_code=502,
            detail="GitHub is temporarily unavailable. Try again later.",
        ) from exc
