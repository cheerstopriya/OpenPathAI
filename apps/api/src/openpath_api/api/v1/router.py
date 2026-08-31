"""Composition point for all version 1 HTTP routes."""

from fastapi import APIRouter

from openpath_api.api.v1.health import router as health_router
from openpath_api.api.v1.repositories import router as repositories_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(repositories_router)
