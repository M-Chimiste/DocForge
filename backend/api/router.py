from fastapi import APIRouter

from api.auto_resolution import router as auto_resolution_router
from api.data_preview import router as data_preview_router
from api.data_sources import router as data_sources_router
from api.editor import router as editor_router
from api.generation import router as generation_router
from api.generation_history import router as generation_history_router
from api.generation_stream import router as generation_stream_router
from api.llm_config import router as llm_config_router
from api.llm_extraction import router as llm_extraction_router
from api.project_export import router as project_export_router
from api.projects import router as projects_router
from api.templates import router as templates_router
from api.validation import router as validation_router

api_router = APIRouter()
api_router.include_router(projects_router)
api_router.include_router(templates_router)
api_router.include_router(data_sources_router)
api_router.include_router(generation_router)
api_router.include_router(auto_resolution_router)
api_router.include_router(validation_router)
api_router.include_router(generation_history_router)
api_router.include_router(data_preview_router)
api_router.include_router(project_export_router)
api_router.include_router(llm_config_router)
api_router.include_router(generation_stream_router)
api_router.include_router(llm_extraction_router)
api_router.include_router(editor_router)
