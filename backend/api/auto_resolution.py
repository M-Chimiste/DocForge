"""Auto-resolution API endpoint."""

from pathlib import Path

from fastapi import APIRouter, Request

from api.errors import DocForgeError
from api.schemas import AutoResolutionMatchResponse, AutoResolutionResponse
from core.data_loader import load_data_sources
from core.engine import GenerationEngine
from db.models import Project

router = APIRouter(tags=["auto-resolution"])


@router.post("/projects/{project_id}/auto-resolve")
async def auto_resolve(project_id: int, request: Request) -> AutoResolutionResponse:
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
        if not project.template_path:
            raise DocForgeError(
                error="no_template",
                message="No template associated with this project",
                status_code=400,
            )
        template_path = Path(project.template_path)

    if not template_path.exists():
        raise DocForgeError(
            error="template_missing",
            message="Template file not found on disk",
            status_code=400,
        )

    # Load data sources
    project_data_dir = settings.upload_dir / str(project_id) / "data"
    data_paths = list(project_data_dir.iterdir()) if project_data_dir.exists() else []

    if not data_paths:
        raise DocForgeError(
            error="no_data",
            message="No data sources uploaded for this project",
            status_code=400,
        )

    engine = GenerationEngine()
    analysis = engine.analyze(template_path)
    data_store = load_data_sources(data_paths)
    report = engine.auto_resolve(analysis, data_store)

    return AutoResolutionResponse(
        matches=[
            AutoResolutionMatchResponse(
                marker_id=m.marker_id,
                data_source=m.data_source,
                field=m.field,
                sheet=m.sheet,
                path=m.path,
                confidence=m.confidence,
                match_type=m.match_type,
                reasoning=m.reasoning,
            )
            for m in report.matches
        ],
        unresolved=report.unresolved,
    )
