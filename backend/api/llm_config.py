"""API endpoints for LLM configuration and connection testing."""

from fastapi import APIRouter, Request

from api.errors import DocForgeError
from api.schemas import LLMConfigResponse, LLMConfigUpdate, LLMTestResponse
from core.llm_client import LLMClient, LLMConfig, resolve_llm_config
from db.models import Project

router = APIRouter(tags=["llm-config"])


def _config_to_response(config: LLMConfig) -> LLMConfigResponse:
    return LLMConfigResponse(
        provider=config.provider,
        model=config.model,
        endpoint=config.endpoint,
        api_key_configured=config.api_key is not None and len(config.api_key) > 0,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


@router.get("/llm/config")
async def get_global_llm_config(request: Request) -> LLMConfigResponse:
    """Return the current global LLM configuration."""
    settings = request.app.state.settings
    config = resolve_llm_config(settings)
    return _config_to_response(config)


@router.post("/llm/test")
async def test_global_llm(request: Request) -> LLMTestResponse:
    """Test connectivity using the global LLM configuration."""
    settings = request.app.state.settings
    config = resolve_llm_config(settings)
    if not config.is_configured:
        return LLMTestResponse(success=False, message="LLM is not configured")
    client = LLMClient(config)
    success, message = client.test_connection()
    return LLMTestResponse(success=success, message=message)


@router.get("/projects/{project_id}/llm-config")
async def get_project_llm_config(project_id: int, request: Request) -> LLMConfigResponse:
    """Return the resolved LLM configuration for a project."""
    settings = request.app.state.settings
    session_factory = request.app.state.db

    with session_factory() as session:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise DocForgeError(
                error="not_found",
                message=f"Project {project_id} not found",
                status_code=404,
            )
        project_llm = project.llm_config or {}

    config = resolve_llm_config(settings, project_llm)
    return _config_to_response(config)


@router.put("/projects/{project_id}/llm-config")
async def update_project_llm_config(
    project_id: int,
    body: LLMConfigUpdate,
    request: Request,
) -> LLMConfigResponse:
    """Update per-project LLM configuration overrides."""
    settings = request.app.state.settings
    session_factory = request.app.state.db

    with session_factory() as session:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise DocForgeError(
                error="not_found",
                message=f"Project {project_id} not found",
                status_code=404,
            )

        # Merge update into existing project llm_config
        current = dict(project.llm_config or {})
        update_data = body.model_dump(exclude_none=True)
        current.update(update_data)
        project.llm_config = current
        session.commit()
        project_llm = dict(project.llm_config)

    config = resolve_llm_config(settings, project_llm)
    return _config_to_response(config)


@router.post("/projects/{project_id}/llm-test")
async def test_project_llm(project_id: int, request: Request) -> LLMTestResponse:
    """Test connectivity using the resolved project LLM configuration."""
    settings = request.app.state.settings
    session_factory = request.app.state.db

    with session_factory() as session:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise DocForgeError(
                error="not_found",
                message=f"Project {project_id} not found",
                status_code=404,
            )
        project_llm = project.llm_config or {}

    config = resolve_llm_config(settings, project_llm)
    if not config.is_configured:
        return LLMTestResponse(success=False, message="LLM is not configured")
    client = LLMClient(config)
    success, message = client.test_connection()
    return LLMTestResponse(success=success, message=message)
