from fastapi import APIRouter

from api.data_sources import router as data_sources_router
from api.generation import router as generation_router
from api.projects import router as projects_router
from api.templates import router as templates_router

api_router = APIRouter()
api_router.include_router(projects_router)
api_router.include_router(templates_router)
api_router.include_router(data_sources_router)
api_router.include_router(generation_router)
