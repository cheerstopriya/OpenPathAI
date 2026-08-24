"""FastAPI application factory and process entry point."""

from fastapi import FastAPI

from openpath_api.api.v1.router import api_v1_router
from openpath_api.config import get_settings


def create_app() -> FastAPI:
    """Build the application explicitly so tests can create isolated instances."""

    settings = get_settings()
    application = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        docs_url="/docs",
        redoc_url=None,
    )
    application.include_router(api_v1_router)
    return application


app = create_app()

