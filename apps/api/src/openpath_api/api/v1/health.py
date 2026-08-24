"""HTTP route for process health."""

from fastapi import APIRouter, Depends, status

from openpath_api.config import Settings, get_settings
from openpath_api.schemas.health import HealthResponse
from openpath_api.services.health_service import build_health_response

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check API liveness",
)
def get_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Confirm that the API process can receive and return a valid response."""

    return build_health_response(settings)

