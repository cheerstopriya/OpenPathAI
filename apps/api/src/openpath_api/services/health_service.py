"""Health-check application logic."""

from openpath_api.config import Settings
from openpath_api.schemas.health import HealthResponse


def build_health_response(settings: Settings) -> HealthResponse:
    """Return process health without contacting optional external dependencies.

    This is a liveness check: it answers whether the API process can serve a
    request. Database and provider checks belong in a separate readiness check.
    """

    return HealthResponse(
        status="ok",
        service=settings.api_title,
        version=settings.api_version,
        environment=settings.environment,
    )

